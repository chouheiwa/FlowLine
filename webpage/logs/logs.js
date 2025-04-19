// 全局变量
let logFiles = [];
let currentLogFile = null;
let logContent = [];
let filteredContent = [];
let searchTerm = '';
let selectedLogLevel = 'all';
let maxLines = 1000;
let autoScroll = true;
let pollingInterval = null;

// DOM 元素
const logFilesEl = document.getElementById('logFiles');
const logContentEl = document.getElementById('logContent');
const currentLogTitleEl = document.getElementById('currentLogTitle');
const searchTermInput = document.getElementById('searchTerm');
const logLevelSelect = document.getElementById('logLevel');
const maxLinesInput = document.getElementById('maxLines');
const applyFilterBtn = document.getElementById('applyFilterBtn');
const refreshBtn = document.getElementById('refreshBtn');
const downloadBtn = document.getElementById('downloadBtn');
const clearLogBtn = document.getElementById('clearLogBtn');
const autoScrollCheckbox = document.getElementById('autoScrollCheckbox');
const toast = document.getElementById('toast');
const toastMessage = document.querySelector('.toast-message');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 加载日志文件列表
    loadLogFiles();
    
    // 绑定事件
    bindEvents();
});

// 绑定事件处理函数
function bindEvents() {
    // 日志文件选择
    logFilesEl.addEventListener('click', (e) => {
        const logFileCard = e.target.closest('.log-file-card');
        if (logFileCard) {
            const logFileName = logFileCard.dataset.filename;
            selectLogFile(logFileName);
        }
    });
    
    // 应用筛选按钮
    applyFilterBtn.addEventListener('click', () => {
        applyFilters();
    });
    
    // 回车键应用筛选
    searchTermInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
            applyFilters();
        }
    });
    
    // 刷新按钮
    refreshBtn.addEventListener('click', () => {
        loadLogFiles();
        if (currentLogFile) {
            loadLogContent(currentLogFile);
        }
        showToast('日志已刷新');
    });
    
    // 下载按钮
    downloadBtn.addEventListener('click', () => {
        if (currentLogFile) {
            downloadLog(currentLogFile);
        }
    });
    
    // 清空日志按钮
    clearLogBtn.addEventListener('click', () => {
        if (currentLogFile) {
            clearLog(currentLogFile);
        }
    });
    
    // 自动滚动复选框
    autoScrollCheckbox.addEventListener('change', () => {
        autoScroll = autoScrollCheckbox.checked;
        if (autoScroll && logContentEl.scrollHeight > 0) {
            scrollToBottom();
        }
    });
}

// 加载日志文件列表
function loadLogFiles() {
    // 模拟API请求获取日志文件列表
    setTimeout(() => {
        // 这里应该是实际的API调用
        // fetch('/api/logs').then(response => response.json()).then(data => {...})
        
        // 使用实际的日志文件作为示例数据
        logFiles = [
            { 
                name: 'flowline.gpu.log',
                fullPath: '/home/me/flowline/flowline/log/flowline.gpu.log',
                size: '512KB',
                type: 'gpu',
                lastModified: '2023-08-18 14:32:15'
            },
            { 
                name: 'flowline.api.log',
                fullPath: '/home/me/flowline/flowline/log/flowline.api.log',
                size: '1.2KB',
                type: 'api',
                lastModified: '2023-08-18 14:30:22'
            },
            { 
                name: 'flowline.todo.log',
                fullPath: '/home/me/flowline/flowline/log/flowline.todo.log',
                size: '1.9KB',
                type: 'todo',
                lastModified: '2023-08-18 14:28:45'
            },
            { 
                name: 'flowline.process.log',
                fullPath: '/home/me/flowline/flowline/log/flowline.process.log',
                size: '2.3KB',
                type: 'process',
                lastModified: '2023-08-18 14:27:10'
            },
            { 
                name: 'flowline.utils.log',
                fullPath: '/home/me/flowline/flowline/log/flowline.utils.log',
                size: '370B',
                type: 'utils',
                lastModified: '2023-08-18 14:25:30'
            },
            { 
                name: 'flowline.program.log',
                fullPath: '/home/me/flowline/flowline/log/flowline.program.log',
                size: '212B',
                type: 'program',
                lastModified: '2023-08-18 14:24:15'
            }
        ];
        
        renderLogFiles();
    }, 300);
}

