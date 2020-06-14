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

output = load_and_check()

if type(output)==bool:
    if output:
        exit()
else:
    data=output
    print(data)

venmo = venmo_auth()

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
    taxable = data_b.iloc[0]['California?']
    pickup = data_b.iloc[0]['Pickup?']
    ret = create_message("succielife@gmail.com",buyer_email,subject,item_list,pay_method,taxable,pickup)
    send_message("me",ret.body)
    if pay_method=='venmo':
        try:
            venmo_req(venmo,data_b.iloc[0]['Venmo Username'], float(ret.total_price), "Succielife! Thank you!")
        except:
            print("Couldn't generate Venmo request for: " + data_b.iloc[0]['Instagram User'] + " (Venmo user: " + data_b.iloc[0]['Venmo Username'] + ")")