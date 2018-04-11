# premierleague.com DIY API

## Potential issues
* Not every fixture might contain kick off time
* Not every fixture might contain refferee name
* Not every player has surname, also some players have two names, some have two surnames
* Not every player has all the inforation about weight, height etc.

## Resource
### Beautiful-soup
https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3
### Selenium
http://www.techbeamers.com/selenium-webdriver-python-tutorial/

## Files
### get_clubs.py
One time fetch all clubs and their premierleague.com API id
### get_fixtures.py
Fetch all the required data from premierleague.com for premier league matches. The data will include goals, cards, substitutions, etc.
### get_managers.py
One time fetch all managers and clubs they manage
### get_players.py
One time fetch all clubs, foreach club list all player with few details (dob, dress number, weight, nationality, height)
### get_referees.py
One time fetch all referees of premier league
### get_stadiums.py
One time fetch all stadiums the premier league teams play on
