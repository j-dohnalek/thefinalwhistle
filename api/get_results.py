from bs4 import BeautifulSoup
import json


# MY LIBS ######################################################################


from helper import grab_html_by_class, init_driver


# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/results?team=FIRST&co=1&se=79&cl=-1"


# FUNCTIONS ####################################################################


def fetch_game_info(driver, match_url):
    """
    Fetch a particular game details
    :param driver: Selenium WebDriver
    :param match_url: url to the match page
    """

    print("Match url", match_url)
    driver.get(match_url)
    wait_for_html_class(driver, "tablist", 10)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    referee = soup.find('div', attrs={'class': 'referee'})
    if referee is not None:
        print("Referee:", referee.get_text().replace('\n', '').strip())
    else:
        print("Referee: None")

    kick_off = soup.find('strong', attrs={'class': 'renderKOContainer'})
    if kick_off is not None:
        print("Kick Off:", kick_off.get_text())

    for event_line in soup.findAll('div', attrs={'class': 'eventLine'}):

        for event in event_line.findAll('div', attrs={'class': 'event'}):

            event_type = event.find('span', attrs={'class': 'visuallyHidden'})
            if event_type is not None:
                print()
                event_info = event_type.get_text()
                print(event_info)

                if "Goal" in event_info and "Own" not in event_info:

                    event_time = event.find('time', attrs={'class': 'min'})
                    scorer = event.find('a', attrs={'class': 'name'})
                    assist = event.find('div', attrs={'class': 'assist'})

                    # Clean the unwanted information
                    time_of_match = event_time.get_text().replace('\'', '')

                    if '+' in time_of_match:
                        time_of_match = time_of_match.split('+')
                    else:
                        print("Match Minute:", event_time.get_text())
                        print("Scorer", scorer.get_text())

                    if assist is not None:
                        assist = assist.get_text().replace('Ast.', '')
                        print("Assist: ", assist.get_text())

                if "Own Goal" in event_info:

                    event_time = event.find('time', attrs={'class': 'min'})
                    scorer = event.find('a', attrs={'class': 'name'})
                    print("Match Minute:", event_time.get_text())
                    print("Scorer: ", scorer.get_text())

                if "Substitution" in event_info:

                    event_time = event.find('time', attrs={'class': 'min'})
                    print("Match Minute:", event_time.get_text())

                    sub_on = event.find('div', attrs={'class': 'subOn'})
                    # Player might be only taken out due to injury
                    if sub_on is not None:
                        player_in = sub_on.find('a', attrs={'class': 'name'})

                        unwanted = player_in.find('div', attrs={'class': 'icn'})
                        unwanted.extract()

                        substituted_in = player_in.get_text().replace('\n', '')
                        print("IN:", substituted_in)

                    player_out = event.find('a', attrs={'class': 'name'})

                    unwanted = player_out.find('div', attrs={'class': 'icn'})
                    unwanted.extract()

                    substituted_out = player_out.get_text().replace('\n', '')
                    print("OUT:", substituted_out)

                if "Yellow Card" in event_info and "Second" not in event_info:

                    event_time = event.find('time', attrs={'class': 'min'})
                    player = event.find('a', attrs={'class': 'name'})
                    print("Match Minute:", event_time.get_text())
                    print("Player:", player.get_text())

                if "Red Card" in event_info:

                    event_time = event.find('time', attrs={'class': 'min'})
                    player = event.find('a', attrs={'class': 'name'})
                    print("Match Minute:", event_time.get_text())
                    print("Player:", player.get_text())


def main():

    url = "https://www.premierleague.com/results?team=FIRST&co=1&se=79&cl=-1"

    class_name = "matchFixtureContainer"
    driver = init_driver()
    html = grab_html_by_class(driver, class_name, url)
    soup = BeautifulSoup(html, "html.parser")

    for section in soup.findAll('section', attrs={'class': 'fixtures'}):

        for fixture_date in section.findAll('time', attrs={'class': 'long'}):

            if fixture_date is not None:

                match_date = fixture_date.get_text()
                match_div = section.find('div', attrs={'data-competition-matches-list': fixture_date.get_text()})
                for match in match_div.findAll('li', attrs={"class": "matchFixtureContainer"}):

                    span_score = match.find('span', attrs={"class": "score"})

                    match_id = match['data-comp-match-item']
                    home_team = match['data-home']
                    away_team = match['data-away']
                    score = span_score.get_text()
                    match_url = 'https://www.premierleague.com/match/'+ match_id

                    print(match_date, home_team, score, away_team)

                    fetch_game_info(driver, match_url)
                    return

    driver.quit()


if __name__ == "__main__":
    main()
