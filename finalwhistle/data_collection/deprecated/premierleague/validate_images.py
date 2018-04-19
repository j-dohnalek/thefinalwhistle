import json
import requests


JSON_DUMP_PATH = 'cache/json/players_images.json'
URL = 'https://platform-static-files.s3.amazonaws.com/premierleague/photos/players/40x40/{}.png'


def validate():
    """
    Validate if image files actually exist
    :return: void
    """
    validated = {}

    with open(JSON_DUMP_PATH) as jsonfile:
        images = json.load(jsonfile)
        total_scraped = len(images)
        processed = 1
        for name, id in images.items():
            r = requests.get(URL.format(id))

            valid = 'invalid'
            if r.status_code == 200:
                validated[name] = id
                valid = 'valid'

            print('{} .. {} .. {} of {}'.format(URL.format(id),valid, processed, total_scraped))
            processed += 1

        # Write the data to json
        with open(JSON_DUMP_PATH, 'w') as outfile:
            json.dump(validated, outfile, ensure_ascii=False, indent=4)
            print('Writing JSON: {}'.format(JSON_DUMP_PATH))
