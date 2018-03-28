from bs4 import BeautifulSoup

# MY LIBS ######################################################################

from helper import grab_html_by_class, init_driver


# CONSTANTS ####################################################################

URL = "https://www.premierleague.com/managers"

# FUNCTIONS ####################################################################


def main():

    html = grab_html_by_class(init_driver(), class_name="managerName", url=URL)
    soup = BeautifulSoup(html, "html.parser")

    managers_list = soup.find('tbody', attrs={'class': 'dataContainer'})

    print('{ "managers": [')
    for row in managers_list.findAll('tr'):

        column_index = 0
        manager_name, club_name_long, club_name_short = '', '', ''
        for column in row.findAll('td'):

            # Manager column
            if column_index == 0:
                manager_name = column.get_text()
            # Team name
            elif column_index == 1:
                club_name_long = column.find('span', attrs={'class': 'long'}).get_text()
                club_name_short = column.find('span', attrs={'class': 'short'}).get_text()
            else:
                break

            column_index += 1

        print('{')
        print(' "manager": "', manager_name, '",')
        print('"club_short": "', club_name_short, '",')
        print('"club_long": "', club_name_long, '"')
        print('},')

    print(']}')


if __name__ == "__main__":
    main()
