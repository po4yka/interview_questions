---
id: sysdes-010
title: Database Sharding and Partitioning / Шардирование и партиционирование баз данных
aliases:
- Database Sharding
- Шардирование баз данных
topic: system-design
subtopics:
- partitioning
- scalability
- sharding
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
- q-cap-theorem-distributed-systems--system-design--hard
- q-horizontal-vertical-scaling--system-design--medium
created: 2025-10-12
updated: 2025-11-11
tags:
- database
- difficulty/hard
- partitioning
- scalability
- sharding
- system-design
sources:
- https://en.wikipedia.org/wiki/Shard_(database_architecture)
anki_cards:
- slug: sysdes-010-0-en
  language: en
  anki_id: 1768468551959
  synced_at: '2026-01-23T13:49:17.851620'
- slug: sysdes-010-0-ru
  language: ru
  anki_id: 1768468551984
  synced_at: '2026-01-23T13:49:17.852444'
---
# Вопрос (RU)
> Что такое шардирование базы данных? Чем оно отличается от партиционирования? Каковы стратегии шардирования и какие компромиссы?

# Question (EN)
> What is database sharding? How is it different from partitioning? What are the sharding strategies, and what are the trade-offs?

---

## Ответ (RU)

Шардирование и партиционирование — это техники горизонтального разделения данных для масштабирования, производительности и управляемости. Важно понимать отличие логического партиционирования внутри одного кластера от распределения данных по независимым шардам, а также типичные стратегии (range, hash, list, географическое, consistent hashing) и их компромиссы: сложность маршрутизации запросов, кросс-шардовые операции, консистентность и решардирование. См. также [[c-architecture-patterns]].

## Answer (EN)

Sharding and partitioning are horizontal data-splitting techniques used to improve scalability, performance, and operability. It is crucial to distinguish logical partitioning within a single cluster from distributing data across independent shards, and to understand common strategies (range, hash, list, geographic, consistent hashing) and their trade-offs: routing complexity, cross-shard operations, consistency challenges, and resharding. See also [[c-architecture-patterns]].

## Follow-ups

- What is the difference between logical and physical sharding?
- How do you handle shard rebalancing with zero downtime?
- What are the strategies for global secondary indexes in sharded databases?

## References

- [[q-horizontal-vertical-scaling--system-design--medium]]
- [[q-cap-theorem-distributed-systems--system-design--hard]]
- "https://en.wikipedia.org/wiki/Shard_(database_architecture)"

## Related Questions

### Prerequisites (Easier)
- [[q-sql-nosql-databases--system-design--medium]] - `Database` fundamentals
- [[q-caching-strategies--system-design--medium]] - Caching strategies

### Related (Same Level)
- [[q-horizontal-vertical-scaling--system-design--medium]] - Scaling strategies
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing

### Advanced (Harder)
- [[q-cap-theorem-distributed-systems--system-design--hard]] - CAP theorem
- [[q-microservices-vs-monolith--system-design--hard]] - Architecture patterns

## Краткая Версия
Шардирование и партиционирование — это горизонтальное разделение данных для масштабирования и производительности.
- Партиционирование: логическое дробление таблиц/индексов внутри одного кластера/СУБД.
- Шардирование: распределение данных по независимым кластерам/шардам.
Компромисс: выигрыш в масштабируемости и отказоустойчивости в обмен на сложность маршрутизации запросов, кросс-шардовые операции, консистентность и решардирование. См. также [[q-horizontal-vertical-scaling--system-design--medium]] и [[q-cap-theorem-distributed-systems--system-design--hard]].

## Подробная Версия
**Теория шардирования и партиционирования:**
Шардирование и партиционирование — техники горизонтального масштабирования баз данных путём распределения данных. Партиционирование обычно реализуется на уровне одной логической базы/кластера (часто на одном сервере или в рамках одного узла СУБД), шардирование — распределяет данные по независимым серверам/кластерам.

