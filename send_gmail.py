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


class Ret:
    def __init__(self):
        self.body = ""
        self.total_price = 0


def open_service():
    SCOPES = ['https://mail.google.com/']
    if os.path.exists("C:/Python/Projects/etsy/token.pickle"):
        with open("C:/Python/Projects/etsy/token.pickle", 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def create_message(sender, to, subject, item_list, pay_method, taxable, pickup):
    ret = Ret()
    tax_rate = 0.0725
    # Create the plain-text and HTML version of your message

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

    insert = ""
    print(item_list["Price"])
    total = item_list["Price"].astype(float).sum()
    print(total)
    if total > 100:
        shipping_price = 0
    elif pickup == 'Y':
        shipping_price = 0
    else:
        shipping_price = 5
    total_price = total + shipping_price

    num_items = len(item_list)

    if pay_method == "venmo":

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

    for i in range(num_items):
        insert += '<tr><td>' + item_list.iloc[i]['Names'] + '</td><td>' + str(
            "{:.2f}".format(float(item_list.iloc[i]['Price']))) + '</td></tr>'

    if taxable == 'Y':
        tax = total * tax_rate
        print('Total ('+str(total)+') + Tax ('+str(tax)+')')
        insert += '<tr><td><i>Tax:</i></td><td><i>' + str("{:.2f}".format(tax)) + '</i></td></tr></table>'
        total_price = total_price + tax

    insert += '<tr><td><i><u>Shipping</u></i></td><td><i><u>' + str("{:.2f}".format(shipping_price)) + '</u></i></td' \
                                                                                                       '></tr> '

    insert += '<tr><td><b>Total:</b></td><td><b>' + str("{:.2f}".format(total_price)) + '<b></td></tr></table>'

    soup = Soup(html, features="html.parser")
    soup.div.append(Soup('<div>' + insert + '</div>', features="html.parser"))

    # print(soup)

    # Turn these into plain/html MIMEText objects

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first

    message = MIMEText(soup, 'html')
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = to

    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    ret.body = {'raw': raw}
    ret.total_price = total_price
    return ret


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


def send_message(user_id, message):
    service = open_service()
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message Id: %s' % message['id'])
        return message
    except Exception as e:
        print('An error occurred: %s' % e)
        return None
