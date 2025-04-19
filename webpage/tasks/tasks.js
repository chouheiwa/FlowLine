// 全局变量
let tasks = [];
let selectedCategory = 'all';
let gpus = [];

// DOM 元素
const taskCategoriesEl = document.getElementById('taskCategories');
const taskListEl = document.getElementById('tasksList');
const tasksListTitleEl = document.getElementById('tasksListTitle');
const taskNameInput = document.getElementById('taskName');
const taskCommandInput = document.getElementById('taskCommand');
const taskGpuSelect = document.getElementById('taskGpu');
const createTaskBtn = document.getElementById('createTaskBtn');
const refreshBtn = document.getElementById('refreshBtn');
const clearBtn = document.getElementById('clearBtn');
const taskDetailPanel = document.getElementById('taskDetailPanel');
const closeDetailBtn = document.getElementById('closeDetailBtn');
const taskDetailTitle = document.getElementById('taskDetailTitle');
const taskDetailContent = document.getElementById('taskDetailContent');
const toast = document.getElementById('toast');
const toastMessage = document.querySelector('.toast-message');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 加载任务和GPU数据
    loadTasks();
    loadGpus();
    
    // 绑定事件
    bindEvents();
});

// 绑定事件处理函数
function bindEvents() {
    // 切换任务分类
    taskCategoriesEl.addEventListener('click', (e) => {
        const categoryCard = e.target.closest('.category-card');
        if (categoryCard) {
            const status = categoryCard.dataset.status;
            selectCategory(status);
        }
    });
    
    // 创建任务
    createTaskBtn.addEventListener('click', createTask);
    
    // 刷新按钮
    refreshBtn.addEventListener('click', () => {
        loadTasks();
        loadGpus();
        showToast('数据已刷新');
    });
    
    // 清空已完成/失败任务
    clearBtn.addEventListener('click', clearCompletedTasks);
    
    // 关闭详情面板
    closeDetailBtn.addEventListener('click', () => {
        taskDetailPanel.classList.remove('show');
    });
}

// 加载任务数据
function loadTasks() {
    // 模拟API请求获取任务数据
    setTimeout(() => {
        // 这里应该是实际的API调用
        // fetch('/api/tasks').then(response => response.json()).then(data => {...})
        
        // 示例数据
        tasks = [
            { 
                id: 'task_001', 
                name: '样例训练任务', 
                command: 'python train.py --model resnet50 --epochs 100', 
                status: 'running', 
                gpu: 'RTX 4090', 
                startTime: '2023-08-15 10:30:45', 
                progress: 45 
            },
            { 
                id: 'task_002', 
                name: '图像分类任务', 
                command: 'python classify.py --input images/ --output results/', 
                status: 'completed', 
                gpu: 'RTX 3080', 
                startTime: '2023-08-14 09:15:30', 
                endTime: '2023-08-14 12:45:22' 
            },
            { 
                id: 'task_003', 
                name: '数据处理任务', 
                command: 'python preprocess.py --data raw_data/ --clean', 
                status: 'failed', 
                gpu: 'RTX 4090', 
                startTime: '2023-08-15 08:10:15', 
                endTime: '2023-08-15 08:15:42',
                error: '内存不足'
            },
            { 
                id: 'task_004', 
                name: '模型评估', 
                command: 'python evaluate.py --model model.pth --test test_data/', 
                status: 'pending', 
                gpu: 'RTX 3080', 
                createTime: '2023-08-15 13:05:10' 
            },
            { 
                id: 'task_005', 
                name: '已终止任务', 
                command: 'python long_process.py', 
                status: 'killed', 
                gpu: 'RTX 4090', 
                startTime: '2023-08-13 14:30:00', 
                endTime: '2023-08-13 14:45:12' 
            }
        ];
        
        updateTaskCounts();
        renderTasks();
    }, 300);
}

// 加载GPU数据
function loadGpus() {
    // 模拟API请求获取GPU数据
    setTimeout(() => {
        // 这里应该是实际的API调用
        // fetch('/api/gpus').then(response => response.json()).then(data => {...})
        
        // 示例GPU数据
        gpus = [
            { id: 'gpu_001', name: 'RTX 4090', status: 'available' },
            { id: 'gpu_002', name: 'RTX 3080', status: 'busy' }
        ];
        
        renderGpuOptions();
    }, 300);
}

