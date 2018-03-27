import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

# CONSTANTS ####################################################################

SCROLL_PAUSE_TIME = 0.5

# FUNCTIONS ####################################################################


def init_driver():
    """
    Initialise the Firefox GeckoDriver
    """
    print("Opening Driver")
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
    print("Visiting url:", url)
    driver.get(url)

    if scroll:
        scroll_to_bottom(driver, SCROLL_PAUSE_TIME)

    wait_for_html_class(driver, class_name, 10)

    html = driver.page_source
    if not leave_open:
        driver.quit()

    return html


def grab_html_by_xpath(driver, xpath, url, leave_open=False, scroll=True):
    """
    :param driver       : Firefox GeckoDriver
    :param xpath        : Wait for xpath attribute before fetching HTML
    :param url          : Source URL
    :param leave_open   : Do not close the Firefox GeckoDriver, default=False
    :param scroll       : Allow to toggle scrolling to bottom of the page
    """
    print("Visiting url:", url)
    driver.get(url)

    if scroll:
        scroll_to_bottom(driver, SCROLL_PAUSE_TIME)

    wait_for_html_class(driver, xpath, 10)

    html = driver.page_source
    if not leave_open:
        driver.quit()

    return html


def scroll_to_bottom(driver, scroll_pause):
    """
    Scroll to the bottom of the page untill it stops loading
    :param driver: Selenium WebDriver
    """
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

    print("Scrolling complete")


def wait_for_html_class(driver, page_element, timeout):
    """
    Allow the script to wait for HTML class to appear on page
    :param page_element: HTML class attribute
    :param driver: Selenium WebDriver
    """
    print("Waiting ...")
    element = WebDriverWait(driver, timeout).until(
       EC.presence_of_element_located((By.CLASS_NAME, page_element))
    )


def wait_for_xpath(driver, xpath, timeout):
    """
    Allow the script to wait for HTML class to appear on page
    :param page_element: HTML class attribute
    :param driver: Selenium WebDriver
    """
    print("Waiting ...")
    elems = WebDriverWait(driver, timeout).until(
        EC.visibility_of_all_elements_located((By.XPATH, xpath))
    )
