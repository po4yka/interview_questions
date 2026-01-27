---
id: q-design-amazon-ecommerce
title: Design Amazon E-commerce
aliases:
- Amazon Design
- E-commerce Platform
- Online Marketplace
topic: system-design
subtopics:
- ecommerce
- distributed-systems
- high-scale
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-database-sharding-partitioning--system-design--hard
- q-caching-strategies--system-design--medium
- q-message-queues-event-driven--system-design--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- system-design
- difficulty/hard
- ecommerce
- distributed-systems
anki_cards:
- slug: q-design-amazon-ecommerce-0-en
  anki_id: null
  synced_at: null
- slug: q-design-amazon-ecommerce-0-ru
  anki_id: null
  synced_at: null
---
# Question (EN)
> How would you design an e-commerce platform like Amazon?

# Vopros (RU)
> Как бы вы спроектировали платформу электронной коммерции, подобную Amazon?

---

## Answer (EN)

### Requirements

**Functional:**
- Product catalog with search and filtering
- Shopping cart (persistent across sessions)
- Inventory management (real-time stock)
- Order processing and payment
- User reviews and ratings
- Seller marketplace platform
- Recommendation engine
- Warehouse and fulfillment tracking

**Non-Functional:**
- 300M active users, 100M DAU
- 500M products in catalog
- 1M+ orders/day peak (Black Friday: 10x)
- 99.99% availability (especially checkout)
- Low latency search (<100ms)
- Strong consistency for inventory/payments
- Global multi-region deployment

### Capacity Estimation

```
Daily active users: 100M
Product views: 100M * 10 views = 1B views/day = 11,574/sec
Search queries: 100M * 5 searches = 500M/day = 5,787/sec
Orders: 1M/day = 11.5/sec (peak: 100/sec)

Product catalog: 500M products * 10KB = 5TB
User data: 300M * 5KB = 1.5TB
Order history: 1M/day * 2KB * 365 = 730GB/year
Images: 500M products * 10 images * 500KB = 2.5PB
```

### High-Level Architecture

```
                          ┌──────────────┐
                          │   CloudFront │
                          │     (CDN)    │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │ API Gateway  │
                          │ + WAF + Auth │
                          └──────┬───────┘
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     │             │             │             │             │
┌────▼────┐  ┌─────▼────┐  ┌─────▼────┐  ┌─────▼────┐  ┌─────▼────┐
│ Product │  │  Search  │  │   Cart   │  │  Order   │  │  User    │
│ Catalog │  │ Service  │  │ Service  │  │ Service  │  │ Service  │
└────┬────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │            │             │             │             │
     │       ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐       │
     │       │Elastic   │  │  Redis   │  │ Payment  │       │
     │       │Search    │  │ Cluster  │  │ Gateway  │       │
     │       └──────────┘  └──────────┘  └──────────┘       │
     │                                                       │
     └───────────────────┬───────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │   Product DB        │
              │ (Sharded Postgres)  │
              └─────────────────────┘
```

### Core Services

**1. Product Catalog Service**
- CRUD operations for products
- Category/attribute management
- Seller product listings
- Price and availability

**2. Search Service**
- Full-text search (Elasticsearch)
- Faceted filtering (price, brand, category)
- Autocomplete suggestions
- Personalized ranking

**3. Shopping Cart Service**
- Session-based and persistent carts
- Cart merge on login
- Inventory reservation (soft lock)
- Price updates

**4. Inventory Service**
- Real-time stock tracking
- Warehouse allocation
- Reservation management
- Back-in-stock notifications

**5. Order Service**
- Order creation and validation
- Payment orchestration
- Order state machine
- Shipment tracking

**6. Recommendation Engine**
- Collaborative filtering
- Content-based filtering
- "Customers also bought"
- Personalized homepage

### Product Search Architecture

```
User Query
    │
    ▼
┌──────────────────┐
│  Query Parser    │ ← Tokenization, spell correction
└────────┬─────────┘
         │
    ┌────▼────┐
    │ Cache?  │──Yes──→ Return cached results
    └────┬────┘
         │ No
    ┌────▼─────────────┐
    │  Elasticsearch   │
    │  Cluster         │
    │  (Sharded by     │
    │   category)      │
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │  Ranking Layer   │ ← Personalization, relevance
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │  Results Merger  │ ← Ads, sponsored products
    └──────────────────┘
```

