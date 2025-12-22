// static/sw.js - Service Worker для PWA
const CACHE_NAME = 'visual-novel-pwa-v3';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/images/icon-192.png',
    '/static/images/icon-512.png',
    '/static/manifest.json'
];

// Устанавливаем Service Worker
self.addEventListener('install', event => {
    console.log('🔄 Service Worker: Установка');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('📦 Service Worker: Кеширование файлов');
                return cache.addAll(urlsToCache);
            })
            .then(() => {
                console.log('✅ Service Worker: Установка завершена');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('❌ Service Worker: Ошибка установки:', error);
            })
    );
});

// Активируем Service Worker
self.addEventListener('activate', event => {
    console.log('🔄 Service Worker: Активация');
    
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('🗑️ Service Worker: Удаляем старый кеш:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('✅ Service Worker: Активация завершена');
            return self.clients.claim();
        })
    );
});

// Обработка fetch запросов
self.addEventListener('fetch', event => {
    // Пропускаем не-GET запросы и chrome-extension
    if (event.request.method !== 'GET' || 
        event.request.url.startsWith('chrome-extension://')) {
        return;
    }
    
    // Для API запросов - только сеть, не кешируем
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    // При ошибке сети для API возвращаем ошибку
                    return new Response(
                        JSON.stringify({ error: 'Офлайн режим для API не поддерживается' }),
                        {
                            status: 503,
                            headers: { 'Content-Type': 'application/json' }
                        }
                    );
                })
        );
        return;
    }
    
    // Для статики - Cache First
    if (event.request.url.includes('/static/')) {
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    if (response) {
                        console.log('📦 Service Worker: Используем кеш для статики:', event.request.url);
                        return response;
                    }
                    
                    return fetch(event.request)
                        .then(response => {
                            // Проверяем валидность ответа
                            if (!response || response.status !== 200 || response.type !== 'basic') {
                                return response;
                            }
                            
                            // Клонируем для кеширования
                            const responseToCache = response.clone();
                            
                            caches.open(CACHE_NAME)
                                .then(cache => {
                                    cache.put(event.request, responseToCache);
                                    console.log('✅ Service Worker: Закеширован новый статический файл:', event.request.url);
                                });
                            
                            return response;
                        })
                        .catch(error => {
                            console.error('❌ Service Worker: Ошибка загрузки статики:', error);
                            return new Response('Офлайн режим', {
                                status: 503,
                                headers: { 'Content-Type': 'text/plain' }
                            });
                        });
                })
        );
        return;
    }
    
    // Для HTML страниц - Network First
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Проверяем валидность ответа
                if (!response || response.status !== 200 || response.type !== 'basic') {
                    return response;
                }
                
                // Клонируем для кеширования
                const responseToCache = response.clone();
                
                caches.open(CACHE_NAME)
                    .then(cache => {
                        cache.put(event.request, responseToCache);
                        console.log('✅ Service Worker: Закеширована страница:', event.request.url);
                    });
                
                return response;
            })
            .catch(() => {
                // При ошибке сети - ищем в кеше
                return caches.match(event.request)
                    .then(response => {
                        if (response) {
                            console.log('📦 Service Worker: Используем кешированную страницу:', event.request.url);
                            return response;
                        }
                        
                        // Если страницы нет в кеше - возвращаем офлайн-страницу
                        return caches.match('/')
                            .then(homePage => {
                                if (homePage) {
                                    return homePage;
                                }
                                
                                // Если даже главной нет - возвращаем сообщение
                                return new Response(
                                    '<h1>Офлайн режим</h1><p>Приложение работает в офлайн режиме. Пожалуйста, проверьте соединение с интернетом.</p>',
                                    {
                                        status: 200,
                                        headers: { 'Content-Type': 'text/html' }
                                    }
                                );
                            });
                    });
            })
    );
});

// Получение сообщений от клиента
self.addEventListener('message', event => {
    console.log('📨 Service Worker: Получено сообщение:', event.data);
    
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// Фоновая синхронизация
self.addEventListener('sync', event => {
    console.log('🔄 Service Worker: Фоновая синхронизация:', event.tag);
    
    if (event.tag === 'sync-novels') {
        event.waitUntil(syncNovels());
    }
});

// Отправка пуш-уведомлений
self.addEventListener('push', event => {
    console.log('🔔 Service Worker: Получено push-уведомление');
    
    const options = {
        body: event.data ? event.data.text() : 'Новое обновление в визуальных новеллах!',
        icon: '/static/images/icon-192.png',
        badge: '/static/images/icon-192.png',
        vibrate: [200, 100, 200],
        data: {
            url: '/'
        }
    };
    
    event.waitUntil(
        self.registration.showNotification('Визуальные новеллы', options)
    );
});

// Обработка кликов по уведомлениям
self.addEventListener('notificationclick', event => {
    console.log('🖱️ Service Worker: Клик по уведомлению');
    
    event.notification.close();
    
    event.waitUntil(
        clients.matchAll({ type: 'window' })
            .then(clientList => {
                for (const client of clientList) {
                    if (client.url === '/' && 'focus' in client) {
                        return client.focus();
                    }
                }
                
                if (clients.openWindow) {
                    return clients.openWindow(event.notification.data.url || '/');
                }
            })
    );
});

// Функция для синхронизации новелл
async function syncNovels() {
    try {
        console.log('🔄 Service Worker: Начинаем синхронизацию новелл');
        
        // Здесь можно добавить логику синхронизации данных
        // Например, отправку данных, сохраненных в IndexedDB
        
        return Promise.resolve();
    } catch (error) {
        console.error('❌ Service Worker: Ошибка синхронизации:', error);
        return Promise.reject(error);
    }
}

// Обработка ошибок Service Worker
self.addEventListener('error', event => {
    console.error('❌ Service Worker: Ошибка:', event.error);
});

// Обработка reject промисов
self.addEventListener('unhandledrejection', event => {
    console.error('❌ Service Worker: Необработанный rejection:', event.reason);
});