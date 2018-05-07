from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# MY LIBS ######################################################################

from finalwhistle.data_collection.premierleague.helper import MyDriver
from finalwhistle.data_collection.premierleague.helper import FireMyFox


# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/results?team=FIRST&co=1&se=79&cl=-1"
ROOT = "{}/".format(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'football_data', 'json')))
JSON_PATH = ROOT + 'new_fixtures/{}.json'
FIXTURE_CACHE = ROOT + 'fixture.cache.json'


# FUNCTIONS ####################################################################


def cleanup(name):
    """
    Cleanup the name if it contains the shirt number
    :param name player name
    :return name removed of dress number
    """
    if name.find('.') is not -1:
        return name.split('.')[1].strip()
    return name


def fetch_game_info(match_url, match_info):
    """
    Fetch a particular game details
    :param match_url:   url to the match page
    :param match_info:  Container to store details
    """
    my_driver = MyDriver()
    driver = my_driver.driver
    driver.get(match_url)
    # print("Visiting", match_url)

    element = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//main[@id='mainContent']/div/section/div[2]/div[2]/div/div/div/ul/li[3]"))
    )
    element.click()
    soup = BeautifulSoup(driver.page_source, "html.parser")

    referee = soup.find('div', attrs={'class': 'referee'})
    if referee is not None:
        match_info['referee'] = referee.get_text().replace('\n', '').strip()
    else:
        match_info['referee'] = "Uknown"

    kick_off = soup.find('strong', attrs={'class': 'renderKOContainer'})
    if kick_off is not None:
        match_info['kick_off'] = kick_off.get_text()

    for event_line in soup.findAll('div', attrs={'class': 'eventLine'}):
        for event in event_line.findAll('div', attrs={'class': 'event'}):
            match_info = parse_events(event, match_info)

    statistics = {}

    stats_table_body = soup.find('tbody', attrs={'class': 'matchCentreStatsContainer'})
    for stats_tr in stats_table_body.findAll('tr'):

        index = 0
        stat_index, home_stat, away_stat = '', '', ''
        for col in stats_tr.findAll('td'):
            if index == 0:
                home_stat = col.get_text().strip()
            elif index == 1:
                stat_index = col.get_text().strip().lower().replace('%', 'percent').replace(' ', '_')
            elif index == 2:
                away_stat = col.get_text().strip()
            else:
                break
            index += 1

            # Endfor

        statistics[stat_index] = dict(home=home_stat, away=away_stat)

    try:
        statistics['shots_on_target']
    except KeyError:
        import sys
        print("Could not download statistics from", match_url, ", please try again later")
        import sys
        sys.exit(0)

    match_info['statistic'] = statistics

    driver.close()
    return match_info


def parse_events(event, match_info):
    """
    Parse the events (Goals, Cards, Substitutions)
    :param event fixture event to parse
    :param match_info storage container with all events
    :return dictionary with events
    """
    event_type = event.find('span', attrs={'class': 'visuallyHidden'})
    if event_type is not None:

        event_info = event_type.get_text()
        match_event = {}

        # Parse the minute with possible additional time information
        # ----------------------------------------------------------
        event_time = event.find('time', attrs={'class': 'min'})
        if event_time is not None:
            time_of_match = event_time.get_text()
            if '+' in time_of_match:
                time_of_match = time_of_match.split('+')
                match_event['minute'] = time_of_match[0].replace("'", "").strip()
                match_event['additional'] = time_of_match[1].replace("'", "").strip()
            else:
                match_event['minute'] = event_time.get_text().replace("'", "").strip()

        # Player scored goal by normal means or by penalty
        # ------------------------------------------------
        if 'Goal' in event_info and 'Own' not in event_info:

            match_event['own_goal'] = "false"
            match_event['penalty'] = "false"

            scorer = event.find('a', attrs={'class': 'name'})
            match_event['scorer'] = cleanup(scorer.get_text().replace('\n', '').strip())

            assist = event.find('div', attrs={'class': 'assist'})
            if assist is not None:
                assist = assist.get_text().replace('Ast.', '')
                match_event['assist'] = cleanup(assist.strip())

            match_info['goals'].append(match_event)

        # Player scored goal by penalty
        # -----------------------------
        elif 'penalty' in event_info:

            match_event['own_goal'] = "false"
            match_event['penalty'] = "true"

            scorer = event.find('a', attrs={'class': 'name'})
            match_event['scorer'] = cleanup(scorer.get_text().replace('\n', '').strip())

            match_info['goals'].append(match_event)

        # Player scored own goal
        # ----------------------
        elif "Own Goal" in event_info:

            match_event['own_goal'] = "true"
            match_event['penalty'] = "false"

            scorer = event.find('a', attrs={'class': 'name'})
            match_event['scorer'] = cleanup(scorer.get_text().replace('\n', '').strip())

            match_info['goals'].append(match_event)

        # Match substitutions
        # -------------------
        if "Substitution" in event_info:

            sub_on = event.find('div', attrs={'class': 'subOn'})
            # Player might be only taken out due to injury
            if sub_on is not None:
                player_in = sub_on.find('a', attrs={'class': 'name'})
                unwanted = player_in.find('div', attrs={'class': 'icn'})
                if unwanted is not None:
                    unwanted.extract()
                substituted_in = player_in.get_text().replace('\n', '')
                match_event['in'] = cleanup(substituted_in.strip())

            player_out = event.find('a', attrs={'class': 'name'})
            unwanted = player_out.find('div', attrs={'class': 'icn'})
            if unwanted is not None:
                unwanted.extract()

            substituted_out = player_out.get_text().replace('\n', '').strip()
            match_event['out'] = cleanup(substituted_out.strip())
            match_info['substitutions'].append(match_event)

        # Red and Yellow cards
        # --------------------
        if "Card" in event_info:

            if "Red Card" in event_info:
                match_event['card'] = 'red'
            else:
                match_event['card'] = 'yellow'

            player = event.find('a', attrs={'class': 'name'})
            match_event['player'] = cleanup(player.get_text().replace('\n', '').strip())
            match_info['cards'].append(match_event)

    return match_info


