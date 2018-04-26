from finalwhistle import app
from finalwhistle.models.user import attempt_login, create_new_user, get_user_by_email
from finalwhistle.views.forms.login import LoginForm
from finalwhistle.views.forms.registration import RegistrationForm
from finalwhistle.views.data_views_helper import get_all_teams, get_league_table
from finalwhistle.views.forms.edit_account_info import EditAccountInfo
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user


#################################
# guest account-related routing #
#################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        print('login form validated')
        # get login params from request form and attempt to fetch user
        email = request.form['email']
        password = request.form['password']
        # if email/password combo valid, log the user in via flask_login method
        user = attempt_login(email, password)
        if user is not None:
            login_user(user)
            return redirect(url_for('home'))
        else:
            error = "Invalid email or password, please try again"
            return render_template('login.html', login_form=login_form, user_error=error)
    if request.method == 'POST':
        print('login form posted but did not pass validate_on_submit()')
        print(request.form)
    return render_template('login.html', login_form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        new_user = create_new_user(request.form['email'],
                                   request.form['username'],
                                   request.form['password'],
                                   request.form['real_name'])
        if new_user is not None:
            # TODO: alert/flash message for successfully created account
            flash('Account created! You may now log in')
            return redirect(url_for('login'))
        else:
            return 'something went wrong and your account wasn\'t created'
    else:
        print('login form received but did not pass validate_on_submit()')
        print(request.form)
    return render_template('register.html', reg_form=registration_form)


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


@app.route('/account', methods=['GET'])
@login_required
def edit_profile():
    profile_form = EditAccountInfo()
    return render_template('account.html', profile_form=profile_form)


@app.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def view_profile(id):
    return f'view user profile {id}'