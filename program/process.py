import os
import threading
import subprocess
import sys
import time
import signal
import psutil
import atexit
import multiprocessing

# 存储所有创建的进程实例，便于程序退出时清理
_all_processes = []

# 退出时清理所有子进程
def cleanup_all_processes():
    print("正在清理所有子进程...")
    for proc in _all_processes:
        try:
            if proc.proc:
                proc.kill()
        except:
            pass
    
    # 检查是否有任何遗留进程
    if psutil.WINDOWS:
        # Windows系统上使用taskkill确保Python进程和所有子进程终止
        python_pids = []
        try:
            for p in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'python' in p.info['name'].lower() and 'test.py' in ' '.join(p.info.get('cmdline', [])):
                    python_pids.append(p.info['pid'])
            
            if python_pids:
                print(f"发现{len(python_pids)}个遗留Python测试进程，正在终止...")
                for pid in python_pids:
                    try:
                        os.system(f'taskkill /F /T /PID {pid}')
                    except:
                        pass
        except:
            pass
    else:
        # Unix系统
        try:
            # 终止所有包含test.py的Python进程
            os.system("ps aux | grep 'python.*test.py' | grep -v grep | awk '{print $2}' | xargs -r kill -9")
        except:
            pass

# 注册退出处理函数
atexit.register(cleanup_all_processes)

# 注册信号处理函数
def signal_handler(signum, frame):
    print(f"收到信号 {signum}，正在终止...")
    cleanup_all_processes()
    sys.exit(0)

# 为常见的终止信号注册处理函数
signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # kill
if hasattr(signal, 'SIGBREAK'):  # Windows Ctrl+Break
    signal.signal(signal.SIGBREAK, signal_handler)

class Process:
    def __init__(self, id: int, dict: dict, todo_id: int, gpu_id: int, on_status_changed=None):
        self.id = id
        self.dict = dict
        self.pid = None
        self.todo_id = todo_id
        self.gpu_id = gpu_id
        
        self.on_status_changed = on_status_changed
        self.status = "pending"  
        
        self.proc = None
        self.thread = self.run()
        _all_processes.append(self)
        
    def change_status(self, status: str): # 状态跟踪: pending, running, completed, failed, killed
        self.status = status
        if self.on_status_changed:
            self.on_status_changed(self, status)
        
    def run(self):
        print(f"[ID {self.id}] [TODO {self.todo_id}] [GPU {self.gpu_id}] Run (dict:'{self.dict}')")
        t = threading.Thread(
            target=self.run_command,
            args=(self.get_command(),),
        )
        t.daemon = True
        t.start()
        self.change_status("running")
        return t
    
    def kill(self):
        print(f"[ID {self.id}] [TODO {self.todo_id}] [GPU {self.gpu_id}] Kill")
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
                print(f"Error killing process: {e}")
                
        # 最多等待3秒钟让线程结束
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3)
            
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
        
        # 保存进程ID
        self.pid = self.proc.pid
        
        stdout, stderr = self.proc.communicate()
        
        if self.proc.returncode == 0:
            print(f"[ID {self.id}] [TODO {self.todo_id}] Success!")
            self.change_status("completed")
        else:
            print("==================================================")
            print(f"[ID {self.id}] [TODO {self.todo_id}] Error code: {self.proc.returncode}")
            if stderr:
                print(f"[ID {self.id}] [TODO {self.todo_id}] Stderr:\n{stderr.decode('utf-8')}")
            print("==================================================")
            
            if self.status != "killed":
                self.change_status("failed")
        
    def get_command(self):
        return f"python test.py " + " ".join([f"--{key} {value}" for key, value in self.dict.items()])
        
class ProcessManager:
    def __init__(self, on_process_changed=None):
        self.processes = []
        self.finished_processes = []
        self.on_process_changed = on_process_changed
        
    def add_process(self, dict: dict, todo_id: int, gpu_id: int):
        process = Process(len(self.processes), dict, todo_id, gpu_id, self.on_process_status_changed)
        self.processes.append(process)
        return process
    
    def get_process_by_id(self, process_id):
        for process in self.processes:
            if process.id == process_id:
                return process
        for process in self.finished_processes:
            if process.id == process_id:
                return process
        return None
    
    def kill_process_by_gpu(self, gpu_id: int):
        processes_to_remove = []
        for process in self.processes:
            if process.gpu_id == gpu_id:
                process.kill()
                processes_to_remove.append(process)
        
        for process in processes_to_remove:
            if process in self.processes:  # 再次检查，避免重复删除
                self.processes.remove(process)
                
    def kill_process_by_id(self, id: int):
        process = self.get_process_by_id(id)
        if process:
            process.kill()
        if process in self.processes:
            self.processes.remove(process)
    
    def on_process_status_changed(self, process, status):
        print(f"[ID {process.id}] [TODO {process.todo_id}] Process changed status: {status}")
        if status in ["completed", "failed", "killed"]: 
            if process in self.processes:
                self.processes.remove(process)
                self.finished_processes.append(process)
            if self.on_process_changed:
                self.on_process_changed(process, status)

if __name__ == "__main__":
    # 简单测试
    def on_completed(process, status):
        print(f"回调: 进程 {process.id} 完成，状态: {status}")
    
    # 注册回调
    process_manager = ProcessManager(on_process_changed=on_completed)
    
    # 添加进程
    process_manager.add_process({"test": "a"}, 1, 0)
    process_manager.add_process({"test": "b"}, 2, 0)
    
    # 等待一段时间
    time.sleep(5)
    
    # 手动终止一个进程
    process_manager.kill_process_by_id(0)
    
    # 等待所有进程完成
    time.sleep(5)
    print("所有死亡进程状态:", [(p.id, p.status) for p in process_manager.finished_processes])
    print("所有活动进程状态:", [(p.id, p.status) for p in process_manager.processes])
    