---
id: sysdes-077
title: Leader Election in Distributed Systems
aliases:
- Leader Election
- Distributed Leader Election
- Bully Algorithm
- Ring Election
topic: system-design
subtopics:
- distributed-systems
- consensus
- fault-tolerance
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
- q-consensus-algorithms--system-design--hard
- q-quorum-consensus--system-design--hard
- q-consistency-models--system-design--hard
- q-byzantine-fault-tolerance--system-design--hard
created: 2025-01-26
updated: 2025-01-26
tags:
- distributed-systems
- difficulty/hard
- consensus
- fault-tolerance
- system-design
---
# Question (EN)
> How does leader election work in distributed systems? Explain the main algorithms and practical implementations.

# Vopros (RU)
> Как работает выбор лидера в распределённых системах? Объясните основные алгоритмы и практические реализации.

---

## Answer (EN)

**Leader election** is the process of designating a single node as the coordinator (leader) in a distributed system. The leader handles coordination tasks, serializes operations, or manages resources that require single-point-of-control.

### Why Leader Election?

```
Problems without a leader:
- Conflicting writes (who decides order?)
- Resource contention (deadlocks)
- Coordination overhead (N-to-N communication)

With leader:
- Serialized operations (leader decides order)
- Simplified coordination (leader as single source)
- Reduced communication (N-to-1, then 1-to-N)

Trade-off:
+ Simpler coordination
- Single point of failure (need re-election)
- Bottleneck at leader
```

### Classic Algorithms

#### 1. Bully Algorithm

```
Assumptions:
- Each node has unique ID
- Higher ID = higher priority
- Synchronous communication (timeouts work)

Process:
1. Node P detects leader failure
2. P sends ELECTION to all nodes with higher IDs
3. If any responds OK → P waits for COORDINATOR message
4. If no response → P declares itself leader
5. New leader sends COORDINATOR to all lower-ID nodes

┌─────────────────────────────────────────────┐
│   Node 4 (leader) crashes                   │
│                                             │
│   Node 2 detects, sends ELECTION to 3,4    │
│   Node 3 responds OK, sends ELECTION to 4   │
│   Node 4 no response                        │
│   Node 3 wins → sends COORDINATOR to 1,2    │
└─────────────────────────────────────────────┘

Complexity: O(n^2) messages worst case
```

#### 2. Ring Algorithm

```
Assumptions:
- Nodes arranged in logical ring
- Each node knows its successor

Process:
1. Initiator sends ELECTION with own ID
2. Each node adds own ID, forwards
3. Message travels full ring back to initiator
4. Initiator picks highest ID as leader
5. COORDINATOR message with result travels ring

┌─────────────────────────────────────────────┐
│        [3] ──────► [5]                      │
│         ↑           │                       │
│         │           ▼                       │
│        [1] ◄────── [7] (new leader)         │
│                                             │
│   Election msg: [3] → [3,5] → [3,5,7] →... │
└─────────────────────────────────────────────┘

Complexity: O(n) messages
```

### Raft Leader Election (Modern Standard)

```
Raft uses randomized timeouts and majority voting.

States:
- Follower: Default state, responds to leader
- Candidate: Seeking votes
- Leader: Handles all client requests

Election process:
1. Follower election timeout (150-300ms randomized)
2. Increment term, become Candidate
3. Vote for self, send RequestVote to all
4. Win if majority votes received
5. Send heartbeats to maintain leadership

┌─────────────────────────────────────────────┐
│                                             │
│   Follower ──timeout──► Candidate           │
│       ↑                     │               │
│       │               majority              │
│       │               votes                 │
│       │                     ▼               │
│       └────────────────── Leader            │
│      (higher term found)    │               │
│                             ▼               │
│                    sends heartbeats         │
└─────────────────────────────────────────────┘
```

#### Raft Election Rules

```
Safety guarantees:
1. At most one leader per term
2. Leader has most complete log
3. Majority required for election

Vote criteria (grant vote if):
- Candidate term >= voter term
- Voter hasn't voted this term (or voted for this candidate)
- Candidate log at least as up-to-date

"Up-to-date" comparison:
- Higher last log term wins
- Same term → longer log wins
```

