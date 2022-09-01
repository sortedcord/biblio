import os
import time
from tabulate import tabulate
import pickle as pk
from rich.progress import track
from utils import createBrowser, shortenlink, get_gdrive_service
from utils import convert_bytes, convert_date
# from utils import clearconsole as clr
from loguru import logger
from rich.progress import Progress
import codecs

from cursesmenu import CursesMenu
from cursesmenu.items import FunctionItem

import PyPDF2


logger.debug("Loading Imports")
logger.debug("All Imports Loaded")

VERSION = '0.0.1'
logger.debug("Createing GDrive API Service Object")
try:
    service = get_gdrive_service()
except:
    logger.error("Failed to create GDrive API Service Object")
    quit()
else:
    logger.success("GDrive API Service Object Created")
browser = False

def clr():
    pass

def fetch_items(folder_id):

    q = f"parents = '{folder_id}'"

    logger.debug("Fetching Items")
    results = service.files().list(
        q=q, orderBy="name", fields="nextPageToken, files(name, id, size, createdTime)").execute()

    items = results.get('files', [])
    logger.success("Items Fetched")
    return items


def check_id(id):
    # Check if ids.dat is present in the current working directory
    logger.debug("Checking if ids.dat is present")
    try:
        with open('ids.dat', 'rb') as file:
            ids = pk.load(file)
    except FileNotFoundError:
        logger.warning("ids.dat file not found")
        return False
    else:
        logger.success("ids.dat file found")

    if id in ids:
        logger.debug(f"id {id} found in ids.dat file")
        return ids[id]
    else:
        logger.debug(f"id {id} not found in ids.dat file")
        return False


def process_items(items):
    new_items = []

    

    with Progress() as progress:
        task1 = progress.add_task("[blue]Fetching...", total=len(items))
        for item in items:
            clr()
            logger.debug(f"Processing item: {item['name']}")

            # Format information
            file_name = item['name']
            item['size'], item['raw_size'] = convert_bytes(
                int(item['size'])), int(item['size'])
            item['date'] = convert_date(item['createdTime'])

            # Format name
            if ".pdf" in file_name:
                logger.debug("File is a PDF")
                if " - " in file_name:
                    file_name, serial = file_name.split(
                        " - ")[-1], file_name.split(" ")[0]
                    item['serial'] = str(serial).strip()
                    logger.info(f"File serial set as {serial}")
                file_name = file_name.replace(".pdf", "")
                item['name'] = file_name

                new_items.append(item)
            else:
                continue

            if check_id(item['id']):
                item['link'] = check_id(item['id'])
            else:
                global browser
                if not browser:
                    # Create browser object
                    logger.debug("Creating Browser Object")
                    try:
                        browser = createBrowser(False)
                    except:
                        logger.error("Failed to create Browser Object")
                        quit()
                    else:
                        logger.success("Browser Object Created")
                # Shorten Link
                logger.debug(f"Shortening Link for {item['name']}")
                try:
                    item['link'] = shortenlink(
                        "https://drive.google.com/uc?export=download&id="+item['id'], browser)
                except:
                    logger.error(f"Failed to shorten link for {item['name']}")
                    item['link'] = "https://drive.google.com/uc?export=download&id="+item['id']
                else:
                    logger.success(f"Link shortened for {item['name']}")

                # Save Shortened Link key

                # Check if ids.dat is present in the current working directory if not then create it
                with open('ids.dat', 'rb') as file:
                    ids = pk.load(file)

                with open('ids.dat', 'wb') as file:
                    ids[item['id']] = item['link']
                    pk.dump(ids, file)
                    logger.success("ids.dat file created and updated")
                progress.update(task1, advance=1)

    if browser:
        browser.quit()
    logger.debug("Browser Object Closed")
    return new_items


