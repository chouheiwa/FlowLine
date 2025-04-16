import multiprocessing
import time

from .log import Log
from .utils import FunctionCall, FunctionCallBack

logger = Log(__name__)

class ProcessStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    KILLING = "killing"
    KILLED = "killed"
    
class Process:
    def __init__(self, process_id: int, fc: FunctionCall, todo_id: int, gpu_id: int, on_status_changed=None):
        self.process_id = process_id
        self.fc = fc
        self.fcb = FunctionCallBack(fc, success_callback=self.on_completed, error_callback=self.on_failed)
        self.todo_id = todo_id
        self.gpu_id = gpu_id
        self.start_time = time.time()
        self.on_status_changed = on_status_changed
        self.status = ProcessStatus.PENDING
        self.pid = None
        self._process = self.run()
        self.pid = self._process.pid
        
    def change_status(self, status: ProcessStatus):
        self.status = status
        if self.on_status_changed:
            self.on_status_changed(self)
        
    def run(self):
        logger.info(f"[ID {self.process_id}] [TODO {self.todo_id}] [GPU {self.gpu_id}] Run (fcb:{self.fcb})")
        proc = multiprocessing.Process(target=self.fcb)
        proc.daemon = True
        proc.start()
        self.change_status(ProcessStatus.RUNNING)
        return proc
            
    def kill(self):
        self._process.terminate()
        self.change_status(ProcessStatus.KILLING)
        self._process.join()
        self.change_status(ProcessStatus.KILLED)
        
    def on_completed(self, result):
        logger.info(f"[ID {self.process_id}] [TODO {self.todo_id}] [GPU {self.gpu_id}] Completed (result:{result})")
        self.change_status(ProcessStatus.COMPLETED)
        
    def on_failed(self, error):
        logger.error(f"[ID {self.process_id}] [TODO {self.todo_id}] [GPU {self.gpu_id}] Failed (error:{error})")
        self.change_status(ProcessStatus.FAILED)
            
class ProcessManager:
    def __init__(self, on_process_changed=None):
        self.process_id_gen = self.id_generator()
        self.on_process_changed = on_process_changed
        
        self.max_processes = 4
        self.processes = []

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
        
    def add_process(self, fc: FunctionCall, todo_id: int, gpu_id: int):
        try:
            if not self.have_space():
                logger.warning(f"ProcessManager: Process number exceeds the maximum limit {self.max_processes}")
                return None
            process = Process(next(self.process_id_gen), fc, todo_id, gpu_id, self.on_process_state)
            self.processes.append(process)
            return process
        except Exception as e:
            logger.error(f"ProcessManager: Failed to add process: {e}")
            return None
            
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
            logger.info(f"ProcessManager: Terminate process ID {process_id}")
            target_process.kill()
            return True
        else:
            logger.warning(f"ProcessManager: Process ID {process_id} not found")
            return False
    
    def on_process_state(self, process):
        if process.status in [ProcessStatus.COMPLETED, ProcessStatus.FAILED, ProcessStatus.KILLED]: 
            if process in self.processes:
                self.processes.remove(process)
        if self.on_process_changed:
            self.on_process_changed(process.todo_id, process.process_id, process.gpu_id, process.pid, process.status)
            
    def kill_all_processes(self):
        processes_to_kill = list(self.processes)
        logger.info(f"ProcessManager: Terminate all processes, {len(processes_to_kill)} processes")
        for process in processes_to_kill:
            process.kill()
        return len(processes_to_kill)

if __name__ == "__main__":
    import torch
    
    # 简单测试
    def on_completed(todo_id, process_id, gpu_id, pid, status):
        print(f"on_completed: Process {process_id} status: {status}")
    
    def test_func(k):
        tensor = torch.randn(1000, 1000).to("cuda:" + str(k))
        i = 0
        while i<10:
            print(i)
            i += 1
            if i > 10:
                raise Exception("test exception")
            time.sleep(1)
        return "test success"
            
    fc1 = FunctionCall(test_func, 4)
    fc2 = FunctionCall(test_func, 5)
    
    process_manager = ProcessManager(on_completed)
    
    process_manager.add_process(fc1, 1, 4)
    process_manager.add_process(fc2, 2, 4)
    
    time.sleep(5)
    
    process_manager.kill_process_by_id(0)
    
    # 等待所有进程完成
    time.sleep(15)
    print("所有活动进程状态:", [(p.process_id, p.status) for p in process_manager.processes])
    
    # python -m flowline.process