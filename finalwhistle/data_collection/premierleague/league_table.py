#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#
#   COMP208 Final Whistle Project
#
#   Obtain a list of all managers and team they manage
#
################################################################################


from bs4 import BeautifulSoup
import json

import shutil

# MY LIBS ######################################################################


from finalwhistle.data_collection.premierleague.helper import FireMyFox


# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/tables?team=FIRST&co=1&se=79&ha=-1"



# FUNCTIONS ####################################################################


def get_league_table(path):
    """
    Download latest premier league table
    :return:
    """

    driver = FireMyFox()
    driver.visit_url(URL)
    driver.wait_for_class("team")
    driver.set_timeout(5)
    soup = BeautifulSoup(driver.html, "html.parser")

    table = {}
    club_list = soup.find('tbody', attrs={'class': 'tableBodyContainer'})

    position = 1
    for row in club_list.findAll('tr'):

        column_index = 0
        club, played, won, drawn, lost, gf, ga, gd, points = '', '', '', '', '', '', '', '', ''
        for col in row.findAll('td'):

            if column_index == 2:
                club = col.find('span', attrs={'class': 'long'}).get_text()
            elif column_index == 3:
                played = col.get_text()
            elif column_index == 4:
                won = col.get_text()
            elif column_index == 5:
                drawn = col.get_text()
            elif column_index == 6:
                lost = col.get_text()
            elif column_index == 7:
                gf = col.get_text()
            elif column_index == 8:
                ga = col.get_text()
            elif column_index == 9:
                gd = col.get_text().replace('\n', '').strip()
            elif column_index == 10:
                points = col.get_text()

            column_index += 1
            # end for

        if len(club) > 0:

            table[position] = {
                'club': club,
                'played': played,
                'won': won,
                'drawn': drawn,
                'lost': lost,
                'gf': gf,
                'ga': ga,
                'gd': gd,
                'points': points
            }

            position += 1
        # end for

    # Write the data to json
    with open(path, 'w') as outfile:
        json.dump(table, outfile, ensure_ascii=False, indent=4)
        print('Writing JSON: {}'.format(path))
