from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import csv
from bs4 import BeautifulSoup


if __name__ == "__main__":
    
    options = Options()
    options.add_argument('-headless')
    driver = Firefox(executable_path='./geckodriver', firefox_options=options)

    #driver.set_window_size(1,0)

    driver.get("https://www.premierleague.com/managers")
    element = WebDriverWait(driver, 3).until(
       EC.presence_of_element_located((By.CLASS_NAME, "managerName"))
    )

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")

    found_data = ""
    parsed_lines = 1
    for body in soup.findAll('tbody', attrs={'class': 'dataContainer'}):

        for td in body.findAll('td'):

            try:
                unwanted = td.find('span',attrs={'short'})
                unwanted.extract()
            except AttributeError:
                pass

            found_data += td.text.strip() + ","

            if parsed_lines % 3 == 0:
                found_data += "|"

            parsed_lines += 1


    found_managers = found_data.split("|")[:-1]

    with open('eggs.csv', 'w') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        for manager in found_managers:
            manager = manager.split(',')[:-1]
            spamwriter.writerow(manager)
