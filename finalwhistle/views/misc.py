from flask import render_template

from finalwhistle import app
from finalwhistle.views.data_views import get_league_table
from finalwhistle.views.misc_helper import validate_contact_us

################
# misc routing #
################


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', table=get_league_table())


@app.route('/terms-of-service', methods=['GET'])
def terms_of_service():
    return render_template('terms.html')

@app.route('/privacy-policy', methods=['GET'])
def privacy_policy():
    return render_template('privacy_policy.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/contact-us', methods=['GET', 'POST'])
def contact_us():
    notification = validate_contact_us()
    return render_template('contact.html', notification=notification)


@app.route('/404', methods=['GET'])
def error_404():
    return render_template('404.html')


@app.route('/500', methods=['GET'])
def error_500():
    return render_template('500.html')
