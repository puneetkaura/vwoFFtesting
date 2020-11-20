#!/usr/bin/python
# coding: utf-8
import os

from flask import Flask, render_template
from dotenv import load_dotenv

import vwo

load_dotenv()
settings_file = vwo.get_settings_file('518132',os.environ.get('SDK_KEY'))

vwo_client_instance = vwo.vwo.VWO(settings_file=settings_file, user_storage=None, is_development_mode=True,should_track_returning_user=True,goal_type_to_track=vwo.GOAL_TYPES.ALL)

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
    variation_name = vwo_client_instance.activate("ab_test_demo", user_id)

    # get_variation_name API
    variation_name = vwo_client_instance.get_variation_name("ab_test_demo", user_id)
    dict = {
        'user_id': user_id,
        'variation_name': variation_name.upper()
    }
    return render_template('vwo_abtest.html', dict=dict)

@app.route('/vwo/ff/<user_id>/')
def vwo_ff(user_id):
    return render_template('vwo_ff.html')

@app.route('/vwo/rollout/')
def vwo_rollout():
    settings_file = vwo.get_settings_file('518132', os.environ.get('SDK_KEY'))

    vwo_client_instance = vwo.vwo.VWO(settings_file=settings_file, user_storage=None, is_development_mode=False ,
                                      should_track_returning_user=True, goal_type_to_track=vwo.GOAL_TYPES.ALL)

    fed = {}


    for i in range(1,101):
        is_feature_enabled = vwo_client_instance.is_feature_enabled('vwo_demo_blue_button_campaign_key', str(i), )
        print(is_feature_enabled, i)
        fed[str(i)] = is_feature_enabled
        # enabled = vwo_client_instance.get_feature_variable_value('vwo_demo_blue_button_campaign_key', 'enabled', 1)


    print(fed)
    return render_template('feature_rollout.html', fed=fed)

@app.route('/conversion/success/<user_id>/')
# @app.route('/conversion/success/')

def conversion_success(user_id):
    vwo_client_instance.track("ab_test_demo", user_id, "test_goal")
    return render_template('conversion.html', dict = {'user_id':user_id})

if __name__ == '__main__':
    app.run(debug=True)