### ZooKeeper Leader Election

Uses **ephemeral sequential nodes** and **watches** for efficient election.

```
Algorithm (sequential ephemeral nodes):
1. Each node creates /election/node-00000X
2. Node with lowest sequence number is leader
3. Others watch node with next-lower sequence
4. If watched node deleted → check if now leader

Example:
/election/node-0000001  ← Leader
/election/node-0000003  (watches 0000001)
/election/node-0000007  (watches 0000003)
/election/node-0000012  (watches 0000007)

Benefits:
- No thundering herd (only one node notified)
- O(1) messages per failure
- Automatic cleanup (ephemeral nodes)
```

#### ZooKeeper Implementation

```java
// Pseudo-code for ZK leader election
public void electLeader() {
    // Create ephemeral sequential node
    String myNode = zk.create("/election/node-",
        data, EPHEMERAL_SEQUENTIAL);

    while (true) {
        List<String> children = zk.getChildren("/election");
        Collections.sort(children);

        if (myNode.equals(children.get(0))) {
            // I am the leader
            runAsLeader();
            return;
        } else {
            // Watch previous node
            String previous = getPreviousNode(myNode, children);
            zk.exists(previous, watchCallback);
            wait(); // Until watch fires
        }
    }
}
```

### etcd Leader Election

Uses **Raft internally** and provides leader election as a service.

```
etcd election features:
- Lease-based leadership (automatic expiry)
- Compare-and-swap for atomic leader claim
- Watch for leader changes

Usage pattern:
1. Acquire lease (e.g., 10 seconds TTL)
2. Try to create key with lease
3. If successful → leader (keep refreshing lease)
4. If key exists → watch for deletion
5. On deletion → retry

```go
// etcd leader election (Go)
session, _ := concurrency.NewSession(client,
    concurrency.WithTTL(10))
election := concurrency.NewElection(session, "/leader/")

// Campaign blocks until elected
election.Campaign(ctx, "node-1")

// Now leader - do work
doLeaderWork()

// Resign when done
election.Resign(ctx)
```
```

### Split-Brain Problem

```
Network partition creates two "leaders":

Before partition:
┌──────────────────────────────────┐
│  [A]  [B]  [C]  [D]  [E]         │
│   └────────┴────────┘            │
│         Leader: C                │
└──────────────────────────────────┘

After partition:
┌───────────────┐   ┌──────────────┐
│  [A]  [B]     │   │   [C]  [D]  [E]
│  Leader: B?   │   │   Leader: C  │
└───────────────┘   └──────────────┘

Problem: Both sides think they have a leader!
```

#### Split-Brain Solutions

```
1. Quorum-based decisions
   - Require majority (n/2 + 1) for any decision
   - Minority partition cannot elect leader
   - Used by: Raft, ZooKeeper, etcd

2. Fencing tokens
   - Leader gets monotonically increasing token
   - Storage rejects requests with old tokens
   - Prevents stale leader from causing damage

3. STONITH (Shoot The Other Node In The Head)
   - Physically power off suspected old leader
   - Used in high-availability clusters
   - Requires out-of-band management (IPMI/iLO)

4. Lease-based leadership
   - Leader must refresh lease periodically
   - Old leader loses leadership when lease expires
   - Requires synchronized clocks (bounded drift)
```

### Comparison of Approaches

| Algorithm | Messages | Fault Model | Use Case |
|-----------|----------|-------------|----------|
| Bully | O(n^2) | Crash-stop | Simple systems |
| Ring | O(n) | Crash-stop | Token ring networks |
| Raft | O(n) | Crash-stop | Databases, KV stores |
| ZooKeeper | O(1) per failure | Crash-stop | Coordination service |
| Paxos | O(n) | Crash-stop | Theoretical foundation |

### Practical Systems

| System | Algorithm | Implementation Details |
|--------|-----------|----------------------|
| **etcd** | Raft | Built-in, used by Kubernetes |
| **Consul** | Raft | Service mesh leader |
| **ZooKeeper** | Zab (Paxos-like) | Ephemeral nodes + watches |
| **Redis Sentinel** | Gossip + voting | Master election for Redis |
| **Kafka** | ZooKeeper/KRaft | Controller election |
| **Elasticsearch** | Zen Discovery | Master election |

