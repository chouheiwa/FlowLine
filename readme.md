# FlowLine

FlowLine是一个GPU任务管理和监控系统，提供命令行和Web界面，能够帮助管理和调度任务，监控GPU状态。

## 功能特点

- 实时监控多个GPU的使用状态（内存、利用率等）
- 自动分配任务到最合适的GPU
- 可视化GPU和任务状态
- 支持任务的启动、终止和调度
- 支持Web界面和命令行界面

## 系统架构

系统由以下部分组成：

1. **后端 (flowline/)**：
   - GPU管理模块：监控和管理GPU状态
   - 进程管理模块：创建、监控和终止进程
   - 任务队列模块：管理待执行的任务
   - API服务：为Web前端提供数据接口

2. **前端 (webpage/)**：
   - HTML/CSS/JavaScript实现的Web界面
   - 实时数据可视化
   - 用户交互操作

## 安装与配置

### 前提条件

- Python 3.6+
- **NVIDIA GPU + CUDA驱动**
- 现代Web浏览器

### 安装步骤

1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/flowline.git
   cd flowline
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

## 使用方法

### 启动API服务器

后端是一个 Flask 应用，您需要运行 server.py 文件来启动它：

```
cd ~/flowline && python server.py
```

使用 Python 的内置 HTTP 服务器来提供前端文件：

```
cd ~/flowline/webpage && python -m http.server 8000
```

这会在 http://localhost:8000 上启动一个简单的 HTTP 服务器，提供前端 HTML、CSS 和 JavaScript 文件。

然后访问 http://localhost:8000

### 使用命令行接口

```
python main.py
```

## API文档

### GPU相关

- `GET /api/gpus` - 获取所有GPU状态
- `POST /api/gpu/<gpu_id>/switch` - 切换GPU可用状态

### 任务相关

- `GET /api/processes` - 获取所有进程
- `GET /api/gpu/<gpu_id>/tasks` - 获取特定GPU上的任务
- `POST /api/task/<task_id>/kill` - 终止特定任务

### 控制相关

- `POST /api/control/start` - 启动处理循环
- `POST /api/control/stop` - 停止处理循环
- `GET /api/control/status` - 获取当前状态

## 界面操作指南

- 点击GPU卡片查看详情和任务
- 右键点击GPU卡片切换GPU可用状态
- 点击任务的"终止"按钮停止正在运行的任务
- 点击"刷新"按钮手动更新数据

## 许可证

MIT

