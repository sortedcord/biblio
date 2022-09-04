import datetime
import loguru
import rich
from cursesmenu import CursesMenu
from cursesmenu.items import FunctionItem
import random
logger = loguru.logger

def dinput(message, default):
    if default is not None and message == "":
        return default
    else: 
        return message


def standalone():
    pass

def chapterwise():
    folder_id = dinput("Enter folder ID: ", "")
    post_id = random.randint(1000,9999)

    folder_path = dinput("Enter folder path: ", "")
    total_pages = int(dinput("Enter total pages", 1000))

    title = ""
    while title=="":
        title= dinput("Enter title of book")

    # generate date in the format as "2022-08-25 16:48:23 +0530"
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")

    author = dinput("Enter author name: ", "Anonymous")
    layout = "post"
    # set permalink as /2022/8/25/title/
    permalink = f"/{current_time[:4]}/{current_time[5:7]}/{current_time[8:10]}/{title}/"

    image = dinput("Enter image URL: ", "https://i.imgur.com/0Z0Z0Z0.png") 

    # generate tags
    while True:
        out = CursesMenu.get_selection()





def genfile():
    # Show menu
    logger.debug("Loading File Generation Menu")
    menu = CursesMenu(f"Biblio Post Generator", "Menu")

    standalone_item = FunctionItem("Generate for Standalone Item", standalone)
    menu.items.append(standalone_item)

    chapterwise_item = FunctionItem("Generate for Chapterwise items", chapterwise)
    menu.items.append(chapterwise_item)


    menu.show()