// Hive Alignment OTA Service Worker (Network-First App Shell + Instant Activation)
const CACHE_NAME = 'hive-alignment-ota-v1';
const APP_SHELL = [
  './',
  './index.html',
  './manifest.json'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return Promise.allSettled(
        APP_SHELL.map((url) =>
          fetch(url, { cache: 'no-store' }).then((res) => {
            if (res && res.ok) return cache.put(url, res.clone());
          })
        )
      );
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) return caches.delete(key);
        })
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Never intercept Supabase, WHOOP, Garmin, Wikipedia, or Aladhan live API calls
  if (
    url.hostname.includes('supabase.co') ||
    url.hostname.includes('whoop.com') ||
    url.hostname.includes('garmin.com') ||
    url.hostname.includes('aladhan.com') ||
    url.hostname.includes('wikipedia.org') ||
    url.hostname.includes('jina.ai') ||
    url.hostname.includes('allorigins.win')
  ) {
    return;
  }

  // Network-First with cache: 'no-store' for same-origin HTML/manifest so git pushes update OTA immediately
  if (url.origin === self.location.origin) {
    event.respondWith(
      fetch(req, { cache: 'no-store' })
        .then((networkRes) => {
          if (networkRes && networkRes.ok) {
            const copy = networkRes.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          }
          return networkRes;
        })
        .catch(() => caches.match(req).then((cached) => cached || caches.match('./index.html')))
    );
    return;
  }

  // Stale-While-Revalidate for external CDN scripts/icons
  event.respondWith(
    caches.match(req).then((cached) => {
      const fetchPromise = fetch(req)
        .then((networkRes) => {
          if (networkRes && networkRes.ok) {
            const copy = networkRes.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          }
          return networkRes;
        })
        .catch(() => cached);
      return cached || fetchPromise;
    })
  );
});
