import pickle as pk
import datetime
import time
from urllib.parse import non_hierarchical
import loguru
import rich
from cursesmenu import CursesMenu
from cursesmenu.items import FunctionItem
import random

from utils import shortenlink
logger = loguru.logger


def dinput(message, default):
    if default is not None and message == "":
        return default
    else:
        return input(message)


def generic_meta(progress=None):
    post_id = random.randint(1000, 9999)
    try:
        title = ""
        while title == "":
            title = dinput("Enter title of book", "BOOKTITLE")
    except Exception as E:
        print(E)

    # generate date in the format as "2022-08-25 16:48:23 +0530"
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")

    author = dinput("Enter author name: ", "Anonymous")
    layout = "post"
    # set permalink as /2022/8/25/title/
    try:
        permalink = f"/{current_time[:4]}/{current_time[5:7]}/{current_time[8:10]}/{title}/"
    except Exception as E:
        print(E)
        time.sleep(5)

    image = dinput("Enter image URL: ", "https://i.imgur.com/0Z0Z0Z0.png")

    #######
    # tags
    try:
        with open("tools.dat", "rb") as f:
            preferences = pk.load(f)
            stored_tags = preferences["tags"]
    except FileNotFoundError:
        with open("tools.dat", "wb") as f:
            preferences = {"recent_files": [],
                           "tags": [],
                           "categories": []}
            stored_tags = preferences["tags"]
            pk.dump(preferences, f)
    except KeyError:
        preferences["tags"] = []
        with open("tools.dat", "wb") as f:
            pk.dump(preferences, f)
        stored_tags = preferences["tags"]

    # generate tags
    logger.debug("Generating tags")
    logger.debug("Inserted new tag option")
    l = stored_tags
    l.insert(0, "Add a new tag")
    logger.debug("Inserting Quit Option")
    l.append("Done")
    logger.debug("Inserted meta options")
    post_tags = []
    while True:
        logger.debug("Showing tags menu")
        menu = CursesMenu.make_selection_menu(
            l, f"Currently applied tags: {post_tags}")
        menu.show()
        menu.join()
        out = menu.selected_option

        if out == 0:
            new_tag = input("Enter new tag: ")
            stored_tags.insert(1, new_tag)
        else:
            if out == len(stored_tags)-1:
                break
            if stored_tags[out] not in post_tags:
                post_tags.append(stored_tags[out])

    ############
    # Categories
    try:
        with open("tools.dat", "rb") as f:
            preferences = pk.load(f)
            stored_categories = preferences["categories"]
    except FileNotFoundError:
        with open("tools.dat", "wb") as f:
            preferences = {"recent_files": [],
                           "categories": [],
                           "categories": []}
            stored_categories = preferences["categories"]
            pk.dump(preferences, f)
    except KeyError:
        preferences["categories"] = []
        with open("tools.dat", "wb") as f:
            pk.dump(preferences, f)
        stored_categories = preferences["categories"]

    # generate categories
    logger.debug("Generating categories")
    logger.debug("Inserted new tag option")
    l = stored_categories
    l.insert(0, "Add a new tag")
    logger.debug("Inserting Quit Option")
    l.append("Done")
    logger.debug("Inserted meta options")
    post_categories = []
    while True:
        logger.debug("Showing categories menu")
        menu = CursesMenu.make_selection_menu(
            l, f"Currently applied categories: {post_categories}")
        menu.show()
        menu.join()
        out = menu.selected_option

        if out == 0:
            new_tag = input("Enter new tag: ")
            stored_categories.insert(1, new_tag)
        else:
            if out == len(stored_categories)-1:
                break
            if stored_categories[out] not in post_categories:
                post_categories.append(stored_categories[out])

    str_tags = ""
    for tag in post_tags:
        str_tags += f"    - {tag}\n"

    str_categories = ""
    for category in post_categories:
        str_categories += f"    - {category}\n"

    if progress is not None:
        str_tags += f"    - {progress}\n"

    file_str = f"""id: {post_id}
title: '{title}'
date: '{current_time}'
author: {author}
layout: {layout}
permalink: {permalink}
image: '{image}'
categories:
{str_categories}

tags:
{str_tags}

---

    """

    # Update tags in tools.dat
    preferences["tags"] = post_tags
    preferences["categories"] = post_categories
    with open("tools.dat", "wb") as f:
        pk.dump(preferences, f)

    return file_str, title, current_time


def save(title, current_time, file_str):
    print(file_str)
    # generate string in the format 2022-08-09-{title}.md
    _ = title.replace(" ", "-")
    file_name = f"{current_time[:10]}-{_}.md"
    folder_output = input("Enter folder to save file: ")

    with open(f"{folder_output}/{file_name}", "w") as f:
        f.write(file_str)
    logger.success(f"File saved successfully as {folder_output}/{file_name}")


def standalone():
    file_str, title, current_time = generic_meta()

    download_link = input("Enter download link: ")

    with open("ids.dat", "rb") as f:
        ids = pk.load(f)

    # Extract file ID from google drive link
    # https://drive.google.com/file/d/115lvsZL2c62rznNDoZiFrpufstA-9N-d/view?usp=sharing
    id = download_link.split("d/")[1].split("/")[0]

    # generate direct download link from sharing link
    direct_link = f"https://drive.google.com/uc?export=download&id={id}"

    if id in ids:
        print("File already shortened")
        shortened_link = ids[id]
    else:
        s = shortenlink(direct_link)

    file_str = "---\n" + file_str + f"[Download]({shortened_link})\n"
    save(title, current_time, file_str)


def chapterwise():
    folder_id = dinput("Enter folder ID: ", "")
    folder_path = dinput("Enter folder path: ", "")
    total_pages = dinput("Enter total pages", 1000)

    progress_list = ["done", "doing", "future", "missing"]
    progress = CursesMenu.get_selection(progress_list, "Select progress")

    file_str, title, current_time = generic_meta(progress_list[progress])
    file_str = "---\n" + f"folder: {folder_id}\n" + \
        f"pages: {total_pages}\n" + f"path: {folder_path}\n" + file_str

    if progress == "doing":
        file_str += """<!-- PROGRESS START -->

<!-- PROGRESS END -->

"""
    file_str += """<!-- TABLE START -->

<!-- TABLE END -->

"""
    save(title, current_time, file_str)


def genfile():
    # Show menu
    logger.debug("Loading File Generation Menu")
    menu = CursesMenu(f"Biblio Post Generator", "Menu")

    standalone_item = FunctionItem("Generate for Standalone Item", standalone)
    menu.items.append(standalone_item)

    chapterwise_item = FunctionItem(
        "Generate for Chapterwise items", chapterwise)
    menu.items.append(chapterwise_item)

    menu.show()


if __name__ == "__main__":
    genfile()
