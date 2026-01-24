---
id: sysdes-050
title: Heartbeat Mechanisms
aliases:
- Heartbeat
- Health Checks
- Failure Detection
topic: system-design
subtopics:
- distributed-systems
- fault-detection
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
- q-failover-strategies--system-design--medium
- q-circuit-breaker--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- distributed-systems
- difficulty/medium
- fault-detection
- system-design
anki_cards:
- slug: sysdes-050-0-en
  language: en
  anki_id: 1769159519544
  synced_at: '2026-01-23T13:29:45.889810'
- slug: sysdes-050-0-ru
  language: ru
  anki_id: 1769159519571
  synced_at: '2026-01-23T13:29:45.891176'
---
# Question (EN)
> What are heartbeat mechanisms in distributed systems? How are they used for failure detection?

# Vopros (RU)
> Что такое механизмы heartbeat в распределённых системах? Как они используются для обнаружения сбоев?

---

## Answer (EN)

**Heartbeat** is a periodic signal sent between nodes to indicate they are alive and functioning.

### Basic Mechanism

```
Node A                           Node B
  │                                │
  │──── heartbeat (t=0) ──────────►│
  │                                │
  │◄─── ACK ──────────────────────│
  │                                │
  │──── heartbeat (t=1s) ─────────►│
  │                                │
  │◄─── ACK ──────────────────────│
  │                                │
  │──── heartbeat (t=2s) ─────────►│
  │                                │
  │         (no ACK - timeout)     │
  │                                │
  │ [Node B marked as failed]      │
```

### Heartbeat Types

| Type | Direction | Use Case |
|------|-----------|----------|
| Push | Node → Monitor | Service health reporting |
| Pull | Monitor → Node | Active health checking |
| Gossip | Node ↔ Node | Decentralized detection |

### Push-based (Common)

```
Services periodically send heartbeat to coordinator:

┌─────────┐    heartbeat    ┌─────────────┐
│ Service │ ───────────────► │ Coordinator │
│    A    │ ◄─────────────── │  (ZooKeeper,│
└─────────┘                  │   Consul)   │
                             └─────────────┘

If no heartbeat received in X seconds → Mark failed
```

### Pull-based (Health Checks)

```
Load balancer actively checks service health:

┌─────────────┐    GET /health    ┌─────────┐
│    Load     │ ─────────────────► │ Service │
│  Balancer   │ ◄───────────────── │         │
└─────────────┘    200 OK          └─────────┘

If check fails N times → Remove from rotation
```

### Gossip Protocol

```
Decentralized failure detection:

1. Each node maintains list of known nodes
2. Periodically pick random node, exchange lists
3. If node not heard from in T seconds → Suspect
4. If suspected by M nodes → Confirmed dead

Used by: Cassandra, DynamoDB, Consul
```

### Failure Detection Trade-offs

```
                 Fast detection ◄────────► Few false positives

Aggressive:     Timeout = 1s, Miss = 2
                → Fast detection
                → Many false positives (network blip = "failure")

Conservative:   Timeout = 30s, Miss = 5
                → Slow detection
                → Few false positives
```

### Phi Accrual Failure Detector

```
Instead of binary (alive/dead), use probability:

φ (phi) = -log10(probability node is alive)

φ < 1:  Probably alive
φ > 1:  Probably dead
φ > 8:  Almost certainly dead

Benefits:
- Adapts to network conditions
- Used by Akka, Cassandra
```

### Best Practices

| Aspect | Recommendation |
|--------|----------------|
| Interval | 1-5 seconds (depends on use case) |
| Timeout | 3x interval minimum |
| Retries | 2-3 failures before marking dead |
| Payload | Minimal (just timestamp, maybe load) |
| Separate channel | Don't share with business traffic |

---

## Otvet (RU)

**Heartbeat** - периодический сигнал между узлами, указывающий что они живы и функционируют.

### Базовый механизм

```
Узел A                           Узел B
  │                                │
  │──── heartbeat (t=0) ──────────►│
  │                                │
  │◄─── ACK ──────────────────────│
  │                                │
  │──── heartbeat (t=1с) ─────────►│
  │                                │
  │         (нет ACK - таймаут)    │
  │                                │
  │ [Узел B помечен как failed]    │
```

### Типы Heartbeat

| Тип | Направление | Применение |
|-----|-------------|------------|
| Push | Узел → Монитор | Отчёт о здоровье сервиса |
| Pull | Монитор → Узел | Активная проверка здоровья |
| Gossip | Узел ↔ Узел | Децентрализованное обнаружение |

### Gossip протокол

```
Децентрализованное обнаружение сбоев:

1. Каждый узел поддерживает список известных узлов
2. Периодически выбираем случайный узел, обмениваемся списками
3. Если узел не отвечает T секунд → Подозреваем
4. Если подозревается M узлами → Подтверждённо мёртв

Используется: Cassandra, DynamoDB, Consul
```

### Компромиссы обнаружения сбоев

```
              Быстрое обнаружение ◄────────► Мало ложных срабатываний

Агрессивно:   Timeout = 1с, Miss = 2
              → Быстрое обнаружение
              → Много false positives

Консервативно: Timeout = 30с, Miss = 5
               → Медленное обнаружение
               → Мало false positives
```

### Phi Accrual Failure Detector

```
Вместо бинарного (жив/мёртв), используем вероятность:

φ (phi) = -log10(вероятность что узел жив)

φ < 1:  Вероятно жив
φ > 1:  Вероятно мёртв
φ > 8:  Почти наверняка мёртв

Преимущества:
- Адаптируется к сетевым условиям
- Используется Akka, Cassandra
```

### Лучшие практики

| Аспект | Рекомендация |
|--------|--------------|
| Интервал | 1-5 секунд |
| Таймаут | Минимум 3x интервал |
| Ретраи | 2-3 сбоя перед пометкой dead |
| Payload | Минимальный (timestamp, может нагрузка) |
| Отдельный канал | Не смешивать с бизнес-трафиком |

---

## Follow-ups

- How does Kubernetes implement health checks (liveness vs readiness)?
- What is the split-brain problem and how do heartbeats relate to it?
- How do you choose heartbeat interval for different scenarios?