// 渲染GPU选项
function renderGpuOptions() {
    taskGpuSelect.innerHTML = '';
    
    // 添加默认选项
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '选择一个GPU';
    defaultOption.disabled = true;
    defaultOption.selected = true;
    taskGpuSelect.appendChild(defaultOption);
    
    // 添加GPU选项
    gpus.forEach(gpu => {
        const option = document.createElement('option');
        option.value = gpu.id;
        option.textContent = `${gpu.name} (${gpu.status === 'available' ? '可用' : '忙碌'})`;
        option.disabled = gpu.status !== 'available';
        taskGpuSelect.appendChild(option);
    });
}

// 更新任务计数
function updateTaskCounts() {
    const counts = {
        all: tasks.length,
        running: tasks.filter(task => task.status === 'running').length,
        pending: tasks.filter(task => task.status === 'pending').length,
        completed: tasks.filter(task => task.status === 'completed').length,
        failed: tasks.filter(task => task.status === 'failed').length,
        killed: tasks.filter(task => task.status === 'killed').length
    };
    
    // 更新计数显示
    Object.keys(counts).forEach(status => {
        const countEl = document.getElementById(`${status}-count`);
        if (countEl) {
            countEl.textContent = counts[status];
        }
    });
}

// 选择任务分类
function selectCategory(status) {
    selectedCategory = status;
    
    // 更新UI状态
    const categoryCards = taskCategoriesEl.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.classList.toggle('selected', card.dataset.status === status);
    });
    
    // 更新标题
    const titles = {
        all: '所有任务',
        running: '运行中的任务',
        pending: '等待中的任务',
        completed: '已完成的任务',
        failed: '失败的任务',
        killed: '已终止的任务'
    };
    tasksListTitleEl.textContent = titles[status] || '任务列表';
    
    // 重新渲染任务列表
    renderTasks();
}

// 渲染任务列表
function renderTasks() {
    // 筛选任务
    const filteredTasks = selectedCategory === 'all' 
        ? tasks 
        : tasks.filter(task => task.status === selectedCategory);
    
    // 清空任务列表
    taskListEl.innerHTML = '';
    
    // 渲染任务卡片
    if (filteredTasks.length === 0) {
        taskListEl.innerHTML = '<div class="empty-state">没有任务</div>';
        return;
    }
    
    filteredTasks.forEach(task => {
        const taskCard = document.createElement('div');
        taskCard.className = 'task-card';
        taskCard.dataset.id = task.id;
        
        const statusLabel = {
            running: '运行中',
            pending: '等待中',
            completed: '已完成',
            failed: '失败',
            killed: '已终止'
        };
        
        taskCard.innerHTML = `
            <div class="task-header">
                <div class="task-id">${task.name}</div>
                <div class="task-status ${task.status}"></div>
            </div>
            <div class="task-info">
                <div>状态: <span>${statusLabel[task.status]}</span></div>
                <div>GPU: <span>${task.gpu}</span></div>
                <div>命令:</div>
                <div class="task-command">${task.command}</div>
                ${task.progress ? `<div>进度: <span>${task.progress}%</span></div>` : ''}
                ${task.startTime ? `<div>开始时间: <span>${task.startTime}</span></div>` : ''}
                ${task.endTime ? `<div>结束时间: <span>${task.endTime}</span></div>` : ''}
                ${task.error ? `<div>错误: <span>${task.error}</span></div>` : ''}
            </div>
            <div class="task-actions">
                <button class="view-detail" data-id="${task.id}">查看详情</button>
                ${task.status === 'running' ? `<button class="kill" data-id="${task.id}">终止</button>` : ''}
            </div>
        `;
        
        taskListEl.appendChild(taskCard);
    });
    
    // 绑定任务卡片事件
    bindTaskCardEvents();
}

// 绑定任务卡片事件
function bindTaskCardEvents() {
    // 查看详情按钮
    const viewDetailBtns = document.querySelectorAll('.view-detail');
    viewDetailBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const taskId = e.target.dataset.id;
            showTaskDetail(taskId);
        });
    });
    
    // 终止任务按钮
    const killBtns = document.querySelectorAll('.kill');
    killBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const taskId = e.target.dataset.id;
            killTask(taskId);
        });
    });
}

