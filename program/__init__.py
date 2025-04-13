import warnings
import asyncio
import threading
from .gpu import GPU_Manager, GPU_info, GPU, gpu_manager
from .process import Process, ProcessManager, process_manager
from .todo import TodoManager, todo_manager


class ProgramManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.gpu_manager = gpu_manager
        self.process_manager = process_manager
        self.todo_manager = todo_manager
        self.if_run = True
        
    def synchronized(func):
        def wrapper(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return wrapper
        
    @synchronized
    async def new_process(self):
        todo_id, dict = self.todo_manager.get_next_todo()
        if todo_id is None:
            warnings.warn("No todo id")
            return
        gpu_id = self.gpu_manager.choose_gpu()
        process_manager.add_process(dict, todo_id, gpu_id)
        
    @synchronized    
    async def switch_gpu(self, id):
        self.gpu_manager.switch_gpu(id)
        
    async def run_process(self):
        while self.if_run:
            self.new_process()
            await asyncio.sleep(1)
            
    async def switch_run(self):
        self.if_run = not self.if_run
        
program = ProgramManager()
        
        
if __name__ == "__main__":
    pass
    
"""
python -m program.__init__
"""