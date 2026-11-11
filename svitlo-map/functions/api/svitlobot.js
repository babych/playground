export async function onRequestGet(context) {
  const { request } = context;
  const cache = caches.default;
  const cacheKey = new Request(request.url, request);

  // 1. Перевірка Cloudflare Edge Cache
  let response = await cache.match(cacheKey);
  if (response) {
    const cachedResponse = new Response(response.body, response);
    cachedResponse.headers.set('X-Edge-Cache', 'HIT');
    return cachedResponse;
  }

  // 2. Якщо кешу немає — 1 запит до СвітлоБота
  try {
    const upstream = await fetch('https://api.svitlobot.in.ua/website/getChannelsForMap', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; SvitloMap/1.0; +https://svitlo-map.pages.dev)'
      }
    });

    if (!upstream.ok) {
      return new Response('Upstream error: ' + upstream.status, { status: 502 });
    }

    const data = await upstream.text();

    response = new Response(data, {
      status: 200,
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'public, max-age=60, s-maxage=60, stale-while-revalidate=30',
        'X-Edge-Cache': 'MISS'
      }
    });

    // Зберігаємо в кеш на 60 секунд (ліміт СвітлоБота — не частіше 1 разу на хвилину)
    if (context.waitUntil) {
      context.waitUntil(cache.put(cacheKey, response.clone()));
    } else {
      await cache.put(cacheKey, response.clone());
    }

    return response;
  } catch (e) {
    return new Response('Error: ' + e.message, { status: 500 });
  }
}
