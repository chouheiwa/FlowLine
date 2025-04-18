from flowline.api import get_app
from flask import send_from_directory, Flask, send_file
import os

def get_command(dict, gpu_id):
    return f"CUDA_VISIBLE_DEVICES={gpu_id} python test.py " + " ".join([f"--{key} {value}" for key, value in dict.items()])

def main():  # 前后端分离，前端使用python -m http.server 8000提供静态文件
    app = get_app(get_command)
    
    # 仅提供API，不提供静态文件
    # 前端静态文件需要通过单独的命令提供：
    # cd webpage && python -m http.server 8000
    
    app.run(host='0.0.0.0', port=5000, debug=True)

def main2():
    # TODO：集成式服务器，同时提供API和前端静态文件
    pass

if __name__ == '__main__':
    main()