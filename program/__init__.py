import warnings
import asyncio
import threading
import signal
import sys
import time
from .gpu import GPU_Manager
from .process import ProcessManager, Process
from .todo import TodoManager


def get_command(dict, gpu_id):
    return f"python main.py " + " ".join([f"--{key} {value}" for key, value in dict.items()] + [f"--gpu {gpu_id}"])

class ProgramManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.gpu_manager = GPU_Manager([0, 1, 2, 3, 4, 5, 6, 7])
        self.process_manager = ProcessManager(get_command, self.on_process_changed)
        self.todo_manager = TodoManager()
        self.if_run = True
        self._main_task = None  # 存储主运行任务
        self._event_loop = None  # 存储事件循环引用
        
    def synchronized(func):
        def wrapper(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return wrapper
    
    def on_process_changed(self, process: Process):
        self.gpu_manager.update_user_process_num(process.gpu_id, process.pid, process.status)
        
    @synchronized
    def new_process(self):
        """创建新进程处理任务"""
        todo_id, dict = self.todo_manager.get_next_todo()
        if todo_id is None:
            return False
        gpu_id = self.gpu_manager.choose_gpu()
        if gpu_id is None:
            return False
        self.process_manager.add_process(dict, todo_id, gpu_id)
        return True
        
    def run_process_loop(self):
        """主循环，持续检查并创建新任务"""
        while self.if_run:
            self.new_process()
            time.sleep(10)
            
    def switch_run(self):
        """切换运行状态"""        
        self.if_run = not self.if_run
        
    def switch_gpu(self, gpu_id):
        """切换GPU可用状态"""
        self.gpu_manager.switch_gpu(gpu_id)
        
    @synchronized
    def kill_process_by_gpu(self, gpu_id):
        """杀死指定GPU上的所有进程"""
        self.process_manager.kill_process_by_gpu(gpu_id)
        
    def kill_process(self, process_id):
        """杀死指定ID的进程"""
        self.process_manager.kill_process_by_id(process_id)


if __name__ == "__main__":
    pass

"""
python -m program.__init__
"""