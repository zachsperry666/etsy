"""
Script to read multiple tabs of a google spreadsheet and write it as csv files.

One can download the credentials.json file from:
https://developers.google.com/drive/api/v3/quickstart/python
(click on the Enable the Drive API button)

And then download the libraries from the same page.

Author: Marius Guerard
Most of the code is taken from: https://gist.github.com/xflr6/57508d28adec1cd3cd047032e8d81266)
"""

import os

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd


KEY = 'AIzaSyBC7aKmx2OD58hUnMb9pIFEwKLgtczCY0Y'


def open_service(sheet_id,range):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
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
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range).execute()
    return sheet


def gsheet2df(gsheet):
    """ Converts Google sheet data to a Pandas DataFrame.
    Note: This script assumes that your data contains a header file on the first row!
    Also note that the Google API returns 'none' from empty cells - in order for the code
    below to work, you'll need to make sure your sheet doesn't contain empty cells,
    or update the code to account for such instances.
    """
    header = gsheet.get('values', [])[0]  # Assumes first line is header!
    values = gsheet.get('values', [])[1:]  # Everything else is data.
    # print(values)
    if not values:
        print('No data found.')
    else:
        all_data = []
        for col_id, col_name in enumerate(header):
            # print(col_id)
            # print(col_name)
            column_data = []
            for row in values:
                # print(row)
                column_data.append(row[col_id])
            ds = pd.Series(data=column_data, name=col_name)
            all_data.append(ds)
        df = pd.concat(all_data, axis=1)
        return df
