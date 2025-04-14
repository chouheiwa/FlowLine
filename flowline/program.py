import threading
import time
import atexit
import psutil
import signal
import sys
import os

from .gpu import GPU_Manager
from .process import ProcessManager, Process
from .todo import TodoManager
from .log import Log

logger = Log(__name__)

####################################

# _all_programs = []

# def clean_all_programs():
#     print("==== clean_all_programs ====")
#     for program in _all_programs:
#         program.exit()
#     try:
#         os.system("ps aux | grep 'python' | grep -v grep | awk '{print $2}' | xargs -r kill -9")
#     except:
#         pass
        
# atexit.register(clean_all_programs)

# def signal_handler(signum, frame):
#     print(f"收到信号 {signum}，正在终止...")
#     clean_all_programs()
#     sys.exit(0)

# signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
# signal.signal(signal.SIGTERM, signal_handler)  # kill
# signal.signal(signal.SIGTSTP, signal_handler)  # Ctrl+Z
# if hasattr(signal, 'SIGBREAK'):  # Windows Ctrl+Break
#     signal.signal(signal.SIGBREAK, signal_handler)

####################################

class ProgramManager:
    def __init__(self, get_command):
        self._lock = threading.Lock()
        self.gpu_manager = GPU_Manager(8, [0, 1, 2])
        self.process_manager = ProcessManager(get_command, self.on_process_changed)
        self.todo_manager = TodoManager()
        self.if_run = True
        self._main_thread = None 
        # _all_programs.append(self)
        
    def synchronized(func):
        def wrapper(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return wrapper
    
    def on_process_changed(self, process: Process):
        logger.info(f"进程 {process.id} 状态已改变: {process.status}")
        self.gpu_manager.update_user_process_num(process.gpu_id, process.pid, process.status)
        if process.status == "completed":
            self.todo_manager.update_todo_ids(process.todo_id)
            logger.info(f"进程 {process.id} 状态为 {process.status}，任务 {process.todo_id} 完成")
        elif process.status in ["failed", "killed"]:
            self.todo_manager.put_todo_ids(process.todo_id)
            logger.warning(f"进程 {process.id} 状态为 {process.status}，任务 {process.todo_id} 重新入队")
        else:
            logger.info(f"进程 {process.id} 状态为 {process.status}")
            
    def set_max_processes(self, max_processes: int):
        self.process_manager.set_max_processes(max_processes)
            
    @synchronized
    def new_process(self):
        """创建新进程处理任务"""
        todo_id, dict = self.todo_manager.get_next_todo()
        if todo_id is None:
            logger.warning("没有可用的任务")
            return
        gpu_id = self.gpu_manager.choose_gpu()
        if gpu_id is None:
            self.todo_manager.put_todo_ids(todo_id)
            logger.warning(f"没有可用的GPU，任务 {todo_id} 重新入队")
            return
        if self.process_manager.add_process(dict, todo_id, gpu_id) is None:
            self.todo_manager.put_todo_ids(todo_id)
            logger.warning(f"无法生成进程，任务 {todo_id} 重新入队")
        
    def run_process_loop(self):
        """主循环，持续检查并创建新任务"""
        while self.if_run:
            self.new_process()
            time.sleep(10)
        logger.info("主处理循环已停止")
            
    def start_process_loop(self):
        """启动主处理循环作为一个后台线程"""
        if self._main_thread and self._main_thread.is_alive():
            print("处理循环已经在运行中")
            return
            
        self.if_run = True
        self._main_thread = threading.Thread(target=self.run_process_loop)
        self._main_thread.daemon = True  # 设置为守护线程，确保主程序退出时线程也会退出
        self._main_thread.start()
        print("处理循环已启动")
        
    def stop_process_loop(self):
        """停止主处理循环"""
        self.if_run = False
        if self._main_thread:
            print("处理循环正在停止...")
        else:
            print("处理循环未运行")
            
    def switch_run(self):
        """切换运行状态"""        
        if self.if_run:
            self.stop_process_loop()
        else:
            self.start_process_loop()
        return self.if_run
        
    def switch_gpu(self, gpu_id):
        """切换GPU可用状态"""
        if 0 <= gpu_id < len(self.gpu_manager.all_gpu):
            is_on = self.gpu_manager.switch_gpu(gpu_id)
            print(f"GPU {gpu_id} 已切换为 {'可用' if is_on else '不可用'}")
            return True
        else:
            print(f"无效的GPU ID: {gpu_id}")
            return False
        
    @synchronized
    def kill_process_by_gpu(self, gpu_id):
        """杀死指定GPU上的所有进程"""
        if 0 <= gpu_id < len(self.gpu_manager.all_gpu):
            num = self.process_manager.kill_process_by_gpu(gpu_id)
            print(f"已终止GPU {gpu_id}上的所有进程，共 {num} 个")
        else:
            print(f"无效的GPU ID: {gpu_id}")
        
    @synchronized
    def kill_process(self, process_id):
        """杀死指定ID的进程"""
        if self.process_manager.kill_process_by_id(process_id):
            print(f"已终止进程 {process_id}")
        else:
            print(f"找不到进程 {process_id}")
    
    def list_processes(self):
        """列出所有正在运行的进程"""
        active_processes = self.process_manager.processes
        if not active_processes:
            print("没有正在运行的进程")
            return
            
        print("\n当前运行的进程:")
        print("-" * 70)
        print(f"{'ID':<5} {'TODO ID':<8} {'GPU ID':<8} {'状态':<10} {'命令':<30}")
        print("-" * 70)
        for p in active_processes:
            cmd_str = str(p.dict)
            if len(cmd_str) > 30:
                cmd_str = cmd_str[:27] + "..."
            print(f"{p.id:<5} {p.todo_id:<8} {p.gpu_id:<8} {p.status:<10} {cmd_str:<30}")
        print("-" * 70)
        print(f"最大进程数: {self.process_manager.get_max_processes()}")
    
    def list_gpus(self):
        """列出所有GPU状态"""
        self.gpu_manager.flash_all_gpu()
        print("\nGPU状态:")
        print("-" * 130)
        print(f"{'ID':<5} {'状态':<5} {'使用率(%)':<10} {'空闲内存/总内存(MB)':<20} {'用户进程数/总进程数':<20} {'温度':<10} {'功率/最大功率(W)':<20}")
        print("-" * 130)
        for i, gpu in enumerate(self.gpu_manager.all_gpu):
            info = gpu.flash()
            status = "可用" if self.gpu_manager.usable_mark[i] else "禁用"
            memory_str = f"{info.free_memory:.0f}/{info.memory:.0f}"
            power_str = f"{info.power:.0f}/{info.max_power:.0f}"
            process_str = f"{info.user_process_num}/{info.all_process_num}"
            print(f"{gpu.id:<5} {status:<5} {info.utilization:<10.2f} {memory_str:<20} {process_str:<20} {info.temperature:<10} {power_str:<20}")
        print("-" * 130)
        
    def exit(self):
        """安全退出，终止所有进程和线程"""
        logger.info("执行退出操作")
        
        # 首先停止主处理循环
        self.stop_process_loop()
        
        # 终止所有子进程
        num_killed = self.process_manager.kill_all_processes()
        logger.info(f"已终止 {num_killed} 个进程")
        
        # 等待主线程完成（如果存在）
        if self._main_thread and self._main_thread.is_alive():
            logger.info("等待主线程结束")
            self._main_thread.join(timeout=3)
            if self._main_thread.is_alive():
                logger.warning("主线程未能在超时时间内结束")
            else:
                logger.info("主线程已结束")
        
        logger.info("退出操作完成")

if __name__ == "__main__":
    def get_command(dict, gpu_id):
        return f"CUDA_VISIBLE_DEVICES={gpu_id} python test.py " + " ".join([f"--{key} {value}" for key, value in dict.items()])
    program = ProgramManager(get_command)
    program.new_process()
    time.sleep(5)
    program.new_process()
    time.sleep(5)

    # python -m program.program