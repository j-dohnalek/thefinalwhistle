from bs4 import BeautifulSoup
import json
import os

# MY LIBS ######################################################################


from finalwhistle.data_collection.premierleague.helper import FireMyFox


# CONSTANTS ####################################################################

ROOT = "{}/".format(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'football_data', 'json')))
JSON_PATH = ROOT + 'list_of_stadiums.json'

URL = "https://www.premierleague.com/clubs"


# FUNCTIONS ####################################################################


def fetch_stadiums():

    driver = FireMyFox()
    driver.visit_url(URL)
    driver.wait_for_class("team")
    soup = BeautifulSoup(driver.html, "html.parser")

    club_list = soup.find('ul', attrs={'class': 'dataContainer'})

    club = {}
    for row in club_list.findAll('li'):

        stadium_name = row.find('div', attrs={'class': 'stadiumName'}).get_text().strip()
        club_name = row.find('h4', attrs={'class': 'clubName'}).get_text().strip()
        club[club_name] = stadium_name

    # Write the data to json
    with open(JSON_PATH, 'w') as outfile:
        values = [{"club": k, "stadium": v} for k, v in club.items()]
        json.dump(values, outfile, ensure_ascii=False, indent=4)
        print('Writing JSON: {}'.format(JSON_PATH))

