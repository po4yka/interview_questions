---
id: sysdes-020
title: Database Replication Strategies
aliases:
- Replication
- Master-Slave
- Primary-Replica
topic: system-design
subtopics:
- databases
- distributed-systems
- availability
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-database-sharding-partitioning--system-design--hard
- q-consistency-models--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- databases
- difficulty/medium
- distributed-systems
- system-design
anki_cards:
- slug: sysdes-020-0-en
  language: en
  anki_id: 1769158891441
  synced_at: '2026-01-23T13:49:17.849578'
- slug: sysdes-020-0-ru
  language: ru
  anki_id: 1769158891466
  synced_at: '2026-01-23T13:49:17.850804'
---
# Question (EN)
> What are the main database replication strategies? Explain synchronous vs asynchronous replication and their trade-offs.

# Vopros (RU)
> Какие основные стратегии репликации баз данных существуют? Объясните синхронную и асинхронную репликацию и их компромиссы.

---

## Answer (EN)

**Database replication** creates copies of data across multiple servers for availability, fault tolerance, and read scaling.

### Replication Topologies

**1. Single-Leader (Master-Slave / Primary-Replica)**
```
         Writes
            ↓
       [Primary]
        /   |   \
       ↓    ↓    ↓
   [Replica][Replica][Replica]
       ↑       ↑       ↑
         Reads
```
- All writes go to primary
- Replicas serve read queries
- Most common pattern

**2. Multi-Leader (Master-Master)**
```
    [Leader A] ←──→ [Leader B]
        ↓               ↓
   [Replica]       [Replica]
```
- Multiple nodes accept writes
- Used for multi-datacenter setups
- Requires conflict resolution

**3. Leaderless (Peer-to-Peer)**
```
   [Node A] ←──→ [Node B]
       ↑  \    /   ↑
       ↓   \  /    ↓
          [Node C]
```
- Any node accepts reads/writes
- Uses quorum for consistency
- Examples: Cassandra, DynamoDB

### Synchronous vs Asynchronous Replication

**Synchronous Replication**
```
Client → Primary → Replica (wait for ACK) → Client ACK

Timeline:
Write → Primary commits → Replica commits → Success returned
```
- Strong consistency
- Higher latency
- Lower availability (replica failure blocks writes)
- Data loss: zero

**Asynchronous Replication**
```
Client → Primary → Client ACK
              ↓
         (later) Replica

Timeline:
Write → Primary commits → Success returned → Replica updated later
```
- Eventual consistency
- Lower latency
- Higher availability
- Data loss: possible (replication lag)

**Semi-Synchronous**
```
Write → Primary → At least 1 replica ACK → Success

Combines: Some durability guarantee with better latency
```

### Comparison Table

| Aspect | Sync | Async | Semi-Sync |
|--------|------|-------|-----------|
| Latency | High | Low | Medium |
| Consistency | Strong | Eventual | Bounded |
| Availability | Lower | Higher | Medium |
| Data loss risk | None | Yes (lag) | Minimal |

### Replication Lag Challenges

**Problem:** Reads from replicas may return stale data.

**Solutions:**
1. **Read-your-writes:** Route reads to primary after writes
2. **Monotonic reads:** Stick user to same replica
3. **Bounded staleness:** Guarantee max lag time

```python
def get_user(user_id, just_wrote=False):
    if just_wrote:
        return primary.get(user_id)  # Read from primary
    return replica.get(user_id)      # Read from replica
```

### Failover Strategies

**Automatic Failover:**
1. Detect primary failure (heartbeat timeout)
2. Elect new primary (most up-to-date replica)
3. Reconfigure clients to new primary
4. Demote old primary when recovered

**Challenges:**
- Split-brain (two primaries)
- Data loss during async failover
- Client connection handling

---

## Otvet (RU)

**Репликация базы данных** создает копии данных на нескольких серверах для доступности, отказоустойчивости и масштабирования чтения.

### Топологии репликации

**1. Single-Leader (Master-Slave / Primary-Replica)**
```
         Записи
            ↓
       [Primary]
        /   |   \
       ↓    ↓    ↓
   [Replica][Replica][Replica]
       ↑       ↑       ↑
         Чтение
```
- Все записи идут на primary
- Реплики обслуживают запросы на чтение
- Самый распространенный паттерн

**2. Multi-Leader (Master-Master)**
```
    [Leader A] ←──→ [Leader B]
        ↓               ↓
   [Replica]       [Replica]
```
- Несколько узлов принимают записи
- Используется для мульти-датацентров
- Требует разрешения конфликтов

**3. Leaderless (Peer-to-Peer)**
```
   [Node A] ←──→ [Node B]
       ↑  \    /   ↑
       ↓   \  /    ↓
          [Node C]
```
- Любой узел принимает чтение/запись
- Использует кворум для согласованности
- Примеры: Cassandra, DynamoDB

### Синхронная vs Асинхронная репликация

**Синхронная репликация**
```
Клиент → Primary → Replica (ждем ACK) → ACK клиенту

Временная шкала:
Запись → Primary коммит → Replica коммит → Успех возвращен
```
- Строгая согласованность
- Выше задержка
- Ниже доступность (сбой реплики блокирует записи)
- Потеря данных: ноль

**Асинхронная репликация**
```
Клиент → Primary → ACK клиенту
              ↓
         (позже) Replica

Временная шкала:
Запись → Primary коммит → Успех возвращен → Replica обновляется позже
```
- Eventual consistency
- Ниже задержка
- Выше доступность
- Потеря данных: возможна (lag репликации)

**Полусинхронная**
```
Запись → Primary → Минимум 1 replica ACK → Успех

Комбинирует: Некоторую гарантию durability с лучшей задержкой
```

### Сравнительная таблица

| Аспект | Синхр | Асинхр | Полусинхр |
|--------|-------|--------|-----------|
| Задержка | Высокая | Низкая | Средняя |
| Согласованность | Строгая | Eventual | Ограниченная |
| Доступность | Ниже | Выше | Средняя |
| Риск потери данных | Нет | Да (lag) | Минимальный |

### Проблемы Replication Lag

**Проблема:** Чтение с реплик может вернуть устаревшие данные.

**Решения:**
1. **Read-your-writes:** Направлять чтения на primary после записей
2. **Monotonic reads:** Привязать пользователя к одной реплике
3. **Bounded staleness:** Гарантировать максимальное время lag

```python
def get_user(user_id, just_wrote=False):
    if just_wrote:
        return primary.get(user_id)  # Чтение с primary
    return replica.get(user_id)      # Чтение с реплики
```

### Стратегии Failover

**Автоматический Failover:**
1. Обнаружить сбой primary (таймаут heartbeat)
2. Выбрать новый primary (самая актуальная реплика)
3. Перенастроить клиентов на новый primary
4. Понизить старый primary при восстановлении

**Сложности:**
- Split-brain (два primary)
- Потеря данных при async failover
- Обработка соединений клиентов

---

## Follow-ups

- How does MySQL handle replication differently from PostgreSQL?
- What is GTID and how does it help with replication?
- How do you monitor replication lag?

## Related Questions

### Prerequisites (Easier)
- [[q-acid-properties--system-design--medium]] - ACID properties
- [[q-consistency-models--system-design--hard]] - Consistency models

### Related (Same Level)
- [[q-master-slave-master-master--system-design--medium]] - Master patterns
- [[q-failover-strategies--system-design--medium]] - Failover

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Sharding
