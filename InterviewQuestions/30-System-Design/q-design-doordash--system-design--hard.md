---
id: q-design-doordash
title: Design DoorDash (Food Delivery)
aliases:
- Design DoorDash
- Food Delivery System
- Three-Sided Marketplace
topic: system-design
subtopics:
- design-problems
- logistics
- real-time
- marketplace
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-uber--system-design--hard
- q-geospatial-indexing--system-design--medium
- q-websockets-sse-long-polling--system-design--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- design-problems
- difficulty/hard
- logistics
- real-time
- system-design
anki_cards:
- slug: q-design-doordash-0-en
  anki_id: null
  synced_at: null
- slug: q-design-doordash-0-ru
  anki_id: null
  synced_at: null
---
# Question (EN)
> How would you design a food delivery platform like DoorDash?

# Vopros (RU)
> Как бы вы спроектировали платформу доставки еды, подобную DoorDash?

---

## Answer (EN)

### Requirements

**Functional**:
- Restaurant search and discovery
- Menu browsing and ordering
- Real-time order tracking
- Driver matching and dispatch
- Payments and tipping
- Ratings and reviews

**Non-functional**:
- Order placement < 2 seconds
- ETA accuracy within 5 minutes
- 99.9% availability during peak hours
- Support 10M+ orders/day

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│     Customer App        Restaurant App         Driver App         │
└─────────┬────────────────────┬────────────────────┬───────────────┘
          │                    │                    │
┌─────────▼────────────────────▼────────────────────▼───────────────┐
│                         API Gateway                                │
│              (Load Balancing, Auth, Rate Limiting)                │
└───────┬──────────┬───────────┬───────────┬───────────┬────────────┘
        │          │           │           │           │
  ┌─────▼─────┐ ┌──▼───┐ ┌─────▼─────┐ ┌───▼───┐ ┌─────▼─────┐
  │ Restaurant│ │Search│ │   Order   │ │Dispatch│ │  Payment  │
  │  Service  │ │Engine│ │  Service  │ │Service │ │  Service  │
  └───────────┘ └──────┘ └─────┬─────┘ └───┬───┘ └───────────┘
                               │           │
                         ┌─────▼───────────▼─────┐
                         │    Message Queue      │
                         │      (Kafka)          │
                         └───────────────────────┘
```

### Three-Sided Marketplace

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  CUSTOMERS  │◄───────►│  PLATFORM   │◄───────►│ RESTAURANTS │
│             │         │             │         │             │
│ - Search    │         │ - Matching  │         │ - Menu mgmt │
│ - Order     │         │ - Pricing   │         │ - Order mgmt│
│ - Pay       │         │ - Dispatch  │         │ - Prep time │
│ - Track     │         │ - Payments  │         │ - Ratings   │
└─────────────┘         └──────┬──────┘         └─────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │   DRIVERS   │
                        │  (Dashers)  │
                        │             │
                        │ - Accept    │
                        │ - Pick up   │
                        │ - Deliver   │
                        │ - Earnings  │
                        └─────────────┘
```

### Order State Machine

```
       ┌──────────┐
       │ CREATED  │ (customer placed order)
       └────┬─────┘
            ↓
       ┌──────────┐
       │ CONFIRMED│ (payment processed)
       └────┬─────┘
            ↓
       ┌──────────┐
       │ PREPARING│ (restaurant cooking)
       └────┬─────┘
            ↓
       ┌──────────┐
       │  READY   │ (food ready for pickup)
       └────┬─────┘
            ↓
       ┌──────────┐
       │PICKED_UP │ (driver has food)
       └────┬─────┘
            ↓
       ┌──────────┐
       │DELIVERING│ (driver en route)
       └────┬─────┘
            ↓
       ┌──────────┐
       │DELIVERED │ (customer received)
       └──────────┘
```

### Driver Matching and Dispatch

```
Dispatch Algorithm:

1. Order becomes READY (or near-ready)
2. Find available drivers:
   - Query geospatial index (radius around restaurant)
   - Filter: available, not on delivery, vehicle type
3. Score candidates:
   - Distance to restaurant (minimize wait)
   - Driver rating and acceptance rate
   - Delivery history with this restaurant
   - Current earnings (fairness)
4. Send offer to top driver (30s timeout)
5. If declined → next driver
6. Match confirmed → Update order status

Batching Optimization:
- Multiple orders to same area
- Stack orders from nearby restaurants
- Reduces driver idle time
- Improves delivery density
```

### ETA Prediction

