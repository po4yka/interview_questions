---
id: sysdes-052
title: Vector Clocks and Lamport Timestamps
aliases:
- Vector Clocks
- Lamport Timestamps
- Logical Clocks
topic: system-design
subtopics:
- distributed-systems
- ordering
- causality
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
- q-quorum-consensus--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- distributed-systems
- difficulty/hard
- ordering
- system-design
anki_cards:
- slug: sysdes-052-0-en
  language: en
  anki_id: 1769160581776
  synced_at: '2026-01-23T13:49:17.723078'
- slug: sysdes-052-0-ru
  language: ru
  anki_id: 1769160581800
  synced_at: '2026-01-23T13:49:17.724313'
---
# Question (EN)
> What are Lamport timestamps and vector clocks? How do they help establish ordering in distributed systems?

# Vopros (RU)
> Что такое метки времени Лампорта и векторные часы? Как они помогают установить порядок событий в распределённых системах?

---

## Answer (EN)

**Lamport timestamps** and **vector clocks** are logical clocks that establish event ordering without relying on synchronized physical clocks.

### The Problem

```
Physical clocks are unreliable in distributed systems:
- Clock drift between machines
- Network delays vary
- Can't determine "which happened first" reliably

Need: Logical ordering that captures causality
```

### Lamport Timestamps

```
Rules:
1. Each process maintains a counter (clock)
2. On local event: clock++
3. On send: attach clock value to message
4. On receive: clock = max(local_clock, received_clock) + 1

Process A:        Process B:
  [1]               [1]
   │                 │
  [2]──── msg ─────►[3]
   │                 │
  [3]               [4]
   │                 │
  [4]◄─── msg ──────[5]
   ↓                 ↓
  [6]               [6]
```

**Limitation:** If L(a) < L(b), we can't conclude a→b (only that b didn't happen before a)

### Vector Clocks

```
Each process maintains a vector of counters (one per process)

Process A [A,B,C]    Process B [A,B,C]
    [1,0,0]              [0,1,0]
       │                    │
    [2,0,0]──── msg ──────►[2,2,0]
       │                    │
    [3,0,0]              [2,3,0]
       │                    │
    [3,3,0]◄─── msg ──────[2,4,0]
```

**Comparison Rules:**
```
V1 < V2  (V1 happened before V2):
  - All V1[i] <= V2[i], AND
  - At least one V1[i] < V2[i]

V1 || V2 (concurrent):
  - Neither V1 < V2 nor V2 < V1

Examples:
[2,0,0] < [2,2,0]  → causally related
[3,0,0] || [2,3,0] → concurrent (conflict possible)
```

### Comparison

| Aspect | Lamport | Vector Clock |
|--------|---------|--------------|
| Size | O(1) | O(n) processes |
| Detects causality | Partial | Full |
| Detects conflicts | No | Yes |
| Use case | Total ordering | Conflict detection |

### Practical Uses

| System | Clock Type | Purpose |
|--------|------------|---------|
| DynamoDB | Vector clocks | Conflict detection |
| Cassandra | Lamport-like | Write ordering |
| Riak | Vector clocks | Sibling detection |
| CockroachDB | Hybrid logical | Serializable transactions |

---

## Otvet (RU)

**Метки времени Лампорта** и **векторные часы** - логические часы, устанавливающие порядок событий без синхронизированных физических часов.

### Проблема

```
Физические часы ненадёжны в распределённых системах:
- Дрейф часов между машинами
- Сетевые задержки варьируются
- Нельзя надёжно определить "что произошло раньше"

Нужно: Логический порядок, отражающий причинность
```

### Метки времени Лампорта

```
Правила:
1. Каждый процесс поддерживает счётчик (часы)
2. На локальное событие: clock++
3. На отправку: приложить значение часов к сообщению
4. На получение: clock = max(local_clock, received_clock) + 1
```

**Ограничение:** Если L(a) < L(b), нельзя заключить a→b

### Векторные часы

```
Каждый процесс поддерживает вектор счётчиков (по одному на процесс)

Процесс A [A,B,C]    Процесс B [A,B,C]
    [1,0,0]              [0,1,0]
       │                    │
    [2,0,0]──── msg ──────►[2,2,0]
```

**Правила сравнения:**
```
V1 < V2 (V1 произошло до V2):
  - Все V1[i] <= V2[i], И
  - Хотя бы один V1[i] < V2[i]

V1 || V2 (конкурентные):
  - Ни V1 < V2, ни V2 < V1

Примеры:
[2,0,0] < [2,2,0]  → причинно связаны
[3,0,0] || [2,3,0] → конкурентные (возможен конфликт)
```

### Сравнение

| Аспект | Лампорт | Векторные часы |
|--------|---------|----------------|
| Размер | O(1) | O(n) процессов |
| Определяет причинность | Частично | Полностью |
| Определяет конфликты | Нет | Да |
| Применение | Общий порядок | Обнаружение конфликтов |

### Практическое использование

| Система | Тип часов | Назначение |
|---------|-----------|------------|
| DynamoDB | Векторные | Обнаружение конфликтов |
| Cassandra | Лампорт-подобные | Порядок записей |
| Riak | Векторные | Обнаружение siblings |

---

## Follow-ups

- What is a hybrid logical clock?
- How do vector clocks scale with many nodes?
- What is the relationship between vector clocks and version vectors?
