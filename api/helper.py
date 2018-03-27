import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By


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

    element = None