**Ключевое различие:**
- **Партиционирование** — логическое разделение большой таблицы (или индекса) на меньшие части в рамках одной СУБД/кластера. Это форма горизонтального разделения данных, которая сама по себе не требует нескольких независимых серверов.
- **Шардирование** — распределение данных по нескольким независимым серверам/кластерам (шардам), каждый из которых хранит только подмножество данных. Это горизонтальное масштабирование за счёт увеличения числа узлов.

### Требования
- Функциональные:
  - Масштабировать объём данных и количество запросов за счёт горизонтального разделения.
  - Обеспечить маршрутизацию запросов к правильному партициону/шарду.
- Нефункциональные:
  - Высокая доступность и отказоустойчивость (failover между шардами/нодами).
  - Предсказуемая производительность и снижение hotspots.
  - Возможность решардирования с минимальным downtime.
  - Соблюдение требований по данным (например, геолокация).

### Архитектура
- Router / Query Router или сервис, знающий схему шардирования.
- Набор шардов (кластеры БД), каждый отвечает за свой диапазон/хеш/регион.
- Возможные вспомогательные компоненты:
  - Сервис метаданных о шардах.
  - Механизм генерации глобально уникальных идентификаторов.
  - Репликация внутри каждого шарда для отказоустойчивости.

**Стратегии партиционирования:**
*1. Range Partitioning (по диапазону):*
```sql
-- Разделение по диапазону дат
CREATE TABLE orders PARTITION BY RANGE (created_at);
CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```
*Теория:* Данные разделяются по диапазонам значений (дата, ID). Хорошо для time-series данных и range-запросов по ключу. Минус: возможны hotspots (последние диапазоны получают большинство новых записей).

*2. Hash Partitioning (по хешу):*
```sql
-- Равномерное распределение по хешу
CREATE TABLE users PARTITION BY HASH (user_id);
CREATE TABLE users_0 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
```
*Теория:* Хеш-функция стремится равномерно распределить данные по партициям и тем самым уменьшить риск hotspots. Минусы: range-запросы могут сканировать все партиции; добавление партиций обычно требует перераспределения данных (rehashing).

*3. `List` Partitioning (по списку):*
```sql
-- Разделение по дискретным значениям
CREATE TABLE products PARTITION BY LIST (category);
CREATE TABLE products_electronics PARTITION OF products
    FOR VALUES IN ('electronics', 'computers');
```
*Теория:* Логическая группировка по категориям. Возможна неравномерная загрузка между партициями.

**Стратегии шардирования:**
*1. Range-Based Sharding:*
```kotlin
// Распределение по диапазону ID
fun getShard(userId: Long): DataSource {
    return when {
        userId < 1_000_000L -> shard1
        userId < 2_000_000L -> shard2
        else -> shard3
    }
}
```
*Теория:* Простая реализация, эффективна для range-запросов по ключу шардирования. Минусы: неравномерная нагрузка и hotspots на "горячих" диапазонах (например, новые ID).

*2. Hash-Based Sharding:*
```kotlin
// Равномерное распределение по хешу с нормализацией индекса
fun getShard(userId: Long): DataSource {
    val raw = userId.hashCode()
    val shardId = Math.floorMod(raw, shards.size)
    return shards[shardId]
}
```
*Теория:* Хеш-функция обычно обеспечивает более равномерное распределение и снижает риск hotspots по сравнению с range. Минус: сложное решардирование (требуется перераспределять значительную часть данных при изменении числа шардов).

