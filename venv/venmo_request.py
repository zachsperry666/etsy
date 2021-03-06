from venmo_api import Client

# Get your access token. You will need to complete the 2FA process
# try:
def venmo_auth():
    access_token = Client.get_access_token(username='Anthony-Dodge',
                                       password='Cello13!',
                                       device_id='31638645-37M7-9D77-50Y8-6JE79O164ND8')

    venmo = Client(access_token=access_token)

    return venmo

def venmo_req(venmo,username_req,price,item):

# Search for users. You get 50 results per page.
    users = venmo.user.search_for_users(query=username_req,
                                    page=1)
    user_this = users[users==username_req]

    venmo.payment.request_money(price, item , user_this.id)


# # Or, you can pass a callback to make it multi-threaded
# def callback(users):
#    for user in users:
#        print(user.username)
# venmo.user.search_for_users(query="peter",
#                             callback=callback,
#                             page=2,
#                             count=10)