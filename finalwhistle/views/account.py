from finalwhistle import app


#################################
# guest account-related routing #
#################################
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


###################################
# logged in account-related routing #
###################################
@app.route('/edit-profile', methods=['GET'])
def edit_profile():
    return 'edit profile page'


@app.route('/user/<id>', methods=['GET'])
def view_profile(id):
    return f'view user profile {id}'