from flask import render_template

from finalwhistle import app
from finalwhistle.views.data_views import get_league_table


################
# misc routing #
################
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', table=get_league_table())


@app.route('/terms-of-service', methods=['GET'])
def terms_of_service():
    return 'terms of service page'


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/contact-us', methods=['GET'])
def contact_us():
    return 'contact us form'


@app.route('/contact-us', methods=['POST'])
def perform_contact_us():
    return 'contact us post'

@app.route('/404', methods=['GET'])
def error_404():
    return render_template('404.html')

@app.route('/500', methods=['GET'])
def error_500():
    return render_template('500.html')
