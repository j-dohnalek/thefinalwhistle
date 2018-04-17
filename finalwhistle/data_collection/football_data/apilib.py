import http.client
import json
from pathlib import Path
import os, time


API_TOKEN = 'ac6a29cb48594f87a2c770e05b4d6b35'
CACHE_PATH = 'cache/tmp/'
API_URL = 'api.football-data.org'
DEBUG = True


def url_to_filename(name):
    """
    Convert the URL to filename
    :param name:
    :return:
    """
    return name[1:].replace('/', '.').replace('?', '-').replace('=', '@')


def fetch_api_data(url, minutes, override=False):
    """
    :param url: API request URL
    :param minutes: time in minutes before the cached file will be updated from API
    :param override:
    :return: JSON Response
    """

    use_by = time.time() - minutes * 60

    filepath = url_to_filename(url)+'.json'
    my_file = Path(CACHE_PATH+filepath)

    # Check for the cached version exists
    if not my_file.is_file() or override or os.path.getatime(CACHE_PATH+filepath) < use_by:

        if DEBUG:
            print("Fetching online ...")

        connection = http.client.HTTPConnection(API_URL)
        headers = {'X-Auth-Token': API_TOKEN, 'X-Response-Control': 'minified'}
        connection.request('GET', url, None, headers)
        reply = connection.getresponse().read()
        response = json.loads(reply.decode())
        write_to_json(CACHE_PATH, filepath, response)

    else:

        if DEBUG:
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
