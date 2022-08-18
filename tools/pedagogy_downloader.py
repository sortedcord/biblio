import base64
import os
import shutil
import time
import selenium.webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# create a function that opens up a browser and goes to a website using chrome
def open_browser():
    website_path = r"https://www.pedagogy.study/"
    s = Service('chromedriver.exe')
    options = Options()
    # options.headless = True
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = selenium.webdriver.Chrome(service=s, options=options)
    options = ChromeOptions()
    # return the browser
    browser.get(website_path)

    return browser

browser = open_browser()
# Find the element with class 'btn btn-outline' and click it
while True:
    try:
        browser.find_element(By.CLASS_NAME,'btn-outline').click()
    except:
        time.sleep(1)
    else:
        break

# Find a checkbox with the name 'term' and check it
actions = ActionChains(browser)

while True:
    try:
        browser.find_element(By.XPATH,"//div[@class='custom-control custom-checkbox']")
    except NoSuchElementException:
        time.sleep(1)
    else:
        break

actions.move_by_offset(425, 588).click().perform()

# Find textbox with the name 'email' and enter your email
browser.find_element(By.NAME,'email').send_keys('email')
# Find textbox with the name 'password' and enter your password
browser.find_element(By.NAME,'pwd').send_keys('pass')

# Submit the form
actions.move_by_offset(0,-42).click().perform()

time.sleep(4)
browser.get('https://www.pedagogy.study/student/course/6278b3228123c50949d81641')

# chapter_name = input("Enter the chapter name: ")
# chapter_name = 'SEQUENCES AND SERIES II'

while True:
    try:
        # click a list item with class name "doc view" and name as chapter_name
        s = browser.find_element(By.XPATH,"//li[contains(@class,'doc')]")
    except:
        time.sleep(1)
    else: break

docs = browser.find_elements(By.XPATH,"//li[@class='doc view' or @class='doc not-view']")

chapter_number = 0
for doc in docs:
    doc_title = doc.text.replace(' ','_')

    doc.click()

    while True:
        try:
            # get the text in a div with class name 'form-group page-no mb-0 form-inline'
            total_pages = browser.find_element(By.XPATH,"//div[@class='form-group page-no mb-0 form-inline']").text
        except:
            time.sleep(1)
        else:
            total_pages = int(total_pages.split('of ')[-1])
            break
    
    chapter_number += 1
    browser.find_element(By.ID,'dropdownManual').click()

    # click button with text '200%'
    browser.find_element(By.XPATH,"//button[contains(text(),'200%')]").click()

    i = 1
    while i < total_pages+1: 

        time.sleep(3)
        # find the element with the 'CANVAS' tag name
        while True:
            try:
                canvas = browser.find_element(By.TAG_NAME,'canvas')
            except NoSuchElementException:
                time.sleep(1)
            else:
                break
        hits = 0
        while True:
            if hits > 8:
                break
            # get the canvas as a PNG base64 string
            canvas_base64 = browser.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)

            # decode
            canvas_png = base64.b64decode(canvas_base64)

            # create a folder with the name of the chapter if it does not exist already
            if not os.path.exists(f'{chapter_number} - {doc_title}'):
                os.makedirs(f"{chapter_number} - {doc_title}")

            # save to a file
            if i < 10:
                file_name = f'0{i}_page.png'
                with open(f"{chapter_number} - {doc_title}/{file_name}", 'wb') as f:
                    f.write(canvas_png)
            else:
                file_name = f'{i}_page.png'
                with open(f"{chapter_number} - {doc_title}/{file_name}", 'wb') as f:
                    f.write(canvas_png)
            
            # get the file size of the image saved
            file_size = os.stat(f"{chapter_number} - {doc_title}/{file_name}").st_size

            # if file size is less than 500 kilobytes, then start over else break
            if file_size < 500000:
                hits += 1
                continue
            else:
                break

        # click a span with class 'fa fa-arrow-down'
        time.sleep(1)
        browser.find_element(By.XPATH,"//span[@class='fa fa-arrow-down']").click()
        i += 1
    
    if chapter_number < 10:
        chap_ = f"0{chapter_number}"
    else:
        chap_ = f"{chapter_number}"

    os.system(f'magick.exe convert "{chapter_number} - {doc_title}/*.png" "{chap_} - {doc_title}.pdf"')
    # shutil.rmtree(doc_title)

    # click a button that has class name as close ml-auto
    browser.find_element(By.XPATH,"//button[@class='close ml-auto']").click()

browser.quit()

# os.system('"C:\Program Files\ImageMagick-7.1.0-Q16\magick.exe" convert *.pdf final.pdf')
# Create an infinite loop preventing browser from closing


