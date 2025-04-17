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
import multiprocessing
import subprocess
import psutil

# os.system("ps aux | grep 'python' | grep -v grep | awk '{print $2}' | xargs -r kill -9")

    
class PopenProcess:
    def __init__(self, success_callback=None, error_callback=None):
        self.popen_process = None
        self.success_callback = success_callback
        self.error_callback = error_callback

    def success(self, *args, **kwargs):
        if self.success_callback:
            self.success_callback(*args, **kwargs)
            
    def error(self, *args, **kwargs):
        if self.error_callback:
            self.error_callback(*args, **kwargs)

    def fcb(self, cmd):
        signal.signal(signal.SIGTERM, self._handle_terminate)
        # self.popen_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.popen_process = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=True)
        try:
            self.popen_process.wait()
            stdout, stderr = self.popen_process.communicate()
            returncode = self.popen_process.returncode
            if returncode == 0:
                self.success()
            else:
                self.error(stderr)
        except Exception as e:
            self.error(e)

    def _handle_terminate(self, signum, frame):
        # print("process terminated", signum)
        proc_pid = self.popen_process.pid
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()


class Process:
    def __init__(self, cmd, backcall):
        self.manager = multiprocessing.Manager()
        self.shared_dict = self.manager.dict()
        self.shared_dict["status"] = "PENDING"
        self.backcall = backcall
        self.cmd = cmd
        self.process = self.run()
        
    def change_status(self, status):
        print(f"Process {self.cmd} status from {self.shared_dict['status']} to {status}")
        self.shared_dict["status"] = status
        self.backcall(status)
        
    def run(self):
        process = multiprocessing.Process(target=PopenProcess(self.on_completed, self.on_failed).fcb, args=(self.cmd,))
        process.start()
        self.change_status("RUNNING")
        return process
        
    def on_completed(self, result = None):
        print("completed", result)
        self.change_status("COMPLETED")
        
    def on_failed(self, error=None):
        print("failed", error)
        self.change_status("FAILED")
        
    def kill(self):
        self.process.terminate()
        self.process.join()
        self.change_status("KILLED")
        

class ProcessManager:
    def __init__(self, cmd):
        self.status = "PENDING"
        self.process = Process(cmd, self.backcall)
        
    def backcall(self, status):
        print(f"backcall: {self.status} to {status}")
        self.status = status
        
    def kill(self):
        self.process.kill()
        
def main():
        
    cmd_a = "CUDA_VISIBLE_DEVICES=4 python test.py --test a"
    cmd_b = "CUDA_VISIBLE_DEVICES=5 python test.py --test b"
    
    process_manager = ProcessManager(cmd_a)
    
    time.sleep(5)
    
    process_manager.kill()
    
    print("status", process_manager.status)

            
    
if __name__ == "__main__":
    main()
    
