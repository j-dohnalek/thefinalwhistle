from server import app
from server import db

from premierleague import get_fixtures


@app.route('/updatefixtures', methods=['GET'])
def update_fixtures():
    get_fixtures.fetch()
    return 'Done'