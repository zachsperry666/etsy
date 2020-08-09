# This program is called by all_pay.py to send invoices. It can be called alone (using the __name__==('__main_') syntax)
# to check the live sale data against the master customer list for validity without sending any invoices.
from venmo_request import venmo_req , venmo_auth
from paypal_request import paypal_req
from send_gmail import create_message
from send_gmail import send_message
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from get_google_sheet import gsheet2df, open_service
import re
from df2gspread import df2gspread as dg2

# for custom mails use: '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'

# Define a function for
# for validating an Email
# NOT USED YET
def check(email):
    # Make a regular expression
    # for validating an Email
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    # pass the regular expression
    # and the string in search() method
    test = email.str.contains(regex)
    test=test[""]
    return test

def load_and_check(): # main loop to check if all required info for live sale is in master customer list, if true then generates merged data table
    stop_on_error = False
    root = tk.Tk() # this is important for some reason to use Tk()
    root.withdraw()

    # this was commented out when we started using Google spreadsheets, but would read an excel file
    # invoice_file_path = filedialog.askopenfilename(title="Choose invoice file:",filetypes=[("Excel files", ".xlsx .xls")])

    # invoice_data = pd.read_excel(invoice_file_path)

    MASTER_ID = '1-Et2zIxQq28ZNXkeiWCO976QKlIPOvoFs9VIwIyddhA' #ID of master customer list google spreadsheet
    SALES_ID = '1tIFKnnx26bIDO0SGnsMADLBIlx35jFObH_gJP_J8JiY' #ID of live sale google spreadsheet

    invoice_sheet = open_service(SALES_ID, input('Input Live Sale Sheet ID: ')) #identify tab of live sale sheet to reference, can use "Live Sale Test" as sandbox
    master_sheet = open_service(MASTER_ID, 'Sheet1') #gets master customer list
    invoice_data = gsheet2df(invoice_sheet.sheet).drop_duplicates() #converts spreadsheet to pandas dataframe
    print(invoice_data)
    invoice_data["Instagram User"] = invoice_data["Instagram User"].str.lower()

    # master_file_path = filedialog.askopenfilename(title="Choose master customer list file:",filetypes=[("Excel files", ".xlsx .xls")])

    # master_data = pd.read_excel(master_file_path)

    master_data = gsheet2df(master_sheet.sheet).drop_duplicates() # gets rid of duplicates in the customer list
    master_data["Instagram User"] = master_data["Instagram User"].str.lower().str.strip() # cleans up potential extra spaces
    master_data["Payment"] = master_data["Payment"].str.lower().str.strip()

    data = pd.merge(invoice_data, master_data, how='left', on=None, left_on=None, right_on=None, #combines the live sale list with the master customer list
                    left_index=False, right_index=False, sort=True,
                    suffixes=('_x', '_y'), copy=True, indicator=False,
                    validate=None)

    error_table_email1 = data["Instagram User"][data["Email"]==''] #checks for empty email
    error_table_email2 = data["Instagram User"][data["Email"].isna()]
    error_table_email3 = data["Instagram User"][data["Email"]=='succielife@gmail.com']
    error_table_venmo = data["Instagram User"][data["Venmo Username"].isna() & data["Payment"] == "venmo"] #checks for empty venmo user
    error_table_pay = data["Instagram User"][data["Payment"].isna()] #checks for empty payment preference

    data_invoice = data[(data["Email"]!="") & (~(data["Email"].isna())) & (
        ~(data["Venmo Username"].isna() & data["Payment"] == "venmo")) & (~(data["Payment"].isna()))]
    data_wait = data[(data["Email"]=="") | (data["Email"].isna()) | (data["Venmo Username"].isna() | data["Payment"] == "venmo") | (data["Payment"].isna())]

    if len(data_wait) > 0 :
        data_wait = data_wait[["Instagram User","ID","Names","Price"]]

    pd.set_option('display.max_rows', None) #setting to print entire data frame to console (otherwise it abridges)

    stop = False #continues by default
    if len(error_table_email1.isnull())>0: #stop if no email
        print("The following users have no valid email:")
        print(error_table_email1.unique())
        stop = True
    elif len(error_table_email2.isnull())>0: #stop if no email
        print("The following users have no valid email:")
        print(error_table_email2.unique())
        stop = True
    else:
        print("All emails found!")

    if len(error_table_venmo) > 0: #stop of no venmo and needed
        print("The following users have no valid venmo:")
        print(error_table_venmo.unique())
        stop = True
    else:
        print("All Venmo found!")

    if len(error_table_pay) > 0: #stop if no payment preference
        print("The following users have no payment method listed:")
        print(error_table_pay.unique())
        stop = True
    else:
        print("All payment found!")

    if len(data_wait) > 0:
        wks_name = 'Pending Invoices'
        dg2.upload(data_wait, SALES_ID, wks_name)

    if stop & stop_on_error:
        return stop
    else:
        return data_invoice

if __name__==('__main__'): #just runs load_and_check
    load_and_check()