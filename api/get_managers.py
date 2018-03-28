from bs4 import BeautifulSoup
import json


# MY LIBS ######################################################################


from helper import grab_html_by_class, init_driver


# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/managers"
JSON_PATH = 'json/managers.json'


# FUNCTIONS ####################################################################


def main():

    html = grab_html_by_class(init_driver(), class_name="managerName", url=URL)
    soup = BeautifulSoup(html, "html.parser")

    club_managers = []

    managers_list = soup.find('tbody', attrs={'class': 'dataContainer'})
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

        club_managers.append({
            "manager": manager_name,
            "club_name": club_name
        })

    # Write the data to json
    with open(JSON_PATH, 'w') as outfile:
        values = [v for v in club_managers]
        json.dump(values, outfile, ensure_ascii=False, indent=4)
        print('Writing JSON: {}'.format(JSON_PATH))


if __name__ == "__main__":
    main()
