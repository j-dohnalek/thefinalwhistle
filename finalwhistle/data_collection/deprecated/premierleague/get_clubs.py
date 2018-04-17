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


# MY LIBS ######################################################################


from helper import FireMyFox


# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/tables?team=FIRST&co=1&se=79&ha=-1"
JSON_PATH = 'jsondump/list_of_clubs.json'


# FUNCTIONS ####################################################################


def main():

    driver = FireMyFox()
    driver.visit_url(URL)
    driver.wait_for_class("team")
    soup = BeautifulSoup(driver.html, "html.parser")

    clubs = {}
    club_list = soup.find('tbody', attrs={'class': 'tableBodyContainer'})
    for row in club_list.findAll('tr'):

        if row.find('td', attrs={'class': 'team'}) is not None:
            col = row.find('td', attrs={'class': 'team'})
            club_id = col.find('a')['href'].split('/')[2]
            club_name = col.find('span', attrs={'class': 'long'}).get_text()

            clubs[club_name] = club_id
            # end if

        # end for

    # Write the data to json
    with open(JSON_PATH, 'w') as outfile:
        values = [{"club": k, "api_id": v} for k, v in clubs.items()]
        json.dump(values, outfile, ensure_ascii=False, indent=4)
        print('Writing JSON: {}'.format(JSON_PATH))


if __name__ == "__main__":
    main()
