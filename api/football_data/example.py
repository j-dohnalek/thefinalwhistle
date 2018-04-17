
# Fetch team information
# print(fetch_api_data('/v1/teams/{}/players'.format(73)))


# Fetch teams
source = '/v1/competitions/{}/teams'.format(445)
print(fetch_api_data(source))


# Fetch fixtures
source = '/v1/competitions/{}/fixtures'.format(445)
print(fetch_api_data(source))


# Fetch leagueTable
source = '/v1/competitions/{}/leagueTable'.format(445)
print(fetch_api_data(source))
