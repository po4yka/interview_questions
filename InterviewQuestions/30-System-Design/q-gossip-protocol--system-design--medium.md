---
id: sysdes-053
title: Gossip Protocol
aliases:
- Gossip Protocol
- Epidemic Protocol
- Rumor Spreading
topic: system-design
subtopics:
- distributed-systems
- communication
- consistency
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-heartbeat-mechanisms--system-design--medium
- q-consistent-hashing--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- distributed-systems
- difficulty/medium
- communication
- system-design
anki_cards:
- slug: sysdes-053-0-en
  language: en
  anki_id: 1769160585577
  synced_at: '2026-01-23T13:49:17.863392'
- slug: sysdes-053-0-ru
  language: ru
  anki_id: 1769160585601
  synced_at: '2026-01-23T13:49:17.864425'
---
# Question (EN)
> What is the gossip protocol? How is it used in distributed systems for information dissemination?

# Vopros (RU)
> Что такое протокол сплетен (gossip)? Как он используется в распределённых системах для распространения информации?

---

## Answer (EN)

**Gossip protocol** (epidemic protocol) spreads information through random peer-to-peer exchanges, similar to how rumors spread in social networks.

### How It Works

```
Each round (e.g., every 1 second):
1. Node selects random peer(s)
2. Exchanges state information
3. Merges received state with local state

Round 1:    A knows "X"
            A → tells B

Round 2:    A, B know "X"
            A → tells C
            B → tells D

Round 3:    A, B, C, D know "X"
            (exponential spread)

After O(log N) rounds: All N nodes know "X"
```

### Gossip Variants

| Variant | Mechanism | Use Case |
|---------|-----------|----------|
| Push | Send updates to random peers | Fast dissemination |
| Pull | Request updates from random peers | Discovering new info |
| Push-Pull | Exchange in both directions | Faster convergence |

### Properties

```
Advantages:
+ Scalable: O(log N) rounds to spread
+ Fault tolerant: No single point of failure
+ Decentralized: No coordinator needed
+ Eventually consistent: All nodes converge

Disadvantages:
- Eventual (not immediate) consistency
- Redundant messages (same info sent multiple times)
- Non-deterministic convergence time
```

### Use Cases

| System | Gossip Usage |
|--------|--------------|
| Cassandra | Cluster membership, failure detection |
| DynamoDB | Membership, partitioning info |
| Consul | Service discovery, health status |
| CockroachDB | Cluster topology |
| Redis Cluster | Node state propagation |

### Failure Detection with Gossip

```
Heartbeat gossip:
- Each node maintains heartbeat counter
- Increment own counter each round
- Gossip counters to random peers
- If node's counter not updated in T seconds → suspect failure

φ accrual failure detector:
- Track heartbeat arrival times
- Calculate probability of failure
- More accurate than fixed timeout
```

### Implementation Example

```python
class GossipNode:
    def __init__(self, node_id):
        self.id = node_id
        self.state = {}  # key → (value, version)
        self.peers = []

    def gossip_round(self):
        # Select random peer
        peer = random.choice(self.peers)

        # Exchange state (push-pull)
        peer_state = peer.receive_gossip(self.state)
        self.merge_state(peer_state)

    def merge_state(self, remote_state):
        for key, (value, version) in remote_state.items():
            if key not in self.state or version > self.state[key][1]:
                self.state[key] = (value, version)
```

---

## Otvet (RU)

**Протокол gossip** (эпидемический протокол) распространяет информацию через случайный обмен между узлами, подобно слухам в социальных сетях.

### Как это работает

```
Каждый раунд (например, каждую 1 секунду):
1. Узел выбирает случайного соседа
2. Обменивается информацией о состоянии
3. Объединяет полученное состояние с локальным

Раунд 1:    A знает "X"
            A → рассказывает B

Раунд 2:    A, B знают "X"
            A → рассказывает C
            B → рассказывает D

Раунд 3:    A, B, C, D знают "X"
            (экспоненциальное распространение)

После O(log N) раундов: Все N узлов знают "X"
```

### Варианты Gossip

| Вариант | Механизм | Применение |
|---------|----------|------------|
| Push | Отправлять обновления случайным | Быстрое распространение |
| Pull | Запрашивать обновления у случайных | Обнаружение нового |
| Push-Pull | Обмен в обе стороны | Быстрая сходимость |

### Свойства

```
Преимущества:
+ Масштабируемый: O(log N) раундов
+ Отказоустойчивый: Нет единой точки отказа
+ Децентрализованный: Не нужен координатор
+ Eventually consistent: Все узлы сходятся

Недостатки:
- Eventual (не немедленная) согласованность
- Избыточные сообщения
- Недетерминированное время сходимости
```

### Применение

| Система | Использование Gossip |
|---------|---------------------|
| Cassandra | Членство в кластере, обнаружение сбоев |
| DynamoDB | Членство, информация о партициях |
| Consul | Service discovery, статус здоровья |
| Redis Cluster | Распространение состояния узлов |

### Обнаружение сбоев через Gossip

```
Heartbeat gossip:
- Каждый узел поддерживает счётчик heartbeat
- Инкрементирует свой счётчик каждый раунд
- Gossip счётчиков случайным соседям
- Если счётчик узла не обновляется T секунд → подозрение на сбой
```

---

## Follow-ups

- How do you prevent gossip protocol from overwhelming the network?
- What is anti-entropy in gossip protocols?
- How does CRDT combine with gossip for eventual consistency?
