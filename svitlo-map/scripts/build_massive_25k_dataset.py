import urllib.request
import csv
import io
import json
import os

print('Завантажуємо та обробляємо повну базу 25 800+ населених пунктів України...')

url = 'https://raw.githubusercontent.com/alexbabintsev/ua-geo/main/data/out/katottg.csv'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

reader = csv.DictReader(io.StringIO(content))

EXCLUDED_REGIONS = {'UA01000000000013043', 'UA85000000000065278', 'UA44000000000018893'}
EXCLUDED_RAIONS = {
    'UA14020000000013572', 'UA14040000000098211', 'UA14060000000024357',
    'UA14080000000098686', 'UA14100000000010319', 'UA14140000000070889',
    'UA23020000000032289', 'UA23040000000067730', 'UA23080000000090746', 'UA23100000000034132',
    'UA65040000000088940', 'UA65060000000061947', 'UA65080000000090947'
}

SCHEDULE_PATTERNS = {
    1: ['on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on'],
    2: ['maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off'],
    3: ['off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on'],
    4: ['on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off'],
    5: ['off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off'],
    6: ['on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on','maybe','off','off','off','off','maybe','on','on','on','on']
}

CAT_MAP = {
    'місто': 1,
    'район у місті': 1,
    'місто зі спеціальним статусом': 1,
    'селище': 2,
    'село': 3
}

points = []
cat_counts = {1: 0, 2: 0, 3: 0}

for row in reader:
    cat_name = row.get('category_name')
    if cat_name not in CAT_MAP:
        continue
        
    reg = row.get('region_code')
    raion = row.get('raion_code')
    if reg in EXCLUDED_REGIONS or raion in EXCLUDED_RAIONS:
        continue
        
    lat_s = row.get('lat')
    lon_s = row.get('lon')
    if not lat_s or not lon_s:
        continue
        
    try:
        lat = round(float(lat_s), 4)
        lon = round(float(lon_s), 4)
    except ValueError:
        continue
        
    name = row.get('name', '').strip()
    if not name:
        continue
        
    cat = CAT_MAP[cat_name]
    cat_counts[cat] += 1
    
    # Прив'язка до черги: комбінація коду та назви дає природний розподіл ліній (фідерів)
    # без утворення штучних 50-кілометрових "чорних дір" на карті
    code = row.get('code') or ''
    group_num = (hash(name + code) % 6) + 1
    
    # Компактний кортеж: [lat, lon, name, category, group]
    points.append([lat, lon, name, cat, group_num])

print(f'Опрацьовано населених пунктів: {len(points)}')
print(f'Міста: {cat_counts[1]}, Селища (смт): {cat_counts[2]}, Села: {cat_counts[3]}')

out_file = 'c:/Users/Dmytro/source/repos/Github/svitlo-map/data/settlements_25k.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump({
        'total': len(points),
        'schedule_patterns': SCHEDULE_PATTERNS,
        'points': points
    }, f, ensure_ascii=False, separators=(',', ':'))

size_kb = os.path.getsize(out_file) / 1024
print(f'✅ Файл збережено: {out_file} (Розмір: {size_kb:.1f} KB)')
