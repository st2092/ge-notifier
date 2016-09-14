import urllib2
import json
import pprint
import Tkinter
import datetime
import os
import platform
from subprocess import call, Popen
from Tkinter import *

RS_GE_API_URL = "http://services.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item="
LOG_FILE_DIR = sys.path[0] + "/price-logs/"
ITEMS_INFO = {}
ITEMS_FROM_USER = {}
ITEMS_TO_SELL = []
ITEMS_TO_BUY = []
TODAY = None
GUI_PROMPT = None


def isUnicode(query_string):
    """
    Checks if the query string is an unicode.

    Parameters:
    query_string -- the string to check if it is in Ascii or Unicode

    Returns -- true, if string is unicode; false, otherwise
    """
    return isinstance(query_string, unicode);

def convertStringFromAPIToInt(item_price_str):
    """
    Converts the response from RS API for the price of an item.

    Parameters:
    item_price_str -- the string form of an item's price

    Returns -- the integer form of the string price
    """
    item_price = -1
    #print "String value: " + item_price_str
    if '.' in item_price_str and 'k' in item_price_str:
        # e.g. "10.1k"
        item_price = int(item_price_str.replace('.','').replace(',','').replace('k',"00"))
    elif ',' in item_price_str:
        # e.g. "9,700"
        item_price = int(item_price_str.replace(",",""))

    return item_price

     
def extractItemCurrentPrice(item_dict):
    """
    Extracts the item's price from the response of the RS API.

    Parameters:
    item_dict -- json object from the RS API

    Returns -- the integer value price of the item
    """

    item_price_str = item_dict["item"]["current"]["price"]
    if isinstance(item_price_str, unicode):
        return convertStringFromAPIToInt(item_price_str.encode('ascii','replace'))
    else:
        return item_price_str

def extractItemId(item_dict):
    """
    Extracts the item's ID from the response of the RS API.

    Parameters:
    item_dict -- json object from the RS API

    Returns -- the id of the item
    """

    item_id = item_dict["item"]["id"]
    return item_id

def extractItemName(item_dict):
    """
    Extracts the item's name from the response of the RS API.

    Parameters:
    item_dict -- json object from the RS API

    Returns -- the name of the item
    """

    item_name = item_dict["item"]["name"]
    if isUnicode(item_name):
        item_name = item_name.encode('ascii','replace')

    return item_name

def obtainItemInformation(item_id, item_key_from_user):
    """
    Tries to obtain the information pertaining to the corresponding id from RS API.

    Parameters:
    item_id -- the id of the item to query the RS API
    item_key_from_user -- the key to associate with the item infromation retrieve from RS API

    """

    global item_number
    request_api_data = urllib2.Request(RS_GE_API_URL + str(item_id))
    response_text = urllib2.urlopen(request_api_data).read()
    item_info_dictionary = json.loads(response_text)
    
    item = {}
    item["name"] = extractItemName(item_info_dictionary)
    item["id"] = extractItemId(item_info_dictionary)
    item["currentPrice"] = extractItemCurrentPrice(item_info_dictionary)
    ITEMS_INFO[item_key_from_user] = item

def parseUserItemsJsonFile(path_to_user_item_list):
    """
    Parse the item file provided by the user. Convert it into a dictionary
    for use to query RS API.

    Parameters:
    path_to_user_item_list -- the full path to the json file containing all the items
                              and their associated buy/sell prices 
    """
    
    global ITEMS_FROM_USER
    user_items_json_file = open(path_to_user_item_list, 'r')
    user_items_list_json_text = user_items_json_file.read()
    user_items_dictionary = json.loads(user_items_list_json_text)

    ITEMS_FROM_USER = user_items_dictionary

def gatherAllItemsInformation(user_items_dictionary):
    """
    Tries to gather information about all the items the user would want a reminder for.

    Parameters:
    user_items_dictionary -- a dictionary representation of the item file provided by the user
    """

    for key, item_info in sorted(user_items_dictionary.iteritems()):
        obtainItemInformation(item_info["id"], key)

def priceWithinSellingMargin(current_price, item_sell_price, margin):
    """
    Determines whether an item's current price is within selling margin provided by the user.

    Parameters:
    current_price -- the current price of the item
    item_sell_price -- the highest price the user want to sell at
    margin -- how far away from the highest price the user is still willing to sell

    Returns -- true, if current price falls between the lowest and highest price point; false, otherwise
    """

    return current_price >= item_sell_price - margin

def determineItemsForSelling(items_current_prices, items_sell_prices):
    """
    Iterates through all the items and creates a list of the items that meets the selling margin
    provided by the user.
    
    Parameters:
    items_current_prices -- a list of the current prices of all the items the user wants to know about
    items_sell_prices -- a list of the highest prices the user wants to sell each item for
    """

    global ITEMS_TO_SELL
    for key, item in items_current_prices.iteritems():
        if priceWithinSellingMargin(item["currentPrice"], items_sell_prices[key]["sellPrice"], items_sell_prices[key]["sellMargin"]):
            ITEMS_TO_SELL.append({ "name": item["name"], "currentPrice": item["currentPrice"] })

