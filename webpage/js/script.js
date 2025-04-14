// API URL - 需要根据实际部署环境修改
const API_BASE_URL = 'http://localhost:5000/api';

// 用于存储数据的变量
let gpuData = [];
let taskData = [];

// 设置刷新按钮点击事件
document.getElementById('refreshBtn').addEventListener('click', fetchData);

// 设置清空按钮点击事件
document.getElementById('clearBtn').addEventListener('click', clearCompletedTasks);

// 初始化页面
fetchData();
document.addEventListener('DOMContentLoaded', () => {
    // 初始加载数据
    fetchData();
    
    // 设置周期性更新（每10秒刷新一次）
    setInterval(fetchData, 10000);
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
        renderUI();
        console.log("UI渲染完成");
    } catch (error) {
        console.error('获取数据失败:', error);
    }
}

// 获取GPU数据
async function fetchGpuData() {
    try {
        const response = await fetch(`${API_BASE_URL}/gpus`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        gpuData = await response.json();
        return gpuData;
    } catch (error) {
        console.error('获取GPU数据失败:', error);
        throw error;
    }
}

// 获取进程数据
async function fetchProcessData() {
    try {
        const response = await fetch(`${API_BASE_URL}/processes`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        taskData = await response.json();
        return taskData;
    } catch (error) {
        console.error('获取进程数据失败:', error);
        throw error;
    }
}

// 获取特定GPU上的任务
async function fetchGpuTasks(gpuId) {
    try {
        const response = await fetch(`${API_BASE_URL}/gpu/${gpuId}/tasks`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const tasks = await response.json();
        return tasks;
    } catch (error) {
        console.error(`获取GPU ${gpuId} 的任务失败:`, error);
        return [];
    }
}

// 终止任务
async function killTask(taskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/task/${taskId}/kill`, {
            method: 'POST',
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        return result.success;
    } catch (error) {
        console.error(`终止任务 ${taskId} 失败:`, error);
        return false;
    }
}

// 切换GPU状态
async function switchGpu(gpuId) {
    try {
        const response = await fetch(`${API_BASE_URL}/gpu/${gpuId}/switch`, {
            method: 'POST',
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        return result.is_on;
    } catch (error) {
        console.error(`切换GPU ${gpuId} 状态失败:`, error);
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
function renderUI() {
    renderGpuList();
    
    // 如果有GPU，则渲染第一个GPU的详情和任务
    if (gpuData.length > 0) {
        const selectedGpu = document.querySelector('.gpu-card.selected');
        const selectedId = selectedGpu ? selectedGpu.dataset.id : gpuData[0].id;
        
        const gpu = gpuData.find(g => g.id === selectedId) || gpuData[0];
        renderGpuDetails(gpu);
        renderActiveTasks(gpu.gpu_id);
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
        const isSelected = selectedGpu ? selectedGpu.dataset.id === gpu.id : gpu.id === gpuData[0].id;
        
        gpuCard.className = `gpu-card ${isSelected ? 'selected' : ''}`;
        gpuCard.dataset.id = gpu.id;
        gpuCard.innerHTML = `
            <div class="gpu-name">GPU ${gpu.gpu_id}</div>
            <div class="gpu-status ${gpu.status}">${getStatusText(gpu.status)}</div>
            <div class="gpu-stats">
                <div class="progress-bar-container">
                    <div class="progress-bar-text">显存：${gpu.memory.free}GB</div>
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
        
        gpuCard.addEventListener('click', () => {
            document.querySelectorAll('.gpu-card').forEach(card => card.classList.remove('selected'));
            gpuCard.classList.add('selected');
            renderGpuDetails(gpu);
            renderActiveTasks(gpu.gpu_id);
        });
        
        // 添加右键菜单，用于切换GPU状态
        gpuCard.addEventListener('contextmenu', async (e) => {
            e.preventDefault();
            const isOn = await switchGpu(gpu.id);
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
function renderActiveTasks(gpuId) {
    console.log("渲染活跃任务, GPU ID:", gpuId);
    
    if (!gpuId) {
        console.error("GPU ID为空，无法渲染任务");
        return;
    }
    
    const tasksEl = document.querySelector('.gpu-tasks .tasks-list');
    const filteredTasks = taskData.filter(task => task.gpu === gpuId);
    
    if (filteredTasks.length === 0) {
        tasksEl.innerHTML = '<div class="no-tasks">当前没有任务</div>';
        return;
    }
    
    tasksEl.innerHTML = '';
    filteredTasks.forEach(task => {
        const taskCard = document.createElement('div');
        taskCard.className = 'task-card';
        taskCard.innerHTML = `
            <div class="task-status ${task.status}"></div>
            <div class="task-info">
                <div class="task-header">
                    <span class="task-id">${task.id}</span>
                    <span class="task-todo-id">${task.todoId}</span>
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
                if (confirm(`确定要终止任务 ${task.id} 吗?`)) {
                    const success = await killTask(task.id);
                    if (success) {
                        fetchData(); // 刷新数据
                    } else {
                        alert(`终止任务 ${task.id} 失败`);
                    }
                }
            });
        }
        
        tasksEl.appendChild(taskCard);
    });
}

// 渲染进程表格
function renderProcessTable() {
    const tableBody = document.querySelector('table tbody');
    tableBody.innerHTML = '';
    
    taskData.forEach(task => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${task.id}</td>
            <td>${task.todoId}</td>
            <td><span class="process-status ${task.status}">${getStatusText(task.status)}</span></td>
            <td>${getGpuName(task.gpu)}</td>
            <td>${task.user}</td>
            <td>${task.startTime}</td>
            <td>${task.runTime}</td>
            <td class="command">${task.command}</td>
        `;
        tableBody.appendChild(tr);
    });
}

// 获取GPU显示名称
function getGpuName(gpuId) {
    const gpu = gpuData.find(g => g.id === gpuId);
    return gpu ? gpu.name : gpuId;
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