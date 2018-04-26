import os

from finalwhistle.data_collection.premierleague import fixtures
from finalwhistle.data_collection.premierleague import league_table
from finalwhistle.data_collection.json_to_db import parse_new_fixtures, parse_statistics

LEAGUE_TABLE_PATH = '../cache/tmp/table.json'

if __name__ == '__main__':

    # Download latest games
    fixtures.get_fixtures()

    # Insert them into database
    # parse_new_fixtures()

    # Insert match statistics
    # parse_statistics()

    # Download latest league table
    # league_table.get_league_table(LEAGUE_TABLE_PATH)
