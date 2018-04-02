import json
import os


def cleanup(name):
    """
    Cleanup the name if it contains the shirt number
    :param name player name
    :return name removed of dress number
    """
    if name.find('.') is not -1:
        return name.split('.')[1].strip()
    return name


def main():
    """
    Iterate over each fixture and cleanup player names
    """

    path = 'jsondump/fixtures/'
    for f in list(os.listdir(path)):
        filename = path+f
        with open(filename) as json_data:

            matchday = json.load(json_data)
            for fixtures in matchday:
                for fixture in fixtures['fixtures']:

                    for name in (fixture['details']['goals']):

                        name['scorer'] = cleanup(name['scorer'])

                        try:
                            name['assist'] = cleanup(name['assist'])
                        except KeyError:
                            pass

                    for name in (fixture['details']['cards']):
                        name['player'] = cleanup(name['player'])

                    for name in (fixture['details']['substitutions']):
                        name['out'] = cleanup(name['out'])

                        try:
                            name['in'] = cleanup(name['in'])
                        except KeyError:
                            pass

            with open(filename, 'w') as outfile:
                json.dump(matchday, outfile, ensure_ascii=False, indent=4)
                print('Writing JSON: {}'.format(filename))


if __name__ == "__main__":
    main()
