from flask import Flask, jsonify, request
from flask_cors import CORS

import threading
import time
import datetime
import json

try:
    from .program import ProgramManager
    from .log import Log
    logger = Log(__name__)
    HAS_DEPENDENCIES = True
except Exception as e:
    print(f"Warning: Error importing dependencies: {e}")
    HAS_DEPENDENCIES = False
    
    # 简单的日志替代
    class SimpleLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def debug(self, msg): pass
    
    logger = SimpleLogger()

app = Flask(__name__)

CORS(app)

program_manager = None

def get_app(get_command):
    global program_manager
    try:
        if HAS_DEPENDENCIES:
            program_manager = ProgramManager(get_command)
            logger.info("ProgramManager initialized successfully")
        else:
            logger.warning("Running in mock mode - dependencies not available")
    except Exception as e:
        logger.error(f"Failed to initialize ProgramManager: {e}")
    
    return app

# 模拟数据，当 program_manager 不可用时使用
def get_mock_gpu_data():
    return [
        {
            'gpu_id': '0',
            'name': '模拟 GPU 0',
            'status': 'available',
            'memory': {
                'free': 8000,
                'used': 2000,
                'total': 10000
            },
            'utilization': 15,
            'temperature': 45,
            'power': {
                'current': 50,
                'max': 250
            },
            'user_process_num': 0,
            'other_process_num': 1
        },
        {
            'gpu_id': '1',
            'name': '模拟 GPU 1',
            'status': 'busy',
            'memory': {
                'free': 2000,
                'used': 8000,
                'total': 10000
            },
            'utilization': 85,
            'temperature': 75,
            'power': {
                'current': 200,
                'max': 250
            },
            'user_process_num': 2,
            'other_process_num': 0
        }
    ]

# GPU数据转换为前端格式
def gpu_to_frontend_format(info, index, usable):
    # 确定状态
    if not usable:
        status = 'disabled'
    elif info.utilization > 50:
        status = 'busy'
    else:
        status = 'available'
    
    # 构建前端格式数据
    memory_used = info.memory - info.free_memory
    dict =  {
        'gpu_id': f'{index}',
        'name': f'{info.name}',
        'status': status,
        'memory': {
            'free': round(info.free_memory),
            'used': round(info.memory - info.free_memory),
            'total': round(info.memory)
        },
        'utilization': round(info.utilization),
        'temperature': info.temperature,
        'power': {
            'current': info.power,
            'max': info.max_power
        },
        'user_process_num': info.user_process_num,
        'other_process_num': info.all_process_num - info.user_process_num
    }
    return dict

