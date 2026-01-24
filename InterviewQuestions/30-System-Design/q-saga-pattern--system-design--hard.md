---
id: sysdes-044
title: Saga Pattern
aliases:
- Saga Pattern
- Distributed Transactions
- Compensating Transactions
topic: system-design
subtopics:
- distributed-systems
- transactions
- microservices
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-acid-properties--system-design--medium
- q-sync-async-communication--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- distributed-systems
- difficulty/hard
- transactions
- system-design
anki_cards:
- slug: sysdes-044-0-en
  language: en
  anki_id: 1769159520843
  synced_at: '2026-01-23T13:49:17.768260'
- slug: sysdes-044-0-ru
  language: ru
  anki_id: 1769159520870
  synced_at: '2026-01-23T13:49:17.770527'
---
# Question (EN)
> What is the Saga pattern? How does it handle distributed transactions across microservices?

# Vopros (RU)
> Что такое паттерн Saga? Как он обрабатывает распределённые транзакции между микросервисами?

---

## Answer (EN)

**Saga pattern** manages distributed transactions as a sequence of local transactions, with compensating actions for rollback.

### Why Saga?

```
Problem: Can't use ACID across microservices
         - No distributed lock
         - Services have separate databases
         - 2PC doesn't scale

Solution: Saga = T1 → T2 → T3 (or C3 → C2 → C1 on failure)
          Each step has a compensating action
```

### Saga Types

| Type | Coordination | Pros | Cons |
|------|--------------|------|------|
| Choreography | Events (no coordinator) | Loose coupling, simple | Hard to track, cyclic deps |
| Orchestration | Central coordinator | Easy to understand | Single point of failure |

### Choreography Example

```
Order Saga (event-driven):

1. Order Service → "OrderCreated" event
2. Payment Service → listens → processes → "PaymentCompleted" event
3. Inventory Service → listens → reserves → "InventoryReserved" event
4. Shipping Service → listens → schedules → "OrderShipped" event

On failure at step 3:
3. Inventory Service → "InventoryFailed" event
2. Payment Service → listens → refund → "PaymentRefunded"
1. Order Service → listens → cancel → "OrderCancelled"
```

### Orchestration Example

```
Saga Orchestrator:

┌──────────────────────────────────┐
│         Order Saga               │
│   ┌────────────────────────┐     │
│   │     Orchestrator       │     │
│   └──────────┬─────────────┘     │
│              ↓                   │
│   Step 1: Create Order           │
│              ↓                   │
│   Step 2: Reserve Inventory      │
│              ↓                   │
│   Step 3: Process Payment ──── FAIL
│              ↓                   │
│   Compensate: Release Inventory  │
│              ↓                   │
│   Compensate: Cancel Order       │
└──────────────────────────────────┘
```

### Compensation Design

```python
class OrderSaga:
    steps = [
        SagaStep(
            action=create_order,
            compensation=cancel_order
        ),
        SagaStep(
            action=reserve_inventory,
            compensation=release_inventory
        ),
        SagaStep(
            action=charge_payment,
            compensation=refund_payment
        ),
    ]

    def execute(self):
        completed = []
        for step in self.steps:
            try:
                step.action()
                completed.append(step)
            except Exception:
                # Compensate in reverse order
                for s in reversed(completed):
                    s.compensation()
                raise SagaFailed()
```

### Key Considerations

- **Idempotency**: Steps must be safely retriable
- **Eventual consistency**: Not immediately consistent
- **Compensation logic**: Must handle partial states
- **Timeout handling**: Stuck sagas need resolution

---

## Otvet (RU)

**Паттерн Saga** управляет распределёнными транзакциями как последовательностью локальных транзакций с компенсирующими действиями для отката.

### Почему Saga?

```
Проблема: Нельзя использовать ACID между микросервисами
          - Нет распределённой блокировки
          - Сервисы имеют отдельные БД
          - 2PC не масштабируется

Решение: Saga = T1 → T2 → T3 (или C3 → C2 → C1 при сбое)
         Каждый шаг имеет компенсирующее действие
```

### Типы Saga

| Тип | Координация | Плюсы | Минусы |
|-----|-------------|-------|--------|
| Хореография | События (без координатора) | Слабая связанность | Сложно отслеживать |
| Оркестрация | Центральный координатор | Легко понять | Единая точка отказа |

### Пример хореографии

```
Order Saga (событийный):

1. Order Service → событие "OrderCreated"
2. Payment Service → слушает → обрабатывает → "PaymentCompleted"
3. Inventory Service → слушает → резервирует → "InventoryReserved"
4. Shipping Service → слушает → планирует → "OrderShipped"

При сбое на шаге 3:
3. Inventory Service → событие "InventoryFailed"
2. Payment Service → слушает → возврат → "PaymentRefunded"
1. Order Service → слушает → отмена → "OrderCancelled"
```

### Пример оркестрации

```
Оркестратор Saga:

   Step 1: Создать заказ
              ↓
   Step 2: Зарезервировать инвентарь
              ↓
   Step 3: Обработать платёж ──── СБОЙ
              ↓
   Компенсация: Освободить инвентарь
              ↓
   Компенсация: Отменить заказ
```

### Ключевые соображения

- **Идемпотентность**: Шаги должны быть безопасно повторяемы
- **Eventual consistency**: Не сразу согласовано
- **Логика компенсации**: Должна обрабатывать частичные состояния
- **Обработка таймаутов**: Зависшие саги требуют разрешения

---

## Follow-ups

- How do you handle saga timeouts?
- What is the difference between saga and 2PC?
- How do you debug failed sagas?
