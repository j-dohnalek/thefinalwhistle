from pprint import pprint

from finalwhistle import app, db
from finalwhistle.models.user import attempt_login, create_new_user, get_user_by_email, UserNotActivated, UserIsBlocked
from finalwhistle.views.forms.login import LoginForm
from finalwhistle.views.forms.registration import RegistrationForm
from finalwhistle.views.forms.edit_account_info import EditAccountInfoForm, ChangePasswordForm
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
        # get login params from request form and attempt to fetch user
        email = str(request.form['email'])
        password = str(request.form['password'])

        # if email/password combo valid, log the user in via flask_login method
        try:
            user = attempt_login(email, password)

            if user is not None:
                login_user(user)
                return redirect(url_for('home'))

            else:
                error = "Invalid email or password, please try again"
                return render_template('login.html', login_form=login_form, user_error=error)

        except UserNotActivated:
            flash('You must first activate your account through the email you have been sent')
            return redirect(url_for('login'))

        except UserIsBlocked:
            flash('Your account has been disabled, please contact an administrator')
            return redirect(url_for('login'))

    return render_template('login.html', login_form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        new_user = create_new_user(registration_form.data['email'],
                                   registration_form.data['username'],
                                   registration_form.data['password'],
                                   registration_form.data['real_name'])
        if new_user is not None:
            flash('Please activate your account through the email we have sent you before logging in')
            return redirect(url_for('login'))
        else:
            flash('An error occurred when creating your account, please contact an administrator')
            return redirect(url_for('home'))
    return render_template('register.html', reg_form=registration_form)


@app.route('/verify-email', methods=['GET'])
def verify_email():

    # try:
    #     email = request.args['username']
    #     token = request.args['token']
    # except KeyError:
    #     return "url missing 'username' and 'token' args"
    # cleaner code - check vs None vs catching exceptions
    pprint(request.args)

    email = request.args.get('email')
    token = request.args.get('token')
    if email is None or token is None:
        flash('There was an error activating your account')
        return redirect(url_for('home'))
    user = get_user_by_email(email)
    # attempt to activate account
    if user is not None:
        if user.activate_account(token):
            flash('Your account has been activated and you are now logged in!')
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('There was an error activating your account')
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


@app.route('/reset-password', methods=['GET'])
def reset_password():
    return 'reset password form'


@app.route('/reset-password', methods=['POST'])
def perform_reset_password():
    return 'reset password post'


#####################################
# logged in account-related routing #
#####################################
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def edit_profile():
    profile_form = EditAccountInfoForm()
    password_form = ChangePasswordForm()
    # profile form logic
    if profile_form.validate_on_submit():
        new_favourite_team_id = request.form.get('favourite_team')
        new_real_name = request.form.get('real_name')
        if new_favourite_team_id is not (None or ''):
            if current_user.set_supported_team(new_favourite_team_id):
                flash('Supported team updated!')
        if new_real_name is not (None or ''):
            if current_user.set_real_name(new_real_name):
                flash('Name updated!')
    # password form logic
    if password_form.validate_on_submit():
        if current_user.set_password(request.form.get('new_pw')):
            flash('Password changed!')
    else:
        print(password_form.data)
        print(password_form.errors)
    return render_template('account.html', profile_form=profile_form, password_form=password_form)


@app.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def view_profile(id):
    return f'view user profile {id}'