def itemtotable(items):
    logger.debug("Generating Table")

    headers = ["S.No.", "File Name",
               "Download Link", "File Size", "Created At"]
    logger.info("Table Headers set as {}".format(headers))

    table = []
    try:
        for item in items:
            table.append([item['serial'].strip(), item['name'], "[Download Link](" +
                        item['link']+")", item['size'].strip(), item['date']])
    except Exception as E:
        if 'serial' in E:
            logger.error("Serial Number not found")
        time.sleep(5)

    logger.debug("Tabulating Table")
    try:
        table = tabulate(table, headers, tablefmt='github', colalign=("left",))
    except:
        logger.error("Failed to Tabulate Table")
        quit()
    else:
        logger.success("Table Tabulated")

    return table

def count_pages(item):
    pages = 0
    if os.path.exists(item):
        if os.path.isdir(item):
            for item_ in os.listdir(item):
                pages += count_pages(f"{item}/{item_}")
        else:
            if ".pdf" in item:
                with open(item, 'rb') as file:
                    pdf = PyPDF2.PdfFileReader(file, strict=False)
                    pages = pdf.numPages
    return pages

def get_upload_progress(folder_path, pages):

    uploaded = count_pages(folder_path)
    
    progress = int((uploaded/pages)*100)
    progress_str = "Current Progress: [ "
    for i in range(0, 40):
        if progress//2.5 > i:
            progress_str += "█"
        else:
            progress_str += "·"

    progress_str += f" ] {progress}%:Completed Uploading {uploaded}/{pages} pages"

    return (progress_str, uploaded, progress)


def generate_table(folder_id=None, out=None, subdirs=None):

    if folder_id is None:
        folder_id = input("Enter Folder ID: ")

    raw_items = fetch_items(folder_id)
    if subdirs is None:
        _ = input(
            "Is this full of sub directories which contain files to be downloaded? (y/n)")
        if _ == "y":
            tables = ""
            for item in raw_items:
                raw_items = fetch_items(item['id'])
                if len(raw_items) < 1:
                    continue
                items = process_items(raw_items)
                table = itemtotable(items)
                tables += f"## {item['name']} \n\n" + table + "\n\n"

            if out is None:
                choice = input(
                    "Do you want to save the table to a file? (y/n)")
                if choice == "y":
                    out = input("Enter the name of the file: ")
                    with codecs.open(out, 'w', "utf-8") as file:
                        file.write(tables)
                        logger.success(f"Table saved to {out}")
            if out == "return":
                return tables

            return None

    items = process_items(raw_items)
    table = itemtotable(items)

    if out is None:
        choice = input("Do you want to save the table to a file? (y/n): ")
        if choice == 'y':
            with codecs.open('table.md', 'w', 'utf-8') as file:
                file.write(table)
                print("Table saved to table.md")

    if out == "return":
        return table


