import paypalrestsdk
from paypalrestsdk import Invoice


def paypal_req(username_req,price,item,quan):
    paypalrestsdk.configure({
        "mode": "sandbox",  # sandbox or live
        "client_id": "AYJoKXgjg4neuijItOyNwMILduzvH-_HYOm3unj7lFni750f1dZ7mdMyBgxfJbX-sdi4NIFYgpj8ORRm",
        "client_secret": "EAHwImaU338nruy1MpvOiL0AyVVF2QNnOEMTiGlcymGgX9jlQggn59q9VcfYwg0labdrcnlZDs9JNFqi"})

    invoice = Invoice({
    'merchant_info': {
        "email": "sb-f47rw61735379@business.example.com",
    },
    "billing_info": [{
        "email": username_req
    }],
    "items": [{
        "name": item,
        "quantity": quan,
        "unit_price": {
            "currency": "USD",
            "value": price
        }
        }],
    })

    response = invoice.create()
    print(response)

    if invoice.send():  # return True or False
        print("Invoice[%s] send successfully" % (invoice.id))
    else:
        print(invoice.error)



