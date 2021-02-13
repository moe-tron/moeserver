# Twitter Account Activity Webhook Handler w/ Azure Queue Connection

It's just a super simple flask app that shoves the incoming data onto an azure queue. You can then have a separate application that reads off of the queue and handles it.

Also includes register_hook to register the hook and subscribe.

**Some setup and usage information**

Obviosuly you need Python. Pretty sure anything Python 3.6 or newer will work but don't quote me on that.

Install pre-reqs with `pip install -r requirements.txt`

Set up ENV vars as needed.

Run using `python server.py` to start up the app that handles the webhook.

Run register_hook.py to register your webhook and subscribe.

Make sure wherever you're hosting this is fast enough to handle the CRC challenge, you need to be able to respond within 3 seconds I believe.

You won't be able to actually get events when running this locally, but you can at least test the queue connection.

**Questions**

Q) Why don't you just do the handling /replying here?
A) In my scenario the workload that my bot does requires a fairly powerful GPU, so I'd have to pay an exorbiant amount of money to host it as hosting options w/ a GPU are ridiculously expensive. It was much cheaper for me to set up an old PC with a decent GPU to handle the workload. I could have used ngrok or something but I wanted Azure experience so here we are.

Q) Can I reuse this code for my own usage?
A) See LICENSE, it's the MIT license which pretty much lets you do what you want.

