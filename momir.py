import json
import random
import requests
from PIL import Image
from io import BytesIO
import os
import time

def update(timediff=1, forceupdate=False):
    """
    Updates the cmcs folder if the difference in time between the current time and the time stored in lastupdate.txt is greater than timediff months.
    
    If forceupdate is True, always updates.
    Creates cmcs folder containing json data if it does not exist otherwise.
    """
    cur_time = time.time()
    try:
        with open("lastupdate.txt", "r") as read_file:
            if (cur_time - int(read_file.read())) >= timediff*2592000:
                forceupdate = True
    except:
        forceupdate = True

    if forceupdate:
        print("Updating...")
        print("Retrieving JSON data...")
        page = requests.get("https://mtgjson.com/json/AllCards.json")
        page_json = json.loads(page.content)

        print("Removing illegal cards and noncreatures...")
        bad_lst = []
        for entry in page_json:
            if not page_json[entry]["legalities"] or "Creature" not in page_json[entry]["types"] or "names" in page_json[entry]:
                bad_lst.append(entry)
        for badentry in bad_lst:
            page_json.pop(badentry)

        print("Creating cmcs folder...")
        try:
            os.mkdir("./cmcs/")
        except:
            print("Directory Already Exists.")
        else:
            print("Success.")

        print("Populating cmcs folder...")
        cmcs_lst = {}
        for item in page_json:
            card_cmc = int(page_json[item]["convertedManaCost"])
            if card_cmc in cmcs_lst:
                cmcs_lst[card_cmc][item] = page_json[item]
            else:
                cmcs_lst[card_cmc] = {item : page_json[item]}
        for mana_cost in cmcs_lst:
            with open("./cmcs/"+str(mana_cost)+".json", "w") as write_file:
                json.dump(cmcs_lst[mana_cost], write_file, indent=4)

        print("Done.")
        with open("lastupdate.txt", "w") as write_file:
            write_file.write(str(int(time.time())))
    else:
        print("No update needed.")

def getCost():
    """
    Retrieves a number from the user.

    Returns whatever value the user inputs (even if it isn't a number).
    """
    # TODO : update this function to use getch
    num = int(input("Enter a converted mana cost: "))
    return num

def getRandomCard(cost):
    """
    Uses the data in the cmcs folder to retrieve a random card of a certain converted mana cost.
    """
    with open("./cmcs/"+str(cost)+".json", "r", encoding="utf-8") as read_file:
            data = json.load(read_file)
    return random.choice(list(data))

def getImage(cardTitle, size="normal"):
    """
    Gets a card image from the scryfall api and returns an image object that is dithered and resized to a receipt printer size.

    Size can be set to either "small", "normal", or "large".
    """
    page = requests.get("https://api.scryfall.com/cards/named?exact="+name)
    page_json = json.loads(page.content)
    image_link = page_json["image_uris"][size]
    image_response = requests.get(image_link)
    img = Image.open(BytesIO(image_response.content))
    return img.resize((384, 535)).convert("1")

def printImage(imageObject):
    """
    Prints the image stored in imageObject using an attached USB receipt printer.

    TODO
    """
    # TODO
    pass

if __name__ == "__main__":
    update()

    while True:
        try:
            cmc = getCost()
            name = getRandomCard(cmc)
            # print(name) would not necessarily be present in the final product.
            print(name)
            img = getImage(name)
            # Use of the receipt printer would replace im.show()
            img.show()
        except KeyboardInterrupt:
            break
        except:
            print("Invalid Converted Mana Cost.")