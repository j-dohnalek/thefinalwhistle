from bs4 import BeautifulSoup
import json


# MY LIBS ######################################################################


from helper import grab_html_by_class, init_driver


# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/clubs"
JSON_PATH = 'jsondump/list_of_stadiums.json'


# FUNCTIONS ####################################################################


def main():

    html = grab_html_by_class(init_driver(), class_name="team", url=URL)
    soup = BeautifulSoup(html, "html.parser")

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


if __name__ == "__main__":
    main()
