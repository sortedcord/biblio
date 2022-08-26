import time
import selenium.webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from alive_progress import alive_bar
import os
import glob


with alive_bar(spinner="twirls") as bar:

    bar.text("Starting Chrome")
    s = Service('chromedriver.exe')
    options = Options()
    options.add_argument(
        "user-data-dir=C:/Users/Administrator/AppData/Local/Google/Chrome/User Data/")
    options.add_argument('--profile-directory=Profile 1')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--disable-web-security")
    # make chrome headless
    # options.add_argument('headless')

    browser = selenium.webdriver.Chrome(service=s, options=options)
    bar()

    file_name = 'target.md'

    # folder_id = input("Enter folder id: ")
    bar.text("Loading Drive Explorer")
    browser.get(r"https://syncwithtech.com/drive?state=%7B%22ids%22:%5B%221GOOTF_FNvpgfe2ZVQU8Rx2u5eUgJ4waA%22%5D,%22action%22:%22open%22,%22userId%22:%22100758669744711932203%22,%22resourceKeys%22:%7B%7D%7D")

    # Wait until a span saying "FILE NAME" is found and then click it
    while True:
        try:
            browser.find_element(By.XPATH, "//span[contains(text(), 'File name')]").click()
        except NoSuchElementException:
            time.sleep(1)
        else:
            break
    bar()

    bar.text("Fetching CSV")
    # Click a span containing text "Export CSV"
    browser.find_element(By.XPATH, "//span[contains(text(), 'Export CSV')]").click()

    # Get the downloads folder
    downloads_folder = os.path.join(os.environ['USERPROFILE'], 'Downloads')

    # Get the last downloaded file in the downloads folder
    time.sleep(0.5)
    list_of_files = glob.glob(f"C:/Users/{os.environ['USERNAME']}/Downloads/*") # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)

    # Move the latest file to current directory as table.csv
    os.system(f"move {latest_file} table.csv")

    # Read table.csv file
    with open('table.csv', 'r') as file:
        csv_data = file.read()
    
    bar()

    bar.text("Loading CSV Convertor")
    browser.get("https://www.convertcsv.com/csv-to-markdown.htm")

    # Wait until textarea is loaded and then enter csv_data into it
    while True:
        try:
            textarea = browser.find_element(By.XPATH, "//textarea")
            textarea.send_keys(csv_data)
        except NoSuchElementException:
            time.sleep(1)
        else:
            break
    bar()

    bar.text("Converting CSV to Markdown")
    # Find all spans with class name 'glyphicon glyphicon-chevron-down'
    spans = browser.find_elements(By.XPATH, "//span[@class='glyphicon glyphicon-chevron-down']")

    for span in spans:
        time.sleep(0.7)
        while True:
            try:
                span.click()
            except ElementClickInterceptedException:
                time.sleep(1)
            else:
                break
        
    with bar.pause():
        _  = input("Do you want to show folder name in table? (y/n)")
    if _ == 'y':
        input_headers = "1,3,4,5,6"
    else:
        input_headers = "3,4,5,6"

    # click on an input with id as  "txtCols"
    browser.find_element(By.ID, "txtCols").click()

    # Clear the text in the input with id as "txtCols"
    browser.find_element(By.ID, "txtCols").clear()

    # Enter the headers in the input with id as "txtCols"
    browser.find_element(By.ID, "txtCols").send_keys(input_headers)
    with bar.pause():
        _ = input("Do you want to show serial numbers? (y/n)")
    if _ == 'y':
        # Click an input with id 'chkLineNumbers'
        while True:
            try:
                browser.find_element(By.ID, "chkLineNumbers").click()
            except ElementClickInterceptedException:
                time.sleep(1)
            else:
                break

    # click on an input with title 'Convert CSV To Markdown Table'
    browser.find_element(By.XPATH, "//input[@title='Convert CSV To Markdown Table']").click()
    bar()
    bar.text("Saving Markdown")

    time.sleep(1)
    # Click on input with value 'Download Result'
    browser.find_element(By.XPATH, "//input[@value='Download Result']").click()

    # Get the last downloaded file in the downloads folder
    time.sleep(0.5)
    list_of_files = glob.glob(f"C:/Users/{os.environ['USERNAME']}/Downloads/*") # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)

    # Move the latest file to current directory as table.csv
    os.system(f"move {latest_file} table.md")

    # Read table.csv file
    with open('table.md', 'r') as file:
        md_table = file.read()

    bar()
    bar.text("Loading Markdown Formatter")
    browser.get("http://markdowntable.com/")

    # Wait until textarea with id as "md_table_holder" is loaded then enter md_table into it
    while True:
        try:
            textarea = browser.find_element(By.ID, "md_table_holder")
            textarea.send_keys(md_table)
        except NoSuchElementException:
            time.sleep(1)
        else:
            break
    bar()
    bar.text("Formatting Markdown")
    # Click on input with id as "format_button"
    browser.find_element(By.ID, "format_button").click()

    # Copy text from textarea with id as "md_table_holder"
    text = browser.find_element(By.ID, "md_table_holder").get_attribute('value')
    bar()

    bar.text("Saving Markdown")
    # Write text to file
    try:
        with open('tools/target.md', 'w') as file:
            file.write(text)
    except:
        with open('target.md', 'w') as file:
            file.write(text)

    
    bar()

    bar.text("Regnerating table")

