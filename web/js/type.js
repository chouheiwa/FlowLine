// toast.js
function showToast(message, duration = 3000, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) {
        console.error('Toast 容器未找到，请确保页面包含 #toastContainer');
        return;
    }

    // 创建一个新的 toast 元素
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-message">${escapeHtml(String(message))}</span>
        </div>
        <div class="progress"></div>
    `;

    const progress = toast.querySelector('.progress');  
    progress.style.setProperty('--toast-duration', `${duration}ms`);

    // 插入容器
    container.appendChild(toast);

    // 下一帧再加 show 触发过渡
    requestAnimationFrame(() => {
        progress.classList.add('run'); 
        toast.classList.add('show');
    });

    // 自动隐藏
    let hideTimer = setTimeout(hide, duration);
    let startedAt = performance.now();

    // 悬停暂停计时
    toast.addEventListener('mouseenter', () => {
        toast.classList.add('hovering');
        clearTimeout(hideTimer);
        duration -= performance.now() - startedAt;
    });
    
    toast.addEventListener('mouseleave', () => {
        toast.classList.remove('hovering');
        hideTimer = setTimeout(hide, duration);
        startedAt = performance.now();
    });

    // 过渡结束后从 DOM 移除，防止内存泄漏
    toast.addEventListener('transitionend', (e) => {
        // 只在淡出（hide）完成后移除
        if (e.propertyName === 'opacity' && toast.classList.contains('hide')) {
            toast.remove();
        }
    });

    function hide() {
        toast.classList.add('hide');
        toast.classList.remove('show');
    }

    // —— 可选：限制最大同时显示数量（例如 4 个），多了就先移除最旧的 ——
    const MAX_TOASTS = 4;
    if (container.children.length > MAX_TOASTS) {
        console.log('remove first toast');
        const first = container.firstElementChild;
        if (first && first !== toast) {
            first.classList.add('hide');
            first.classList.remove('show');
            // 立刻移除或等待过渡结束移除，这里选择等待过渡
            first.addEventListener('transitionend', () => first.remove(), { once: true });
        }
    }
}

// 简单的转义，避免把 <script> 当成 HTML 注入
function escapeHtml(text) {
    const map = {
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// 挂载到 window 全局对象，确保其他页面可访问
window.showToast = showToast;