// 渲染日志文件列表
function renderLogFiles() {
    // 清空日志文件列表
    logFilesEl.innerHTML = '';
    
    // 渲染日志文件卡片
    logFiles.forEach(logFile => {
        const logFileCard = document.createElement('div');
        logFileCard.className = 'log-file-card';
        logFileCard.dataset.filename = logFile.name;
        
        if (currentLogFile && currentLogFile === logFile.name) {
            logFileCard.classList.add('selected');
        }
        
        logFileCard.innerHTML = `
            <div class="log-file-indicator ${logFile.type}"></div>
            <div class="log-file-name">${logFile.name}</div>
            <div class="log-file-size">${logFile.size}</div>
        `;
        
        logFilesEl.appendChild(logFileCard);
    });
}

// 选择日志文件
function selectLogFile(logFileName) {
    // 如果选择的是当前已选择的文件，不做任何操作
    if (currentLogFile === logFileName) return;
    
    // 更新当前选择的日志文件
    currentLogFile = logFileName;
    
    // 更新UI状态
    const logFileCards = logFilesEl.querySelectorAll('.log-file-card');
    logFileCards.forEach(card => {
        card.classList.toggle('selected', card.dataset.filename === logFileName);
    });
    
    // 更新标题
    currentLogTitleEl.textContent = `日志文件: ${logFileName}`;
    
    // 启用相关按钮
    downloadBtn.disabled = false;
    clearLogBtn.disabled = false;
    
    // 加载日志内容
    loadLogContent(logFileName);
    
    // 启动轮询
    startPolling(logFileName);
}

// 加载日志内容
function loadLogContent(logFileName) {
    // 显示加载状态
    logContentEl.innerHTML = '<div class="empty-log-state">正在加载日志内容...</div>';
    
    // 模拟API请求获取日志内容
    setTimeout(() => {
        // 这里应该是实际的API调用
        // fetch(`/api/logs/${logFileName}?maxLines=${maxLines}`).then(response => response.json()).then(data => {...})
        
        // 模拟生成日志内容
        logContent = generateMockLogContent(logFileName, maxLines);
        
        // 应用过滤器并渲染日志内容
        applyFilters();
    }, 500);
}

