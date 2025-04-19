from flowline.api_test import get_app
from flask import send_from_directory, Flask, send_file, request, abort
from flask_cors import CORS  # 添加CORS支持
import os
import logging

def func(dict, gpu_id):
    return "CUDA_VISIBLE_DEVICES="+str(gpu_id)+" python test.py "+ " ".join([f"--{k}={v}" for k, v in dict.items()])

def main():  # 前后端分离，前端使用python -m http.server 8000提供静态文件
    app = get_app(func)
    # 添加CORS支持，允许前端从不同端口访问API
    CORS(app)
    
    # 仅提供API，不提供静态文件
    # 前端静态文件需要通过单独的命令提供：
    # cd webpage && python -m http.server 8000
    
    app.run(host='0.0.0.0', port=5000, debug=True)

def main2():
    # TODO: 集成式服务器，同时提供API和前端静态文件
    pass

if __name__ == '__main__':
    main()  # 注释掉分离式服务器
    # main2()   # 使用集成式服务器