*3. Consistent Hashing:*
```kotlin
// Минимальное перемещение данных при изменении числа шардов (упрощённый пример)
class ConsistentHashRouter {
    private val ring = java.util.TreeMap<Int, DataSource>()
    fun addShard(hash: Int, dataSource: DataSource) {
        ring[hash] = dataSource
    }
    fun getShard(key: String): DataSource {
        require(ring.isNotEmpty()) { "No shards configured" }
        val hash = key.hashCode()
        return ring.ceilingEntry(hash)?.value ?: ring.firstEntry().value
    }
}
```
*Теория:* При добавлении/удалении шарда перераспределяется только примерно 1/N ключей (где N — количество шардов), а не почти все данные, как при простом хешировании. Используется в таких системах, как Cassandra, Dynamo-подобные системы. Минус: повышенная сложность реализации и необходимости виртуальных узлов для равномерного распределения.

*4. Geographic Sharding:*
```kotlin
// Разделение по географии для снижения задержки
fun getShard(userId: Long): DataSource {
    val region = getUserRegion(userId)
    return when (region) {
        "US" -> usaShard
        "EU" -> europeShard
        "ASIA" -> asiaShard
        else -> defaultShard
    }
}
```
*Теория:* Данные хранятся ближе к пользователям. Плюсы: низкая задержка, соответствие требованиям законодательства (например, GDPR). Минусы: неравномерная нагрузка между регионами, усложнение глобальных запросов и согласованности.

**Проблемы шардирования:**
*1. Cross-Shard Joins:*
```kotlin
// Проблема: данные на разных шардах
val user = shard1.getUser(userId)
val orders = shard2.getOrders(userId) // Другой шард!
```
*Решение:* Денормализация, дублирование данных, application-level joins, продуманный выбор ключей шардирования для минимизации cross-shard операций.

*2. Распределённые транзакции:*
*Решение:* Шаблоны типа Saga, eventual consistency, минимизация или избегание cross-shard транзакций, использование idempotent-операций.

*3. Генерация уникальных ID:*
*Решение:* UUID, Snowflake-подобные ID (Twitter), sequences/hi-lo per shard, time-based или комбинированные схемы, гарантирующие уникальность без глобальной блокировки.

*4. Решардирование:*
*Решение:* Логические шарды (больше логических, чем физических), consistent hashing, двойная запись во время миграции, постепенное перетаскивание диапазонов.

## Short Version
Sharding and partitioning are horizontal data-splitting techniques for scale and performance.
- Partitioning: logical splitting of tables/indexes within a single database/cluster.
- Sharding: distribution of data across independent database clusters/shards.
Trade-offs: better scalability and availability at the cost of routing complexity, cross-shard operations, consistency challenges, and resharding complexity. See also [[q-horizontal-vertical-scaling--system-design--medium]] and [[q-cap-theorem-distributed-systems--system-design--hard]].

## Detailed Version
**Sharding and Partitioning Theory:**
Sharding and partitioning are horizontal data distribution techniques used for scaling databases. Partitioning is typically implemented within a single logical database/cluster (often on a single server or DBMS node), while sharding distributes data across independent servers/clusters.

**Key Difference:**
- **Partitioning** - logical splitting of a large table (or index) into smaller parts within a single DBMS/cluster. It is a form of horizontal partitioning that does not inherently require multiple independent servers.
- **Sharding** - splitting data across multiple independent servers/clusters (shards), each holding only a subset of the data. This is horizontal scaling by adding more nodes.

### Requirements
- Functional:
  - Scale read/write throughput and data volume via horizontal splitting.
  - Correctly route queries to the right partition/shard.
- Non-functional:
  - High availability and fault tolerance (replication within shards/nodes).
  - Predictable performance and hotspot mitigation.
  - Ability to reshard with minimal downtime.
  - Compliance with data locality/regulation constraints.

### Architecture
- Router / query router or service that knows sharding/partitioning rules.
- `Set` of shards (DB clusters), each responsible for its range/hash/region.
- Optional components:
  - Metadata service describing shard ownership and placement.
  - Global unique ID generation mechanism.
  - Replication within each shard for durability and availability.