// 生成模拟日志内容
function generateMockLogContent(logFileName, lines) {
    const mockContent = [];
    const logTypes = ['INFO', 'WARNING', 'ERROR', 'DEBUG'];
    const timestamp = new Date();
    
    // 根据不同的日志文件生成不同的内容
    let logMessages = [];
    
    if (logFileName === 'flowline.gpu.log') {
        logMessages = [
            'GPU状态检查：RTX 4090 - 温度: 65°C, 使用率: 78%, 内存使用: 8.2GB/24GB',
            'GPU状态检查：RTX 3080 - 温度: 72°C, 使用率: 92%, 内存使用: 9.6GB/10GB',
            '启动GPU监控服务，间隔: 5秒',
            '检测到GPU温度过高: RTX 3080 - 温度: 85°C, 启动降频',
            'GPU状态更新：RTX 4090 - 分配给任务ID: task_001',
            'GPU状态更新：RTX 3080 - 分配给任务ID: task_002',
            'GPU利用率异常低: RTX 4090 - 使用率仅为12%，可能存在性能瓶颈',
            'GPU内存溢出: RTX 3080 - 请求分配12GB内存，但仅有10GB容量',
            'GPU驱动程序版本: 528.49, CUDA版本: 12.1'
        ];
    } else if (logFileName === 'flowline.api.log') {
        logMessages = [
            'API服务启动，监听端口: 5000',
            'HTTP请求: GET /api/tasks, 状态码: 200, 响应时间: 128ms',
            'HTTP请求: POST /api/tasks, 状态码: 201, 响应时间: 215ms',
            'HTTP请求: GET /api/gpus, 状态码: 200, 响应时间: 87ms',
            'API错误: 请求 DELETE /api/tasks/invalid_id 返回状态码 404 - 任务不存在',
            'API调用频率过高: IP 192.168.1.5 在5分钟内发送了超过100次请求',
            'HTTP请求: PUT /api/gpus/gpu_001, 状态码: 200, 响应时间: 156ms',
            '身份验证失败: 无效的令牌访问 /api/admin/settings'
        ];
    } else if (logFileName === 'flowline.todo.log') {
        logMessages = [
            '创建任务: task_001 - 样例训练任务',
            '任务状态更新: task_001 从 pending 变为 running',
            '任务进度更新: task_001 进度: 45%',
            '创建任务: task_002 - 图像分类任务',
            '任务状态更新: task_002 从 pending 变为 running',
            '任务状态更新: task_002 从 running 变为 completed',
            '创建任务: task_003 - 数据处理任务',
            '任务状态更新: task_003 从 pending 变为 running',
            '任务错误: task_003 失败，错误信息: 内存不足',
            '任务状态更新: task_003 从 running 变为 failed',
            '创建任务: task_004 - 模型评估',
            '创建任务: task_005 - 已终止任务',
            '任务状态更新: task_005 从 pending 变为 running',
            '任务状态更新: task_005 从 running 变为 killed'
        ];
    } else if (logFileName === 'flowline.process.log') {
        logMessages = [
            '进程启动: PID 12345 - 命令: python train.py --model resnet50 --epochs 100',
            '进程启动: PID 12346 - 命令: python classify.py --input images/ --output results/',
            '进程启动: PID 12347 - 命令: python preprocess.py --data raw_data/ --clean',
            '进程终止: PID 12347 - 退出码: 1, 信号: SIGSEGV (段错误)',
            '进程启动: PID 12348 - 命令: python evaluate.py --model model.pth --test test_data/',
            '进程启动: PID 12349 - 命令: python long_process.py',
            '进程终止: PID 12349 - 退出码: 0, 信号: SIGTERM (终止请求)',
            '进程内存使用超出限制: PID 12345 使用了 8.5GB 内存，超出了限制的 8GB',
            '进程CPU使用率过高: PID 12348 持续使用超过95%的CPU时间',
            '系统负载过高: 当前负载平均值为 8.75，可能影响其他任务'
        ];
    } else if (logFileName === 'flowline.utils.log') {
        logMessages = [
            '配置文件加载成功: config.yaml',
            '清理临时文件: 删除了5个过期的临时文件',
            '磁盘空间警告: 剩余空间不足20GB',
            '数据库连接池初始化: 最大连接数 10',
            '缓存刷新: 清除了超过24小时的缓存数据'
        ];
    } else if (logFileName === 'flowline.program.log') {
        logMessages = [
            'FlowLine 服务启动, 版本: 1.2.3',
            '加载模块: GPU, API, Todo, Process, Utils',
            '服务就绪，运行时间: 0天 0小时 0分钟 5秒',
            '系统信息: Linux 5.15.0-52-generic, CPU: 16核, 内存: 64GB',
            '注册信号处理程序: SIGINT, SIGTERM'
        ];
    }
    
    // 生成随机日志内容
    for (let i = 0; i < lines; i++) {
        const logType = logTypes[Math.floor(Math.random() * logTypes.length)];
        const messageIndex = Math.floor(Math.random() * logMessages.length);
        const message = logMessages[messageIndex];
        
        // 创建一个过去的时间戳，随机减少一些秒数
        const pastTimestamp = new Date(timestamp);
        pastTimestamp.setSeconds(pastTimestamp.getSeconds() - (lines - i));
        
        mockContent.push({
            timestamp: formatTimestamp(pastTimestamp),
            level: logType,
            message: message
        });
    }
    
    return mockContent;
}

