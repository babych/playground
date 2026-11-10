/**
 * СвітлоКарта України — 25 800+ Населених Пунктів за графіками відключень
 * Високопродуктивний Canvas-рушій із просторовим відсіканням (Frustum Culling)
 */

let map;
let canvasOverlay;
let ctx;
let activeDataset = 'settlements_25k'; // 'settlements_25k', 'hromadas', 'svitlobot'
let settlements25k = [];
let hromadasData = [];
let svitlobotData = [];
let isSvitlobotLoading = false;
let hromadasGeoLayer = null;
let showPolygons = false;
let currentHour = new Date().getHours();
let isPlaying = false;
let playInterval = null;
let activeItem = null;
let selectedGroup = 'all';

// Шаблони розкладів черг 1..6
const SCHEDULE_PATTERNS = {
  1: ['on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on'],
  2: ['maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off'],
  3: ['off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on'],
  4: ['on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off'],
  5: ['off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off'],
  6: ['on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on']
};

const CAT_NAMES = {
  1: 'Місто / Район',
  2: 'Селище (смт)',
  3: 'Село'
};

// 1. Ініціалізація карти
function initMap() {
  map = L.map('map', {
    center: [48.6, 31.5],
    zoom: 6,
    minZoom: 5,
    maxZoom: 16,
    zoomControl: false
  });

  L.control.zoom({ position: 'bottomright' }).addTo(map);

  // Темна преміум-підкладка ESRI Dark Gray Canvas (Без водяних знаків та без ключів)
  L.tileLayer('https://services.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    attribution: '&copy; Esri, OpenStreetMap',
    maxZoom: 16
  }).addTo(map);

  createCanvasOverlay();
  loadDatasets();
  setupUIEvents();
}

// 2. Створення Canvas шару поверх карти
function createCanvasOverlay() {
  const mapPane = map.getPanes().overlayPane;
  canvasOverlay = document.createElement('canvas');
  canvasOverlay.className = 'glow-canvas-layer';
  mapPane.appendChild(canvasOverlay);
  ctx = canvasOverlay.getContext('2d');

  function resizeCanvas() {
    const size = map.getSize();
    const dpr = window.devicePixelRatio || 1;
    canvasOverlay.width = size.x * dpr;
    canvasOverlay.height = size.y * dpr;
    canvasOverlay.style.width = size.x + 'px';
    canvasOverlay.style.height = size.y + 'px';
    ctx.scale(dpr, dpr);

    const topLeft = map.containerPointToLayerPoint([0, 0]);
    L.DomUtil.setPosition(canvasOverlay, topLeft);
    renderGlow();
  }

  map.on('move', () => {
    const topLeft = map.containerPointToLayerPoint([0, 0]);
    L.DomUtil.setPosition(canvasOverlay, topLeft);
    renderGlow();
  });

  map.on('zoom', resizeCanvas);
  map.on('resize', resizeCanvas);
  resizeCanvas();

  map.on('click', handleMapClick);
}

// 3. Завантаження датасетів
async function loadDatasets() {
  try {
    // 1. Повна база 25 897 сіл та міст України
    const res25k = await fetch('data/settlements_25k.json');
    const json25k = await res25k.json();
    settlements25k = json25k.points; // [lat, lon, name, cat, group]

    // 2. Датасет 1315 громад
    fetch('data/hromadas_points.json').then(r => r.json()).then(j => { hromadasData = j.districts; });

    // Межі областей України для фону
    const resGeo = await fetch('data/ukraine_full.geojson');
    const ukraineGeoJson = await resGeo.json();
    L.geoJSON(ukraineGeoJson, {
      style: {
        color: '#263445',
        weight: 1.2,
        opacity: 0.5,
        fillColor: '#070b12',
        fillOpacity: 0.15
      }
    }).addTo(map);

    updateTime(currentHour);
  } catch (err) {
    console.error('Помилка завантаження геоданих:', err);
  }
}

