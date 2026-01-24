---
id: sysdes-071
title: Two-Phase Commit (2PC) Limitations
aliases:
- Two-Phase Commit
- 2PC
- Distributed Transactions
topic: system-design
subtopics:
- distributed-systems
- transactions
- consistency
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-saga-pattern--system-design--hard
- q-acid-properties--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- distributed-systems
- difficulty/hard
- transactions
- system-design
anki_cards:
- slug: sysdes-071-0-en
  language: en
  anki_id: 1769161757684
  synced_at: '2026-01-23T13:49:17.871858'
- slug: sysdes-071-0-ru
  language: ru
  anki_id: 1769161757705
  synced_at: '2026-01-23T13:49:17.872908'
---
# Question (EN)
> What is Two-Phase Commit (2PC)? What are its limitations and why is it often avoided in distributed systems?

# Vopros (RU)
> Что такое двухфазный коммит (2PC)? Каковы его ограничения и почему его часто избегают в распределённых системах?

---

## Answer (EN)

**Two-Phase Commit (2PC)** is a distributed algorithm that ensures all participants in a transaction either commit or abort together, achieving atomicity across multiple nodes.

### How 2PC Works

```
Phase 1: Prepare (Voting)
┌─────────────┐
│ Coordinator │
└──────┬──────┘
       │ PREPARE
       ▼
┌──────┴──────┐
│             │
▼             ▼
Participant A  Participant B
    │             │
    │ VOTE YES    │ VOTE YES
    └─────┬───────┘
          ▼
    Coordinator

Phase 2: Commit (Decision)
┌─────────────┐
│ Coordinator │
└──────┬──────┘
       │ COMMIT
       ▼
┌──────┴──────┐
│             │
▼             ▼
Participant A  Participant B
    │             │
    │ ACK         │ ACK
    └─────────────┘
```

### The Protocol

| Phase | Action | Failure Handling |
|-------|--------|------------------|
| Prepare | Coordinator asks all participants to prepare | Any NO vote -> abort all |
| Commit | If all vote YES, coordinator sends commit | Participants must commit |

### Limitations

```
1. Blocking Protocol
   - If coordinator fails after prepare, participants are BLOCKED
   - Cannot release locks until coordinator recovers
   - Can block indefinitely

2. Single Point of Failure
   - Coordinator crash = entire transaction stuck
   - Requires coordinator recovery mechanism

3. Latency
   - 2 round trips minimum
   - All participants must be available
   - Slowest participant determines speed

4. Availability vs Consistency
   - Cannot proceed if ANY participant is down
   - Sacrifices availability for consistency
```

### Failure Scenarios

```
Scenario 1: Coordinator fails after PREPARE
┌─────────────┐
│ Coordinator │ ← CRASH
└──────┬──────┘
       │ PREPARE sent
       ▼
Participant A (prepared, holding locks)
Participant B (prepared, holding locks)

Result: Both participants BLOCKED, holding locks
        Cannot decide to commit or abort alone

Scenario 2: Participant fails after voting YES
- Coordinator will timeout waiting for ACK
- Must retry until participant recovers
- Transaction cannot complete
```

### Why Avoided in Modern Systems

| Problem | Impact |
|---------|--------|
| Blocking | Reduced availability |
| Latency | Poor performance at scale |
| Recovery complexity | Operational burden |
| Network partitions | Cannot make progress |

### Alternatives

| Alternative | Tradeoff |
|-------------|----------|
| **Saga pattern** | Eventual consistency, compensating transactions |
| **3PC** | Non-blocking but more complex, still has issues |
| **TCC (Try-Confirm-Cancel)** | Application-level coordination |
| **Outbox pattern** | Reliable messaging without distributed tx |

### When 2PC is Still Used

- Within a single database (internal coordination)
- XA transactions in enterprise systems
- When strong consistency is mandatory and latency acceptable
- Small number of participants with reliable network

---

## Otvet (RU)

**Двухфазный коммит (2PC)** - распределённый алгоритм, обеспечивающий атомарность транзакции между несколькими узлами: все участники либо фиксируют, либо откатывают изменения вместе.

### Как работает 2PC

```
Фаза 1: Подготовка (Голосование)
┌─────────────┐
│ Координатор │
└──────┬──────┘
       │ PREPARE
       ▼
Участник A    Участник B
    │             │
    │ VOTE YES    │ VOTE YES
    └──────┬──────┘
           ▼
      Координатор

Фаза 2: Фиксация (Решение)
┌─────────────┐
│ Координатор │
└──────┬──────┘
       │ COMMIT
       ▼
Участник A    Участник B
    │             │
    │ ACK         │ ACK
    └─────────────┘
```

### Ограничения

```
1. Блокирующий протокол
   - Если координатор падает после prepare - участники ЗАБЛОКИРОВАНЫ
   - Не могут освободить блокировки до восстановления координатора

2. Единая точка отказа
   - Падение координатора = вся транзакция зависла

3. Задержка
   - Минимум 2 round trip
   - Все участники должны быть доступны
   - Скорость определяется самым медленным

4. Доступность vs Согласованность
   - Невозможно продолжить, если ЛЮБОЙ участник недоступен
```

### Почему избегают в современных системах

| Проблема | Последствие |
|----------|-------------|
| Блокировка | Снижение доступности |
| Задержка | Плохая производительность |
| Сложность восстановления | Операционная нагрузка |
| Сетевые разделения | Невозможность прогресса |

### Альтернативы

| Альтернатива | Компромисс |
|--------------|------------|
| **Saga pattern** | Eventual consistency, компенсирующие транзакции |
| **3PC** | Non-blocking, но сложнее |
| **TCC** | Координация на уровне приложения |
| **Outbox pattern** | Надёжная доставка без распределённых транзакций |

### Когда 2PC всё ещё используют

- Внутри одной базы данных
- XA транзакции в enterprise системах
- Когда строгая согласованность обязательна
- Малое число участников с надёжной сетью

---

## Follow-ups

- How does 3PC improve upon 2PC?
- What is the Saga pattern and how does it handle failures?
- How do databases implement 2PC internally?
