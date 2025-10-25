---
id: 20251012-300004
title: "CAP Theorem and Distributed Systems / CAP теорема и распределённые системы"
aliases: ["CAP Theorem", "CAP теорема"]
topic: system-design
subtopics: [availability, consistency, distributed-systems, partition-tolerance]
question_kind: system-design
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-cap-theorem, q-caching-strategies--system-design--medium, q-microservices-vs-monolith--system-design--hard]
created: 2025-10-12
updated: 2025-01-25
tags: [cap-theorem, consistency, difficulty/hard, distributed-systems, system-design]
sources: [https://en.wikipedia.org/wiki/CAP_theorem]
date created: Sunday, October 12th 2025, 8:27:12 pm
date modified: Saturday, October 25th 2025, 7:58:41 pm
---

# Вопрос (RU)
> Что такое CAP теорема? Какие компромиссы делают разные системы, и как выбрать между CP и AP системами?

# Question (EN)
> What is the CAP theorem? What trade-offs do different systems make, and how do you choose between CP and AP systems?

---

## Ответ (RU)

**Теория CAP теоремы:**
CAP теорема (теорема Брюера, 2000) утверждает, что распределённая система может обеспечить максимум ДВЕ из трёх гарантий: **Консистентность**, **Доступность** и **Устойчивость к разделению**. Это фундаментальное ограничение распределённых систем, основанное на физических законах распространения информации.

**Три гарантии:**
- **Consistency (C)** - каждое чтение получает самую последнюю запись (линеаризуемость). Все узлы видят одинаковые данные одновременно, как будто система работает на одной машине.
- **Availability (A)** - каждый запрос получает ответ без ошибок в разумное время. Система продолжает обслуживать запросы даже при отказе узлов.
- **Partition Tolerance (P)** - система работает несмотря на разделение сети. Узлы могут потерять связь друг с другом, но система продолжает функционировать.

**Почему невозможны все три:**
В реальности сетевые разделения неизбежны (отказы сети, задержки, потеря пакетов). Когда происходит разделение, система должна выбрать: либо отклонить запросы (жертвуя доступностью), либо разрешить несогласованные данные (жертвуя консистентностью). Невозможно одновременно гарантировать консистентность и доступность при разделении сети.

**CP системы (Консистентность + Устойчивость к разделению):**

*Теория:* CP системы жертвуют доступностью ради строгой консистентности. При разделении сети система блокирует операции, которые могут нарушить консистентность. Используют алгоритмы консенсуса (Paxos, Raft) для координации между узлами. Применяются в финансовых системах, где неправильные данные хуже временной недоступности.

*Примеры:* MongoDB (с majority write concern), HBase, Redis (с WAIT), ZooKeeper, etcd, Consul.

*Сценарии:* Банковские переводы, управление инвентарём, системы бронирования, медицинские записи.

```kotlin
// CP: Строгая консистентность, блокировка при разделении
database.transaction {
    val account = database.getAccount(id) // Блокируется при разделении
    database.updateBalance(id, newBalance) // Гарантия ACID
}
```

**AP системы (Доступность + Устойчивость к разделению):**

*Теория:* AP системы жертвуют строгой консистентностью ради высокой доступности. При разделении сети обе стороны продолжают принимать запросы, что может привести к временной несогласованности. Используют eventual consistency - данные со временем сходятся к согласованному состоянию. Применяют механизмы разрешения конфликтов (last-write-wins, version vectors, CRDTs).

*Примеры:* Cassandra, DynamoDB, Riak, CouchDB, DNS.

*Сценарии:* Социальные сети, каталоги товаров, логирование, аналитика, счётчики просмотров.

```kotlin
// AP: Высокая доступность, eventual consistency
database.incrementLikes(postId) // Всегда успешно
val likes = database.getLikes(postId) // Может быть слегка устаревшим
```

**Разрешение конфликтов в AP системах:**

*Теория:* При разделении сети разные узлы могут принимать конфликтующие обновления. После восстановления связи необходимо разрешить конфликты.

*Стратегии:*
- **Last-Write-Wins (LWW)** - побеждает запись с более поздней меткой времени. Простая, но может терять данные.
- **Version Vectors** - отслеживают причинно-следственные связи между версиями. Обнаруживают конфликты, требуют ручного разрешения.
- **CRDTs** - структуры данных, которые автоматически сходятся к согласованному состоянию без конфликтов. Математически гарантируют корректное слияние.

```kotlin
// CRDT: Автоматическое корректное слияние без конфликтов
class GCounter {
    private val counters = mutableMapOf<NodeId, Long>()
    fun increment(nodeId: NodeId) { counters[nodeId] = (counters[nodeId] ?: 0) + 1 }
    fun value(): Long = counters.values.sum()
    fun merge(other: GCounter): GCounter { /* Всегда корректно сходится */ }
}
```

**Модели консистентности:**

*Теория:* Существует спектр моделей консистентности между строгой и слабой.

- **Строгая консистентность (Linearizability)** - самая сильная гарантия. Все операции выглядят как выполненные мгновенно в некоторой последовательности. Эквивалентна работе на одной машине.
- **Sequential consistency** - операции всех процессов выполняются в некотором последовательном порядке, но порядок может не соответствовать реальному времени.
- **Causal consistency** - сохраняет причинно-следственные связи. Если операция A вызвала операцию B, все узлы видят A перед B.
- **Eventual consistency** - самая слабая гарантия. Если прекратить обновления, все реплики со временем сойдутся к одному значению.

**Настраиваемая консистентность:**

*Теория:* Некоторые системы (Cassandra, DynamoDB) позволяют настраивать уровень консистентности для каждого запроса. Используя кворумы (R + W > N), можно достичь строгой консистентности в AP системе.

```kotlin
// Настройка per-request: CP для критических, AP для обычных операций
criticalRead(id, ConsistencyLevel.QUORUM) // CP: строгая консистентность
casualRead(id, ConsistencyLevel.ONE) // AP: eventual consistency
```

## Answer (EN)

**CAP Theorem Theory:**
CAP theorem (Brewer's theorem, 2000) states that a distributed system can provide at most TWO of three guarantees: **Consistency**, **Availability**, and **Partition Tolerance**. This is a fundamental limitation of distributed systems based on physical laws of information propagation.

**Three Guarantees:**
- **Consistency (C)** - every read receives the most recent write (linearizability). All nodes see the same data simultaneously, as if the system runs on a single machine.
- **Availability (A)** - every request receives a response without errors in reasonable time. The system continues serving requests even when nodes fail.
- **Partition Tolerance (P)** - system continues despite network partitions. Nodes may lose connection to each other, but the system continues functioning.

**Why all three are impossible:**
In reality, network partitions are inevitable (network failures, delays, packet loss). When a partition occurs, the system must choose: either reject requests (sacrificing availability), or allow inconsistent data (sacrificing consistency). It's impossible to simultaneously guarantee consistency and availability during network partitions.

**CP Systems (Consistency + Partition Tolerance):**

*Theory:* CP systems sacrifice availability for strong consistency. During network partitions, the system blocks operations that could violate consistency. Use consensus algorithms (Paxos, Raft) for node coordination. Applied in financial systems where incorrect data is worse than temporary unavailability.

*Examples:* MongoDB (with majority write concern), HBase, Redis (with WAIT), ZooKeeper, etcd, Consul.

*Use cases:* Bank transfers, inventory management, booking systems, medical records.

```kotlin
// CP: Strong consistency, blocks during partition
database.transaction {
    val account = database.getAccount(id) // Blocks during partition
    database.updateBalance(id, newBalance) // ACID guarantee
}
```

**AP Systems (Availability + Partition Tolerance):**

*Theory:* AP systems sacrifice strong consistency for high availability. During network partitions, both sides continue accepting requests, which may lead to temporary inconsistency. Use eventual consistency - data converges to consistent state over time. Apply conflict resolution mechanisms (last-write-wins, version vectors, CRDTs).

*Examples:* Cassandra, DynamoDB, Riak, CouchDB, DNS.

*Use cases:* Social media, product catalogs, logging, analytics, view counters.

```kotlin
// AP: High availability, eventual consistency
database.incrementLikes(postId) // Always succeeds
val likes = database.getLikes(postId) // May be slightly stale
```

**Conflict Resolution in AP Systems:**

*Theory:* During network partitions, different nodes may accept conflicting updates. After connection is restored, conflicts must be resolved.

*Strategies:*
- **Last-Write-Wins (LWW)** - write with later timestamp wins. Simple but may lose data.
- **Version Vectors** - track causal relationships between versions. Detect conflicts, require manual resolution.
- **CRDTs** - data structures that automatically converge to consistent state without conflicts. Mathematically guarantee correct merging.

```kotlin
// CRDT: Automatic correct merging without conflicts
class GCounter {
    private val counters = mutableMapOf<NodeId, Long>()
    fun increment(nodeId: NodeId) { counters[nodeId] = (counters[nodeId] ?: 0) + 1 }
    fun value(): Long = counters.values.sum()
    fun merge(other: GCounter): GCounter { /* Always converges correctly */ }
}
```

**Consistency Models:**

*Theory:* There is a spectrum of consistency models between strong and weak.

- **Strong consistency (Linearizability)** - strongest guarantee. All operations appear as if executed instantaneously in some sequence. Equivalent to single-machine operation.
- **Sequential consistency** - operations of all processes execute in some sequential order, but order may not correspond to real time.
- **Causal consistency** - preserves cause-effect relationships. If operation A caused operation B, all nodes see A before B.
- **Eventual consistency** - weakest guarantee. If updates stop, all replicas eventually converge to the same value.

**Tunable Consistency:**

*Theory:* Some systems (Cassandra, DynamoDB) allow tuning consistency level per request. Using quorums (R + W > N), strong consistency can be achieved in an AP system.

```kotlin
// Per-request tuning: CP for critical, AP for casual operations
criticalRead(id, ConsistencyLevel.QUORUM) // CP: strong consistency
casualRead(id, ConsistencyLevel.ONE) // AP: eventual consistency
```

---

## Follow-ups

- What is the difference between strong and eventual consistency?
- How does the PACELC theorem extend CAP?
- Explain different conflict resolution strategies in AP systems

## Related Questions

### Prerequisites (Easier)
- [[q-caching-strategies--system-design--medium]] - Caching fundamentals
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing

### Related (Same Level)
- [[q-horizontal-vertical-scaling--system-design--medium]] - Scaling strategies
- [[q-message-queues-event-driven--system-design--medium]] - Message queues

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - Architecture patterns
- [[q-database-sharding-partitioning--system-design--hard]] - Database scaling
