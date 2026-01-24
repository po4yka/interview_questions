---
id: sysdes-047
title: Design Uber
aliases:
- Design Uber
- Ride Sharing System
- Location-Based Matching
topic: system-design
subtopics:
- design-problems
- location
- real-time
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-whatsapp--system-design--hard
- q-websockets-sse-long-polling--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- design-problems
- difficulty/hard
- location
- system-design
anki_cards:
- slug: sysdes-047-0-en
  language: en
  anki_id: 1769159520996
  synced_at: '2026-01-23T13:49:17.774325'
- slug: sysdes-047-0-ru
  language: ru
  anki_id: 1769159521020
  synced_at: '2026-01-23T13:49:17.775662'
---
# Question (EN)
> Design a ride-sharing service like Uber. Focus on matching riders with drivers and real-time location tracking.

# Vopros (RU)
> Спроектируйте сервис совместных поездок типа Uber. Фокус на матчинге пассажиров с водителями и отслеживании локации в реальном времени.

---

## Answer (EN)

### Requirements

**Functional**: Request ride, match with driver, real-time tracking, payments, ratings
**Non-functional**: <1 min matching, real-time location updates, high availability

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               Rider App          Driver App                │
└─────────────────────┬──────────────────┬────────────────────┘
                      │                  │
┌─────────────────────▼──────────────────▼────────────────────┐
│                    API Gateway                              │
│            (Load Balancing, Auth, Rate Limiting)           │
└────────┬──────────────┬──────────────┬──────────────────────┘
         │              │              │
   ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
   │ Ride      │  │ Location  │  │ Matching  │
   │ Service   │  │ Service   │  │ Service   │
   └───────────┘  └─────┬─────┘  └───────────┘
                        │
                  ┌─────▼─────┐
                  │ Geospatial│
                  │ Index     │
                  │ (Redis)   │
                  └───────────┘
```

### Location Tracking

```
Driver location updates:
- Every 3-5 seconds when active
- Use WebSocket/long polling
- Store in geospatial index

Geospatial Storage (Redis):
  GEOADD drivers:city_id longitude latitude driver_id
  GEORADIUS drivers:city_id lng lat 5 km

Alternative: QuadTree or S2 cells for efficient geo queries
```

### Matching Algorithm

```
1. Rider requests ride
2. Find nearby drivers:
   - Query geospatial index (5km radius)
   - Filter: available, correct vehicle type
3. Rank candidates:
   - Distance (ETA)
   - Driver rating
   - Acceptance rate
4. Send request to top driver
5. If declined/timeout (15s) → next driver
6. Match confirmed → Start trip

Optimization:
- Supply/demand prediction
- Pre-position drivers to high-demand areas
- Surge pricing for supply-demand balance
```

### Trip State Machine

```
          ┌─────────┐
          │ PENDING │ (rider requesting)
          └────┬────┘
               ↓
          ┌─────────┐
          │SEARCHING│ (finding driver)
          └────┬────┘
               ↓
          ┌─────────┐
          │ MATCHED │ (driver assigned)
          └────┬────┘
               ↓
          ┌─────────┐
          │EN_ROUTE │ (driver going to pickup)
          └────┬────┘
               ↓
          ┌─────────┐
          │ PICKUP  │ (rider picked up)
          └────┬────┘
               ↓
          ┌─────────┐
          │IN_TRANSIT│ (going to destination)
          └────┬────┘
               ↓
          ┌─────────┐
          │COMPLETED│ (trip finished)
          └─────────┘
```

### Key Technical Challenges

| Challenge | Solution |
|-----------|----------|
| Location scale (millions/sec) | Geospatial sharding by city |
| Real-time matching | In-memory index (Redis) |
| ETA calculation | Pre-computed road graphs, ML models |
| Driver-rider communication | WebSocket connections |
| Payment processing | Async with idempotency |

### Scale Numbers

```
Uber scale:
- 5M+ rides/day
- 1M+ active drivers
- 10M+ location updates/minute
- 99.99% availability requirement
```

---

## Otvet (RU)

### Требования

**Функциональные**: Запрос поездки, матчинг с водителем, отслеживание в реальном времени, платежи
**Нефункциональные**: <1 мин на матчинг, обновления локации в реальном времени

### Отслеживание локации

```
Обновления локации водителя:
- Каждые 3-5 секунд когда активен
- WebSocket/long polling
- Хранение в геопространственном индексе

Геопространственное хранилище (Redis):
  GEOADD drivers:city_id longitude latitude driver_id
  GEORADIUS drivers:city_id lng lat 5 km

Альтернатива: QuadTree или S2 cells
```

### Алгоритм матчинга

```
1. Пассажир запрашивает поездку
2. Найти ближайших водителей:
   - Запрос к геоиндексу (радиус 5км)
   - Фильтр: доступен, правильный тип авто
3. Ранжирование кандидатов:
   - Расстояние (ETA)
   - Рейтинг водителя
   - Acceptance rate
4. Отправить запрос топ водителю
5. При отказе/таймауте (15с) → следующий водитель
6. Матч подтверждён → Начало поездки
```

### Ключевые технические вызовы

| Вызов | Решение |
|-------|---------|
| Масштаб локаций (миллионы/сек) | Геопространственный шардинг по городам |
| Матчинг в реальном времени | In-memory индекс (Redis) |
| Расчёт ETA | Предвычисленные графы дорог, ML модели |
| Коммуникация водитель-пассажир | WebSocket соединения |
| Обработка платежей | Async с идемпотентностью |

### Масштабные числа

```
Масштаб Uber:
- 5M+ поездок/день
- 1M+ активных водителей
- 10M+ обновлений локации/минуту
- 99.99% требование доступности
```

---

## Follow-ups

- How does Uber handle surge pricing?
- What is the S2 library and how does it help with geo-queries?
- How do you design Uber Eats differently from Uber rides?