# 进程数据转换为前端格式
def process_to_frontend_format(process):
    # 计算运行时间
    if process.start_time:
        run_time = datetime.datetime.now() - process.start_time
        hours, remainder = divmod(run_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        run_time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
        run_time = "-"
    
    # 格式化开始时间
    start_time_str = process.start_time.strftime("%Y-%m-%d %H:%M:%S") if process.start_time else ""
    
    dict = {
        'id': f'{process.id}',
        'todoId': f'{process.todo_id}',
        'status': process.status,
        'pid': process.pid,
        'gpu': f'{process.gpu_id}',
        'user': 'user',
        'startTime': start_time_str,
        'runTime': run_time_str,
        'command': process.cmd
    }
    return dict

@app.route('/api/gpus', methods=['GET'])
def get_gpus():
    try:
        if program_manager is None or not HAS_DEPENDENCIES:
            logger.warning("Using mock GPU data - ProgramManager not available")
            return jsonify(get_mock_gpu_data())
        
        program_manager.gpu_manager.flash_all_gpu()
        gpus = []
        
        for i, gpu in enumerate(program_manager.gpu_manager.all_gpu):
            usable = program_manager.gpu_manager.usable_mark[i]
            gpus.append(gpu_to_frontend_format(gpu.info, i, usable))
        
        return jsonify(gpus)
    except Exception as e:
        logger.error(f"Error getting GPUs: {e}")
        return jsonify(get_mock_gpu_data())  # 出错时返回模拟数据

@app.route('/api/processes', methods=['GET'])
def get_processes():
    try:
        if program_manager is None or not HAS_DEPENDENCIES:
            logger.warning("Using mock process data - ProgramManager not available")
            return jsonify([])  # 返回空数组，表示没有进程
        
        processes = []
        for process in program_manager.process_manager.processes:
            processes.append(process_to_frontend_format(process))
        
        return jsonify(processes)
    except Exception as e:
        logger.error(f"Error getting processes: {e}")
        return jsonify([])  # 出错时返回空数组

@app.route('/api/gpu/<gpu_id>/tasks', methods=['GET'])
def get_gpu_tasks(gpu_id):
    try:
        if program_manager is None or not HAS_DEPENDENCIES:
            logger.warning(f"Using mock task data for GPU {gpu_id} - ProgramManager not available")
            return jsonify([])
        
        gpu_index = int(gpu_id.split('-')[1])
        tasks = []
        
        for process in program_manager.process_manager.processes:
            if process.gpu_id == gpu_index:
                tasks.append(process_to_frontend_format(process))
        
        return jsonify(tasks)
    except Exception as e:
        logger.error(f"Error getting GPU tasks: {e}")
        return jsonify([])

@app.route('/api/task/<task_id>/kill', methods=['POST'])
def kill_task(task_id):
    try:
        if program_manager is None or not HAS_DEPENDENCIES:
            logger.warning(f"Cannot kill task {task_id} - ProgramManager not available")
            return jsonify({'success': False, 'error': 'Service not fully initialized'})
        
        process_id = int(task_id.split('-')[1])
        success = program_manager.kill_process(process_id)
        
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error killing task: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gpu/<gpu_id>/switch', methods=['POST'])
def switch_gpu(gpu_id):
    try:
        if program_manager is None or not HAS_DEPENDENCIES:
            logger.warning(f"Cannot switch GPU {gpu_id} - ProgramManager not available")
            return jsonify({'gpu_id': gpu_id, 'is_on': False, 'error': 'Service not fully initialized'})
        
        gpu_index = int(gpu_id.split('-')[1])
        is_on = program_manager.switch_gpu(gpu_index)
        
        return jsonify({'gpu_id': gpu_id, 'is_on': is_on})
    except Exception as e:
        logger.error(f"Error switching GPU: {e}")
        return jsonify({'gpu_id': gpu_id, 'is_on': False, 'error': str(e)})

@app.route('/api/control/start', methods=['POST'])
def start_process_loop():
    try:
        if program_manager is None or not HAS_DEPENDENCIES:
            logger.warning("Cannot start process loop - ProgramManager not available")
            return jsonify({'status': 'error', 'error': 'Service not fully initialized'})
        
        program_manager.start_process_loop()
        return jsonify({'status': 'started'})
    except Exception as e:
        logger.error(f"Error starting process loop: {e}")
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/api/control/stop', methods=['POST'])
def stop_process_loop():
    try:
        if program_manager is None or not HAS_DEPENDENCIES:
            logger.warning("Cannot stop process loop - ProgramManager not available")
            return jsonify({'status': 'error', 'error': 'Service not fully initialized'})
        
        program_manager.stop_process_loop()
        return jsonify({'status': 'stopped'})
    except Exception as e:
        logger.error(f"Error stopping process loop: {e}")
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/api/control/status', methods=['GET'])
def get_status():
    try:
        if program_manager is None or not HAS_DEPENDENCIES:
            logger.warning("Cannot get status - ProgramManager not available")
            return jsonify({
                'running': False,
                'max_processes': 0,
                'message': 'Service not fully initialized'
            })
        
        return jsonify({
            'running': program_manager.if_run,
            'max_processes': program_manager.process_manager.get_max_processes()
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'running': False,
            'max_processes': 0,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 