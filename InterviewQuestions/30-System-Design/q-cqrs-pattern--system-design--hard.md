---
id: sysdes-066
title: CQRS Pattern
aliases:
- CQRS
- Command Query Responsibility Segregation
- Read Write Separation
topic: system-design
subtopics:
- advanced
- patterns
- architecture
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-event-sourcing--system-design--hard
- q-database-sharding-partitioning--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- advanced
- difficulty/hard
- patterns
- system-design
anki_cards:
- slug: sysdes-066-0-en
  language: en
  anki_id: 1769160582374
  synced_at: '2026-01-23T13:49:17.750232'
- slug: sysdes-066-0-ru
  language: ru
  anki_id: 1769160582400
  synced_at: '2026-01-23T13:49:17.751629'
---
# Question (EN)
> What is CQRS? When would you use it, and how does it relate to event sourcing?

# Vopros (RU)
> Что такое CQRS? Когда его использовать и как он связан с event sourcing?

---

## Answer (EN)

**CQRS** (Command Query Responsibility Segregation) separates read and write operations into different models, allowing each to be optimized independently.

### Traditional vs CQRS

```
Traditional (Single Model):
┌──────────────────────────────────────┐
│              Application             │
│  Create ─┐                           │
│  Read   ─┼─► Single Model ◄─► Single DB
│  Update ─┤                           │
│  Delete ─┘                           │
└──────────────────────────────────────┘

CQRS (Separate Models):
┌──────────────────────────────────────────────────┐
│                  Application                      │
│                                                   │
│  Commands ──► Write Model ──► Write DB           │
│                    │                              │
│                    │ (sync/async)                 │
│                    ▼                              │
│  Queries ◄── Read Model ◄── Read DB              │
└──────────────────────────────────────────────────┘
```

### Command Side (Write)

```
Commands:
- CreateOrder(items, userId)
- UpdateOrderStatus(orderId, status)
- CancelOrder(orderId, reason)

Write Model:
- Validates business rules
- Enforces invariants
- Normalized for consistency
- Optimized for writes
```

### Query Side (Read)

```
Queries:
- GetOrderDetails(orderId)
- GetUserOrders(userId, filters)
- GetOrdersByStatus(status)

Read Model:
- Denormalized for fast queries
- Pre-computed aggregations
- Multiple projections for different views
- Optimized for reads
```

### Architecture with Event Sourcing

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Command   │───►│   Event     │───►│   Write     │
│   Handler   │    │   Store     │    │   Model     │
└─────────────┘    └──────┬──────┘    └─────────────┘
                          │
                          │ Events
                          ▼
┌─────────────┐    ┌──────────────┐   ┌─────────────┐
│   Query     │◄───│  Projector   │◄──│   Read      │
│   Handler   │    │              │   │   Model     │
└─────────────┘    └──────────────┘   └─────────────┘

Projector: Transforms events into read-optimized views
```

### Benefits

| Benefit | Description |
|---------|-------------|
| Independent scaling | Scale read/write separately |
| Optimized models | Each optimized for its purpose |
| Simpler queries | Denormalized, no complex joins |
| Performance | Read replicas, caching |
| Flexibility | Different storage for read/write |

### Challenges

| Challenge | Mitigation |
|-----------|------------|
| Eventual consistency | Accept or use sync updates |
| Complexity | Only use when benefits outweigh |
| Data synchronization | Event-driven updates |
| Testing | Test both sides independently |

### When to Use CQRS

**Good fit:**
- High read/write ratio disparity
- Complex domain logic
- Different scaling needs
- Multiple read views needed
- Event sourcing already used

**Poor fit:**
- Simple CRUD
- Consistent read-after-write required
- Small scale applications
- Team unfamiliar with pattern

### Example: E-commerce

```
Write Model (Orders):
- Validates inventory
- Processes payment
- Stores normalized order data

Read Models (Multiple):
- OrderSummary (for listing)
- OrderDetails (for detail view)
- UserOrderHistory (for user dashboard)
- AdminDashboard (for analytics)

Each read model optimized for its use case
```

---

## Otvet (RU)

**CQRS** (Command Query Responsibility Segregation) разделяет операции чтения и записи на разные модели, позволяя оптимизировать каждую независимо.

### Традиционный vs CQRS

```
Традиционный (Одна модель):
  Create ─┐
  Read   ─┼─► Single Model ◄─► Single DB
  Update ─┤
  Delete ─┘

CQRS (Раздельные модели):
  Commands ──► Write Model ──► Write DB
                   │
                   │ (sync/async)
                   ▼
  Queries ◄── Read Model ◄── Read DB
```

### Command Side (Запись)

```
Commands:
- CreateOrder(items, userId)
- UpdateOrderStatus(orderId, status)

Write Model:
- Валидирует бизнес-правила
- Обеспечивает инварианты
- Нормализован для согласованности
- Оптимизирован для записи
```

### Query Side (Чтение)

```
Queries:
- GetOrderDetails(orderId)
- GetUserOrders(userId, filters)

Read Model:
- Денормализован для быстрых запросов
- Предвычисленные агрегации
- Множество проекций для разных view
- Оптимизирован для чтения
```

### Преимущества

| Преимущество | Описание |
|--------------|----------|
| Независимое масштабирование | Масштабировать read/write отдельно |
| Оптимизированные модели | Каждая оптимизирована под свою задачу |
| Простые запросы | Денормализованные, без сложных join |
| Производительность | Read replicas, кеширование |

### Проблемы

| Проблема | Решение |
|----------|---------|
| Eventual consistency | Принять или использовать sync |
| Сложность | Использовать только когда польза перевешивает |
| Синхронизация данных | Event-driven обновления |

### Когда использовать CQRS

**Хорошо подходит:**
- Большое различие в соотношении read/write
- Сложная доменная логика
- Разные потребности в масштабировании
- Нужны множественные read view
- Event sourcing уже используется

**Плохо подходит:**
- Простой CRUD
- Требуется согласованность read-after-write
- Малый масштаб приложений
- Команда незнакома с паттерном

---

## Follow-ups

- How do you handle consistency between read and write models?
- Can you use CQRS without event sourcing?
- How do you implement real-time updates with CQRS?
