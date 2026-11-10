/**
 * СвітлоКарта України — 1472 Територіальні Громади та Міста за графіками відключень
 */

let map;
let canvasOverlay;
let ctx;
let activeDataset = 'hromadas'; // 'hromadas' (1472 ТГ) або 'cities' (421 місто)
let hromadasData = [];
let citiesData = [];
let currentPoints = [];
let hromadasGeoLayer = null;
let showPolygons = false;
let currentHour = new Date().getHours();
let isPlaying = false;
let playInterval = null;
let activeItem = null;
let selectedGroup = 'all';

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

  // Темна базова підкладка CartoDB Dark Matter
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 18
  }).addTo(map);

  // Створюємо високопродуктивний Canvas шар для статичного сяйва
  createCanvasOverlay();

  // Завантажуємо геодані
  loadDatasets();

  // Налаштовуємо події інтерфейсу
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

// 3. Завантаження датасетів (1472 громади + 421 місто)
async function loadDatasets() {
  try {
    // 1472 Територіальні громади
    const resHromadas = await fetch('data/hromadas_points.json');
    const jsonHromadas = await resHromadas.json();
    hromadasData = jsonHromadas.districts;

    // 421 Місто України
    const resCities = await fetch('data/districts.json');
    const jsonCities = await resCities.json();
    citiesData = jsonCities.districts;

    // За замовчуванням вмикаємо повний шар 1472 громад
    currentPoints = hromadasData;

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

// 4. Оптичне статичне світіння 1472 громад (Radial Screen Bloom, No Animation)
function renderGlow() {
  if (!ctx || !currentPoints.length) return;

  const width = map.getSize().x;
  const height = map.getSize().y;
  ctx.clearRect(0, 0, width, height);

  let onCount = 0;
  let maybeCount = 0;
  let offCount = 0;

  const zoom = map.getZoom();
  // Динамічний радіус залежно від зуму
  const zoomFactor = Math.max(0.5, (zoom - 4) * 0.35);

  currentPoints.forEach(p => {
    if (selectedGroup !== 'all' && p.group !== parseInt(selectedGroup, 10)) {
      return;
    }

    const pt = map.latLngToContainerPoint([p.lat, p.lon]);

    // Швидкий frustum culling (відсікання точок поза межами екрана)
    if (pt.x < -80 || pt.x > width + 80 || pt.y < -80 || pt.y > height + 80) {
      return;
    }

    const state = p.hourly_schedule[currentHour]; // 'on', 'maybe', 'off'
    const isMajor = p.importance === 'high';

    // Розмір світлового ореолу
    const radius = isMajor
      ? Math.max(14, Math.min(50, 16 * zoomFactor))
      : Math.max(7, Math.min(24, 7.5 * zoomFactor));

    if (state === 'on') {
      onCount++;
      drawStaticGlow(pt.x, pt.y, radius, 1.0, isMajor);
    } else if (state === 'maybe') {
      maybeCount++;
      drawStaticGlow(pt.x, pt.y, radius * 0.75, 0.45, isMajor);
    } else {
      offCount++;
      drawExtinguishedPoint(pt.x, pt.y, isMajor);
    }
  });

  document.getElementById('countOn').textContent = onCount;
  document.getElementById('countMaybe').textContent = maybeCount;
  document.getElementById('countOff').textContent = offCount;

  // Оновлюємо стилі полігонів громад, якщо вони увімкнені
  if (hromadasGeoLayer) {
    hromadasGeoLayer.setStyle(getHromadaPolygonStyle);
  }
}

/**
 * Оптичне фізичне світіння розжареного джерела світла
 */
function drawStaticGlow(x, y, radius, intensity, isMajor) {
  const grad = ctx.createRadialGradient(x, y, 0, x, y, radius);

  if (intensity >= 0.8) {
    grad.addColorStop(0.00, 'rgba(255, 255, 240, 0.98)');   // Гаряче біло-золоте ядро
    grad.addColorStop(0.12, 'rgba(255, 225, 80, 0.88)');    // Тепле золоте сяйво
    grad.addColorStop(0.35, 'rgba(255, 175, 30, 0.40)');    // Бурштиновий ореол
    grad.addColorStop(0.70, 'rgba(240, 130, 10, 0.10)');    // Атмосферне розсіювання
    grad.addColorStop(1.00, 'rgba(0, 0, 0, 0)');
  } else {
    // Сіра зона (Можливе відключення)
    grad.addColorStop(0.00, 'rgba(255, 235, 160, 0.65)');
    grad.addColorStop(0.18, 'rgba(235, 175, 50, 0.40)');
    grad.addColorStop(0.45, 'rgba(200, 120, 20, 0.15)');
    grad.addColorStop(1.00, 'rgba(0, 0, 0, 0)');
  }

  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, Math.PI * 2);
  ctx.fill();

  // Центральна точка для точності географічного центру
  ctx.fillStyle = intensity >= 0.8 ? '#ffffff' : '#ffd000';
  ctx.beginPath();
  const coreR = isMajor ? Math.max(1.8, radius * 0.08) : Math.max(1.1, radius * 0.07);
  ctx.arc(x, y, coreR, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}

/**
 * Знеструмлена локація (Темрява)
 */
function drawExtinguishedPoint(x, y, isMajor) {
  ctx.save();
  ctx.fillStyle = isMajor ? 'rgba(55, 65, 80, 0.55)' : 'rgba(38, 48, 62, 0.35)';
  ctx.beginPath();
  ctx.arc(x, y, isMajor ? 2.2 : 1.2, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

// 5. Полігональний шар меж громад (опціональний)
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
        style: getHromadaPolygonStyle,
        onEachFeature: (feature, layer) => {
          layer.on('click', () => {
            const p = hromadasData.find(item => item.name === feature.properties.hromada);
            if (p) showItemCard(p);
          });
        }
      }).addTo(map);
    }
  }
}

