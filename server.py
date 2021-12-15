import json
import numpy as np
from flask import Flask, request, jsonify
import pandas
import requests
from yolo_play import Model
import datetime
import csv
from final_project_classes import *

model = Model()
default_class = ['metal', 'paper', 'plastic', 'other']
adjusting = {0:'metal', 1:'plastic', 2:'paper', 3:'other'}

 # = {} # structure {1:{'volume':[[datatime, volume each class]], 'location':[lat, lon], 'data':[length 10 list for average]}}
reset_database = {}; new_key_db = {1:{0:'metal', 1:'other', 2:'plastic', 3:'paper'}}
local_data = []
t = 0; time_range = 9; threshold = 0.15 # time range is time_range+1
#------------------
lat, lon = 40.810033, -73.96201  # nwc
lat1, lon1 = 40.802948, -73.964268  # old home
database = {1: {'volume': [[get_datetime(), 0., 0., 0., 0.]], 'location': [lat1, lon1]}, 2: {'volume': [[get_datetime(), 0., 0., 0., 0.]], 'location': [lat, lon]}}
m = Map(database)
m.initialize_random()
m.update_map(new_key_db)

map_key = 'AIzaSyDVsu34HwY6IHeqaah5CLT_pMZbhgr9mQo'
#--------------------------------------------------
app = Flask(__name__)

@app.route('/picture', methods=['PUT'])
def predict_timerange():
    global t
    data = json.loads(request.data)
    picture = np.array(data, dtype='uint8')
    result = model.get_predict(picture)
    local_data.append(result)
    prediction = np.mean(local_data[np.max(t-time_range, 0):t+1], axis=0) # average confidence for each class
    final_result = []
    for i in range(prediction.shape[0]):
        if prediction[i] >= threshold:
            final_result.append([default_class[i], prediction[i]])
    if len(final_result) > 1:
        final_result = np.array(final_result); index = final_result[:, 1].astype('float32')
        final_result = final_result[index.argsort()].tolist()
    t += 1
    return jsonify({'results': final_result})

@app.route('/volume', methods=['PUT'])
def record_volume():
    volume_pac = json.loads(request.data) # time t, volume in each class
    for i in volume_pac.keys(): # only have one key, string i
        volume_with_time = volume_pac[i]['volume']
        database[int(i)]['volume'] += volume_with_time # database must use int index
    generate_pic(database)
    m.update_map(new_key_db)
    return jsonify('Get!')

@app.route('/location', methods=['PUT'])
def record_location():
    location = json.loads(request.data)
    for i in location.keys():
        location = location[i]['location']
        if int(i) in database.keys(): database[int(i)]['location'] = location
        else: database[int(i)] = {'volume': [], 'location':location}
    database[1]['location'] = [lat1, lon1]
    database[2]['location'] = [lat, lon]
    return jsonify('Get Location!')

@app.route('/reset', methods=['PUT'])
def reset():
    # compute dynamic adjusting; id is {'index':id}
    reset_index = json.loads(request.data)
    index = int(list(reset_index.keys())[0])
    volume_last = database[index]['volume'][-1][1:]
    if not index in reset_database.keys(): reset_database[index] = [volume_last]
    else: reset_database[index].append(volume_last)
    new_key = np.argsort(np.mean(reset_database[index], axis=0))
    for i in range(4):
        adjusting[i] = default_class[new_key[i]]
    new_key_db[index] = adjusting
    database[index]['volume'].append([get_datetime(), 0, 0, 0, 0]) # clear all trash to reset
    # print(new_key_db)
    m.update_map(new_key_db)
    return jsonify(adjusting)

@app.route('/picture', methods=['DELETE'])
def remove():
    for key in database.keys():
        w = csv.writer(open('output.csv'+str(key), 'w'))
        for time, volume in database[key]:
            w.writerow([time, volume])
    database[key]['volume']=[datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), 0, 0, 0, 0]
    return jsonify({'Return':'Sucess Save and show new plot'})

app.run(host='0.0.0.0', port=5000)