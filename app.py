import os
import requests
import pandas as pd
import json
import datetime
from slack_bolt import App
import config

def list_of_keys():
    '''
    1.The payload returned by slack when we use a 
    slash command is a dictionary.
    2. We only need certain items in that dictionary,
     so we're going to create a list which contains 
     only the keys of the items that we actually want
    '''
    key_list = ['text','user_name','channel_name']
    return key_list
def get_slash_data(slack_json):
    '''
    This will take a json as input and get only
     the relevant fields that you want to upload
     to the airtbale
    '''
    key_list = list_of_keys()
#     build a dictionary that only contains key and value pairs from
#      the list we defined in list_ok_keys
    filtered_dict = {k:v for k,v in slack_json.items() if k in key_list}
    return filtered_dict

def format_for_at_upload(slack_json):
    '''
    1.This will return a dictionary that's formatted
    specifically for an airtable upload.
    2. See the link below for airtable formatting requirements
    https://airtable.com/developers/web/api/create-records
    '''
    list_dict_for_at = {
    "records":[
        {
            "fields":get_slash_data(slack_json) #<----- change this when running actual app
            }
        ]
    }
    list_dict_for_at = json.dumps(list_dict_for_at)
    return list_dict_for_at

# ------------------------------------------
# airtable api data upload
# ------------------------------------------
def airt_api_headers():
    airt_headers = {
    'Authorization': f'Bearer {os.environ.get("AIRT_API_TOKEN")}',
    'Content-Type': 'application/json'
    }
    return airt_headers

def airt_api_url():
    '''
    This will construct the airtable url
     which will be called to add a record
    '''
    airtable_api_url = 'https://api.airtable.com/v0/'
    cust_fback_base_id = os.environ.get("CUST_FBACK_BASE_ID")
    slack_bot_product_requests_table_id = os.environ.get("SLACK_BOT_PRODUCT_REQUESTS_TABLE_ID")
    create_record_url = f'{airtable_api_url}{cust_fback_base_id}/{slack_bot_product_requests_table_id}'
    return create_record_url

def airt_api_post(slack_json):
    post_request = requests.request(
        "POST",
        airt_api_url(),
        headers=airt_api_headers(),
        data=format_for_at_upload(slack_json)
    )
    print(post_request.content)
    return post_request

# ------------------------------------------
# SLACK APP
# ------------------------------------------

# Initialize your app with your bot token and signing secret
app = App(
    # token=config.SLACK_BOT_TOKEN,
    # signing_secret=config.SLACK_SIGNING_SECRET,
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)

# Add functionality here later
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",

        # body of the view
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Welcome to your _App's Home tab isn't it great!_* :tada:"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
            }
          },
          {
            "type": "actions",
            "elements": [
              {
                "type": "button",
                "text": {
                  "type": "plain_text",
                  "text": "Click me!"
                }
              }
            ]
          }
        ]
      }
    )

  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

# This will match any message that contains hi
@app.message("hi")
def say_hello(message, say):
    user = message['user']
    say(f"Hi there, <@{user}>!")

# The echo command simply echoes on command
@app.command("/product_req")
def repeat_text(ack, respond, command, body):
    # Acknowledge command request
    ack()
    respond(f"{command['text']}")
#     Run a function that can save the text that was placed after the bot command
#     list_test.append(command['text'])
    airt_api_post(body)
    print("ok got it")
    print(body)

# Ready? Start your app!
if __name__ == "__main__":
#     app.start(port=int(os.environ.get("PORT", 3000)))
    app.start(port=int(os.environ.get("PORT", 80)))

# config tests