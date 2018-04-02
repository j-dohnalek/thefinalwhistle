#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#
#   COMP208 Final Whistle Project
#
#   Store the general functions for webscraping of key information from websites
#
################################################################################


from selenium.webdriver import Firefox
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
import time


# CONSTANTS ####################################################################


SCROLL_PAUSE_TIME = 1
DEBUG = True


# FUNCTIONS ####################################################################


def init_driver():
    """
    Initialise the Firefox GeckoDriver
    """
    if DEBUG:
        print("Opening Firefox GeckoDriver")

    options = Options()
    options.add_argument('-headless')
    return Firefox(executable_path='./geckodriver', firefox_options=options)


def grab_html_by_class(driver, class_name, url, leave_open=False, scroll=True):
    """
    :param driver       : Firefox GeckoDriver
    :param class_name   : Wait for class attribute name before fetching HTML
    :param url          : Source URL
    :param leave_open   : Do not close the Firefox GeckoDriver, default=False
    :param scroll       : Allow to toggle scrolling to bottom of the page
    """

    if DEBUG:
        print("Visiting url:", url)

    driver.get(url)

    # Attempt to load page several times
    attempts_to_load = 0
    while attempts_to_load < 5:
        # Scroll to the bottom of page
        if scroll:
            scroll_to_bottom(driver, SCROLL_PAUSE_TIME)
        # Search for a class
        try:
            wait_for_html_class(driver, class_name, 10)
            break
        except TimeoutException:
            if DEBUG:
                print("Couldn't find class {}".format(class_name))
            pass
        attempts_to_load += 1

    html = driver.page_source
    if not leave_open:
        driver.quit()

    return html


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


def wait_for_html_class(driver, page_element, timeout):
    """
    Allow the script to wait for HTML class to appear on page
    :param page_element: HTML class attribute
    :param driver: Selenium WebDriver
    :return True if success, else throws TimeoutException
    """
    print("Waiting for class", page_element, "to appear")

    element = WebDriverWait(driver, timeout).until(
       EC.presence_of_element_located((By.CLASS_NAME, page_element))
    )

    return True
