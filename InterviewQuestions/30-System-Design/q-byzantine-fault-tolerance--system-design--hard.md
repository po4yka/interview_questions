---
id: sysdes-073
title: Byzantine Fault Tolerance
aliases:
- Byzantine Fault Tolerance
- BFT
- Byzantine Generals Problem
topic: system-design
subtopics:
- distributed-systems
- consensus
- fault-tolerance
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-consensus-algorithms--system-design--hard
- q-gossip-protocol--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- distributed-systems
- difficulty/hard
- consensus
- system-design
anki_cards:
- slug: sysdes-073-0-en
  language: en
  anki_id: 1769161753182
  synced_at: '2026-01-23T13:49:17.742028'
- slug: sysdes-073-0-ru
  language: ru
  anki_id: 1769161753207
  synced_at: '2026-01-23T13:49:17.743165'
---
# Question (EN)
> What is Byzantine Fault Tolerance (BFT)? How does it differ from crash fault tolerance?

# Vopros (RU)
> Что такое византийская отказоустойчивость (BFT)? Чем она отличается от отказоустойчивости к сбоям?

---

## Answer (EN)

**Byzantine Fault Tolerance (BFT)** is the ability of a distributed system to reach consensus even when some nodes behave maliciously or arbitrarily (not just crash).

### The Byzantine Generals Problem

```
Scenario: Generals must agree on attack or retreat
          Some generals may be TRAITORS

    General A          General B          General C
   (Loyal)            (TRAITOR)          (Loyal)
      │                   │                  │
      │ "Attack!"         │ "Retreat!"       │
      │ ────────────────> │ ────────────────>│
      │                   │ "Attack!"        │
      │ <──────────────── │                  │
      │                   │ <────────────────│

Problem: How can loyal generals agree when traitors send conflicting messages?
```

### Crash Fault vs Byzantine Fault

| Aspect | Crash Fault | Byzantine Fault |
|--------|-------------|-----------------|
| Failure mode | Node stops responding | Node sends wrong/malicious data |
| Behavior | Fail-stop (predictable) | Arbitrary (unpredictable) |
| Nodes needed | 2f + 1 to tolerate f failures | 3f + 1 to tolerate f failures |
| Examples | Server crash, network partition | Hacked node, software bug, malicious actor |
| Algorithms | Raft, Paxos | PBFT, Tendermint, HotStuff |

### Why 3f + 1 Nodes?

```
To tolerate f Byzantine nodes:
- Need 3f + 1 total nodes
- Requires 2f + 1 agreement (quorum)

Example with f = 1 (tolerate 1 bad node):
- Need 4 nodes total
- Need 3 nodes to agree

Why? With 3 nodes and 1 Byzantine:
  Node A (honest): "Value is X"
  Node B (honest): "Value is X"
  Node C (Byzantine): Tells A "Value is X", Tells B "Value is Y"

  → B cannot distinguish who is lying!

With 4 nodes and 1 Byzantine:
  3 honest nodes will outvote the 1 Byzantine node
```

### PBFT (Practical Byzantine Fault Tolerance)

```
Three phases:

1. Pre-prepare: Leader proposes value
   Leader → All: <PRE-PREPARE, view, seq, digest>

2. Prepare: Nodes validate and broadcast
   All → All: <PREPARE, view, seq, digest, node_id>
   Wait for 2f matching prepares

3. Commit: Nodes commit if enough prepares
   All → All: <COMMIT, view, seq, digest, node_id>
   Wait for 2f + 1 matching commits

View change: If leader is faulty, elect new leader
```

### BFT in Practice

| System | BFT Algorithm | Use Case |
|--------|---------------|----------|
| Bitcoin | Proof of Work (Nakamoto) | Cryptocurrency |
| Ethereum 2.0 | Casper FFG | Cryptocurrency |
| Hyperledger Fabric | PBFT variant | Enterprise blockchain |
| Cosmos/Tendermint | Tendermint BFT | Blockchain platform |
| LibraBFT (Diem) | HotStuff variant | Payment network |

