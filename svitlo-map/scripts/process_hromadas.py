import urllib.request
import json
import os

url = 'https://raw.githubusercontent.com/slawomirmatuszak/ukrainian_geodata/main/hromady.geojson'
print('Завантажуємо 1472 територіальні громади України...')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as resp:
    geo_data = json.loads(resp.read().decode('utf-8'))

OBLAST_OPERATORS = {
    'Київська область': 'ДТЕК Київські регіональні мережі',
    'м. Київ': 'ДТЕК Київські електромережі',
    'Дніпропетровська область': 'ДТЕК Дніпровські електромережі',
    'Одеська область': 'ДТЕК Одеські електромережі',
    'Донецька область': 'ДТЕК Донецькі електромережі',
    'Львівська область': 'Львівобленерго',
    'Харківська область': 'Харківобленерго',
    'Вінницька область': 'Вінницяобленерго',
    'Волинська область': 'Волиньобленерго',
    'Житомирська область': 'Житомиробленерго',
    'Закарпатська область': 'Закарпаттяобленерго',
    'Запорізька область': 'Запоріжжяобленерго',
    'Івано-Франківська область': 'Прикарпаттяобленерго',
    'Кіровоградська область': 'Кіровоградобленерго',
    'Луганська область': 'Луганське ЕО',
    'Миколаївська область': 'Миколаївобленерго',
    'Полтавська область': 'Полтаваобленерго',
    'Рівненська область': 'Рівнеобленерго',
    'Сумська область': 'Сумиобленерго',
    'Тернопільська область': 'Тернопільобленерго',
    'Херсонська область': 'Херсонобленерго',
    'Хмельницька область': 'Хмельницькобленерго',
    'Черкаська область': 'Черкасиобленерго',
    'Чернівецька область': 'Чернівціобленерго',
    'Чернігівська область': 'Чернігівобленерго',
    'Автономна Республіка Крим': 'Крименерго',
    'м. Севастополь': 'Севастопольенерго'
}

SCHEDULE_PATTERNS = {
    1: ['on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on'],
    2: ['maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off'],
    3: ['off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on'],
    4: ['on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off'],
    5: ['off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off'],
    6: ['on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on']
}

def get_centroid(geometry):
    coords = []
    g_type = geometry.get('type')
    raw_coords = geometry.get('coordinates', [])
    
    if g_type == 'Polygon':
        for ring in raw_coords:
            for pt in ring:
                coords.append(pt)
    elif g_type == 'MultiPolygon':
        for poly in raw_coords:
            for ring in poly:
                for pt in ring:
                    coords.append(pt)
                    
    if not coords:
        return None, None
        
    avg_lon = sum(c[0] for c in coords) / len(coords)
    avg_lat = sum(c[1] for c in coords) / len(coords)
    return avg_lat, avg_lon

hromadas_points = []
features = geo_data['features']

for idx, f in enumerate(features):
    props = f['properties']
    hromada_name = props.get('hromada') or f"Громада {idx}"
    region_name = props.get('region') or 'Україна'
    rayon_name = props.get('rayon') or ''
    
    lat, lon = get_centroid(f['geometry'])
    if lat is None or lon is None:
        continue
        
    # Детермінована черга 1..6 за назвою громади
    group_num = (hash(hromada_name + region_name) % 6) + 1
    operator = OBLAST_OPERATORS.get(region_name, 'Обленерго')
    
    # Визначаємо важливість (обласні центри / ключові громади)
    is_major = any(k in hromada_name for k in ['Київ', 'Харків', 'Одес', 'Дніпр', 'Львів', 'Запоріж', 'Криворізьк', 'Вінницьк', 'Миколаїв', 'Полтав', 'Черкас', 'Чернігів', 'Суми', 'Хмельницьк', 'Житомир', 'Рівнен', 'Івано-Франків', 'Тернопіль', 'Луцьк', 'Ужгород', 'Чернівець', 'Кропивницьк'])

    # Оновлюємо властивості у самій геометрії для полігонів
    f['properties']['group'] = group_num
    f['properties']['operator'] = operator
    f['properties']['lat'] = round(lat, 5)
    f['properties']['lon'] = round(lon, 5)

    item = {
        'id': f"hromada_{idx}",
        'name': hromada_name,
        'city': hromada_name.replace(' територіальна громада', ''),
        'rayon': rayon_name,
        'region': region_name,
        'operator': operator,
        'group': group_num,
        'lat': round(lat, 5),
        'lon': round(lon, 5),
        'importance': 'high' if is_major else 'normal',
        'hourly_schedule': SCHEDULE_PATTERNS[group_num]
    }
    hromadas_points.append(item)

# Зберігаємо точковий датасет громад
out_points = 'c:/Users/Dmytro/source/repos/Github/svitlo-map/data/hromadas_points.json'
with open(out_points, 'w', encoding='utf-8') as fp:
    json.dump({'districts': hromadas_points, 'schedule_patterns': SCHEDULE_PATTERNS}, fp, ensure_ascii=False, indent=2)

# Зберігаємо оновлений GeoJSON із полігонами громад
out_geo = 'c:/Users/Dmytro/source/repos/Github/svitlo-map/data/hromadas_boundaries.geojson'
with open(out_geo, 'w', encoding='utf-8') as fg:
    json.dump(geo_data, fg, ensure_ascii=False)

print(f"✅ Успішно опрацьовано {len(hromadas_points)} громад України!")
print(f"Точковий файл: {out_points}")
print(f"Полігональний файл: {out_geo}")
