import os
import threading
import subprocess
import time
import psutil
import atexit
import signal
import sys
import datetime

from .log import Log

logger = Log(__name__)

####################################

# _all_processes = []

# def clean_all_processes():
#     print("==== clean_all_processes ====")
#     for process in _all_processes:
#         process.kill()

# atexit.register(clean_all_processes)

# def signal_handler(signum, frame):
#     print(f"收到信号 {signum}，正在终止...")
#     clean_all_processes()
#     sys.exit(0)

# signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
# signal.signal(signal.SIGTERM, signal_handler)  # kill
# signal.signal(signal.SIGTSTP, signal_handler)  # Ctrl+Z
# if hasattr(signal, 'SIGBREAK'):  # Windows Ctrl+Break
#     signal.signal(signal.SIGBREAK, signal_handler)

####################################

class Process:
    def __init__(self, id: int, dict: dict, todo_id: int, gpu_id: int, get_command, on_status_changed=None):
        self.id = id
        self.dict = dict
        self.pid = None
        self.todo_id = todo_id
        self.gpu_id = gpu_id
        self.cmd = get_command(dict, gpu_id)
        self.start_time = datetime.datetime.now()
        
        self.on_status_changed = on_status_changed
        self.status = "pending"  
        
        self.proc = None
        self.pid = None
        self.thread = self.run()
        # _all_processes.append(self)
        
    def change_status(self, status: str): # 状态跟踪: pending, running, completed, failed, killed
        self.status = status
        if self.on_status_changed:
            self.on_status_changed(self)
        
    def run(self):
        logger.info(f"[ID {self.id}] [TODO {self.todo_id}] [GPU {self.gpu_id}] Run (dict:'{self.dict}')")
        t = threading.Thread(
            target=self.run_command,
            args=(self.cmd,),
        )
        t.daemon = True
        t.start()
        self.change_status("running")
        return t
    
    def run_command(self, cmd):
        # 创建进程，并设置进程组ID，这样可以杀掉整个进程树
        if os.name != 'nt':  # 非Windows系统
            self.proc = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,  # 在新的会话中运行命令，这样可以一次性杀死所有相关进程
                # start_new_session=True  # 确保创建新会话
            )
        else:  # Windows系统
            self.proc = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
            )
        
        self.pid = self.proc.pid
        
        stdout, stderr = self.proc.communicate()
        
        if self.status != "killed":
            if self.proc.returncode == 0:
                logger.info(f"[ID {self.id}] [TODO {self.todo_id}] Success!")
                self.change_status("completed")
            else:
                logger.error(f"[ID {self.id}] [TODO {self.todo_id}] Error code: {self.proc.returncode}")
                if stderr:
                    logger.error(f"[ID {self.id}] [TODO {self.todo_id}] Stderr:\n{stderr.decode('utf-8')}")
                self.change_status("failed")
            
    def kill(self):
        if self.status == "killed":
            logger.info(f"[ID {self.id}] [TODO {self.todo_id}] [GPU {self.gpu_id}] Already killed")
            return
        logger.info(f"[ID {self.id}] [TODO {self.todo_id}] [GPU {self.gpu_id}] Kill")
        self.change_status("killed")
        if self.proc:
            try:
                pid = self.proc.pid
                
                # 使用psutil杀死整个进程树
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                
                for child in children:
                    try:
                        child.terminate()
                    except:
                        pass
                        
                # 终止父进程
                try:
                    parent.terminate()
                    gone, alive = psutil.wait_procs([parent] + children, timeout=3)
                    
                    # 如果仍有进程存活，发送SIGKILL
                    for p in alive:
                        try:
                            p.kill()
                        except:
                            pass
                except:
                    pass
                    
                # # 备用方法 
                # if os.name == 'nt':  # Windows
                #     os.system(f'taskkill /F /T /PID {pid}')
                # else:  # Unix/Linux
                #     os.killpg(os.getpgid(pid), signal.SIGKILL)
                    
            except Exception as e:
                logger.error(f"Error killing process: {e}")
                
        # 最多等待3秒钟让线程结束
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3)
            
            
class ProcessManager:
    def __init__(self, get_command, on_process_changed=None):
        self.id = 0
        self.get_command = get_command
        self.on_process_changed = on_process_changed
        
        self.max_processes = 10
        self.processes = []
        self.finished_processes = []
        
    def set_max_processes(self, max_processes: int):
        self.max_processes = max_processes
        
    def get_max_processes(self):
        return self.max_processes
        
    def add_process(self, dict: dict, todo_id: int, gpu_id: int):
        try:
            if len(self.processes) >= self.max_processes:
                logger.warning(f"进程数超过最大限制 {self.max_processes}")
                return None
            process = Process(self.id, dict, todo_id, gpu_id, self.get_command, self.on_process_status_changed)
            self.processes.append(process)
            self.id += 1
            return process
        except Exception as e:
            logger.error(f"添加进程失败: {e}")
            return None
            
    def kill_process_by_gpu(self, gpu_id: int):
        processes_to_kill = [p for p in self.processes if p.gpu_id == gpu_id]
        num = len(processes_to_kill)
        logger.info(f"找到 {num} 个GPU {gpu_id}的进程需要终止")
        for process in processes_to_kill:
            logger.info(f"终止进程 {process.id} : {process.gpu_id}")
            process.kill()
        return num
        
    def kill_process_by_id(self, id: int):
        target_process = None
        for process in self.processes:
            if process.id == id:
                target_process = process
                break
                
        if target_process:
            logger.info(f"终止进程ID {id}")
            target_process.kill()
            return True
        else:
            logger.warning(f"找不到进程ID {id}")
            return False
    
    def on_process_status_changed(self, process):
        # print(f"[ID {process.id}] [TODO {process.todo_id}] Process changed status: {process.status}")
        if process.status in ["completed", "failed", "killed"]: 
            if process in self.processes:
                self.processes.remove(process)
                self.finished_processes.append(process)
        if self.on_process_changed:
            self.on_process_changed(process)
            
    def kill_all_processes(self):
        processes_to_kill = list(self.processes)
        logger.info(f"终止所有进程，共 {len(processes_to_kill)} 个")
        
        for process in processes_to_kill:
            process.kill()
            
        return len(processes_to_kill)

if __name__ == "__main__":
    # 简单测试
    def on_completed(process):
        print(f"回调: 进程 {process.id} 状态改变为: {process.status}")
        
    def get_command(dict, gpu_id):
        return f"CUDA_VISIBLE_DEVICES={gpu_id} python test.py " + " ".join([f"--{key} {value}" for key, value in dict.items()])
    
    # 注册回调
    process_manager = ProcessManager(get_command, on_completed)
    
    # 添加进程
    process_manager.add_process({"test": "a"}, 1, 4)
    process_manager.add_process({"test": "b"}, 2, 4)
    
    # 等待一段时间
    time.sleep(5)
    
    # 手动终止一个进程
    process_manager.kill_process_by_id(0)
    
    # 等待所有进程完成
    time.sleep(5)
    print("所有死亡进程状态:", [(p.id, p.status) for p in process_manager.finished_processes])
    print("所有活动进程状态:", [(p.id, p.status) for p in process_manager.processes])
    