# -*- coding: utf-8 -*-
import json
from bs4 import BeautifulSoup
from pathlib import Path

# MY LIBS ######################################################################

from helper import grab_html_by_class, init_driver

# CONSTANTS ####################################################################

URL = "https://www.premierleague.com/players"
CLUBS = 'clubs2.json'
PLAYERS = 'players.json'

# FUNCTIONS ####################################################################


def get_club_player():
    """
    Create a dictionary list of all clubs and their corresponding API id
    """
    club_list = {}
    with open(PLAYERS) as json_data:
        clubs = json.load(json_data)
        for club in clubs:
            club_list[club['team']] = club['players']

    print(club_list)


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


def main():

    driver = init_driver()

    clubs = {}
    my_file = Path(CLUBS)
    if not my_file.is_file():

        class_name = "dropDown"
        html = grab_html_by_class(driver, class_name, URL, leave_open=True)
        soup = BeautifulSoup(html, "html.parser")

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
        clubs = get_clubs()

    for club_name, api_id in clubs.items():

        club_players = {}

        players = []
        url = URL + '?se=79&cl={}'.format(api_id)
        class_name = "playerName"
        html = grab_html_by_class(driver, class_name, url, leave_open=True)
        soup = BeautifulSoup(html, "html.parser")

        managers_list = soup.find('tbody', attrs={'class': 'dataContainer'})
        for row in managers_list.findAll('tr'):

            player = {}
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

            player_html = grab_html_by_class(
                init_driver(), 'number', player_link, leave_open=False, scroll=True)
            playersoup = BeautifulSoup(player_html, "html.parser")
            player_number = -1
            try:
                player_number = playersoup.find('div', attrs={'class': 'number'}).get_text()
            except AttributeError:
                pass

            column_index = 0
            personal_lists = playersoup.find('div', attrs={'class': 'personalLists'})
            nationality, age, dob, height, weight = '', '', '', '', ''

            try:
                for detail in personal_lists.findAll('div', attrs={'class': 'info'}):
                    if column_index == 0:
                        nationality = detail.get_text().replace('\n', '')
                    elif column_index == 1:
                        age = detail.get_text()
                    elif column_index == 2:
                        dob = detail.get_text()
                    elif column_index == 3:
                        height = detail.get_text()
                    elif column_index == 4:
                        weight = detail.get_text()
                    else:
                        break

                    column_index += 1

            except AttributeError:
                pass

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

        path = '{}.json'.format(club_name.replace(' ', '_'))

        with open(PLAYERS, 'w') as outfile:
            values = [{"team": k, "players": v} for k, v in club_players.items()]
            json.dump(values, outfile, ensure_ascii=False, indent=4)
            print('Writing to JSON complete')

    # end for
    driver.quit()


if __name__ == "__main__":
    main()
