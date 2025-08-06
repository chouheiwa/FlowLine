import datetime
import os
import re
import platform
import psutil

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit

from flowline.core import ProgramManager
from flowline.utils import Log


logger = Log(__name__)
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
start_time = datetime.datetime.now()

program_manager = None

def get_app(func, task_db_path="tasks.db"):
    try:
        global program_manager
        program_manager = ProgramManager(func, task_db_path)
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
    
@app.route('/api/process/<process_id>/kill', methods=['POST'])
def kill_process(process_id):
    try:
        if_success = program_manager.kill_process(int(process_id))
        return jsonify({'success': if_success})
    except Exception as e:
        logger.error(f"Error killing process: {e}")

@app.route('/api/gpu/<gpu_id>/process', methods=['GET'])
def get_gpu_tasks(gpu_id):
    try:
        process_dict = program_manager.get_process_dict_by_gpu(int(gpu_id))
        return jsonify(process_dict)
    except Exception as e:
        logger.error(f"Error getting GPU tasks: {e}")
        return jsonify({'error': str(e)})

@app.route('/api/gpu/<gpu_id>/switch', methods=['POST'])
def switch_gpu(gpu_id):
    try:
        if_success, is_on = program_manager.switch_gpu(int(gpu_id))
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

@app.route('/api/task/list', methods=['GET'])
def get_task_list():
    try:
        task_dict = program_manager.get_task_dict()
        return jsonify(task_dict)
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return jsonify({'error': str(e)})
    
@app.route('/api/task/create', methods=['POST'])
def create_task():
    try:
        data = request.json
        name = data.get('name', 'Unnamed Task')
        cmd = data.get('cmd', '')
        need_run_num = data.get('need_run_num', 1)
        config_dict = data.get('config_dict', {})
        
        if not cmd:
            return jsonify({'success': False, 'error': 'Command is required'})
            
        if_success = program_manager.create_task(name, cmd, need_run_num, config_dict)
        return jsonify({'success': if_success})
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/log/list', methods=['GET'])
def log_file_list():
    try:
        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_path = os.path.dirname(current_path)
        log_dir = os.path.join(parent_path, 'log')

        if not os.path.exists(log_dir):
            return jsonify({'files': []})

        files = []
        for fname in os.listdir(log_dir):
            fpath = os.path.join(log_dir, fname)
            if os.path.isfile(fpath):
                stat = os.stat(fpath)
                size = stat.st_size
                if size > 1024 * 1024:
                    size_str = f"{size / (1024*1024):.1f}MB"
                elif size > 1024:
                    size_str = f"{size / 1024:.1f}KB"
                else:
                    size_str = f"{size}B"
                files.append({
                    'name': fname,
                    'fullPath': fpath,
                    'size': size_str,
                    'lastModified': 
                        __import__('datetime').datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        return jsonify({'files': files})
    except Exception as e:
        logger.error(f"Error getting log file list: {e}")
        return jsonify({'error': str(e)})
    
@app.route('/api/log/<log_file_name>', methods=['GET'])
def get_log_content(log_file_name):
    max_lines = request.args.get('maxLines', default=100, type=int)
    try:
        current_path = os.path.dirname(os.path.abspath(__file__))
        parent_path = os.path.dirname(current_path)
        log_dir = os.path.join(parent_path, 'log')
        log_file_path = os.path.join(log_dir, log_file_name)
        lines = log_lines(log_file_path, max_lines)
        return jsonify({'lines': lines})
    except Exception as e:
        logger.error(f"Error getting log content: {e}")
        return jsonify({'error': str(e)})
    
def log_lines(log_file_path, max_lines):
    """
    读取日志文件的最后 max_lines 行，并将每行解析为结构化的 dict:
    {
        "timestamp": "2025-07-30 14:15:58",
        "level": "INFO",
        "message": "Process 3 finished with return code -9"
    }
    """
    result = []
    if not os.path.exists(log_file_path):
        return result

    # 读取最后 max_lines 行
    lines = []
    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        try:
            # 先尝试用 seek 反向读取
            f.seek(0, os.SEEK_END)
            filesize = f.tell()
            blocksize = 4096
            data = ''
            pointer = filesize
            while pointer > 0 and len(lines) < max_lines:
                read_size = blocksize if pointer - blocksize > 0 else pointer
                pointer -= read_size
                f.seek(pointer)
                data = f.read(read_size) + data
                lines = data.splitlines()
            # 只取最后 max_lines 行
            lines = lines[-max_lines:]
        except Exception:
            # 回退到普通读取
            f.seek(0)
            all_lines = f.readlines()
            lines = all_lines[-max_lines:]

    # 日志行正则
    # 例: [2025-07-30 14:15:58,282] [INFO] - Process 3 finished with return code -9
    log_pattern = re.compile(
        r'^\[(?P<timestamp>[\d\-: ,]+)\]\s+\[(?P<level>[A-Z]+)\]\s*-\s*(?P<message>.*)$'
    )

    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = log_pattern.match(line)
        if m:
            # 去掉毫秒部分
            ts = m.group('timestamp').split(',')[0]
            result.append({
                'timestamp': ts,
                'level': m.group('level'),
                'message': m.group('message')
            })
        else:
            # 不是标准格式，原样返回
            result.append({
                'timestamp': '',
                'level': '',
                'message': line
            })
    return result

@app.route('/api/system/info', methods=['GET'])
def get_system_info():
     # 操作系统和内核版本
    os_info = f"{platform.system()} {platform.release()}"
    
    # CPU 核心数（逻辑核数）
    cpu_count = os.cpu_count()

    # 内存总量（单位：GB，保留两位小数）
    mem = psutil.virtual_memory()
    mem_total_gb = round(mem.total / (1024 ** 3), 2)

    return f"{os_info}, CPU: {cpu_count} cores, Memory: {mem_total_gb} GB"

@app.route('/api/system/uptime', methods=['GET'])
def get_uptime():
    uptime = datetime.datetime.now() - start_time
    return jsonify({'days': uptime.days, 'hours': uptime.seconds // 3600, 'minutes': (uptime.seconds % 3600) // 60, 'seconds': uptime.seconds % 60})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
    
    
"""
curl -X POST http://127.0.0.1:5000/api/gpu/7/switch
curl -X POST http://127.0.0.1:5000/api/run

curl http://127.0.0.1:5000/api/process
curl http://127.0.0.1:5000/api/gpus
curl http://127.0.0.1:5000/api/task/list
curl http://127.0.0.1:5000/api/system/info

curl http://127.0.0.1:5000/api/log/flowline.core.program.log?maxLines=1000
"""