### Interview Edge Cases

```
Q: What if two candidates get same votes?
A: Both wait random timeout, retry. Randomization
   prevents repeated ties.

Q: How to detect leader failure?
A: Heartbeat timeout. Follower starts election
   if no heartbeat within timeout window.

Q: What if leader is slow, not crashed?
A: May cause unnecessary elections. Use adaptive
   timeouts, or leader leases.

Q: Can Byzantine nodes disrupt election?
A: Standard algorithms assume crash-stop.
   Need BFT consensus (PBFT) for Byzantine.

Q: What's fencing for?
A: Prevents old leader from making changes after
   new leader elected. Uses monotonic tokens.
```

---

## Otvet (RU)

**Выбор лидера** - это процесс назначения одного узла в качестве координатора (лидера) в распределённой системе. Лидер обрабатывает задачи координации, сериализует операции или управляет ресурсами, требующими единой точки контроля.

### Зачем нужен выбор лидера?

```
Проблемы без лидера:
- Конфликтующие записи (кто определяет порядок?)
- Конкуренция за ресурсы (дедлоки)
- Накладные расходы на координацию (N-to-N связь)

С лидером:
- Сериализованные операции (лидер определяет порядок)
- Упрощённая координация (лидер как единый источник)
- Уменьшение коммуникации (N-to-1, затем 1-to-N)

Компромисс:
+ Проще координация
- Единая точка отказа (нужны перевыборы)
- Узкое место на лидере
```

### Классические алгоритмы

#### 1. Алгоритм задиры (Bully)

```
Предположения:
- У каждого узла уникальный ID
- Больший ID = выше приоритет
- Синхронная связь (таймауты работают)

Процесс:
1. Узел P обнаруживает отказ лидера
2. P отправляет ELECTION всем узлам с большим ID
3. Если кто-то ответил OK → P ждёт COORDINATOR
4. Если нет ответа → P объявляет себя лидером
5. Новый лидер отправляет COORDINATOR всем с меньшим ID

Сложность: O(n^2) сообщений в худшем случае
```

#### 2. Кольцевой алгоритм

```
Предположения:
- Узлы расположены в логическом кольце
- Каждый узел знает своего преемника

Процесс:
1. Инициатор отправляет ELECTION со своим ID
2. Каждый узел добавляет свой ID, передаёт дальше
3. Сообщение проходит полный круг к инициатору
4. Инициатор выбирает наибольший ID как лидера
5. Сообщение COORDINATOR с результатом идёт по кольцу

Сложность: O(n) сообщений
```

### Выбор лидера в Raft

```
Raft использует рандомизированные таймауты и голосование большинством.

Состояния:
- Follower: Состояние по умолчанию, отвечает лидеру
- Candidate: Собирает голоса
- Leader: Обрабатывает все запросы клиентов

Процесс выборов:
1. Таймаут Follower (150-300мс, рандомизирован)
2. Увеличить term, стать Candidate
3. Проголосовать за себя, отправить RequestVote всем
4. Победа при получении большинства голосов
5. Отправлять heartbeats для поддержания лидерства
```

#### Правила выборов Raft

```
Гарантии безопасности:
1. Максимум один лидер за term
2. У лидера наиболее полный лог
3. Требуется большинство для избрания

Критерии голосования (дать голос если):
- Term кандидата >= term голосующего
- Голосующий не голосовал в этом term
- Лог кандидата не менее актуален

Сравнение "актуальности":
- Больший term последней записи побеждает
- Одинаковый term → побеждает более длинный лог
```

### Выбор лидера в ZooKeeper

Использует **эфемерные последовательные узлы** и **наблюдатели (watches)**.

```
Алгоритм:
1. Каждый узел создаёт /election/node-00000X
2. Узел с наименьшим номером - лидер
3. Остальные наблюдают за узлом с ближайшим меньшим номером
4. При удалении наблюдаемого узла → проверить, стал ли лидером

Пример:
/election/node-0000001  ← Лидер
/election/node-0000003  (наблюдает за 0000001)
/election/node-0000007  (наблюдает за 0000003)
/election/node-0000012  (наблюдает за 0000007)

Преимущества:
- Нет эффекта громового стада (уведомляется один узел)
- O(1) сообщений на отказ
- Автоматическая очистка (эфемерные узлы)
```

