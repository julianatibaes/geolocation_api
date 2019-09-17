#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 2019

@author: Juliana Tibães
"""

from flask import Flask,render_template, jsonify, request
from flask_googlemaps import GoogleMaps, Map, icons
from flask_material import Material

import threading
import time
import requests
import json

import googlemaps
from datetime import datetime

app = Flask(__name__)
Material(app)
GoogleMaps(app, key='KEY_MAPS') 
gmaps = googlemaps.Client(key='KEY_MAPS')

path_data = 'dataset/data.json'
# FONT: https://libraries.io/github/Jandersoft/Flask-GoogleMaps
# FONT: https://github.com/rochacbruno-archive/Flask-GoogleMaps/blob/master/examples/jsonify_examples.py
# FONT: https://googlemaps.github.io/google-maps-services-python/docs/
POOL_TIME = 3600 

def get_location():
    with open(path_data) as json_file:
        data = json.load(json_file)
        locations = [ [p['lat'], p['lng'], p['name'] ] for p in data['results'] ]   
    return locations

LOCATIONS = get_location()   

#test server
@app.route('/')
def index():
	return 'Flask server conected.'

#show map with your data dots
@app.route('/maps')
def map_api():
    locations = LOCATIONS
    
	#maptype: The map type - ROADMAP, SATELLITE, HYBRID, TERRAIN. Defaults to ROADMAP.
    snd_map = Map(
        identifier="view-side",
        lat=locations[0][0],
        lng=locations[0][1],
        zoom='4',
        style='height:500px;width:800px;margin:0;',
        language='pt',
        maptype='styled_map',
        markers=[(loc[0], loc[1], loc[2],icons.dots.yellow ) for loc in locations],
        fit_markers_to_bounds = True
    )
    return render_template('index.html', sndmap = snd_map)

#update data
def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            print('In start loop')
            try:
                r = requests.get('http://127.0.0.1:5000/')
                if r.status_code == 200:
                    print('Server started, quiting start_loop')
                    LOCATIONS = get_location()
                    print(LOCATIONS)
                    not_started = False
                print(r.status_code)
            except:
                print('Server not yet started')
            time.sleep(POOL_TIME)
            not_started = True
    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()
  
#route - WIP  
@app.route('/direction/<location>', methods=['GET', 'POST'])
def get_direction(location):
    
    locations = LOCATIONS
    
    origin = (locations[0][0], locations[0][1])
    destination = (locations[1][0], locations[1][1])
    
    now = datetime.now()
    
    layer = gmaps.directions(origin, destination,mode='driving', departure_time = now)
    
    return jsonify(route = layer)

#save lat and lng
@app.route('/location', methods=['POST'])
def save_location():
    data = request.get_json()
    lat= data['lat']
    lng= data['lng']
    name= data['name']

    with open(path_data, 'w') as outfile:
        json.dump(data, outfile)
    
    return jsonify({'result': 'Localização salva com sucesso!', 'lat': lat, 'lng': lng, 'name': name})

if __name__ == '__main__':
    #start_runner() 
    app.run(debug=True)
