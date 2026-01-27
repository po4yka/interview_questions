---
id: q-design-ticketmaster
title: Design Ticketmaster (Ticket Booking)
aliases:
- Design Ticketmaster
- Ticket Booking System
- Flash Sale System
- Concert Ticket System
topic: system-design
subtopics:
- design-problems
- high-concurrency
- booking-systems
- flash-sales
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-rate-limiting-algorithms--system-design--medium
- q-distributed-tracing--system-design--medium
- q-saga-pattern--system-design--hard
- q-caching-strategies--system-design--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- design-problems
- difficulty/hard
- high-concurrency
- system-design
anki_cards:
- slug: q-design-ticketmaster-0-en
  anki_id: null
  synced_at: null
- slug: q-design-ticketmaster-0-ru
  anki_id: null
  synced_at: null
---
# Question (EN)
> How would you design a ticket booking system like Ticketmaster that handles flash sales with millions of concurrent users trying to buy tickets?

# Vopros (RU)
> Как бы вы спроектировали систему бронирования билетов, подобную Ticketmaster, для обработки мгновенных распродаж с миллионами одновременных пользователей?

---

## Answer (EN)

### Requirements

**Functional**:
- Browse events, view venue/seat maps
- Select seats and hold them temporarily
- Complete purchase within time limit
- Prevent overselling (no double-booking)
- Handle cancellations and refunds

**Non-functional**:
- Handle 10M+ concurrent users during flash sales
- <100ms seat availability checks
- Fair access (prevent bots, ensure fairness)
- 99.99% availability during sales
- Strong consistency for seat inventory

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Users / Browsers                        │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                          CDN + WAF                              │
│              (Static assets, DDoS protection)                   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                     Virtual Waiting Room                        │
│              (Queue during high demand periods)                 │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                        API Gateway                              │
│           (Rate Limiting, Auth, Bot Detection)                  │
└───────┬─────────────┬─────────────┬─────────────┬───────────────┘
        │             │             │             │
  ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
  │  Event    │ │ Inventory │ │  Booking  │ │  Payment  │
  │  Service  │ │  Service  │ │  Service  │ │  Service  │
  └───────────┘ └─────┬─────┘ └───────────┘ └───────────┘
                      │
                ┌─────▼─────┐
                │   Redis   │
                │ (Seat     │
                │  Holds)   │
                └───────────┘
```

### Seat Inventory Management

```
Seat States:
┌──────────────┐
│  AVAILABLE   │◄─────────────────────────────┐
└──────┬───────┘                              │
       │ User selects                         │
       ▼                                      │
┌──────────────┐     TTL expires              │
│    HELD      │──────────────────────────────┘
└──────┬───────┘
       │ Payment success
       ▼
┌──────────────┐
│   RESERVED   │
└──────┬───────┘
       │ Ticket issued
       ▼
┌──────────────┐
│     SOLD     │
└──────────────┘

Hold TTL: 5-10 minutes (configurable per event)
```

### Optimistic vs Pessimistic Locking

| Approach | Description | Use Case |
|----------|-------------|----------|
| **Pessimistic** | Lock seat on selection, block others | Low concurrency, VIP sales |
| **Optimistic** | Check version on commit, retry on conflict | High concurrency, general sales |

**Recommended: Optimistic with Redis**

```python
# Optimistic locking with Redis
def hold_seat(event_id, seat_id, user_id, ttl=600):
    key = f"seat:{event_id}:{seat_id}"

    # SETNX - only succeeds if key doesn't exist
    success = redis.set(key, user_id, nx=True, ex=ttl)

    if success:
        return {"status": "held", "expires_in": ttl}
    else:
        return {"status": "unavailable"}
```

### Virtual Waiting Room

Protects backend during flash sales by queuing excess traffic.

```
Implementation:
1. User arrives → Assigned position in queue
2. Queue drains at controlled rate (e.g., 1000 users/sec)
3. User gets "token" when turn arrives
4. Token required for all booking APIs
5. Token expires after session timeout

