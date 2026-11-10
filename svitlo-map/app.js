/**
 * СвітлоКарта України — 25 800+ Населених Пунктів за графіками відключень
 * Високопродуктивний Canvas-рушій із просторовим відсіканням (Frustum Culling)
 */

let map;
let canvasOverlay;
let ctx;
let activeDataset = 'settlements_25k'; // 'settlements_25k' (25.8k населених пунктів), 'hromadas' (1.3k)
let colorDataSource = 'schedule'; // 'schedule' (погодинний графік доби) або 'svitlobot' (фактичний стан за 2 700+ датчиками)
let settlements25k = [];
let hromadasData = [];
let svitlobotSensors = [];
let svitlobotGrid = new Map();
let svitlobotCellStats = new Map();
let isSvitlobotLoading = false;
let hromadasGeoLayer = null;
let showPolygons = false;
let currentHour = new Date().getHours();
let isPlaying = false;
let playInterval = null;
let activeItem = null;

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

    // Фонове оновлення фактичного стану за датчиками СвітлоБота для автоматичного визначення 0 черг
    loadSvitlobotData();

    // Автоматичне періодичне оновлення телеметрії кожні 5 хвилин
    setInterval(loadSvitlobotData, 5 * 60 * 1000);

    // Автоматична синхронізація години у реальному часі кожну хвилину
    setInterval(() => {
      if (!isPlaying) {
        const nowHour = new Date().getHours();
        if (nowHour !== currentHour) {
          updateTime(nowHour);
        }
      }
    }, 60 * 1000);
  } catch (err) {
    console.error('Помилка завантаження геоданих:', err);
  }
}

// Завантаження живих даних з 2 700+ датчиків СвітлоБота (svitlobot.in.ua)
async function loadSvitlobotData() {
  if (isSvitlobotLoading) return;
  isSvitlobotLoading = true;
  try {
    let res;
    try {
      res = await fetch('/api/svitlobot');
      if (!res.ok) throw new Error('Proxy status: ' + res.status);
    } catch (e) {
      // Фолбек для локальної розробки або якщо проксі недоступний
      res = await fetch('https://api.svitlobot.in.ua/website/getChannelsForMap');
    }
    const text = await res.text();
    const lines = text.trim().split('\n');
    const sensors = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!line || line.length < 5) continue;
      const parts = line.split(';&&&;');
      if (parts.length >= 8) {
        const status = parseInt(parts[1].trim(), 10);
        const lat = parseFloat(parts[6].trim());
        const lon = parseFloat(parts[7].trim());
        if ((status === 1 || status === 2) && !isNaN(lat) && !isNaN(lon)) {
          sensors.push({
            status: status,
            lat: lat,
            lon: lon,
            name: parts[3] ? parts[3].trim() : 'Датчик СвітлоБот',
            tg: parts[4] ? parts[4].trim() : '',
            time: parts[2] ? parts[2].trim() : ''
          });
        }
      }
    }
    svitlobotSensors = sensors;

    // Швидка просторова сітка для миттєвої інтерполяції кольорів точок (~20-30 км)
    svitlobotGrid.clear();
    sensors.forEach(s => {
      const key = Math.floor(s.lat * 5) + '_' + Math.floor(s.lon * 5);
      if (!svitlobotGrid.has(key)) svitlobotGrid.set(key, []);
      svitlobotGrid.get(key).push(s);
    });

    // Агрегація регіональної телеметрії для динамічного виявлення зон з 0 чергами
    svitlobotCellStats.clear();
    sensors.forEach(s => {
      const key = Math.floor(s.lat * 3.33) + '_' + Math.floor(s.lon * 3.33);
      if (!svitlobotCellStats.has(key)) svitlobotCellStats.set(key, { on: 0, off: 0 });
      const c = svitlobotCellStats.get(key);
      if (s.status === 1) c.on++;
      else if (s.status === 2) c.off++;
    });

    isSvitlobotLoading = false;
    // Оновлюємо карту з урахуванням виявлених зон 0 черг
    renderGlow();
    if (activeItem) {
      showItemCard(activeItem);
    }
  } catch (err) {
    console.error('Помилка завантаження даних СвітлоБота:', err);
    isSvitlobotLoading = false;
  }
}

