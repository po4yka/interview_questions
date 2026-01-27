---
id: q-design-airbnb
title: Design Airbnb
aliases:
- Design Airbnb
- Rental Marketplace
- Booking System
topic: system-design
subtopics:
- marketplace
- geospatial
- booking
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-uber--system-design--hard
- q-geospatial-indexing--system-design--medium
- q-elasticsearch-full-text-search--system-design--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- system-design
- difficulty/medium
- marketplace
- geospatial
anki_cards:
- slug: q-design-airbnb-0-en
  anki_id: null
  synced_at: null
- slug: q-design-airbnb-0-ru
  anki_id: null
  synced_at: null
---
# Question (EN)
> How would you design a rental marketplace like Airbnb?

# Vopros (RU)
> Как бы вы спроектировали маркетплейс аренды жилья, подобный Airbnb?

---

## Answer (EN)

### Requirements

**Functional:**
- Search listings with geo-filters (location, dates, price, amenities)
- Listing management for hosts (CRUD, photos, pricing)
- Booking system with availability calendar
- Dynamic pricing engine
- Host/guest matching and verification
- Reviews and ratings (bidirectional)
- Payment processing with escrow
- Real-time messaging system
- Fraud detection

**Non-Functional:**
- 150M users, 7M+ listings
- Search latency <200ms
- High availability (99.9%)
- Strong consistency for bookings (no double-booking)
- Global scale with geo-distribution

### Capacity Estimation

```
Search queries: 100M/day = 1,157/sec
Bookings: 2M/day = 23/sec
Average listing photos: 20 * 2MB = 40MB/listing
Total storage: 7M * 40MB = 280TB (media only)

Peak load: 3x average = ~3,500 searches/sec
```

### High-Level Architecture

```
                     ┌─────────────────┐
                     │   Load Balancer │
                     └────────┬────────┘
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
  ┌────▼────┐           ┌─────▼─────┐          ┌─────▼─────┐
  │ Search  │           │  Booking  │          │  Listing  │
  │ Service │           │  Service  │          │  Service  │
  └────┬────┘           └─────┬─────┘          └─────┬─────┘
       │                      │                      │
       │    ┌─────────────────┼─────────────────┐    │
       │    │                 │                 │    │
  ┌────▼────▼───┐       ┌─────▼─────┐     ┌─────▼────▼───┐
  │Elasticsearch│       │ Postgres  │     │   Listings   │
  │ (Geo Index) │       │ (Bookings)│     │   DB         │
  └─────────────┘       └───────────┘     └──────────────┘
                              │
                        ┌─────▼─────┐
                        │  Payment  │
                        │  Service  │
                        └───────────┘
```

### Core Components

**1. Search Service**
- Full-text search with Elasticsearch
- Geospatial queries (geo_bounding_box, geo_distance)
- Faceted filtering (price, amenities, property type)
- Availability filtering (check calendar)

**2. Booking Service**
- Availability calendar management
- Reservation with pessimistic locking
- Payment orchestration (hold -> capture)
- Cancellation policy enforcement

**3. Listing Service**
- CRUD for property listings
- Photo upload and processing
- Pricing rules and calendar
- Verification status

### Search Flow

```
1. User enters: location, check-in, check-out, guests
2. Geocode location → bounding box coordinates
3. Query Elasticsearch:
   - geo_bounding_box filter
   - availability check (exclude booked dates)
   - facet filters (price, amenities, type)
4. Rank results:
   - Relevance score
   - Host response rate
   - Reviews/ratings
   - Price competitiveness
5. Return paginated results with CDN-served images
```

### Geospatial Indexing

```
Elasticsearch mapping:
{
  "location": {
    "type": "geo_point"
  },
  "geo_shape": {
    "type": "geo_shape"  // for neighborhood boundaries
  }
}

Query example:
{
  "geo_distance": {
    "distance": "10km",
    "location": {
      "lat": 37.7749,
      "lon": -122.4194
    }
  }
}

Alternative: Quadtree or S2 cells for efficient geo queries
```

### Booking Flow (Preventing Double-Booking)

```
1. Guest selects dates → Check availability (optimistic)
2. "Book Now" clicked:
   a. Acquire lock on listing calendar (SELECT FOR UPDATE)
   b. Verify availability again
   c. Create PENDING reservation
   d. Initiate payment hold
3. Payment hold successful:
   a. Mark dates as BOOKED in calendar
   b. Create reservation record
   c. Release lock
4. Payment failed:
   a. Release lock
   b. Return error to user

Calendar table:
┌────────────┬────────────┬─────────────┬────────────┐
│ listing_id │ date       │ status      │ booking_id │
├────────────┼────────────┼─────────────┼────────────┤
│ 123        │ 2024-03-15 │ AVAILABLE   │ NULL       │
│ 123        │ 2024-03-16 │ BOOKED      │ 456        │
│ 123        │ 2024-03-17 │ BLOCKED     │ NULL       │
└────────────┴────────────┴─────────────┴────────────┘
```