### When Do You Need BFT?

```
Need BFT:
- Public blockchains (untrusted participants)
- Multi-organization systems (no single trust)
- High-value transactions (financial systems)
- Adversarial environments

Don't need BFT (Crash fault tolerance is enough):
- Single organization systems
- Internal microservices
- Trusted data centers
- Most enterprise applications
```

### Performance Comparison

| Algorithm | Communication | Latency | Throughput |
|-----------|---------------|---------|------------|
| Raft (CFT) | O(n) | Low | High |
| PBFT (BFT) | O(n^2) | Higher | Lower |
| HotStuff (BFT) | O(n) | Medium | Medium |

---

## Otvet (RU)

**Византийская отказоустойчивость (BFT)** - способность распределённой системы достигать консенсуса даже когда некоторые узлы ведут себя злонамеренно или произвольно (не просто падают).

### Проблема византийских генералов

```
Сценарий: Генералы должны согласовать атаку или отступление
          Некоторые генералы могут быть ПРЕДАТЕЛЯМИ

    Генерал A          Генерал B          Генерал C
   (Лояльный)         (ПРЕДАТЕЛЬ)        (Лояльный)
      │                   │                  │
      │ "Атака!"          │ "Отступление!"   │
      │ ────────────────> │ ────────────────>│

Проблема: Как лояльным генералам договориться, когда предатели шлют противоречивые сообщения?
```

### Crash Fault vs Byzantine Fault

| Аспект | Crash Fault | Byzantine Fault |
|--------|-------------|-----------------|
| Режим отказа | Узел перестаёт отвечать | Узел шлёт неверные данные |
| Поведение | Предсказуемое (падение) | Произвольное |
| Нужно узлов | 2f + 1 для f отказов | 3f + 1 для f отказов |
| Примеры | Сбой сервера, разделение сети | Взломанный узел, баг, злоумышленник |
| Алгоритмы | Raft, Paxos | PBFT, Tendermint, HotStuff |

### Почему 3f + 1 узлов?

```
Для устойчивости к f византийским узлам:
- Нужно 3f + 1 узлов всего
- Требуется согласие 2f + 1 (кворум)

Пример с f = 1:
- Нужно 4 узла
- Нужно согласие 3 узлов

Почему? С 3 узлами и 1 византийским:
  Узел B не может определить, кто лжёт!

С 4 узлами и 1 византийским:
  3 честных узла переголосуют 1 византийский
```

### BFT на практике

| Система | BFT алгоритм | Применение |
|---------|--------------|------------|
| Bitcoin | Proof of Work | Криптовалюта |
| Ethereum 2.0 | Casper FFG | Криптовалюта |
| Hyperledger Fabric | Вариант PBFT | Enterprise блокчейн |
| Cosmos/Tendermint | Tendermint BFT | Блокчейн платформа |

### Когда нужен BFT?

```
Нужен BFT:
- Публичные блокчейны (недоверенные участники)
- Мультиорганизационные системы
- Высокоценные транзакции
- Враждебные среды

Не нужен BFT (достаточно CFT):
- Системы одной организации
- Внутренние микросервисы
- Доверенные дата-центры
- Большинство enterprise приложений
```

### Сравнение производительности

| Алгоритм | Коммуникация | Задержка | Пропускная способность |
|----------|--------------|----------|------------------------|
| Raft (CFT) | O(n) | Низкая | Высокая |
| PBFT (BFT) | O(n^2) | Выше | Ниже |
| HotStuff (BFT) | O(n) | Средняя | Средняя |

---

## Follow-ups

- How does Proof of Work achieve Byzantine fault tolerance?
- What is the CAP theorem relationship with BFT?
- How do modern BFT algorithms like HotStuff improve on PBFT?
