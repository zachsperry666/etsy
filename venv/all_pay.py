# This is the main program to call for sending invoices. It uses check_sale_list_emails.py to merge the live sale data
# with the master customer list, both on Google sheets. Then it uses send_gmail.py to create and send email invoices.
# For venmo customers it sends a venmo payment request (handled by venmo_request.py). Finally it reports total CA tax
# to the console.

from venmo_request import venmo_req , venmo_auth
from paypal_request import paypal_req
from send_gmail import create_message
from send_gmail import send_message
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from get_google_sheet import gsheet2df, open_service
from check_sale_list_emails import load_and_check

# invoice_file_path = filedialog.askopenfilename(title="Choose invoice file:",filetypes=[("Excel files", ".xlsx .xls")])

# invoice_data = pd.read_excel(invoice_file_path)

output = load_and_check() # function from check_sale_list_emails to merge live sale and master customer list

if type(output)==bool: # don't proceed if output is a boolean, which means that load_and_check threw an error
    if output:
        exit()
else: #if no error, proceeds with program
    data=output
    print(data)

venmo = venmo_auth() # initializes venmo connection

buyers = data["Instagram User"].unique() # get unique list of buyers, as instagram usernames

nb = len(buyers) # number of unique buyers

#print(nb)

subject = "Your Succielife Invoice" # subject line of email

total_tax = 0 # initialize total tax sum

for b in range(nb): # this loop runs once for each unique buyer
    #print('b='+str(b))
    print(buyers[b]) # buyer name printed to console
    data_b = data[data["Instagram User"] == buyers[b]] # gets list of items and information for this buyer
    item_list=pd.DataFrame(columns=['Names','Price'])
    item_list["Names"] = data_b["Names"]
    item_list["Price"] = data_b["Price"]
    pay_method = data_b.iloc[0]['Payment']
    buyer_email = data_b.iloc[0]['Email']
    taxable = data_b.iloc[0]['California?']
    pickup = data_b.iloc[0]['Pickup?']
    ret = create_message("succielife@gmail.com",buyer_email,subject,item_list,pay_method,taxable,pickup) # generates email, gets total and tax info
    send_message("me",ret.body) # sends email
    total_tax = total_tax + ret.tax
    if pay_method=='venmo':
        try:
            venmo_req(venmo,data_b.iloc[0]['Venmo Username'], float(ret.total_price), "Succielife! Thank you!") # generates venmo request
        except:
            print("Couldn't generate Venmo request for: " + data_b.iloc[0]['Instagram User'] + " (Venmo user: " + data_b.iloc[0]['Venmo Username'] + ")") # reports venmo error

print("Total CA tax: "+total_tax) # prints total tax to console