from football_data import apilib
from football import Team, MatchStatistics, Match


EPL = 445  # English Premier League 2017-2018


def get_league_table():
    source = '/v1/competitions/{}/leagueTable'.format(EPL)
    return apilib.fetch_api_data(source, 10)


def get_all_teams():
    source = '/v1/competitions/{}/teams'.format(EPL)
    return apilib.fetch_api_data(source, 60)


if __name__ == '__main__':

    response = get_all_teams()
    teams = response['teams']
    print(teams)

    response = get_league_table()
    for position in response['standing']:

        team_name = None
        for team in teams:
            if team['id'] == position['teamId']:
                team_name = team['name']

        print('{} {} {} {} {}'.format(team_name,
                                      position['playedGames'],
                                      position['goalsAgainst'],
                                      position['goalDifference'],
                                      position['points']))


