#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#
#   COMP208 Final Whistle Project
#
#   Obtain a list of all referees in premier league
#
################################################################################


from bs4 import BeautifulSoup
import json
import os


# MY LIBS ######################################################################


from finalwhistle.data_collection.premierleague.helper import FireMyFox


# CONSTANTS ####################################################################


ROOT = "{}/".format(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'football_data', 'json')))
JSON_PATH = ROOT + 'list_of_referees.json'

URL = "https://www.premierleague.com/referees/index"


# FUNCTIONS ####################################################################


def fetch_referees():
    """
    Fetch all referees from the premierleague.com website
    :return: void
    """

    driver = FireMyFox()
    driver.visit_url(URL)
    driver.wait_for_class("managerName")
    soup = BeautifulSoup(driver.html, "html.parser")

    pl_referees = {'referees': []}

    managers_list = soup.find('tbody', attrs={'class': 'dataContainer'})
    for row in managers_list.findAll('tr'):

        column_index = 0
        referee_name, club_name = '', ''
        for column in row.findAll('td'):
            # Manager column
            if column_index == 0:
                referee_name = column.get_text()
            else:
                break
            column_index += 1

            referee_name = referee_name.replace('Anthony', 'Andy')
        # EndFor

        pl_referees['referees'].append(referee_name)

    # Write the data to json
    with open(JSON_PATH, 'w') as outfile:
        values = [{"referees": v} for k, v in pl_referees.items()]
        json.dump(values, outfile, ensure_ascii=False, indent=4)
