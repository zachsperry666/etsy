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


def create_message(sender, to, subject, item_list, pay_method):
    # Create the plain-text and HTML version of your message

    html = """\
    <html>
    <body>

    <h2>Your Succielife Invoice</h2>
    
    <p>Thank you for your purchase! Your invoice and instructions for payment are below.</p>

    <div>
    </div>
    
    <p>I work hard to bring you beautiful and unique succulents at crazy good prices!
    If you ever have comments, questions, or concerns, reach out to me at
    <a href="https://www.instagram.com/succielife">Instagram (@succielife)</a>.</p>
    
    <a href="https://ibb.co/QFQXR5t"><img src="https://i.ibb.co/SXyJ8LG/succie-life-word-logo.png" alt="succie-life-word-logo" border="0" width="167" height="89"></a>
    
    </body>
    </html>
        """

    insert = ""
    total = item_list["Price"].sum()
    if total > 100:
        shipping_price = 0
    else:
        shipping_price = 5
    total_price = total + shipping_price

    num_items = len(item_list)

    if pay_method == "Venmo":

        insert += """\
        <p>If we have your <b>Venmo</b> information, you should soon receive a request from 
        Anthony-Dodge. Please hit 'Pay' on the request to complete. If you have not sent us Venmo your information 
        yet, please contact us through <a href='https://www.instagram.com/succielife'>Instagram (@succielife)</a>.</p> """

    elif pay_method == "Paypal":

        insert += """\
        <p>If you are paying via <b>Paypal</b>, please generate a payment for the invoice total to 
        <b>mvhs_celloplayer@yahoo.com</b>. You can start the process <a 
        href="https://www.paypal.com/us/for-you/transfer-money/send-money">here</a>.</p> """

    else:
        insert += """\
        <p>For payments with Zelle or another method, please send us payment information through <a 
        href="https://www.instagram.com/succielife">Instagram (@succielife)</a>. If you have already done so, 
        you can expect a payment request soon.</p> </p> """

    insert += """\
        <table style="width:50%">
          <tr>
            <th align="left">Item Name</th>
            <th align="left">Price</th>
          </tr>
          """

    for i in range(num_items):
        insert += '<tr><td>' + item_list.iloc[i]['Names'] + '</td><td>' + str(item_list.iloc[i]['Price']) + '</td></tr>'

    insert += '<tr><td><u>Shipping<u></td><td><u>' + str(shipping_price) + '<u></td></tr>'

    insert += '<tr><td><b>Total:<b></td><td><b>' + str(total_price) + '<b></td></tr></table>'

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
    body = {'raw': raw}
    return body


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
