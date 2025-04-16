class FunctionCall:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def __call__(self):
        return self.func(*self.args, **self.kwargs)
    
    def __str__(self):
        return f"{self.func.__name__}({self.args}, {self.kwargs})"
    
class FunctionCallBack:
    def __init__(self, fc: FunctionCall, success_callback=None, error_callback=None):
        self.fc = fc
        self.success_callback = success_callback
        self.error_callback = error_callback
        
    def success(self, result):
        if self.success_callback:
            self.success_callback(result)
            
    def error(self, error):
        if self.error_callback:
            self.error_callback(error)
            
    def __call__(self):
        try:
            result = self.fc()
            self.success(result)
        except Exception as e:
            self.error(e)
        
if __name__ == "__main__":
    import time
    import threading
    import multiprocessing
    import torch
    import ctypes


    mark = True
    
    def test_func(k):
        tensor = torch.randn(1000, 1000).to("cuda:" + str(k))

        i = 0
        while mark:
            print(i)
            i += 1
            if i > 10:
                raise Exception("test exception")
            time.sleep(1)
            
    def success_callback(result):
        print(f"进程成功完成，结果为: {result}")

    def error_callback(error):
        print(f"进程出错: {error}")
            
    fc1 = FunctionCall(test_func, 4)
    fc2 = FunctionCall(test_func, 5)
    
    fcb1 = FunctionCallBack(fc1, success_callback=success_callback, error_callback=error_callback)  
    fcb2 = FunctionCallBack(fc2, success_callback=success_callback, error_callback=error_callback)
    
    p1 = multiprocessing.Process(target=fcb1)
    p2 = multiprocessing.Process(target=fcb2)
    
    p1.start()
    time.sleep(2)
    p2.start()
    print(p1.pid)
    print(p2.pid)
    
    time.sleep(2)
    p1.terminate()
    time.sleep(2)
    print(p1.is_alive())
    print(p2.is_alive())
    
    while True:
        print(time.time())
        time.sleep(1)
    
    
    
    
