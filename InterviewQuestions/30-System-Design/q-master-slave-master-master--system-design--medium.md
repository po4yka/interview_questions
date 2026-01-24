---
id: sysdes-021
title: Master-Slave vs Master-Master Replication
aliases:
- Master-Slave
- Master-Master
- Primary-Replica
topic: system-design
subtopics:
- databases
- distributed-systems
- replication
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-replication-strategies--system-design--medium
- q-database-sharding-partitioning--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- databases
- difficulty/medium
- replication
- system-design
anki_cards:
- slug: sysdes-021-0-en
  language: en
  anki_id: 1769158890991
  synced_at: '2026-01-23T13:49:17.802166'
- slug: sysdes-021-0-ru
  language: ru
  anki_id: 1769158891016
  synced_at: '2026-01-23T13:49:17.804096'
---
# Question (EN)
> What is the difference between Master-Slave and Master-Master replication? When would you use each?

# Vopros (RU)
> В чем разница между Master-Slave и Master-Master репликацией? Когда использовать каждую?

---

## Answer (EN)

Both are database replication patterns, but they differ in how writes are handled.

### Master-Slave (Primary-Replica)

**Architecture:**
```
       Writes only
           ↓
       [Master]
        /     \
       ↓       ↓
   [Slave 1] [Slave 2]
       ↑       ↑
      Reads
```

**Characteristics:**
- Single master accepts all writes
- Slaves replicate data from master
- Slaves serve read queries
- Simple conflict resolution (no conflicts)

**Pros:**
- Simple to implement and understand
- No write conflicts
- Good for read-heavy workloads
- Easy consistency model

**Cons:**
- Master is single point of failure
- Write scaling limited to one node
- Failover requires promotion logic

### Master-Master (Multi-Leader)

**Architecture:**
```
    Writes ↓           ↓ Writes
       [Master 1] ←──→ [Master 2]
           ↓               ↓
       [Slave]         [Slave]
```

**Characteristics:**
- Multiple masters accept writes
- Masters replicate to each other
- Requires conflict resolution
- Often used for multi-datacenter

**Pros:**
- No single point of failure for writes
- Write scaling across masters
- Better for geographically distributed systems
- Lower write latency (local master)

**Cons:**
- Complex conflict resolution
- Risk of data inconsistency
- Harder to implement correctly
- Potential for split-brain

### Conflict Resolution Strategies

**1. Last Write Wins (LWW)**
```
Master A: UPDATE user SET name='Alice' WHERE id=1  (t=100)
Master B: UPDATE user SET name='Bob' WHERE id=1    (t=101)

Result: name='Bob' (later timestamp wins)
Problem: Alice's update lost silently
```

**2. Application-Level Resolution**
```python
def resolve_conflict(value_a, value_b, metadata):
    # Custom logic based on business rules
    if metadata['priority_a'] > metadata['priority_b']:
        return value_a
    return value_b
```

**3. Merge/CRDT**
```
Master A: Add item 'X' to cart
Master B: Add item 'Y' to cart

Result: Cart contains both X and Y (merge)
```

### Comparison Table

| Aspect | Master-Slave | Master-Master |
|--------|--------------|---------------|
| Write availability | Single point | Multiple points |
| Conflict handling | None needed | Complex |
| Consistency | Simpler | More complex |
| Use case | Read scaling | Geo-distribution |
| Failover | Requires promotion | Automatic |
| Implementation | Simpler | Complex |

### When to Use Each

**Master-Slave:**
- Read-heavy workloads (90%+ reads)
- Single datacenter
- Simpler consistency requirements
- Analytics/reporting replicas

**Master-Master:**
- Multi-datacenter deployments
- Need high write availability
- Can handle conflict resolution
- Geographic user distribution

### Real-World Examples

| Database | Master-Slave | Master-Master |
|----------|--------------|---------------|
| MySQL | Yes (native) | Yes (Galera, Group Replication) |
| PostgreSQL | Yes (streaming) | Yes (BDR, Citus) |
| MongoDB | Yes (replica sets) | No (use sharding) |
| CockroachDB | N/A | Built-in (Raft) |

