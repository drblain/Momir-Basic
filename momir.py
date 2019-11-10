import json
import random
import requests
from PIL import Image
from io import BytesIO
import os
import time

def update(timediff=1, forceupdate=False):
    cur_time = time.time()
    try:
        with open("lastupdate.txt", "r") as read_file:
            if (cur_time - int(read_file.read())) >= timediff*2592000:
                forceupdate = True
    except:
        forceupdate = True

    if forceupdate:
        print('Updating...')
        print("Retrieving JSON data...")
        page = requests.get("https://mtgjson.com/json/AllCards.json")
        page_json = json.loads(page.content)

        print("Removing illegal cards and noncreatures...")
        bad_lst = []
        for entry in page_json:
            # last condition changed from page_json[entry]['names'][0] != entry to "names" in page_json[entry]
            # removed try: except: pass from around the if statement
            if not page_json[entry]["legalities"] or "Creature" not in page_json[entry]["types"] or "names" in page_json[entry]:
                bad_lst.append(entry)
        for badentry in bad_lst:
            page_json.pop(badentry)

        print("Creating cmcs folder...", end=" ")
        try:
            os.mkdir("./cmcs/")
        except:
            print("Directory Already Exists.")
        else:
            print("Success.")

        print("Populating cmcs folder...", end=" ")
        #This 'range(17)' has to be updated if any creature is released that costs more than 16
        # cmcs_lst changed to empty dictionary
        #cmcs_lst = [{} for i in range(17)]
        cmcs_lst = {}
        for item in page_json:
            card_cmc = int(page_json[item]["convertedManaCost"])
            if card_cmc in cmcs_lst:
                cmcs_lst[card_cmc][item] = page_json[item]
            else:
                cmcs_lst[card_cmc] = {item : page_json[item]}
            #cmcs_lst[card_cmc][item] = page_json[item]
        #for num in range(len(cmcs_lst)):
        for mana_cost in cmcs_lst:
            #with open("./cmcs/"+str(num)+".json", "w") as write_file:
            with open("./cmcs/"+str(mana_cost)+".json", "w") as write_file:
                json.dump(cmcs_lst[mana_cost], write_file, indent=4)
                #json.dump(cmcs_lst[num], write_file, indent=4)

        print("Done.")
        with open("lastupdate.txt", "w") as write_file:
            write_file.write(str(int(time.time())))
    else:
        print('No update needed.')

def getCost():
    num = int(input("Enter a converted mana cost: "))
    # print("\n"*100)
    return num

def getRandomCard(cost):
    with open("./cmcs/"+str(cost)+".json", "r", encoding="utf-8") as read_file:
            data = json.load(read_file)
    return random.choice(list(data))

def getImage(cardTitle, size='normal'):
    page = requests.get("https://api.scryfall.com/cards/named?exact="+name)
    page_json = json.loads(page.content)
    image_link = page_json['image_uris'][size]
    #can change size to small, normal, or large
    #GET IMAGE FROM IMAGE_LINK
    image_response = requests.get(image_link)
    img = Image.open(BytesIO(image_response.content))
    #resize to receipt width and convert to monochrome bitmap with dithering
    return img.resize((384, 535)).convert('1')

def printImage(imageObject):
    #Print the image stored in imageObject using an attached USB receipt printer
    pass

if __name__ == '__main__':
    update()

    while True:
        try:
            cmc = getCost()
            name = getRandomCard(cmc)
            print(name)
            img = getImage(name)
            #Shows the image (This is where the receipt printer code would go)
            #PRINT(img)
            img.show()
        except KeyboardInterrupt:
            break
        except:
            print('Invalid Converted Mana Cost.')