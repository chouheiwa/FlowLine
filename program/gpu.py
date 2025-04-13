import pynvml
import time
import threading


class GPU_info:
    def __init__(self, free_memory, utilization, other_user_process_num, time):
        self.free_memory = free_memory
        self.utilization = utilization
        self.other_user_process_num = other_user_process_num
        self.time = time

class GPU:
    def __init__(self, id):
        self.id = id
        self.info_history = []
        self.info = []
        self.flash()
        
    def flash(self):
        """
        更新GPU的空闲内存和利用率。
        """
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(self.id)
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        utilization_info = pynvml.nvmlDeviceGetUtilizationRates(handle)
        process_info = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
         # for process in process_info:
        #     print(process)
        self.info = GPU_info(memory_info.free / (1024 ** 2), utilization_info.gpu, len(process_info) - len(self.process_pool), time.time())
        self.info_history.append(self.info)
        print(f"GPU {self.id} flashed: free memory={self.info.free_memory}MB, utilization={self.info.utilization}%, other user process num={self.info.other_user_process_num}") 
        pynvml.nvmlShutdown()
        return self.info
    
class GPU_Manager:
    def __init__(self, all_gpu: list):
        self._lock = threading.Lock()
        self.all_gpu = [GPU(i) for i in all_gpu]
        self.usable_mark = [True] * len(all_gpu)
        
        self.min_process_memory = 10000
        
    def synchronized(func):
        def wrapper(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return wrapper
    
    @synchronized
    def choose_gpu(self):
        gpu_id = None
        min_utilization = 101
        for gpu in self.all_gpu:
            info: GPU_info = gpu.flash()
            if info.free_memory > self.min_process_memory:
                if info.utilization < min_utilization:
                    min_utilization = info.utilization
                    gpu_id = gpu.id
        return gpu_id
        
    @synchronized
    def turn_on_gpu(self, id):
        self.usable_mark[id] = True
        
    @synchronized
    def turn_off_gpu(self, id):
        self.usable_mark[id] = False


# 示例使用
gpu_manager = GPU_Manager([0, 1, 2, 3, 4, 5, 6, 7])