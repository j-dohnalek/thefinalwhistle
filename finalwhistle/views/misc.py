from flask import render_template

from finalwhistle import app


################
# misc routing #
################
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


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

@app.route('/404', methods=['GET'])
def error_404():
    return render_template('404.html')

@app.route('/500', methods=['GET'])
def error_500():
    return render_template('500.html')
