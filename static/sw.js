self.addEventListener("install", e => {
  e.waitUntil(
    caches.open("fitmind-cache").then(cache =>
      cache.addAll(["/", "/static/style.css", "/static/scripts.js", "/static/manifest.json"])
    )
  );
});

self.addEventListener("fetch", e => {
  e.respondWith(
    caches.match(e.request).then(response => response || fetch(e.request))
  );
});
