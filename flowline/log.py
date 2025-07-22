import logging
import os

class Log:
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(self.current_path, 'log')
        
        # 尝试创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 尝试创建文件处理器
        file_handler = logging.FileHandler(os.path.join(log_dir, f'{name}.log'))
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
 
        
    def info(self, message):
        self.logger.info(message)
        
    def debug(self, message):
        self.logger.debug(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def error(self, message):
        self.logger.error(message)
        
        
        


