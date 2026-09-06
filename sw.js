/* SankaraShield — service worker kill switch.
 *
 * The previous site registered a cache-first service worker
 * (CACHE_NAME "sankarashield-v3.0.0"). Any browser that visited the old site
 * still holds that worker and would keep serving the OLD pages from cache
 * after this rebuild goes live — deleting sw.js is NOT enough to undo that.
 *
 * This file replaces it: it claims control, deletes every cache, unregisters
 * itself and reloads open tabs onto the live site.
 *
 * Keep this file deployed for at least 60 days after cutover, then remove it.
 */
self.addEventListener('install', function () {
  self.skipWaiting();
});

self.addEventListener('activate', function (event) {
  event.waitUntil((async function () {
    var keys = await caches.keys();
    await Promise.all(keys.map(function (k) { return caches.delete(k); }));
    await self.registration.unregister();
    var clientList = await self.clients.matchAll({ type: 'window' });
    clientList.forEach(function (client) { client.navigate(client.url); });
  })());
});