Redis Sorted Set:
  ZADD waitingroom:{event_id} {timestamp} {user_id}
  ZRANGE waitingroom:{event_id} 0 999  # Get next 1000

Fairness:
- Random position assignment (prevents time-based advantage)
- CAPTCHA on entry (bot prevention)
- One queue position per verified account
```

### Rate Limiting & Bot Prevention

```
Multi-layer defense:

1. CDN/WAF Layer:
   - IP-based rate limiting
   - Geographic restrictions
   - Known bot signatures

2. Virtual Queue Layer:
   - CAPTCHA challenge
   - Device fingerprinting
   - Behavioral analysis

3. API Layer:
   - User-based rate limits
   - Request pattern detection
   - Token bucket per user

4. Business Logic:
   - Max tickets per user per event
   - Purchase history analysis
   - Velocity checks
```

### Database Design

```sql
-- Events
CREATE TABLE events (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    venue_id UUID,
    event_date TIMESTAMP,
    sale_start TIMESTAMP,
    sale_end TIMESTAMP,
    status ENUM('draft', 'on_sale', 'sold_out', 'cancelled')
);

-- Seat Inventory (per event)
CREATE TABLE seats (
    id UUID PRIMARY KEY,
    event_id UUID REFERENCES events(id),
    section VARCHAR(50),
    row VARCHAR(10),
    number INT,
    price_tier_id UUID,
    status ENUM('available', 'held', 'reserved', 'sold'),
    held_by UUID,
    held_until TIMESTAMP,
    version INT DEFAULT 0,  -- Optimistic locking

    INDEX idx_event_status (event_id, status),
    UNIQUE (event_id, section, row, number)
);

-- Bookings
CREATE TABLE bookings (
    id UUID PRIMARY KEY,
    user_id UUID,
    event_id UUID,
    status ENUM('pending', 'confirmed', 'cancelled'),
    total_amount DECIMAL(10, 2),
    created_at TIMESTAMP,
    confirmed_at TIMESTAMP
);

-- Booking Items (seats in booking)
CREATE TABLE booking_items (
    booking_id UUID REFERENCES bookings(id),
    seat_id UUID REFERENCES seats(id),
    price DECIMAL(10, 2),
    PRIMARY KEY (booking_id, seat_id)
);
```

### Booking Flow (Distributed Transaction)

```
User selects seats → Hold seats → Checkout → Payment → Confirm

Saga Pattern for booking:

1. Create booking (PENDING)
   ↓
2. Hold seats in Redis (5 min TTL)
   ↓ (on failure: compensate step 1)
3. Reserve seats in DB (optimistic lock)
   ↓ (on failure: release Redis holds, compensate step 1)
4. Process payment
   ↓ (on failure: release seats, cancel booking)
5. Confirm booking
   ↓
6. Generate tickets
   ↓
7. Send confirmation email

Compensation actions:
- releaseSeats()
- refundPayment()
- cancelBooking()
```

### Payment Integration

```
Key considerations:

1. Idempotency:
   - Generate idempotency_key before payment
   - Retry-safe with same key
   - Store payment attempts with outcomes

2. Timeout Handling:
   - Payment timeout = 3 minutes
   - If timeout: query payment status
   - If unknown: hold seats, resolve async

3. Failure Modes:
   - Payment declined → Release seats immediately
   - Network error → Retry with backoff
   - Timeout → Async reconciliation

4. Webhook Processing:
   - Payment success → Confirm booking
   - Payment failed → Release seats
   - Refund → Update booking status
```

### Caching Strategy

```
Multi-tier caching:

1. CDN (edge):
   - Event pages (static content)
   - Venue maps (images)
   - TTL: minutes to hours

2. Application Cache (Redis):
   - Event metadata (TTL: 1 min)
   - Price tiers (TTL: 5 min)
   - Seat availability counts (TTL: 10 sec)

3. Seat Holds (Redis):
   - Real-time seat status
   - TTL-based auto-expiry
   - Single source of truth during sale

