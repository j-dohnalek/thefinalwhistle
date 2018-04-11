import http.client
import json
from pathlib import Path


API_TOKEN = 'ac6a29cb48594f87a2c770e05b4d6b35'
CACHE_PATH = 'cache/'


def url_to_filename(name):
    return name[1:].replace('/', '.').replace('?', '-').replace('=', '@')


def fetch_api_data(url, override=False):

    filepath = url_to_filename(url)+'.json'
    my_file = Path(CACHE_PATH+filepath)

    # Check for the cached version exists
    if not my_file.is_file() or override:

        print("Fetching online ...")
        connection = http.client.HTTPConnection('football_data')
        headers = {'X-Auth-Token': API_TOKEN, 'X-Response-Control': 'minified'}
        connection.request('GET', url, None, headers)
        reply = connection.getresponse().read()
        response = json.loads(reply.decode())
        write_to_json(CACHE_PATH, filepath, response)

    else:

        print("Fetching cached ...")
        with open(CACHE_PATH+filepath) as json_data:
            response = json.load(json_data)

    return response


def write_to_json(directory, filename, data):
    """
    Write the data to json
    :param directory
    :param filename
    :param data
    """
    with open(directory + filename, 'w') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
        print('Writing JSON: {}'.format(directory + filename))


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
