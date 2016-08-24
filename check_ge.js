var RS_GE_API_URL = "http://services.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item=";
var wine_of_zammy_id = 245;
var ITEMS_INFO = [];

function extractItemID(response_text) {
    return response_text["item"]["id"];
}

function extractItemName(response_text){
    return response_text["item"]["name"];
}

function extractItemCurrentPrice(response_text){
    var item_price_str = response_text["item"]["current"]["price"];
    var item_price;
    
    if (item_price_str.includes(".") && item_price_str.includes("k")) {
        // e.g. "10.1k"
        item_price = parseInt(item_price_str.replace(",","").replace(".", "").replace("k","00"));
    } 
    else
    {
        // e.g. "9,700"
        item_price = parseInt(item_price_str.replace(",",""));
    }

    return item_price;
}

function obtainItemInformation(item_id_for_processing)
{
    var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
    var item_ge_api_request = new XMLHttpRequest();
    item_ge_api_request.open("GET", RS_GE_API_URL + item_id_for_processing, false);
    item_ge_api_request.send();

    if (item_ge_api_request.status == 200) {
//        console.log(item_ge_api_request.responseText);
        var item_info_object = JSON.parse(item_ge_api_request.responseText);
        var item = {
            name: extractItemName(item_info_object),
            id: extractItemID(item_info_object),
            currentPrice: extractItemCurrentPrice(item_info_object)
        };
        ITEMS_INFO.push(item);
    }
    else {
        console.log("Error obtaining information about item with ID: " + item_id_for_processing);
    }
}

obtainItemInformation("245");
console.log(ITEMS_INFO);
