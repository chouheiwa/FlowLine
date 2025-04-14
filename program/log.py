import logging
import os

class Log:
    def __init__(self, name):
        self.name = name
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        logging.basicConfig(level=logging.INFO, handlers=[logging.NullHandler()])
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not os.path.exists(os.path.join(self.current_path, 'log')):
            os.makedirs(os.path.join(self.current_path, 'log'))
        file_handler = logging.FileHandler(os.path.join(self.current_path, 'log', f'{name}.log'))
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
        
        
        