**Search Index Structure:**
```json
{
  "product_id": "B001234",
  "title": "Apple iPhone 15 Pro",
  "description": "Latest iPhone with A17 chip",
  "category_path": ["Electronics", "Phones", "Smartphones"],
  "brand": "Apple",
  "price": 999.00,
  "rating": 4.7,
  "review_count": 15420,
  "attributes": {
    "color": "Black",
    "storage": "256GB",
    "carrier": "Unlocked"
  },
  "seller_id": "ATVPDKIKX0DER",
  "in_stock": true,
  "prime_eligible": true
}
```

### Shopping Cart Design

**Why Redis for Cart:**
- Sub-millisecond latency
- Atomic operations (HINCRBY for quantity)
- TTL for abandoned carts
- Pub/Sub for real-time updates

**Cart Data Model:**
```
Key: cart:{user_id}
Type: Hash

Fields:
  product_1234: {"qty": 2, "price": 29.99, "added_at": 1706000000}
  product_5678: {"qty": 1, "price": 149.99, "added_at": 1706001000}

TTL: 30 days (refreshed on access)
```

**Cart Merge Flow (Guest → Logged In):**
```
1. User adds items as guest (session-based cart)
2. User logs in
3. Cart service:
   - Fetch guest cart (by session)
   - Fetch user cart (by user_id)
   - Merge: user cart items take priority for duplicates
   - Delete guest cart
   - Return merged cart
```

### Inventory Management

**Challenge:** Prevent overselling during high traffic.

**Solution: Two-Phase Inventory Lock**

```
Phase 1 - Soft Lock (Add to Cart):
  - Decrement available_count in Redis
  - Set TTL (15 minutes)
  - If expires, auto-release

Phase 2 - Hard Lock (Checkout):
  - Verify soft lock still valid
  - Decrement actual inventory in DB (transaction)
  - Create order record
  - Release soft lock
```

**Inventory Data Model:**
```sql
inventory (
    product_id: bigint,
    warehouse_id: int,
    available_qty: int,
    reserved_qty: int,
    total_qty: int,
    last_restock: timestamp,
    PRIMARY KEY (product_id, warehouse_id)
)
```

**Redis for Real-Time Stock:**
```
Key: stock:{product_id}:{warehouse_id}
Value: available_qty

Key: reserved:{order_id}:{product_id}
Value: qty
TTL: 15 minutes
```

### Order Processing Pipeline

```
                    ┌────────────────┐
                    │  Order Created │
                    │   (PENDING)    │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │   Inventory    │
                    │   Reserved     │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐     ┌──────────────┐
                    │    Payment     │────►│  FAILED      │
                    │   Processing   │     │ (Release Inv)│
                    └───────┬────────┘     └──────────────┘
                            │ Success
                    ┌───────▼────────┐
                    │   CONFIRMED    │
                    └───────┬────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
       ┌──────▼──────┐ ┌────▼────┐ ┌──────▼──────┐
       │  Warehouse  │ │ Seller  │ │   Notify    │
       │  Allocation │ │  Notify │ │   Customer  │
       └──────┬──────┘ └─────────┘ └─────────────┘
              │
       ┌──────▼──────┐
       │   SHIPPED   │
       └──────┬──────┘
              │
       ┌──────▼──────┐
       │  DELIVERED  │
       └─────────────┘
```

**Order State Machine (Event-Sourced):**
```
Events:
- OrderCreated
- PaymentReceived
- PaymentFailed
- InventoryReserved
- InventoryReleaseFailed
- OrderShipped
- OrderDelivered
- OrderCancelled
- RefundInitiated
- RefundCompleted
```

### Payment Integration

**Payment Flow:**
```
1. Client initiates checkout
2. Order Service creates pending order
3. Payment Service:
   a. Tokenize card (PCI compliance)
   b. Pre-authorize amount
   c. Return authorization token
4. Order confirmation:
   a. Capture payment
   b. Update order status
5. On failure:
   a. Release inventory reservation
   b. Send notification
```

**Multi-PSP Strategy:**
```
Primary: Stripe (US/EU)
Secondary: Adyen (APAC)
Fallback: PayPal

Routing logic:
- Route by region
- Route by payment method
- Automatic failover on PSP outage
```

