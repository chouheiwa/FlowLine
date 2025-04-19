// API URL - 需要根据实际部署环境修改
// const API_BASE_URL = '/api';
const API_BASE_URL = 'http://localhost:5000/api';

// 用于存储数据的变量
let gpuData = [];
let taskData = [];

// 设置刷新按钮点击事件
document.getElementById('refreshBtn').addEventListener('click', function(e) {
    // 防止页面刷新
    e.preventDefault();
    console.log("刷新按钮被点击");
    fetchData();
});

// 设置清空按钮点击事件
document.getElementById('clearBtn').addEventListener('click', clearCompletedTasks);

// 初始化页面 - 移除这里的直接调用
fetchData(); 

// 在 DOMContentLoaded 事件中初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log("页面已加载，开始初始化...");
    // 初始加载数据
    fetchData();
    
    // 设置周期性更新，降低频率（改为30秒一次）
    setInterval(fetchData, 30000);
});

// 获取所有数据
async function fetchData() {
    try {
        console.log("开始获取数据...");
        
        // 获取GPU数据
        await fetchGpuData();
        console.log("GPU数据:", gpuData);
        
        // 获取进程数据
        await fetchProcessData();
        console.log("进程数据:", taskData);
        
        // 渲染页面
        await renderUI();
        console.log("UI渲染完成");
    } catch (error) {
        console.error('获取数据失败:', error);
        // 在页面上显示错误信息
        document.getElementById('gpuList').innerHTML = `<div class="error-message">获取数据失败: ${error.message}</div>`;
    }
}