/**
 * Визначає статус точки (світло є / відключено) за найближчими датчиками СвітлоБота
 */
function getSvitlobotStatus(lat, lon, fallbackState) {
  if (!svitlobotSensors.length) return fallbackState || 'on';

  const cLat = Math.floor(lat * 5);
  const cLon = Math.floor(lon * 5);
  let bestDist = 999;
  let bestStatus = null;

  for (let dlat = -2; dlat <= 2; dlat++) {
    for (let dlon = -2; dlon <= 2; dlon++) {
      const cell = svitlobotGrid.get((cLat + dlat) + '_' + (cLon + dlon));
      if (cell) {
        for (let i = 0; i < cell.length; i++) {
          const s = cell[i];
          const d = (s.lat - lat) * (s.lat - lat) + (s.lon - lon) * (s.lon - lon);
          if (d < bestDist && d < 0.45) { // радіус пошуку ~75 км
            bestDist = d;
            bestStatus = s.status;
          }
        }
      }
    }
  }

  if (bestStatus === 1) return 'on';
  if (bestStatus === 2) return 'off';
  return fallbackState || 'on';
}

/**
 * Перевірка, чи діє в локації режим 0 черг Укренерго (обмеження не застосовуються, світло 24/7).
 * Обчислюється комбіновано:
 * 1. Гарантовані карпатські/прикарпатські енерговузли (Івано-Франківщина/Яремче, Закарпаття, Буковина).
 * 2. Динамічний аналіз телеметрії СвітлоБота: якщо в навколишньому секторі (~35 км) >= 3 датчиків і
 *    понад 88% мають живлення (або 0 вимкнень), цей сектор функціонує в режимі 0 черг.
 */
