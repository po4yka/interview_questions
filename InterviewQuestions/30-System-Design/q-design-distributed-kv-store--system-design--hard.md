---
id: q-design-distributed-kv-store
title: Design Distributed Key-Value Store
aliases:
- Design Distributed Key-Value Store
- Design DynamoDB
- Design Redis Cluster
- Design Cassandra
topic: system-design
subtopics:
- distributed-systems
- storage
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
- q-consistent-hashing--system-design--hard
- q-cap-theorem-distributed-systems--system-design--hard
- q-consensus-algorithms--system-design--hard
- q-vector-clocks-lamport--system-design--hard
- q-design-distributed-cache--system-design--hard
created: 2025-01-26
updated: 2025-01-26
tags:
- distributed-systems
- difficulty/hard
- storage
- system-design
anki_cards:
- slug: q-design-distributed-kv-store-0-en
  anki_id: null
  synced_at: null
- slug: q-design-distributed-kv-store-0-ru
  anki_id: null
  synced_at: null
---
# Question (EN)
> How would you design a distributed key-value store like DynamoDB or Redis Cluster?

# Vopros (RU)
> Как бы вы спроектировали распределённое хранилище ключ-значение, подобное DynamoDB или Redis Cluster?

---

## Answer (EN)

### Requirements

**Functional**: GET/PUT/DELETE operations, range queries (optional), TTL support
**Non-functional**: High availability, partition tolerance, low latency (<10ms), horizontal scaling, tunable consistency

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Coordinator / Router                        │
│           (Request routing, quorum coordination)             │
└─────────────────────────┬───────────────────────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
┌───▼───┐             ┌───▼───┐             ┌───▼───┐
│Node A │←────────────→│Node B │←────────────→│Node C │
│Shard 1│  Gossip +    │Shard 2│  Gossip +    │Shard 3│
│       │  Replication │       │  Replication │       │
└───────┘             └───────┘             └───────┘
```

### Data Partitioning: Consistent Hashing

```
Hash Ring (0 to 2^128-1):

           Node A
              ↑
       ●──────●──────● ← Node B
       │             │
    key1 →     ●     │
       │    (key2)   │
       ●──────●──────●
              ↓
           Node C

key → hash(key) → find first node clockwise

Virtual nodes for even distribution:
- Node A → A-1, A-2, A-3 ... A-100
- Each physical node = 100-256 virtual nodes
```

### Replication Strategies

**Leader-Follower (Redis Cluster)**
```
Write: Client → Leader → Followers (async)
Read:  Client → Leader (or Follower for stale reads)

Pros: Simple, strong consistency possible
Cons: Leader bottleneck, failover complexity
```

**Leaderless (DynamoDB, Cassandra)**
```
Write: Client → N replicas simultaneously
Read:  Client → R replicas, take latest version

Pros: No single point of failure, better availability
Cons: Conflict resolution needed, eventual consistency
```

### Consistency Models

| Model | Description | Use Case |
|-------|-------------|----------|
| Strong | All replicas agree before response | Financial data |
| Eventual | Replicas converge over time | Social media, analytics |
| Tunable | Configure per-request (R + W > N) | Mixed workloads |

**Quorum Formula:**
```
N = total replicas (typically 3)
W = write quorum (replicas that must acknowledge write)
R = read quorum (replicas to read from)

Strong consistency: R + W > N
Example: N=3, W=2, R=2 → 2+2=4 > 3 ✓
```

### Conflict Resolution

**Problem:** Concurrent writes to same key on different nodes.

**Vector Clocks:**
```
Write A on Node 1: {Node1: 1}
Write B on Node 2: {Node2: 1}
Concurrent! Both versions stored.

Client reads both, resolves conflict.
Merged version: {Node1: 1, Node2: 1, Node3: 1}
```

**Last-Write-Wins (LWW):**
```
Each write has timestamp.
Latest timestamp wins.

Pros: Simple, no client conflict resolution
Cons: Data loss if clocks skew
```

**CRDTs (Conflict-free Replicated Data Types):**
```
Special data structures that auto-merge:
- G-Counter: grow-only counter
- OR-Set: observed-remove set
- LWW-Register: last-write-wins register

