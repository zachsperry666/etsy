import urllib
import webbrowser

from etsy2 import Etsy
from etsy2.oauth import EtsyOAuthHelper, EtsyOAuthClient
import urllib.parse as urlparse
from urllib.parse import parse_qs
import json


def get_oauth():
    api_key = '1umpcgbvnatx94degvtisq14'
    shared_secret = 'zoyxtjlizf'

    # define permission scopes
    permission_scopes = ['listings_r', 'transactions_r']
    callback_uri = 'https://www.etsy.com'

    login_url, temp_oauth_token_secret = \
        EtsyOAuthHelper.get_request_url_and_token_secret(api_key, shared_secret, permission_scopes)

    query = urlparse.urlparse(login_url).query
    temp_oauth_token = parse_qs(query)['oauth_token'][0]

    print(login_url)
    webbrowser.open(login_url)
    # follow the url to acquire the verifier.

    oauth_token, oauth_token_secret = \
        EtsyOAuthHelper.get_oauth_token_via_verifier(api_key, shared_secret, temp_oauth_token, temp_oauth_token_secret,
                                                     input('Verifier: '))

    #auth_url = callback_uri
    #oauth_token, oauth_token_secret = \
    #    EtsyOAuthHelper.get_oauth_token_via_auth_url(api_key, shared_secret, temp_oauth_token_secret, auth_url)

    # print('token= ' + oauth_token)
    # print('secret= ' + oauth_token_secret)

    etsy_oauth = EtsyOAuthClient(client_key=api_key,
                                 client_secret=shared_secret,
                                 resource_owner_key=oauth_token,
                                 resource_owner_secret=oauth_token_secret)

    etsy = Etsy(etsy_oauth_client=etsy_oauth)

    return etsy


def use_oauth():
    api_key = '1umpcgbvnatx94degvtisq14'
    shared_secret = 'zoyxtjlizf'
    oauth_token = '7ff6163d93381cd8c59f0b40f1ee82'
    oauth_token_secret = '8e0a052ca6'
    etsy_oauth = EtsyOAuthClient(client_key=api_key,
                                 client_secret=shared_secret,
                                 resource_owner_key=oauth_token,
                                 resource_owner_secret=oauth_token_secret)

    etsy = Etsy(etsy_oauth_client=etsy_oauth)

    return etsy