Cache invalidation:
- Event updates → Invalidate event cache
- Sale starts → Warm seat availability cache
- Booking confirmed → Update availability counts
```

### Handling Failures Mid-Booking

```
Failure scenarios and recovery:

1. User closes browser during hold:
   - Redis TTL expires → Seats auto-release
   - No action needed

2. Payment service down:
   - Circuit breaker activates
   - Hold extended if user in checkout
   - Show "Try again" message

3. Database failure during reservation:
   - Saga compensation: release Redis holds
   - User notified, can retry

4. Booking service crash:
   - Seats held in Redis survive
   - On restart: reconcile holds with bookings
   - Orphaned holds expire via TTL

5. Network partition:
   - Redis cluster with replicas
   - Prefer CP over AP for inventory
   - Accept brief unavailability over overselling
```

### Scale Numbers

```
Ticketmaster scale:
- 500M+ tickets sold/year
- 10M+ concurrent users during major sales
- <100ms seat availability response
- 5 minute average hold time
- 10,000+ events simultaneously on sale

Traffic spike example (Taylor Swift):
- 14M users in queue
- 2M tickets available
- 3.5B system requests in one day
- Queue wait: 2+ hours
```

### Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Seat holds | Redis with TTL | Fast, auto-expiry, atomic ops |
| Locking | Optimistic | Scales better under contention |
| Queue | Virtual waiting room | Protects backend, ensures fairness |
| Transactions | Saga pattern | Distributed, compensatable |
| Consistency | Strong for inventory | No overselling allowed |

---

## Otvet (RU)

### Требования

**Функциональные**:
- Просмотр мероприятий, схемы залов
- Выбор и временное удержание мест
- Оплата в пределах лимита времени
- Предотвращение перепродажи (без двойного бронирования)
- Обработка отмен и возвратов

**Нефункциональные**:
- Обработка 10M+ одновременных пользователей при мгновенных распродажах
- <100мс проверка доступности мест
- Справедливый доступ (защита от ботов)
- 99.99% доступность во время продаж
- Строгая консистентность для инвентаря мест

### Управление инвентарём мест

```
Состояния места:
┌──────────────┐
│  AVAILABLE   │◄─────────────────────────────┐
│ (доступно)   │                              │
└──────┬───────┘                              │
       │ Пользователь выбирает                │
       ▼                                      │
┌──────────────┐     TTL истёк                │
│    HELD      │──────────────────────────────┘
│ (удержано)   │
└──────┬───────┘
       │ Оплата успешна
       ▼
┌──────────────┐
│   RESERVED   │
│(зарезервир.) │
└──────┬───────┘
       │ Билет выдан
       ▼
┌──────────────┐
│     SOLD     │
│  (продано)   │
└──────────────┘

TTL удержания: 5-10 минут
```

### Оптимистичная vs Пессимистичная блокировка

| Подход | Описание | Применение |
|--------|----------|------------|
| **Пессимистичная** | Блокировка места при выборе | Низкая конкуренция, VIP |
| **Оптимистичная** | Проверка версии при коммите | Высокая конкуренция |

**Рекомендуется: Оптимистичная с Redis**

```python
# Оптимистичная блокировка через Redis
def hold_seat(event_id, seat_id, user_id, ttl=600):
    key = f"seat:{event_id}:{seat_id}"

    # SETNX - успех только если ключ не существует
    success = redis.set(key, user_id, nx=True, ex=ttl)

    if success:
        return {"status": "held", "expires_in": ttl}
    else:
        return {"status": "unavailable"}
```

### Виртуальная комната ожидания

Защищает бэкенд при мгновенных распродажах через очередь избыточного трафика.

```
Реализация:
1. Пользователь приходит → Назначается позиция в очереди
2. Очередь опустошается с контролируемой скоростью
3. Пользователь получает "токен" когда приходит очередь
4. Токен требуется для всех API бронирования
5. Токен истекает после таймаута сессии

Redis Sorted Set:
  ZADD waitingroom:{event_id} {timestamp} {user_id}
  ZRANGE waitingroom:{event_id} 0 999

