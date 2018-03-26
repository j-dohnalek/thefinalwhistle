from flask import Flask
from flask.ext.bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ensure application url routes are registered with the app object [1]
# [1]: http://flask.pocoo.org/docs/0.12/patterns/packages/#simple-packages
import finalwhistle.views.account
import finalwhistle.views.admin
import finalwhistle.views.data_views
import finalwhistle.views.editor
import finalwhistle.views.misc