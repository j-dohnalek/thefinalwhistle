from premierleague import helper
from flask_config import app as srv

import unittest
import urllib.request as urllib2
from flask_testing import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

# https://pythonhosted.org/Flask-Testing/


@srv.route("/test")
def temp_page():
    """
    Set up temporary website to be scraped
    :return: test HTML
    """
    return '<div class="test">OK</div>'


class MyDriverTest(unittest.TestCase):

    @staticmethod
    def test_driver():
        my_driver = helper.MyDriver()
        assert type(my_driver.driver) == WebDriver


class FireMyFoxTest(LiveServerTestCase):

    def create_app(self):
        app = srv
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 9000
        app.config['LIVESERVER_TIMEOUT'] = 10
        return app

    def test_server_is_up_and_running(self):
        response = urllib2.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

    def test_html_fetch(self):
        my_fox = helper.FireMyFox()
        my_fox.visit_url('{}/test'.format(self.get_server_url()))
        my_fox.wait_for_class("test")
        my_fox.set_timeout(2)
        self.assertEqual(my_fox.html, '<html><head></head><body><div class="test">OK</div></body></html>')


if __name__ == '__main__':
    unittest.main()