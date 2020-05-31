from venmo_request import venmo_req , venmo_auth
from paypal_request import paypal_req
from send_gmail import create_message
from send_gmail import send_message
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from get_google_sheet import gsheet2df, open_service

root = tk.Tk()
root.withdraw()

# invoice_file_path = filedialog.askopenfilename(title="Choose invoice file:",filetypes=[("Excel files", ".xlsx .xls")])

# invoice_data = pd.read_excel(invoice_file_path)

MASTER_ID = '1-Et2zIxQq28ZNXkeiWCO976QKlIPOvoFs9VIwIyddhA'
SALES_ID = '1tIFKnnx26bIDO0SGnsMADLBIlx35jFObH_gJP_J8JiY'

invoice_sheet = open_service(SALES_ID,input('Input Live Sale Sheet ID: '))
master_sheet = open_service(MASTER_ID,'Sheet1')
invoice_data = gsheet2df(invoice_sheet)
# print(invoice_data)
invoice_data["Instagram User"] = invoice_data["Instagram User"].str.lower()

# master_file_path = filedialog.askopenfilename(title="Choose master customer list file:",filetypes=[("Excel files", ".xlsx .xls")])

# master_data = pd.read_excel(master_file_path)

master_data=gsheet2df(master_sheet)
print(master_data)
master_data["Instagram User"] = master_data["Instagram User"].str.lower()
master_data["Payment"] = master_data["Payment"].str.lower()

data = pd.merge(invoice_data, master_data, how='left', on=None, left_on=None, right_on=None,
         left_index=False, right_index=False, sort=True,
         suffixes=('_x', '_y'), copy=True, indicator=False,
         validate=None)

error_table_email = data["Instagram User"][data["Email"].isna()]
error_table_venmo = data["Instagram User"][data["Venmo Username"].isna() & data["Payment"]=="venmo"]
error_table_pay = data["Instagram User"][data["Payment"].isna()]

pd.set_option('display.max_rows', None)

if len(error_table_email)>0:
    print("The following users have no valid email:")
    print(error_table_email.unique())
else:
    print("All emails found!")

if len(error_table_venmo)>0:
    print("The following users have no valid venmo:")
    print(error_table_venmo.unique())
else:
    print("All Venmo found!")

if len(error_table_pay)>0:
    print("The following users have no payment method listed:")
    print(error_table_pay.unique())
else:
    print("All payment found!")