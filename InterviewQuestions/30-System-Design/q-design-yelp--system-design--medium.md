---
id: sysdes-078
title: Design Yelp
aliases:
- Design Yelp
- Location-Based Review Platform
- Nearby Search System
topic: system-design
subtopics:
- design-problems
- geospatial
- search
- reviews
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
- q-design-google-search--system-design--hard
created: 2025-01-26
updated: 2025-01-26
tags:
- design-problems
- difficulty/medium
- geospatial
- system-design
---
# Question (EN)
> How would you design a location-based review platform like Yelp?

# Vopros (RU)
> Как бы вы спроектировали платформу отзывов на основе местоположения, подобную Yelp?

---

## Answer (EN)

### Requirements

**Functional**:
- Business listing and management
- Geospatial search (find nearby businesses)
- Review and rating system
- Search with filters (category, price, rating)
- Photo uploads
- Business owner tools

**Non-functional**:
- <100ms search latency
- High read availability (reads >> writes)
- Eventual consistency acceptable for reviews

### Scale Estimation

```
Users: 100M monthly active
Businesses: 200M worldwide
Reviews: 500M total
Daily searches: 500M
QPS: ~6K (peak 20K)
```

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Mobile/Web Clients                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      API Gateway                            │
│            (Auth, Rate Limiting, Routing)                   │
└────────┬──────────────┬──────────────┬──────────────────────┘
         │              │              │
   ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
   │ Business  │  │  Search   │  │  Review   │
   │ Service   │  │  Service  │  │  Service  │
   └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
         │              │              │
   ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
   │ Business  │  │ Geospatial│  │  Review   │
   │    DB     │  │   Index   │  │    DB     │
   │ (MySQL)   │  │(QuadTree) │  │ (MySQL)   │
   └───────────┘  └───────────┘  └───────────┘
```

### Geospatial Indexing

**Option 1: QuadTree**
```
World divided into quadrants recursively
Each leaf node contains businesses in that area

Structure:
- Top-left, Top-right, Bottom-left, Bottom-right
- Max businesses per leaf: ~100
- Rebuild when distribution changes significantly

Search:
1. Find leaf containing user location
2. Expand to neighboring leaves until radius covered
3. Filter by exact distance
```

**Option 2: Geohash**
```
Encode lat/lng into string: 37.7749, -122.4194 → "9q8yy"

Properties:
- Longer hash = more precise
- Common prefix = nearby locations
- Easy to store in standard DB with prefix queries

Precision:
- 4 chars: ~40km accuracy
- 6 chars: ~1km accuracy
- 8 chars: ~20m accuracy

Search:
  SELECT * FROM businesses
  WHERE geohash LIKE '9q8yy%'
  AND distance(lat, lng, user_lat, user_lng) < radius
```

**Comparison**

| Aspect | QuadTree | Geohash |
|--------|----------|---------|
| Update cost | High (rebalance) | Low (recalculate hash) |
| Memory | In-memory only | DB-storable |
| Edge cases | Handles density well | Edge boundary issues |
| Implementation | Custom | Standard libraries |

### Business Data Model

```sql
CREATE TABLE businesses (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    category_id INT,
    lat DECIMAL(10, 8),
    lng DECIMAL(11, 8),
    geohash VARCHAR(12),
    address TEXT,
    phone VARCHAR(20),
    hours JSON,
    avg_rating DECIMAL(2, 1),
    review_count INT,
    price_level TINYINT,
    created_at TIMESTAMP
);

CREATE INDEX idx_geohash ON businesses(geohash);
CREATE INDEX idx_category ON businesses(category_id, avg_rating);
```

### Review System

```sql
CREATE TABLE reviews (
    id BIGINT PRIMARY KEY,
    business_id BIGINT,
    user_id BIGINT,
    rating TINYINT,
    text TEXT,
    photos JSON,
    useful_count INT,
    created_at TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id)
);

-- Denormalized counters updated async
-- avg_rating recalculated periodically or on write
```

**Rating Calculation**
```
Simple average: (sum of ratings) / count
Weighted average: Recent reviews weighted higher
Bayesian average: Accounts for review count

Example Bayesian:
  weighted_rating = (v/(v+m)) * R + (m/(v+m)) * C
  v = number of votes
  m = minimum votes threshold
  R = average rating
  C = global mean
