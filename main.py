from flowline.core import run_cli

if __name__ == "__main__":
    def func(dict, gpu_id):
        return "CUDA_VISIBLE_DEVICES="+str(gpu_id)+" python -u test.py "+ " ".join([f"--{k}={v}" for k, v in dict.items()])
    
    run_cli(func, "todo.xlsx")
    
# pkill -9 python