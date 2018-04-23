from finalwhistle import app
from finalwhistle.models.user import attempt_login, create_new_user, get_user_by_email
from finalwhistle.views.forms.login import LoginForm
from finalwhistle.views.forms.registration import RegistrationForm
from flask import request, render_template, redirect, url_for
from flask_login import login_required, login_user, logout_user


#################################
# guest account-related routing #
#################################
@app.route('/login', methods=['GET', 'POST'])
def login():
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
    else:
        print('login form received but did not pass validate_on_submit()')
        print(request.form)
    return render_template('login.html', login_form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        # TODO: account creation login

        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        # will return user object if account created successfully
        new_user = create_new_user(email=email,
                                   username=username,
                                   password=password)
        if new_user is not None:
            return 'new user created'
        else:
            return 'something went wrong and your account wasn\'t created'
    else:
        print('login form received but did not pass validate_on_submit()')
        print(request.form)
    return render_template('register.html', form=registration_form)


# testing login required
@app.route('/restricted', methods=['GET'])
@login_required
def restricted():
    return 'restricted page'


@app.route('/reset-password', methods=['GET'])
def reset_password():
    return 'reset password form'


@app.route('/reset-password', methods=['POST'])
def perform_reset_password():
    return 'reset password post'


@app.route('/verify-email', methods=['GET'])
def verify_email():
    # try:
    #     email = request.args['username']
    #     token = request.args['token']
    # except KeyError:
    #     return "url missing 'username' and 'token' args"
    # cleaner code - check vs None vs catching exceptions
    email = request.args.get('username')
    token = request.args.get('token')
    if email is None or token is None:
        return "url missing 'username' or 'token' args"
    user = get_user_by_email(email)
    # attempt to activate account
    if user is not None:
        if user.activate_account(token):
            return 'your account has been activated and you have been logged in'
        else:
            return 'could not activate account - are you already activated?'
    else:
        return 'could not find user from email address'


#####################################
# logged in account-related routing #
#####################################
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile/edit', methods=['GET'])
@login_required
def edit_profile():
    return 'edit own user profile'


@app.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def view_profile(id):
    return f'view user profile {id}'