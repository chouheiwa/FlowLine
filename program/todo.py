from tqdm import tqdm
import pandas as pd
import os
import threading
import queue  # 导入标准库的queue模块

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

def read_configs():
    """
    Read the configuration parameters from the Excel file.
    """
    df = pd.read_excel(todo_excel_path)
    return df


def priority_sort(df):
    sorted_df = df.sort_values(
        by=['run_num', 'domain_num', 'data_name', 'model_name', 'method_name'],
        ascending=[True, True, True, True, True]
    )
    return sorted_df


class TodoManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.df = read_configs()
        self.todo_ids = queue.PriorityQueue()
        for id in self.get_todo_ids():
            self.todo_ids.put(id)
        
    def synchronized(func):
        def wrapper(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return wrapper

    def get_todo_configs(self):
        return self.df[self.df['run_num']==0]

    def get_todo_ids(self):
        todo_df = self.get_todo_configs()
        # sorted_df = priority_sort(todo_df)
        return list(todo_df.index)
    
    # -------------------------------
    
    @synchronized
    def get_next_todo(self) -> tuple[int, dict]:  
        id = self.todo_ids.get()
        if self.todo_ids.empty():
            return None, None
        row = self.df.iloc[id]
        config_dict = row.drop('run_num').to_dict()
        return id, config_dict
    
    @synchronized
    def put_todo_ids(self, id):
        self.todo_ids.put(id)
    
    @synchronized
    def update_todo_ids(self, id):
        self.df.loc[id, 'run_num'] += 1
        self.df.to_excel(todo_excel_path, index=False)
        
    def get(self):
        return self.get_next_todo()
        
    def put(self, id):
        return self.put_todo_ids(id)
        
    def update(self, id):
        return self.update_todo_ids(id)

# todo_manager = TodoManager()

if __name__ == "__main__":
    process_configs()
    # print(2)
    # todo = Todo()
    
    # print(1)
    # while True:
    #     print("--------------------------------")
    #     id, config = todo.get()
    #     print(id)
    #     print(config)
    #     todo.put(id)
    #     print("--------------------------------")
    
