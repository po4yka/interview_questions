---
id: sysdes-065
title: Event Sourcing
aliases:
- Event Sourcing
- Event Store
- Event Log
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
- q-cqrs-pattern--system-design--hard
- q-saga-pattern--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- advanced
- difficulty/hard
- patterns
- system-design
anki_cards:
- slug: sysdes-065-0-en
  language: en
  anki_id: 1769160580074
  synced_at: '2026-01-23T13:29:45.861195'
- slug: sysdes-065-0-ru
  language: ru
  anki_id: 1769160580098
  synced_at: '2026-01-23T13:29:45.864482'
---
# Question (EN)
> What is event sourcing? How does it differ from traditional CRUD, and when would you use it?

# Vopros (RU)
> Что такое Event Sourcing? Чем он отличается от традиционного CRUD и когда его использовать?

---

## Answer (EN)

**Event sourcing** stores state as a sequence of events rather than current values. State is reconstructed by replaying events.

### CRUD vs Event Sourcing

```
CRUD (Traditional):
┌────────────────────────┐
│ Account: #123          │
│ Balance: $500          │  ← Only current state
│ Updated: 2024-01-15    │
└────────────────────────┘

Event Sourcing:
┌─────────────────────────────────────┐
│ Event 1: AccountCreated(#123)       │
│ Event 2: MoneyDeposited($1000)      │
│ Event 3: MoneyWithdrawn($300)       │  ← Full history
│ Event 4: MoneyWithdrawn($200)       │
└─────────────────────────────────────┘
Current state: $1000 - $300 - $200 = $500
```

### Event Structure

```json
{
  "eventId": "uuid-123",
  "eventType": "MoneyWithdrawn",
  "aggregateId": "account-456",
  "aggregateType": "BankAccount",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": 4,
  "payload": {
    "amount": 200,
    "currency": "USD",
    "reason": "ATM withdrawal"
  },
  "metadata": {
    "userId": "user-789",
    "correlationId": "txn-abc"
  }
}
```

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Command Side                      │
│  Command → Validate → Generate Events → Store Events│
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │  Event Store   │
              │ (append-only)  │
              └────────┬───────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                    Query Side                        │
│  Events → Projections → Read Models → Queries       │
└─────────────────────────────────────────────────────┘
```

### Benefits

| Benefit | Description |
|---------|-------------|
| Audit trail | Complete history of all changes |
| Temporal queries | State at any point in time |
| Event replay | Fix bugs, rebuild projections |
| Debugging | See exactly what happened |
| Integration | Events as integration points |

### Challenges

| Challenge | Solution |
|-----------|----------|
| Event schema evolution | Upcasters, versioning |
| Performance (many events) | Snapshots |
| Storage growth | Archival, compaction |
| Eventual consistency | CQRS + projections |
| Complexity | Start simple, add when needed |

### Snapshots

```
Instead of replaying 10,000 events:

Events: [1, 2, 3, ..., 9997, 9998, 9999, 10000]
                    ↓
Snapshot at event 9990 + events [9991...10000]

Snapshot: {
  aggregateId: "account-456",
  version: 9990,
  state: { balance: 5000 }
}
```

### When to Use

**Good fit:**
- Financial systems (audit trail required)
- Collaborative editing (need history)
- Complex domain with many state changes
- Microservices integration via events

**Poor fit:**
- Simple CRUD applications
- High-frequency updates (performance)
- No need for history
- Small teams (complexity overhead)

---

## Otvet (RU)

**Event sourcing** хранит состояние как последовательность событий вместо текущих значений. Состояние восстанавливается воспроизведением событий.

### CRUD vs Event Sourcing

```
CRUD (Традиционный):
┌────────────────────────┐
│ Account: #123          │
│ Balance: $500          │  ← Только текущее состояние
└────────────────────────┘

Event Sourcing:
┌─────────────────────────────────────┐
│ Event 1: AccountCreated(#123)       │
│ Event 2: MoneyDeposited($1000)      │
│ Event 3: MoneyWithdrawn($300)       │  ← Полная история
│ Event 4: MoneyWithdrawn($200)       │
└─────────────────────────────────────┘
Текущее состояние: $1000 - $300 - $200 = $500
```

### Преимущества

| Преимущество | Описание |
|--------------|----------|
| Audit trail | Полная история всех изменений |
| Временные запросы | Состояние в любой момент времени |
| Replay событий | Исправление багов, пересборка проекций |
| Отладка | Видно точно что произошло |
| Интеграция | События как точки интеграции |

### Проблемы

| Проблема | Решение |
|----------|---------|
| Эволюция схемы событий | Upcasters, версионирование |
| Производительность (много событий) | Snapshots |
| Рост хранилища | Архивация, compaction |
| Eventual consistency | CQRS + проекции |
| Сложность | Начинать просто, добавлять по необходимости |

### Snapshots

```
Вместо воспроизведения 10,000 событий:

События: [1, 2, 3, ..., 9997, 9998, 9999, 10000]
                    ↓
Snapshot на событии 9990 + события [9991...10000]

Snapshot: {
  aggregateId: "account-456",
  version: 9990,
  state: { balance: 5000 }
}
```

### Когда использовать

**Хорошо подходит:**
- Финансовые системы (требуется audit trail)
- Совместное редактирование (нужна история)
- Сложный домен с частыми изменениями состояния
- Интеграция микросервисов через события

**Плохо подходит:**
- Простые CRUD приложения
- Высокочастотные обновления
- Не нужна история
- Маленькие команды (overhead сложности)

---

## Follow-ups

- How do you handle event schema versioning?
- What is the relationship between event sourcing and CQRS?
- How do you implement event replay for bug fixes?
