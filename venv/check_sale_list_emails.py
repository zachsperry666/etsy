from venmo_request import venmo_req
from paypal_request import paypal_req
from send_gmail import create_message
from send_gmail import send_message
import tkinter as tk
from tkinter import filedialog
import pandas as pd

root = tk.Tk()
root.withdraw()

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

error_table_email = data["Instagram User"][data["Email"].isna()]
error_table_venmo = data["Instagram User"][data["Venmo Username"].isna() & data["Payment"]=="venmo"]
error_table_pay = data["Instagram User"][data["Payment"].isna()]

pd.set_option('display.max_rows', None)

if len(error_table_email)>0:
    print("The following users have no valid email:")
    print(error_table_email.unique())

if len(error_table_venmo)>0:
    print("The following users have no valid venmo:")
    print(error_table_venmo.unique())

if len(error_table_pay)>0:
    print("The following users have no payment method listed:")
    print(error_table_pay.unique())