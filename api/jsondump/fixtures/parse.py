import json
from datetime import datetime


def main():
    with open('list_of_fixtures28032018.json') as json_data:
        fixtures = json.load(json_data)

        match_day = {}
        match = {}

        previous_match_day = None
        for fixture in fixtures:

            if previous_match_day is None:
                match_day[fixture['date']] = []
                previous_match_day = fixture['date']

            if previous_match_day == fixture['date']:
                pass
            else:
                matchday_dt = datetime.strptime(fixture['date'], '%A %d %B %Y')

                timestamp = int(matchday_dt.timestamp())
                path = 'temp/{}-MatchesOn-{}-{}-{}.json'.format(timestamp, matchday_dt.day, matchday_dt.month, matchday_dt.year)
                with open(path, 'w') as outfile:
                    values = [{"date": k, "fixtures": v} for k, v in match_day.items()]
                    json.dump(values, outfile, ensure_ascii=False, indent=4)
                    print('Writing JSON: {}'.format(path))

                match = {}
                match_day = {}
                match_day[fixture['date']] = []

            match['url'] = fixture['url']
            match['score'] = fixture['score']
            match['details'] = fixture['details']
            match['away_team'] = fixture['away_team']
            match['home_team'] = fixture['home_team']

            match_day[fixture['date']].append(match)
            previous_match_day = fixture['date']


if __name__ == "__main__":
    main()
