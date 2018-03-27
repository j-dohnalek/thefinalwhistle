from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

# MY LIBS ######################################################################

from helper import wait_for_html_class, scroll_to_bottom

# CONSTANTS ####################################################################

# Wait to load page
SCROLL_PAUSE_TIME = 0.5

URL = "https://www.premierleague.com/clubs"

# FUNCTIONS ####################################################################


def init_driver():
    """
    Initialise the Firefox geckodriver
    """
    print("Opening Driver")
    options = Options()
    options.add_argument('-headless')
    return Firefox(executable_path='./geckodriver', firefox_options=options)


def grab_html(driver, class_name, url):
    """
    :param driver       : Firefox GeckoDriver
    :param class_name   : Wait for class attribute name before fetching HTML
    :param url          : Source URL
    """
    print("Visiting url:", url)
    driver.get(url)
    scroll_to_bottom(driver, SCROLL_PAUSE_TIME)
    wait_for_html_class(driver, class_name, 10)

    html = driver.page_source
    driver.quit()
    return html


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
