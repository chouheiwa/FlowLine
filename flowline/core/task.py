import pandas as pd
import threading
import queue

from flowline.utils import Log

logger = Log(__name__)


class TaskStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"

class Task:
    def __init__(self, task_id, dict, run_num, name=None):
        self.task_id = task_id
        self.dict = dict
        self.run_num = run_num
        self.need_run_num = 1
        self.name = f"Task:{task_id}" if name is None else name
        self.state = TaskStatus.PENDING if self.run_num < self.need_run_num else TaskStatus.COMPLETED

    def __str__(self) -> str:
        return f"Task:{self.task_id}"
    
    def get_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "dict": str(self.dict),
            "run_num": self.run_num,
            "name": self.name,
            "status": self.state,
            "need_run_num": self.need_run_num
        }

class TaskManager:
    def __init__(self, excel_path):
        self._lock = threading.Lock()
        self.excel_path = excel_path
        logger.info(f"读取配置文件: {excel_path}")
        self.df = pd.read_excel(excel_path)
        self.df.to_excel(excel_path, index=False)

        self.tasks = []
        for idx, row in self.df.iloc[:].iterrows():
            config_dict = row.drop('run_num').to_dict()
            run_num = row['run_num']
            self.tasks.append(Task(idx, config_dict, run_num))

        self.task_ids = queue.PriorityQueue()
        for id in self.get_task_ids():
            self.task_ids.put(id)

    def synchronized(func):
        def wrapper(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return wrapper

    def get_task_ids(self):
        todo_df = self.df[self.df['run_num']==0]
        return list(todo_df.index)
    
    # -------------------------------
    
    def get_task_dict(self):
        list = []
        for task in self.tasks:
            if task.run_num == 0:
                list.append(task.get_dict())
        return list
    
    @synchronized
    def get_next_task(self) -> tuple[int, dict]:
        if self.task_ids.empty():
            return None, None
        id = self.task_ids.get()
        dict = self.tasks[id].dict
        logger.info(f"get task {id} config: {dict}")
        return id, dict
    
    @synchronized
    def put_task_ids(self, id):
        self.task_ids.put(id)
        logger.info(f"put task {id} back to queue")
        
    @synchronized
    def update_task_ids(self, id):
        self.tasks[id].run_num += 1
        self.df.loc[id, 'run_num'] += 1
        self.df.to_excel(self.excel_path, index=False)
        logger.info(f"update task {id} run times: {self.df.loc[id, 'run_num']}")

    @synchronized
    def create_task(self, name, cmd):
        return True

# task_manager = TaskManager()

if __name__ == "__main__":
    pass
    # print(2)
    # task = TaskManager()
    # print(task.get_next_task())
    # print(task.get_next_task())
    # task.update_task_ids(0)
    # print(todo.get_next_todo())
    
    """
    python -m flowline.todo
    """
