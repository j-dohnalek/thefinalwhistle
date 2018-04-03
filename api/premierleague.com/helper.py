#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#
#   COMP208 Final Whistle Project
#
#   Store the general classes and functions for webscraping of key information
#   from websites
#
################################################################################


from selenium.webdriver import Firefox
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
import time
import sys


# CONSTANTS ####################################################################


SCROLL_PAUSE_TIME = 1
DEBUG = True


# CLASSES ######################################################################


class MyDriver:
    """ Firefox Gecko Driver Wrapper """

    # Firefox Gecko Driver Options
    __options__ = None

    # Firefox Gecko Driver Object
    __driver__ = None

    def __init__(self):
        """ Initialise Firefox Gecko Driver """
        if DEBUG:
            print("Opening Firefox GeckoDriver")
        self.__options__ = Options()
        self.__options__.add_argument('-headless')
        self.__driver__ = Firefox(executable_path='./geckodriver', firefox_options=self.__options__)

    @property
    def driver(self):
        """
        Get Firefox Gecko Driver Object
        :return Firefox Gecko Driver Object
        """
        return self.__driver__


class FireMyFox():
    """ Load Firefox Gecko Driver open the URL and fetch the HTML page  """

    # Firefox Gecko Driver
    __driver__ = None

    # Leave the Firefox Gecko Driver open
    __leave_open__ = False

    # URL to visit
    __url__ = None

    # Scroll Flag default True
    __scroll__ = True

    # Class attribute name to look out for
    __classattr__ = True

    # Default waiting timeout
    __timeout__ = 10

    # Wait implicit time
    __implicit__ = None

    # Maximum attempts of loading page before terminating
    __max_attempts__ = 3

    def __init__(self):
        geckoDriver = MyDriver()
        self.__driver__ = geckoDriver.driver

    def force_implicit(self, seconds):
        """ Force to wait implicit time to load the page """
        self.__implicit__ = seconds

    def leave_open(self):
        """ Leave the GeckoDriver open """
        self.__leave_open__ = True

    def stop_scroll(self):
        """ Disable scrolling down the page """
        self.__scroll__ = False

    def visit_url(self, url):
        """ URL to visit """
        self.__url__ = url

    def wait_for_class(self, classattr):
        """ Attribute class to wait for """
        self.__classattr__ = classattr

    def set_timeout(self, timeout):
        """ Set own timeout, default 10 """
        self.__timeout__ = timeout

    def close(self):
        """ Close GeckoDriver at any point """
        self.__driver__.quit()

    def wait_to_load(self):
        """
        Allow the script to wait for HTML class to appear on page
        :return True if success, else throws TimeoutException
        """
        if self.__implicit__ is not None:
            if DEBUG:
                print("Waiting implicitly", self.__implicit__, "seconds")
            self.__driver__.implicitly_wait(self.__implicit__)  # seconds
            return True

        try:
            if DEBUG:
                print("Waiting for class", self.__classattr__, "to appear")
            wait = WebDriverWait(self.__driver__, self.__timeout__)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, self.__classattr__)))
            return True

        except TimeoutException:
            if DEBUG:
                print("Couldn't find class {}".format(self.__classattr__))
            return False

    @property
    def html(self):
        """ Fetch HTML of the request page """
        if DEBUG:
            print("Visiting url:", self.__url__)
        self.__driver__.get(self.__url__)

        attempts_to_load = 0      # Monitor the attemtps
        stop_termination = False  # Assume to terminate the script if can not load page
        while attempts_to_load < self.__max_attempts__:
            stop_termination = self.wait_to_load()
            if stop_termination and self.__scroll__:
                scroll_to_bottom(self.__driver__, SCROLL_PAUSE_TIME)
                break
            attempts_to_load += 1

        if not stop_termination:
            print("The failed to load content from {}, terminating program".format(self.__url__))
            sys.exit(0)

        html = self.__driver__.page_source
        if not self.__leave_open__:
            self.close()

        return html


# FUNCTIONS ####################################################################


def scroll_to_bottom(driver, scroll_pause):
    """
    Scroll to the bottom of the page untill it stops loading
    :param driver: Selenium WebDriver
    """

    if DEBUG:
        print("Scrolling to the bottom ...")

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
