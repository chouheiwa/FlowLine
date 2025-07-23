import os

class BaseConfig:
    # API_HOST = "127.0.0.1"
    # API_PORT = 5000
    DEFAULT_MIN_PROCESS_MEMORY = 10000 # MB
    DEFAULT_MAX_PROCESSES = 4
    DEBUG = False

class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    DEBUG = False

env = os.getenv("FLOWLINE_ENV", "dev")
# print(f"env: {env}")
if env == "prod":
    config = ProdConfig()
else:
    config = DevConfig()