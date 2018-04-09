from flask import Flask
from football import db
import os


def create_app():
    # Create server and configure
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'test.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'debug-key'
    db.init_app(app)
    return app


if __name__ == '__main__':
    create_app().run()
