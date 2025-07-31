from .log import Log

import signal
import psutil
import subprocess
import os

logger = Log(__name__)

        
class PopenProcess:
    def __init__(self, result_queue, process_id):
        self.process_id = process_id
        self.result_queue = result_queue
        self.popen_process = None

    def fcb(self, cmd):
        try:
            signal.signal(signal.SIGTERM, self._handle_terminate)
            
            stdout_file = f"log/{self.process_id}.out"
            stderr_file = f"log/{self.process_id}.err"
            if not os.path.exists("log"):
                os.makedirs("log")
            
            with open(stdout_file, 'w', encoding='utf-8') as stdout_f, \
                 open(stderr_file, 'w', encoding='utf-8') as stderr_f:
                self.popen_process = subprocess.Popen(
                    cmd,
                    stdout=stdout_f,
                    stderr=stderr_f,
                    shell=True,
                )
                self.popen_process.wait()
            
            _, stderr = self.popen_process.communicate()
            returncode = self.popen_process.returncode
            logger.info(f"Process {self.process_id} finished with return code {returncode}")
            if returncode == 0:
                self.result_queue.put((True, None))
            else:
                self.result_queue.put((False, stderr))
        except Exception as e:
            logger.error(f"Process {self.process_id} failed: {e}")
            self.result_queue.put((False, str(e)))

    def _handle_terminate(self, signum, frame):
        # print("process terminated", signum)
        proc_pid = self.popen_process.pid
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
        
if __name__ == "__main__":
    import multiprocessing
    import time
        
    result_queue = multiprocessing.Queue()

    cmd_a = "CUDA_VISIBLE_DEVICES=4 python test.py --test a"
    cmd_b = "CUDA_VISIBLE_DEVICES=5 python -u test.py --test b"
    
    proc_a = multiprocessing.Process(target=PopenProcess(result_queue, 0).fcb, args=(cmd_a,))
    proc_b = multiprocessing.Process(target=PopenProcess(result_queue, 1).fcb, args=(cmd_b,))
    
    proc_a.start()
    proc_b.start()
    
    time.sleep(3)
    
    while True:
        time.sleep(1)
        if proc_a.is_alive():
            print("proc_a is alive")
        else:
            print("proc_a is dead")
        if proc_b.is_alive():
            print("proc_b is alive")
        else:
            print("proc_b is dead")
        if result_queue.empty():
            print("result_queue is empty")
        else:
            print("result_queue is not empty")
