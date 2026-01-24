---
id: sysdes-035
title: Quorum and Read/Write Quorum
aliases:
- Quorum
- Read Write Quorum
- W+R>N
topic: system-design
subtopics:
- distributed-systems
- consistency
- replication
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-consistency-models--system-design--hard
- q-replication-strategies--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- distributed-systems
- difficulty/hard
- consistency
- system-design
anki_cards:
- slug: sysdes-035-0-en
  language: en
  anki_id: 1769159521797
  synced_at: '2026-01-23T13:49:17.826942'
- slug: sysdes-035-0-ru
  language: ru
  anki_id: 1769159521819
  synced_at: '2026-01-23T13:49:17.828044'
---
# Question (EN)
> What is quorum in distributed systems? Explain read and write quorum and the W+R>N formula.

# Vopros (RU)
> Что такое кворум в распределенных системах? Объясните кворум чтения и записи и формулу W+R>N.

---

## Answer (EN)

**Quorum** is the minimum number of nodes that must agree for an operation to succeed in a distributed system.

### The Quorum Formula

```
N = Total replicas
W = Write quorum (nodes that must ACK write)
R = Read quorum (nodes that must respond to read)

For strong consistency: W + R > N

This guarantees read sees latest write (overlap exists)
```

### How It Works

```
N=3 replicas, W=2, R=2

Write "X=5":
- Write to 2 of 3 nodes (success)
- Node 1: X=5, Node 2: X=5, Node 3: X=old

Read X:
- Read from 2 of 3 nodes
- Get X=5 from Node 1 or 2 (guaranteed by W+R>N)
- Return latest value based on timestamp/version
```

### Common Configurations

| Config | W | R | Trade-off |
|--------|---|---|-----------|
| W=N, R=1 | All | One | Fast reads, slow writes |
| W=1, R=N | One | All | Fast writes, slow reads |
| W=R=(N+1)/2 | Majority | Majority | Balanced |
| W=1, R=1 | One | One | Eventual consistency (W+R <= N) |

### Example: N=5 Cluster

```
Strong consistency options:
- W=3, R=3 (majority quorum)
- W=4, R=2 (write-heavy)
- W=2, R=4 (read-heavy)

All satisfy: W + R > 5
```

### Sloppy Quorum

When nodes are unavailable, use temporary nodes:
- Write to available nodes + "hinted handoff" nodes
- Improves availability, weakens consistency guarantee

```
Normal: Write to replicas A, B, C
A unavailable: Write to B, C, D (D holds hint for A)
When A returns: D forwards hint to A
```

### Use Cases

| System | Default Quorum |
|--------|----------------|
| Cassandra | W=1, R=1 (tunable) |
| DynamoDB | W=2, R=2 (N=3) |
| Riak | W=quorum, R=quorum |
| ZooKeeper | Majority (Raft) |

---

## Otvet (RU)

**Кворум** - минимальное число узлов, которые должны согласиться для успешного выполнения операции в распределенной системе.

### Формула кворума

```
N = Всего реплик
W = Кворум записи (узлы, которые должны подтвердить запись)
R = Кворум чтения (узлы, которые должны ответить на чтение)

Для строгой согласованности: W + R > N

Это гарантирует, что чтение видит последнюю запись (есть пересечение)
```

### Как это работает

```
N=3 реплики, W=2, R=2

Запись "X=5":
- Запись на 2 из 3 узлов (успех)
- Узел 1: X=5, Узел 2: X=5, Узел 3: X=старое

Чтение X:
- Чтение с 2 из 3 узлов
- Получаем X=5 с Узла 1 или 2 (гарантировано W+R>N)
- Возвращаем последнее значение по timestamp/версии
```

### Распространенные конфигурации

| Конфиг | W | R | Компромисс |
|--------|---|---|------------|
| W=N, R=1 | Все | Один | Быстрое чтение, медленная запись |
| W=1, R=N | Один | Все | Быстрая запись, медленное чтение |
| W=R=(N+1)/2 | Большинство | Большинство | Сбалансировано |
| W=1, R=1 | Один | Один | Eventual consistency (W+R <= N) |

### Sloppy Quorum

Когда узлы недоступны, используются временные узлы:
- Запись на доступные узлы + "hinted handoff" узлы
- Улучшает доступность, ослабляет гарантию согласованности

---

## Follow-ups

- What is the difference between strict and sloppy quorum?
- How does Cassandra implement tunable consistency?
- What happens during network partition with quorum?
