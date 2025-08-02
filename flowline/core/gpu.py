import pynvml
import time
import threading

from flowline.config import config
from flowline.utils import Log

logger = Log(__name__)


class GPU_info:
    def __init__(self, free_memory, total_memory, utilization, all_process_num, name, temperature, power, max_power):
        self.free_memory = free_memory
        self.total_memory = total_memory
        self.utilization = utilization
        self.user_process_num = 0
        self.all_process_num = all_process_num
        self.time = time.time(),
        self.name = name
        self.temperature = temperature
        self.power = power
        self.max_power = max_power
        
    def to_dict(self):
        return {
            "free_memory": self.free_memory,
            "total_memory": self.total_memory,
            "utilization": self.utilization,
            "user_process_num": self.user_process_num,
            "all_process_num": self.all_process_num,
            "name": self.name,
            "temperature": self.temperature,
            "power": self.power,
            "max_power": self.max_power
        }
        
class GPU:
    def __init__(self, gpu_id, on_flash=None):
        self.gpu_id = gpu_id
        self.info_history = []
        self.info_history_length = 10
        self.info = []
        self.user_process_num = 0
        self.on_flash = on_flash
        self.monitor_interval = 5
        self.monitor_thread = self._run_monitor()
        
    def flash(self):
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(self.gpu_id)
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        utilization_info = pynvml.nvmlDeviceGetUtilizationRates(handle)
        process_info = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)

        total_memory = memory_info.total / (1024 ** 2)
        free_memory = memory_info.free / (1024 ** 2)
        utilization = utilization_info.gpu
        all_process_num = len(process_info)
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        name = gpu_name.decode('utf-8') if isinstance(gpu_name, bytes) else gpu_name
        temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000
        try:
            max_power = pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000
        except pynvml.NVMLError as e:
            if e.value == pynvml.NVML_ERROR_NOT_SUPPORTED:
                max_power = '?'
            else:
                raise
            
        self.info = GPU_info(free_memory, total_memory, utilization, all_process_num, name, temperature, power, max_power)
        self.info_history.append(self.info)
        self.info_history = self.info_history[-self.info_history_length:]
        
        # logger.info(f"GPU: GPU {self.gpu_id} flashed") 
        if self.on_flash:
            self.on_flash(self.gpu_id, self.info)
        pynvml.nvmlShutdown()
        
    def _monitor_gpu(self):
        while True:
            self.flash()
            time.sleep(self.monitor_interval)
            
    def _run_monitor(self):
        thread = threading.Thread(target=self._monitor_gpu)
        thread.daemon = True
        thread.start()
        return thread
    
    def get_dict(self):
        return self.info.to_dict()
    
    def __str__(self) -> str:
        return f"GPU:{self.gpu_id}"
    
def get_gpu_count():
    pynvml.nvmlInit()
    gpu_count = pynvml.nvmlDeviceGetCount()
    pynvml.nvmlShutdown()
    return gpu_count
    
class GPU_Manager:
    def __init__(self, use_gpu_id: list, on_flash=None):
        self._lock = threading.Lock()
        self.all_gpu = [GPU(i, on_flash) for i in range(get_gpu_count())]
        self.usable_mark = [False] * len(self.all_gpu)
        for gpu_id in use_gpu_id:
            self.usable_mark[gpu_id] = True
        self.user_process_pid = []
        self.min_process_memory = config.DEFAULT_MIN_PROCESS_MEMORY
        
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
        self.flash_all_gpu()
        choose_gpu = None
        for gpu in self.all_gpu:
            if self.usable_mark[gpu.gpu_id]:
                info = gpu.info
                if info.free_memory > self.min_process_memory:
                    if choose_gpu is None:
                        choose_gpu = gpu
                        continue
                    elif info.utilization < choose_gpu.info.utilization:
                        choose_gpu = gpu
                    elif info.utilization == gpu.info.utilization:
                        if info.free_memory > choose_gpu.info.free_memory:
                            choose_gpu = gpu
        logger.info(f"GPU_Manager choose_gpu: {choose_gpu}")
        return choose_gpu.gpu_id if choose_gpu is not None else None

    @synchronized
    def switch_gpu(self, gpu_id):
        if gpu_id < 0 or gpu_id >= len(self.all_gpu):
            logger.error(f"GPU_Manager switch_gpu: Invalid GPU ID: {gpu_id}")
            return False, None
        self.usable_mark[gpu_id] = not self.usable_mark[gpu_id]
        return True, self.usable_mark[gpu_id]
    
    def get_gpu_dict(self):
        gpu_dict = {}
        for gpu in self.all_gpu:
            dict = gpu.get_dict()
            dict['status'] = "available" if self.usable_mark[gpu.gpu_id] else "disabled"
            gpu_dict[gpu.gpu_id] = dict
        return gpu_dict
                
    def set_min_process_memory(self, min_process_memory):
        self.min_process_memory = min_process_memory

    def get_min_process_memory(self):
        return self.min_process_memory
                
# 示例使用
# gpu_manager = GPU_Manager([0, 1, 2, 3, 4, 5, 6, 7])

if __name__ == "__main__":
    gpu_manager = GPU_Manager([0, 1, 2])
    print(gpu_manager.choose_gpu())