Pros: Automatic resolution, no conflicts
Cons: Limited operations, space overhead
```

### Failure Detection

**Gossip Protocol:**
```
Every T seconds:
1. Node A picks random node B
2. A sends its membership list to B
3. B merges lists, sends back
4. Both update failure suspicions

Failure detection:
- No heartbeat for X seconds → suspected
- Multiple nodes suspect → confirmed dead
```

**Phi Accrual Failure Detector:**
```
Instead of binary alive/dead:
- Calculate probability of failure (phi)
- Phi > threshold → declare dead
- Adapts to network conditions
```

### Read/Write Paths

**Write Path:**
```
1. Client sends PUT(key, value)
2. Coordinator hashes key → finds N replicas
3. Forward to W replicas
4. Wait for W acknowledgments
5. Return success to client

Durability options:
- Memory only (fastest, volatile)
- Write-ahead log (durable, slower)
- Memtable + SSTable (LSM-tree)
```

**Read Path:**
```
1. Client sends GET(key)
2. Coordinator hashes key → finds N replicas
3. Query R replicas in parallel
4. Return value with highest version
5. Read repair: update stale replicas
```

### Storage Engine: LSM-Tree

```
Write path:
1. Write to WAL (durability)
2. Write to Memtable (sorted in-memory)
3. When full, flush to SSTable (sorted on disk)
4. Background compaction merges SSTables

Read path:
1. Check Memtable
2. Check Bloom filters for each SSTable
3. Search matching SSTables

┌─────────────┐
│  Memtable   │ (in-memory, sorted)
└──────┬──────┘
       ↓ flush
┌─────────────┐
│  SSTable 0  │ (immutable, sorted)
├─────────────┤
│  SSTable 1  │
├─────────────┤
│  SSTable 2  │ → Compaction → merged SSTable
└─────────────┘
```

### Cluster Membership: Gossip

```
Membership state per node:
{
  "node-1": {status: "alive", heartbeat: 1000},
  "node-2": {status: "alive", heartbeat: 998},
  "node-3": {status: "suspect", heartbeat: 950}
}

Seed nodes: initial contact points for joining
```

### Comparison: DynamoDB vs Redis Cluster vs Cassandra

| Feature | DynamoDB | Redis Cluster | Cassandra |
|---------|----------|---------------|-----------|
| Replication | Leaderless | Leader-follower | Leaderless |
| Consistency | Tunable | Eventual | Tunable |
| Conflict | LWW | Last-write | Vector clocks |
| Storage | Proprietary | In-memory + RDB/AOF | LSM-tree |
| Partitioning | Consistent hash | Hash slots (16384) | Consistent hash |
| Use case | Serverless, AWS | Cache, sessions | Time-series, IoT |

### Key Design Decisions Summary

| Decision | Options | Trade-off |
|----------|---------|-----------|
| Replication | Leader vs Leaderless | Consistency vs Availability |
| Consistency | Strong vs Eventual | Latency vs Correctness |
| Partitioning | Hash vs Range | Even load vs Range queries |
| Conflict | Vector clock vs LWW | Complexity vs Data loss |
| Storage | In-memory vs LSM | Speed vs Capacity |

---

## Otvet (RU)

### Требования

**Функциональные**: GET/PUT/DELETE операции, range-запросы (опционально), поддержка TTL
**Нефункциональные**: Высокая доступность, устойчивость к разделению, низкая задержка (<10ms), горизонтальное масштабирование, настраиваемая согласованность

### Партиционирование данных: Консистентное хеширование

```
Хеш-кольцо (от 0 до 2^128-1):

key → hash(key) → найти первый узел по часовой стрелке

Виртуальные узлы для равномерного распределения:
- Node A → A-1, A-2, A-3 ... A-100
- Каждый физический узел = 100-256 виртуальных узлов
```

### Стратегии репликации

**Лидер-последователь (Redis Cluster)**
```
Запись: Client → Leader → Followers (async)
Чтение: Client → Leader (или Follower для устаревших данных)

Плюсы: Просто, возможна строгая согласованность
Минусы: Лидер - узкое место, сложность failover
```

**Без лидера (DynamoDB, Cassandra)**
```
Запись: Client → N реплик одновременно
Чтение: Client → R реплик, берём последнюю версию

