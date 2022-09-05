import datetime
import selenium.webdriver
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tabulate import tabulate
from rich.console import Console


def clearconsole():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def menugen(options):
    print= Console().print

    while True:
        clearconsole()
        for i in range(len(options)):
            print(f"{i+1} {options[i]}")

        user_input = (input("\nEnter your choice: "))

        try:
            user_input = int(user_input)

        except ValueError:
            print("Not a valid integer. Try again.", style="bold red")
            time.sleep(0.4)
            continue
        else:
            if type(user_input) != int:
                print("Not a valid integer. Try again.", style="bold red")
                time.sleep(0.4)
                continue
            elif user_input < 1 or user_input > len(options):
                print("Not a valid option. Try again.", style="bold red")
                time.sleep(0.4)
                continue
            else:
                print("You have selected option: ", user_input, style="bold green")
                break

        
    return user_input

def get_gdrive_service():
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    return build('drive', 'v3', credentials=creds)


class DummyClass():
    text = ""

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


def remove_serial(line, fl):
    _ = 0
    if fl:
        _ += 1
    rest_line = ""
    for i in line.split("|")[3+_:]:
        rest_line += i + "|"
    return line.split("|")[0+_] + "|" + line.split("|")[1+_] + "|" + line.split("|")[2+_].split(" -")[-1] + "|" + rest_line


def createBrowser(headless):
    s = Service('chromedriver.exe')
    options = Options()
    options.add_argument(
        "user-data-dir=C:/Users/Administrator/AppData/Local/Google/Chrome/User Data/")
    options.add_argument('--profile-directory=Profile 1')
    # options.add_experimental_option('excludeSwitches', ['enable-logging'])
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


def mdtocsv(csv, show_serials=True, folder_name=False, folder_path=False):

    lines = []
    for line in csv.split("\n"):
        lines.append(line.replace('"', '').replace(", 20", " "))
    del lines[0]

    data = {
        'folder_name': [],
        'folder_path': [],
        'file_name': [],
        'download_link': [],
        'file_size': [],
        'created_at': []
    }

    table = []
    headers = ['S.No.', 'folder_name', 'folder_path',
               'file_name', 'download_link', 'file_size', 'created_at']

    if not folder_name:
        headers.remove('folder_name')

    if not folder_path:
        headers.remove('folder_path')

    if show_serials:
        serials = []
        for i in range(len(lines)):
            serials.append(i)
        data['S.No.'] = serials

    else:
        headers.remove('S.No.')

    for line in lines:
        _ = line.split(',')
        data['folder_name'].append(_[0])
        data['folder_path'].append(_[1])
        data['file_name'].append(_[2])
        data['download_link'].append(_[3])
        data['file_size'].append(_[4])
        data['created_at'].append(_[5])

        if show_serials:
            record = [lines.index(line)]
            fl = 1
        else:
            record = []
            fl = 0

        for i in _:
            record.append(i)

        if not folder_name:
            del record[fl+1]

        if not folder_path:
            del record[fl+2]

        table.append(record)

    table = tabulate(table, headers, tablefmt='github')

    return table


# Create a function that takes in bytes as input and returns the value in kilobytes, megabytes, or gigabytes accordingly

def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    
# Create a function that takes in 2022-08-27T12:47:08 and returns the date in the format August 25, 2022 at 12:05:04 PM

def convert_date(date_time):
    date_time =date_time.split('.')[0]

    date_time = date_time.split("T")
    date = date_time[0].split("-")
    time = date_time[1].split(":")
    date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))
    date = date.strftime("%B %d, %Y at %I:%M:%S %p")
    return date