// PWA Service Worker регистрация
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log(' ServiceWorker зарегистрирован: ', registration.scope);
                
                // Проверяем обновления Service Worker
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    console.log(' Обновление Service Worker найдено');
                    
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            console.log(' Новый контент доступен!');
                            // Можем показать уведомление пользователю
                            showUpdateNotification();
                        }
                    });
                });
            })
            .catch(err => {
                console.log(' Ошибка регистрации ServiceWorker: ', err);
            });
    });
}

// Установка PWA
let deferredPrompt;
const installButton = document.getElementById('install-button');

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Показываем кнопку установки
    if (installButton) {
        installButton.style.display = 'block';
        installButton.addEventListener('click', installPWA);
    }
});

function installPWA() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(choiceResult => {
            if (choiceResult.outcome === 'accepted') {
                console.log(' Пользователь установил PWA');
                if (installButton) {
                    installButton.style.display = 'none';
                }
            }
            deferredPrompt = null;
        });
    }
}

// Офлайн режим
function showOfflineStatus() {
    const offlineDiv = document.createElement('div');
    offlineDiv.id = 'offline-status';
    offlineDiv.innerHTML = `
        <div class="offline-banner">
            <i class="icon-wifi-off"></i>
            <span>Вы в офлайн-режиме</span>
        </div>
    `;
    document.body.prepend(offlineDiv);
}

function hideOfflineStatus() {
    const offlineDiv = document.getElementById('offline-status');
    if (offlineDiv) {
        offlineDiv.remove();
    }
}

// Проверка соединения
window.addEventListener('online', () => {
    console.log(' Соединение восстановлено');
    hideOfflineStatus();
});

window.addEventListener('offline', () => {
    console.log(' Отсутствует интернет-соединение');
    showOfflineStatus();
});

// Проверяем при загрузке
if (!navigator.onLine) {
    showOfflineStatus();
}

// Уведомление об обновлении
function showUpdateNotification() {
    const notification = document.createElement('div');
    notification.className = 'update-notification';
    notification.innerHTML = `
        <div class="update-content">
            <p>Доступно обновление приложения!</p>
            <button onclick="location.reload()" class="btn btn-sm btn-primary">
                Обновить
            </button>
        </div>
    `;
    document.body.appendChild(notification);
    
    // Автоматически скрываем через 10 секунд
    setTimeout(() => {
        notification.remove();
    }, 10000);
}

// Сохранение данных в IndexedDB для офлайн работы
const DB_NAME = 'visual_novel_pwa';
const DB_VERSION = 1;
const STORE_NAME = 'novels';

function initDB() {
    return new Promise((resolve, reject) => {
        if (!window.indexedDB) {
            reject('IndexedDB не поддерживается');
            return;
        }
        
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
                store.createIndex('author_id', 'author_id', { unique: false });
                store.createIndex('is_published', 'is_published', { unique: false });
            }
        };
    });
}

// Функция для сохранения новеллы в IndexedDB
async function saveNovelOffline(novelData) {
    try {
        const db = await initDB();
        const tx = db.transaction(STORE_NAME, 'readwrite');
        const store = tx.objectStore(STORE_NAME);
        
        await store.put({
            ...novelData,
            saved_at: new Date().toISOString(),
            is_offline: true
        });
        
        console.log(' Новелла сохранена для офлайн доступа');
        return true;
    } catch (error) {
        console.error(' Ошибка сохранения для офлайн:', error);
        return false;
    }
}

// Функция для получения новелл из IndexedDB
async function getOfflineNovels() {
    try {
        const db = await initDB();
        const tx = db.transaction(STORE_NAME, 'readonly');
        const store = tx.objectStore(STORE_NAME);
        const request = store.getAll();
        
        return new Promise((resolve, reject) => {
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    } catch (error) {
        console.error(' Ошибка получения офлайн новелл:', error);
        return [];
    }
}