def priceWithinBuyMargin(current_price, item_buy_price, margin):
    """
    Determines whether an item's current price is within buying margin provided by the user.

    Parameters:
    current_price -- the current price of the item
    item_buy_price -- the lowest price the user wants to buy at
    margin -- how much more the user is willing to spend
    """

    return current_price <= item_buy_price + margin

def determineItemsForBuying(items_current_prices, items_buy_prices):
    """
    Iterates through all the items and creates a list of the items that meets the buying margin
    provided by the user.

    Parameters:
    items_current_prices -- a list of the current prices of all the items the user wants to know about
    items_buy_prices -- a list of the lowest prices the user wants to buy each item for
    """

    global ITEMS_TO_BUY
    for key, item in items_current_prices.iteritems():
        if priceWithinBuyMargin(item["currentPrice"], items_buy_prices[key]["buyPrice"], items_buy_prices[key]["buyMargin"]):
            ITEMS_TO_BUY.append({ "name": item["name"], "currentPrice": item["currentPrice"] })

def niceFormatItemPrice(items_list):
    """
    Converts the list of items with their current prices into a nice format for logging.

    Parameters:
    items_list -- a list that holds item name and their current price

    Return -- nice formatted string of the item list
    """

    string_format = ""

    if len(items_list) <= 0:
        return "none"

    for item in items_list:
        string_format = string_format + item["name"] + ": " + str(item["currentPrice"]) + "\n"
    return string_format

def writePriceLogFile(items_to_buy, items_to_sell):
    """
    Writes a price log file of all the items to buy or sell.

    Parameters:
    items_to_buy -- a list of all the items that is within buying margin
    items_to_sell -- a list of all the items that is within selling margin
    """

    global TODAY
    today = datetime.date.today()
    TODAY = today.isoformat()
    filename = today.isoformat() + "-price-log.txt"

    if not os.path.exists(LOG_FILE_DIR):
        os.makedirs(LOG_FILE_DIR)

    log_file = open(LOG_FILE_DIR + filename, "w")
    log_file.write("<item name: current price>\n")
    log_file.write("Items to buy:\n")
    log_file.write(niceFormatItemPrice(items_to_buy))

    log_file.write("\nItems to sell:\n")
    log_file.write(niceFormatItemPrice(items_to_sell))

def invokeNotepadToShowLog():
    """
    Opens up a text editor to show the price log.

    Note: This has only been tested on Windows 10
    """

    log_filename = TODAY + "-price-log.txt"
    
    log_file = open(LOG_FILE_DIR + log_filename, "r")
    if os.path.exists(LOG_FILE_DIR + log_filename):
        if platform.system() is "Windows":
            notepad_pid = Popen(["notepad.exe", LOG_FILE_DIR + log_filename]).pid
        elif platform.system() is "Linux":
            # untested
            gedit_pid = Popen(["gedit", LOG_FILE_DIR + log_filename]).pid
        
def promptGUIAboutItemsStatus():
    """
    Creates a pop-up to notify user the price analysis is complete. The pop-up also has a button
    for the user to open up the log file.
    """

    global GUI_PROMPT

    # set up main graphics window
    GUI_PROMPT = Tkinter.Tk()
    GUI_PROMPT.title("RS GE Notifier")
    GUI_PROMPT.geometry("250x150+300+300")
    program_directory = sys.path[0]
    GUI_PROMPT.wm_iconbitmap(os.path.join(program_directory, "coins.ico"))

    message = StringVar()
    message.set("Done processing item prices!\nYou have potentially " + str(len(ITEMS_TO_BUY)) + " items to buy and " + str(len(ITEMS_TO_SELL)) + " items to sell.\n\nUse the view log button for more details.") 
    message_box = Message(GUI_PROMPT, textvariable = message, width = 200)
    message_box.pack(fill = Y)

    open_log_file_button = Tkinter.Button(GUI_PROMPT, text = "View price log", command = invokeNotepadToShowLog)
    open_log_file_button.pack()
    
    # starts the main window until the user quit it
    GUI_PROMPT.mainloop()

if __name__ == "__main__":
    #parseUserItemsJsonFile("./items.json")
    parseUserItemsJsonFile(os.path.join(sys.path[0], "items.json"))
    gatherAllItemsInformation(ITEMS_FROM_USER)
    determineItemsForBuying(ITEMS_INFO, ITEMS_FROM_USER)
    determineItemsForSelling(ITEMS_INFO, ITEMS_FROM_USER)

    writePriceLogFile(ITEMS_TO_BUY, ITEMS_TO_SELL)

    promptGUIAboutItemsStatus()
