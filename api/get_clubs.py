from bs4 import BeautifulSoup

# MY LIBS ######################################################################

from helper import grab_html, init_driver

# CONSTANTS ####################################################################

# Wait to load page
SCROLL_PAUSE_TIME = 0.5

URL = "https://www.premierleague.com/clubs"

# FUNCTIONS ####################################################################


def main():

    html = grab_html(init_driver(), class_name="team", url=URL)
    soup = BeautifulSoup(html, "html.parser")

    club_list = soup.find('tbody', attrs={'class': 'allTimeDataContainer'})

    print('{ "clubs" :[')

    for row in club_list.findAll('tr'):

        stadium = row.find('td', attrs={'class': 'venue'}).get_text().strip()
        club_column = row.find('td', attrs={'class': 'team'})
        club = club_column.get_text().strip()
        club_id = club_column.find('a')['href'].split('/')[4].strip()

        print('{"club_id":"', club_id, '", "club": "', club, '", "stadium": "', stadium, '"},')

    print(']}')


if __name__ == "__main__":
    main()