**Partitioning Strategies:**
*1. Range Partitioning:*
```sql
-- Split by date range
CREATE TABLE orders PARTITION BY RANGE (created_at);
CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```
*Theory:* Data is split by value ranges (date, ID). Good for time-series data and range queries on the partition key. Downside: potential hotspots when recent ranges receive most new writes.

*2. Hash Partitioning:*
```sql
-- Even distribution by hash
CREATE TABLE users PARTITION BY HASH (user_id);
CREATE TABLE users_0 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
```
*Theory:* The hash function aims to distribute data evenly across partitions, reducing hotspot risk. Downsides: range queries may need to scan all partitions; adding partitions usually requires data redistribution (rehashing).

*3. `List` Partitioning:*
```sql
-- Split by discrete values
CREATE TABLE products PARTITION BY LIST (category);
CREATE TABLE products_electronics PARTITION OF products
    FOR VALUES IN ('electronics', 'computers');
```
*Theory:* Logical grouping by categories. May lead to unbalanced load across partitions.

**Sharding Strategies:**
*1. Range-Based Sharding:*
```kotlin
// Distribution by ID range
fun getShard(userId: Long): DataSource {
    return when {
        userId < 1_000_000L -> shard1
        userId < 2_000_000L -> shard2
        else -> shard3
    }
}
```
*Theory:* Simple to implement, efficient for range queries on the shard key. Downsides: uneven load and hotspots on "hot" ranges (e.g., newest IDs).

*2. Hash-Based Sharding:*
```kotlin
// Even distribution by hash with index normalization
fun getShard(userId: Long): DataSource {
    val raw = userId.hashCode()
    val shardId = Math.floorMod(raw, shards.size)
    return shards[shardId]
}
```
*Theory:* Hash-based sharding usually yields more uniform distribution and lowers hotspot risk compared to pure range-based sharding. Downside: resharding is expensive since changing the number of shards requires moving a large portion of data.

*3. Consistent Hashing:*
```kotlin
// Minimal data movement when changing the number of shards (simplified example)
class ConsistentHashRouter {
    private val ring = java.util.TreeMap<Int, DataSource>()
    fun addShard(hash: Int, dataSource: DataSource) {
        ring[hash] = dataSource
    }
    fun getShard(key: String): DataSource {
        require(ring.isNotEmpty()) { "No shards configured" }
        val hash = key.hashCode()
        return ring.ceilingEntry(hash)?.value ?: ring.firstEntry().value
    }
}
```
*Theory:* When adding/removing a shard, only roughly 1/N of the keys (where N is the number of shards) need to move, instead of most keys as with simple hashing. Used in Cassandra and Dynamo-style systems. Downside: more complex implementation and need for virtual nodes to ensure balance.

*4. Geographic Sharding:*
```kotlin
// Split by geography for lower latency
fun getShard(userId: Long): DataSource {
    val region = getUserRegion(userId)
    return when (region) {
        "US" -> usaShard
        "EU" -> europeShard
        "ASIA" -> asiaShard
        else -> defaultShard
    }
}
```
*Theory:* Data is stored close to users. Pros: lower latency, regulatory compliance (e.g., GDPR). Cons: uneven regional load, more complex global queries and consistency.

**Sharding Challenges:**
*1. Cross-Shard Joins:*
```kotlin
// Problem: data on different shards
val user = shard1.getUser(userId)
val orders = shard2.getOrders(userId) // Different shard!
```
*Solution:* Denormalization, data duplication, application-level joins, and careful shard key design to minimize cross-shard operations.

*2. Distributed Transactions:*
*Solution:* Saga-like patterns, eventual consistency, minimizing or avoiding cross-shard transactions, using idempotent operations.

*3. Unique ID Generation:*
*Solution:* UUID, Snowflake-like IDs (Twitter), sequences/hi-lo per shard, time/segment-based schemes that ensure uniqueness without a single global bottleneck.

*4. Resharding:*
*Solution:* Logical shards (more logical than physical), consistent hashing, double-writing during migration, gradual range movement.
