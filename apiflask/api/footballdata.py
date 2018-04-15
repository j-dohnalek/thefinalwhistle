from api import apilib


EPL = 445  # English Premier League 2017-2018


def get_league_table():
    source = '/v1/competitions/{}/leagueTable'.format(EPL)
    return apilib.fetch_api_data(source, 10)


def get_all_teams():
    source = '/v1/competitions/{}/teams'.format(EPL)
    return apilib.fetch_api_data(source, 60)