// Завантаження живих даних з 2 700+ датчиків СвітлоБота (svitlobot.in.ua)
async function loadSvitlobotData() {
  if (isSvitlobotLoading) return;
  isSvitlobotLoading = true;
  try {
    const res = await fetch('https://api.svitlobot.in.ua/website/getChannelsForMap');
    const text = await res.text();
    const lines = text.trim().split('\n');
    const points = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!line || line.length < 5) continue;
      const parts = line.split(';&&&;');
      if (parts.length >= 8) {
        const status = parseInt(parts[1].trim(), 10);
        const lat = parseFloat(parts[6].trim());
        const lon = parseFloat(parts[7].trim());
        if (isNaN(lat) || isNaN(lon)) continue;

        points.push({
          status: isNaN(status) ? 0 : status,
          time: parts[2] ? parts[2].trim() : '',
          name: parts[3] ? parts[3].trim() : 'Датчик СвітлоБот',
          tg: parts[4] ? parts[4].trim() : '',
          users: parseInt(parts[5].trim(), 10) || 0,
          lat: lat,
          lon: lon,
          groupName: parts[9] ? parts[9].trim() : '',
          isSvitlobot: true
        });
      }
    }
    svitlobotData = points;
    isSvitlobotLoading = false;
    renderGlow();
  } catch (err) {
    console.error('Помилка завантаження даних СвітлоБота:', err);
    isSvitlobotLoading = false;
  }
}

