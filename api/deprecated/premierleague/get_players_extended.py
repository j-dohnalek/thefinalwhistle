#!/usr/bin/env python3
# -*- coding: utf-8 -*-


################################################################################
#
#   COMP208 Final Whistle Project
#
#   Obtain all teams of Premier League, for each of the team obtain all players
#   1. Start at https://www.premierleague.com/players scraping all teams from a
#   HTML dropdown caching the result.
#   2. Select the team T from the dropdown, obtain all team members and a link
#   for the players personal page
#   3. Visit individual player page and obtain the information about the player
#   4. Store all results in JSON File
#
################################################################################


import json
from bs4 import BeautifulSoup
from pathlib import Path


# MY LIBS ######################################################################


from helper import FireMyFox


# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/players"
CLUBS = 'tmp/outstanding_clubs.json'
JSON_DUMP_PATH = 'jsondump/clubs'


# FUNCTIONS ####################################################################


def get_clubs():
    """
    Create a dictionary list of all clubs and their corresponding API id
    """
    club_list = {}
    with open(CLUBS) as json_data:
        clubs = json.load(json_data)
        for club in clubs:
            club_list[club['club']] = int(club['api'])

    return club_list


def get_cached_clubs():
    """
    Retrieved the cached version of clubs if exists
    :return clubs dictionary
    """
    clubs = {}
    my_file = Path(CLUBS)
    # Check for the cached version of the club list if not exist fetch it from
    # the website
    if not my_file.is_file():

        driver = FireMyFox()
        driver.visit_url(URL)
        driver.wait_for_class("dropDown")
        soup = BeautifulSoup(driver.html, "html.parser")

        # Filter available clubs and their API ids
        club_dropdown = soup.find('ul', attrs={'data-dropdown-list': 'clubs'})
        ignore_first_line = True
        clubs = {}
        for row in club_dropdown.findAll('li'):
            if ignore_first_line:
                ignore_first_line = False
            else:
                clubs[row.get_text()] = int(row['data-option-id'])

        with open(CLUBS, 'w') as outfile:
            values = [{"club": k, "api": v} for k, v in clubs.items()]
            json.dump(values, outfile, indent=4)

    else:
        # Cached version
        clubs = get_clubs()


def main():

    # Prepare the storage
    club_players = {}
    players = []

    # Fetch the HTML
    driver = FireMyFox()
    driver.visit_url(URL)
    driver.wait_for_class("playerName")
    soup = BeautifulSoup(driver.html, "html.parser")

    # Fetch the list of players
    players_list = soup.find('tbody', attrs={'class': 'dataContainer'})
    for row in players_list.findAll('tr'):

        player = {}

        # Fetch player name, position, and link
        column_index = 0
        player_name, position = '', ''
        for column in row.findAll('td'):

            if column_index == 0:
                player_name = column.get_text()
                player_link = column.find('a')['href']
                player_link = 'https:{}'.format(player_link)
            elif column_index == 1:
                position = column.get_text()
            else:
                break

            column_index += 1

            # end for

        # Fetch information from players personal page
        # Fetch the HTML
        driver = FireMyFox()
        driver.visit_url(player_link)
        driver.wait_for_class("info")
        playersoup = BeautifulSoup(driver.html, "html.parser")

        # Player number is in separate div tag
        player_number = -1
        try:
            player_number = playersoup.find('div', attrs={'class': 'number'}).get_text()
        except AttributeError:
            pass

        # Fetch players nationality, age, dob, height, weight
        column_index = 0
        personal_lists = playersoup.find('div', attrs={'class': 'personalLists'})
        nationality, age, dob, height, weight = '', '', '', '', ''
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

        print("Visit complete")

        player["name"] = player_name
        player["position"] = position
        player["shirt_number"] = player_number
        player["nationality"] = nationality
        player["age"] = age
        player["dob"] = dob
        player["height"] = height
        player["weight"] = weight

        players.append(player)
        # end for

    club_players[club_name] = players

    # Write the data to json
    path = '{}/players-{}.json'.format(JSON_DUMP_PATH, club_name.replace(' ', '_'))
    with open(path, 'w') as outfile:
        values = [{"team": k, "players": v} for k, v in club_players.items()]
        json.dump(values, outfile, ensure_ascii=False, indent=4)
        print('Writing JSON: {}'.format(path))



if __name__ == "__main__":
    main()
