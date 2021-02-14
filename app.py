import base64
import hashlib
import hmac
import json
import os
from flask import Flask, request, send_from_directory, make_response
from enum import Enum
import re
from azure.storage.queue import (
    QueueService,
    QueueMessageFormat)
from register_hook import register


class EventType(str, Enum):
  DIRECT = "dm"
  TWEET = "tweet"
  NONE = ""


class Event:
  msg_type = EventType.NONE  # Can be a tweet or a DM
  respond_id = ""  # Id of the tweet to respond to or id of DM
  text = ""  # Text content of tweet or DM
  user_id = ""  # Id of the user who triggered the tweet or DM

  def __init__(self, msg_type, respond_id, text, user_id):
    self.msg_type = msg_type
    self.respond_id = respond_id
    self.text = text
    self.user_id = user_id


# Data read in from env vars..
CONS_SECRET = os.environ.get("TW_MOE_SECRET")
ENVNAME = os.environ.get('ENVIRON_NAME')
WEBHOOK_URL = os.environ.get('MOE_URL')
MOEQUE_CONN_STRING = os.environ.get('MOEQUE_CONN_STRING')
MOE_ID = os.environ.get('MOE_ID')
queue_name = os.environ.get('QUEUE_NAME')

# Set up queue w/ Azure
queue_service = QueueService(connection_string=MOEQUE_CONN_STRING)
queue_service.create_queue(queue_name)

# Supported commands, will probably add more here later.
commands = ['moerand', 'moename', 'moemess']
match_commands = re.compile(r'(?:{})'.format(
    '|'.join(map(re.escape, commands))), re.IGNORECASE)

app = Flask(__name__)
# Super simple flask API that handles events from the account activity API and places them on an azure queue.
# Events are parsed and those that I actually want my bot to respond to are parsed and placed on the queue.

@app.errorhandler(404)
def not_found(e):
    print("404")
    return "Wow, there's nothing here.."


@app.route("/")
def hello():
    return "lol."

# CRC Check
@app.route('/webhook', methods=['GET'])
def webhook_challenge():
  try:
    print("Handling CRC...")
    signature = hmac.new(bytes(CONS_SECRET, 'UTF-8'), bytes(
        request.args.get('crc_token'), 'UTF-8'), digestmod=hashlib.sha256).digest()
    encoded_sig = base64.b64encode(signature)
    response = {
        'response_token': 'sha256=' + encoded_sig.decode('UTF-8')
    }
    return json.dumps(response)
  except Exception as e:
    print("Something went wrong with CRC")
    print(e)
    response = {
        'statusCode': 500,
        'body': "Error with CRC"
    }
    return response

# Webhook, handles incoming events and puts events that we want onto the queue.
@app.route("/webhook", methods=["POST"])
def receive_event():
  twitter_events = request.get_json()
  try:
    if 'tweet_create_events' in twitter_events:  # Handle tweet create event
      events = twitter_events['tweet_create_events']
      for tweet_ev in events:
        if match_commands.search(tweet_ev['text']):
          if tweet_ev['in_reply_to_user_id_str'] == MOE_ID or any(mention['id_str'] == MOE_ID for mention in tweet_ev['entities']['user_mentions']):
            resp_event = Event(
                EventType.TWEET, tweet_ev['id'], tweet_ev['text'], tweet_ev['user']['id'])
            queue_service.put_message(
                queue_name, json.dumps(resp_event.__dict__))
    elif 'direct_message_events' in twitter_events:  # Handle direct messages
      direct_messages = twitter_events['direct_message_events']
      for dm in direct_messages:
        if match_commands.search(dm['message_create']['message_data']['text']) and dm['message_create']['sender_id'] != MOE_ID:
          resp_event = Event(EventType.DIRECT, dm['id'], dm['message_create']
                             ['message_data']['text'], dm['message_create']['sender_id'])
          queue_service.put_message(
              queue_name, json.dumps(resp_event.__dict__))
  except Exception as e:
    print(e)
    error_response = {
        'statusCode': 500,
        'body': "Error with handling message"
    }
    return error_response
  response = {
      'statusCode': 200,
      'body': "Event(s) processed"
  }
  return response


if __name__ == "__main__":
  register()
  app.run(debug=True)
