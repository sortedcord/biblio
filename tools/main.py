from tabulate import tabulate
import pickle as pk
from rich.progress import track
from utils import createBrowser, shortenlink, get_gdrive_service, menugen
from utils import clearconsole as clr
from utils import convert_bytes, convert_date
from loguru import logger
from rich.progress import Progress


logger.debug("Loading Imports")
logger.debug("All Imports Loaded")

VERSION = '0.0.1'


def fetch_items(folder_id):
    logger.debug("Createing GDrive API Service Object")
    try:
        service = get_gdrive_service()
    except:
        logger.error("Failed to create GDrive API Service Object")
        quit()
    else:
        logger.success("GDrive API Service Object Created")

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

    # Create browser object
    logger.debug("Creating Browser Object")
    try:
        browser = createBrowser(True)
    except:
        logger.error("Failed to create Browser Object")
        quit()
    else:
        logger.success("Browser Object Created")

    with Progress() as progress:
        task1 = progress.add_task("[blue]Downloading...", total=len(items))
        for item in items:

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
                    item['serial'] = serial.strip()
                    logger.info(f"File serial set as {serial}")
                file_name = file_name.replace(".pdf", "")
                item['name'] = file_name

                new_items.append(item)
            else:
                continue

            if check_id(item['id']):
                item['link'] = check_id(item['id'])
            else:
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


    browser.quit()
    logger.debug("Browser Object Closed")
    return new_items


def itemtotable(items):
    logger.debug("Generating Table")

    headers = ["S.No.", "File Name",
               "Download Link", "File Size", "Created At"]
    logger.info("Table Headers set as {}".format(headers))

    table = []

    for item in items:
        table.append([item['serial'], item['name'], "[Download Link](" +
                     item['link']+")", item['size'], item['date']])

    logger.debug("Tabulating Table")
    try:
        table = tabulate(table, headers, tablefmt='github')
    except:
        logger.error("Failed to Tabulate Table")
        quit()
    else:
        logger.success("Table Tabulated")

    return table


def generate_table(folder_id, out=None):

    raw_items = fetch_items(folder_id)
    items = process_items(raw_items)
    table = itemtotable(items)

    if out is None:
        choice = input("Do you want to save the table to a file? (y/n): ")
        if choice == 'y':
            with open('table.md', 'w') as file:
                file.write(table)
                print("Table saved to table.md")

    if out == "return":
        return table


def updateFile(out):
    logger.debug("Reading File {}".format(out))

    try:
        with open(out, 'r') as mdfile:
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
    with open(out, 'r') as file:
        content = file.read()
        try:
            content = content.split("<!-- TABLE START -->")[0] + "<!-- TABLE START -->\n" + \
                table + "\n<!-- TABLE END -->" + \
                content.split("<!-- TABLE END -->")[1]
        except:
            logger.error("Could not find table start and end markers")
            quit()
        else:
            logger.success("Table Inserted")

    with open(out, 'w') as file:
        file.write(content)
        logger.success("File {} updated".format(out))


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
    
    options = ["Generate Table", "Update File", "Quit"]
    choice = menugen(options)

    if choice == 1:
        # Some code
        f_id = input("Enter folder id: ")
        generate_table(f_id)
    elif choice == 2:
        updateFile(input("Enter file path along with name: "))
    elif choice == 3:
        quit()


def show_ids():
    with open("ids.dat", 'rb') as file:
        ids = pk.load(file)
    
    for key, value in ids.items():
        print(f"{key} : {value}")

if __name__ == "__main__":
    main()
    # show_ids()

