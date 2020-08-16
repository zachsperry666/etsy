# called by all_pay.py to send format invoice emails, including calculation of total price, shipping, and tax

from __future__ import print_function

import base64
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup as Soup
import tkinter as tk
from tkinter import filedialog
import pandas as pd


class Ret:  # defines ret, which is the variable returned by the main function create_message.
    def __init__(self):
        self.body = ""  # initialize email body as string
        self.total_price = 0  # initialize total price as number
        self.tax = 0  # initialize tax as number


def open_service():  # this establishes the connection between the draft message and the gmail account to send from
    SCOPES = ['https://mail.google.com/']
    if os.path.exists("C:/Python/Projects/etsy/token.pickle"):
        with open("C:/Python/Projects/etsy/token.pickle", 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not ('creds' in locals()) or not creds or not creds.valid:
        if 'creds' in locals() and creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:\Python\Projects\etsy\credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def create_message(sender, to, subject, item_list, pay_method, taxable, pickup, shipping):
    ret = Ret()  # initializes return variable
    tax_rate = 0.0725
    # Create the plain-text and HTML version of your message

    # form email, variable portion goes in the <div> section

    #  <p><b>Click <a href="https://cutt.ly/succielifetshirt">here</a> to pre-order your SuccieLife t-shirt,
    #  20% off for a limited time!</b></p>

    html = """\
    <html>
    <body>

    <h2>Your Succielife Invoice</h2>
    
    <p>Thank you for tuning in to another live sale! Please find your invoice and instructions for payment below.</p>
    
    <div>
    </div>
    
    <p>If you would like to combine your live sale order with an Etsy order, we are happy to do so! Just send me a 
    message after you place your order on Etsy. Our Etsy shop can be found <a href="www.succielife.etsy.com">here</a>.</p> 
    
    <p>Thank you for your support of our small business! Plants will be shipped in the next few days. If you ever 
    have comments, questions, or concerns, please don’t hesitate to reach out to us on <a 
    href="https://www.instagram.com/succielife">Instagram (@succielife)</a>.</p> 
    
    </body>
    </html>
        """

    insert = ""  # initializes variable portion of email
    total = item_list["Price"].astype(float).sum()  # calculates total for buyer
    if total > 100:  # calculates shipping based on total price and shipping preference (default is $5)
        shipping_price = 0
    elif pickup == 'Y':
        shipping_price = 0
    else:
        shipping_price = 5
    total_price = total + shipping_price  # updates total order price

    num_items = len(item_list)

    if pickup == 'Y':
        addr_insert = "Pickup"
    elif pickup == "N":
        addr_insert = shipping.replace('\n', '<br>')
        print(repr(shipping))

    insert += "<p>Shipping address on file:</p>"
    insert += "<p>" + addr_insert + "</p>"

    if pay_method == "venmo":  # email portion depending on payment type

        insert += """\
        <p>If you have requested to pay via Venmo, you should soon receive a request from 
        Anthony-Dodge. Please hit 'Pay' on the request to complete. If you do not receive a request, please let us 
        know. </p> """

    elif pay_method == "paypal":

        insert += """\
        <p>For payments via Paypal, please send payment for invoice total to succielife@gmail.com. You 
        can start the process <a href="https://www.paypal.com/us/for-you/transfer-money/send-money">here</a>.</p> """

    else:
        insert += """\
        <p>For payments with Zelle or Quickpay, please send payment to Anthony Dodge - dodg0091@umn.edu. </p> </p> """

    # initialize table of items and prices
    insert += """\
        <style>
      table,
      th,
      td {
        padding: 10px;
        border: 1px solid black;
        border-collapse: collapse;
      }
    </style>
        <table style="width:50%">
          <tr>
            <th align="left"><u>Item Name</u></th>
            <th align="left"><u>Price</u></th>
          </tr>
          """

    # fill table of items and prices
    for i in range(num_items):
        insert += '<tr><td>' + item_list.iloc[i]['Names'] + '</td><td>' + str(
            "{:.2f}".format(float(item_list.iloc[i]['Price']))) + '</td></tr>'

    tax = 0  # initialize tax
    if taxable == 'Y':  # calculates and adds tax to total price and invoice, if applicable
        tax = total * tax_rate
        insert += '<tr><td><i>Tax:</i></td><td><i>' + str("{:.2f}".format(tax)) + '</i></td></tr></table>'
        total_price = total_price + tax

    # adds shipping to invoice table
    insert += '<tr><td><i><u>Shipping</u></i></td><td><i><u>' + str("{:.2f}".format(shipping_price)) + '</u></i></td' \
                                                                                                       '></tr> '
    # adds total price to invoice table
    insert += '<tr><td><b>Total:</b></td><td><b>' + str("{:.2f}".format(total_price)) + '<b></td></tr></table>'

    soup = Soup(html, features="html.parser")  # program to niceley handle html code for email
    soup.div.append(Soup('<div>' + insert + '</div>', features="html.parser"))

    # print(soup)

    # Turn these into plain/html MIMEText objects

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first

    # generates email message
    message = MIMEText(soup, 'html')
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = to

    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    ret.body = {'raw': raw}
    ret.total_price = total_price
    ret.tax = tax
    return ret


# NOT USED YET but could generate a draft to save to the gmail inbox rather than an actual message...not sure if useful, copypasta
def create_draft(user_id, message_body):
    service = open_service()
    try:
        message = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body=message).execute()

        print("Draft id: %s\nDraft message: %s" % (draft['id'], draft['message']))

        return draft
    except Exception as e:
        print('An error occurred: %s' % e)
        return None


# function to send generated email message
def send_message(user_id, message):
    service = open_service()
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message Id: %s' % message['id'])
        return message
    except Exception as e:
        print('An error occurred: %s' % e)
        return None
