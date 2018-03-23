from finalwhistle import app


@app.route('/', methods=['GET'])
def home():
    return 'home'


#########################
# login-related routing #
#########################
@app.route('/login', methods=['GET'])
def login():
    return 'login form'


@app.route('/login', methods=['POST'])
def perform_login():
    return 'login post'


@app.route('/register', methods=['GET'])
def register():
    return 'registration form'


@app.route('/register', methods=['POST'])
def perform_registration():
    return 'registration (post)'


@app.route('/reset-password', methods=['GET'])
def reset_password():
    return 'reset password form'


@app.route('/reset-password', methods=['POST'])
def perform_reset_password():
    return 'reset password post'


#####################
# data view routing #
#####################


################
# misc routing #
################
@app.route('/terms-of-service', methods=['GET'])
def terms_of_service():
    return 'terms of service page'


@app.route('/about', methods=['GET'])
def about():
    return 'about page'


@app.route('/contact-us', methods=['GET'])
def contact_us():
    return 'contact us form'


@app.route('/contact-us', methods=['POST'])
def perform_contact_us():
    return 'contact us post'
