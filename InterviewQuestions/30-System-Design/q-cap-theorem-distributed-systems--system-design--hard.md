---
id: sysdes-004
title: CAP Theorem and Distributed Systems / CAP теорема и распределённые системы
aliases:
- CAP Theorem
- CAP теорема
topic: system-design
subtopics:
- availability
- consistency
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
- c-architecture-patterns
- q-caching-strategies--system-design--medium
- q-microservices-vs-monolith--system-design--hard
created: 2025-10-12
updated: 2025-11-11
tags:
- cap-theorem
- consistency
- difficulty/hard
- distributed-systems
- system-design
sources:
- https://en.wikipedia.org/wiki/CAP_theorem
anki_cards:
- slug: sysdes-004-0-en
  language: en
  anki_id: 1768468551659
  synced_at: '2026-01-23T13:29:45.900719'
- slug: sysdes-004-0-ru
  language: ru
  anki_id: 1768468551684
  synced_at: '2026-01-23T13:29:45.901895'
---
# Вопрос (RU)
> Что такое CAP теорема? Какие компромиссы делают разные системы, и как выбрать между CP и AP системами?

# Question (EN)
> What is the CAP theorem? What trade-offs do different systems make, and how do you choose between CP and AP systems?

---

## Ответ (RU)

См. разделы "Краткая Версия" и "Детальная Версия" ниже для полного ответа.

## Answer (EN)

See "`Short` Version" and "Detailed Version" sections below for the complete answer.

## Follow-ups

- What is the difference between strong and eventual consistency?
- How does the PACELC theorem extend CAP?
- Explain different conflict resolution strategies in AP systems.

## References
- [[c-cap-theorem]]
- https://en.wikipedia.org/wiki/CAP_theorem

## Related Questions

### Base (easier)
- [[q-caching-strategies--system-design--medium]] - Caching basics
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing strategies

### Adjacent (same level)
- [[q-horizontal-vertical-scaling--system-design--medium]] - Scaling strategies
- [[q-message-queues-event-driven--system-design--medium]] - `Message` queues and event-driven systems

### Advanced (harder)
- [[q-microservices-vs-monolith--system-design--hard]] - Architectural approaches
- [[q-database-sharding-partitioning--system-design--hard]] - `Database` sharding and partitioning

## Краткая Версия
В условиях реального сетевого разделения распределённая система не может одновременно обеспечить строгую консистентность и полную доступность, сохраняя устойчивость к разделению. Практически P считается обязательным, а реальный выбор идёт между CP и AP-поведением, исходя из требований бизнеса и допустимых рисков.
### Детальная Версия
**Теория CAP теоремы:**
CAP теорема (теорема Брюэра, формализована Гилбертом и Линчем в 2002) описывает поведение распределённых систем при сетевых разделениях. В присутствии разделения сети система не может одновременно гарантировать и строгую **Консистентность**, и полную **Доступность**; она вынуждена выбирать между ними, сохраняя **Устойчивость к разделению**. Важно: в практических распределённых системах устойчивость к разделению не является опцией — разделения необходимо уметь переживать, поэтому реальный выбор при разделении идёт между C и A.
### Требования
- Функциональные:
  - Обслуживать запросы на чтение и запись в распределённой среде.
  - Обеспечивать репликацию данных между узлами.
- Нефункциональные:
  - Толерантность к сетевым разделениям (P).
  - Заданные уровни консистентности и доступности в зависимости от сценариев.
  - Предсказуемое поведение при отказах (чёткий выбор CP или AP-компромисса).
