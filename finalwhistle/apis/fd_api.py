import http.client
import json
from pathlib import Path
import os, time

# https://stackoverflow.com/questions/9856683/using-pythons-os-path-how-do-i-go-up-one-directory
CACHE_PATH = "{}/".format(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cache', 'tmp')))
API_TOKEN = 'ac6a29cb48594f87a2c770e05b4d6b35'
API_URL = 'api.football-data.org'
DEBUG = False
EPL = 445  # English Premier League 2017-2018


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
    file_path = url_to_filename(url)+'.json'
    my_file = Path(CACHE_PATH+file_path)

    # Check for the cached version exists
    if not my_file.is_file() or override or os.path.getatime(CACHE_PATH+file_path) < use_by:

        if DEBUG:
            print("Fetching online ...")

        connection = http.client.HTTPConnection(API_URL)
        headers = {'X-Auth-Token': API_TOKEN, 'X-Response-Control': 'minified'}
        connection.request('GET', url, None, headers)
        reply = connection.getresponse().read()
        response = json.loads(reply.decode())

        with open(CACHE_PATH + file_path, 'w') as outfile:
            json.dump(response, outfile, ensure_ascii=False, indent=4)
            print('Caching {}'.format(file_path))

    else:
        if DEBUG:
            print("Fetching cached ...")
        with open(CACHE_PATH+file_path) as json_data:
            response = json.load(json_data)
    return response