```
ETA Components:
┌─────────────────────────────────────────────────────────┐
│ Total ETA = Prep Time + Pickup Wait + Delivery Time    │
└─────────────────────────────────────────────────────────┘

Prep Time Estimation:
- Historical data per restaurant
- Current queue depth
- Time of day patterns
- Item complexity (ML model)

Delivery Time Estimation:
- Real-time traffic data
- Route optimization
- Historical delivery times
- Weather conditions

Continuous Updates:
- Re-calculate every 30 seconds
- Push updates via WebSocket
- Adjust for delays (kitchen, traffic)
```

### Restaurant Search and Discovery

```
Search System:

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Query     │────►│ Elasticsearch│────►│   Results   │
│ "pizza near │     │             │     │  (ranked)   │
│    me"      │     │ - Name match│     │             │
└─────────────┘     │ - Cuisine   │     └─────────────┘
                    │ - Location  │
                    │ - Rating    │
                    └─────────────┘

Ranking Factors:
- Relevance to search query
- Distance from customer
- Restaurant rating
- Estimated delivery time
- Conversion rate (sponsored)
- Currently open/closed
```

### Dynamic Pricing (Surge)

```
Surge Pricing Triggers:
- High demand, low driver supply
- Bad weather
- Special events
- Peak meal times

Pricing Formula:
  base_price + distance_fee + service_fee + surge_multiplier

Surge Multiplier:
  1.0x (normal) → 1.5x → 2.0x → 2.5x (extreme)

Supply-Side Response:
- Higher earnings attract more drivers
- Notify offline drivers of surge
- Self-balancing mechanism
```

### Payment Flow

```
Order Payment:
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Customer │───►│ Auth     │───►│ Hold     │───►│ Capture  │
│ Checkout │    │ Card     │    │ Amount   │    │ on       │
│          │    │          │    │          │    │ Delivery │
└──────────┘    └──────────┘    └──────────┘    └──────────┘

Payout Distribution:
┌────────────────────────────────────────────────────────┐
│ Order Total: $30                                       │
│ ├── Restaurant: $21 (70%)                             │
│ ├── Driver: $6 (base + tips)                          │
│ └── Platform: $3 (10% commission)                     │
└────────────────────────────────────────────────────────┘

Tipping:
- Post-delivery tip (can adjust)
- 100% goes to driver
- Default tip suggestions
```

### Real-Time Order Tracking

```
Tracking System:

Driver App                Platform                Customer App
    │                        │                        │
    │ Location update        │                        │
    │ (every 5 sec)          │                        │
    ├───────────────────────►│                        │
    │                        │ Push update            │
    │                        ├───────────────────────►│
    │                        │                        │ Show on map
    │                        │                        │

Technology Stack:
- WebSocket for real-time updates
- Redis Pub/Sub for event distribution
- GPS with battery optimization
- Geofencing for arrival detection
```

### Key Technical Challenges

| Challenge | Solution |
|-----------|----------|
| Peak hour scaling | Auto-scaling, queue-based load leveling |
| Driver-order matching | Real-time geospatial index (Redis) |
| ETA accuracy | ML models + real-time traffic |
| Order batching | Graph optimization algorithms |
| Payment reliability | Idempotent transactions, saga pattern |
| Restaurant integration | Tablet app, POS integration, API |

### Scale Numbers

```
DoorDash scale:
- 25M+ customers
- 500K+ restaurants
- 2M+ drivers (Dashers)
- 1.5B+ orders/year
- Peak: 2M+ orders/day
- Location updates: 50M+/hour during peak
```

---

## Otvet (RU)

### Требования

**Функциональные**:
- Поиск ресторанов
- Просмотр меню и заказ
- Отслеживание заказа в реальном времени
- Матчинг и диспетчеризация курьеров
- Платежи и чаевые
- Рейтинги и отзывы

**Нефункциональные**:
- Размещение заказа < 2 секунд
- Точность ETA в пределах 5 минут
- 99.9% доступность в пиковые часы
- Поддержка 10M+ заказов/день

### Трёхсторонний маркетплейс

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   КЛИЕНТЫ   │◄───────►│  ПЛАТФОРМА  │◄───────►│  РЕСТОРАНЫ  │
│             │         │             │         │             │
│ - Поиск     │         │ - Матчинг   │         │ - Меню      │
│ - Заказ     │         │ - Ценообр.  │         │ - Заказы    │
│ - Оплата    │         │ - Диспетч.  │         │ - Готовка   │
│ - Трекинг   │         │ - Платежи   │         │ - Рейтинги  │
└─────────────┘         └──────┬──────┘         └─────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │   КУРЬЕРЫ   │
                        │  (Dashers)  │
                        │             │
                        │ - Принять   │
                        │ - Забрать   │
                        │ - Доставить │
                        │ - Заработок │
                        └─────────────┘