### Архитектура (на Уровне Концепций CAP)
На высоком уровне распределённая архитектура строится вокруг следующих решений:
- Репликация данных между несколькими узлами или датацентрами.
- Механизмы координации для CP-систем (консенсус, лидерство, кворумы).
- Механизмы eventual consistency и разрешения конфликтов для AP-систем.
- Настраиваемые уровни консистентности для отдельных операций в гибридных системах.
**Три гарантии:**
- **Consistency (C)** — каждое чтение получает результат последней завершённой записи (линеаризуемость). Все узлы видят данные согласованно, как будто система работает на одной машине.
- **Availability (A)** — каждый запрос к неотказавшему узлу получает ответ (не ошибку) в разумное время. Система продолжает обслуживать запросы при частичных отказах.
- **Partition Tolerance (P)** — система корректно работает при разделении сети: узлы могут терять связь друг с другом, но система обрабатывает запросы, допускаемые выбранным компромиссом между C и A.
**Почему невозможно обеспечить все три одновременно при разделении:**
Сетевые разделения, задержки и потери пакетов неизбежны. Когда происходит разделение, система должна выбирать:
- отклонять или блокировать часть операций, чтобы не нарушить консистентность (жертвуя доступностью), или
- принимать запросы независимо в разных частях кластера, допуская временную рассогласованность данных (жертвуя строгой консистентностью).
Нельзя одновременно гарантировать строгую консистентность и полноту доступности для всех запросов в условиях реального сетевого разделения.
**CP системы (Консистентность + Устойчивость к разделению):**
*Теория:* CP-системы в условиях разделения отдают приоритет строгой консистентности над доступностью. При потере связи между узлами операции, которые нельзя безопасно подтверждать, блокируются или отклоняются. Часто используются алгоритмы консенсуса (Paxos, Raft) для координации. Такой подход характерен для сценариев, где некорректные данные хуже временной недоступности.
*Примеры (по поведению и конфигурации):* кластеры MongoDB при использовании majority write concern и соответствующих режимов чтения, HBase, ZooKeeper, etcd, Consul, распределённые транзакционные хранилища на основе Paxos/Raft. Некоторые режимы Redis (например, с `WAIT` и строгой конфигурацией) могут приближаться к CP-поведению, но по умолчанию Redis не даёт полноценных CP-гарантий в распределённом режиме.
*Сценарии:* банковские переводы, управление балансами и инвентарём, системы бронирования, медицинские записи.
```kotlin
// Концептуальный пример CP-поведения:
// При разделении кластер может заблокировать операции записи/чтения,
// если не может безопасно подтвердить консенсус (жертва доступности ради консистентности).
database.transaction {
    val account = database.getAccount(id) // Может блокироваться или завершаться ошибкой при разделении
    database.updateBalance(id, newBalance) // Гарантируется согласованное состояние (ACID/линеаризуемость)
}
```
**AP системы (Доступность + Устойчивость к разделению):**
*Теория:* AP-системы в условиях разделения приоритетно сохраняют высокую доступность. Узлы в разных частях кластера продолжают принимать запросы независимо, что может приводить к временной неконсистентности между репликами. Обычно используется eventual consistency: при отсутствии новых обновлений все копии данных со временем сходятся к согласованному состоянию. Для этого применяются стратегии разрешения конфликтов (Last-Write-Wins, версионные векторы, CRDT и др.).
*Примеры (по модели):* Cassandra, Riak, CouchDB, многие реализации Dynamo-подобных хранилищ, отдельные режимы Amazon DynamoDB. DNS на практике также демонстрирует AP-поведение.
*Сценарии:* социальные сети, каталоги товаров, логирование, аналитика, счётчики просмотров.
```kotlin
// Концептуальный пример AP-поведения:
// Операции принимаются локально даже при возможном разделении;
// чтения могут возвращать устаревшие данные до сходимости.
database.incrementLikes(postId) // Стремится быть успешной операцией даже при сбоях сети
val likes = database.getLikes(postId) // Может вернуть слегка устаревшее значение
```
**Разрешение конфликтов в AP системах:**
*Теория:* При разделении сети разные узлы могут принять конфликтующие обновления одного и того же объекта. После восстановления связи система должна обнаружить и разрешить конфликты так, чтобы обеспечить сходимость.
*Стратегии:*
- **Last-Write-Wins (LWW)** — побеждает запись с более поздней меткой времени. Просто, но может приводить к потере параллельных обновлений.
- **Version Vectors** — отслеживают причинно-следственные связи между версиями. Позволяют обнаруживать конфликтующие версии и обрабатывать их (часто с участием прикладной логики).
- **CRDTs** — специальные структуры данных, которые при определённых операциях и правилах merge гарантированно сходятся к согласованному состоянию без потерь, независимо от порядка доставки и дублирования сообщений.
```kotlin
// Упрощённый пример G-Counter CRDT: монотонное увеличение и коммутативное слияние
class GCounter {
    private val counters = mutableMapOf<NodeId, Long>()
    fun increment(nodeId: NodeId) {
        counters[nodeId] = (counters[nodeId] ?: 0L) + 1L
    }
    fun value(): Long = counters.values.sum()
    fun merge(other: GCounter): GCounter {
        val result = GCounter()
        (counters.keys + other.counters.keys).forEach { nodeId ->
            val thisVal = this.counters[nodeId] ?: 0L
            val otherVal = other.counters[nodeId] ?: 0L
            result.counters[nodeId] = maxOf(thisVal, otherVal)
        }
        return result
    }
}
```
**Модели консистентности:**
*Теория:* Между строгой и слабой консистентностью существует спектр моделей. Важно понимать их отличие от бинарного деления CAP.
- **Строгая консистентность (линеаризуемость)** — самая сильная гарантия. Каждая операция выглядит как мгновенно выполненная в некоторый момент времени в единой глобальной последовательности.
- **Sequential consistency** — существует некоторый общий порядок операций, согласованный между всеми процессами, но он не обязан соответствовать реальному времени.
- **Causal consistency** — сохраняются причинно-следственные зависимости: если операция A повлияла на B, все узлы видят A не позже B.
- **Eventual consistency** — при остановке обновлений все реплики в итоге сходятся к одному значению, но момент и порядок промежуточных состояний не регламентированы.
**Настраиваемая консистентность:**
*Теория:* Некоторые системы (например, Cassandra, Dynamo-подобные базы данных) позволяют выбирать уровень консистентности для конкретного запроса. При использовании кворумов (`R + W > N`) можно добиться более сильной, квазилинеаризуемой консистентности для чтений и записей, однако это не превращает систему в «чистую» CP-систему по CAP: при реальном разделении всё равно приходится выбирать между отказом части операций и принятием потенциально рассогласованных данных.
```kotlin
// Пример настройки на уровне запроса:
// для критичных операций используем более сильный (quorum) уровень консистентности,
// для некритичных — более слабый.
criticalRead(id, ConsistencyLevel.QUORUM) // Более сильная консистентность за счёт кворума
casualRead(id, ConsistencyLevel.ONE) // Лучшая доступность, eventual consistency
```
## Short Version
Under a real network partition, a distributed system cannot simultaneously provide strong consistency and full availability while remaining partition-tolerant. In practice, P is mandatory, and real-world systems make CP/AP-flavored trade-offs based on business requirements and acceptable risk.
## Detailed Version
**CAP Theorem Theory:**
The CAP theorem (Brewer's theorem, formalized by Gilbert and Lynch in 2002) describes behavior of distributed systems under network partitions. In the presence of a partition, a system cannot simultaneously guarantee both strong **Consistency** and full **Availability**; it must choose between them while maintaining **Partition Tolerance**. Importantly, in practical distributed systems partition tolerance is not optional — you must assume partitions can happen — so the real trade-off under partition is between C and A.
### Requirements
- Functional:
  - Serve reads and writes across distributed nodes.
  - Replicate data across nodes/data centers.
- Non-functional:
  - Partition tolerance (P) as a baseline requirement.
  - Targeted consistency and availability guarantees per use case.
  - Predictable behavior under failures (clear CP vs AP trade-offs).
### Architecture (CAP-level view)
At a high level, distributed architectures make the following choices:
- Data replication across multiple nodes or data centers.
- Coordination/consensus mechanisms (e.g., leader election, Paxos/Raft, quorums) for CP-style systems.
- Eventual consistency and conflict-resolution mechanisms for AP-style systems.
- Tunable per-request consistency in hybrid systems.
**Three Guarantees:**
- **Consistency (C)** — every read sees the result of the latest completed write (linearizability). All nodes observe data as if the system ran on a single machine.
- **Availability (A)** — every request to a non-failing node receives a non-error response within a reasonable time. The system continues serving requests under partial failures.
- **Partition Tolerance (P)** — the system continues to operate correctly in the presence of network partitions: nodes may not be able to communicate, yet the system still processes requests subject to its chosen C/A trade-off.
**Why you cannot have all three during a partition:**
Network partitions, delays, and packet loss are unavoidable. When a partition occurs, the system must choose:
- to reject or block some operations to avoid violating consistency (sacrificing availability), or
- to accept operations independently in different partitions, allowing temporary inconsistency (sacrificing strong consistency).
You cannot simultaneously guarantee both strong consistency and full availability for all requests in the face of an actual network partition.
**CP Systems (Consistency + Partition Tolerance):**
*Theory:* CP systems, under partitions, favor strong consistency over availability. When nodes cannot communicate, operations that cannot be safely committed are blocked or failed. They often rely on consensus algorithms (Paxos, Raft) for coordination. This approach is common where incorrect data is worse than temporary unavailability.
*Examples (by behavior/configuration):* MongoDB clusters configured with majority write concern and appropriate read concern, HBase, ZooKeeper, etcd, Consul, and other Raft/Paxos-based transactional stores. Some Redis setups (e.g., using `WAIT` and strict configuration) can behave closer to CP, but Redis in distributed/replicated mode does not provide full CP guarantees by default.
*Use cases:* Bank transfers, balance and inventory management, booking systems, medical records.
```kotlin
// Conceptual CP-style behavior:
// On partition, the cluster may block or fail operations
// if it cannot safely reach consensus (sacrificing availability for consistency).
database.transaction {
    val account = database.getAccount(id) // May block or fail on partition
    database.updateBalance(id, newBalance) // Ensures a consistent (e.g. ACID/linearizable) state
}
```
**AP Systems (Availability + Partition Tolerance):**
*Theory:* AP systems prioritize high availability under partitions. Nodes in different partitions continue accepting requests independently, which may cause temporary inconsistencies between replicas. They typically use eventual consistency: if no new updates occur, all replicas converge to a consistent state over time. Conflict resolution mechanisms (Last-Write-Wins, version vectors, CRDTs, etc.) are applied.
*Examples (by model):* Cassandra, Riak, CouchDB, many Dynamo-style systems; certain modes of Amazon DynamoDB. DNS in practice also exhibits AP-like behavior.
*Use cases:* Social networks, product catalogs, logging, analytics, view counters.
```kotlin
// Conceptual AP-style behavior:
// Operations are accepted locally even under suspected partitions;
// reads may return stale data until replicas converge.
database.incrementLikes(postId) // Aims to succeed even with network issues
val likes = database.getLikes(postId) // May be slightly stale
```
**Conflict Resolution in AP Systems:**
*Theory:* Under partitions, different nodes may accept conflicting updates for the same item. Once connectivity is restored, the system must detect and resolve conflicts in a way that ensures convergence.
*Strategies:*
- **Last-Write-Wins (LWW)** — the value with the latest timestamp wins. Simple but can discard concurrent updates.
- **Version Vectors** — track causal relationships between versions; allow detection of conflicts and resolution by application logic or merge functions.
- **CRDTs** — specially designed data structures that provably converge under concurrent, out-of-order, and duplicated updates without centralized coordination.
```kotlin
// Simplified G-Counter CRDT: monotonic increments and commutative merge
class GCounter {
    private val counters = mutableMapOf<NodeId, Long>()
    fun increment(nodeId: NodeId) {
        counters[nodeId] = (counters[nodeId] ?: 0L) + 1L
    }
    fun value(): Long = counters.values.sum()
    fun merge(other: GCounter): GCounter {
        val result = GCounter()
        (counters.keys + other.counters.keys).forEach { nodeId ->
            val thisVal = this.counters[nodeId] ?: 0L
            val otherVal = other.counters[nodeId] ?: 0L
            result.counters[nodeId] = maxOf(thisVal, otherVal)
        }
        return result
    }
}
```
**Consistency Models:**
*Theory:* There is a spectrum of consistency models between strong and weak guarantees. These refine the coarse CAP classification.
- **Strong consistency (linearizability)** — the strongest guarantee; every operation appears instantaneous at some point between its call and return in a single global order.
- **Sequential consistency** — there exists a total order of operations consistent with each client's program order, but it may not reflect real-time order.
- **Causal consistency** — preserves cause-effect relationships: if A causally influences B, all nodes observe A no later than B.
- **Eventual consistency** — if no new updates occur, all replicas eventually converge to the same value; intermediate states and ordering are unconstrained.
**Tunable Consistency:**
*Theory:* Some systems (e.g., Cassandra, Dynamo-style databases) support per-request consistency levels. By using quorums (`R + W > N`), you can obtain stronger guarantees (such as read-your-writes and, in some configurations, effectively linearizable operations). However, this does not make the system purely CP in CAP terms: under real partitions it still must choose whether to fail some operations (leaning CP) or accept them and reconcile later (leaning AP).
```kotlin
// Per-request tuning:
// stronger (quorum) consistency for critical operations,
// weaker consistency for latency/availability-sensitive ones.
criticalRead(id, ConsistencyLevel.QUORUM) // Stronger, quorum-based consistency
casualRead(id, ConsistencyLevel.ONE) // Higher availability, eventual consistency
```
## Дополнительные Вопросы (RU)
- В чем отличие строгой консистентности от eventual consistency?
- Как теорема PACELC дополняет CAP?
- Объясните различные стратегии разрешения конфликтов в AP-системах.
## Связанные Вопросы (RU)
### База (проще)
- [[q-caching-strategies--system-design--medium]] - Основы кэширования
- [[q-load-balancing-strategies--system-design--medium]] - Балансировка нагрузки
### Смежные (тот Же уровень)
- [[q-horizontal-vertical-scaling--system-design--medium]] - Стратегии масштабирования
- [[q-message-queues-event-driven--system-design--medium]] - Очереди сообщений и событийные системы
### Продвинутые (сложнее)
- [[q-microservices-vs-monolith--system-design--hard]] - Архитектурные подходы
- [[q-database-sharding-partitioning--system-design--hard]] - Масштабирование баз данных