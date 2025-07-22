from tqdm import tqdm
import pandas as pd
import os
import threading
import queue
from .log import Log

logger = Log(__name__)

current_path = os.path.dirname(os.path.abspath(__file__))
todo_excel_path = os.path.join(current_path, "todo.xlsx")

def config_generator():
    """
    A generator function that yields configuration parameters.
    """
    configs = {
        "data_name": ["rotate_mnist", "color_mnist", "portraits"],
        "model_name": ["cnn", "vgg", "resnet"],
        "method_name": ["GST", "GOAT", "GDO", "GAS"],
        "domain_num": [2, 3, 4, 5, 6],
        "seed": [1, 2, 3, 4, 5]
    }

    for data_name in configs["data_name"]:
        for model_name in configs["model_name"]:
            for method_name in configs["method_name"]:
                for domain_num in configs["domain_num"]:
                    for seed in configs["seed"]:
                        yield {
                            "data_name": data_name,
                            "model_name": model_name,
                            "method_name": method_name,
                            "domain_num": domain_num,
                            "seed": seed
                        }
    
def process_configs():
    """
    Process the configuration parameters using the generator and store them in an Excel file.
    """
    # Create DataFrame from generator
    configs = list(config_generator())
    df = pd.DataFrame(configs)
    
    # Add 'is_run' column initialized to False
    df['run_num'] = 0
    
    # Save to Excel if file doesn't exist, otherwise load and update
    if os.path.exists(todo_excel_path):
        existing_df = pd.read_excel(todo_excel_path)
        df = df.merge(existing_df[['data_name', 'model_name', 'method_name', 'domain_num', 'seed', 'run_num']], 
                      on=['data_name', 'model_name', 'method_name', 'domain_num', 'seed', 'run_num'], 
                      how='left')
        # print(df)
        df['run_num'] = df['run_num'].fillna(0)
    
    # Save to Excel
    df.to_excel(todo_excel_path, index=False)
    
    # Process only unrun configurations
    for config in tqdm(configs):
        if not df[(df['data_name'] == config['data_name']) & 
                  (df['model_name'] == config['model_name']) & 
                  (df['method_name'] == config['method_name']) & 
                  (df['domain_num'] == config['domain_num']) & 
                  (df['seed'] == config['seed'])]['run_num'].iloc[0]:
            df.loc[(df['data_name'] == config['data_name']) & 
                   (df['model_name'] == config['model_name']) & 
                   (df['method_name'] == config['method_name']) & 
                   (df['domain_num'] == config['domain_num']) & 
                   (df['seed'] == config['seed']), 'run_num'] = 0
    
    df.to_excel(todo_excel_path, index=False)


# -------------------------------

def read_configs(excel_path):
    """
    Read the configuration parameters from the Excel file.
    """
    logger.info(f"读取配置文件: {excel_path}")
    df = pd.read_excel(excel_path)
    return df


class TaskManager:
    def __init__(self, excel_path=todo_excel_path):
        excel_path = excel_path if excel_path else todo_excel_path
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
        logger.info(f"获取任务 {id} 配置: {config_dict}")
        return id, config_dict
    
    @synchronized
    def put_task_ids(self, id):
        self.task_ids.put(id)
        logger.info(f"任务 {id} 重新入队")
        
    @synchronized
    def update_task_ids(self, id):
        self.df.loc[id, 'run_num'] += 1
        self.df.to_excel(self.excel_path, index=False)
        logger.info(f"更新任务 {id} 运行次数: {self.df.loc[id, 'run_num']}")

# task_manager = TaskManager()

if __name__ == "__main__":
    process_configs()
    # print(2)
    # task = TaskManager()
    # print(task.get_next_task())
    # print(task.get_next_task())
    # task.update_task_ids(0)
    # print(todo.get_next_todo())
    
    """
    python -m flowline.todo
    """