// 格式化时间戳
function formatTimestamp(date) {
    const pad = (num) => (num < 10 ? '0' + num : num);
    
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

// 应用过滤器
function applyFilters() {
    // 获取过滤值
    searchTerm = searchTermInput.value.trim().toLowerCase();
    selectedLogLevel = logLevelSelect.value;
    maxLines = parseInt(maxLinesInput.value, 10) || 1000;
    
    // 应用过滤
    filteredContent = logContent.filter(log => {
        // 先过滤日志级别
        if (selectedLogLevel !== 'all' && log.level.toLowerCase() !== selectedLogLevel) {
            return false;
        }
        
        // 再过滤搜索词
        if (searchTerm && !log.message.toLowerCase().includes(searchTerm) && !log.level.toLowerCase().includes(searchTerm)) {
            return false;
        }
        
        return true;
    });
    
    // 限制显示行数
    if (filteredContent.length > maxLines) {
        filteredContent = filteredContent.slice(-maxLines);
    }
    
    // 渲染过滤后的日志内容
    renderLogContent();
    
    // 显示提示
    showToast('筛选已应用');
}

// 渲染日志内容
function renderLogContent() {
    // 如果没有选择日志文件或没有日志内容，显示空状态
    if (!currentLogFile || filteredContent.length === 0) {
        logContentEl.innerHTML = '<div class="empty-log-state">没有匹配的日志内容</div>';
        return;
    }
    
    // 清空日志内容
    logContentEl.innerHTML = '';
    
    // 渲染日志行
    filteredContent.forEach(log => {
        const logLine = document.createElement('div');
        logLine.className = `log-line ${log.level.toLowerCase()}`;
        
        // 格式化日志行
        let logMessage = log.message;
        
        // 高亮搜索词
        if (searchTerm) {
            const regex = new RegExp(`(${searchTerm})`, 'gi');
            logMessage = logMessage.replace(regex, '<span class="log-highlight">$1</span>');
        }
        
        logLine.innerHTML = `<span class="log-timestamp">${log.timestamp}</span><span class="log-level">[${log.level}]</span> ${logMessage}`;
        
        logContentEl.appendChild(logLine);
    });
    
    // 如果启用了自动滚动，滚动到底部
    if (autoScroll) {
        scrollToBottom();
    }
}

// 滚动到底部
function scrollToBottom() {
    logContentEl.scrollTop = logContentEl.scrollHeight;
}

// 启动轮询更新
function startPolling(logFileName) {
    // 先清除现有的轮询
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
    
    // 每5秒钟轮询一次日志更新
    pollingInterval = setInterval(() => {
        if (currentLogFile === logFileName) {
            // 模拟日志更新
            appendNewLogs();
        } else {
            // 如果当前日志文件改变了，停止轮询
            clearInterval(pollingInterval);
        }
    }, 5000);
}

// 追加新日志
function appendNewLogs() {
    // 实际应用中，这里应该是从服务器获取新的日志
    // 模拟添加1-3条新日志
    const newLogsCount = Math.floor(Math.random() * 3) + 1;
    const newLogs = generateMockLogContent(currentLogFile, newLogsCount);
    
    // 添加到现有日志
    logContent = [...logContent, ...newLogs];
    
    // 限制总日志行数
    if (logContent.length > 5000) {
        logContent = logContent.slice(-5000);
    }
    
    // 重新应用过滤器
    applyFilters();
}

// 下载日志
function downloadLog(logFileName) {
    // 实际应用中，这里应该直接提供一个API端点来下载日志文件
    // 模拟下载
    const logText = filteredContent.map(log => 
        `${log.timestamp} [${log.level}] ${log.message}`
    ).join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = logFileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('日志文件已下载');
}

// 清空日志
function clearLog(logFileName) {
    // 实际应用中，这里应该调用API来清空日志文件
    // 模拟清空日志
    logContent = [];
    filteredContent = [];
    
    // 更新UI
    renderLogContent();
    
    showToast(`日志文件 ${logFileName} 已清空`);
}

// 显示消息提示
function showToast(message) {
    toastMessage.textContent = message;
    toast.classList.add('show');
    
    // 3秒后自动隐藏
    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('hide');
        
        // 动画结束后移除hide类
        setTimeout(() => {
            toast.classList.remove('hide');
        }, 300);
    }, 3000);
} 