import time
import selenium.webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import loguru
from alive_progress import alive_bar

s = Service('chromedriver.exe')
options = Options()
options.add_argument(
    "user-data-dir=C:/Users/Administrator/AppData/Local/Google/Chrome/User Data/Default")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
# make chrome headless
options.add_argument('headless')
browser = selenium.webdriver.Chrome(service=s, options=options)
options = ChromeOptions()

file_name = 'target.md'

try:
    with open(file_name, 'r') as file:
        text = file.read()
except:
    file_name = 'tools/target.md'

lines = []


with open(file_name, 'r') as f:
    # add 1 to counter everytime 'https://drive.google.com' is found in the file
    counter = 0
    a = f.readlines()
    for line in a:
        if 'https://drive.google.com' in line:
            counter += 1

    print("Found {} links in {}".format(counter, file_name))

    # if counter is less than 1 then quit
    if counter < 1:
        print("No links found in {}".format(file_name))
        quit()

    i = 1
    with alive_bar(counter) as bar:
        for line in a:
            new_line = line.replace('.pdf', '').replace(
                ' - ', ' | ').replace('<', '[Download Link](').replace('>', ')')
            new_line = new_line.replace(
                '| https://', '| [Download Link](https://').replace('export=download |', 'export=download) |').replace(' # ', ' S.No. ')
            line = new_line


            if 'https://drive.google.com' in line:
                i += 1
                bar.text = "Extracted Link"
                old_link = line.split('(')[-1].split(')')[0]

                bar.text = "Opening url shortner"
                browser.get("https://www.shorturl.at/")

                while True:
                    try:
                        s = browser.find_element(By.NAME, 'u')
                    except NoSuchElementException:
                        time.sleep(1)
                    else:
                        break

                s.send_keys(old_link)
                bar.text = "Submit old link to server"
                # click the button with value 'Shorten URL'
                try:
                    browser.find_element(
                        By.XPATH, "//input[@value='Shorten URL']").click()
                except NoSuchElementException:
                    while True:
                        pass
                else:
                    bar.text = "Request sent for short link"

                # find the input with id shortenurl and get the value
                new_link = (browser.find_element(
                    By.ID, 'shortenurl').get_attribute('value'))
                bar.text = "Shortened link found"
                new_line = new_line.replace(old_link, "https://"+new_link)
                bar.text = "Replacing old link with new link"
                bar()

            lines.append(new_line)
browser.quit()

with open(file_name, 'w') as f:
    for line in lines:
        f.write(line)

