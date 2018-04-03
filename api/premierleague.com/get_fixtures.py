from bs4 import BeautifulSoup
import json
from datetime import datetime

# MY LIBS ######################################################################


from helper import FireMyFox


# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/results?team=FIRST&co=1&se=79&cl=-1"
JSON_PATH = 'jsondump/fixtures/{}.json'
LAST_WEBSCRAPED_MATCHDAY = 'Saturday 31 March 2018'


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

        event_time = event.find('time', attrs={'class': 'min'})
        if event_time is not None:
            time_of_match = event_time.get_text()
            if '+' in time_of_match:
                time_of_match = time_of_match.split('+')
                match_event['minute'] = time_of_match[0].replace("'", "").strip()
                match_event['additional'] = time_of_match[1].replace("'", "").strip()
            else:
                match_event['minute'] = event_time.get_text().replace("'", "").strip()

        if "Goal" in event_info and "Own" not in event_info:

            scorer = event.find('a', attrs={'class': 'name'})
            assist = event.find('div', attrs={'class': 'assist'})
            match_event['own_goal'] = "false"
            match_event['scorer'] = cleanup(scorer.get_text().replace('\n', '').strip())
            if assist is not None:
                assist = assist.get_text().replace('Ast.', '')
                match_event['assist'] = cleanup(assist.strip())
            else:
                match_event['penalty'] = "true"
            match_info['goals'].append(match_event)

        if "Own Goal" in event_info:

            event_time = event.find('time', attrs={'class': 'min'})
            scorer = event.find('a', attrs={'class': 'name'})
            match_event['scorer'] = cleanup(scorer.get_text().replace('\n', '').strip())
            match_event['own_goal'] = "true"
            match_event['penalty'] = "false"
            match_info['goals'].append(match_event)

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

        if "Card" in event_info:

            if "Red Card" in event_info:
                match_event['card'] = 'red'
            else:
                match_event['card'] = 'yellow'

            player = event.find('a', attrs={'class': 'name'})
            match_event['player'] = cleanup(player.get_text().replace('\n', '').strip())
            match_info['cards'].append(match_event)

    return match_info


def main():
    """
    Load the page with the games, iteratively read the page from top to bottom
    until the last_scraped_matchdate is reached
    """

    # The date for which the last game was obtained
    last_scraped_matchdate = datetime.strptime(LAST_WEBSCRAPED_MATCHDAY, '%A %d %B %Y')

    driver = FireMyFox()
    driver.visit_url(URL)
    driver.wait_for_class("matchFixtureContainer")
    soup = BeautifulSoup(driver.html, "html.parser")

    section = soup.find('section', attrs={'class': 'fixtures'})
    for fixture_date in section.findAll('time', attrs={'class': 'long'}):

        match_date = fixture_date.get_text()
        matchdate = datetime.strptime(match_date, '%A %d %B %Y')

        # If the last webscraped matchdate is reached force the program to terminate
        if last_scraped_matchdate == matchdate:
            print('Process complete')
            return

        matches = section.find('div', attrs={'data-competition-matches-list': match_date})
        match_container = {}  # Clear the data written to JSON
        match_container[match_date] = []

        for match in matches.findAll('li', attrs={"class": "matchFixtureContainer"}):

            score = match.find('span', attrs={"class": "score"})
            match_id = match['data-comp-match-item']
            match_url = 'https://www.premierleague.com/match/'+match_id
            match_info = {'goals': [], 'cards': [], 'substitutions': []}

            game_info = {
                'home_team': match['data-home'],
                'away_team': match['data-away'],
                'score': score.get_text(),
                'url': match_url,
                'details': fetch_game_info(match_url, match_info),
            }

            match_container[match_date].append(game_info)

        # Write the data to json for all matches on a particular day
        timestamp = int(matchdate.timestamp())
        path = JSON_PATH.format("{}-MatchesOn-{}-{}-{}".format(
            timestamp, matchdate.day, matchdate.month, matchdate.year
        ))

        with open(path, 'w') as outfile:
            values = [{"date": k, "fixtures": v} for k, v in match_container.items()]
            json.dump(values, outfile, ensure_ascii=False, indent=4)
            print('Writing JSON: {}'.format(path))


if __name__ == "__main__":
    main()
