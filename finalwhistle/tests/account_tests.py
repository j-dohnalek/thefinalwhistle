# http://www.patricksoftwareblog.com/unit-testing-a-flask-application/
import os
import unittest
from finalwhistle import app, db, mail

TEST_DB = 'unittests.db'


class AccountTests(unittest.TestCase):
    # executed before each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.config['BASEDIR'], TEST_DB)
        self.app = app.test_client()
        # empty db of previous test data
        db.drop_all()
        db.create_all()

        # Disable sending emails during unit testing
        mail.init_app(app)
        self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
        pass

    #########
    # tests #
    #########
