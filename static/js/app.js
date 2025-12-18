// Регистрация Service Worker для PWA
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js')
        .then(() => console.log('Service Worker зарегистрирован'))
        .catch(err => console.log('Ошибка регистрации SW:', err));
}

// Запрос на установку PWA
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // Показать кнопку "Установить"
});

function installPWA() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(() => {
            deferredPrompt = null;
        });
    }
}