```

### Search Flow

```
1. User searches "pizza near me"

2. Parse query:
   - Location: user's lat/lng
   - Category: "pizza"
   - Radius: 5km default

3. Geospatial query:
   - Find geohash prefix for location
   - Query businesses in geohash range
   - Filter by exact distance

4. Apply filters:
   - Category match
   - Open now (check hours)
   - Price level
   - Minimum rating

5. Rank results:
   - Distance (primary for "nearby")
   - Rating × review_count (engagement)
   - Recency of reviews
   - Sponsored (paid placement)

6. Return paginated results with business cards
```

### Caching Strategy

```
Cache layers:
1. CDN: Static assets, business photos
2. API cache: Popular searches (Redis)
3. Database: Read replicas for queries

Popular area caching:
- Pre-compute top businesses per geohash prefix
- Cache "Top 10 restaurants in SF" type queries
- TTL: 1 hour (balance freshness vs load)

Cache key examples:
  nearby:{geohash_4}:category:pizza
  business:{id}:details
  business:{id}:reviews:page:1
```

### Photo Uploads

```
Upload flow:
1. Client requests presigned S3 URL
2. Client uploads directly to S3
3. Lambda triggers image processing:
   - Generate thumbnails
   - Extract metadata
   - Content moderation (ML)
4. Update business/review with photo URLs

Storage:
- Original: S3 Standard
- Thumbnails: S3 with CloudFront
- Delete originals after 30 days (keep processed)
```

### Fraud Detection

```
Review fraud signals:
- Same IP for multiple reviews
- Similar text across reviews (copy-paste)
- New account + many reviews quickly
- Geographic anomaly (review in NYC, IP in Russia)
- Timing patterns (burst of 5-star reviews)

Countermeasures:
- Rate limiting per user/IP
- ML model for spam detection
- Review gating (hold for moderation)
- Verified purchase/visit badges
- Report and appeal system
```

### Business Owner Tools

```
Dashboard features:
- Analytics (views, clicks, calls)
- Respond to reviews
- Update business info
- Photo management
- Advertising/promotion

Claim verification:
1. Phone call verification
2. Mail postcard with code
3. Email domain verification
4. Document upload
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Geo index | Geohash + DB | Simpler, scales with sharding |
| Rating storage | Denormalized | Avoid joins on reads |
| Photos | S3 + CDN | Cost-effective at scale |
| Search | Elasticsearch | Full-text + geo support |

---

## Otvet (RU)

### Требования

**Функциональные**:
- Листинг и управление бизнесами
- Геопространственный поиск (найти рядом)
- Система отзывов и рейтингов
- Поиск с фильтрами (категория, цена, рейтинг)
- Загрузка фотографий
- Инструменты для владельцев бизнеса

**Нефункциональные**:
- <100мс задержка поиска
- Высокая доступность на чтение (чтений >> записей)
- Eventual consistency допустима для отзывов

### Оценка масштаба

```
Пользователи: 100M активных в месяц
Бизнесы: 200M по всему миру
Отзывы: 500M всего
Поисков в день: 500M
QPS: ~6K (пик 20K)
```

### Геопространственное индексирование

**Вариант 1: QuadTree**
```
Мир делится на квадранты рекурсивно
Каждый листовой узел содержит бизнесы этой области

Структура:
- Сверху-слева, Сверху-справа, Снизу-слева, Снизу-справа
- Максимум бизнесов на лист: ~100
- Перестроение при изменении распределения

Поиск:
1. Найти лист с локацией пользователя
2. Расширить на соседние листы до покрытия радиуса
3. Фильтр по точному расстоянию
```

**Вариант 2: Geohash**
```
Кодирование lat/lng в строку: 37.7749, -122.4194 → "9q8yy"

Свойства:
- Длиннее хеш = точнее
- Общий префикс = близкие локации
- Легко хранить в обычной БД с prefix-запросами

Точность:
- 4 символа: ~40км
- 6 символов: ~1км
- 8 символов: ~20м
```

**Сравнение**

| Аспект | QuadTree | Geohash |
|--------|----------|---------|
| Стоимость обновления | Высокая (ребалансировка) | Низкая (пересчёт хеша) |
| Память | Только in-memory | Хранится в БД |
| Краевые случаи | Хорошо с плотностью | Проблемы на границах |
| Реализация | Кастомная | Стандартные библиотеки |

