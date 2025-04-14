 // 示例数据 - 在实际应用中会从后端API获取
const gpuData = [
    {
        id: 'gpu-0',
        name: 'NVIDIA RTX 4090',
        status: 'available',
        memory: { used: 2, total: 24 },
        utilization: 5,
        temperature: 42,
        power: { current: 30, max: 350 }
    },
    {
        id: 'gpu-1',
        name: 'NVIDIA RTX 3080',
        status: 'busy',
        memory: { used: 9, total: 12 },
        utilization: 85,
        temperature: 78,
        power: { current: 220, max: 320 }
    },
    {
        id: 'gpu-2',
        name: 'NVIDIA RTX 2080 Ti',
        status: 'available',
        memory: { used: 1, total: 11 },
        utilization: 2,
        temperature: 38,
        power: { current: 25, max: 250 }
    },
    {
        id: 'gpu-3',
        name: 'NVIDIA RTX 3090',
        status: 'disabled',
        memory: { used: 0, total: 24 },
        utilization: 0,
        temperature: 35,
        power: { current: 15, max: 350 }
    }
];

const taskData = [
    {
        id: 'task-1',
        todoId: 'todo-458',
        status: 'running',
        gpu: 'gpu-1',
        user: 'zhang.san',
        startTime: '2023-05-15 14:32:45',
        runTime: '02:45:18',
        command: 'python train.py --model resnet50 --batch_size 64 --epochs 100'
    },
    {
        id: 'task-2',
        todoId: 'todo-459',
        status: 'completed',
        gpu: 'gpu-0',
        user: 'li.si',
        startTime: '2023-05-15 10:15:32',
        runTime: '03:22:41',
        command: 'python evaluate.py --model efficientnet --dataset imagenet'
    },
    {
        id: 'task-3',
        todoId: 'todo-460',
        status: 'failed',
        gpu: 'gpu-2',
        user: 'wang.wu',
        startTime: '2023-05-16 09:05:12',
        runTime: '00:15:22',
        command: 'python inference.py --input data/test --output results/test'
    }
];

// 初始化页面
document.addEventListener('DOMContentLoaded', () => {
    renderGpuList();
    if (gpuData.length > 0) {
        renderGpuDetails(gpuData[0]);
        renderActiveTasks(gpuData[0].id);
    }
    renderProcessTable();
});

// 渲染GPU列表
function renderGpuList() {
    const gpuListEl = document.querySelector('.gpu-list');
    gpuListEl.innerHTML = '';
    
    gpuData.forEach(gpu => {
        const memoryPercent = (gpu.memory.used / gpu.memory.total * 100).toFixed(0);
        const memoryClass = memoryPercent > 80 ? 'danger' : memoryPercent > 50 ? 'warning' : '';
        
        const utilizationClass = gpu.utilization > 80 ? 'danger' : gpu.utilization > 50 ? 'warning' : '';
        
        const temperatureClass = gpu.temperature > 80 ? 'danger' : gpu.temperature > 70 ? 'warning' : '';
        
        const gpuCard = document.createElement('div');
        gpuCard.className = `gpu-card ${gpu.id === 'gpu-0' ? 'selected' : ''}`;
        gpuCard.dataset.id = gpu.id;
        gpuCard.innerHTML = `
            <div class="gpu-name">${gpu.name}</div>
            <div class="gpu-status ${gpu.status}">${getStatusText(gpu.status)}</div>
            <div class="gpu-stats">
                <div>
                    <div>显存: <span class="stat-value">${gpu.memory.used}GB / ${gpu.memory.total}GB</span></div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill ${memoryClass}" style="width: ${memoryPercent}%"></div>
                    </div>
                </div>
                <div>
                    <div>利用率: <span class="stat-value">${gpu.utilization}%</span></div>
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
            renderActiveTasks(gpu.id);
        });
        
        gpuListEl.appendChild(gpuCard);
    });
}

// 渲染GPU详情
function renderGpuDetails(gpu) {
    const detailsEl = document.querySelector('.gpu-details .details-info');
    
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
}

// 渲染当前GPU上的活跃任务
function renderActiveTasks(gpuId) {
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
            killButton.addEventListener('click', (e) => {
                e.stopPropagation();
                if (confirm(`确定要终止任务 ${task.id} 吗?`)) {
                    console.log(`终止任务: ${task.id}`);
                    // 实际应用中，这里会向后端发送请求
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

// 添加周期性更新
setInterval(() => {
    // 实际应用中，这里会从后端获取最新数据
    console.log('更新数据...');
    // 模拟数据变化
    gpuData.forEach(gpu => {
        if (gpu.status === 'available') {
            gpu.utilization = Math.floor(Math.random() * 10);
            gpu.temperature = 35 + Math.floor(Math.random() * 10);
        } else if (gpu.status === 'busy') {
            gpu.utilization = 70 + Math.floor(Math.random() * 30);
            gpu.temperature = 70 + Math.floor(Math.random() * 15);
        }
    });
    
    renderGpuList();
    const selectedGpu = document.querySelector('.gpu-card.selected');
    if (selectedGpu) {
        const gpuId = selectedGpu.dataset.id;
        const gpu = gpuData.find(g => g.id === gpuId);
        renderGpuDetails(gpu);
    }
}, 5000);