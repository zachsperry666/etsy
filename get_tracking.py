from etsy_py.api import EtsyAPI
import requests
from requests_oauthlib import OAuth1

key = '1umpcgbvnatx94degvtisq14'
key_post = '?api_key=' + key

api = EtsyAPI(api_key=key)

print(api)

r = api.get('receipts/1643009665'+key_post)

print(r)

data = r.json()

print(data)