function isZeroQueuesLocation(lat, lon) {
  // 1. Прикарпаття / Івано-Франківська обл. (включно з Яремче, Надвірною, Карпатами, Коломиєю)
  if (lat >= 47.7 && lat <= 49.3 && lon >= 23.5 && lon <= 25.7) return true;
  // Закарпатська область
  if (lat >= 47.8 && lat <= 49.3 && lon >= 22.0 && lon <= 24.3) return true;
  // Чернівецька область (Буковина)
  if (lat >= 47.7 && lat <= 48.7 && lon >= 24.8 && lon <= 27.5) return true;

  // 2. Динамічна верифікація за телеметрією СвітлоБота
  if (svitlobotSensors.length > 0) {
    const cLat = Math.floor(lat * 3.33);
    const cLon = Math.floor(lon * 3.33);
    let totalOn = 0;
    let totalOff = 0;

    for (let dlat = -1; dlat <= 1; dlat++) {
      for (let dlon = -1; dlon <= 1; dlon++) {
        const c = svitlobotCellStats.get((cLat + dlat) + '_' + (cLon + dlon));
        if (c) {
          totalOn += c.on;
          totalOff += c.off;
        }
      }
    }

    const total = totalOn + totalOff;
    if (total >= 3) {
      const pct = totalOn / total;
      if (totalOff === 0 || pct >= 0.88) {
        return true;
      }
    }
  }

  return false;
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

  let onCount = 0;
  let maybeCount = 0;
  let offCount = 0;

  if (activeDataset === 'settlements_25k') {
    if (!settlements25k.length) return;

    // Масштабні коефіцієнти залежно від зуму
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

      // Розрахунок статусу: або за СвітлоБотом, або за розкладом ГПВ із врахуванням 0 черг
      let state;
      if (colorDataSource === 'svitlobot') {
        state = getSvitlobotStatus(lat, lon, 'on');
      } else if (isZeroQueuesLocation(lat, lon)) {
        // Регіони без обмежень (0 черг Укренерго) — світло є 24/7 (жодних синіх кіл!)
        state = 'on';
      } else {
        state = SCHEDULE_PATTERNS[grp][currentHour];
      }

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
    // Режим 'hromadas' (1.3k громад)
    const list = hromadasData;
    const zoomFactor = Math.max(0.5, (zoom - 4) * 0.4);

    list.forEach(p => {
      if (p.lat < south || p.lat > north || p.lon < west || p.lon > east) return;

      let state;
      if (colorDataSource === 'svitlobot') {
        state = getSvitlobotStatus(p.lat, p.lon, 'on');
      } else if (isZeroQueuesLocation(p.lat, p.lon)) {
        state = 'on'; // Режим 0 черг — без синіх кіл!
      } else {
        state = p.hourly_schedule[currentHour];
      }

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
 * Знеструмлена точка — Чіткий неоново-сапфіровий індикатор (Goldilocks calibration)
 * 1. Оптимальний калібрований радіус: чітко видно на будь-якому зумі, але не роздувається у плями.
 * 2. Насичене напівпрозоре темно-синє ядро rgba(30, 58, 138, 0.7) — не зливається з чорним фоном.
 * 3. Яскравий, контрастний неоновий контур cyan (#38bdf8) для безпомилкової читабельності.
 */
function drawExtinguishedPoint(x, y, cat, isFar, zoom) {
  ctx.save();

  let r;
  if (cat === 1) {
    // Міста: помітні чіткі неонові вузли (~5-6px)
    r = isFar ? Math.max(2.8, (zoom - 4) * 0.9) : Math.max(4.8, (zoom - 5) * 1.4);
  } else if (cat === 2) {
    // Смт (~3px)
    r = isFar ? Math.max(1.8, (zoom - 4) * 0.6) : Math.max(3.0, (zoom - 5) * 0.9);
  } else {
    // Села: чітко видимі електричні цятки (~1.8-2.2px)
    r = isFar ? Math.max(1.2, (zoom - 4) * 0.35) : Math.max(1.7, (zoom - 5) * 0.5);
  }

  // М'який неоновий ореол сенсора для міст і смт
  if (cat <= 2 && r >= 2.5) {
    const glow = ctx.createRadialGradient(x, y, r * 0.5, x, y, r * 1.8);
    glow.addColorStop(0, 'rgba(56, 189, 248, 0.45)');
    glow.addColorStop(0.6, 'rgba(30, 58, 138, 0.18)');
    glow.addColorStop(1, 'rgba(15, 23, 42, 0)');
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(x, y, r * 1.8, 0, Math.PI * 2);
    ctx.fill();
  }

  // Насичена напівпрозора основа — контрастна до чорного фону
  ctx.fillStyle = cat === 1 ? 'rgba(30, 58, 138, 0.75)' : cat === 2 ? 'rgba(30, 58, 138, 0.65)' : 'rgba(23, 37, 84, 0.60)';
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();

  // Яскравий контрастний неоновий обідок (Cyan / Electric Blue)
  ctx.strokeStyle = cat === 1 ? '#38bdf8' : cat === 2 ? 'rgba(56, 189, 248, 0.90)' : 'rgba(56, 189, 248, 0.75)';
  ctx.lineWidth = cat === 1 ? 1.2 : cat === 2 ? 1.0 : 0.85;
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

  if (activeDataset === 'settlements_25k') {
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

  const isZero = isZeroQueuesLocation(item.lat, item.lon);
  let state;
  if (colorDataSource === 'svitlobot') {
    state = getSvitlobotStatus(item.lat, item.lon, 'on');
  } else if (isZero) {
    state = 'on';
  } else {
    state = item.hourly_schedule ? item.hourly_schedule[currentHour] : 'on';
  }

  document.getElementById('cardTitle').textContent = item.name;
  document.getElementById('cardRayon').textContent = item.category || item.rayon || '';
  document.getElementById('cardRegion').textContent = item.region || 'ОЕС України';
  document.getElementById('cardOperator').textContent = item.operator || 'ДТЕК / Обленерго';
  document.getElementById('cardGroupNum').textContent = isZero
    ? 'Режим 0 черг (Обмежень не застосовується • Світло 24/7)'
    : (colorDataSource === 'svitlobot' ? `Черга ${item.group} • СвітлоБот Live` : `Черга ${item.group}`);

  badge.className = 'card-status-badge';
  if (state === 'on') {
    badge.textContent = isZero ? 'Світло є (0 черг Укренерго)' : (colorDataSource === 'svitlobot' ? 'Світло є (За даними СвітлоБота)' : 'Світло є');
    badge.classList.add('badge-on');
  } else if (state === 'maybe') {
    badge.textContent = 'Сіра зона (Можливе відключення)';
    badge.classList.add('badge-maybe');
  } else {
    badge.textContent = colorDataSource === 'svitlobot' ? 'Знеструмлено (За даними СвітлоБота)' : 'Знеструмлено (Графік)';
    badge.classList.add('badge-off');
  }

  const mini = document.getElementById('miniTimeline');
  mini.innerHTML = '';
  if (colorDataSource === 'svitlobot') {
    const info = document.createElement('div');
    info.style.fontSize = '12px';
    info.style.color = '#94a3b8';
    info.style.lineHeight = '1.5';
    info.style.padding = '8px 0';
    info.innerHTML = `Статус населеного пункту визначено на основі найближчих онлайн-датчиків мережі <b>СвітлоБот</b>.<br><span style="color:#38bdf8">Фактичний стан: ${state === 'on' ? '🟢 Живлення присутнє' : '🔵 Зафіксовано знеструмлення'}</span>`;
    mini.appendChild(info);
  } else if (isZero) {
    // 0 черг — графік не застосовується, живлення цілодобове
    for (let idx = 0; idx < 24; idx++) {
      const bar = document.createElement('div');
      bar.className = 'mini-bar bar-on';
      if (idx === currentHour) bar.classList.add('current');
      bar.title = `${idx}:00 — Світло є (0 черг)`;
      mini.appendChild(bar);
    }
    const info = document.createElement('div');
    info.style.fontSize = '11px';
    info.style.color = '#38bdf8';
    info.style.marginTop = '6px';
    info.textContent = '⚡ У цьому регіоні наразі діє 0 черг ГПВ (обмеження не застосовуються)';
    mini.appendChild(info);
  } else if (item.hourly_schedule) {
    item.hourly_schedule.forEach((s, idx) => {
      const bar = document.createElement('div');
      bar.className = `mini-bar bar-${s}`;
      if (idx === currentHour) bar.classList.add('current');
      bar.title = `${idx}:00 — ${s === 'on' ? 'Світло є' : s === 'maybe' ? 'Сіра зона' : 'Відключено'}`;
      mini.appendChild(bar);
    });
  }

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

  // Перемикачі шарів пунктів (25.8k сіл/міст або 1.3k громад)
  const btn25k = document.getElementById('btnLayer25k');
  const btnHromadas = document.getElementById('btnLayerHromadas');

  btn25k.addEventListener('click', () => {
    btn25k.classList.add('active');
    btnHromadas.classList.remove('active');
    activeDataset = 'settlements_25k';
    renderGlow();
  });

  btnHromadas.addEventListener('click', () => {
    btnHromadas.classList.add('active');
    btn25k.classList.remove('active');
    activeDataset = 'hromadas';
    renderGlow();
  });

  // Перемикачі джерела кольорів точок:
  // 📅 За графіком ГПВ (жовті/сині за розкладом доби)
  // 📡 СвітлоБот Live (жовті/сині за фактичними даними 2 700+ датчиків)
  const btnSourceSchedule = document.getElementById('btnSourceSchedule');
  const btnSourceSvitlobot = document.getElementById('btnSourceSvitlobot');

  btnSourceSchedule.addEventListener('click', () => {
    btnSourceSchedule.classList.add('active');
    btnSourceSvitlobot.classList.remove('active');
    colorDataSource = 'schedule';
    renderGlow();
  });

  btnSourceSvitlobot.addEventListener('click', () => {
    btnSourceSvitlobot.classList.add('active');
    btnSourceSchedule.classList.remove('active');
    colorDataSource = 'svitlobot';
    if (!svitlobotSensors.length) {
      loadSvitlobotData();
    } else {
      renderGlow();
    }
  });

  document.getElementById('btnTogglePolygons').addEventListener('click', toggleHromadasPolygons);

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
    if (activeDataset === 'settlements_25k') {
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
        <div class="search-item-sub">${m.catName} • Черга ${m.group}</div>
      `;
      item.addEventListener('click', () => {
        map.flyTo([m.lat, m.lon], 12, { duration: 1.2 });
        showItemCard({
          name: m.name,
          category: m.catName,
          group: m.group,
          lat: m.lat,
          lon: m.lon,
          hourly_schedule: SCHEDULE_PATTERNS[m.group]
        });
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
    if (colorDataSource === 'svitlobot') {
      loadSvitlobotData();
    }
  }, 30000);
}

window.addEventListener('DOMContentLoaded', initMap);