def updateFile(out=None):

    # check if tools.dat exists
    if os.path.exists('tools.dat'):
        with open('tools.dat', 'rb') as file:
            recent_files = pk.load(file)
            recent_files.insert(0, "Update new file")

    out = CursesMenu.get_selection(recent_files)
    if out != 0:
        out = recent_files[out]

    if out is None or out == 0:
        out = input("Enter the name of the file: ")

    logger.debug("Reading File {}".format(out))

    try:
        with codecs.open(out, 'r', "utf-8") as mdfile:
            content = mdfile.readlines()
    except:
        logger.error("Failed to read file {}".format(out))
        quit()
    else:
        logger.success("File {} read".format(out))

    logger.debug("Searching for folder id in file")
    _ = False
    for line in content:
        if "folder: " in line:
            folder_id = line.split("folder: ")[1].strip()
            _ = True
            break
    if _:
        logger.success("Folder id found")
    else:
        logger.warning("Folder id not found in file. enter it manually")
        folder_id = input("Enter folder id: ")

    table = generate_table(folder_id, out="return")

    logger.debug("Updating File {}".format(out))
    with codecs.open(out, 'r', "utf-8") as file:
        content = file.read()
        try:
            print(content.split("<!-- TABLE START -->")[0],  content.split("<!-- TABLE END -->")[1])
            content = content.split("<!-- TABLE START -->")[0] + "<!-- TABLE START -->\n\n" \
                + table + "\n\n<!-- TABLE END -->" + \
                content.split("<!-- TABLE END -->")[1]
        except Exception as e:
            logger.error("Could not find table start and end markers")
            print(e)
            time.sleep(5)
            quit()
        else:
            logger.success("Table Inserted")

    # Update progress

    clr()
    _ = input("Do you want to update progress (y/n)")

    if _ == "y":
        logger.debug(
            "Searching for folder path and total number of pages in file")

        path_prop, page_prop = False, False

        for line in content.split("\n"):
            clr()
            logger.debug(f"Searching for folder path in {line}")
            if "path: " in line:
                logger.debug(f"Found folder path in {line}")
                folder_path = line.split("path: ")[1]
                path_prop = True
            if "pages: " in line:
                logger.debug(f"Found total number of pages in {line}")
                pages = line.split("pages: ")[1]
                page_prop = True
            if path_prop and page_prop:
                logger.success("Found folder path and total number of pages")
                break

        logger.debug("Checking a few conditions")
        if not path_prop:
            clr()
            logger.warning("Folder path not found in file. enter it manually")
            folder_path = input("Enter folder path: ")
        if not page_prop:
            clr()
            logger.warning(
                "Total number of pages not found in file. enter it manually")
            pages = input("Enter total number of pages: ")

        logger.debug("Checking for file availability")
        logger.info(f"File set as {folder_path}")

        if os.path.exists(str(folder_path).strip()):
            logger.debug("Folder path found on device")

            try:
                logger.info(folder_path[:-1])
                cont = get_upload_progress(str(folder_path).strip(), int(pages))
            except Exception as e:
                print(e)
                time.sleep(5)
            logger.success("Upload progress found")
            print(cont)
            content = content.split("<!-- PROGRESS START -->")[0] + "<!-- PROGRESS START -->\n" + cont[0] + "\n<!-- PROGRESS END -->" + content.split("<!-- PROGRESS END -->")[-1]
            logger.success("Splicing successful")
        else:
            logger.error("Invalid file path. Aborting")

    print(out)
    try:
        with codecs.open(out, 'w', "utf-8") as file:
            file.write(content)
            logger.success(f"File {out} updated")
    except Exception as e:
        print(e)
        time.sleep(10)


    try:
        with open("tools.dat", "rb") as f:
            recent_files = pk.load(f)
    except:
        recent_files = []
    if out not in recent_files:
        recent_files.append(out)
        with open("tools.dat", "wb") as f:
            pk.dump(recent_files, f)


def main():

    # if ids.dat is not in the current directory then create it
    logger.debug("Checking if ids.dat is present")
    try:
        with open('ids.dat', 'rb') as file:
            ids = pk.load(file)
    except FileNotFoundError:
        # Create ids.dat
        logger.warning("ids.dat file not found")
        logger.info("Creating ids.dat file")
        with open('ids.dat', 'wb') as file:
            ids = {}
            pk.dump(ids, file)
            logger.success("ids.dat file created")

    # Show menu
    logger.debug("Loading Menu")
    menu = CursesMenu(f"Biblio Tools {VERSION}", "Main Menu")

    gen_table_item = FunctionItem("Generate Table", generate_table)
    menu.items.append(gen_table_item)

    update_item = FunctionItem("Update File", updateFile)
    menu.items.append(update_item)

    test_page = FunctionItem("Check Page Progress Function", get_upload_progress, [
                             "G:/My Drive/Material/Books/MTG Foundation Class 6th Science", 886])
    menu.items.append(test_page)

    menu.show()

    clr()


def show_ids():
    with open("ids.dat", 'rb') as file:
        ids = pk.load(file)

    for key, value in ids.items():
        print(f"{key} : {value}")


if __name__ == "__main__":
    main()
    # show_ids()
