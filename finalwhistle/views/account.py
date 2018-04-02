from finalwhistle import app
from finalwhistle.models.user import attempt_login, create_new_user
from finalwhistle.views.forms.login import LoginForm
from finalwhistle.views.forms.registration import RegistrationForm
from flask import request, render_template, redirect, url_for
from flask_login import login_required, login_user, logout_user


#################################
# guest account-related routing #
#################################


@app.route('/login', methods=['GET'])
def login():
    login_form = LoginForm()
    return render_template('login.html', form=login_form)


@app.route('/login', methods=['POST'])
def perform_login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        print('login form validated')
        # get login params from request form and attempt to fetch user
        email = request.form['email']
        password = request.form['password']
        user = attempt_login(email, password)
        # if email/password combo valid, log the user in via flask_login method
        if user:
            login_user(user)
            return f'welcome {user.username}'
        else:
            return 'invalid credentials'
    return render_template('login.html', form=login_form)


# testing login required
@app.route('/restricted', methods=['GET'])
@login_required
def restricted():
    return 'restricted page'


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET'])
def register():
    registration_form = RegistrationForm()
    return render_template('register.html', form=registration_form)


@app.route('/register', methods=['POST'])
def perform_registration():
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        # TODO: account creation login
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        # will return user object if account created successfully
        if create_new_user(email=email,
                           username=username,
                           password=password):
            raise NotImplementedError
        else:
            return 'something went wrong and your account wasn\'t created'

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