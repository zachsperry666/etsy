from send_gmail import open_service

serv = open_service()

# Call the Gmail API to fetch INBOX
results = serv.users().labels().list(userId='me').execute()
labels = results.get('labels', [])

if not labels:
    print('No labels found.')
else:
  print('Labels:')
  for label in labels:
    print(label['name']+ " "+label['id'])


results = serv.users().messages().list(userId='me', labelIds=['Label_3458690111019497815']).execute()
messages = results.get('messages', [])

for message in messages:
    msg = serv.users().messages().get(userId='me', id=message['id']).execute()
    print(msg['snippet'])
