import time
import selenium.webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from alive_progress import alive_bar
import os
import glob
import pickle as pk
import random

from utils import waitforpage, createBrowser, shortenlink, clearconsole


def remove_serial(line, fl):
    _ = 0
    if fl:
        _ += 1
    rest_line = ""
    for i in line.split("|")[3+_:]:
        rest_line += i + "|"
    return line.split("|")[0+_] + "|" + line.split("|")[1+_] + "|" + line.split("|")[2+_].split(" -")[-1] + "|" + rest_line


def fetch_table():
    clearconsole()

    with alive_bar(dual_line=False) as bar:

        bar.text("Starting Chrome")
        browser = createBrowser(False)
        bar()

        with bar.pause():
            folder_id = input("Enter folder id: ")
        clearconsole()

        bar.text("Loading Drive Explorer")
        browser.get(
            f'https://syncwithtech.com/drive?state=%7B"ids":%5B"{folder_id}"%5D,"action":"open","userId":"100758669744711932203","resourceKeys":%7B%7D%7D')

        # Wait until a span saying "FILE NAME" is found and then click it
        waitforpage(browser, By.XPATH,
                    '//span[contains(text(), "File name")]', True)
        bar()

        bar.text("Fetching CSV")
        # Click a span containing text "Export CSV"
        browser.find_element(
            By.XPATH, "//span[contains(text(), 'Export CSV')]").click()

        # Get the downloads folder
        downloads_folder = os.path.join(os.environ['USERPROFILE'], 'Downloads')

        # Get the last downloaded file in the downloads folder
        time.sleep(1)
        # * means all if need specific format then *.csv
        list_of_files = glob.glob(
            f"C:/Users/{os.environ['USERNAME']}/Downloads/*")
        latest_file = max(list_of_files, key=os.path.getctime)

        # Move the latest file to current directory as table.csv
        os.system(f"move {latest_file} table.csv")
        clearconsole()

        # Read table.csv file
        with open('table.csv', 'r') as file:
            csv_data = file.read().replace("ï»¿", "")

        # Delete table.csv
        try:
            os.system('del table.csv')
        except:
            pass
        clearconsole()
        bar()

        bar.text("Loading CSV Convertor")
        browser.get("https://www.convertcsv.com/csv-to-markdown.htm")

        # Wait until textarea is loaded and then enter csv_data into it
        text_area = waitforpage(browser, By.XPATH, '//textarea')
        text_area.send_keys(csv_data)
        bar()

        bar.text("Converting CSV to Markdown")
        # Find all spans with class name 'glyphicon glyphicon-chevron-down'
        spans = browser.find_elements(
            By.XPATH, "//span[@class='glyphicon glyphicon-chevron-down']")

        for span in spans:
            time.sleep(0.5)
            while True:
                try:
                    span.click()
                except ElementClickInterceptedException:
                    time.sleep(1)
                else:
                    break

        with bar.pause():
            _ = input("Do you want to show folder name in table? (y/n)")
            clearconsole()
        if _ == 'y':
            input_headers = "1,3,4,5,6"
            fl = True
        else:
            input_headers = "3,4,5,6"
            fl = False

        # click on an input with id as  "txtCols"
        browser.find_element(By.ID, "txtCols").click()

        # Clear the text in the input with id as "txtCols"
        browser.find_element(By.ID, "txtCols").clear()

        # Enter the headers in the input with id as "txtCols"
        browser.find_element(By.ID, "txtCols").send_keys(input_headers)
        with bar.pause():
            _ = input("Do you want to show serial numbers? (y/n)")
            clearconsole()
        if _ == 'y':
            # Click an input with id 'chkLineNumbers'
            while True:
                try:
                    browser.find_element(By.ID, "chkLineNumbers").click()
                except ElementClickInterceptedException:
                    time.sleep(1)
                else:
                    break

        uname = f"{random.randint(1000,9999)}bibtable"

        browser.find_element(
            By.XPATH, "//input[@title='Enter filename without extension']").clear()
        browser.find_element(
            By.XPATH, "//input[@title='Enter filename without extension']").send_keys(uname)

        # click on an input with title 'Convert CSV To Markdown Table'
        browser.find_element(
            By.XPATH, "//input[@title='Convert CSV To Markdown Table']").click()
        bar()
        bar.text("Saving Markdown")
        time.sleep(2)

        # Click on input with value 'Download Result' and type="button"
        while True:
            browser.find_element(
                By.XPATH, "//input[@value='Download Result' and @type='button']").click()

            time.sleep(1)
            list_of_files = glob.glob(
                f"C:/Users/{os.environ['USERNAME']}/Downloads/*")
            latest_file = max(list_of_files, key=os.path.getctime)

            if f"{uname}.md" in latest_file:
                break

        # Read table.csv file
        with open(latest_file, 'r') as file:
            md_table = file.read()
        os.system(f"del {latest_file}")

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
        text = browser.find_element(
            By.ID, "md_table_holder").get_attribute('value')
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

    bib_format(browser, fl)


def bib_format(browser, fl):
    clearconsole()

    # If 'tools/ids.dat' file exists then pickle load it
    if os.path.exists('tools/ids.dat'):
        with open('tools/ids.dat', 'rb') as file:
            ids = pk.load(file)
    else:
        ids = {}

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
        with alive_bar(counter, title="Shortening Links") as bar:
            for line in a:
                new_line = line.replace('.pdf', '').replace(
                    '<', '[Download Link](').replace('>', ')')
                new_line = new_line.replace(
                    '| https://', '| [Download Link](https://').replace('export=download |', 'export=download) |').replace(' # ', ' S.No. ')

                new_line = remove_serial(new_line, fl)

                if 'https://drive.google.com' in new_line:
                    i += 1
                    bar.text = "Extracted Link"
                    old_link = new_line.split('(')[-1].split(')')[0]

                    # Get the google drive file id from link
                    file_id = old_link.split('id=')[-1].split("&export=")[0]

                    # check if file_id is in ids
                    if file_id in ids.keys():
                        new_link = 'https://' + ids[file_id]
                    else:
                        new_link = shortenlink(old_link, browser, bar)
                        bar.text = "Shortened link found"

                    new_line = new_line.replace(old_link, new_link)
                    bar.text = "Replacing old link with new link"
                    bar()

                    ids[file_id] = new_link

                lines.append(new_line)

    browser.quit()

    with open('tools/ids.dat', 'wb') as file:
        pk.dump(ids, file)

    with open(file_name, 'w') as f:
        for line in lines:
            f.write(line)


fetch_table()