Справедливость:
- Рандомная позиция (предотвращает преимущество по времени)
- CAPTCHA на входе
- Одна позиция в очереди на верифицированный аккаунт
```

### Rate Limiting и защита от ботов

```
Многоуровневая защита:

1. CDN/WAF уровень:
   - Rate limiting по IP
   - Географические ограничения
   - Сигнатуры известных ботов

2. Уровень очереди:
   - CAPTCHA
   - Fingerprinting устройства
   - Поведенческий анализ

3. API уровень:
   - Лимиты по пользователю
   - Детекция паттернов запросов
   - Token bucket на пользователя

4. Бизнес-логика:
   - Максимум билетов на пользователя
   - Анализ истории покупок
```

### Поток бронирования (Saga паттерн)

```
Выбор мест → Удержание → Оплата → Подтверждение

1. Создать бронирование (PENDING)
   ↓
2. Удержать места в Redis (5 мин TTL)
   ↓ (при ошибке: компенсация шага 1)
3. Зарезервировать в БД (оптимистичная блокировка)
   ↓ (при ошибке: освободить Redis, компенсация шага 1)
4. Провести оплату
   ↓ (при ошибке: освободить места, отменить бронирование)
5. Подтвердить бронирование
   ↓
6. Сгенерировать билеты
   ↓
7. Отправить подтверждение на email

Компенсационные действия:
- releaseSeats()
- refundPayment()
- cancelBooking()
```

### Стратегия кэширования

```
Многоуровневое кэширование:

1. CDN (edge):
   - Страницы мероприятий
   - Карты залов
   - TTL: минуты-часы

2. Application Cache (Redis):
   - Метаданные мероприятий (TTL: 1 мин)
   - Ценовые тарифы (TTL: 5 мин)
   - Счётчики доступных мест (TTL: 10 сек)

3. Удержания мест (Redis):
   - Реальный статус мест
   - Автоистечение по TTL
   - Единый источник правды во время продажи
```

### Обработка ошибок во время бронирования

```
Сценарии отказов и восстановление:

1. Пользователь закрыл браузер при удержании:
   - TTL Redis истекает → Места автоосвобождаются
   - Действий не требуется

2. Платёжный сервис недоступен:
   - Circuit breaker активируется
   - Удержание продлевается если пользователь в checkout
   - Показать "Попробуйте снова"

3. Сбой БД при резервировании:
   - Компенсация Saga: освободить Redis holds
   - Пользователь уведомлён, может повторить

4. Сбой сервиса бронирования:
   - Удержания в Redis сохраняются
   - При рестарте: сверка holds с бронированиями
   - Осиротевшие holds истекут по TTL

5. Сетевой раздел:
   - Redis кластер с репликами
   - Предпочесть CP над AP для инвентаря
   - Принять краткую недоступность вместо overselling
```

### Масштабные числа

```
Масштаб Ticketmaster:
- 500M+ билетов/год
- 10M+ одновременных пользователей
- <100мс ответ на проверку доступности
- 5 минут среднее время удержания
- 10,000+ мероприятий одновременно в продаже

Пример пика (Taylor Swift):
- 14M пользователей в очереди
- 2M билетов доступно
- 3.5B системных запросов за день
- Ожидание в очереди: 2+ часа
```

### Ключевые технические решения

| Решение | Выбор | Обоснование |
|---------|-------|-------------|
| Удержание мест | Redis с TTL | Быстро, автоистечение, атомарные операции |
| Блокировка | Оптимистичная | Лучше масштабируется при конкуренции |
| Очередь | Виртуальная комната ожидания | Защита бэкенда, справедливость |
| Транзакции | Saga паттерн | Распределённые, компенсируемые |
| Консистентность | Строгая для инвентаря | Недопустим overselling |

---

## Follow-ups

- How would you implement dynamic pricing (like surge pricing for high-demand events)?
- How do you handle scalper detection and prevention?
- What happens if Redis fails during a flash sale?
- How would you design the seat selection UI for a 50,000 seat stadium?
- How do you handle partial order failures (some seats successful, some failed)?
- What is the difference between general admission and reserved seating architectures?
