from flask import render_template
from flask_mail import Message

from finalwhistle import app, mail
from finalwhistle.views.data_views import get_league_table, list_all_matches
from finalwhistle.views.misc_helper import validate_contact_us

################
# misc routing #
################
@app.route('/', methods=['GET'])
def home():
    from finalwhistle.models.article import get_latest_news
    return render_template('index.html',
                           news=get_latest_news(2),
                           table=get_league_table(),
                           matches=list_all_matches(3),
                           last_match=list_all_matches(1)[0])


@app.route('/terms-of-service', methods=['GET'])
def terms_of_service():
    return render_template('terms.html')


@app.route('/privacy-policy', methods=['GET'])
def privacy_policy():
    return render_template('privacy_policy.html')


@app.route('/community-guidelines', methods=['GET'])
def community_guidelines():
    return render_template('community_guidelines.html')


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


@app.errorhandler(404)
def error_404_2(e):
    return render_template('404.html')


@app.route('/500', methods=['GET'])
def error_500():
    return render_template('500.html')


@app.errorhandler(500)
def error_500_2(e):
    return render_template('500.html')
