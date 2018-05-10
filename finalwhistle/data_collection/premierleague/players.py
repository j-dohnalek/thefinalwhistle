#!/usr/bin/env python3
# -*- coding: utf-8 -*-


################################################################################
#
#   COMP208 Final Whistle Project
#
################################################################################


import json
from bs4 import BeautifulSoup
import os

from finalwhistle.models.football import Player, Team

# MY LIBS ######################################################################


from finalwhistle.data_collection.premierleague.helper import FireMyFox, PageError


# CONSTANTS ####################################################################

ROOT = "{}/".format(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'football_data', 'tmp')))
URL = "https://www.premierleague.com/players?se=79&cl=-1"
DUMP_PATH = ROOT + 'new_players.json'
DUMP_CACHE = ROOT + 'new_players.cache.json'
SEASON = '2017/2018'

# FUNCTIONS ####################################################################


def get_all_player():
    """
    Fetch all players from premierleague.com website
    :return: all players dictionary
    """
    driver = FireMyFox()
    driver.visit_url(URL)
    driver.wait_for_class("playerName")
    soup = BeautifulSoup(driver.html, "html.parser")

    players = {}
    # Fetch the list of players
    players_list = soup.find('tbody', attrs={'class': 'dataContainer'})
    for row in players_list.findAll('tr'):
        # Fetch player name, position, and link
        column_index = 0
        player_name, player_link = '', ''
        for column in row.findAll('td'):
            if column_index == 0:
                player_name = column.get_text()
                player_link = column.find('a')['href']
                player_link = 'https:{}'.format(player_link)
            else:
                break
            column_index += 1
            # end for
        players[player_name] = player_link

    return players


def compare_players():
    """
    Compare players from Database vs premierleague.com
    :return: list of player not in database
    """

    # Fetch all player in database
    players = Player.query.all()
    pm_players = get_all_player()

    for player in players:
        pm_players.pop(player.name, None)
    return pm_players


def fetch_new_players(new_players):
    """
    Fetch all players not in database
    :param new_players: list of players to fetch
    """

    players = []

    # Load cache from the tmp folder
    with open(DUMP_CACHE) as outfile:
        cached_players = json.load(outfile)

    for player_name, player_link in new_players.items():

        try:
            if cached_players[player_name] == 'Visited':
                pass
        except KeyError:
            cached_players[player_name] = 'Visited'

            # Fetch information from players personal page
            player_driver = FireMyFox()
            player_driver.visit_url(player_link)
            player_driver.wait_for_class("info")

            try:
                player_soup = BeautifulSoup(player_driver.html, "html.parser")

            except PageError:
                pass

            else:
                player_details = dict(position='', club='')

                player_intro = player_soup.find('section', attrs={'class': 'playerIntro'})
                for label in player_intro.findAll('div', attrs={'class': 'label'}):
                    label_text = label.get_text().lower()
                    info = label.find_next_sibling('div', attrs={'class': 'info'})
                    player_info = None
                    if 'club' in label_text:
                        player_info = info.find('a').get_text().replace('\n', '').strip()
                    elif 'position' in label_text:
                        player_info = info.get_text()
                    player_details[label_text] = player_info

                player_club_history = player_soup.find('div', attrs={'class': 'playerClubHistory'})
                player_tr = player_club_history.find('tr', attrs={'class': 'table'})

                td_season = player_tr.find('td', attrs={'class': 'season'})
                season = td_season.find('p').get_text()
                club = player_tr.find('span', attrs={'class': 'long'}).get_text()
                if SEASON == season:
                    player_details['old_club'] = club

                team = Team.query.filter(Team.name == player_details['club']).first()
                old_team = Team.query.filter(Team.name == player_details['old_club']).first()
                if team is not None or old_team is not None:

                    player = {}

                    # Player number is in separate div tag
                    player_number = -1
                    try:
                        player_number = player_soup.find('div', attrs={'class': 'number'}).get_text()
                    except AttributeError:
                        pass

                    # Fetch players nationality, age, dob, height, weight
                    column_index = 0
                    personal_lists = player_soup.find('div', attrs={'class': 'personalLists'})
                    nationality, age, dob, height, weight = '', '', '', '', ''
                    try:
                        for detail in personal_lists.findAll('div', attrs={'class': 'info'}):
                            if column_index == 0:
                                try:
                                    nationality = detail.get_text().replace('\n', '')
                                except AttributeError:
                                    pass
                            elif column_index == 1:
                                try:
                                    age = detail.get_text()
                                except AttributeError:
                                    pass
                            elif column_index == 2:
                                try:
                                    dob = detail.get_text()
                                except AttributeError:
                                    pass
                            elif column_index == 3:
                                try:
                                    height = detail.get_text()
                                except AttributeError:
                                    pass
                            elif column_index == 4:
                                try:
                                    weight = detail.get_text()
                                except AttributeError:
                                    pass
                            else:
                                break

                            column_index += 1

                    except AttributeError:
                        pass

                    player["name"] = player_name
                    player["position"] = player_details['position']
                    player["shirt_number"] = player_number
                    player["nationality"] = nationality
                    player["age"] = age
                    player["dob"] = dob
                    player["height"] = height
                    player["weight"] = weight
                    player["new_club"] = player_details['club']
                    player["old_club"] = player_details['old_club']

                    players.append(player)
                    # end for

                # Write the data to json
                with open(DUMP_PATH, 'w') as outfile:
                    json.dump(players, outfile, ensure_ascii=False, indent=4)

        # Update the cache file with the newly sourced matches
        with open(DUMP_CACHE, 'w') as outfile:
            json.dump(cached_players, outfile, ensure_ascii=False, indent=4)

    # end for
    print("Fetching of players complete")


def fetch_records():
    fetch_new_players(compare_players())


if __name__ == "__main__":
    fetch_records()