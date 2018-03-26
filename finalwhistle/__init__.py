from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

# Create app server and set configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SECRET_KEY'] = 'debug-key'

# Initialise Flask extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

# Register url routes with app object [1]
# [1]: http://flask.pocoo.org/docs/0.12/patterns/packages/#simple-packages
import finalwhistle.views.account
import finalwhistle.views.admin
import finalwhistle.views.data_views
import finalwhistle.views.editor
import finalwhistle.views.misc