// 4. ЯДРО: Рендеринг через Canvas з Frustum Culling
function renderGlow() {
  if (!ctx) return;

  const width = map.getSize().x;
  const height = map.getSize().y;
  ctx.clearRect(0, 0, width, height);

  const bounds = map.getBounds();
  const south = bounds.getSouth() - 0.15;
  const north = bounds.getNorth() + 0.15;
  const west = bounds.getWest() - 0.2;
  const east = bounds.getEast() + 0.2;

  const zoom = map.getZoom();
  const groupFilter = selectedGroup === 'all' ? null : selectedGroup === 'none' ? 'none' : parseInt(selectedGroup, 10);

  let onCount = 0;
  let maybeCount = 0;
  let offCount = 0;

  if (activeDataset === 'svitlobot') {
    if (!svitlobotData.length) {
      if (!isSvitlobotLoading) loadSvitlobotData();
      return;
    }
    const isFar = zoom <= 7;
    const r = isFar ? Math.max(3.5, (zoom - 4) * 1.8) : Math.max(7.0, (zoom - 4) * 3.0);

    for (let i = 0; i < svitlobotData.length; i++) {
      const p = svitlobotData[i];
      if (p.lat < south || p.lat > north || p.lon < west || p.lon > east) continue;

      const pt = map.latLngToContainerPoint([p.lat, p.lon]);

      if (p.status === 1) {
        onCount++;
        drawSettlementGlow(pt.x, pt.y, r, 1.0, 1, isFar);
      } else if (p.status === 2) {
        offCount++;
        drawExtinguishedPoint(pt.x, pt.y, 1, isFar, zoom);
      } else {
        maybeCount++;
        drawPausedSensorPoint(pt.x, pt.y, Math.max(2.0, r * 0.45));
      }
    }
  } else if (activeDataset === 'settlements_25k') {
    if (!settlements25k.length) return;

    // Масштабні коефіцієнти залежно від зуму
    // На рівні країни (zoom 5-7) села мають бути мініатюрними точками, щоб створювати "космічне сяйво"
    const isFar = zoom <= 7;
    const villageRadius = isFar ? Math.max(1.0, (zoom - 4) * 0.7) : Math.max(2.5, (zoom - 6) * 1.8);
    const townRadius = isFar ? Math.max(2.5, (zoom - 4) * 1.5) : Math.max(5.0, (zoom - 5) * 2.8);
    const cityRadius = isFar ? Math.max(6.0, (zoom - 4) * 3.0) : Math.max(12.0, (zoom - 4) * 4.5);

    for (let i = 0; i < settlements25k.length; i++) {
      const p = settlements25k[i]; // [lat, lon, name, cat, group]
      const lat = p[0];
      const lon = p[1];

      // Швидке просторове відсікання за межами екрана (Frustum Culling)
      if (lat < south || lat > north || lon < west || lon > east) {
        continue;
      }

      const grp = p[4];
      if (groupFilter !== null && groupFilter !== 'none' && grp !== groupFilter) {
        continue;
      }

      // Якщо режим 0 черг — світло є скрізь 24/7!
      const state = groupFilter === 'none' ? 'on' : SCHEDULE_PATTERNS[grp][currentHour];
      const cat = p[3]; // 1 = місто, 2 = смт, 3 = село

      if (state === 'on') onCount++;
      else if (state === 'maybe') maybeCount++;
      else offCount++;

      const pt = map.latLngToContainerPoint([lat, lon]);

      if (state === 'on') {
        const r = cat === 1 ? cityRadius : cat === 2 ? townRadius : villageRadius;
        drawSettlementGlow(pt.x, pt.y, r, 1.0, cat, isFar);
      } else if (state === 'maybe') {
        const r = (cat === 1 ? cityRadius : cat === 2 ? townRadius : villageRadius) * 0.75;
        drawSettlementGlow(pt.x, pt.y, r, 0.45, cat, isFar);
      } else {
        drawExtinguishedPoint(pt.x, pt.y, cat, isFar, zoom);
      }
    }
  } else {
    // Режим 'hromadas'
    const list = hromadasData;
    const zoomFactor = Math.max(0.5, (zoom - 4) * 0.4);

    list.forEach(p => {
      if (p.lat < south || p.lat > north || p.lon < west || p.lon > east) return;
      if (groupFilter !== null && groupFilter !== 'none' && p.group !== groupFilter) return;

      const state = groupFilter === 'none' ? 'on' : p.hourly_schedule[currentHour];
      const isMajor = p.importance === 'high';
      const r = isMajor ? Math.max(14, Math.min(50, 16 * zoomFactor)) : Math.max(7, Math.min(24, 7.5 * zoomFactor));

      if (state === 'on') onCount++;
      else if (state === 'maybe') maybeCount++;
      else offCount++;

      const pt = map.latLngToContainerPoint([p.lat, p.lon]);
      if (state === 'on') drawSettlementGlow(pt.x, pt.y, r, 1.0, isMajor ? 1 : 2, false);
      else if (state === 'maybe') drawSettlementGlow(pt.x, pt.y, r * 0.75, 0.45, isMajor ? 1 : 2, false);
      else drawExtinguishedPoint(pt.x, pt.y, isMajor ? 1 : 2, false, zoom);
    });
  }

  document.getElementById('countOn').textContent = onCount;
  document.getElementById('countMaybe').textContent = maybeCount;
  document.getElementById('countOff').textContent = offCount;

  if (hromadasGeoLayer) {
    hromadasGeoLayer.setStyle(getHromadaPolygonStyle);
  }
}

/**
 * Фізичне статичне світіння населеного пункту (Screen Additive Bloom)
 */
