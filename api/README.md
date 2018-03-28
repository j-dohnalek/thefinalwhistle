# Web Scraping Routines

## Resource
### Beautiful-soup
https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3
### Selenium
http://www.techbeamers.com/selenium-webdriver-python-tutorial/

## Folders
* json/
..* club_ids.json
..* clubs_and_stadiums.json
..* fixtures_upon_28-March-2018.json
..* managers.json
* json/players/
..* see for you self
## Files
### get_clubs_and_stadiums.py
Fetch all clubs and stadium they play on include club API id (API premier league uses to reference teams)
### get_fixtures.py
Fetch all the required data from premierleague.com for premier league matches. The data will include goals, cards, substitutions, etc.
### get_managers.py
Fetch all managers and clubs they manage
### get_players.py
Fetch all clubs, foreach club list all player with few details (dob, dress number, weight, nationality, height)
