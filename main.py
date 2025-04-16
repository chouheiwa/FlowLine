from flowline.interface import run_cli
import time

if __name__ == "__main__":
    def func(dict, gpu_id):
        while True:
            print(dict, gpu_id)
            time.sleep(1)
    run_cli(func)