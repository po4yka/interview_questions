---
id: sysdes-070
title: Design Distributed Cache
aliases:
- Design Distributed Cache
- Design Memcached
- Design Redis Cluster
topic: system-design
subtopics:
- design-problems
- caching
- distributed-systems
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-caching-strategies--system-design--medium
- q-consistent-hashing--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- design-problems
- difficulty/hard
- caching
- system-design
anki_cards:
- slug: sysdes-070-0-en
  language: en
  anki_id: 1769160582327
  synced_at: '2026-01-23T13:49:17.747713'
- slug: sysdes-070-0-ru
  language: ru
  anki_id: 1769160582350
  synced_at: '2026-01-23T13:49:17.749023'
---
# Question (EN)
> Design a distributed cache system like Memcached or Redis.

# Vopros (RU)
> Спроектируйте систему распределённого кеша типа Memcached или Redis.

---

## Answer (EN)

### Requirements

**Functional**: GET/SET/DELETE operations, TTL support, eviction policies
**Non-functional**: Sub-millisecond latency, high throughput, horizontal scaling, fault tolerance

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Servers                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Cache Client                             │
│      (Consistent hashing, Connection pooling)              │
└─────────────────────────┬───────────────────────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
┌───▼───┐             ┌───▼───┐             ┌───▼───┐
│Cache 1│             │Cache 2│             │Cache N│
│ Shard │             │ Shard │             │ Shard │
└───────┘             └───────┘             └───────┘
```

### Data Partitioning

```
Consistent hashing for key distribution:

Hash Ring:
         0
        /|\
       / | \
      /  |  \
   Node A   Node B
      \  |  /
       \ | /
        \|/
       Node C

key1 → hash(key1) → falls between A and B → Node B
key2 → hash(key2) → falls between B and C → Node C

Benefits:
- Add/remove nodes: only K/N keys move
- Virtual nodes for even distribution
```

### Cache Node Architecture

```
┌─────────────────────────────────────────┐
│              Cache Node                  │
│  ┌─────────────────────────────────┐    │
│  │         Hash Table              │    │
│  │    (key → value + metadata)     │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │       Eviction Manager          │    │
│  │    (LRU list, TTL heap)         │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │       Memory Allocator          │    │
│  │    (Slab allocation)            │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Eviction Policies

| Policy | Description | Use Case |
|--------|-------------|----------|
| LRU | Evict least recently used | General purpose |
| LFU | Evict least frequently used | Long-term popularity |
| TTL | Evict expired items | Session data |
| Random | Random eviction | Simple, low overhead |
| FIFO | Evict oldest | Not common |

### LRU Implementation

```
Doubly linked list + Hash map:

┌──────────────────────────────────────────┐
│ Hash Map: key → node pointer             │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ Doubly Linked List (most → least recent) │
│                                          │
│ HEAD ↔ [A] ↔ [B] ↔ [C] ↔ [D] ↔ TAIL     │
│        most                  least       │
│       recent                recent       │
└──────────────────────────────────────────┘

GET key:
1. Lookup in hash map O(1)
2. Move node to head O(1)

SET key:
1. Add to hash map O(1)
2. Add node at head O(1)
3. If full, evict tail O(1)
```

### Replication

```
Master-Replica model:

Write path:
Client → Master → Replicas (async)

Read path:
Client → Any node (master or replica)

Failover:
1. Replica detects master failure
2. Replica promotes to master
3. Clients redirect to new master
```

### Handling Hot Keys

```
Problem: One key gets 90% of traffic

Solutions:

1. Local cache layer
   App servers cache hot keys locally

2. Key replication
   Replicate hot key to multiple shards
   key → [shard1, shard2, shard3]

3. Read replicas
   Scale reads with more replicas
```

### Protocol Design

```
Simple text protocol:
SET key 0 3600 5\r\n
value\r\n

GET key\r\n
VALUE key 0 5\r\n
value\r\n
END\r\n

DELETE key\r\n
DELETED\r\n

Binary protocol:
[header][key][value]
- More efficient parsing
- Less bandwidth
```

### Key Design Decisions

| Decision | Options | Trade-off |
|----------|---------|-----------|
| Consistency | Strong vs Eventual | Latency vs Consistency |
| Persistence | None vs AOF/RDB | Speed vs Durability |
| Threading | Single vs Multi | Simplicity vs Throughput |
| Memory | Pre-allocated vs Dynamic | Predictable vs Flexible |

---

## Otvet (RU)

### Требования

**Функциональные**: GET/SET/DELETE операции, поддержка TTL, политики вытеснения
**Нефункциональные**: Sub-millisecond задержка, высокая пропускная способность, горизонтальное масштабирование

### Партиционирование данных

```
Consistent hashing для распределения ключей:

Преимущества:
- Добавление/удаление узлов: перемещается только K/N ключей
- Виртуальные узлы для равномерного распределения
```

### Политики вытеснения

| Политика | Описание | Применение |
|----------|----------|------------|
| LRU | Вытеснить наименее недавно использованный | Общего назначения |
| LFU | Вытеснить наименее часто используемый | Долгосрочная популярность |
| TTL | Вытеснить истёкшие | Данные сессий |
| Random | Случайное вытеснение | Просто, низкий overhead |

### Реализация LRU

```
Двусвязный список + Hash map:

GET key:
1. Lookup в hash map O(1)
2. Переместить node в head O(1)

SET key:
1. Добавить в hash map O(1)
2. Добавить node в head O(1)
3. Если полно, вытеснить tail O(1)
```

### Репликация

```
Модель Master-Replica:

Путь записи:
Client → Master → Replicas (async)

Путь чтения:
Client → Любой узел (master или replica)

Failover:
1. Replica обнаруживает сбой master
2. Replica продвигается в master
3. Клиенты перенаправляются на новый master
```

### Обработка горячих ключей

```
Проблема: Один ключ получает 90% трафика

Решения:

1. Локальный слой кеша
   App серверы кешируют hot keys локально

2. Репликация ключа
   Реплицировать hot key на несколько шардов

3. Read replicas
   Масштабировать чтения с большим количеством реплик
```

### Ключевые решения дизайна

| Решение | Опции | Компромисс |
|---------|-------|------------|
| Согласованность | Strong vs Eventual | Latency vs Consistency |
| Persistence | None vs AOF/RDB | Скорость vs Durability |
| Threading | Single vs Multi | Простота vs Throughput |

---

## Follow-ups

- How do you handle cache stampede (thundering herd)?
- What is the difference between Memcached and Redis architectures?
- How do you implement distributed locking with a cache?
