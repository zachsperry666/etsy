import smtplib, ssl
from bs4 import BeautifulSoup as Soup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time


def email_invoice(receiver_email, item_list):
    t = time.time()
    port = 465  # For SSL

    sender_email = "succielife@gmail.com"
    #receiver_email = "ckbrough4@gmail.com"
    password = "Zhongwen1"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Succielife Invoice"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = """\
    Hi,
    How are you?
    Real Python has many great tutorials:
    www.realpython.com"""

    html = """"\
    <html>
<body>

<p>Thank you for your purchase! Your invoice and instructions for payment are below.</p>

<p>If you have any questions, please contact us through 
<a href="https://www.instagram.com/succielife">Instagram (@succielife)</a>.</p>

<div>

</div>

<p>If you are paying via Venmo and already gave me your Venmo information, you should have already received a request from Anthony_Dodge. Please hit "Send" to complete. If you have not sent us your information yet, please contact us through <a href="https://www.instagram.com/succielife">Instagram (@succielife)</a>.</p>
 </p>
<p>If you are paying via Paypal, please generate a payment to mvhs_celloplayer@yahoo.com . You can start the process 
<a href="https://www.paypal.com/us/for-you/transfer-money/send-money">here</a>.</p>
<p>If you are paying with any other method (Zelle, etc.), please send us payment information through <a href="https://www.instagram.com/succielife">Instagram (@succielife)</a>. If you have already done so, you can expect a payment request shortly.</p>
</p>

</body>
</html>
    """

    insert="""\
<table style="width:50%">
  <tr>
    <th align="left">Item Name</th>
    <th align="left">Price</th>
  </tr>
  <tr>
    <td>Echevaria</td>
    <td>10</td>
  </tr>
  <tr>
    <td>Pachyvaria</td>
    <td>10</td>
  </tr>
  <tr>
    <td><i>Subtotal<i></td>
    <td><i>20<i></td>
  </tr>
  <tr>
    <td><u>Shipping<u></td>
    <td><u>5<u></td>
  </tr>
  </tr>
    <tr>
    <td><b>Total:<b></td>
    <td><b>25<b></td>
  </tr>
</table>
"""
    print('1: '+str(time.time()-t))
    soup = Soup(html,features="html.parser")
    soup.div.append(Soup('<div>'+'test'+'</div>',features="html.parser"))

    print(soup)

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    print('2: '+str(time.time() - t))
    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)
    print('3: '+str(time.time() - t))
    # Create a secure SSL context
    context = ssl.create_default_context()
    print('3.5: '+str(time.time() - t))

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        print('4: '+str(time.time() - t))
        server.login(sender_email, password)
        print('5: '+str(time.time() - t))
        server.sendmail(sender_email, receiver_email, message.as_string())
        print('6: '+str(time.time() - t))

email_invoice("ckbrough4@gmail.com",[])