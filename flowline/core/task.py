import pandas as pd
import threading
import queue

from flowline.utils import Log

logger = Log(__name__)

def read_configs(excel_path):
    """
    Read the configuration parameters from the Excel file.
    """
    logger.info(f"读取配置文件: {excel_path}")
    df = pd.read_excel(excel_path)
    return df


class TaskManager:
    def __init__(self, excel_path):
        self._lock = threading.Lock()
        self.excel_path = excel_path
        self.df = read_configs(excel_path)
        self.df.to_excel(excel_path, index=False)
        self.task_ids = queue.PriorityQueue()
        for id in self.get_task_ids():
            self.task_ids.put(id)

    def synchronized(func):
        def wrapper(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return wrapper

    def get_task_configs(self):
        return self.df[self.df['run_num']==0]

    def get_task_ids(self):
        todo_df = self.get_task_configs()
        return list(todo_df.index)
    
    # -------------------------------
    
    def get_task_dict(self):
        return self.get_task_configs().to_dict(orient='records')
    
    @synchronized
    def get_next_task(self) -> tuple[int, dict]:
        if self.task_ids.empty():
            return None, None
        id = self.task_ids.get()
        row = self.df.iloc[id]
        config_dict = row.drop('run_num').to_dict()
        logger.info(f"get task {id} config: {config_dict}")
        return id, config_dict
    
    @synchronized
    def put_task_ids(self, id):
        self.task_ids.put(id)
        logger.info(f"put task {id} back to queue")
        
    @synchronized
    def update_task_ids(self, id):
        self.df.loc[id, 'run_num'] += 1
        self.df.to_excel(self.excel_path, index=False)
        logger.info(f"update task {id} run times: {self.df.loc[id, 'run_num']}")

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
