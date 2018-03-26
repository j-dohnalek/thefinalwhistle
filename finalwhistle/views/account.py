from finalwhistle import app
from finalwhistle.models.user import user_from_email
from flask import request

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


@app.route('/verify-email', methods=['GET'])
def verify_email():
    # get user to verify from url args
    # use direct access to the args dict rather than .get so we can handle the case of missing params via KeyError
    # email = request.args.get('username')
    # token = request.args.get('token')
    try:
        email = request.args['username']
        token = request.args['token']
    except KeyError:
        return "url missing 'username' and 'token' args"
    user = user_from_email(email)
    # attempt to activate account
    if user.activate_account(token):
        return 'your account has been activated and you have been logged in'
    else:
        return 'could not activate account - are you already activated?'


#####################################
# logged in account-related routing #
#####################################
@app.route('/profile/edit', methods=['GET'])
def edit_profile():
    return 'edit own user profile'


@app.route('/profile/<int:user_id>', methods=['GET'])
def view_profile(id):
    return f'view user profile {id}'