### Recommendation Engine

**Approaches:**

1. **Collaborative Filtering:**
   - "Customers who bought X also bought Y"
   - User-item interaction matrix
   - Matrix factorization (ALS)

2. **Content-Based:**
   - Similar product attributes
   - Category affinity
   - Brand affinity

3. **Hybrid (Real-Time + Batch):**
```
Batch Pipeline (Daily):
  - Process purchase history
  - Train ML models
  - Generate product-to-product mappings
  - Store in Redis/DynamoDB

Real-Time Layer:
  - Current session behavior
  - Recently viewed products
  - Merge with batch recommendations
  - Apply business rules (no duplicates, in-stock only)
```

### Review System

**Design Considerations:**
- Verified purchase badge
- Helpful votes
- Spam/fake review detection
- Media attachments (photos/videos)

**Data Model:**
```sql
reviews (
    review_id: bigint PRIMARY KEY,
    product_id: bigint,
    user_id: bigint,
    rating: int CHECK (1-5),
    title: varchar(200),
    body: text,
    verified_purchase: boolean,
    helpful_votes: int,
    created_at: timestamp,
    INDEX (product_id, created_at)
)
```

**Aggregation Strategy:**
- Pre-compute rating distribution
- Update on new review (async)
- Cache product rating summary

### Seller Platform

**Multi-Tenant Architecture:**
```
┌─────────────────────────────────────────────────────┐
│                  Seller Portal                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Product  │  │  Orders  │  │ Analytics│          │
│  │ Listing  │  │ Mgmt     │  │ Dashboard│          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
└───────┼─────────────┼─────────────┼────────────────┘
        │             │             │
        ▼             ▼             ▼
   ┌─────────────────────────────────────────┐
   │         Marketplace Services            │
   │  - Seller onboarding                    │
   │  - Commission calculation               │
   │  - Payment settlement                   │
   │  - Seller performance metrics           │
   └─────────────────────────────────────────┘
```

### Warehouse and Fulfillment

**Fulfillment Options:**
- FBA (Fulfilled by Amazon) - Amazon warehouses
- FBM (Fulfilled by Merchant) - Seller ships
- SFP (Seller Fulfilled Prime) - Seller Prime-eligible

**Warehouse Selection Algorithm:**
```python
def select_warehouse(order_items, delivery_address):
    candidates = []

    for warehouse in get_warehouses_with_stock(order_items):
        score = calculate_score(
            distance=geo_distance(warehouse, delivery_address),
            shipping_cost=estimate_shipping(warehouse, delivery_address),
            capacity=warehouse.current_capacity,
            fulfillment_speed=warehouse.avg_processing_time
        )
        candidates.append((warehouse, score))

    # Prefer single warehouse fulfillment
    single_warehouse = find_single_warehouse_option(candidates, order_items)
    if single_warehouse:
        return single_warehouse

    # Split shipment if necessary
    return optimize_multi_warehouse(candidates, order_items)
```

### Peak Load Handling (Black Friday)

**Strategies:**
1. **Pre-warming:** Cache popular products hours before
2. **Queue-based checkout:** Rate limit checkout, show queue position
3. **Circuit breakers:** Graceful degradation of non-critical services
4. **Reserved capacity:** Auto-scale groups pre-provisioned
5. **Static fallbacks:** Pre-rendered deal pages on CDN

**Priority Queues:**
```
High: Payment processing, inventory updates
Medium: Order confirmation emails, analytics
Low: Recommendations, reviews sync
```

### Scaling Strategy

| Component | Strategy |
|-----------|----------|
| Product Catalog | Shard by category, read replicas |
| Search | Elasticsearch cluster, sharded by category |
| Cart | Redis Cluster, sharded by user_id |
| Inventory | Shard by product_id, strong consistency |
| Orders | Shard by user_id, event sourcing |
| Images | S3 + CloudFront CDN |
| Sessions | Redis with sticky sessions |

### Database Choices

| Data Type | Database | Reason |
|-----------|----------|--------|
| Product catalog | PostgreSQL (sharded) | ACID, complex queries |
| Search index | Elasticsearch | Full-text, facets |
| User sessions/cart | Redis Cluster | Speed, TTL |
| Orders | PostgreSQL + Kafka | Event sourcing, consistency |
| Analytics | ClickHouse/Redshift | OLAP, aggregations |
| Recommendations | Redis/DynamoDB | Low latency lookups |