// 显示任务详情
function showTaskDetail(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    
    taskDetailTitle.textContent = `任务详情: ${task.name}`;
    
    const statusLabel = {
        running: '运行中',
        pending: '等待中',
        completed: '已完成',
        failed: '失败',
        killed: '已终止'
    };
    
    taskDetailContent.innerHTML = `
        <div class="detail-section">
            <h3>基本信息</h3>
            <div class="detail-item">
                <span class="detail-label">任务ID:</span>
                <span class="detail-value">${task.id}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">名称:</span>
                <span class="detail-value">${task.name}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">状态:</span>
                <span class="detail-value status-${task.status}">${statusLabel[task.status]}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">GPU:</span>
                <span class="detail-value">${task.gpu}</span>
            </div>
            ${task.progress ? `
            <div class="detail-item">
                <span class="detail-label">进度:</span>
                <span class="detail-value">${task.progress}%</span>
            </div>
            ` : ''}
            ${task.startTime ? `
            <div class="detail-item">
                <span class="detail-label">开始时间:</span>
                <span class="detail-value">${task.startTime}</span>
            </div>
            ` : ''}
            ${task.endTime ? `
            <div class="detail-item">
                <span class="detail-label">结束时间:</span>
                <span class="detail-value">${task.endTime}</span>
            </div>
            ` : ''}
            ${task.error ? `
            <div class="detail-item">
                <span class="detail-label">错误:</span>
                <span class="detail-value">${task.error}</span>
            </div>
            ` : ''}
        </div>
        
        <div class="detail-section">
            <h3>命令</h3>
            <div class="task-command">${task.command}</div>
        </div>
        
        <div class="detail-section">
            <h3>日志输出</h3>
            <div class="task-logs">
                <pre>${task.logs || '暂无日志输出'}</pre>
            </div>
        </div>
    `;
    
    taskDetailPanel.classList.add('show');
}

// 创建任务
function createTask() {
    const name = taskNameInput.value.trim();
    const command = taskCommandInput.value.trim();
    const gpuId = taskGpuSelect.value;
    
    // 验证输入
    if (!name) {
        showToast('请输入任务名称');
        return;
    }
    if (!command) {
        showToast('请输入任务命令');
        return;
    }
    if (!gpuId) {
        showToast('请选择GPU');
        return;
    }
    
    // 获取选中的GPU
    const selectedGpu = gpus.find(gpu => gpu.id === gpuId);
    
    // 模拟API请求创建任务
    // 实际应该是 fetch('/api/tasks', { method: 'POST', body: JSON.stringify({...}) })
    
    // 模拟创建任务
    const newTask = {
        id: `task_${Date.now()}`,
        name: name,
        command: command,
        status: 'pending',
        gpu: selectedGpu.name,
        createTime: new Date().toLocaleString()
    };
    
    // 添加到任务列表
    tasks.unshift(newTask);
    
    // 更新UI
    updateTaskCounts();
    
    // 如果当前显示的是所有任务或待处理任务，则重新渲染
    if (selectedCategory === 'all' || selectedCategory === 'pending') {
        renderTasks();
    }
    
    // 清空表单
    taskNameInput.value = '';
    taskCommandInput.value = '';
    taskGpuSelect.value = '';
    
    // 显示提示
    showToast('任务已创建');
}

// 终止任务
function killTask(taskId) {
    // 模拟API请求终止任务
    // 实际应该是 fetch(`/api/tasks/${taskId}/kill`, { method: 'POST' })
    
    // 更新任务状态
    const task = tasks.find(t => t.id === taskId);
    if (task) {
        task.status = 'killed';
        task.endTime = new Date().toLocaleString();
        
        // 更新UI
        updateTaskCounts();
        renderTasks();
        
        // 如果详情面板打开，更新详情
        if (taskDetailPanel.classList.contains('show') && taskDetailTitle.textContent.includes(task.name)) {
            showTaskDetail(taskId);
        }
        
        // 显示提示
        showToast('任务已终止');
    }
}

// 清空已完成/失败任务
function clearCompletedTasks() {
    // 模拟API请求清空任务
    // 实际应该是 fetch('/api/tasks/clear', { method: 'POST' })
    
    // 过滤出非已完成/失败的任务
    tasks = tasks.filter(task => !['completed', 'failed', 'killed'].includes(task.status));
    
    // 更新UI
    updateTaskCounts();
    renderTasks();
    
    // 显示提示
    showToast('已清空完成/失败任务');
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