import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager

# Create server and configure
app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Try to fetch secret key from OS
try:
    app.config['SECRET_KEY'] = os.environ['FINALWHISTLE_SECRET_KEY']
except KeyError:
    # If cannot find secret key, exit unless in debug mode
    if app.debug:
        app.config['SECRET_KEY'] = 'debug-key'
    else:
        print('Trying to run outside of debug mode without OS provided secret key, exiting')
        exit(1)

# Initialise Flask extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
login = LoginManager(app)

# tell flask_login which view to redirect users to when they need to log in
login.login_view = 'login'

@login.user_loader
def load_user(user_id):
    from finalwhistle.models.user import user_from_id
    return user_from_id(user_id)

# Register url routes with app object [1]
# [1]: http://flask.pocoo.org/docs/0.12/patterns/packages/#simple-packages
import finalwhistle.views.account
import finalwhistle.views.admin
import finalwhistle.views.data_views
import finalwhistle.views.editor
import finalwhistle.views.misc

# Import all models to ensure they're loaded
# This shouldn't be required later on once all models are referenced in other parts of the app
# but for creating and testing a db, this works for now
import finalwhistle.models.user
import finalwhistle.models.comment
import finalwhistle.models.user
import finalwhistle.models.article
