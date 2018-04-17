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
    def test_add_users(self):
        from finalwhistle.models.user import User
        users = [User('tom@tom.123', 'tom', 'tom'),
                 User('jiri@jiri.123', 'jiri', 'jiri')
                 ]
        db.session.bulk_save_objects(users)
        assert User.query.count() == len(users)


if __name__ == '__main__':
    unittest.main()