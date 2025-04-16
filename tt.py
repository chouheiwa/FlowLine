import os
import threading
import subprocess
import time
import psutil
import atexit
import signal
import sys
import datetime
import torch

# os.system("ps aux | grep 'python' | grep -v grep | awk '{print $2}' | xargs -r kill -9")



import multiprocessing
import subprocess

def run_command(command):
    # 设置stdout参数为subprocess.PIPE
    completed_process = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr, shell=True)
    # 读取子进程的stdout
    # output = completed_process.communicate()[0]
    # error = completed_process.communicate()[1]
    
def main():
    
    cmd_a = "CUDA_VISIBLE_DEVICES=5 python test.py --test a"
    cmd_b = "CUDA_VISIBLE_DEVICES=5 python test.py --test b"
    
    process1 = multiprocessing.Process(
        target=run_command,
        args=(cmd_a,),
    )
    process2 = multiprocessing.Process(
        target=run_command,
        args=(cmd_b,),
    )
    process1.start()
    process2.start()
    
    time.sleep(4)
    
    process1.terminate()
    
    time.sleep(5)
    
if __name__ == "__main__":
    main()