### Dynamic Pricing Engine

```
Base price * modifiers:

1. Demand multiplier:
   - High demand dates (holidays, events): 1.2-2.0x
   - Low demand: 0.8-0.9x

2. Seasonality:
   - Peak season: 1.3x
   - Off-season: 0.7x

3. Day of week:
   - Weekends: 1.1x
   - Weekdays: 1.0x

4. Length of stay:
   - Weekly discount: 10%
   - Monthly discount: 20%

5. Last-minute adjustment:
   - <3 days out, unbooked: 0.85x

Smart pricing algorithm:
- ML model trained on historical bookings
- Competitor analysis (similar listings)
- Supply/demand in area
```

### Payment Processing (Escrow Model)

```
Timeline:
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│  BOOKING  │───▶│  HOLD     │───▶│  STAY     │───▶│  PAYOUT   │
│  REQUEST  │    │  FUNDS    │    │  COMPLETE │    │  TO HOST  │
└───────────┘    └───────────┘    └───────────┘    └───────────┘
     │                │                 │                │
     │           Guest charged     24h after         Host receives
     │           (held in escrow)  check-in          funds
     │
  Cancellation → Refund based on cancellation policy
```

### Messaging System

```
Real-time messaging:
- WebSocket connections for online users
- Message queue (Redis) for delivery
- Persistent storage in Cassandra
- Push notifications for offline users

Message flow:
Guest → API Gateway → Message Service → Redis Pub/Sub → Host
                         │
                    Cassandra (persist)
                         │
                    Push Service (if offline)
```

### Fraud Detection

```
Signals monitored:
- Payment patterns (chargebacks, declined cards)
- Account velocity (new account, many bookings)
- Message content (external payment requests)
- Photo/listing quality (stolen images)
- Review patterns (fake reviews)

Actions:
- Flag for manual review
- Require additional verification
- Block suspicious accounts
- Hold payouts pending review
```

### Data Models

**Listing**
```sql
listings (
    listing_id: bigint PRIMARY KEY,
    host_id: bigint,
    title: varchar(200),
    description: text,
    property_type: enum,
    location: geography(POINT),
    address: jsonb,
    amenities: jsonb,
    base_price: decimal,
    max_guests: int,
    bedrooms: int,
    bathrooms: int,
    status: enum(active, inactive, pending),
    created_at: timestamp,
    INDEX (location) USING GIST,
    INDEX (host_id)
)
```

**Booking**
```sql
bookings (
    booking_id: bigint PRIMARY KEY,
    listing_id: bigint,
    guest_id: bigint,
    check_in: date,
    check_out: date,
    guests: int,
    total_price: decimal,
    status: enum(pending, confirmed, cancelled, completed),
    payment_intent_id: varchar(100),
    created_at: timestamp,
    UNIQUE (listing_id, check_in, check_out, status)
)
```

### Scaling Strategies

| Component | Strategy |
|-----------|----------|
| Search | Elasticsearch cluster, sharded by region |
| Bookings | Postgres with read replicas, shard by listing_id |
| Media | S3 + CloudFront CDN |
| Messages | Cassandra (write-heavy), WebSocket servers |
| Calendar | Redis for availability cache, DB for source of truth |
| Payments | Third-party (Stripe) with idempotency keys |

### Key Technical Challenges

| Challenge | Solution |
|-----------|----------|
| Search at scale | Elasticsearch with geo-sharding |
| Double-booking prevention | Pessimistic locking + DB constraints |
| Real-time availability | Redis cache + cache invalidation |
| Payment trust | Escrow model with delayed payout |
| Global latency | Multi-region deployment, CDN |
| Fraud at scale | ML-based detection + manual review |

---

## Otvet (RU)

### Требования

**Функциональные:**
- Поиск объявлений с гео-фильтрами (локация, даты, цена, удобства)
- Управление объявлениями для хостов (CRUD, фото, цены)
- Система бронирования с календарём доступности
- Движок динамического ценообразования
- Матчинг и верификация хостов/гостей
- Отзывы и рейтинги (двунаправленные)
- Обработка платежей с эскроу
- Система обмена сообщениями в реальном времени
- Обнаружение мошенничества

**Нефункциональные:**
- 150M пользователей, 7M+ объявлений
- Задержка поиска <200мс
- Высокая доступность (99.9%)
- Строгая консистентность для бронирований (без двойных бронирований)
- Глобальный масштаб с гео-распределением

### Оценка мощности