### Модель данных бизнеса

```sql
CREATE TABLE businesses (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    category_id INT,
    lat DECIMAL(10, 8),
    lng DECIMAL(11, 8),
    geohash VARCHAR(12),
    address TEXT,
    avg_rating DECIMAL(2, 1),
    review_count INT,
    price_level TINYINT
);
```

### Система отзывов

```sql
CREATE TABLE reviews (
    id BIGINT PRIMARY KEY,
    business_id BIGINT,
    user_id BIGINT,
    rating TINYINT,
    text TEXT,
    photos JSON,
    useful_count INT,
    created_at TIMESTAMP
);
```

**Расчёт рейтинга**
```
Простое среднее: (сумма рейтингов) / количество
Взвешенное: Недавние отзывы весят больше
Байесовское: Учитывает количество отзывов

Пример Байесовского:
  weighted_rating = (v/(v+m)) * R + (m/(v+m)) * C
  v = количество голосов
  m = минимальный порог
  R = средний рейтинг
  C = глобальное среднее
```

### Поток поиска

```
1. Пользователь ищет "пицца рядом"

2. Парсинг запроса:
   - Локация: lat/lng пользователя
   - Категория: "пицца"
   - Радиус: 5км по умолчанию

3. Геопространственный запрос:
   - Найти префикс geohash для локации
   - Запрос бизнесов в диапазоне geohash
   - Фильтр по точному расстоянию

4. Применить фильтры:
   - Совпадение категории
   - Открыто сейчас
   - Уровень цен
   - Минимальный рейтинг

5. Ранжирование:
   - Расстояние (основное для "рядом")
   - Рейтинг × количество_отзывов
   - Свежесть отзывов
   - Спонсорские (платное размещение)
```

### Стратегия кеширования

```
Слои кеша:
1. CDN: Статика, фото бизнесов
2. API кеш: Популярные запросы (Redis)
3. База: Read-реплики для запросов

Кеширование популярных зон:
- Предвычисление топ бизнесов по geohash-префиксу
- Кеш запросов типа "Топ 10 ресторанов в Москве"
- TTL: 1 час

Примеры ключей:
  nearby:{geohash_4}:category:pizza
  business:{id}:details
  business:{id}:reviews:page:1
```

### Обнаружение мошенничества

```
Сигналы фрода в отзывах:
- Один IP для нескольких отзывов
- Похожий текст (копипаст)
- Новый аккаунт + много отзывов быстро
- Географическая аномалия
- Паттерны времени (всплеск 5-звёздочных)

Контрмеры:
- Rate limiting по пользователю/IP
- ML модель для спама
- Модерация отзывов
- Бейджи верифицированного посещения
- Система жалоб и апелляций
```

### Инструменты владельца бизнеса

```
Функции дашборда:
- Аналитика (просмотры, клики, звонки)
- Ответы на отзывы
- Обновление информации о бизнесе
- Управление фото
- Реклама/продвижение

Верификация владения:
1. Звонок для подтверждения
2. Почтовая открытка с кодом
3. Верификация email-домена
4. Загрузка документов
```

### Ключевые решения

| Решение | Выбор | Обоснование |
|---------|-------|-------------|
| Гео-индекс | Geohash + БД | Проще, масштабируется с шардингом |
| Хранение рейтинга | Денормализованный | Избежать джойнов на чтении |
| Фото | S3 + CDN | Экономично на масштабе |
| Поиск | Elasticsearch | Full-text + гео поддержка |

---

## Follow-ups

- How would you handle multi-language reviews and search?
- What is the difference between QuadTree and R-Tree for geo-indexing?
- How do you design a recommendation system based on user preferences?
- How would you implement "Trending" businesses?

## Related Questions

### Prerequisites (Easier)
- [[q-geohash-geospatial-indexing--system-design--medium]] - Geohash basics
- [[q-caching-strategies--system-design--medium]] - Caching patterns

### Related (Same Level)
- [[q-design-uber--system-design--hard]] - Location-based matching
- [[q-design-google-search--system-design--hard]] - Search ranking

### Advanced (Harder)
- [[q-design-google-maps--system-design--hard]] - Map rendering and routing
