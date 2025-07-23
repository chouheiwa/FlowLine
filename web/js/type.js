// toast.js
function showToast(message, duration = 3000) {
    const toast = document.getElementById('toast');
    if (!toast) {
        console.error('Toast 元素未找到，请确保页面包含 toast HTML 结构');
        return;
    }
    const toastMessage = toast.querySelector('.toast-message');
    toastMessage.textContent = message;
    
    toast.classList.add('show');
    toast.classList.remove('hide');
    
    setTimeout(() => {
        toast.classList.add('hide');
        toast.classList.remove('show');
    }, duration);
}

// 挂载到 window 全局对象，确保其他页面可访问
window.showToast = showToast;