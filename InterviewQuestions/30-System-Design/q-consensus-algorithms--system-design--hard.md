---
id: sysdes-064
title: Consensus Algorithms - Raft and Paxos
aliases:
- Consensus Algorithms
- Raft
- Paxos
- Leader Election
topic: system-design
subtopics:
- distributed-systems
- consistency
- coordination
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-quorum-consensus--system-design--hard
- q-consistency-models--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- distributed-systems
- difficulty/hard
- consistency
- system-design
anki_cards:
- slug: sysdes-064-0-en
  language: en
  anki_id: 1769160583427
  synced_at: '2026-01-23T13:49:17.787268'
- slug: sysdes-064-0-ru
  language: ru
  anki_id: 1769160583449
  synced_at: '2026-01-23T13:49:17.788631'
---
# Question (EN)
> What are Raft and Paxos consensus algorithms? How do they ensure consistency in distributed systems?

# Vopros (RU)
> Что такое алгоритмы консенсуса Raft и Paxos? Как они обеспечивают согласованность в распределённых системах?

---

## Answer (EN)

**Consensus algorithms** allow distributed systems to agree on a single value even when some nodes fail. Raft and Paxos are the most widely used.

### Why Consensus?

```
Problem: Multiple nodes need to agree on:
- Who is the leader?
- What is the committed log?
- What order did operations happen?

Without consensus:
Node A: "X = 5"
Node B: "X = 10"
→ Split brain, inconsistent state
```

### Raft Overview

```
Raft is designed to be understandable.

Three roles:
- Leader: Handles all client requests
- Follower: Passive, responds to leader
- Candidate: During election

┌─────────────────────────────────────────────┐
│           Raft State Machine                │
│                                             │
│   Follower ──timeout──► Candidate           │
│       ↑                     │               │
│       │                     │ wins election │
│       │                     ▼               │
│       └────────────────── Leader            │
│         (discovers higher term)             │
└─────────────────────────────────────────────┘
```

### Raft Leader Election

```
1. Follower timeout (no heartbeat from leader)
2. Becomes Candidate, increments term
3. Votes for itself, requests votes from others
4. If majority votes received → becomes Leader
5. Sends heartbeats to maintain leadership

Election safety:
- Each node votes once per term
- Candidate with most up-to-date log preferred
- Majority required → only one leader per term
```

### Raft Log Replication

```
Client → Leader: "Set X=5"

1. Leader appends to local log (uncommitted)
2. Leader sends AppendEntries to followers
3. Followers append and acknowledge
4. When majority acknowledge → committed
5. Leader applies to state machine
6. Leader responds to client

Log structure:
┌────┬────┬────┬────┬────┐
│ T1 │ T1 │ T2 │ T2 │ T3 │  ← Term numbers
├────┼────┼────┼────┼────┤
│X=1 │Y=2 │X=5 │Z=3 │Y=7 │  ← Commands
└────┴────┴────┴────┴────┘
  1    2    3    4    5    ← Index
```

### Paxos vs Raft

| Aspect | Paxos | Raft |
|--------|-------|------|
| Understandability | Complex | Designed for clarity |
| Leader | Optional (Multi-Paxos) | Required |
| Log ordering | Per-entry | Continuous log |
| Implementation | Harder | Easier |
| Academic usage | Original (1989) | Newer (2014) |

### Systems Using Consensus

| System | Algorithm | Purpose |
|--------|-----------|---------|
| etcd | Raft | Kubernetes state |
| Consul | Raft | Service discovery |
| CockroachDB | Raft | Distributed SQL |
| ZooKeeper | Zab (Paxos-like) | Coordination |
| Google Spanner | Paxos | Global database |

### Key Guarantees

```
Safety (always):
- Only one leader per term
- Committed entries never lost
- All nodes agree on log content

Liveness (eventually):
- System makes progress
- Requires majority available
- Leader elected within bounded time
```

---

## Otvet (RU)

**Алгоритмы консенсуса** позволяют распределённым системам договориться о едином значении даже при отказе некоторых узлов. Raft и Paxos - наиболее широко используемые.

### Зачем консенсус?

```
Проблема: Множество узлов должны договориться о:
- Кто лидер?
- Какой лог закоммичен?
- В каком порядке произошли операции?

Без консенсуса:
Узел A: "X = 5"
Узел B: "X = 10"
→ Split brain, несогласованное состояние
```

### Обзор Raft

```
Raft разработан для понятности.

Три роли:
- Leader: Обрабатывает все запросы клиентов
- Follower: Пассивный, отвечает лидеру
- Candidate: Во время выборов
```

### Выборы лидера в Raft

```
1. Follower таймаут (нет heartbeat от лидера)
2. Становится Candidate, инкрементирует term
3. Голосует за себя, запрашивает голоса у других
4. Если получено большинство голосов → становится Leader
5. Отправляет heartbeats для поддержания лидерства

Безопасность выборов:
- Каждый узел голосует один раз за term
- Предпочтение кандидату с актуальным логом
- Требуется большинство → только один лидер за term
```

### Репликация лога в Raft

```
Клиент → Leader: "Set X=5"

1. Leader добавляет в локальный лог (uncommitted)
2. Leader отправляет AppendEntries followers
3. Followers добавляют и подтверждают
4. Когда большинство подтвердило → committed
5. Leader применяет к state machine
6. Leader отвечает клиенту
```

### Paxos vs Raft

| Аспект | Paxos | Raft |
|--------|-------|------|
| Понятность | Сложный | Разработан для ясности |
| Лидер | Опциональный | Обязательный |
| Упорядочение лога | По записям | Непрерывный лог |
| Реализация | Сложнее | Проще |

### Системы использующие консенсус

| Система | Алгоритм | Назначение |
|---------|----------|------------|
| etcd | Raft | Состояние Kubernetes |
| Consul | Raft | Service discovery |
| CockroachDB | Raft | Distributed SQL |
| ZooKeeper | Zab (Paxos-подобный) | Координация |
| Google Spanner | Paxos | Глобальная БД |

### Ключевые гарантии

```
Safety (всегда):
- Только один лидер за term
- Закоммиченные записи никогда не теряются
- Все узлы согласны о содержимом лога

Liveness (в конечном счёте):
- Система прогрессирует
- Требуется доступное большинство
```

---

## Follow-ups

- What happens during a network partition in Raft?
- What is Multi-Paxos and how does it differ from basic Paxos?
- How does Raft handle log compaction (snapshotting)?
