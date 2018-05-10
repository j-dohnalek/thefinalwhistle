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
import os


# MY LIBS ######################################################################


from finalwhistle.data_collection.premierleague.helper import FireMyFox


# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/managers"

ROOT = "{}/".format(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'football_data', 'json')))
JSON_PATH = ROOT + 'list_of_managers.json'


# FUNCTIONS ####################################################################


def fetch_club_staff():

    driver = FireMyFox()
    driver.visit_url(URL)
    driver.wait_for_class("managerName")
    soup = BeautifulSoup(driver.html, "html.parser")

    club_managers = {}
    managers = []

    managers_list = soup.find('tbody', attrs={'class': 'dataContainer'})
    previous_club = None
    for row in managers_list.findAll('tr'):

        column_index = 0
        manager_name, club_name = '', ''
        for column in row.findAll('td'):

            # Manager column
            if column_index == 0:
                manager_name = column.get_text()
            # Team name
            elif column_index == 1:
                club_name = column.find('span', attrs={'class': 'long'}).get_text()
            else:
                break

            column_index += 1

        if club_name == previous_club or previous_club is None:
            managers.append(manager_name)
        else:
            managers = [manager_name]

        club_managers[club_name] = managers
        previous_club = club_name

    # Write the data to json
    with open(JSON_PATH, 'w') as outfile:
        values = [{"club": k, "managers": v} for k, v in club_managers.items()]
        json.dump(values, outfile, ensure_ascii=False, indent=4)
