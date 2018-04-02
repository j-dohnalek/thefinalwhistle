# premierleague.com DIY API

## Resource
### Beautiful-soup
https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3
### Selenium
http://www.techbeamers.com/selenium-webdriver-python-tutorial/

## Files
### get_clubs.py
Fetch all clubs and their premierleague.com API id
### get_fixtures.py
Fetch all the required data from premierleague.com for premier league matches. The data will include goals, cards, substitutions, etc.
Added functionality: Stop sourcing fixtures if a specified date is reached (i.e. Saturday 31 March 2018)
### get_managers.py
Fetch all managers and clubs they manage
### get_players.py
Fetch all clubs, foreach club list all player with few details (dob, dress number, weight, nationality, height)
### get_referees.py
Fetch all referees of premier league
### get_stadiums.py
Fetch all stadiums the premier league teams play on
