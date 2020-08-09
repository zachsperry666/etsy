from send_gmail import open_service
from datetime import datetime
import time
import re
import pandas as pd
from df2gspread import df2gspread as dg2

serv = open_service()

# Call the Gmail API to fetch INBOX
# results = serv.users().labels().list(userId='me').execute()
# labels = results.get('labels', [])

# if not labels:
#     print('No labels found.')
# else:
#   print('Labels:')
#   for label in labels:
#     print(label['name']+ " "+label['id'])

date = input('Input live sale date as m/d/yy: ')  # user inputs start date for etsy orders

dt = datetime.strptime(date, '%m/%d/%y')  # converts string date to date format

unixtime = time.mktime(dt.timetuple())  # converts data to unixtime format (for etxy API)

results = serv.users().messages().list(userId='me', labelIds=['Label_3458690111019497815']).execute()
paypal_messages = results.get('messages', [])

results = serv.users().messages().list(userId='me', labelIds=['Label_8575013520056744518']).execute()
venmo_messages = results.get('messages', [])

payer = list()
amount = list()

# print('Getting paypal')
for message in paypal_messages:
    msg = serv.users().messages().get(userId='me', id=message['id']).execute()
    if unixtime <= float(msg.get('internalDate')) / 1000:
        payer_this = re.compile('(?<=Hello, Anthony Dodge )(.+?)(?= sent)').search(msg['snippet'])
        # print(msg['snippet'])
        pay_amount = re.compile('(?<=\$)(([1-9]\d*)?\d)(\.\d\d)').search(msg['snippet'])
        payer.append(payer_this.group(0))
        amount.append(pay_amount.group(0))
        print(payer_this.group(0))
        print(pay_amount.group(0))
    else:
        break

# print('Getting venmo')
for message in venmo_messages:
    msg = serv.users().messages().get(userId='me', id=message['id']).execute()
    if unixtime <= float(msg.get('internalDate')) / 1000:
        try:
            payer_this = re.compile('(.+?)(?= completed your )').search(
                msg.get('payload').get('headers')[16].get('value'))
            pay_amount = re.compile('(?<=\$)(([1-9]\d*)?\d)(\.\d\d)').search(
                msg.get('payload').get('headers')[16].get('value'))
            pay_amount = pay_amount.group(0)
            payer_name = payer_this.group(0)
        except AttributeError:
            try:
                payer_this = re.compile('(.+?)(?= paid you )').search(
                    msg.get('payload').get('headers')[16].get('value'))
                pay_amount = re.compile('(?<=\$)(([1-9]\d*)?\d)(\.\d\d)').search(
                    msg.get('payload').get('headers')[16].get('value'))
                pay_amount = pay_amount.group(0)
                payer_name = payer_this.group(0)
            except AttributeError:
                try:
                    payer_this = re.compile('(?<=Fwd: )(.+?)(?= completed your )').search(
                        msg.get('payload').get('headers')[30].get('value'))
                    pay_amount = re.compile('(?<=\$)(([1-9]\d*)?\d)(\.\d\d)').search(
                        msg.get('payload').get('headers')[30].get('value'))
                    pay_amount = pay_amount.group(0)
                    payer_name = payer_this.group(0)
                except AttributeError:
                    try:
                        payer_this = re.compile('(?<=Fwd: )(.+?)(?= paid you )').search(
                            msg.get('payload').get('headers')[30].get('value'))
                        pay_amount = re.compile('(?<=\$)(([1-9]\d*)?\d)(\.\d\d)').search(
                            msg.get('payload').get('headers')[30].get('value'))
                        pay_amount = pay_amount.group(0)
                        payer_name = payer_this.group(0)
                    except:
                        payer_name = 'Could Not Parse'
        payer.append(payer_name)
        amount.append(pay_amount)
        print(payer_name)
        print(pay_amount)
    else:
        break
print(payer)
print(amount)
payer_df = pd.DataFrame(payer, columns=['Payer'])
payer_df['Amount'] = amount
print(payer_df)
SALES_ID = '1tIFKnnx26bIDO0SGnsMADLBIlx35jFObH_gJP_J8JiY'
wks_name = 'Paid Name and Amount'
dg2.upload(payer_df, SALES_ID, wks_name)