---

## Otvet (RU)

### Требования

**Функциональные:**
- Каталог товаров с поиском и фильтрацией
- Корзина покупок (сохраняется между сессиями)
- Управление запасами (реальное время)
- Обработка заказов и оплата
- Отзывы и рейтинги пользователей
- Маркетплейс для продавцов
- Рекомендательная система
- Отслеживание склада и доставки

**Нефункциональные:**
- 300M активных пользователей, 100M DAU
- 500M товаров в каталоге
- 1M+ заказов/день в пик (Black Friday: 10x)
- 99.99% доступность (особенно checkout)
- Низкая задержка поиска (<100мс)
- Строгая консистентность для запасов/платежей
- Глобальное мультирегиональное развертывание

### Оценка нагрузки

```
DAU: 100M
Просмотры товаров: 100M * 10 = 1B/день = 11,574/сек
Поисковые запросы: 100M * 5 = 500M/день = 5,787/сек
Заказы: 1M/день = 11.5/сек (пик: 100/сек)

Каталог товаров: 500M * 10KB = 5TB
Данные пользователей: 300M * 5KB = 1.5TB
История заказов: 1M/день * 2KB * 365 = 730GB/год
Изображения: 500M товаров * 10 изображений * 500KB = 2.5PB
```

### Основные сервисы

**1. Сервис каталога товаров**
- CRUD операции для товаров
- Управление категориями/атрибутами
- Листинги продавцов
- Цены и наличие

**2. Сервис поиска**
- Полнотекстовый поиск (Elasticsearch)
- Фасетная фильтрация (цена, бренд, категория)
- Автодополнение
- Персонализированное ранжирование

**3. Сервис корзины**
- Сессионные и постоянные корзины
- Объединение корзин при входе
- Резервирование запасов (мягкая блокировка)
- Обновление цен

**4. Сервис запасов**
- Отслеживание остатков в реальном времени
- Распределение по складам
- Управление резервированием
- Уведомления о появлении товара

**5. Сервис заказов**
- Создание и валидация заказов
- Оркестрация платежей
- Машина состояний заказа
- Отслеживание доставки

### Архитектура поиска товаров

```
Запрос пользователя
    │
    ▼
┌──────────────────┐
│  Парсер запроса  │ ← Токенизация, исправление опечаток
└────────┬─────────┘
         │
    ┌────▼────┐
    │  Кеш?   │──Да──→ Вернуть кешированные результаты
    └────┬────┘
         │ Нет
    ┌────▼─────────────┐
    │  Elasticsearch   │
    │  Кластер         │
    │  (Шардирован по  │
    │   категориям)    │
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │ Слой ранжирования│ ← Персонализация, релевантность
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │ Объединение      │ ← Реклама, спонсорские товары
    │ результатов      │
    └──────────────────┘
```

### Дизайн корзины покупок

**Почему Redis для корзины:**
- Субмиллисекундная задержка
- Атомарные операции (HINCRBY для количества)
- TTL для брошенных корзин
- Pub/Sub для обновлений в реальном времени

**Модель данных корзины:**
```
Ключ: cart:{user_id}
Тип: Hash

Поля:
  product_1234: {"qty": 2, "price": 29.99, "added_at": 1706000000}
  product_5678: {"qty": 1, "price": 149.99, "added_at": 1706001000}

TTL: 30 дней (обновляется при доступе)
```

### Управление запасами

**Проблема:** Предотвратить пересортировку при высокой нагрузке.

**Решение: Двухфазная блокировка запасов**

```
Фаза 1 - Мягкая блокировка (добавление в корзину):
  - Уменьшить available_count в Redis
  - Установить TTL (15 минут)
  - При истечении - автоосвобождение

Фаза 2 - Жесткая блокировка (Checkout):
  - Проверить валидность мягкой блокировки
  - Уменьшить фактический запас в БД (транзакция)
  - Создать запись заказа
  - Освободить мягкую блокировку
```

### Pipeline обработки заказов

