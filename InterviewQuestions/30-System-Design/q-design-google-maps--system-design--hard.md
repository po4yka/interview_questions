---
id: sysdes-077
title: Design Google Maps
aliases:
- Design Google Maps
- Navigation System Design
- Mapping Service Architecture
topic: system-design
subtopics:
- design-problems
- geospatial
- routing
- maps
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-geospatial-indexing--system-design--medium
- q-design-uber--system-design--hard
- q-cdn-content-delivery-network--system-design--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- design-problems
- difficulty/hard
- geospatial
- system-design
anki_cards:
- slug: sysdes-077-0-en
  anki_id: null
  synced_at: null
- slug: sysdes-077-0-ru
  anki_id: null
  synced_at: null
---
# Question (EN)
> How would you design a navigation system like Google Maps?

# Vopros (RU)
> Как бы вы спроектировали навигационную систему, подобную Google Maps?

---

## Answer (EN)

### Requirements

**Functional Requirements:**
- Map rendering (pan, zoom, satellite/terrain views)
- Route calculation (driving, walking, cycling, transit)
- Real-time traffic updates and rerouting
- ETA prediction
- Turn-by-turn navigation
- POI (Points of Interest) search and geocoding
- Offline maps

**Non-Functional Requirements:**
- Low latency: <100ms for map tile loading
- Route calculation: <2s for typical routes
- High availability: 99.99%
- Global scale: billions of users, petabytes of map data
- Real-time: traffic updates every 1-2 minutes

### Scale Estimation

```
Users: 1B+ monthly active users
Daily requests:
- Map tile requests: 100B+ per day
- Route calculations: 1B+ per day
- Search queries: 500M+ per day

Storage:
- Map data: 20+ PB (vector tiles, satellite imagery)
- Road graph: 100+ TB
- Traffic data: TBs per day
```

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client Apps (Mobile/Web)                     │
│              [Offline cache, GPS, Sensors, Renderer]            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                        CDN Layer                                 │
│              [Map tiles, static assets, caching]                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      API Gateway                                 │
│           [Load Balancing, Auth, Rate Limiting, Routing]        │
└────┬──────────┬──────────┬──────────┬──────────┬────────────────┘
     │          │          │          │          │
┌────▼────┐┌────▼────┐┌────▼────┐┌────▼────┐┌────▼────┐
│  Tile   ││ Routing ││ Search  ││ Traffic ││   ETA   │
│ Service ││ Service ││ Service ││ Service ││ Service │
└────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘
     │          │          │          │          │
┌────▼──────────▼──────────▼──────────▼──────────▼────┐
│                    Data Layer                        │
│ [Road Graph DB, Tile Storage, POI Index, Traffic DB] │
└─────────────────────────────────────────────────────┘
```

### Map Tile Rendering

```
Tile System:
- World divided into tiles at each zoom level
- Zoom 0: 1 tile (whole world)
- Zoom 1: 4 tiles (2x2)
- Zoom N: 4^N tiles
- Typical range: zoom 0-21

Tile Addressing (Slippy Map):
  URL: /tiles/{z}/{x}/{y}.{format}
  Example: /tiles/15/5241/12661.png

┌─────────────────────────────┐
│ Zoom 0     │ Zoom 1        │
│            │ ┌───┬───┐     │
│  ┌───┐     │ │0,0│1,0│     │
│  │   │     │ ├───┼───┤     │
│  └───┘     │ │0,1│1,1│     │
│            │ └───┴───┘     │
└─────────────────────────────┘

Vector vs Raster Tiles:
┌─────────────┬───────────────────────────────────┐
│ Raster      │ Pre-rendered images (PNG/JPEG)    │
│ (Legacy)    │ Simple, but larger, less flexible │
├─────────────┼───────────────────────────────────┤
│ Vector      │ Raw geometry data (Protobuf)      │
│ (Modern)    │ Smaller, client-side rendering    │
│             │ Dynamic styling, rotation, 3D     │
└─────────────┴───────────────────────────────────┘
```

### Geospatial Indexing

```
Three main approaches for spatial data:

1. Geohash:
   - Encode lat/lng as hierarchical string
   - "9q8yy" = 5km cell
   - Good for range queries, easy sharding
   - Problem: edge cases at cell boundaries

2. QuadTree:
   - Recursive 4-way space division
   - Good for variable density data
   - Used for POI indexing

3. S2 Cells (Google's choice):
   - Project sphere onto cube faces
   - Hilbert curve cell addressing
   - 64-bit cell IDs, levels 0-30
   - ~1cm precision at level 30
   - Equal-area cells, no pole singularities

S2 Cell Hierarchy:
Level 0:  ~7,800 km face edge
Level 12: ~3 km cells (city blocks)
Level 14: ~700 m cells (streets)
Level 23: ~1 m cells (precise locations)
Level 30: ~1 cm cells (maximum precision)

Use cases:
- Tile indexing: S2 cells map to tiles
- POI search: Find all POIs in S2 covering
- Geofencing: Check cell containment
```

### Road Network Graph

```
Graph Representation:
- Nodes: Intersections, endpoints, shape points
- Edges: Road segments with attributes

Edge Attributes:
┌─────────────────────────────────────────┐
│ - length (meters)                       │
│ - speed_limit (km/h)                    │
│ - road_class (highway, local, etc.)     │
│ - direction (one-way, both)             │
│ - turn_restrictions                     │
│ - geometry (polyline)                   │
│ - real_time_speed (from traffic)        │
└─────────────────────────────────────────┘

Scale:
- 50M+ km of roads globally
- 500M+ nodes
- 1B+ edges
- Graph size: ~100TB

Storage:
- Partitioned by geographic region
- Hierarchical: local roads, arterials, highways
- Compressed adjacency lists
```

### Routing Algorithms

```
1. Dijkstra's Algorithm:
   - Classic shortest path
   - O(E + V log V) with min-heap
   - Too slow for long distances

2. A* Algorithm:
   - Dijkstra + heuristic (straight-line distance)
   - Faster for point-to-point routing
   - Still slow for continental routes

3. Contraction Hierarchies (CH):
   - Pre-processing: Contract nodes by importance
   - Query: Bidirectional search on hierarchy
   - 1000x faster than Dijkstra
   - Used by Google Maps, OSRM

Contraction Hierarchies:
┌────────────────────────────────────────────────┐
│ Pre-processing:                                │
│ 1. Order nodes by importance (highways first)  │
│ 2. Contract least important node               │
│ 3. Add shortcut edges if needed                │
│ 4. Repeat until all contracted                 │
│                                                │
│ Query:                                         │
│ 1. Bidirectional search (forward + backward)  │
│ 2. Only traverse "upward" in hierarchy         │
│ 3. Meet in the middle                          │
│ 4. Unpack shortcuts for full path              │
│                                                │
│ Performance:                                   │
│ - Pre-processing: hours to days                │
│ - Query: < 1ms for continental routes          │
└────────────────────────────────────────────────┘

4. Alternative Routes:
   - Plateau algorithm
   - Penalty method (penalize used edges)
   - K-shortest paths with diversity
```

### Real-Time Traffic

```
Data Sources:
┌─────────────────────────────────────────┐
│ 1. Crowdsourced GPS (phones, Waze)      │
│ 2. Connected vehicles                    │
│ 3. Road sensors / cameras               │
│ 4. Historical patterns                  │
│ 5. Events (accidents, construction)     │
└─────────────────────────────────────────┘

Traffic Processing Pipeline:
┌─────────┐    ┌──────────┐    ┌───────────┐
│ GPS     │───►│ Map      │───►│ Speed     │
│ Points  │    │ Matching │    │ Estimation│
└─────────┘    └──────────┘    └─────┬─────┘
                                     │
                               ┌─────▼─────┐
                               │ Traffic   │
                               │ Flow Model│
                               └─────┬─────┘
                                     │
                               ┌─────▼─────┐
                               │ Edge      │
                               │ Weights   │
                               └───────────┘

Map Matching:
- Match noisy GPS points to road segments
- Hidden Markov Model (HMM) approach
- Consider: distance, heading, connectivity

Speed Estimation:
- Aggregate speeds per road segment
- Time windows (5-min, 15-min)
- Confidence based on sample size

Traffic Flow Representation:
- Free flow: > 80% of speed limit
- Moderate: 50-80%
- Heavy: 25-50%
- Standstill: < 25%

Color coding: Green → Yellow → Orange → Red
```

### ETA Prediction

```
ETA = f(distance, traffic, time_of_day, weather, road_type)

Components:
1. Base Travel Time:
   - Sum of segment times (length / speed)
   - Current traffic speeds

2. Predictive Traffic:
   - Historical patterns by time/day
   - ML models for congestion prediction
   - Event impact modeling

3. Turn Delays:
   - Left turns, U-turns
   - Traffic signals timing
   - Stop signs

4. Arrival Uncertainty:
   - Confidence intervals
   - "Usually 15-25 min at this time"

ML Model Architecture:
┌───────────────────────────────────────────┐
│ Features:                                 │
│ - Current traffic on route segments       │
│ - Time of day, day of week                │
│ - Weather conditions                      │
│ - Historical travel times                 │
│ - Special events                          │
│                                           │
│ Model: Gradient Boosted Trees / Neural Net│
│ Output: Travel time distribution          │
└───────────────────────────────────────────┘
```

### Turn-by-Turn Navigation

```
Navigation State Machine:
┌─────────┐    ┌──────────┐    ┌──────────┐
│ ROUTING │───►│NAVIGATING│───►│ ARRIVED  │
└─────────┘    └────┬─────┘    └──────────┘
                    │
               ┌────▼─────┐
               │REROUTING │ (missed turn, traffic)
               └──────────┘

Components:
1. Location Tracking:
   - GPS + sensors (accelerometer, gyroscope)
   - Road snapping (stay on route)
   - Dead reckoning in tunnels

2. Instruction Generation:
   - Distance to next maneuver
   - Street names, landmarks
   - Lane guidance
   - "In 500 meters, turn right onto Main St"

3. Rerouting Triggers:
   - Deviation from route
   - Significant traffic change
   - Road closure detected
   - Faster route available

Voice Instruction Timing:
┌─────────────────────────────────────────┐
│ Highway: 2km, 1km, 500m before turn     │
│ City: 500m, 200m, "now"                 │
│ Adjust for current speed                │
└─────────────────────────────────────────┘
```

### POI Search and Geocoding

```
Geocoding:
- Forward: "1600 Amphitheatre Parkway" → (37.4224, -122.0841)
- Reverse: (37.4224, -122.0841) → "Googleplex, Mountain View, CA"

Search Architecture:
┌───────────────────────────────────────────────────┐
│                Query: "coffee near me"            │
└────────────────────────┬──────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────┐
│              Query Understanding                   │
│  - Intent classification (search, navigate)       │
│  - Entity extraction (category: coffee)           │
│  - Location context (near me → user location)     │
└────────────────────────┬──────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────┐
│              Candidate Retrieval                   │
│  - Geospatial index (S2 cells around user)        │
│  - Category filter (restaurants/cafes)            │
│  - Text matching (inverted index)                 │
└────────────────────────┬──────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────┐
│                  Ranking                           │
│  - Distance                                        │
│  - Relevance score                                 │
│  - Rating, reviews                                 │
│  - Opening hours                                   │
│  - Personalization                                 │
└───────────────────────────────────────────────────┘

POI Data Structure:
{
  "id": "place_abc123",
  "name": "Starbucks",
  "location": {"lat": 37.4224, "lng": -122.0841},
  "s2_cell_id": "89c2597...",
  "categories": ["coffee_shop", "restaurant"],
  "address": {...},
  "hours": {...},
  "rating": 4.2,
  "review_count": 1234
}
```

### Offline Maps

```
Offline Package Contents:
┌─────────────────────────────────────────┐
│ 1. Vector tiles for selected region     │
│ 2. Road graph (compressed)              │
│ 3. POI data (subset)                    │
│ 4. Address database                     │
│ 5. Search index                         │
└─────────────────────────────────────────┘

Download Strategy:
- User selects region (city, area)
- Pre-compute bounding box tiles
- Delta updates (only changed tiles)

Size Optimization:
- Vector tiles: 10-50 MB per city
- Road graph: 5-20 MB per city
- Total: 50-200 MB for major city

Offline Routing:
- Full Contraction Hierarchies
- Basic traffic (historical patterns)
- Limited rerouting capability
```

### Key Technical Challenges

| Challenge | Solution |
|-----------|----------|
| Tile serving at scale | Multi-tier CDN, edge caching |
| Real-time traffic updates | Stream processing (Kafka), incremental graph updates |
| Fast routing globally | Contraction Hierarchies, geographic partitioning |
| Map data freshness | Crowdsourced updates, satellite imagery ML |
| Offline maps | Delta updates, compressed formats |
| Battery efficiency (mobile) | Batch GPS, smart polling, client-side logic |

### Data Pipeline

```
Map Data Sources:
┌────────────────────────────────────────────────┐
│ Satellite/Aerial Imagery → ML extraction       │
│ Street View cars → Road geometry, signs        │
│ Government data → Official boundaries          │
│ User contributions → Edits, new places         │
│ Partner data → Business info, transit          │
└────────────────────────────────────────────────┘

Processing Pipeline:
Raw Data → Conflation → Validation → Graph Build → Tile Generation
                                          ↓
                              Contraction Hierarchies
                                          ↓
                              Production Deployment
```

---

## Otvet (RU)

### Требования

**Функциональные требования:**
- Отрисовка карты (панорамирование, масштабирование, спутник/рельеф)
- Расчёт маршрута (авто, пешком, велосипед, транспорт)
- Обновления трафика в реальном времени и перестроение маршрута
- Предсказание ETA
- Пошаговая навигация
- Поиск POI и геокодирование
- Офлайн-карты

**Нефункциональные требования:**
- Низкая задержка: <100мс для загрузки тайлов
- Расчёт маршрута: <2с для типичных маршрутов
- Высокая доступность: 99.99%
- Глобальный масштаб: миллиарды пользователей, петабайты данных карт

### Оценка масштаба

```
Пользователи: 1B+ активных в месяц
Ежедневные запросы:
- Запросы тайлов: 100B+ в день
- Расчёты маршрутов: 1B+ в день
- Поисковые запросы: 500M+ в день

Хранилище:
- Данные карт: 20+ PB (векторные тайлы, спутниковые снимки)
- Граф дорог: 100+ TB
- Данные трафика: TB в день
```

### Система тайлов карт

```
Система тайлов:
- Мир разделён на тайлы на каждом уровне масштаба
- Zoom 0: 1 тайл (весь мир)
- Zoom 1: 4 тайла (2x2)
- Zoom N: 4^N тайлов
- Типичный диапазон: zoom 0-21

Адресация тайлов:
  URL: /tiles/{z}/{x}/{y}.{format}
  Пример: /tiles/15/5241/12661.png

Векторные vs Растровые тайлы:
┌─────────────┬───────────────────────────────────┐
│ Растровые   │ Предрендеренные изображения       │
│ (устаревшие)│ Просто, но больше размер          │
├─────────────┼───────────────────────────────────┤
│ Векторные   │ Сырые геометрические данные       │
│ (современные)│ Меньше размер, рендеринг на клиенте │
│             │ Динамические стили, 3D            │
└─────────────┴───────────────────────────────────┘
```

### Геопространственное индексирование

```
Три основных подхода:

1. Geohash:
   - Кодирование lat/lng в иерархическую строку
   - "9q8yy" = ячейка 5км
   - Хорошо для диапазонных запросов
   - Проблема: граничные случаи

2. QuadTree:
   - Рекурсивное деление пространства на 4 части
   - Хорошо для данных с переменной плотностью

3. S2 Cells (выбор Google):
   - Проекция сферы на грани куба
   - Адресация ячеек кривой Гильберта
   - 64-битные ID ячеек, уровни 0-30
   - Точность ~1см на уровне 30
   - Равноплощадные ячейки

Иерархия S2 ячеек:
Level 12: ~3 км ячейки (городские кварталы)
Level 14: ~700 м ячейки (улицы)
Level 23: ~1 м ячейки (точные локации)
```

### Граф дорожной сети

```
Представление графа:
- Узлы: Перекрёстки, конечные точки
- Рёбра: Сегменты дорог с атрибутами

Атрибуты рёбер:
┌─────────────────────────────────────────┐
│ - длина (метры)                         │
│ - ограничение скорости (км/ч)           │
│ - класс дороги (шоссе, локальная)       │
│ - направление (одностороннее, оба)      │
│ - ограничения поворотов                 │
│ - геометрия (полилиния)                 │
│ - скорость в реальном времени           │
└─────────────────────────────────────────┘

Масштаб:
- 50M+ км дорог глобально
- 500M+ узлов
- 1B+ рёбер
- Размер графа: ~100TB
```

### Алгоритмы маршрутизации

```
1. Алгоритм Дейкстры:
   - Классический кратчайший путь
   - O(E + V log V) с min-heap
   - Слишком медленный для длинных расстояний

2. Алгоритм A*:
   - Дейкстра + эвристика (расстояние по прямой)
   - Быстрее для точка-точка
   - Всё ещё медленный для континентальных маршрутов

3. Contraction Hierarchies (CH):
   - Предобработка: сжатие узлов по важности
   - Запрос: двунаправленный поиск по иерархии
   - В 1000 раз быстрее Дейкстры
   - Используется в Google Maps, OSRM

Contraction Hierarchies:
┌────────────────────────────────────────────────┐
│ Предобработка:                                 │
│ 1. Упорядочить узлы по важности (шоссе первыми)│
│ 2. Сжать наименее важный узел                  │
│ 3. Добавить shortcut рёбра если нужно          │
│ 4. Повторять до полного сжатия                 │
│                                                │
│ Запрос:                                        │
│ 1. Двунаправленный поиск (вперёд + назад)      │
│ 2. Двигаться только "вверх" по иерархии        │
│ 3. Встретиться посередине                      │
│ 4. Распаковать shortcuts для полного пути      │
│                                                │
│ Производительность:                            │
│ - Предобработка: часы-дни                      │
│ - Запрос: < 1мс для континентальных маршрутов  │
└────────────────────────────────────────────────┘
```

### Трафик в реальном времени

```
Источники данных:
┌─────────────────────────────────────────┐
│ 1. Краудсорсинг GPS (телефоны, Waze)    │
│ 2. Подключённые автомобили              │
│ 3. Дорожные сенсоры / камеры            │
│ 4. Исторические паттерны                │
│ 5. События (ДТП, ремонт)                │
└─────────────────────────────────────────┘

Пайплайн обработки трафика:
┌─────────┐    ┌──────────┐    ┌───────────┐
│ GPS     │───►│ Map      │───►│ Оценка    │
│ точки   │    │ Matching │    │ скорости  │
└─────────┘    └──────────┘    └─────┬─────┘
                                     │
                               ┌─────▼─────┐
                               │ Модель    │
                               │ потока    │
                               └─────┬─────┘
                                     │
                               ┌─────▼─────┐
                               │ Веса      │
                               │ рёбер     │
                               └───────────┘

Map Matching:
- Сопоставление зашумлённых GPS точек с сегментами дорог
- Подход Hidden Markov Model (HMM)
- Учитывать: расстояние, направление, связность

Представление потока трафика:
- Свободный поток: > 80% от ограничения скорости
- Умеренный: 50-80%
- Плотный: 25-50%
- Пробка: < 25%

Цветовое кодирование: Зелёный → Жёлтый → Оранжевый → Красный
```

### Предсказание ETA

```
ETA = f(расстояние, трафик, время_дня, погода, тип_дороги)

Компоненты:
1. Базовое время в пути:
   - Сумма времён сегментов (длина / скорость)
   - Текущие скорости трафика

2. Предиктивный трафик:
   - Исторические паттерны по времени/дню
   - ML модели для предсказания заторов

3. Задержки на поворотах:
   - Левые повороты, развороты
   - Тайминг светофоров
   - Знаки стоп

4. Неопределённость прибытия:
   - Доверительные интервалы
   - "Обычно 15-25 мин в это время"

Архитектура ML модели:
┌───────────────────────────────────────────┐
│ Фичи:                                     │
│ - Текущий трафик на сегментах маршрута    │
│ - Время дня, день недели                  │
│ - Погодные условия                        │
│ - Исторические времена в пути             │
│ - Специальные события                     │
│                                           │
│ Модель: Gradient Boosted Trees / нейросеть│
│ Выход: распределение времени в пути       │
└───────────────────────────────────────────┘
```

### Пошаговая навигация

```
Машина состояний навигации:
┌─────────┐    ┌──────────┐    ┌──────────┐
│МАРШРУТИ-│───►│НАВИГАЦИЯ │───►│ ПРИБЫТИЕ │
│ЗАЦИЯ    │    └────┬─────┘    └──────────┘
└─────────┘         │
               ┌────▼─────┐
               │ПЕРЕСТРОЕ-│ (пропуск поворота, трафик)
               │НИЕ       │
               └──────────┘

Компоненты:
1. Отслеживание местоположения:
   - GPS + сенсоры (акселерометр, гироскоп)
   - Привязка к дороге (оставаться на маршруте)
   - Dead reckoning в туннелях

2. Генерация инструкций:
   - Расстояние до следующего манёвра
   - Названия улиц, ориентиры
   - Подсказки по полосам
   - "Через 500 метров поверните направо на ул. Главную"

3. Триггеры перестроения маршрута:
   - Отклонение от маршрута
   - Значительное изменение трафика
   - Обнаружено закрытие дороги
   - Доступен более быстрый маршрут
```

### Поиск POI и геокодирование

```
Геокодирование:
- Прямое: "Тверская улица, 1" → (55.7558, 37.6173)
- Обратное: (55.7558, 37.6173) → "Тверская улица, Москва"

Архитектура поиска:
┌───────────────────────────────────────────────────┐
│                Запрос: "кофе рядом"               │
└────────────────────────┬──────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────┐
│              Понимание запроса                     │
│  - Классификация интента (поиск, навигация)       │
│  - Извлечение сущностей (категория: кофе)         │
│  - Контекст локации (рядом → позиция пользователя)│
└────────────────────────┬──────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────┐
│              Получение кандидатов                  │
│  - Геопространственный индекс (S2 ячейки)         │
│  - Фильтр по категории                            │
│  - Текстовое соответствие (инвертированный индекс)│
└────────────────────────┬──────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────┐
│                  Ранжирование                      │
│  - Расстояние                                      │
│  - Оценка релевантности                            │
│  - Рейтинг, отзывы                                 │
│  - Часы работы                                     │
│  - Персонализация                                  │
└───────────────────────────────────────────────────┘
```

### Офлайн-карты

```
Содержимое офлайн-пакета:
┌─────────────────────────────────────────┐
│ 1. Векторные тайлы для выбранного региона│
│ 2. Граф дорог (сжатый)                   │
│ 3. Данные POI (подмножество)             │
│ 4. База адресов                          │
│ 5. Поисковый индекс                      │
└─────────────────────────────────────────┘

Стратегия загрузки:
- Пользователь выбирает регион (город, область)
- Предвычисленные тайлы по bounding box
- Дельта-обновления (только изменённые тайлы)

Оптимизация размера:
- Векторные тайлы: 10-50 МБ на город
- Граф дорог: 5-20 МБ на город
- Всего: 50-200 МБ для крупного города
```

### Ключевые технические вызовы

| Вызов | Решение |
|-------|---------|
| Раздача тайлов в масштабе | Многоуровневый CDN, edge-кэширование |
| Обновления трафика в реальном времени | Stream processing (Kafka), инкрементальные обновления графа |
| Быстрая маршрутизация глобально | Contraction Hierarchies, географическое партиционирование |
| Актуальность данных карт | Краудсорсинг обновлений, ML на спутниковых снимках |
| Офлайн-карты | Дельта-обновления, сжатые форматы |
| Эффективность батареи (мобильные) | Пакетная обработка GPS, умный polling |

---

## Follow-ups

- How does Google Maps handle map data updates from multiple sources (conflation)?
- What is the difference between S2 and H3 geospatial indexing?
- How would you design the traffic prediction ML pipeline?
- How does turn-by-turn navigation work offline?
- How would you implement lane-level navigation?