Плюсы: Нет единой точки отказа, лучшая доступность
Минусы: Нужно разрешение конфликтов, eventual consistency
```

### Модели согласованности

| Модель | Описание | Применение |
|--------|----------|------------|
| Строгая | Все реплики согласны до ответа | Финансовые данные |
| Eventual | Реплики сходятся со временем | Соцсети, аналитика |
| Настраиваемая | Конфигурируется per-request (R + W > N) | Смешанные нагрузки |

**Формула кворума:**
```
N = всего реплик (обычно 3)
W = кворум записи (реплики, которые должны подтвердить запись)
R = кворум чтения (реплики для чтения)

Строгая согласованность: R + W > N
Пример: N=3, W=2, R=2 → 2+2=4 > 3 ✓
```

### Разрешение конфликтов

**Проблема:** Одновременные записи одного ключа на разных узлах.

**Векторные часы:**
```
Запись A на Node 1: {Node1: 1}
Запись B на Node 2: {Node2: 1}
Конкурентные! Обе версии сохраняются.

Клиент читает обе, разрешает конфликт.
```

**Last-Write-Wins (LWW):**
```
Каждая запись имеет timestamp.
Побеждает последний timestamp.

Плюсы: Просто, нет разрешения конфликтов клиентом
Минусы: Потеря данных при расхождении часов
```

**CRDTs (Conflict-free Replicated Data Types):**
```
Специальные структуры данных с авто-слиянием:
- G-Counter: только растущий счётчик
- OR-Set: observed-remove set
- LWW-Register: last-write-wins регистр
```

### Обнаружение отказов: Gossip Protocol

```
Каждые T секунд:
1. Узел A выбирает случайный узел B
2. A отправляет свой список членов в B
3. B объединяет списки, отправляет обратно
4. Оба обновляют подозрения об отказах

Обнаружение отказа:
- Нет heartbeat X секунд → подозреваемый
- Несколько узлов подозревают → подтверждено мёртв
```

### Путь записи и чтения

**Путь записи:**
```
1. Клиент отправляет PUT(key, value)
2. Координатор хеширует key → находит N реплик
3. Пересылает на W реплик
4. Ждёт W подтверждений
5. Возвращает успех клиенту
```

**Путь чтения:**
```
1. Клиент отправляет GET(key)
2. Координатор хеширует key → находит N реплик
3. Запрашивает R реплик параллельно
4. Возвращает значение с наивысшей версией
5. Read repair: обновляет устаревшие реплики
```

### Storage Engine: LSM-Tree

```
Путь записи:
1. Запись в WAL (durability)
2. Запись в Memtable (отсортировано в памяти)
3. При заполнении, flush в SSTable (отсортировано на диске)
4. Фоновая компактификация объединяет SSTable

Путь чтения:
1. Проверить Memtable
2. Проверить Bloom filters для каждой SSTable
3. Искать в подходящих SSTable
```

### Сравнение: DynamoDB vs Redis Cluster vs Cassandra

| Свойство | DynamoDB | Redis Cluster | Cassandra |
|----------|----------|---------------|-----------|
| Репликация | Без лидера | Лидер-последователь | Без лидера |
| Согласованность | Настраиваемая | Eventual | Настраиваемая |
| Конфликты | LWW | Last-write | Векторные часы |
| Хранение | Proprietary | In-memory + RDB/AOF | LSM-tree |
| Партиционирование | Consistent hash | Hash slots (16384) | Consistent hash |
| Применение | Serverless, AWS | Кеш, сессии | Time-series, IoT |

### Ключевые решения дизайна

| Решение | Опции | Компромисс |
|---------|-------|------------|
| Репликация | Лидер vs Без лидера | Согласованность vs Доступность |
| Согласованность | Строгая vs Eventual | Задержка vs Корректность |
| Партиционирование | Hash vs Range | Равномерная нагрузка vs Range-запросы |
| Конфликты | Векторные часы vs LWW | Сложность vs Потеря данных |
| Хранение | In-memory vs LSM | Скорость vs Объём |

---

## Follow-ups

- How do you handle hot partitions (celebrity problem)?
- What is the difference between DynamoDB's partition key and sort key?
- How does Cassandra's gossip protocol work in detail?
- How would you implement secondary indexes in a distributed KV store?
- What is anti-entropy and how does it help with consistency?