```
Поисковые запросы: 100M/день = 1,157/сек
Бронирования: 2M/день = 23/сек
Среднее количество фото на объявление: 20 * 2MB = 40MB/объявление
Общее хранилище: 7M * 40MB = 280TB (только медиа)

Пиковая нагрузка: 3x от средней = ~3,500 поисков/сек
```

### Геопространственное индексирование

```
Elasticsearch маппинг:
{
  "location": {
    "type": "geo_point"
  },
  "geo_shape": {
    "type": "geo_shape"  // для границ районов
  }
}

Альтернатива: Quadtree или S2 cells для эффективных гео-запросов
```

### Поток бронирования (предотвращение двойного бронирования)

```
1. Гость выбирает даты → Проверка доступности (оптимистичная)
2. Нажатие "Забронировать":
   a. Захват блокировки на календарь (SELECT FOR UPDATE)
   b. Повторная проверка доступности
   c. Создание резервации в статусе PENDING
   d. Инициация холда платежа
3. Холд платежа успешен:
   a. Пометка дат как BOOKED в календаре
   b. Создание записи бронирования
   c. Освобождение блокировки
4. Платёж не прошёл:
   a. Освобождение блокировки
   b. Возврат ошибки пользователю
```

### Движок динамического ценообразования

```
Базовая цена * модификаторы:

1. Множитель спроса:
   - Высокий спрос (праздники, события): 1.2-2.0x
   - Низкий спрос: 0.8-0.9x

2. Сезонность:
   - Пиковый сезон: 1.3x
   - Несезон: 0.7x

3. День недели:
   - Выходные: 1.1x
   - Будни: 1.0x

4. Продолжительность проживания:
   - Недельная скидка: 10%
   - Месячная скидка: 20%

5. Last-minute корректировка:
   - <3 дней, не забронировано: 0.85x

Алгоритм умного ценообразования:
- ML модель на исторических данных
- Анализ конкурентов (похожие объявления)
- Соотношение спроса/предложения в районе
```

### Обработка платежей (модель эскроу)

```
Временная шкала:
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│  ЗАПРОС   │───▶│  ХОЛД     │───▶│  ЗАЕЗД    │───▶│  ВЫПЛАТА  │
│  БРОНИ    │    │  СРЕДСТВ  │    │  ЗАВЕРШЁН │    │  ХОСТУ    │
└───────────┘    └───────────┘    └───────────┘    └───────────┘
     │                │                 │                │
     │         Деньги списаны      24ч после         Хост получает
     │         (в эскроу)          заезда            средства
     │
  Отмена → Возврат по политике отмены
```

### Обнаружение мошенничества

```
Отслеживаемые сигналы:
- Платёжные паттерны (чарджбеки, отклонённые карты)
- Скорость активности (новый аккаунт, много бронирований)
- Содержание сообщений (запросы оплаты вне платформы)
- Качество фото/объявления (украденные изображения)
- Паттерны отзывов (фейковые отзывы)

Действия:
- Пометка для ручной проверки
- Требование дополнительной верификации
- Блокировка подозрительных аккаунтов
- Задержка выплат до проверки
```

### Стратегии масштабирования

| Компонент | Стратегия |
|-----------|-----------|
| Поиск | Elasticsearch кластер, шардирование по региону |
| Бронирования | Postgres с репликами, шардирование по listing_id |
| Медиа | S3 + CloudFront CDN |
| Сообщения | Cassandra (write-heavy), WebSocket серверы |
| Календарь | Redis для кеша доступности, БД как source of truth |
| Платежи | Сторонний сервис (Stripe) с ключами идемпотентности |

### Ключевые технические вызовы

| Вызов | Решение |
|-------|---------|
| Поиск в масштабе | Elasticsearch с гео-шардированием |
| Предотвращение двойного бронирования | Пессимистичная блокировка + DB constraints |
| Доступность в реальном времени | Redis кеш + инвалидация кеша |
| Доверие к платежам | Модель эскроу с отложенной выплатой |
| Глобальная задержка | Мульти-региональный деплой, CDN |
| Мошенничество в масштабе | ML-детекция + ручная проверка |

---

## Follow-ups

- How do you handle instant booking vs. request-to-book?
- How do you design the review system to prevent fake reviews?
- How do you implement smart pricing recommendations for hosts?
- How would you design Airbnb Experiences (activities marketplace)?

## Related Questions

### Prerequisites (Easier)
- [[q-geospatial-indexing--system-design--medium]] - Geospatial Indexing
- [[q-elasticsearch-full-text-search--system-design--medium]] - Elasticsearch

### Related (Same Level)
- [[q-design-uber--system-design--hard]] - Uber (geo matching)
- [[q-design-notification-system--system-design--hard]] - Notifications

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Sharding
- [[q-cqrs-pattern--system-design--hard]] - CQRS