---

## Otvet (RU)

Оба паттерна репликации баз данных, но они отличаются в обработке записей.

### Master-Slave (Primary-Replica)

**Архитектура:**
```
       Только записи
           ↓
       [Master]
        /     \
       ↓       ↓
   [Slave 1] [Slave 2]
       ↑       ↑
      Чтение
```

**Характеристики:**
- Один master принимает все записи
- Slave'ы реплицируют данные с master
- Slave'ы обслуживают запросы на чтение
- Простое разрешение конфликтов (конфликтов нет)

**Плюсы:**
- Просто реализовать и понять
- Нет конфликтов записи
- Хорошо для read-heavy нагрузок
- Простая модель согласованности

**Минусы:**
- Master - единая точка отказа
- Масштабирование записи ограничено одним узлом
- Failover требует логики промоушена

### Master-Master (Multi-Leader)

**Архитектура:**
```
    Записи ↓           ↓ Записи
       [Master 1] ←──→ [Master 2]
           ↓               ↓
       [Slave]         [Slave]
```

**Характеристики:**
- Несколько master'ов принимают записи
- Master'ы реплицируют друг другу
- Требует разрешения конфликтов
- Часто используется для мульти-датацентров

**Плюсы:**
- Нет единой точки отказа для записей
- Масштабирование записи по master'ам
- Лучше для географически распределенных систем
- Ниже задержка записи (локальный master)

**Минусы:**
- Сложное разрешение конфликтов
- Риск несогласованности данных
- Сложнее правильно реализовать
- Потенциал для split-brain

### Стратегии разрешения конфликтов

**1. Last Write Wins (LWW)**
```
Master A: UPDATE user SET name='Alice' WHERE id=1  (t=100)
Master B: UPDATE user SET name='Bob' WHERE id=1    (t=101)

Результат: name='Bob' (выигрывает поздний timestamp)
Проблема: Обновление Alice потеряно молча
```

**2. Разрешение на уровне приложения**
```python
def resolve_conflict(value_a, value_b, metadata):
    # Кастомная логика на основе бизнес-правил
    if metadata['priority_a'] > metadata['priority_b']:
        return value_a
    return value_b
```

**3. Merge/CRDT**
```
Master A: Добавить товар 'X' в корзину
Master B: Добавить товар 'Y' в корзину

Результат: Корзина содержит X и Y (merge)
```

### Сравнительная таблица

| Аспект | Master-Slave | Master-Master |
|--------|--------------|---------------|
| Доступность записи | Одна точка | Несколько точек |
| Обработка конфликтов | Не нужна | Сложная |
| Согласованность | Проще | Сложнее |
| Применение | Масштабирование чтения | Гео-распределение |
| Failover | Требует промоушен | Автоматический |
| Реализация | Проще | Сложная |

### Когда использовать

**Master-Slave:**
- Read-heavy нагрузки (90%+ чтения)
- Один датацентр
- Простые требования к согласованности
- Реплики для аналитики/отчетов

**Master-Master:**
- Мульти-датацентр развертывания
- Нужна высокая доступность записи
- Можете обработать разрешение конфликтов
- Географическое распределение пользователей

### Примеры из практики

| База данных | Master-Slave | Master-Master |
|-------------|--------------|---------------|
| MySQL | Да (нативно) | Да (Galera, Group Replication) |
| PostgreSQL | Да (streaming) | Да (BDR, Citus) |
| MongoDB | Да (replica sets) | Нет (используйте sharding) |
| CockroachDB | Н/Д | Встроено (Raft) |

---

## Follow-ups

- How do you handle auto-increment IDs in master-master setup?
- What is split-brain and how do you prevent it?
- How does MySQL Group Replication differ from traditional master-master?

## Related Questions

### Prerequisites (Easier)
- [[q-replication-strategies--system-design--medium]] - Replication basics

### Related (Same Level)
- [[q-consistency-models--system-design--hard]] - Consistency
- [[q-failover-strategies--system-design--medium]] - Failover

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Sharding
