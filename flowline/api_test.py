from flask import Flask, jsonify
from flask_cors import CORS

import threading
import time
import datetime
import json

def get_command(dict, gpu_id):
    return f"CUDA_VISIBLE_DEVICES={gpu_id} python test.py " + " ".join([f"--{key} {value}" for key, value in dict.items()])

def prepare():
    # Comment out the import that's causing problems
    # from .program import ProgramManager
    pass
    
prepare()

app = Flask(__name__)
CORS(app)

def get_app(get_command):
    return app

@app.route('/api/gpus', methods=['GET'])
def get_gpus():
    return jsonify([
        {
            'gpu_id': '0',
            'name': '模拟GPU',
            'status': 'available',
            'memory': {'free': 1, 'used': 11, 'total': 12},
            'utilization': 5,
            'temperature': 40,
            'power': {'current': 30, 'max': 250},
            'user_process_num': 1,
            'other_process_num': 2
        }
    ])

@app.route('/api/processes', methods=['GET'])
def get_processes():
    return jsonify([
        {
            'id': '0',
            'todoId': '0',
            'status': 'running',
            'pid': 12345,
            'gpu': '0',
            'user': 'user',
            'startTime': '2023-01-01 12:00:00',
            'runTime': '00:00:00',
            'command': 'python test.py'
        },
        {
            'id': '1',
            'todoId': '1',
            'status': 'running',
            'pid': 12346,
            'gpu': '0',
            'user': 'user',
            'startTime': '2023-01-01 12:00:00',
            'runTime': '00:00:00',
            'command': 'python test.py'
        },
    ])
