import pynvml
import time
import threading
from .log import Log

logger = Log(__name__)

class GPU_info:
    def __init__(self, free_memory, memory, utilization, other_user_process_num, time):
        self.free_memory = free_memory
        self.memory = memory
        self.utilization = utilization
        self.other_user_process_num = other_user_process_num
        self.time = time

class GPU:
    def __init__(self, id):
        self.id = id
        self.info_history = []
        self.info_history_length = 10
        self.info = []
        self.user_process_num = 0
        
    def flash(self):
        """
        更新GPU的空闲内存和利用率。
        """
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(self.id)
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        utilization_info = pynvml.nvmlDeviceGetUtilizationRates(handle)
        process_info = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)

        memory = memory_info.total / (1024 ** 2)
        free_memory = memory_info.free / (1024 ** 2)
        utilization = utilization_info.gpu
        other_user_process_num = len(process_info) - self.user_process_num
            
        self.info = GPU_info(free_memory, memory, utilization, other_user_process_num, time.time())
        self.info_history.append(self.info)
        self.info_history = self.info_history[-self.info_history_length:]
        
        logger.info(f"GPU {self.id} flashed: free memory={self.info.free_memory}MB, utilization={self.info.utilization}%, other user process num={self.info.other_user_process_num}") 
        
        pynvml.nvmlShutdown()
        return self.info
    
class GPU_Manager:
    def __init__(self, all_gpu_num, use_gpu_id: list):
        self._lock = threading.Lock()
        self.all_gpu = [GPU(i) for i in range(all_gpu_num)]
        self.usable_mark = [False] * len(self.all_gpu)
        for gpu_id in use_gpu_id:
            self.usable_mark[gpu_id] = True
        self.user_process_pid = []
        self.min_process_memory = 10000
        
    def synchronized(func):
        def wrapper(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return wrapper
    
    def update_user_process_num(self, gpu_id, pid, status):
        if status == "running":
            self.all_gpu[gpu_id].user_process_num += 1
        elif status == "completed":
            self.all_gpu[gpu_id].user_process_num -= 1
        elif status == "killed":
            self.all_gpu[gpu_id].user_process_num -= 1
            
    def flash_all_gpu(self):
        for gpu in self.all_gpu:
            gpu.flash()
    
    @synchronized
    def choose_gpu(self):
        choose_gpu = None
        for gpu in self.all_gpu:
            if self.usable_mark[gpu.id]:
                info: GPU_info = gpu.flash()
                if info.free_memory > self.min_process_memory:
                    if choose_gpu is None:
                        choose_gpu = gpu
                        continue
                    elif info.utilization < choose_gpu.info.utilization:
                        choose_gpu = gpu
                    elif info.utilization == gpu.info.utilization:
                        if info.free_memory > choose_gpu.info.free_memory:
                            choose_gpu = gpu
        return choose_gpu.id
        
    @synchronized
    def turn_on_gpu(self, id):
        self.usable_mark[id] = True
        
    @synchronized
    def turn_off_gpu(self, id):
        self.usable_mark[id] = False

    @synchronized
    def switch_gpu(self, id):
        self.usable_mark[id] = not self.usable_mark[id]
        return self.usable_mark[id]
                
                
# 示例使用
# gpu_manager = GPU_Manager([0, 1, 2, 3, 4, 5, 6, 7])

if __name__ == "__main__":
    gpu_manager = GPU_Manager(8, [0, 1, 2])
    print(gpu_manager.choose_gpu())