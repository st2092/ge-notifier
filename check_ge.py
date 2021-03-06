import urllib2
import json
import pprint
import Tkinter
import datetime
import os
import platform
from subprocess import call, Popen
from Tkinter import *
try:
    import cPickle as pickle
except:
    import pickle

RS_GE_API_URL = "http://services.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item="
RS_RUNEDATE_URL = "https://secure.runescape.com/m=itemdb_rs/api/info.json"
OSRS_RUNEDATE_URL = "https://secure.runescape.com/m=itemdb_oldschool/api/info.json";
OSRS_GE_API_URL = "http://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item=";
RS3 = 0
OSRS = 1
MODE_VERSION = RS3
LOG_FILE_DIR = sys.path[0] + "/price-logs/"
DATABASE_FILE_DIR = sys.path[0] + "/database/"
ITEMS_INFO = {}
ITEMS_FROM_USER = {}
ITEMS_TO_SELL = []
ITEMS_TO_BUY = []
TODAY = None
GUI_PROMPT = None
PRICE_DATABASE_FILENAME = "prices_db.json"
MOD_DATE_DB_FILENAME = "mod_date.db"
USER_ITEMS_FILENAME = "items.json"
NATURE_RUNE_ID = 561
GE_UPDATE_CHECK_ITEM = NATURE_RUNE_ID
LAST_GE_UPDATE_FILENAME = "last_ge_update.db"

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
        item_price = int(item_price_str.replace(',',''))
    elif '.' in item_price_str and 'm' in item_price_str:
        # e.g. 12.8m
        item_price = int(item_price_str.replace('.', '').replace(',', '').replace('m', "00000"))
    elif '.' in item_price_str and 'b' in item_price_str:
        # e.g. 2.1b
        item_price = int(item_price_str.replace('.', '').replace(',', '').replace('b', "00000000"))
    else:
        # e.g. 100
        item_price = int(item_price_str)

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

    global item_number, MODE_VERSION
    if MODE_VERSION == RS3:
        request_string = RS_GE_API_URL + str(item_id)
    else:
        request_string = OSRS_GE_API_URL + str(item_id)

    request_api_data = urllib2.Request(request_string)
    response_text = urllib2.urlopen(request_api_data).read()
    item_info_dictionary = json.loads(response_text)
    
    if item_key_from_user is not None:
        item = {}
        item["name"] = extractItemName(item_info_dictionary)
        item["id"] = extractItemId(item_info_dictionary)
        item["currentPrice"] = extractItemCurrentPrice(item_info_dictionary)
        ITEMS_INFO[item_key_from_user] = item
    else:
        return extractItemCurrentPrice(item_info_dictionary)

def parseUserItemsJsonFile(path_to_user_item_list):
    """
    Parse the item file provided by the user. Convert it into a dictionary
    for use to query RS API.

    Parameters:
    path_to_user_item_list -- the full path to the json file containing all the items
                              and their associated buy/sell prices 
    """
    
    global ITEMS_FROM_USER, MODE_VERSION
    user_items_json_file = open(path_to_user_item_list, 'r')
    user_items_list_json_text = user_items_json_file.read()
    user_items_dictionary = json.loads(user_items_list_json_text)

    if "type" in user_items_dictionary:
        itemFileType = user_items_dictionary["type"]["version"]
        if (itemFileType == OSRS):
            MODE_VERSION = OSRS
            print "Set to OSRS mode"
        else:
            print "Set to RS3 mode"
        del user_items_dictionary["type"]    

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

def getFileLastModifiedDate(full_path_to_file):
    return os.path.getmtime(full_path_to_file)

def backupPriceDatabase():
    if not os.path.exists(DATABASE_FILE_DIR):
        os.makedirs(DATABASE_FILE_DIR)

    price_data_file = open(DATABASE_FILE_DIR + PRICE_DATABASE_FILENAME, "w")
    json.dump(ITEMS_INFO, price_data_file)

def loadPriceBackupDatabase():
    if os.path.exists(DATABASE_FILE_DIR + PRICE_DATABASE_FILENAME):
        price_data_file = open(DATABASE_FILE_DIR + PRICE_DATABASE_FILENAME, "r")
        return json.load(price_data_file)
    else:
        return {}

