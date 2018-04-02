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


# MY LIBS ######################################################################


from helper import grab_html_by_class, init_driver

# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/referees/index"
JSON_PATH = 'jsondump/list_of_referees.json'


# FUNCTIONS ####################################################################


def main():

    html = grab_html_by_class(init_driver(), class_name="managerName", url=URL)
    soup = BeautifulSoup(html, "html.parser")

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

        pl_referees['referees'].append(referee_name)

    # Write the data to json
    with open(JSON_PATH, 'w') as outfile:
        values = [{"referees": v} for k, v in pl_referees.items()]
        json.dump(values, outfile, ensure_ascii=False, indent=4)
        print('Writing JSON: {}'.format(JSON_PATH))


if __name__ == "__main__":
    main()
