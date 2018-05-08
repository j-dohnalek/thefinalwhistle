from finalwhistle.data_collection.premierleague import fixtures as ws
import unittest


class ScrapeTest(unittest.TestCase):

    match_url = "https://www.premierleague.com/match/22648"

    expected_info = {
        "substitutions": [
            {"out": "Tom Davies","in": "Dominic Calvert-Lewin", "minute": "53" },
            {"out": "Ramadan Sobhi", "in": "Eric Maxim Choupo-Moting", "minute": "72"},
            {"out": "Xherdan Shaqiri", "in": "Saido Berahino", "minute": "76"},
            {"out": "Eric Maxim Choupo-Moting", "in": "Jesé", "minute": "79"},
            {"out": "Wayne Rooney", "in": "Morgan Schneiderlin", "minute": "87"},
            {"out": "Yannick Bolasie", "in": "Mason Holgate", "additional": "2", "minute": "90"}
        ],

        "goals": [
            {"assist": "Dominic Calvert-Lewin", "own_goal": "false", "scorer": "Cenk Tosun", "minute": "69" },
            {"assist": "Joe Allen", "own_goal": "false", "scorer": "Eric Maxim Choupo-Moting", "minute": "77"},
            {"assist": "Theo Walcott", "own_goal": "false", "scorer": "Cenk Tosun", "minute": "84" }
        ],
        "referee": "Martin Atkinson",
        "kick_off": "15:00",
        "cards": [
            {"player": "Charlie Adam", "card": "red", "minute": "30"},
            {"player": "Ryan Shawcross", "card": "yellow", "minute": "55"},
            {"player": "Phil Jagielka", "card": "yellow", "minute": "82"}
        ]
    }

    match_info = {'goals': [], 'cards': [], 'substitutions': []}

    ignore_setup = False

    @classmethod
    def setUpClass(cls):
        cls.match_info = ws.fetch_game_info(cls.match_url, cls.match_info)

    def test_referee_scraping(self):
        self.assertEqual(self.match_info['referee'], self.expected_info['referee'])

    def test_kickoff_scraping(self):
        self.assertEqual(self.match_info['kick_off'], self.expected_info['kick_off'])

    def test_scraped_substitutions(self):
        self.assertEqual(len(self.match_info['substitutions']), 6)

    def test_scraped_goals(self):
        self.assertEqual(len(self.match_info['goals']), 3)

    def test_scraped_cards(self):
        self.assertEqual(len(self.match_info['cards']), 3)


class ScrapingCleanupTest(unittest.TestCase):

    def test_cleanup(self):
        name = '15. Name Surname'
        clean_up_name = ws.cleanup(name)
        self.assertEqual(clean_up_name, 'Name Surname')


if __name__ == '__main__':
    unittest.main()