```

### Жизненный цикл заказа

```
       ┌──────────┐
       │ СОЗДАН   │ (клиент разместил заказ)
       └────┬─────┘
            ↓
       ┌──────────┐
       │ПОДТВЕРЖДЁН│ (платёж прошёл)
       └────┬─────┘
            ↓
       ┌──────────┐
       │ГОТОВИТСЯ │ (ресторан готовит)
       └────┬─────┘
            ↓
       ┌──────────┐
       │  ГОТОВ   │ (еда готова к выдаче)
       └────┬─────┘
            ↓
       ┌──────────┐
       │ ЗАБРАН   │ (курьер забрал еду)
       └────┬─────┘
            ↓
       ┌──────────┐
       │ДОСТАВЛЯЕТСЯ│ (курьер в пути)
       └────┬─────┘
            ↓
       ┌──────────┐
       │ДОСТАВЛЕН │ (клиент получил)
       └──────────┘
```

### Алгоритм диспетчеризации

```
Алгоритм назначения:

1. Заказ становится ГОТОВ (или почти готов)
2. Найти доступных курьеров:
   - Запрос к геоиндексу (радиус от ресторана)
   - Фильтр: свободен, не на доставке
3. Оценка кандидатов:
   - Расстояние до ресторана
   - Рейтинг и acceptance rate
   - История доставок
   - Текущий заработок (справедливость)
4. Отправить предложение топ курьеру (30с таймаут)
5. При отказе → следующий курьер
6. Матч подтверждён → Обновить статус

Оптимизация батчинга:
- Несколько заказов в один район
- Стекирование заказов из соседних ресторанов
- Сокращение простоя курьера
```

### Предсказание ETA

```
Компоненты ETA:
┌─────────────────────────────────────────────────────────┐
│ Общий ETA = Время готовки + Ожидание + Время доставки  │
└─────────────────────────────────────────────────────────┘

Оценка времени готовки:
- Исторические данные по ресторану
- Текущая очередь заказов
- Паттерны времени суток
- Сложность блюд (ML модель)

Оценка времени доставки:
- Данные о трафике в реальном времени
- Оптимизация маршрута
- Исторические времена доставки
- Погодные условия
```

### Динамическое ценообразование (Surge)

```
Триггеры повышения цены:
- Высокий спрос, мало курьеров
- Плохая погода
- Особые события
- Пиковые часы еды

Формула цены:
  базовая_цена + плата_за_расстояние + сервисный_сбор + множитель

Множитель:
  1.0x (норма) → 1.5x → 2.0x → 2.5x (экстрим)

Реакция предложения:
- Высокий заработок привлекает больше курьеров
- Уведомления офлайн курьерам о surge
- Самобалансирующийся механизм
```

### Поток платежей

```
Распределение выплат:
┌────────────────────────────────────────────────────────┐
│ Сумма заказа: $30                                      │
│ ├── Ресторан: $21 (70%)                               │
│ ├── Курьер: $6 (база + чаевые)                        │
│ └── Платформа: $3 (10% комиссия)                      │
└────────────────────────────────────────────────────────┘

Чаевые:
- Чаевые после доставки (можно изменить)
- 100% идут курьеру
```

### Ключевые технические вызовы

| Вызов | Решение |
|-------|---------|
| Масштабирование в пик | Auto-scaling, очереди |
| Матчинг курьер-заказ | Real-time геоиндекс (Redis) |
| Точность ETA | ML модели + трафик |
| Батчинг заказов | Алгоритмы оптимизации графов |
| Надёжность платежей | Идемпотентность, saga pattern |
| Интеграция ресторанов | Планшет, POS, API |

### Масштабные числа

```
Масштаб DoorDash:
- 25M+ клиентов
- 500K+ ресторанов
- 2M+ курьеров (Dashers)
- 1.5B+ заказов/год
- Пик: 2M+ заказов/день
- Обновления локации: 50M+/час в пик
```

---

## Follow-ups

- How does DoorDash handle order batching optimization?
- What happens when a restaurant is running behind on orders?
- How do you handle driver fraud (fake deliveries)?
- How does the system handle peak load during Super Bowl?
- Design the restaurant onboarding and menu management system.
- How would you implement a loyalty/rewards program?
