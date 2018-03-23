from finalwhistle import app


@app.route('/', methods=['GET'])
def home():
    return 'home'


@app.route('/login', methods=['GET'])
def render_login():
    return 'login get'


@app.route('/login', methods=['POST'])
def perform_login():
    return 'login post'
