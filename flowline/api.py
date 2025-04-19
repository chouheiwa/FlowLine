import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit

from .program import ProgramManager
from .log import Log


logger = Log(__name__)
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

program_manager = None

def get_app(func):
    try:
        global program_manager
        program_manager = ProgramManager(func, todo_dir="todo.xlsx")
        logger.info("ProgramManager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ProgramManager: {e}")
        raise e
    return app

@app.route('/api/gpus', methods=['GET'])
def get_gpus():
    try:
        gpus_dict = program_manager.get_gpu_dict()
        return jsonify(gpus_dict)
    except Exception as e:
        logger.error(f"Error getting GPUs: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/process', methods=['GET'])
def get_processes():
    try:
        process_dict = program_manager.get_process_dict()
        return jsonify(process_dict)
    except Exception as e:
        logger.error(f"Error getting processes: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/gpu/<gpu_id>/process', methods=['GET'])
def get_gpu_tasks(gpu_id):
    try:
        gpu_id = int(gpu_id)
        process_dict = program_manager.get_process_dict_by_gpu(gpu_id)
        return jsonify(process_dict)
    except Exception as e:
        logger.error(f"Error getting GPU tasks: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/gpu/<gpu_id>/switch', methods=['POST'])
def switch_gpu(gpu_id):
    try:
        gpu_id = int(gpu_id)
        if_success, is_on = program_manager.switch_gpu(gpu_id)
        return jsonify({'gpu_id': gpu_id, 'success': if_success, 'is_on': is_on})
    except Exception as e:
        logger.error(f"Error switching GPU: {e}")
        return jsonify({'gpu_id': gpu_id, 'success': False, 'error': str(e)})

@app.route('/api/run', methods=['POST'])
def run_process_loop():
    try:
        if_run = program_manager.switch_run()
        return jsonify({'if_run': if_run})
    except Exception as e:
        logger.error(f"Error starting process loop: {e}")
        return jsonify({'if_run': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
    
    
"""
curl -X POST http://127.0.0.1:5000/api/gpu/7/switch
curl -X POST http://127.0.0.1:5000/api/run

curl http://127.0.0.1:5000/api/process
curl http://127.0.0.1:5000/api/gpus
"""