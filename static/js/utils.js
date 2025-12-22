// static/js/utils.js - Общие утилиты
class Utils {
    static showNotification(message, type = 'info') {
        const notificationArea = document.getElementById('notification-area') || 
                                this.createNotificationArea();
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 400px;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                ${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}
                <span>${message}</span>
            </div>
        `;
        
        notificationArea.appendChild(notification);
        
        // Автоматически скрываем через 3 секунды
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    static createNotificationArea() {
        const area = document.createElement('div');
        area.id = 'notification-area';
        document.body.appendChild(area);
        return area;
    }
    
    static showLoading() {
        let loadingDiv = document.getElementById('loading-overlay');
        if (!loadingDiv) {
            loadingDiv = document.createElement('div');
            loadingDiv.id = 'loading-overlay';
            loadingDiv.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255,255,255,0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            `;
            loadingDiv.innerHTML = `
                <div class="loading-spinner"></div>
            `;
            document.body.appendChild(loadingDiv);
        }
        loadingDiv.style.display = 'flex';
    }
    
    static hideLoading() {
        const loadingDiv = document.getElementById('loading-overlay');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
    }
    
    static escapeHtml(text) {
        if (typeof text !== 'string') return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    static validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    static validatePassword(password) {
        return password.length >= 6;
    }
    
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}