function getHromadaPolygonStyle(feature) {
  const grp = feature.properties.group || 1;
  const p = hromadasData.find(item => item.name === feature.properties.hromada);
  const state = p ? p.hourly_schedule[currentHour] : 'off';

  if (state === 'on') {
    return {
      color: '#ffd000',
      weight: 1,
      opacity: 0.45,
      fillColor: '#ffbb00',
      fillOpacity: 0.12
    };
  } else if (state === 'maybe') {
    return {
      color: '#f59e0b',
      weight: 0.8,
      opacity: 0.35,
      fillColor: '#b45309',
      fillOpacity: 0.08
    };
  } else {
    return {
      color: '#1e293b',
      weight: 0.6,
      opacity: 0.3,
      fillColor: '#0a0f18',
      fillOpacity: 0.25
    };
  }
}

// 6. Клік по карті для пошуку найближчої громади
function handleMapClick(e) {
  const clickPoint = map.latLngToContainerPoint(e.latlng);
  let closest = null;
  let minDist = 25; // 25px радіус захоплення

  currentPoints.forEach(p => {
    const pt = map.latLngToContainerPoint([p.lat, p.lon]);
    const dist = Math.hypot(pt.x - clickPoint.x, pt.y - clickPoint.y);
    if (dist < minDist) {
      minDist = dist;
      closest = p;
    }
  });

  if (closest) {
    showItemCard(closest);
  }
}

// 7. Відкриття картки громади з добовим графіком
function showItemCard(item) {
  activeItem = item;
  const card = document.getElementById('districtCard');
  const badge = document.getElementById('cardStatusBadge');
  const state = item.hourly_schedule[currentHour];

  document.getElementById('cardTitle').textContent = item.name;
  document.getElementById('cardRayon').textContent = item.rayon || item.city || '';
  document.getElementById('cardRegion').textContent = item.region || '';
  document.getElementById('cardOperator').textContent = item.operator || 'Оператор мережі';
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

  // 24-годинна міні-шкала
  const mini = document.getElementById('miniTimeline');
  mini.innerHTML = '';
  item.hourly_schedule.forEach((s, idx) => {
    const bar = document.createElement('div');
    bar.className = `mini-bar bar-${s}`;
    if (idx === currentHour) {
      bar.classList.add('current');
    }
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

// 9. Налаштування UI та пошуку громад
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
    if (isPlaying) {
      stopPlay();
    } else {
      startPlay();
    }
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

  // Перемикач шарів (Громади 1472 ТГ vs Міста 421)
  const btnHromadas = document.getElementById('btnLayerHromadas');
  const btnCities = document.getElementById('btnLayerCities');

  btnHromadas.addEventListener('click', () => {
    btnHromadas.classList.add('active');
    btnCities.classList.remove('active');
    activeDataset = 'hromadas';
    currentPoints = hromadasData;
    renderGlow();
  });

  btnCities.addEventListener('click', () => {
    btnCities.classList.add('active');
    btnHromadas.classList.remove('active');
    activeDataset = 'cities';
    currentPoints = citiesData;
    renderGlow();
  });

  // Кнопка меж громад
  document.getElementById('btnTogglePolygons').addEventListener('click', toggleHromadasPolygons);

  // Фільтр за чергами 1..6
  document.getElementById('groupSelect').addEventListener('change', (e) => {
    selectedGroup = e.target.value;
    renderGlow();
  });

  // Пошук громад з автокомплітом
  const searchInput = document.getElementById('searchInput');
  const searchResults = document.getElementById('searchResults');

  searchInput.addEventListener('input', (e) => {
    const val = e.target.value.trim().toLowerCase();
    if (val.length < 2) {
      searchResults.style.display = 'none';
      return;
    }

    const matches = currentPoints.filter(p => 
      p.name.toLowerCase().includes(val) || 
      (p.city && p.city.toLowerCase().includes(val)) ||
      (p.rayon && p.rayon.toLowerCase().includes(val))
    ).slice(0, 8);

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
        <div class="search-item-sub">${m.rayon ? m.rayon + ', ' : ''}${m.region} • Черга ${m.group}</div>
      `;
      item.addEventListener('click', () => {
        map.flyTo([m.lat, m.lon], 11, { duration: 1.2 });
        showItemCard(m);
        searchResults.style.display = 'none';
        searchInput.value = m.name;
      });
      searchResults.appendChild(item);
    });
    searchResults.style.display = 'block';
  });

  // Закриття випадаючого списку при кліку за межами
  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      searchResults.style.display = 'none';
    }
  });
}

window.addEventListener('DOMContentLoaded', initMap);
