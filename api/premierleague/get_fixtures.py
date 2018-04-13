from bs4 import BeautifulSoup
import json
from datetime import datetime

# MY LIBS ######################################################################


from premierleague.helper import FireMyFox


# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/results?team=FIRST&co=1&se=79&cl=-1"
JSON_PATH = 'cache/json/new_fixtures/{}.json'
FIXTURE_CACHE = 'cache/json/fixture.cache.json'


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

    driver = FireMyFox()
    driver.leave_open()
    driver.visit_url(match_url)
    driver.wait_for_class("renderKOContainer")
    soup = BeautifulSoup(driver.html, "html.parser")

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
        if "Goal" in event_info and "Own" not in event_info:

            scorer = event.find('a', attrs={'class': 'name'})
            assist = event.find('div', attrs={'class': 'assist'})
            match_event['own_goal'] = "false"
            match_event['scorer'] = cleanup(scorer.get_text().replace('\n', '').strip())
            if assist is not None:
                assist = assist.get_text().replace('Ast.', '')
                match_event['assist'] = cleanup(assist.strip())
            else:
                # Assuming if there is no assistant to the goal the goal was most
                # likely scored by penalty
                match_event['penalty'] = "true"
            match_info['goals'].append(match_event)

        # Player scored own goal
        # ----------------------
        if "Own Goal" in event_info:

            scorer = event.find('a', attrs={'class': 'name'})
            match_event['scorer'] = cleanup(scorer.get_text().replace('\n', '').strip())
            match_event['own_goal'] = "true"
            match_event['penalty'] = "false"
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


def get_last_collected_match_day():
    """
    tmp folder contains the cache of all match days and corresponding urls to matches
    for which the data was collected. Seach overt the cache and compute highest match
    day by timestamp
    Allow to scrape everything after the highest match day
    return: last cached match day
            dictionary of all cached matches to updated the dictionary with new matches
    """
    last_collected_match_day = None
    collected_fixtures = {}

    # Load cache from the tmp folder
    with open(FIXTURE_CACHE) as outfile:
        cached_fixtures = json.load(outfile)
        max_timestamp = 0
        for fixture in cached_fixtures:
            collected_fixtures[fixture['date']] = fixture['fixtures']
            matchday = datetime.strptime(fixture['date'], '%A %d %B %Y')
            match_timestamp = matchday.timestamp()
            if int(match_timestamp) > max_timestamp:
                max_timestamp = match_timestamp
                last_collected_match_day = matchday

    return last_collected_match_day, collected_fixtures


def fetch():
    """ Scrape all fixtures """

    # See the function description
    last_collected_match_day, collected_fixtures = get_last_collected_match_day()

    # Open webdriver
    driver = FireMyFox()
    driver.visit_url(URL)
    driver.wait_for_class("matchFixtureContainer")

    # Initialise BeautifulSoup to scrape the collected page
    soup = BeautifulSoup(driver.html, "html.parser")
    section = soup.find('section', attrs={'class': 'fixtures'})

    # Iterate over each matchday
    for fixture_date in section.findAll('time', attrs={'class': 'long'}):

        match_date = fixture_date.get_text()
        match_day = datetime.strptime(match_date, '%A %d %B %Y')

        # The script have reached a day for which the data was already
        # collected, assuming the page is in order from newest to oldest
        # the data was also collected for the dates older than last match day
        # stop the collection
        if last_collected_match_day == match_day:
            print("No more data to process, stopping collection ... ")
            break

        # Clear the data written to JSON
        match_container = {match_date: []}

        # Update the cache
        collected_fixtures[match_date] = []

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

            # Update the cache
            collected_fixtures[match_date].append(match_url)

        # Write the data to json for all matches on a particular day
        timestamp = int(match_day.timestamp())
        path = JSON_PATH.format("{}-MatchesOn-{}-{}-{}".format(
            timestamp, match_day.day, match_day.month, match_day.year
        ))

        # Record the standard matches inforation
        with open(path, 'w') as outfile:
            values = [{"date": k, "fixtures": v} for k, v in match_container.items()]
            json.dump(values, outfile, ensure_ascii=False, indent=4)
            print('Writing JSON: {}'.format(path))

    # Update the cache file with the newly sourced matches
    with open(FIXTURE_CACHE, 'w') as outfile:
        values = [{"date": k, "fixtures": v} for k, v in collected_fixtures.items()]
        json.dump(values, outfile, ensure_ascii=False, indent=4)
        print('Writing JSON: {}'.format(FIXTURE_CACHE))


if __name__ == "__main__":
    fetch()