// 获取GPU数据
async function fetchGpuData() {
    try {
        console.log(`正在请求: ${API_BASE_URL}/gpus`);
        const response = await fetch(`${API_BASE_URL}/gpus`);
        console.log('GPU数据响应状态:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const gpuObject = await response.json();
        
        // 处理新的API格式：把对象中的GPU数据转换为数组
        gpuData = [];
        for (const gpu_id in gpuObject) {
            if (gpuObject.hasOwnProperty(gpu_id)) {
                const gpu = gpuObject[gpu_id];
                // 添加GPU ID到数据中
                gpuData.push({
                    gpu_id: gpu_id,
                    name: gpu.name,
                    status: gpu.status,
                    memory: {
                        used: ((gpu.total_memory - gpu.free_memory) / 1024).toFixed(1),
                        free: (gpu.free_memory / 1024).toFixed(1),
                        total: (gpu.total_memory / 1024).toFixed(1)
                    },
                    utilization: gpu.utilization,
                    temperature: gpu.temperature,
                    power: {
                        current: gpu.power,
                        max: gpu.max_power
                    }
                });
            }
        }
        
        return gpuData;
    } catch (error) {
        console.error('获取GPU数据失败:', error);
        throw error;
    }
}

// 获取进程数据
async function fetchProcessData() {
    try {
        // 使用正确的API端点
        const response = await fetch(`${API_BASE_URL}/process`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const processObject = await response.json();
        
        // 处理新的API格式：把对象中的进程数据转换为数组
        taskData = [];
        for (const process_id in processObject) {
            if (processObject.hasOwnProperty(process_id)) {
                const process = processObject[process_id];
                // 创建当前日期时间用于计算运行时间
                const now = new Date();
                // 使用API提供的启动时间
                const startTime = process.start_time ? new Date(process.start_time * 1000) : new Date();
                const runTime = Math.floor((now - startTime) / 60000); // 分钟
                
                taskData.push({
                    process_id: process_id,
                    todo_id: process.todo_id,
                    status: process.status.toLowerCase(),
                    gpu_id: process.gpu_id.toString(),
                    user: "user", // 假设API没有提供用户信息
                    command: process.func,
                    startTime: startTime.toLocaleString(),
                    runTime: `${runTime} 分钟`
                });
            }
        }
        
        return taskData;
    } catch (error) {
        console.error('获取进程数据失败:', error);
        throw error;
    }
}

// 获取特定GPU上的任务
async function fetchGpuTasks(gpu_id) {
    try {
        const response = await fetch(`${API_BASE_URL}/gpu/${gpu_id}/process`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const taskObject = await response.json();
        
        // 处理新的API格式：把对象中的任务数据转换为数组
        const tasks = [];
        for (const task_id in taskObject) {
            if (taskObject.hasOwnProperty(task_id)) {
                const task = taskObject[task_id];
                // 创建当前日期时间用于计算运行时间
                const now = new Date();
                // 使用API提供的启动时间，如果有的话
                const startTime = task.start_time ? new Date(task.start_time * 1000) : new Date();
                const runTime = Math.floor((now - startTime) / 60000); // 分钟
                
                tasks.push({
                    process_id: task_id,
                    todo_id: task.todo_id,
                    status: task.status.toLowerCase(),
                    gpu_id: task.gpu_id.toString(),
                    user: "user", // 假设API没有提供用户信息
                    command: task.func,
                    startTime: startTime.toLocaleString(),
                    runTime: `${runTime} 分钟`
                });
            }
        }
        
        return tasks;
    } catch (error) {
        console.error(`获取GPU ${gpu_id} 的任务失败:`, error);
        return [];
    }
}

// 终止任务
async function killTask(process_id) {
    try {
        const response = await fetch(`${API_BASE_URL}/process/${process_id}/kill`, {
            method: 'POST',
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        return result.success;
    } catch (error) {
        console.error(`终止任务 ${process_id} 失败:`, error);
        return false;
    }
}

// 切换GPU状态
async function switchGpu(gpu_id) {
    try {
        const response = await fetch(`${API_BASE_URL}/gpu/${gpu_id}/switch`, {
            method: 'POST',
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        return result.is_on;
    } catch (error) {
        console.error(`切换GPU ${gpu_id} 状态失败:`, error);
        return null;
    }
}

// 清空已完成的任务（示例函数，实际API需要实现）
async function clearCompletedTasks() {
    alert('此功能需要后端API支持');
    // 实际应用中，这里会调用后端API
    // 暂时仅触发刷新数据
    fetchData();
}

// 渲染整个UI
async function renderUI() {
    renderGpuList();
    
    // 如果有GPU，则渲染第一个GPU的详情和任务
    if (gpuData.length > 0) {
        const selectedGpu = document.querySelector('.gpu-card.selected');
        const selectedGpuId = selectedGpu ? selectedGpu.dataset.gpu_id : gpuData[0].gpu_id;
        
        const gpu = gpuData.find(g => g.gpu_id === selectedGpuId) || gpuData[0];
        renderGpuDetails(gpu);
        await renderActiveTasks(gpu.gpu_id);
    }
    
    renderProcessTable();
}

// 渲染GPU列表
function renderGpuList() {
    console.log("开始渲染GPU列表...");
    const gpuListEl = document.querySelector('.gpu-list');
    if (!gpuListEl) {
        console.error("找不到GPU列表元素！");
        return;
    }
    
    gpuListEl.innerHTML = '';
    
    // 检查gpuData是否为空
    if (!gpuData || gpuData.length === 0) {
        console.warn("没有GPU数据可渲染");
        gpuListEl.innerHTML = '<div class="no-data">没有可用的GPU数据</div>';
        return;
    }
    
    gpuData.forEach(gpu => {
        const memoryPercent = (gpu.memory.used / gpu.memory.total * 100).toFixed(0);
        const memoryClass = memoryPercent > 80 ? 'danger' : memoryPercent > 50 ? 'warning' : '';
        const utilizationClass = gpu.utilization > 80 ? 'danger' : gpu.utilization > 50 ? 'warning' : '';
        
        const gpuCard = document.createElement('div');
        const selectedGpu = document.querySelector('.gpu-card.selected');
        const isSelected = selectedGpu ? selectedGpu.dataset.gpu_id === gpu.gpu_id : gpu.gpu_id === gpuData[0].gpu_id;
        
        gpuCard.className = `gpu-card ${isSelected ? 'selected' : ''}`;
        gpuCard.dataset.gpu_id = gpu.gpu_id;
        gpuCard.innerHTML = `
            <div class="gpu-name">GPU ${gpu.gpu_id}</div>
            <div class="gpu-status ${gpu.status}">${getStatusText(gpu.status)}</div>
            <div class="gpu-stats">
                <div class="progress-bar-container">
                    <div class="progress-bar-text">显存：${gpu.memory.free}GB 可用</div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill ${memoryClass}" style="width: ${memoryPercent}%"></div>
                    </div>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-text">利用率：${gpu.utilization}%</div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill ${utilizationClass}" style="width: ${gpu.utilization}%"></div>
                    </div>
                </div>
            </div>
        `;
        
        gpuCard.addEventListener('click', async () => {
            document.querySelectorAll('.gpu-card').forEach(card => card.classList.remove('selected'));
            gpuCard.classList.add('selected');
            renderGpuDetails(gpu);
            await renderActiveTasks(gpu.gpu_id);
        });
        
        // 添加右键菜单，用于切换GPU状态
        gpuCard.addEventListener('contextmenu', async (e) => {
            e.preventDefault();
            const isOn = await switchGpu(gpu.gpu_id);
            if (isOn !== null) {
                fetchData(); // 刷新数据
            }
        });
        
        gpuListEl.appendChild(gpuCard);
    });
}

// 渲染GPU详情
function renderGpuDetails(gpu) {
    console.log("渲染GPU详情:", gpu);
    
    if (!gpu) {
        console.error("GPU对象为空，无法渲染详情");
        return;
    }
    
    const detailsEl = document.querySelector('.gpu-details .details-info');
    if (!detailsEl) {
        console.error("找不到GPU详情元素");
        return;
    }
    
    try {
        detailsEl.innerHTML = `
            <div class="detail-item">
                <div class="detail-label">GPU名称</div>
                <div class="detail-value">${gpu.name}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">状态</div>
                <div class="detail-value">${getStatusText(gpu.status)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">显存</div>
                <div class="detail-value">${gpu.memory.used}GB / ${gpu.memory.total}GB</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">利用率</div>
                <div class="detail-value">${gpu.utilization}%</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">温度</div>
                <div class="detail-value">${gpu.temperature}°C</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">功率</div>
                <div class="detail-value">${gpu.power.current}W / ${gpu.power.max}W</div>
            </div>
        `;
    } catch (error) {
        console.error("渲染GPU详情时出错:", error);
        detailsEl.innerHTML = '<div class="error">渲染GPU详情时出错</div>';
    }
}

// 渲染当前GPU上的活跃任务
async function renderActiveTasks(gpu_id) {
    console.log("渲染活跃任务, GPU ID:", gpu_id);
    
    if (!gpu_id) {
        console.error("GPU ID为空，无法渲染任务");
        return;
    }
    
    const tasksEl = document.querySelector('.gpu-tasks .tasks-list');
    if (!tasksEl) {
        console.error("找不到任务列表元素");
        return;
    }
    
    try {
        // 获取当前GPU的任务数据
        const gpuTasks = await fetchGpuTasks(gpu_id);
        
        if (!gpuTasks || gpuTasks.length === 0) {
            tasksEl.innerHTML = '<div class="no-tasks">当前没有任务</div>';
            return;
        }
        
        tasksEl.innerHTML = '';
        gpuTasks.forEach(task => {
            const taskCard = document.createElement('div');
            taskCard.className = 'task-card';
            taskCard.innerHTML = `
                <div class="task-status ${task.status}"></div>
                <div class="task-info">
                    <div class="task-header">
                        <span class="task-id">${task.process_id}</span>
                        <span class="task-todo-id">${task.todo_id}</span>
                    </div>
                    <div class="task-command">${task.command}</div>
                </div>
                <div class="task-actions">
                    <button class="kill">终止</button>
                </div>
            `;
            
            const killButton = taskCard.querySelector('.kill');
            if (task.status !== 'running') {
                killButton.style.display = 'none';
            } else {
                killButton.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (confirm(`确定要终止任务 ${task.process_id} 吗?`)) {
                        const success = await killTask(task.process_id);
                        if (success) {
                            fetchData(); // 刷新数据
                        } else {
                            alert(`终止任务 ${task.process_id} 失败`);
                        }
                    }
                });
            }
            
            tasksEl.appendChild(taskCard);
        });
    } catch (error) {
        console.error(`渲染GPU ${gpu_id} 任务时出错:`, error);
        tasksEl.innerHTML = '<div class="error">获取任务数据失败</div>';
    }
}

// 渲染进程表格
function renderProcessTable() {
    const tableBody = document.querySelector('table tbody');
    tableBody.innerHTML = '';
    
    taskData.forEach(task => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${task.process_id}</td>
            <td>${task.todo_id}</td>
            <td><span class="process-status ${task.status}">${getStatusText(task.status)}</span></td>
            <td>${getGpuName(task.gpu_id)}</td>
            <td>${task.user}</td>
            <td>${task.startTime}</td>
            <td>${task.runTime}</td>
            <td class="command">${task.command}</td>
        `;
        tableBody.appendChild(tr);
    });
}

// 获取GPU显示名称
function getGpuName(gpu_id) {
    const gpu = gpuData.find(g => g.gpu_id === gpu_id);
    return gpu ? gpu.name : gpu_id;
}

// 获取状态文本
function getStatusText(status) {
    const statusMap = {
        'available': '空闲',
        'busy': '忙碌',
        'disabled': '禁用',
        'running': '运行中',
        'completed': '已完成',
        'failed': '失败',
        'killed': '已终止'
    };
    return statusMap[status] || status;
}