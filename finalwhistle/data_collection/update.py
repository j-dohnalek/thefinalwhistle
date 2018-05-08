from finalwhistle.data_collection.premierleague import fixtures, referees, club_staff, players
from finalwhistle.data_collection.premierleague import league_table
from finalwhistle.data_collection.json_to_db import parse_new_fixtures, parse_match_statistics, parse_referee, \
    parse_club_staff, parse_player_statistics, parse_new_players


def update():

    print("Updating referee cache")
    referees.fetch_referees()
    parse_referee()

    print("Updating club staff cache")
    club_staff.fetch_club_staff()
    parse_club_staff()

    print("Updating players cache")
    players.fetch_records()
    parse_new_players()

    print("Updating played match cache")
    fixtures.get_fixtures()
    parse_new_fixtures()

    print("Updating match statistics cache")
    parse_match_statistics()
    parse_player_statistics()

    print("Updating league table cache")
    league_table.get_league_table()


if __name__ == '__main__':
    update()