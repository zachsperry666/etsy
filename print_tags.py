import tkinter as tk
from tkinter import filedialog
import pandas as pd
from oauth_etsy import get_oauth
from oauth_etsy import use_oauth
import sys
import numpy as np
import array
from datetime import datetime
import time
import PySimpleGUI as sg

date = input('Input start date for orders to pack as m/d/yy: ')

dt = datetime.strptime(date, '%m/%d/%y')

unixtime = time.mktime(dt.timetuple())

etsy = use_oauth()
print('Collecting receipts...')
i = 1
receipts_all = list()
receipts_this = etsy.findAllShopReceipts(shop_id='19387834', min_created=unixtime, limit=100, page=i)

while len(receipts_this) > 0:
    i = i + 1
    receipts_all.extend(receipts_this)
    receipts_this = etsy.findAllShopReceipts(shop_id='19387834', min_created=unixtime, limit=100, page=i)

print('Receipts collected...')
data = pd.DataFrame(receipts_all)

root = tk.Tk()
root.withdraw()

# file_path = filedialog.askopenfilename()
#
# data = pd.read_excel(file_path, header=1)

# item = data["Item Name"]
#
# names_only = item.str.findall(' - (.*?) - ')
#
# error_check = pd.DataFrame(columns=['excel_row', 'check'])
#
# error_check["check"] = item.str.count(' - ') == 2
# error_check["excel_row"] = error_check.index + 2
# print(error_check[error_check["check"] == False])
#
# data["Names"] = names_only
#
# data["Names"] = data["Names"].str[0]
#
# buyers = data["Ship Name"].unique()

buyers = data['name'].unique()

nb = len(buyers)

to_print = []

for b in range(nb):  # in range(nb):
    # perc_comp = "%.1f" % (b/nb*100)
    # print('Processing: ' + perc_comp + '% complete...')
    sg.one_line_progress_meter('Receipt Progress:', b + 1, nb, key='meter')
    messages = list()
    data_b = data[data["name"] == buyers[b]]
    receipts = data_b["receipt_id"].values
    items_b = list()
    to_print.append('* ' + buyers[b] + ' *')
    total = 0
    for r in range(len(receipts)):
        receipt_this = receipts[r].item()
        # print(receipt_this)
        transactions_this = etsy.findAllShop_Receipt2Transactions(receipt_id=receipt_this,
                                                                  limit=100)  # turn back on printing url in requests.sessions
        receipt_obj = next(item for item in receipts_all if item["receipt_id"] == receipt_this)
        # receipt_obj = receipt_obj[0]
        if not (receipt_obj['message_from_buyer'] is None):
            if not receipt_obj['message_from_buyer'] == '':
                messages.append('Message: ' + receipt_obj["message_from_buyer"].replace('&#39;', "'").replace('&quot;', "'"))
        if not (receipt_obj['gift_message'] is None):
            if not receipt_obj['gift_message'] == '':
                messages.append('Gift: ' + receipt_obj["gift_message"].replace('&#39;', "'").replace('&quot;', "'"))
        for t in range(len(transactions_this)):
            item_this = transactions_this[t]
            for q in range(item_this["quantity"]):
                try:
                    to_print.append(item_this["title"].rsplit(' - ')[1].replace('&#39;', "'").replace('&quot;', "'"))
                except:
                    print('Bad Listing: ' + item_this["title"].replace('&#39;', "'").replace('&quot;',
                                                                                             '"') + ' (Listing '
                                                                                                    'ID: ' +
                          str(item_this['listing_id']) + ')')
                    to_print.append(item_this["title"].replace('&#39;', "'").replace('&quot;', '"'))

                total = total + float(item_this["price"])

    # print(data_b)

    # print(num_purch)
    # print(total)
    if total >= 50:
        to_print.append('Gift  =)')
    for m in range(len(messages)):
        to_print.append(messages[m])
    # elif total >= 35:
    #    to_print.append('Gift  =)')

#print(to_print)
# data_update.to_excel(file_path.replace('.xls', ' - updated.xls'))
root.wm_attributes('-topmost', 1)
file_path = filedialog.asksaveasfile(initialfile='etsy_tags_' + date.replace('/', '-'), defaultextension='.xls',
                                     filetypes=([("Excel files", "*.xls")]))

df = pd.DataFrame(to_print)
writer = pd.ExcelWriter(file_path.name)
df.to_excel(writer, index=False, header=False)
writer.save()