def get_collected_match_day():
    """
    tmp folder contains the cache of all match days and corresponding urls to matches
    for which the data was collected. Seach overt the cache and compute highest match
    day by timestamp
    Allow to scrape everything after the highest match day
    return: last cached match day
            dictionary of all cached matches to updated the dictionary with new matches
    """

    # Load cache from the tmp folder
    with open(FIXTURE_CACHE) as outfile:
        cached_fixtures = json.load(outfile)

    return cached_fixtures


def get_fixtures():
    """ Scrape all fixtures """

    # See the function description
    collected_match_days = get_collected_match_day()

    # Open web driver
    driver = FireMyFox()
    driver.visit_url(URL)
    driver.wait_for_class("matchFixtureContainer")

    # Initialise BeautifulSoup to scrape the collected page
    soup = BeautifulSoup(driver.html, "html.parser")
    section = soup.find('section', attrs={'class': 'fixtures'})

    # Iterate over each match day
    for fixture_date in section.findAll('time', attrs={'class': 'long'}):

        match_date = fixture_date.get_text()
        match_day = datetime.strptime(match_date, '%A %d %B %Y')

        # The script have reached a day for which the data was already
        # collected, assuming the page is in order from newest to oldest
        # the data was also collected for the dates older than last match day
        # stop the collection
        try:
            if collected_match_days[match_day.strftime("%d-%m-%Y")] == 'Visited':
                pass

        except KeyError:
            # Key is not present
            collected_match_days[match_day.strftime("%d-%m-%Y")] = 'Visited'

            # Clear the data written to JSON
            match_container = {match_date: []}

            # Iterate over all games on match day
            matches = section.find('div', attrs={'data-competition-matches-list': match_date})
            for match in matches.findAll('li', attrs={"class": "matchFixtureContainer"}):

                score = match.find('span', attrs={"class": "score"})
                match_id = match['data-comp-match-item']
                match_url = 'https://www.premierleague.com/match/'+match_id
                match_info = {'goals': [], 'cards': [], 'substitutions': []}

                # collect information about game
                game_info = {'home_team': match['data-home'], 'away_team': match['data-away'], 'score': score.get_text(),
                             'url': match_url, 'details': fetch_game_info(match_url, match_info)}

                # Store the new data to be written to JSON
                match_container[match_date].append(game_info)

            # Write the data to json for all matches on a particular day
            timestamp = int(match_day.timestamp())
            path = JSON_PATH.format("{}-MatchesOn-{}-{}-{}".format(
                timestamp, match_day.day, match_day.month, match_day.year
            ))

            # Record the standard matches information
            with open(path, 'w') as outfile:
                values = [{"date": k, "fixtures": v} for k, v in match_container.items()]
                json.dump(values, outfile, ensure_ascii=False, indent=4)

        # Update the cache file with the newly sourced matches
        with open(FIXTURE_CACHE, 'w') as outfile:
            json.dump(collected_match_days, outfile, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    get_fixtures()
