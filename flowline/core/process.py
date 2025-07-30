import multiprocessing
import time
import threading

from flowline.config import config
from flowline.utils import FunctionCall, PopenProcess, Log

logger = Log(__name__)

class ProcessStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    KILLING = "KILLING"
    KILLED = "KILLED"
    
    def __str__(self):
        return self.name
    
"""
PENDING ─> RUNNING ─> COMPLETED √
              ├─> KILLING ─> KILLED
              └─> FAILED
"""

class Process:
    def __init__(self, process_id: int, cmd: str, task_id: int, gpu_id: int, on_status_changed=None):
        self.manager = multiprocessing.Manager()
        self.shared_dict = self.manager.dict()
        self.shared_dict["status"] = ProcessStatus.PENDING
        self.on_status_changed = on_status_changed
        
        self.process_id = process_id
        self.cmd = cmd
        self.task_id = task_id
        self.gpu_id = gpu_id
        self.start_time = time.time()
        
        self.pid = None
        self._process = None
        self.result_queue = multiprocessing.Queue()
        self.run()
        self.pid = self._process.pid
        
    def change_status(self, status: ProcessStatus):
        try:
            logger.info(f"[ID {self.process_id}] [Task {self.task_id}] [GPU {self.gpu_id}] Change status from '{self.shared_dict['status']}' to '{status}'")
            self.shared_dict["status"] = status
            if self.on_status_changed:
                self.on_status_changed(self)
        except Exception as e:
            logger.error(f"Process change_status: failed: {e}")
            
    def get_status(self):
        return self.shared_dict["status"]
        
    def run(self):
        try:
            self._process = multiprocessing.Process(target=PopenProcess(self.result_queue, self.process_id).fcb, args=(self.cmd,))
            self._process.daemon = True
            self._process.start()
            self.change_status(ProcessStatus.RUNNING)
            threading.Thread(target=self._wait_result, daemon=True).start()
        except Exception as e:
            logger.error(f"Process run: failed: {e}")
            raise e
    
    def _wait_result(self):
        try:
            self._process.join()
            success, result = self.result_queue.get()
            if success:
                self.on_completed()
            else:
                if self.get_status() != ProcessStatus.KILLED and self.get_status() != ProcessStatus.KILLING:
                    self.on_failed(result)
        except Exception as e:
            logger.error(f"Process _wait_result: failed: {e}")
            
    def kill(self):
        if self.shared_dict["status"] in [ProcessStatus.RUNNING]:
            self._process.terminate()
            self.change_status(ProcessStatus.KILLING)
            self._process.join()
            if self._process.is_alive():
                logger.warning(f"[ID {self.process_id}] [Task {self.task_id}] [GPU {self.gpu_id}] Process is can't be killed")
                return False
            else:
                self.change_status(ProcessStatus.KILLED)
                return True
        else:
            logger.warning(f"[ID {self.process_id}] [Task {self.task_id}] [GPU {self.gpu_id}] Process is not running")
            return False
        
    def on_completed(self, result = None):
        logger.info(f"[ID {self.process_id}] [Task {self.task_id}] [GPU {self.gpu_id}] Completed (result:{result})")
        self.change_status(ProcessStatus.COMPLETED)
        
    def on_failed(self, error):
        logger.error(f"[ID {self.process_id}] [Task {self.task_id}] [GPU {self.gpu_id}] Failed (error:{error})")
        self.change_status(ProcessStatus.FAILED)
        
    def get_dict(self):
        return {
            "process_id": self.process_id,
            "pid": self.pid,
            "task_id": self.task_id,
            "gpu_id": self.gpu_id,
            "start_time": self.start_time,
            "status": self.get_status(),
            "cmd": self.cmd
        }
            
class ProcessManager:
    def __init__(self, on_process_changed=None):
        self._lock = threading.Lock()
        self.process_id_gen = self.id_generator()
        self.on_process_changed = on_process_changed
        
        self.max_processes = config.DEFAULT_MAX_PROCESSES
        self.processes = []
        
    def synchronized(func):
        def wrapper(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return wrapper

    def id_generator(self):
        current_id = 0
        while True:
            yield current_id
            current_id += 1
            
    def set_max_processes(self, max_processes: int):
        self.max_processes = max_processes
        
    def get_max_processes(self):
        return self.max_processes
        
    def have_space(self) -> bool:
        return len(self.processes) < self.max_processes
            
    def on_process_state(self, process):
        # logger.info(f"ProcessManager on_process_state: Process {process.process_id} status: '{process.shared_dict['status']}'")
        if process.shared_dict['status'] in [ProcessStatus.COMPLETED, ProcessStatus.FAILED, ProcessStatus.KILLED]: 
            self.remove_process(process)
        if self.on_process_changed:
            self.on_process_changed(process.task_id, process.process_id, process.gpu_id, process.pid, process.get_status())
        
    @synchronized
    def remove_process(self, process):
        self.processes.remove(process)
        
    @synchronized
    def add_process(self, cmd: str, task_id: int, gpu_id: int):
        try:
            if not self.have_space():
                logger.warning(f"ProcessManager: Process number exceeds the maximum limit {self.max_processes}")
                return None
            process = Process(next(self.process_id_gen), cmd, task_id, gpu_id, self.on_process_state)
            self.processes.append(process)
            return True
        except Exception as e:
            logger.error(f"ProcessManager add_process: Failed to add process: {e}")
            return False
            
    def kill_process_by_gpu(self, gpu_id: int):
        processes_to_kill = [p for p in self.processes if p.gpu_id == gpu_id]
        num = len(processes_to_kill)
        logger.info(f"ProcessManager: Found {num} processes on GPU {gpu_id} to terminate")
        for process in processes_to_kill:
            logger.info(f"ProcessManager: Terminate process {process.process_id} : {process.gpu_id}")
            process.kill()
        return num
        
    def kill_process_by_id(self, process_id: int):
        target_process = None
        for process in self.processes:
            if process.process_id == process_id:
                target_process = process
                break
        if target_process:
            success = target_process.kill()
            logger.info(f"ProcessManager kill_process_by_id: Terminate process ID {process_id} {'success' if success else 'failed'}")
            return success
        else:
            logger.warning(f"ProcessManager kill_process_by_id: Process ID {process_id} not found")
            return False
            
    def kill_all_processes(self):
        processes_to_kill = list(self.processes)
        logger.info(f"ProcessManager: Terminate all processes, {len(processes_to_kill)} processes")
        for process in processes_to_kill:
            process.kill()
        return len(processes_to_kill)

    def get_process_dict(self):
        return {p.process_id: p.get_dict() for p in self.processes}
    
    def get_process_dict_by_gpu(self, gpu_id: int):
        return {p.process_id: p.get_dict() for p in self.processes if p.gpu_id == gpu_id}

if __name__ == "__main__":
    def on_completed(task_id, process_id, gpu_id, pid, status):
        print(f"on_completed: Process {process_id} status: {status}")
    
    def func(k, v):
        return f"CUDA_VISIBLE_DEVICES={k} python test.py --test {v}"
            
    fc1 = FunctionCall(func, 4, "a")
    # fc2 = FunctionCall(func, 5, "b")
    
    process_manager = ProcessManager(on_completed)
    
    process_manager.add_process(fc1(), 1, 4)
    # process_manager.add_process(fc2(), 2, 4)
    
    # time.sleep(5)
    
    # process_manager.kill_process_by_id(0)
    
    # 等待所有进程完成
    time.sleep(5)
    print("所有活动进程状态:", [(p.process_id, p.get_status()) for p in process_manager.processes])
    
    # python -m flowline.process