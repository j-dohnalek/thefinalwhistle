from finalwhistle import app


#####################
# data view routing #
#####################
@app.route('/matches', methods=['GET'])
def matches_overview():
    return 'matches overview'


@app.route('/matches/<id>', methods=['GET'])
def match_page(id):
    return f'match page {id}'


@app.route('/players', methods=['GET'])
def players_overview():
    return 'players overview'


@app.route('/players/<id>', methods=['GET'])
def player_page(id):
    return f'player page {id}'


@app.route('/news', methods=['GET'])
def news_overview():
    return 'news overview'


@app.route('/news/<id>', methods=['GET'])
def news_page(id):
    return f'news page {id}'


@app.route('/teams', methods=['GET'])
def teams_overview():
    return 'teams overview'


@app.route('/teams/<id>', methods=['GET'])
def team_page(id):
    return f'team page {id}'
