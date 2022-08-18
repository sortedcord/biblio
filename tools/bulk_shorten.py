import time
import selenium.webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

s = Service('chromedriver.exe')
options = Options()
options.add_argument( "user-data-dir=C:/Users/Administrator/AppData/Local/Google/Chrome/User Data/Default" )
options.add_experimental_option('excludeSwitches', ['enable-logging'])
# make chrome headless
options.add_argument('headless')
browser = selenium.webdriver.Chrome(service=s, options=options)
options = ChromeOptions()

file_name = 'target.md'
lines = []


with open(file_name, 'r') as f:
    # add 1 to counter everytime 'https://drive.google.com' is found in the file
    counter = 0
    a = f.readlines()
    for line in a:
        if 'https://drive.google.com' in line:
            counter += 1

    print("Found {} links in {}".format(counter, file_name))


    i = 1
    for line in a:
        new_line = line.replace('.pdf', '').replace(' - ', ' | ').replace('<', '[Download Link](').replace('>', ')')
        new_line = new_line.replace('| https://','| [Download Link](https://').replace('export=download |', 'export=download) |')
        line = new_line

        
        if 'https://drive.google.com' in line:
            print(f"Processing link {i} of {counter}")
            i += 1
            old_link = line.split('(')[-1].split(')')[0]

            browser.get("https://www.shorturl.at/")

            while True:
                try:
                    s = browser.find_element(By.NAME,'u')
                except NoSuchElementException:
                    time.sleep(1)
                else: break
        
            s.send_keys(old_link)

            # click the button with value 'Shorten URL'
            try:
                browser.find_element(By.XPATH,"//input[@value='Shorten URL']").click()
            except NoSuchElementException:
                while True:
                    pass

            # find the input with id shortenurl and get the value
            new_link = (browser.find_element(By.ID,'shortenurl').get_attribute('value'))
            new_line = new_line.replace(old_link, "https://"+new_link)

        lines.append(new_line)
browser.quit()

with open(file_name, 'w') as f:
    for line in lines:
        f.write(line)

        


