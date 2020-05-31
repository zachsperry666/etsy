from venmo_request import venmo_req , venmo_auth
from paypal_request import paypal_req
from send_gmail import create_message
from send_gmail import send_message
import tkinter as tk
from tkinter import filedialog
import pandas as pd

root = tk.Tk()
root.withdraw()
venmo = venmo_auth()

invoice_file_path = filedialog.askopenfilename(title="Choose invoice file:",filetypes=[("Excel files", ".xlsx .xls")])

invoice_data = pd.read_excel(invoice_file_path)
invoice_data["Instagram User"] = invoice_data["Instagram User"].str.lower()

master_file_path = filedialog.askopenfilename(title="Choose master customer list file:",filetypes=[("Excel files", ".xlsx .xls")])

master_data = pd.read_excel(master_file_path)

master_data["Instagram User"] = master_data["Instagram User"].str.lower()
master_data["Payment"] = master_data["Payment"].str.lower()

data = pd.merge(invoice_data, master_data, how='left', on=None, left_on=None, right_on=None,
         left_index=False, right_index=False, sort=True,
         suffixes=('_x', '_y'), copy=True, indicator=False,
         validate=None)

error_table = data["Instagram User"][data["Email"].isna()]

if len(error_table)>0:
    print("The following users have no valid email:")
    print(error_table)
    exit()

#print(data)

buyers = data["Instagram User"].unique()

nb = len(buyers)

#print(nb)

subject = "Your Succielife Invoice"

for b in range(nb):
    #print('b='+str(b))
    print(buyers[b])
    data_b = data[data["Instagram User"] == buyers[b]]
    item_list=pd.DataFrame(columns=['Names','Price'])
    item_list["Names"] = data_b["Names"]
    item_list["Price"] = data_b["Price"]
    pay_method = data_b.iloc[0]['Payment']
    buyer_email = data_b.iloc[0]['Email']
    this_mess = create_message("succielife@gmail.com",buyer_email,subject,item_list,pay_method)
    send_message("me",this_mess)
    if pay_method=='venmo':
        total = item_list["Price"].sum()
        if total > 100:
            shipping_price = 0
        else:
            shipping_price = 5
        total_price = total + shipping_price
        try:
            venmo_req(venmo,data_b.iloc[0]['Venmo Username'], float(total_price), "Succielife! Thank you!")
        except:
            print("Couldn't generate Venmo request for: " + data_b.iloc[0]['Instagram User'] + " (Venmo user: " + data_b.iloc[0]['Venmo Username'] + ")")