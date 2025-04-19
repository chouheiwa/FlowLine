from flowline.interface import run_cli
import time

if __name__ == "__main__":
    def func(dict, gpu_id):
        return "CUDA_VISIBLE_DEVICES="+str(gpu_id)+" python test.py "+ " ".join([f"--{k}={v}" for k, v in dict.items()])
    
    run_cli(func, todo_dir="todo.xlsx")
    
# pkill -9 python