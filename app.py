import base64
import hashlib
import hmac
import json
import os
from flask import Flask, request, send_from_directory, make_response
from azure.storage.queue import (
        QueueService,
        QueueMessageFormat)
from register_hook import register


# Data read in from env vars..
CONS_KEY = os.environ.get("TW_MOE_KEY")
CONS_SECRET = os.environ.get("TW_MOE_SECRET")
ACCESS_TOKEN = os.environ.get("TW_TOKEN")
ACCESS_SECRET = os.environ.get("TW_TOKEN_SECRET")
ENVNAME = os.environ.get('ENVIRON_NAME')
WEBHOOK_URL = os.environ.get('MOE_URL')
MOEQUE_CONN_STRING = os.environ.get('MOEQUE_CONN_STRING')
queue_name = os.environ.get('QUEUE_NAME')

# Set up queue w/ Azure
queue_service = QueueService(connection_string=MOEQUE_CONN_STRING)
queue_service.create_queue(queue_name)
app = Flask(__name__)

# Super simple flask API that handles events from the account activity API and places them on an azure queue.

@app.errorhandler(404)
def not_found(e):
    print("404")
    return 'Route not found...'

@app.route("/")
def hello():
    return "Wow, there's nothing here.."

# CRC Challenge
@app.route('/webhook', methods=['GET'])
def webhook_challenge():
  try:
    print("Handling CRC...")
    signature = hmac.new(bytes(CONS_SECRET, 'UTF-8'), bytes(request.args.get('crc_token'), 'UTF-8'), digestmod=hashlib.sha256).digest()
    encoded_sig = base64.b64encode(signature)
    response = {
      'response_token': 'sha256=' + encoded_sig.decode('UTF-8')
    }
    return json.dumps(response)
  except Exception as e:
    print("something went wrong")
    print(e)
    response = {
        'statusCode': 500,
              'body': "Error with CRC Challenge"
          }
    return response

# Webhook handle currently just shoves the messages onto a queue so they can be read by another server
# Later we can probably parse them some here when we know what they will look like, so we don't clog up the queue so much.
@app.route("/webhook", methods=["POST"])
def receive_event():
  request_json = request.get_json()
  queue_service.put_message(queue_name, json.dumps(request_json))
  return "Success"

if __name__ == "__main__":
    app.run(debug=True)
