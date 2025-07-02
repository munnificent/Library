'use strict';

// Импортируем библиотеку sw-toolbox
importScripts('sw-toolbox.js');

// --- Конфигурация Service Worker ---

// 1. Файлы "оболочки" приложения для немедленного кэширования.
// Это основные ресурсы, необходимые для запуска приложения.
const appShellFiles = [
  '/',
  'index.html',
  '404.html',
  'manifest.json',
  'books.json',
  'css/styles.css',
  'css/404.css',
  'js/script.js',
  'assets/icon/favicon.ico',
  'assets/icon/apple-icon-180x180.png'
];

// Кэшируем "оболочку" приложения при установке
toolbox.precache(appShellFiles);


// 2. Стратегии кэширования в реальном времени (runtime).

// Стратегия для изображений и PDF-файлов книг: "сначала кэш".
// Если ресурс есть в кэше, он будет взят оттуда мгновенно.
// Если нет - будет загружен из сети и добавлен в кэш.
toolbox.router.get('/assets/(img|files)/.*', toolbox.cacheFirst, {
  cache: {
    name: 'asset-cache',
    maxEntries: 100, // Максимум 100 файлов (обложки + книги)
    maxAgeSeconds: 30 * 24 * 60 * 60, // Хранить 30 дней
  }
});

// Стратегия для API шрифтов Google: "сначала кэш".
// Шрифты редко меняются, поэтому их безопасно кэшировать.
toolbox.router.get('https://fonts.googleapis.com/.*', toolbox.cacheFirst, {
  cache: {
    name: 'google-fonts-cache',
    maxEntries: 5,
  }
});

// Стратегия по умолчанию для всех остальных запросов: "сначала сеть".
// Приложение попытается получить свежую версию из сети.
// Если сети нет, будет использована версия из кэша.
toolbox.router.get('/*', toolbox.networkFirst, {
  networkTimeoutSeconds: 5, // Таймаут ожидания сети (5 секунд)
});


// 3. Жизненный цикл Service Worker (необязательно, для отладки).

self.addEventListener('install', event => {
  console.log('[Service Worker] Установка...');
  // Принудительная активация новой версии Service Worker
  return self.skipWaiting();
});

self.addEventListener('activate', event => {
  console.log('[Service Worker] Активация...');
  // Управление текущей страницей без необходимости перезагрузки
  return self.clients.claim();
});