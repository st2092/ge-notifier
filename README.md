# __Grand Exchange Notifier__

Keep track of all your precious investments on Runescape 3 without checking prices yourself every day. Add in your item to look out for, set your buy and sell price, and you are ready to go. Run the script when you need to know how your items are doing and find out if it is time to buy or sell.

**Note**: I am not responsible for any failed investments that occurred due to the usage of this project. It is only to help simplified the investment process.

## __How To Use__

Clone this repository and add in your items into the items json file. Then run the script.

If this is your first time use, you need to create the items json file either manually or using the [Items File Creator](https://github.com/st2092/items-file-creator).

On Linux,

```
python ./check_ge.py
```

On Windows,

```
C:\Python27\python.exe <path-to-ge-notifier-dirctory>\check_ge.py
```

Alternatively, you can run the cmd file to run the script on Windows.

When the script is done processing, you'll get a pop up letting you know how your items are doing.

![Main Interface](/imgs/main-interface.PNG)

![Log file](/imgs/log-file.PNG)


## __How To Add Items Manually__

The items.json file follows the following format

```
"item#": { "name": "ITEM NAME", "id": "ITEM_ID", "buyPrice": YOUR_BUY_PRICE, "sellPrice": YOUR_SELL_PRICE, "buyMargin": YOUR_MARGIN_FOR_BUYING, "sellMargin": YOUR_MARGIN_FOR_SELLING}
```


In the item entry, the ITEM_ID and ITEM NAME are the only two parts that you must find out for your item. The rest is what you want to put in.

### __How To Find ITEM_ID__

The easiest way to get the ITEM_ID for your item is to go to the [official Runescape Grand Exchange catalog page](http://services.runescape.com/m=itemdb_rs/). Then search for your item. I am going to use raw shark.

The numbers at the end of the web browser's URL is the item number for your item. For example, this is the URL for raw shark from the Grand Exchange Catalog.

```
http://services.runescape.com/m=itemdb_rs/Raw_shark/viewitem?obj=383
```

In this case, raw shark's ITEM_ID is 383.

### __How To Find ITEM NAME__

To find the ITEM NAME, you must first have the ITEM_ID for your item. Once you do, you can get the name by web browser. Enter the following URL into the web browser, but **REPLACE X with the ITEM_ID**.

```
http://services.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item=X
```

For example, for raw shark with ITEM_ID of 383, the URL is
```
http://services.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item=383
```

You will get back a lot of extra details, but what you are after is the name. Capitalization, spaces, and symbols do matter, so I recommend copy and paste to avoid any error.

Here is the data you will see for raw shark.

```
{"item":{"icon":"http://services.runescape.com/m=itemdb_rs/1523872848638_obj_sprite.gif?id=383","icon_large":"http://services.runescape.com/m=itemdb_rs/1523872848638_obj_big.gif?id=383","id":383,"type":"Cooking ingredients","typeIcon":"http://www.runescape.com/img/categories/Cooking ingredients","name":"Raw shark","description":"I should try cooking this.","current":{"trend":"neutral","price":"1,172"},"today":{"trend":"positive","price":"+9"},"members":"true","day30":{"trend":"positive","change":"+6.0%"},"day90":{"trend":"negative","change":"-21.0%"},"day180":{"trend":"negative","change":"-4.0%"}}}
```

So, in this case, the ITEM NAME is from the entry "name": "Raw shark". The ITEM NAME is Raw shark.