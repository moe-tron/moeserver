from requests_oauthlib import OAuth1Session
import os

def register():
    CONS_KEY = os.environ.get("TW_MOE_KEY")
    CONS_SECRET = os.environ.get("TW_MOE_SECRET")
    ACCESS_TOKEN = os.environ.get("TW_TOKEN")
    ACCESS_SECRET = os.environ.get("TW_TOKEN_SECRET")
    ENVNAME = os.environ.get('ENVIRON_NAME')
    WEBHOOK_URL = os.environ.get('MOE_URL')

    auth = OAuth1Session(CONS_KEY,
                            client_secret=CONS_SECRET,
                            resource_owner_key=ACCESS_TOKEN,
                            resource_owner_secret=ACCESS_SECRET)

    # First we have to register our webhook, then we subscribe.
    try:
        register_url = 'https://api.twitter.com/1.1/account_activity/all/{}/webhooks.json?url={}'.format(ENVNAME, WEBHOOK_URL)
        reg_response = auth.post(register_url)
        print(reg_response)
        sub_url = 'https://api.twitter.com/1.1/account_activity/all/{}/subscriptions.json'.format(ENVNAME)
        sub_response = auth.post(sub_url)
        print(sub_response)
    except Exception as e:
        print("Something went wrong while registering your webhook/subscribing: ")
        print(e)

if __name__ == "__main__":
    register()