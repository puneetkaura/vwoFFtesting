#!/usr/bin/python
# coding: utf-8
import os

from flask import Flask, render_template
from dotenv import load_dotenv
import random
import time
import redis
import json

import vwo

from vwo import LOG_LEVELS


###########################################################################
import logging
import sys

import ldclient
from ldclient.config import Config

from ldclient.feature_store import CacheConfig
from ldclient.integrations import Redis

# Logging in launch darkly
root = logging.getLogger()
root.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

store = Redis.new_feature_store(url='redis://127.0.0.1:6379',
    prefix='ldd', caching=CacheConfig(expiration=30))

config = Config(
    sdk_key="sdk-9b3f0c68-9bd9-4ddf-9099-2525f8a67d15", 
    events_max_pending= 100,
    flush_interval= 60,
    feature_store=store,
)

ldclient.set_config(config)

# ldclient.set_config(Config("sdk-9b3f0c68-9bd9-4ddf-9099-2525f8a67d15"))
##########################################################################

# STORAGE SERVICE
class STORAGE_SERVICE():
  def __init__(self):
    self.redis_client = redis.Redis(
        host='127.0.0.1',
        port=6379,
        password=''
    )
  
  def get(self, user_id, campaign_key):
    print("GET FROM REDIS...")
    return self.redis_client.get(json.loads(hash((user_id, campaign_key))))
  
  def set(self, user_storage_data):
    print("SET TO REDIS...")
    self.redis_client.set(
        hash((user_storage_data['userId'], user_storage_data['campaignKey'])), 
        json.dumps(user_storage_data)
    )

load_dotenv()
# settings_file = vwo.get_settings_file('518132',os.environ.get('SDK_KEY'))

storage_service = STORAGE_SERVICE()

# vwo_client_instance = vwo.launch(settings_file=settings_file, storage_service=storage_service, 
# is_development_mode=True,
# should_track_returning_user=True,
# log_level= LOG_LEVELS.DEBUG, 
# goal_type_to_track=vwo.GOAL_TYPES.ALL)


def flush_callback(err, events):
    print(err)
    print(events)

settings_file = vwo.get_settings_file('518132', os.environ.get('SDK_KEY_ROLLOUT'))

vwo_client_instance = vwo.launch(
    # settings_file=settings_file, 
    # user_storage=storage_service,
    # is_development_mode=True,
    # should_track_returning_user=True,
    # log_level= LOG_LEVELS.DEBUG, 
    # goal_type_to_track=vwo.GOAL_TYPES.ALL,
    # batch_event_settings={
    #     'events_per_request': 100,
    #     'request_time_interval': 60,
    #     'flush_callback': flush_callback
    # }
    settings_file,
    # Enable UserStorage and add code in get and set method
    user_storage = storage_service,
    # Enable custom logger to check how it works
    # logger = CustomLogger()
    log_level = LOG_LEVELS.DEBUG,
    is_development_mode=False,
    should_track_returning_user=False,
    # uncomment batch_events to enable event batching
    batch_events={
        'events_per_request': 5,
        'request_time_interval': 60,
        'flush_callback': flush_callback
    }
)

app = Flask(  # Create a flask app
	__name__,
	template_folder='templates',  # Name of html file folder
	static_folder='static'  # Name of directory for static files
)

@app.route('/')
def entry_point():
    return render_template('home.html')

@app.route('/vwo/abtest/<user_id>/')
def vwo_abtest(user_id):
    # activate API
    variation_name = vwo_client_instance.activate("vwo_demo_blue_button_campaign_key_abtest", user_id)

    # get_variation_name API
    variation_name = vwo_client_instance.get_variation_name("vwo_demo_blue_button_campaign_key_abtest", user_id)
    dict = {
        'user_id': user_id,
        'variation_name': variation_name.upper() if variation_name else ""
    }
    return render_template('vwo_abtest.html', dict=dict)

@app.route('/vwo/ff/<user_id>/')
def vwo_ff(user_id):
    return render_template('vwo_ff.html')


##############################################
@app.route('/ld/feature_flag')
def ld_feature_flag():
  start_time = time.time()
  fed = {}

  for i in range(1,101):
    # these keys can also be used for filteration
    user = {
      "key": str(i * random.randint(1, 100000)* 19.1111),
    #   "key": str(i),
      "firstName": "Bob-" + str(i),
      "lastName": "Loblaw",
      "custom": {
        "groups": "beta_testers",
        "isNew": i&2
      }
    }
    is_feature_enabled = ldclient.get().variation("ld-blue-button", user, False)
    fed[str(i)] = is_feature_enabled
      
  print(fed)
  print("TOTAL TIME TAKEN", time.time() - start_time)
  return render_template('feature_rollout.html', fed=fed)


@app.route('/ld/feature_flag_json')
def ld_feature_flag_json():
  start_time = time.time()

  fed = {}

  for i in range(1,101):
    # these keys can also be used for filteration
    user = {
      "key": str(i * random.randint(1, 100000)* 19.1111),
      "firstName": "Bob-" + str(i),
      "lastName": "Loblaw",
      "custom": {
        "groups": "beta_testers",
        "isNew": i&2
      }
    }
    json_value = ldclient.get().variation("LD_JSON", user, {})
    fed[str(i)] = json_value.get('isEnabled')
      
  print(fed)
  print("TOTAL TIME TAKEN", time.time() - start_time)
  return render_template('feature_rollout.html', fed=fed)
############################################


@app.route('/vwo/flush/')
def flush():
    vwo_client_instance.flush_events(mode="async")
    return {"succees": 200}


@app.route('/vwo/rollout/')
def vwo_rollout():
#     settings_file = vwo.get_settings_file('518132', os.environ.get('SDK_KEY_ROLLOUT'))

#     vwo_client_instance = vwo.launch(settings_file=settings_file, 
#     storage_service=storage_service,is_development_mode=True,should_track_returning_user=True,
# log_level= LOG_LEVELS.DEBUG, 
# goal_type_to_track=vwo.GOAL_TYPES.ALL)
    start_time = time.time()
    fed = {}

    for i in range(1,101):
        user_id = str(i * random.randint(1, 100000)* 19.1111)
        # user_id = str(i)
        is_feature_enabled = vwo_client_instance.is_feature_enabled(
            'vwo_demo_blue_button_campaign_key', 
            user_id,
        )
        print(is_feature_enabled, i)

        val = vwo_client_instance.get_feature_variable_value('vwo_demo_blue_button_campaign_key', 'enabled', user_id)

        fed[str(i)] = is_feature_enabled and not val
        # enabled = vwo_client_instance.get_feature_variable_value('vwo_demo_blue_button_campaign_key', 'enabled', 1)


    print(fed)
    print("TOTAL TIME TAKEN", time.time() - start_time)
    return render_template('feature_rollout.html', fed=fed)

@app.route('/conversion/success/<user_id>/')
# @app.route('/conversion/success/')

def conversion_success(user_id):
    vwo_client_instance.track("ab_test_demo", user_id, "test_goal")
    return render_template('conversion.html', dict = {'user_id':user_id})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',  # Establishes the host, required for repl to detect the site
		port=7890)
