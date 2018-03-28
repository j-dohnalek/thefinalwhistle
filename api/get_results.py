from bs4 import BeautifulSoup
import json


# MY LIBS ######################################################################


from helper import grab_html_by_class, init_driver


# CONSTANTS ####################################################################


URL = "https://www.premierleague.com/results?team=FIRST&co=1&se=79&cl=-1"
JSON_PATH = 'json/fixtures/{}.json'


# FUNCTIONS ####################################################################


def fetch_game_info(match_url, match_info):
    """
    Fetch a particular game details
    :param match_url:   url to the match page
    :param match_info:  Container to store details
    """
    driver = init_driver()
    html = grab_html_by_class(driver, "renderKOContainer", match_url)
    soup = BeautifulSoup(html, "html.parser")

    referee = soup.find('div', attrs={'class': 'referee'})
    if referee is not None:
        match_info['referee'] = referee.get_text().replace('\n', '').strip()

    kick_off = soup.find('strong', attrs={'class': 'renderKOContainer'})
    if kick_off is not None:
        match_info['kick_off'] = kick_off.get_text()

    for event_line in soup.findAll('div', attrs={'class': 'eventLine'}):
        for event in event_line.findAll('div', attrs={'class': 'event'}):
            match_info = parse_events(event, match_info)

    return match_info


def parse_events(event, match_info):
    """
    """
    event_type = event.find('span', attrs={'class': 'visuallyHidden'})
    if event_type is not None:

        event_info = event_type.get_text()
        match_event = {}

        # Clean the unwanted information
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
            match_event['scorer'] = scorer.get_text().replace('\n', '').strip()

            if assist is not None:
                assist = assist.get_text().replace('Ast.', '')
                match_event['assist'] = assist.strip()

            match_info['goals'].append(match_event)

        if "Own Goal" in event_info:

            event_time = event.find('time', attrs={'class': 'min'})
            scorer = event.find('a', attrs={'class': 'name'})

            match_event['scorer'] = scorer.get_text().replace('\n', '').strip()
            match_event['own_goal'] = "true"

            match_info['goals'].append(match_event)

        if "Substitution" in event_info:

            sub_on = event.find('div', attrs={'class': 'subOn'})
            # Player might be only taken out due to injury
            if sub_on is not None:
                player_in = sub_on.find('a', attrs={'class': 'name'})
                unwanted = player_in.find('div', attrs={'class': 'icn'})
                unwanted.extract()
                substituted_in = player_in.get_text().replace('\n', '')

                match_event['in'] = substituted_in.strip()

            player_out = event.find('a', attrs={'class': 'name'})
            unwanted = player_out.find('div', attrs={'class': 'icn'})
            unwanted.extract()
            substituted_out = player_out.get_text().replace('\n', '').strip()

            match_event['out'] = substituted_out.strip()
            match_info['substitutions'].append(match_event)

        if "Card" in event_info:

            if "Yellow Card" in event_info and "Second" not in event_info:
                match_event['card'] = 'yellow'
            elif "Red Card" in event_info:
                match_event['card'] = 'red'

            player = event.find('a', attrs={'class': 'name'})
            match_event['player'] = player.get_text().replace('\n', '').strip()
            match_info['cards'].append(match_event)

    return match_info


def main():

    html = grab_html_by_class(init_driver(), "matchFixtureContainer", URL)
    soup = BeautifulSoup(html, "html.parser")

    match_counter = 1
    section = soup.find('section', attrs={'class': 'fixtures'})
    for fixture_date in section.findAll('time', attrs={'class': 'long'}):

        match_date = fixture_date.get_text()
        matches = section.find('div', attrs={'data-competition-matches-list': match_date})
        for match in matches.findAll('li', attrs={"class": "matchFixtureContainer"}):

            match_data = []

            score = match.find('span', attrs={"class": "score"})
            match_id = match['data-comp-match-item']
            match_url = 'https://www.premierleague.com/match/'+match_id

            match_info = {'goals': [], 'cards': [], 'substitutions': []}
            match_info = fetch_game_info(match_url, match_info)

            game_info = {
                'date': match_date,
                'home_team': match['data-home'],
                'away_team': match['data-away'],
                'score': score.get_text(),
                'details': match_info
            }

            match_data.append(game_info)

            # Write the data to json
            path = JSON_PATH.format("match"+str(match_counter))
            with open(path, 'w') as outfile:
                values = [v for v in match_data]
                json.dump(values, outfile, ensure_ascii=False, indent=4)
                print('Writing JSON: {}'.format(path))
            match_counter += 1
            return


if __name__ == "__main__":
    main()
