import json
import os

print('Фільтруємо дані: залишаємо ВИКЛЮЧНО підконтрольні території з графіками Обленерго...')

# 1. Обробка hromadas_points.json
with open('c:/Users/Dmytro/source/repos/Github/svitlo-map/data/hromadas_points.json', encoding='utf-8') as f:
    data_hromadas = json.load(f)

hromadas_list = data_hromadas['districts']
filtered_hromadas = []

EXCLUDED_REGIONS = [
    'Автономна республіка Крим',
    'Автономна Республіка Крим',
    'м. Севастополь',
    'Луганська область'
]

EXCLUDED_RAYONS = {
    'Донецька область': [
        'Маріупольський район', 'Маріупольский район', 'Горлівський район',
        'Кальміуський район', 'Донецький район', 'Волноваський район', 'Бахмутський район'
    ],
    'Запорізька область': [
        'Бердянський район', 'Мелітопольський район', 'Василівський район', 'Пологівський район'
    ],
    'Херсонська область': [
        'Генічеський район', 'Каховський район', 'Скадовський район'
    ]
}

for h in hromadas_list:
    reg = h.get('region', '')
    rayon = h.get('rayon', '')
    
    if reg in EXCLUDED_REGIONS:
        continue
        
    if reg in EXCLUDED_RAYONS and rayon in EXCLUDED_RAYONS[reg]:
        continue
        
    filtered_hromadas.append(h)

print(f'Громади: було {len(hromadas_list)}, залишилось у графіках Обленерго: {len(filtered_hromadas)}')

with open('c:/Users/Dmytro/source/repos/Github/svitlo-map/data/hromadas_points.json', 'w', encoding='utf-8') as f:
    json.dump({'districts': filtered_hromadas, 'schedule_patterns': data_hromadas['schedule_patterns']}, f, ensure_ascii=False, indent=2)

# 2. Обробка полігонів hromadas_boundaries.geojson
with open('c:/Users/Dmytro/source/repos/Github/svitlo-map/data/hromadas_boundaries.geojson', encoding='utf-8') as f:
    geo_data = json.load(f)

allowed_names = set(h['name'] for h in filtered_hromadas)
filtered_features = [
    feat for feat in geo_data['features'] 
    if feat['properties'].get('hromada') in allowed_names
]

print(f'Полігони громад: було {len(geo_data["features"])}, залишилось: {len(filtered_features)}')
geo_data['features'] = filtered_features

with open('c:/Users/Dmytro/source/repos/Github/svitlo-map/data/hromadas_boundaries.geojson', 'w', encoding='utf-8') as f:
    json.dump(geo_data, f, ensure_ascii=False)

# 3. Обробка districts.json (421 місто)
with open('c:/Users/Dmytro/source/repos/Github/svitlo-map/data/districts.json', encoding='utf-8') as f:
    data_cities = json.load(f)

cities_list = data_cities['districts']
filtered_cities = []

OCCUPIED_CITIES = {
    'АР Крим': True, 'Севастополь': True, 'Сімферополь': True, 'Керч': True, 'Євпаторія': True,
    'Ялта': True, 'Феодосія': True, 'Джанкой': True, 'Алушта': True, 'Бахчисарай': True,
    'Красноперекопськ': True, 'Саки': True, 'Армянськ': True, 'Судак': True, 'Білогірськ': True,
    'Щолкіне': True, 'Старий Крим': True, 'Алупка': True,
    # Луганщина
    'Луганськ': True, 'Алчевськ': True, 'Сєвєродонецьк': True, 'Лисичанськ': True, 'Хрустальний': True,
    'Кадіївка': True, 'Довжанськ': True, 'Рубіжне': True, 'Антрацит': True, 'Ровеньки': True,
    'Брянка': True, 'Сорокине': True, 'Первомайськ': True, 'Голубівка': True, 'Перевальськ': True,
    'Молодогвардійськ': True, 'Суходільськ': True, 'Кремінна': True, 'Сватове': True, 'Старобільськ': True,
    'Попасна': True, 'Лутугине': True, 'Ювілейне': True, 'Вознесенівка': True, 'Теплогірськ': True,
    # Донеччина (окуповані)
    'Донецьк': True, 'Маріуполь': True, 'Макіївка': True, 'Горлівка': True, 'Єнакієве': True,
    'Бахмут': True, 'Чистякове': True, 'Харцизьк': True, 'Шахтарськ': True, 'Сніжне': True,
    'Ясинувата': True, 'Авдіївка': True, 'Торез': True, 'Дебальцеве': True, 'Волноваха': True,
    'Докучаєвськ': True, 'Амвросіївка': True, 'Хрестівка': True, 'Іловайськ': True, 'Вуглегірськ': True,
    'Новоазовськ': True, 'Зугрес': True, 'Моспине': True,
    # Запоріжжя (окуповані)
    'Мелітополь': True, 'Бердянськ': True, 'Енергодар': True, 'Токмак': True, 'Пологи': True,
    'Дніпрорудне': True, 'Василівка': True, 'Приморськ': True,
    # Херсонщина (окуповані лівобережжя)
    'Нова Каховка': True, 'Каховка': True, 'Олешки': True, 'Генічеськ': True, 'Скадовськ': True,
    'Гола Пристань': True, 'Таврійськ': True
}

for c in cities_list:
    city_name = c.get('city') or c.get('name')
    reg = c.get('region', '')
    
    if reg in ['АР Крим', 'Автономна Республіка Крим', 'м. Севастополь', 'Луганська область']:
        continue
    if city_name in OCCUPIED_CITIES or c.get('name') in OCCUPIED_CITIES:
        continue
    filtered_cities.append(c)

print(f'Міста: було {len(cities_list)}, залишилось у графіках Обленерго: {len(filtered_cities)}')

with open('c:/Users/Dmytro/source/repos/Github/svitlo-map/data/districts.json', 'w', encoding='utf-8') as f:
    json.dump({'districts': filtered_cities, 'schedule_patterns': data_cities['schedule_patterns']}, f, ensure_ascii=False, indent=2)

print('✅ Фільтрація завершена успішно!')
