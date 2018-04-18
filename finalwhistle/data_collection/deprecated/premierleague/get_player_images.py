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


from premierleague.helper import FireMyFox


# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/players?se=79&cl=-1"
JSON_DUMP_PATH = 'cache/json/players_images.json'


# FUNCTIONS ####################################################################


def fetch():

    # Prepare the storage
    players = {}

    # Fetch the HTML
    driver = FireMyFox()
    driver.visit_url(URL)
    driver.wait_for_class("playerName")
    soup = BeautifulSoup(driver.html, "html.parser")

    # Fetch the list of players
    players_list = soup.find('tbody', attrs={'class': 'dataContainer'})

    for row in players_list.findAll('tr'):

        # Fetch player name, position, and link
        column_index = 0
        player_name, player_image_id = '', ''
        for column in row.findAll('td'):

            if column_index == 0:
                player_name = column.get_text()
                player_image_id = column.find('img')['data-player']
            else:
                break

            column_index += 1
            # end for

        players[player_name] = player_image_id

    # Write the data to json
    with open(JSON_DUMP_PATH, 'w') as outfile:
        json.dump(players, outfile, ensure_ascii=False, indent=4)
        print('Writing JSON: {}'.format(JSON_DUMP_PATH))

    # end for


if __name__ == "__main__":
    main()