function drawSettlementGlow(x, y, radius, intensity, cat, isFar) {
  ctx.save();
  ctx.globalCompositeOperation = 'screen';

  if (cat === 3 && isFar) {
    // Оптимізація для 24 000 сіл на загальній карті України:
    // Маленькі теплі світлові зерна, які зливаються в зоряний чумацький шлях
    ctx.fillStyle = intensity >= 0.8 ? 'rgba(255, 215, 60, 0.65)' : 'rgba(220, 150, 30, 0.3)';
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    return;
  }

  // Для міст, смт або при наближенні — повний радіальний градієнт
  const grad = ctx.createRadialGradient(x, y, 0, x, y, radius);

  if (intensity >= 0.8) {
    grad.addColorStop(0.00, 'rgba(255, 255, 240, 0.98)');   // Гаряче біло-золоте ядро
    grad.addColorStop(0.15, 'rgba(255, 225, 80, 0.85)');    // Теплий бурштиновий спалах
    grad.addColorStop(0.40, 'rgba(255, 170, 30, 0.38)');    // Ореол
    grad.addColorStop(0.75, 'rgba(230, 120, 10, 0.08)');    // Атмосферне розсіювання
    grad.addColorStop(1.00, 'rgba(0, 0, 0, 0)');
  } else {
    grad.addColorStop(0.00, 'rgba(255, 235, 160, 0.60)');
    grad.addColorStop(0.20, 'rgba(235, 175, 50, 0.38)');
    grad.addColorStop(0.50, 'rgba(200, 120, 20, 0.12)');
    grad.addColorStop(1.00, 'rgba(0, 0, 0, 0)');
  }

  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, Math.PI * 2);
  ctx.fill();

  // Центральна точка
  if (cat <= 2 || !isFar) {
    ctx.fillStyle = intensity >= 0.8 ? '#ffffff' : '#ffd000';
    ctx.beginPath();
    ctx.arc(x, y, Math.max(1.0, radius * 0.1), 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.restore();
}

/**
 * Знеструмлена точка — Темно-синій холодний індикатор із градацією розмірів
 * (Міста помітно більші за села, пропорційно масштабу, як і світлоточки)
 */
function drawExtinguishedPoint(x, y, cat, isFar, zoom) {
  ctx.save();

  let r;
  if (cat === 1) {
    // Міста: помітно більший радіус
    r = isFar ? Math.max(3.6, (zoom - 4) * 1.6) : Math.max(6.0, (zoom - 4) * 2.5);
  } else if (cat === 2) {
    // Смт
    r = isFar ? Math.max(2.2, (zoom - 4) * 1.0) : Math.max(3.8, (zoom - 5) * 1.5);
  } else {
    // Села
    r = isFar ? Math.max(1.3, (zoom - 4) * 0.5) : Math.max(2.0, (zoom - 5) * 0.9);
  }

  // Для міст малюємо легкий холодний темно-синій ореол, щоб підкреслити масштаб знеструмлення
  if (cat === 1 && r >= 3.5) {
    const halo = ctx.createRadialGradient(x, y, r * 0.4, x, y, r * 2.0);
    halo.addColorStop(0, 'rgba(30, 58, 138, 0.45)');
    halo.addColorStop(0.7, 'rgba(15, 23, 42, 0.15)');
    halo.addColorStop(1, 'rgba(15, 23, 42, 0)');
    ctx.fillStyle = halo;
    ctx.beginPath();
    ctx.arc(x, y, r * 2.0, 0, Math.PI * 2);
    ctx.fill();
  }

  // Насичене темно-синє ядро
  ctx.fillStyle = cat === 1 ? '#172554' : cat === 2 ? '#1e293b' : '#0f172a';
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();

  // Контрастний холодний обідок (блакитний електрик)
  ctx.strokeStyle = cat === 1 ? 'rgba(96, 165, 250, 0.85)' : cat === 2 ? 'rgba(96, 165, 250, 0.65)' : 'rgba(96, 165, 250, 0.45)';
  ctx.lineWidth = cat === 1 ? 1.2 : 0.8;
  ctx.stroke();

  ctx.restore();
}

/**
 * Неактивний датчик (Технічна перерва / немає зв'язку)
 */
function drawPausedSensorPoint(x, y, r) {
  ctx.save();
  ctx.fillStyle = '#475569';
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = 'rgba(148, 163, 184, 0.4)';
  ctx.lineWidth = 0.8;
  ctx.stroke();
  ctx.restore();
}

// 5. Контури громад
async function toggleHromadasPolygons() {
  if (showPolygons) {
    if (hromadasGeoLayer) {
      map.removeLayer(hromadasGeoLayer);
      hromadasGeoLayer = null;
    }
    showPolygons = false;
    document.getElementById('btnTogglePolygons').classList.remove('active');
  } else {
    showPolygons = true;
    document.getElementById('btnTogglePolygons').classList.add('active');
    if (!hromadasGeoLayer) {
      const res = await fetch('data/hromadas_boundaries.geojson');
      const geo = await res.json();
      hromadasGeoLayer = L.geoJSON(geo, {
        style: getHromadaPolygonStyle
      }).addTo(map);
    }
  }
}

function getHromadaPolygonStyle(feature) {
  const grp = feature.properties.group || 1;
  const state = SCHEDULE_PATTERNS[grp][currentHour];

  if (state === 'on') {
    return { color: '#ffd000', weight: 1, opacity: 0.45, fillColor: '#ffbb00', fillOpacity: 0.12 };
  } else if (state === 'maybe') {
    return { color: '#f59e0b', weight: 0.8, opacity: 0.35, fillColor: '#b45309', fillOpacity: 0.08 };
  } else {
    return { color: '#1e293b', weight: 0.6, opacity: 0.3, fillColor: '#0a0f18', fillOpacity: 0.25 };
  }
}

// 6. Клік по карті для пошуку найближчого населеного пункту
function handleMapClick(e) {
  const clickPoint = map.latLngToContainerPoint(e.latlng);
  let closest = null;
  let minDist = 25;

  if (activeDataset === 'svitlobot') {
    for (let i = 0; i < svitlobotData.length; i++) {
      const p = svitlobotData[i];
      const pt = map.latLngToContainerPoint([p.lat, p.lon]);
      const dist = Math.hypot(pt.x - clickPoint.x, pt.y - clickPoint.y);
      if (dist < minDist) {
        minDist = dist;
        closest = p;
      }
    }
  } else if (activeDataset === 'settlements_25k') {
    for (let i = 0; i < settlements25k.length; i++) {
      const p = settlements25k[i];
      const pt = map.latLngToContainerPoint([p[0], p[1]]);
      const dist = Math.hypot(pt.x - clickPoint.x, pt.y - clickPoint.y);
      if (dist < minDist) {
        minDist = dist;
        closest = {
          name: p[2],
          city: p[2],
          category: CAT_NAMES[p[3]],
          group: p[4],
          lat: p[0],
          lon: p[1],
          hourly_schedule: SCHEDULE_PATTERNS[p[4]]
        };
      }
    }
  } else {
    const list = hromadasData;
    list.forEach(p => {
      const pt = map.latLngToContainerPoint([p.lat, p.lon]);
      const dist = Math.hypot(pt.x - clickPoint.x, pt.y - clickPoint.y);
      if (dist < minDist) {
        minDist = dist;
        closest = p;
      }
    });
  }

  if (closest) {
    showItemCard(closest);
  }
}

// 7. Відкриття картки населеного пункту з добовим графіком
function showItemCard(item) {
  activeItem = item;
  const card = document.getElementById('districtCard');
  const badge = document.getElementById('cardStatusBadge');

  if (item.isSvitlobot) {
    document.getElementById('cardTitle').textContent = item.name;
    document.getElementById('cardRayon').textContent = 'Живий датчик (Телеметрія)';
    document.getElementById('cardRegion').textContent = item.groupName || 'СвітлоБот Україна';
    document.getElementById('cardOperator').textContent = item.tg ? `Канал: @${item.tg}` : 'СвітлоБот';
    document.getElementById('cardGroupNum').textContent = item.status === 1 ? 'Світло є (Online)' : item.status === 2 ? 'Знеструмлено (Offline)' : 'Зв’язок відсутній';

    badge.className = 'card-status-badge';
    if (item.status === 1) {
      badge.textContent = 'Світло є (Фактично онлайн)';
      badge.classList.add('badge-on');
    } else if (item.status === 2) {
      badge.textContent = 'Знеструмлено (Фактично офлайн)';
      badge.classList.add('badge-off');
    } else {
      badge.textContent = 'Немає зв’язку з датчиком';
      badge.classList.add('badge-maybe');
    }

    const mini = document.getElementById('miniTimeline');
    mini.innerHTML = '';
    if (item.tg) {
      const btn = document.createElement('a');
      btn.href = `https://t.me/${item.tg}`;
      btn.target = '_blank';
      btn.rel = 'noopener noreferrer';
      btn.className = 'btn-tg-channel';
      btn.innerHTML = '✈️ Перейти до Telegram-каналу';
      mini.appendChild(btn);
    }
    const info = document.createElement('div');
    info.style.fontSize = '11px';
    info.style.color = '#94a3b8';
    info.style.marginTop = '10px';
    info.style.lineHeight = '1.4';
    const dateStr = item.time ? new Date(item.time).toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' }) : '';
    info.innerHTML = `Час оновлення: <b>${dateStr}</b><br>Підписників каналу: <b>${item.users}</b><br><span style="color:#64748b">Джерело: svitlobot.in.ua</span>`;
    mini.appendChild(info);

    card.style.display = 'block';
    return;
  }

  const state = item.hourly_schedule ? item.hourly_schedule[currentHour] : 'on';

  document.getElementById('cardTitle').textContent = item.name;
  document.getElementById('cardRayon').textContent = item.category || item.rayon || '';
  document.getElementById('cardRegion').textContent = item.region || 'ОЕС України';
  document.getElementById('cardOperator').textContent = item.operator || 'ДТЕК / Обленерго';
  document.getElementById('cardGroupNum').textContent = `Черга ${item.group}`;

  badge.className = 'card-status-badge';
  if (state === 'on') {
    badge.textContent = 'Світло є (За планом)';
    badge.classList.add('badge-on');
  } else if (state === 'maybe') {
    badge.textContent = 'Сіра зона (Можливе відключення)';
    badge.classList.add('badge-maybe');
  } else {
    badge.textContent = 'Знеструмлено (Графік відключень)';
    badge.classList.add('badge-off');
  }

  const mini = document.getElementById('miniTimeline');
  mini.innerHTML = '';
  item.hourly_schedule.forEach((s, idx) => {
    const bar = document.createElement('div');
    bar.className = `mini-bar bar-${s}`;
    if (idx === currentHour) bar.classList.add('current');
    bar.title = `${idx}:00 — ${s === 'on' ? 'Світло є' : s === 'maybe' ? 'Сіра зона' : 'Відключено'}`;
    mini.appendChild(bar);
  });

  card.style.display = 'block';
}

// 8. Оновлення години
function updateTime(hour) {
  currentHour = hour;
  const formattedTime = (hour < 10 ? '0' : '') + hour + ':00';
  document.getElementById('timeDisplay').textContent = formattedTime;
  document.getElementById('hourSlider').value = hour;

  renderGlow();

  if (activeItem) {
    showItemCard(activeItem);
  }
}

// 9. Налаштування UI та швидкого пошуку
function setupUIEvents() {
  const slider = document.getElementById('hourSlider');
  slider.addEventListener('input', (e) => {
    if (isPlaying) stopPlay();
    updateTime(parseInt(e.target.value, 10));
  });

  document.getElementById('btnLive').addEventListener('click', () => {
    if (isPlaying) stopPlay();
    const liveHour = new Date().getHours();
    updateTime(liveHour);
  });

  const btnPlay = document.getElementById('btnPlay');
  btnPlay.addEventListener('click', () => {
    if (isPlaying) stopPlay();
    else startPlay();
  });

  function startPlay() {
    isPlaying = true;
    btnPlay.textContent = '⏸';
    playInterval = setInterval(() => {
      let next = (currentHour + 1) % 24;
      updateTime(next);
    }, 1100);
  }

  function stopPlay() {
    isPlaying = false;
    btnPlay.textContent = '▶';
    if (playInterval) clearInterval(playInterval);
  }

  document.getElementById('btnCloseCard').addEventListener('click', () => {
    document.getElementById('districtCard').style.display = 'none';
    activeItem = null;
  });

  // Перемикачі шарів
  const btn25k = document.getElementById('btnLayer25k');
  const btnHromadas = document.getElementById('btnLayerHromadas');
  const btnSvitlobot = document.getElementById('btnLayerSvitlobot');

  btn25k.addEventListener('click', () => {
    btn25k.classList.add('active');
    btnHromadas.classList.remove('active');
    btnSvitlobot.classList.remove('active');
    activeDataset = 'settlements_25k';
    renderGlow();
  });

  btnHromadas.addEventListener('click', () => {
    btnHromadas.classList.add('active');
    btn25k.classList.remove('active');
    btnSvitlobot.classList.remove('active');
    activeDataset = 'hromadas';
    renderGlow();
  });

  btnSvitlobot.addEventListener('click', () => {
    btnSvitlobot.classList.add('active');
    btn25k.classList.remove('active');
    btnHromadas.classList.remove('active');
    activeDataset = 'svitlobot';
    if (!svitlobotData.length) {
      loadSvitlobotData();
    } else {
      renderGlow();
    }
  });

  document.getElementById('btnTogglePolygons').addEventListener('click', toggleHromadasPolygons);

  document.getElementById('groupSelect').addEventListener('change', (e) => {
    selectedGroup = e.target.value;
    renderGlow();
  });

  // Пошук із автодоповненням
  const searchInput = document.getElementById('searchInput');
  const searchResults = document.getElementById('searchResults');

  searchInput.addEventListener('input', (e) => {
    const val = e.target.value.trim().toLowerCase();
    if (val.length < 2) {
      searchResults.style.display = 'none';
      return;
    }

    let matches = [];
    if (activeDataset === 'svitlobot') {
      matches = svitlobotData.filter(p => p.name.toLowerCase().includes(val)).slice(0, 8).map(p => ({
        name: p.name,
        catName: p.groupName || 'Датчик',
        group: p.status === 1 ? 'Світло є' : 'Офлайн',
        lat: p.lat,
        lon: p.lon,
        isSvitlobot: true,
        status: p.status,
        time: p.time,
        tg: p.tg,
        users: p.users
      }));
    } else if (activeDataset === 'settlements_25k') {
      for (let i = 0; i < settlements25k.length; i++) {
        const p = settlements25k[i];
        if (p[2].toLowerCase().includes(val)) {
          matches.push({
            name: p[2],
            catName: CAT_NAMES[p[3]],
            group: p[4],
            lat: p[0],
            lon: p[1]
          });
          if (matches.length >= 8) break;
        }
      }
    } else {
      const list = hromadasData;
      matches = list.filter(p => p.name.toLowerCase().includes(val)).slice(0, 8).map(p => ({
        name: p.name,
        catName: p.rayon || '',
        group: p.group,
        lat: p.lat,
        lon: p.lon
      }));
    }

    if (!matches.length) {
      searchResults.style.display = 'none';
      return;
    }

    searchResults.innerHTML = '';
    matches.forEach(m => {
      const item = document.createElement('div');
      item.className = 'search-item';
      item.innerHTML = `
        <div class="search-item-title">${m.name}</div>
        <div class="search-item-sub">${m.catName} • ${m.group}</div>
      `;
      item.addEventListener('click', () => {
        map.flyTo([m.lat, m.lon], 12, { duration: 1.2 });
        if (m.isSvitlobot) {
          showItemCard(m);
        } else {
          showItemCard({
            name: m.name,
            category: m.catName,
            group: m.group,
            hourly_schedule: SCHEDULE_PATTERNS[m.group]
          });
        }
        searchResults.style.display = 'none';
        searchInput.value = m.name;
      });
      searchResults.appendChild(item);
    });
    searchResults.style.display = 'block';
  });

  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      searchResults.style.display = 'none';
    }
  });

  // Автоматична синхронізація часу за годинником та автооновлення даних СвітлоБота
  setInterval(() => {
    if (!isPlaying) {
      const realHour = new Date().getHours();
      if (realHour !== currentHour) {
        updateTime(realHour);
      }
    }
    if (activeDataset === 'svitlobot') {
      loadSvitlobotData();
    }
  }, 30000);
}

window.addEventListener('DOMContentLoaded', initMap);