### Выбор лидера в etcd

Использует **Raft внутри** и предоставляет выбор лидера как сервис.

```
Особенности etcd:
- Лидерство на основе lease (автоматическое истечение)
- Compare-and-swap для атомарного захвата лидерства
- Watch для отслеживания изменений лидера

Паттерн использования:
1. Получить lease (например, 10 секунд TTL)
2. Попытаться создать ключ с lease
3. Если успешно → лидер (продлевать lease)
4. Если ключ существует → наблюдать за удалением
5. При удалении → повторить попытку
```

### Проблема Split-Brain

```
Сетевой раздел создаёт двух "лидеров":

После раздела:
┌───────────────┐   ┌──────────────┐
│  [A]  [B]     │   │   [C]  [D]  [E]
│  Лидер: B?    │   │   Лидер: C   │
└───────────────┘   └──────────────┘

Проблема: Обе стороны думают, что у них есть лидер!
```

#### Решения Split-Brain

```
1. Решения на основе кворума
   - Требовать большинство (n/2 + 1) для любого решения
   - Меньшинство не может выбрать лидера
   - Используется в: Raft, ZooKeeper, etcd

2. Токены ограждения (fencing tokens)
   - Лидер получает монотонно возрастающий токен
   - Хранилище отклоняет запросы со старыми токенами
   - Предотвращает ущерб от устаревшего лидера

3. STONITH (Shoot The Other Node In The Head)
   - Физически выключить предполагаемого старого лидера
   - Используется в кластерах высокой доступности
   - Требует внеполосного управления (IPMI/iLO)

4. Лидерство на основе lease
   - Лидер должен периодически обновлять lease
   - Старый лидер теряет лидерство при истечении
   - Требует синхронизированных часов
```

### Сравнение подходов

| Алгоритм | Сообщения | Модель отказов | Применение |
|----------|-----------|----------------|------------|
| Bully | O(n^2) | Crash-stop | Простые системы |
| Ring | O(n) | Crash-stop | Кольцевые сети |
| Raft | O(n) | Crash-stop | БД, KV-хранилища |
| ZooKeeper | O(1) на отказ | Crash-stop | Сервис координации |
| Paxos | O(n) | Crash-stop | Теоретическая основа |

### Практические системы

| Система | Алгоритм | Детали реализации |
|---------|----------|-------------------|
| **etcd** | Raft | Встроенный, используется Kubernetes |
| **Consul** | Raft | Лидер service mesh |
| **ZooKeeper** | Zab (Paxos-подобный) | Эфемерные узлы + watches |
| **Redis Sentinel** | Gossip + голосование | Выбор мастера для Redis |
| **Kafka** | ZooKeeper/KRaft | Выбор контроллера |
| **Elasticsearch** | Zen Discovery | Выбор мастера |

### Граничные случаи на интервью

```
В: Что если два кандидата получат одинаковое число голосов?
О: Оба ждут случайный таймаут, повторяют. Рандомизация
   предотвращает повторные ничьи.

В: Как обнаружить отказ лидера?
О: Таймаут heartbeat. Follower начинает выборы,
   если нет heartbeat в пределах окна таймаута.

В: Что если лидер медленный, а не упал?
О: Может вызвать лишние выборы. Использовать
   адаптивные таймауты или lease лидера.

В: Могут ли византийские узлы нарушить выборы?
О: Стандартные алгоритмы предполагают crash-stop.
   Нужен BFT консенсус (PBFT) для византийских узлов.

В: Для чего нужно ограждение (fencing)?
О: Предотвращает изменения от старого лидера после
   избрания нового. Использует монотонные токены.
```

---

## Follow-ups

- How does Raft handle network partitions during leader election?
- What is the difference between leader election and consensus?
- How do you implement leader election in Kubernetes using ConfigMaps or Leases?
- What are the trade-offs between ZooKeeper and etcd for leader election?
- How does Redis Sentinel handle split-brain scenarios?
