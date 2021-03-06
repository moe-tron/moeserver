from requests_oauthlib import OAuth1Session
import requests
import urllib
import os

def register():
    CONS_KEY = os.environ.get("TW_MOE_KEY")
    CONS_SECRET = os.environ.get("TW_MOE_SECRET")
    ACCESS_TOKEN = os.environ.get("TW_TOKEN")
    ACCESS_SECRET = os.environ.get("TW_TOKEN_SECRET")
    ENVNAME = os.environ.get('ENVIRON_NAME')
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

    auth = OAuth1Session(client_key=CONS_KEY,
                            client_secret=CONS_SECRET,
                            resource_owner_key=ACCESS_TOKEN,
                            resource_owner_secret=ACCESS_SECRET,
                            signature_method='HMAC-SHA1')

    # First we have to register our webhook, then we subscribe.
    register_url = 'https://api.twitter.com/1.1/account_activity/all/{}/webhooks.json?url={}'.format(ENVNAME, urllib.parse.quote_plus(WEBHOOK_URL))
    headers = requests.utils.default_headers()
    reg_response = auth.post(register_url,headers=headers)
    sub_url = 'https://api.twitter.com/1.1/account_activity/all/{}/subscriptions.json'.format(ENVNAME)
    sub_response = auth.post(sub_url,headers=headers)

if __name__ == "__main__":
    register()