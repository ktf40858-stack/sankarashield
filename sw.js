const CACHE_NAME = 'sankarashield-v3.0.0';
const urlsToCache = [
  '/',
  '/index.html',
  '/about.html',
  '/services.html',
  '/partners.html',
  '/contact.html',
  '/privacy.html',
  '/terms.html',
  '/css/styles.css',
  '/js/app.js',
  '/manifest.json',
  '/Logo.png',
  '/world.jpg',
  '/fortinet.png',
  '/juniper.png',
  '/cisco-black-logo-hd-png-701751694708581xqutvctmyl.png',
  '/Palo Alto Networks_idMI_itknr_1.png',
  '/icons/icon-72.png',
  '/icons/icon-96.png',
  '/icons/icon-128.png',
  '/icons/icon-144.png',
  '/icons/icon-152.png',
  '/icons/icon-192.png',
  '/icons/icon-384.png',
  '/icons/icon-512.png'
];

self.addEventListener('install', event => {
  console.log('[ServiceWorker] Installation en cours...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[ServiceWorker] Mise en cache des ressources');
        return Promise.all(
          urlsToCache.map(url => {
            return cache.add(url).catch(err => {
              console.warn(`[ServiceWorker] Impossible de mettre en cache: ${url}`, err);
            });
          })
        );
      })
      .then(() => {
        console.log('[ServiceWorker] Installation terminée');
        return self.skipWaiting();
      })
      .catch(err => {
        console.error('[ServiceWorker] Erreur lors de l\'installation:', err);
      })
  );
});

self.addEventListener('activate', event => {
  console.log('[ServiceWorker] Activation en cours...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[ServiceWorker] Suppression ancien cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[ServiceWorker] Service Worker activé');
      return self.clients.claim();
    })
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }

        return fetch(event.request).then(response => {
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          const responseToCache = response.clone();

          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });

          return response;
        });
      })
      .catch(() => {
        if (event.request.destination === 'document') {
          return caches.match('/index.html');
        }
        return new Response('Contenu non disponible hors ligne', {
          status: 503,
          statusText: 'Service Indisponible',
          headers: new Headers({
            'Content-Type': 'text/plain; charset=utf-8'
          })
        });
      })
  );
});

self.addEventListener('message', event => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }

  if (event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      caches.open(CACHE_NAME)
        .then(cache => cache.addAll(event.data.payload))
    );
  }
});

self.addEventListener('sync', event => {
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

async function syncData() {
  try {
    console.log('[ServiceWorker] Synchronisation des données');
    const response = await fetch('/api/sync', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        timestamp: new Date().toISOString()
      })
    });

    if (response.ok) {
      console.log('[ServiceWorker] Synchronisation réussie');
    }
  } catch (error) {
    console.error('[ServiceWorker] Erreur de synchronisation:', error);
  }
}

self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'Nouvelle notification de SankaraShield',
    icon: '/icons/icon-192.png',
    badge: '/icons/icon-96.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Voir détails',
        icon: '/icons/icon-96.png'
      },
      {
        action: 'close',
        title: 'Fermer',
        icon: '/icons/icon-96.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('SankaraShield Alert', options)
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/index.html#notifications')
    );
  } else if (event.action === 'close') {
    event.notification.close();
  } else {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});