```
                    ┌────────────────┐
                    │ Заказ создан   │
                    │   (PENDING)    │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │    Запасы      │
                    │  зарезервированы│
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐     ┌──────────────┐
                    │   Обработка    │────►│   FAILED     │
                    │    платежа     │     │(Освоб. запас)│
                    └───────┬────────┘     └──────────────┘
                            │ Успех
                    ┌───────▼────────┐
                    │  ПОДТВЕРЖДЕН   │
                    └───────┬────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
       ┌──────▼──────┐ ┌────▼────┐ ┌──────▼──────┐
       │ Распределение│ │ Уведом. │ │   Уведом.  │
       │  по складам │ │ продавца│ │   клиента  │
       └──────┬──────┘ └─────────┘ └─────────────┘
              │
       ┌──────▼──────┐
       │  ОТПРАВЛЕН  │
       └──────┬──────┘
              │
       ┌──────▼──────┐
       │  ДОСТАВЛЕН  │
       └─────────────┘
```

### Рекомендательная система

**Подходы:**

1. **Коллаборативная фильтрация:**
   - "Покупатели, купившие X, также купили Y"
   - Матрица взаимодействий пользователь-товар
   - Матричная факторизация (ALS)

2. **Контентная фильтрация:**
   - Похожие атрибуты товаров
   - Аффинити категорий
   - Аффинити брендов

3. **Гибрид (Реальное время + Batch):**
```
Batch Pipeline (ежедневно):
  - Обработка истории покупок
  - Обучение ML моделей
  - Генерация маппингов товар-товар
  - Сохранение в Redis/DynamoDB

Real-Time слой:
  - Поведение текущей сессии
  - Недавно просмотренные товары
  - Объединение с batch рекомендациями
  - Бизнес-правила (без дубликатов, только в наличии)
```

### Платформа продавцов

**Мультитенантная архитектура:**
- Seller Portal для управления товарами
- Управление заказами для продавцов
- Дашборд аналитики
- Расчет комиссий
- Выплаты продавцам

### Обработка пиковых нагрузок (Black Friday)

**Стратегии:**
1. **Pre-warming:** Кеширование популярных товаров заранее
2. **Queue-based checkout:** Rate limiting, показ позиции в очереди
3. **Circuit breakers:** Graceful degradation некритичных сервисов
4. **Зарезервированная мощность:** Предварительное масштабирование
5. **Статические fallback:** Предрендеренные страницы на CDN

### Стратегия масштабирования

| Компонент | Стратегия |
|-----------|-----------|
| Каталог | Шардирование по категории, read replicas |
| Поиск | Elasticsearch кластер, шарды по категории |
| Корзина | Redis Cluster, шардирование по user_id |
| Запасы | Шардирование по product_id, строгая консистентность |
| Заказы | Шардирование по user_id, event sourcing |
| Изображения | S3 + CloudFront CDN |

### Выбор баз данных

| Тип данных | База данных | Причина |
|------------|-------------|---------|
| Каталог товаров | PostgreSQL (sharded) | ACID, сложные запросы |
| Поисковый индекс | Elasticsearch | Полнотекстовый поиск, фасеты |
| Сессии/корзина | Redis Cluster | Скорость, TTL |
| Заказы | PostgreSQL + Kafka | Event sourcing, консистентность |
| Аналитика | ClickHouse/Redshift | OLAP, агрегации |
| Рекомендации | Redis/DynamoDB | Низкая задержка |

---

## Follow-ups

- How do you handle flash sales with limited inventory?
- How do you implement cross-border e-commerce with multiple currencies?
- How do you design the A/B testing infrastructure for the recommendation engine?
- How do you handle returns and refunds at scale?

## Related Questions

### Prerequisites (Easier)
- [[q-caching-strategies--system-design--medium]] - Caching
- [[q-message-queues-event-driven--system-design--medium]] - Message queues
- [[q-elasticsearch-full-text-search--system-design--medium]] - Elasticsearch

### Related (Same Level)
- [[q-design-uber--system-design--hard]] - Uber (different domain, similar scale)
- [[q-design-netflix--system-design--hard]] - Netflix (recommendations)
- [[q-design-notification-system--system-design--hard]] - Notifications

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Sharding
- [[q-cqrs-pattern--system-design--hard]] - CQRS
- [[q-saga-pattern--system-design--hard]] - Saga pattern
