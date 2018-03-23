from flask import request
from finalwhistle import app
import rendering_methods as rm


@app.route('/')
def homepage():
    rm.render_homepage()


@app.route('/test')
def test():
    return 'Hello'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        rm.render_login_form()
    elif request.method == 'POST':
        rm.perform_user_login()