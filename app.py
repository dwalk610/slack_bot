import os
import requests
import pandas as pd
import json
import datetime
from slack_bolt import App
import config

# ------------------------------------------------
# Set keys and tokens to env variables here
# ------------------------------------------------

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
########################################
# airtable api data upload
########################################
def airt_api_headers():
    airt_headers = {
    'Authorization': f'Bearer {airt_api_token}',
    'Content-Type': 'application/json'
    }
    return airt_headers
def airt_api_url():
    '''
    This will construct the airtable url
     which will be called to add a record
    '''
    airtable_api_url = 'https://api.airtable.com/v0/'
    cust_fback_base_id = 'appPuvZYmQ84PioWi'
    slack_bot_product_requests_table_id = 'tbl1L8UicdmyfrjHe'
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

# test
print(config.SLACK_BOT_TOKEN)