def backupModDateDatabase():
    if not os.path.exists(DATABASE_FILE_DIR):
        os.makedirs(DATABASE_FILE_DIR)
    mod_date_db_file = open(DATABASE_FILE_DIR + MOD_DATE_DB_FILENAME, 'wb')
    pickle.dump(getFileLastModifiedDate(os.path.join(sys.path[0], USER_ITEMS_FILENAME)), mod_date_db_file)

def backupGEUpdateInformation():
    if not os.path.exists(DATABASE_FILE_DIR):
        os.makedirs(DATABASE_FILE_DIR)
    ge_update_db_file = open(DATABASE_FILE_DIR + LAST_GE_UPDATE_FILENAME, "w")
    pickle.dump(getFileLastModifiedDate(os.path.join(sys.path[0], USER_ITEMS_FILENAME)), ge_update_db_file)
    pickle.dump(obtainItemInformation(GE_UPDATE_CHECK_ITEM, None), ge_update_db_file)

def sameTimeStamp(time1, time2):
    return time1 == time2

def samePrice(price1, price2):
    return price1 == price2

def getRunedate():
    request_api_data = urllib2.Request(RS_RUNEDATE_URL)
    response_text = urllib2.urlopen(request_api_data).read()
    print response_text

def lastGEUpdate():
    """
    Obtains the last time the grand exchange price's updated. Ideally, we would like to know
    the date and or time. But with the limitation of the RS API, we will be checking the
    recorded price of an item that we know is always changing with each update.
    
    Returns -- last modified time of user json file and last recorded GE update
    """
    if not os.path.exists(DATABASE_FILE_DIR + LAST_GE_UPDATE_FILENAME):
        return None, None
    else:
        ge_update_db_file = open(DATABASE_FILE_DIR + LAST_GE_UPDATE_FILENAME, "r")
        user_item_file_last_modified_datetime = pickle.load(ge_update_db_file)
        last_ge_update_price = pickle.load(ge_update_db_file)
        return user_item_file_last_modified_datetime, last_ge_update_price


def geHasUpdated():
    """
    Checks if the grand exchange prices' have updated compare to the last time
    this script ran.

    Note: Due to the limitation of the RS API, for checking price update we will
    use a very commonly trade item. The price of that item is compare to the last
    time.
    """
    item_file_last_modified_datetime, last_ge_update_check_price = lastGEUpdate()
    current_ge_update_check_price = obtainItemInformation(GE_UPDATE_CHECK_ITEM, None)
    if sameTimeStamp(getFileLastModifiedDate(os.path.join(sys.path[0], USER_ITEMS_FILENAME)), item_file_last_modified_datetime) and samePrice(last_ge_update_check_price, current_ge_update_check_price):
        return False
    else:
        return True


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
    if MODE_VERSION == RS3:
        GUI_PROMPT.title("RS3 GE Notifier")
    else:
        GUI_PROMPT.title("OSRS GE Notifier")

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

def obtainUpToDatePricesFromRsApi():
    gatherAllItemsInformation(ITEMS_FROM_USER)
    determineItemsForBuying(ITEMS_INFO, ITEMS_FROM_USER)
    determineItemsForSelling(ITEMS_INFO, ITEMS_FROM_USER)

def backUpAllDatabases():
    backupPriceDatabase()
    backupModDateDatabase()
    backupGEUpdateInformation()

def main_geUpdated():
    print "There was a price update...\nUpdating prices please wait..."
    parseUserItemsJsonFile(os.path.join(sys.path[0], USER_ITEMS_FILENAME))
    obtainUpToDatePricesFromRsApi()

    writePriceLogFile(ITEMS_TO_BUY, ITEMS_TO_SELL)

    backUpAllDatabases()

def main_noGeUpdate():
    print "There has not been an update today."
    parseUserItemsJsonFile(os.path.join(sys.path[0], USER_ITEMS_FILENAME))
    ITEMS_INFO = loadPriceBackupDatabase()
    determineItemsForBuying(ITEMS_INFO, ITEMS_FROM_USER)
    determineItemsForSelling(ITEMS_INFO, ITEMS_FROM_USER)

    writePriceLogFile(ITEMS_TO_BUY, ITEMS_TO_SELL)

if __name__ == "__main__":
    if geHasUpdated():
        main_geUpdated()
    else:
        main_noGeUpdate()

    promptGUIAboutItemsStatus()
