'use strict';

// Импортируем библиотеку sw-toolbox
importScripts('sw-toolbox.js');

/**
 * Перечень файлов, которые будут закешированы во время установки
 * (на этапе 'install' Service Worker).
 * В нашем примере это основные страницы и стили/скрипты.
 */
toolbox.precache([
  'index.html',
  '404.html',
  'style/style.css',
  'style/404.css',
  'js/script.js'
]);

/**
 * Стратегия для изображений:
 *  - cacheFirst: сначала пытаемся получить файл из кеша,
 *    при отсутствии файла в кеше – делаем сетевой запрос
 */
toolbox.router.get('/assets/img/*', toolbox.cacheFirst, {
  // Дополнительные настройки кеша (необязательно)
  cache: {
    name: 'img-cache',     // Имя кеша
    maxEntries: 50,        // Максимальное кол-во ресурсов в кеше
    maxAgeSeconds: 7 * 24 * 60 * 60 // Срок хранения (в секундах), напр. 7 дней
  }
});

/**
 * Стратегия для всех остальных запросов:
 *  - networkFirst: пытаемся получить ресурс из сети,
 *    если сеть недоступна или не отвечает дольше networkTimeoutSeconds,
 *    используем кеш
 */
toolbox.router.get('/*', toolbox.networkFirst, {
  networkTimeoutSeconds: 5, // Таймаут сети в секундах
  cache: {
    name: 'default-cache',  // Имя кеша для прочих запросов
    maxEntries: 100,
    maxAgeSeconds: 30 * 24 * 60 * 60 // Напр., 30 дней
  }
});

/**
 * Опционально: Обработчик события установки (install).
 * Можно управлять тем, когда сервис-воркер активируется,
 * дожидаясь завершения кеширования и пр.
 */
self.addEventListener('install', event => {
  console.log('[Service Worker] Install event.');
  // Можно добавить пропуск ожидания активации (skipWaiting)
  // event.waitUntil(self.skipWaiting());
});

/**
 * Опционально: Обработчик события активации (activate).
 * Можно, например, чистить старые версии кешей.
 */
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activate event.');
  // event.waitUntil(...) – логика очистки устаревших кешей и т.д.
});
