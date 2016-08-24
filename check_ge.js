var RS_GE_API_URL = "http://services.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item=";

var wine_of_zammy_id = 245;
var clean_cadantine_id = 265;
var clean_kwuarm_id = 263;
var clean_torstol_id = 269;
var clean_toadflax_id = 2998;

var black_dragon_leather_id = 2509;
var red_dragon_leather_id = 2507;
var blue_dragon_leather_id = 2505;
var green_dragon_leather_id = 1745;

var uncut_ruby_id = 1619;
var uncut_diamond_id = 1617;
var uncut_dragonstone_id = 1631;

var super_attack_3_id = 145;
var super_strength_3_id = 157;
var super_defence_3_id = 163;
var super_ranging_3_id = 169;
var super_magic_3_id = 3042;

var mud_rune_id = 4698;

var lustrous_energy_id = 29320;
var vibrant_energy_id = 29319;

var ITEMS_INFO = [];
var test_array = [];

function setUpTestArray() {
    test_array.push(wine_of_zammy_id);
    test_array.push(clean_cadantine_id);
    test_array.push(clean_kwuarm_id);
    test_array.push(clean_torstol_id);
    test_array.push(clean_toadflax_id);
    test_array.push(black_dragon_leather_id);
    test_array.push(blue_dragon_leather_id);
    test_array.push(green_dragon_leather_id);
    test_array.push(red_dragon_leather_id);
    test_array.push(uncut_diamond_id);
    test_array.push(uncut_ruby_id);
    test_array.push(uncut_dragonstone_id);
    test_array.push(super_attack_3_id);
    test_array.push(super_strength_3_id);
    test_array.push(super_defence_3_id);
    test_array.push(super_ranging_3_id);
    test_array.push(super_magic_3_id);
    test_array.push(mud_rune_id);
    test_array.push(lustrous_energy_id);
    test_array.push(vibrant_energy_id);
}

function isNumber(query) {
    return !isNaN(query-0) && query !== null && query !== "" && query !== false;
}

function extractItemID(response_text) {
    return response_text["item"]["id"];
}

function extractItemName(response_text) {
    return response_text["item"]["name"];
}

function extractItemCurrentPrice(response_text) {
    var item_price_str = response_text["item"]["current"]["price"];
    var item_price;
   
    if (isNumber(item_price_str))
    {
        // e.g. 700
        // Note: prices under 1,000 gp seems to return as an integer from the RS API instead of a string
        return item_price_str;
    }

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

function obtainItemInformation(item_id_for_processing) {
    var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
    var item_ge_api_request = new XMLHttpRequest();
    item_ge_api_request.open("GET", RS_GE_API_URL + item_id_for_processing.toString(), false);
    item_ge_api_request.send();

    if (item_ge_api_request.status == 200) {
        //console.log(item_ge_api_request.responseText);
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

function obtainItemFullInformation(item_id) {
    var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
    var item_ge_api_request = new XMLHttpRequest();
    item_ge_api_request.open("GET", RS_GE_API_URL + item_id.toString(), false);
    item_ge_api_request.send();

    if (item_ge_api_request.status == 200) {
        console.log(item_ge_api_request.responseText);
        return item_ge_api_request.responseText;
    }

    return "";
}

function gatherPriceInfoForAllItems(item_list) {
    for (var i = 0; i < item_list.length; i++) {
        obtainItemInformation(item_list[i]);
    }
}

setUpTestArray();
gatherPriceInfoForAllItems(test_array);
//obtainItemInformation("245");
console.log(ITEMS_INFO);
//console.log(obtainItemFullInformation());
