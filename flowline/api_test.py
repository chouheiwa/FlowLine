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
    return jsonify(
        {
            "0": {
                "all_process_num": 1, 
                "free_memory": 47159.6875, 
                "max_power": 450.0, 
                "name": "NVIDIA GeForce RTX 4090", 
                "power": 69.87, 
                "status": "disabled", 
                "temperature": 39, 
                "total_memory": 49140.0, 
                "user_process_num": 0, 
                "utilization": 0
            }, 
            "1": {
                "all_process_num": 0, 
                "free_memory": 48643.25, 
                "max_power": 450.0, 
                "name": "NVIDIA GeForce RTX 4090", 
                "power": 6.886, 
                "status": "disabled", 
                "temperature": 27, 
                "total_memory": 49140.0, 
                "user_process_num": 0, 
                "utilization": 0
            }, 
            "2": {
                "all_process_num": 1, 
                "free_memory": 44603.6875, 
                "max_power": 450.0, 
                "name": "NVIDIA GeForce RTX 4090", 
                "power": 255.892, 
                "status": "disabled", 
                "temperature": 58, 
                "total_memory": 49140.0, 
                "user_process_num": 0, 
                "utilization": 55
            },
        }
    )

@app.route('/api/process', methods=['GET'])
def get_processes():
    return jsonify(
        {
            "0": {
                "func": "func(({'data_name': 'rotate_mnist', 'model_name': 'cnn', 'method_name': 'GST', 'domain_num': 2, 'seed': 1}, 4), {})", 
                "gpu_id": 0, 
                "pid": 1738158, 
                "process_id": 0, 
                "status": "RUNNING", 
                "start_time": 1745037341.512741, 
                "task_id": 0
            }, 
            "1": {
                "func": "func(({'data_name': 'rotate_mnist', 'model_name': 'cnn', 'method_name': 'GST', 'domain_num': 2, 'seed': 2}, 4), {})", 
                "gpu_id": 1, 
                "pid": 1738246, 
                "process_id": 1, 
                "status": "RUNNING", 
                "start_time": 1745037346.512741, 
                "task_id": 1
            },
        }
    )

@app.route('/api/gpu/<gpu_id>/process', methods=['GET'])
def get_gpu_tasks(gpu_id):
    if gpu_id == "0":
        return jsonify(
            {
                "0": {
                    "func": "func(({'data_name': 'rotate_mnist', 'model_name': 'cnn', 'method_name': 'GST', 'domain_num': 2, 'seed': 1}, 4), {})", 
                    "gpu_id": 0, 
                    "pid": 1738158, 
                    "process_id": 0, 
                    "status": "RUNNING", 
                    "task_id": 0
                }
            }
        )
    elif gpu_id == "1":
        return jsonify(
            {
                "1": {
                    "func": "func(({'data_name': 'rotate_mnist', 'model_name': 'cnn', 'method_name': 'GST', 'domain_num': 2, 'seed': 2}, 4), {})", 
                    "gpu_id": 1, 
                    "pid": 1738246, 
                    "process_id": 1, 
                    "status": "RUNNING", 
                    "task_id": 1
                },
            }
        )
    elif gpu_id == "2":
        return jsonify({})
    else:
        return jsonify(
            {
                "error": "Invalid GPU ID"
            }
        )

"""
curl http://127.0.0.1:5000/api/process
curl http://127.0.0.1:5000/api/gpus
curl http://127.0.0.1:5000/api/gpu/0/process
"""