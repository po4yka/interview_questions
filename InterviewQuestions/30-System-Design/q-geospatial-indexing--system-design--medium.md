---
id: sysdes-074
title: Geo-spatial Indexing
aliases:
- Geo-spatial Indexing
- Location-based Search
- Spatial Databases
topic: system-design
subtopics:
- data-management
- indexing
- location
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-database-indexing--system-design--medium
- q-design-uber--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- data-management
- difficulty/medium
- indexing
- system-design
anki_cards:
- slug: sysdes-074-0-en
  language: en
  anki_id: 1769161752983
  synced_at: '2026-01-23T13:49:17.733903'
- slug: sysdes-074-0-ru
  language: ru
  anki_id: 1769161753007
  synced_at: '2026-01-23T13:49:17.735084'
---
# Question (EN)
> What is geo-spatial indexing? What data structures are used for location-based queries?

# Vopros (RU)
> Что такое геопространственное индексирование? Какие структуры данных используются для запросов по местоположению?

---

## Answer (EN)

**Geo-spatial indexing** enables efficient queries on location data, such as "find all restaurants within 5km" or "find the nearest driver."

### Common Query Types

```
1. Point-in-polygon: Is this location inside a region?
2. Range query: Find all points within a bounding box
3. Nearest neighbor: Find K closest points to a location
4. Distance query: Find all points within radius R
```

### Key Data Structures

| Structure | How It Works | Best For |
|-----------|--------------|----------|
| **Geohash** | Encode lat/lng to string prefix | Range queries, easy sharding |
| **Quadtree** | Recursive 4-way space division | Variable density, dynamic data |
| **R-tree** | Bounding rectangles hierarchy | Complex shapes, polygons |
| **S2 (Google)** | Sphere mapped to cube faces | Global scale, precise queries |
| **H3 (Uber)** | Hexagonal grid hierarchy | Movement patterns, coverage |

### Geohash

```
Geohash: Encode location as hierarchical string

(37.7749, -122.4194) → "9q8yy"

Longer prefix = more precision:
"9"     → ~5000km cell
"9q"    → ~1250km cell
"9q8"   → ~156km cell
"9q8y"  → ~39km cell
"9q8yy" → ~5km cell

Benefits:
- Nearby locations share prefix
- Easy database indexing (string comparison)
- Simple sharding by prefix

Limitation:
- Edge cases: Adjacent cells may have different prefixes
  "9q8yy" and "9q8yz" might be neighbors but no common prefix
```

### Quadtree

```
Recursively divide 2D space into 4 quadrants:

┌───────────┬───────────┐
│     │     │           │
│  NW │ NE  │           │
├─────┼─────┤     NE    │
│     │     │           │
│  SW │ SE  │           │
├─────┴─────┼───────────┤
│           │           │
│    SW     │    SE     │
│           │           │
└───────────┴───────────┘

Subdivide cells with too many points
Stop when cell has ≤ threshold points

Query: Start at root, descend into overlapping quadrants
```

### S2 Geometry (Google)

```
Project Earth onto a cube, then unfold:

     ┌───┐
     │ 2 │
 ┌───┼───┼───┬───┐
 │ 3 │ 0 │ 1 │ 4 │
 └───┼───┼───┴───┘
     │ 5 │
     └───┘

Each face divided into cells using Hilbert curve
Cell IDs: 64-bit integers with hierarchical structure

Level 0: 6 faces
Level 30: ~1cm² cells

Benefits:
- No singularities at poles
- Cells are roughly equal area
- Efficient cell operations
```

### Practical Implementation

```
PostgreSQL + PostGIS:
CREATE INDEX idx_location ON places USING GIST (location);
SELECT * FROM places
WHERE ST_DWithin(location, ST_MakePoint(-122.4, 37.7), 5000);

Redis + Geo:
GEOADD locations -122.4194 37.7749 "restaurant1"
GEORADIUS locations -122.4 37.7 5 km WITHDIST

MongoDB:
db.places.createIndex({ location: "2dsphere" })
db.places.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-122.4, 37.7] },
      $maxDistance: 5000
    }
  }
})
```

### Choosing the Right Structure

| Use Case | Recommended | Reason |
|----------|-------------|--------|
| Simple proximity search | Geohash | Easy to implement, good enough |
| Ride-sharing (Uber) | H3 | Hexagons for coverage analysis |
| Maps (Google) | S2 | Global scale, precision |
| Game maps, small area | Quadtree | Simple, efficient for bounded space |
| Complex polygons | R-tree | Handles arbitrary shapes |

---

## Otvet (RU)

**Геопространственное индексирование** обеспечивает эффективные запросы по данным о местоположении: "найти все рестораны в радиусе 5км" или "найти ближайшего водителя".

### Типы запросов

```
1. Точка в полигоне: Находится ли точка внутри региона?
2. Диапазонный запрос: Найти все точки в ограничивающем прямоугольнике
3. Ближайший сосед: Найти K ближайших точек
4. Запрос по расстоянию: Найти все точки в радиусе R
```

### Ключевые структуры данных

| Структура | Как работает | Лучше для |
|-----------|--------------|-----------|
| **Geohash** | Кодирует lat/lng в строку | Диапазонные запросы, шардинг |
| **Quadtree** | Рекурсивное деление на 4 части | Переменная плотность |
| **R-tree** | Иерархия ограничивающих прямоугольников | Сложные формы, полигоны |
| **S2 (Google)** | Сфера на грани куба | Глобальный масштаб |
| **H3 (Uber)** | Шестиугольная сетка | Паттерны движения |

### Geohash

```
Кодирование местоположения в иерархическую строку:

(37.7749, -122.4194) → "9q8yy"

Длиннее префикс = больше точность:
"9"     → ~5000км ячейка
"9q8yy" → ~5км ячейка

Преимущества:
- Близкие точки имеют общий префикс
- Простое индексирование в БД
- Простой шардинг по префиксу

Ограничение:
- Граничные случаи: соседние ячейки могут иметь разные префиксы
```

### Quadtree

```
Рекурсивное деление 2D пространства на 4 квадранта:

┌───────────┬───────────┐
│  NW │ NE  │           │
├─────┼─────┤     NE    │
│  SW │ SE  │           │
├─────┴─────┼───────────┤
│    SW     │    SE     │
└───────────┴───────────┘

Подразделять ячейки с большим числом точек
Остановиться когда точек ≤ порога
```

### Практическая реализация

```
PostgreSQL + PostGIS:
CREATE INDEX idx_location ON places USING GIST (location);
SELECT * FROM places
WHERE ST_DWithin(location, ST_MakePoint(-122.4, 37.7), 5000);

Redis + Geo:
GEOADD locations -122.4194 37.7749 "restaurant1"
GEORADIUS locations -122.4 37.7 5 km WITHDIST

MongoDB:
db.places.createIndex({ location: "2dsphere" })
```

### Выбор структуры

| Сценарий | Рекомендация | Причина |
|----------|--------------|---------|
| Простой поиск близости | Geohash | Легко реализовать |
| Райдшеринг (Uber) | H3 | Шестиугольники для анализа покрытия |
| Карты (Google) | S2 | Глобальный масштаб, точность |
| Игровые карты | Quadtree | Просто, эффективно для ограниченного пространства |
| Сложные полигоны | R-tree | Работает с произвольными формами |

---

## Follow-ups

- How does Uber use H3 for surge pricing?
- What are the tradeoffs between Geohash and S2?
- How do you handle moving objects (like drivers) efficiently?
