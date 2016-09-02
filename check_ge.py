import urllib2
import json
import pprint

RS_GE_API_URL = "http://services.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item="
ITEMS_INFO = {}
ITEMS_FROM_USER = {}
ITEMS_TO_SELL = []
ITEMS_TO_BUY = []

def isUnicode(query_string):
    return isinstance(query_string, unicode);

def convertStringFromAPIToInt(item_price_str):
    item_price = -1
    #print type(item_price_str)
    #print "String value: " + item_price_str
    if '.' in item_price_str and 'k' in item_price_str:
        # e.g. "10.1k"
        item_price = int(item_price_str.replace('.','').replace(',','').replace('k',"00"))
    elif ',' in item_price_str:
        # e.g. "9,700"
        item_price = int(item_price_str.replace(",",""))

    return item_price

     
def extractItemCurrentPrice(item_dict):
    item_price_str = item_dict["item"]["current"]["price"]
    #print type(item_price_str)
    if isinstance(item_price_str, unicode):
        return convertStringFromAPIToInt(item_price_str.encode('ascii','replace'))
    else:
        return item_price_str

def extractItemId(item_dict):
    item_id = item_dict["item"]["id"]
    return item_id

def extractItemName(item_dict):
    item_name = item_dict["item"]["name"]
    if isUnicode(item_name):
        item_name = item_name.encode('ascii','replace')

    return item_name

def obtainItemInformation(item_id, item_key_from_user):
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
    global ITEMS_FROM_USER
    user_items_json_file = open(path_to_user_item_list, 'r')
    user_items_list_json_text = user_items_json_file.read()
    user_items_dictionary = json.loads(user_items_list_json_text)

    ITEMS_FROM_USER = user_items_dictionary

def gatherAllItemsInformation(user_items_dictionary):
    for key, item_info in sorted(user_items_dictionary.iteritems()):
        obtainItemInformation(item_info["id"], key)

def priceWithinSellingMargin(current_price, item_sell_price, margin):
    return current_price >= item_sell_price - margin

def determineItemsForSelling(items_current_prices, items_sell_prices):
    global ITEMS_TO_SELL
    for key, item in items_current_prices.iteritems():
        if priceWithinSellingMargin(item["currentPrice"], items_sell_prices[key]["sellPrice"], items_sell_prices[key]["sellMargin"]):
            ITEMS_TO_SELL.append({ "name": item["name"], "currentPrice": item["currentPrice"] })

def priceWithinBuyMargin(current_price, item_buy_price, margin):
    return current_price <= item_buy_price + margin

def determineItemsForBuying(items_current_prices, items_buy_prices):
    global ITEMS_TO_BUY
    for key, item in items_current_prices.iteritems():
        if priceWithinBuyMargin(item["currentPrice"], items_buy_prices[key]["buyPrice"], items_buy_prices[key]["buyMargin"]):
            ITEMS_TO_BUY.append({ "name": item["name"], "currentPrice": item["currentPrice"] })

if __name__ == "__main__":
    parseUserItemsJsonFile("./items.json")
    gatherAllItemsInformation(ITEMS_FROM_USER)
    determineItemsForBuying(ITEMS_INFO, ITEMS_FROM_USER)
    determineItemsForSelling(ITEMS_INFO, ITEMS_FROM_USER)
    print "\nITEMS TO SELL\n"
    pprint.pprint(ITEMS_TO_SELL)
    print "\nITEMS TO BUY\n"
    pprint.pprint(ITEMS_TO_BUY)
