import selenium.webdriver
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
import os


class DummyClass():
    text = ""


def clearconsole():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def waitforpage(browser, method, element, click=True):
    i = 0
    while True:
        try:
            i += 1
            e = browser.find_element(method, element)
            time.sleep(1)
        except NoSuchElementException:
            time.sleep(1)
            continue
        else:
            break
    if click:
        e.click()
    return e


def createBrowser(headless):
    s = Service('chromedriver.exe')
    options = Options()
    options.add_argument(
        "user-data-dir=C:/Users/Administrator/AppData/Local/Google/Chrome/User Data/")
    options.add_argument('--profile-directory=Profile 1')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--disable-web-security")

    if headless:
        # make chrome headless
        options.add_argument('headless')

    return selenium.webdriver.Chrome(service=s, options=options)


def shortenlink(old_link, browser=None, bar=None):
    if browser is None:
        browser = createBrowser(True)
    if bar is None:
        bar = DummyClass()

    browser.get("https://www.shorturl.at/")

    s = waitforpage(browser, By.NAME, "u", False)

    s.send_keys(old_link)
    bar.text = "Submit old link to server"
    browser.find_element(By.XPATH, "//input[@value='Shorten URL']").click()
    bar.text = "Request sent for short link"

    new_link = waitforpage(browser, By.ID, 'shortenurl')
    x = new_link.get_attribute('value')

    return "https://"+x
