---
id: sysdes-010
title: "Database Sharding and Partitioning / Шардирование и партиционирование баз данных"
aliases: ["Database Sharding", "Шардирование баз данных"]
topic: system-design
subtopics: [database, partitioning, scalability, sharding]
question_kind: system-design
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-database-sharding, q-cap-theorem-distributed-systems--system-design--hard, q-horizontal-vertical-scaling--system-design--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [database, difficulty/hard, partitioning, scalability, sharding, system-design]
sources: [https://en.wikipedia.org/wiki/Shard_(database_architecture)]
date created: Sunday, October 12th 2025, 8:44:15 pm
date modified: Saturday, October 25th 2025, 8:03:01 pm
---

# Вопрос (RU)
> Что такое шардирование базы данных? Чем оно отличается от партиционирования? Каковы стратегии шардирования и какие компромиссы?

# Question (EN)
> What is database sharding? How is it different from partitioning? What are the sharding strategies, and what are the trade-offs?

---

## Ответ (RU)

**Теория шардирования и партиционирования:**
Шардирование и партиционирование - техники горизонтального масштабирования баз данных путём распределения данных. Партиционирование разделяет данные на одном сервере, шардирование - по нескольким серверам.

**Ключевое различие:**
- **Партиционирование** - разделение большой таблицы на меньшие части на **одном сервере** (вертикальное масштабирование)
- **Шардирование** - разделение данных по **нескольким серверам** (горизонтальное масштабирование)

**Стратегии партиционирования:**

*1. Range Partitioning (по диапазону):*
```sql
-- Разделение по диапазону дат
CREATE TABLE orders PARTITION BY RANGE (created_at);
CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```
*Теория:* Данные разделяются по диапазонам значений (дата, ID). Хорошо для time-series данных. Минус: возможны hotspots (новые данные получают все записи).

*2. Hash Partitioning (по хешу):*
```sql
-- Равномерное распределение по хешу
CREATE TABLE users PARTITION BY HASH (user_id);
CREATE TABLE users_0 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
```
*Теория:* Хеш-функция равномерно распределяет данные. Нет hotspots, но range-запросы сканируют все партиции. Сложно добавлять партиции (требуется rehashing).

*3. List Partitioning (по списку):*
```sql
-- Разделение по дискретным значениям
CREATE TABLE products PARTITION BY LIST (category);
CREATE TABLE products_electronics PARTITION OF products
    FOR VALUES IN ('electronics', 'computers');
```
*Теория:* Логическая группировка по категориям. Может быть неравномерное распределение.

**Стратегии шардирования:**

*1. Range-Based Sharding:*
```kotlin
// Распределение по диапазону ID
fun getShard(userId: Long): DataSource {
    return when {
        userId < 1000000 -> shard1
        userId < 2000000 -> shard2
        else -> shard3
    }
}
```
*Теория:* Простая реализация, хорошо для range-запросов. Минус: неравномерная нагрузка, hotspots на новых данных.

*2. Hash-Based Sharding:*
```kotlin
// Равномерное распределение по хешу
fun getShard(userId: Long): DataSource {
    val shardId = userId.hashCode() % shards.size
    return shards[shardId]
}
```
*Теория:* Равномерное распределение, нет hotspots. Минус: сложное решардирование (rehashing всех данных).

*3. Consistent Hashing:*
```kotlin
// Минимальное перемещение данных при добавлении шардов
class ConsistentHashRouter {
    private val ring = TreeMap<Int, DataSource>()

    fun getShard(key: String): DataSource {
        val hash = key.hashCode()
        return ring.ceilingEntry(hash)?.value ?: ring.firstEntry().value
    }
}
```
*Теория:* При добавлении/удалении шарда перемещается только K/N данных (K - ключи, N - шарды). Используется в Cassandra, DynamoDB. Минус: сложность реализации.

*4. Geographic Sharding:*
```kotlin
// Разделение по географии для низкой задержки
fun getShard(userId: Long): DataSource {
    val region = getUserRegion(userId)
    return when (region) {
        "US" -> usaShard
        "EU" -> europeShard
        "ASIA" -> asiaShard
    }
}
```
*Теория:* Данные хранятся близко к пользователям. Низкая задержка, соответствие законам (GDPR). Минус: неравномерная нагрузка между регионами.

**Проблемы шардирования:**

*1. Cross-Shard Joins:*
```kotlin
// Проблема: Данные на разных шардах
val user = shard1.getUser(userId)
val orders = shard2.getOrders(userId) // Другой шард!
```
*Решение:* Денормализация, дублирование данных, application-level joins.

*2. Распределённые транзакции:*
*Решение:* Saga pattern, eventual consistency, избегать cross-shard транзакций.

*3. Генерация уникальных ID:*
*Решение:* UUID, Snowflake ID (Twitter), database sequences per shard.

*4. Решардирование:*
*Решение:* Логические шарды (больше логических, чем физических), consistent hashing, двойная запись во время миграции.

## Answer (EN)

**Sharding and Partitioning Theory:**
Sharding and partitioning are horizontal database scaling techniques through data distribution. Partitioning splits data on one server, sharding across multiple servers.

**Key Difference:**
- **Partitioning** - splitting large table into smaller pieces on **one server** (vertical scaling)
- **Sharding** - splitting data across **multiple servers** (horizontal scaling)

**Partitioning Strategies:**

*1. Range Partitioning:*
```sql
-- Split by date range
CREATE TABLE orders PARTITION BY RANGE (created_at);
CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```
*Theory:* Data split by value ranges (date, ID). Good for time-series data. Downside: possible hotspots (recent data gets all writes).

*2. Hash Partitioning:*
```sql
-- Even distribution by hash
CREATE TABLE users PARTITION BY HASH (user_id);
CREATE TABLE users_0 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
```
*Theory:* Hash function distributes data evenly. No hotspots, but range queries scan all partitions. Hard to add partitions (requires rehashing).

*3. List Partitioning:*
```sql
-- Split by discrete values
CREATE TABLE products PARTITION BY LIST (category);
CREATE TABLE products_electronics PARTITION OF products
    FOR VALUES IN ('electronics', 'computers');
```
*Theory:* Logical grouping by categories. May have uneven distribution.

**Sharding Strategies:**

*1. Range-Based Sharding:*
```kotlin
// Distribution by ID range
fun getShard(userId: Long): DataSource {
    return when {
        userId < 1000000 -> shard1
        userId < 2000000 -> shard2
        else -> shard3
    }
}
```
*Theory:* Simple implementation, good for range queries. Downside: uneven load, hotspots on new data.

*2. Hash-Based Sharding:*
```kotlin
// Even distribution by hash
fun getShard(userId: Long): DataSource {
    val shardId = userId.hashCode() % shards.size
    return shards[shardId]
}
```
*Theory:* Even distribution, no hotspots. Downside: complex resharding (rehashing all data).

*3. Consistent Hashing:*
```kotlin
// Minimal data movement when adding shards
class ConsistentHashRouter {
    private val ring = TreeMap<Int, DataSource>()

    fun getShard(key: String): DataSource {
        val hash = key.hashCode()
        return ring.ceilingEntry(hash)?.value ?: ring.firstEntry().value
    }
}
```
*Theory:* When adding/removing shard, only K/N data moves (K - keys, N - shards). Used in Cassandra, DynamoDB. Downside: implementation complexity.

*4. Geographic Sharding:*
```kotlin
// Split by geography for low latency
fun getShard(userId: Long): DataSource {
    val region = getUserRegion(userId)
    return when (region) {
        "US" -> usaShard
        "EU" -> europeShard
        "ASIA" -> asiaShard
    }
}
```
*Theory:* Data stored close to users. Low latency, compliance with laws (GDPR). Downside: uneven load between regions.

**Sharding Challenges:**

*1. Cross-Shard Joins:*
```kotlin
// Problem: Data on different shards
val user = shard1.getUser(userId)
val orders = shard2.getOrders(userId) // Different shard!
```
*Solution:* Denormalization, data duplication, application-level joins.

*2. Distributed Transactions:*
*Solution:* Saga pattern, eventual consistency, avoid cross-shard transactions.

*3. Unique ID Generation:*
*Solution:* UUID, Snowflake ID (Twitter), database sequences per shard.

*4. Resharding:*
*Solution:* Logical shards (more logical than physical), consistent hashing, double-write during migration.

---

## Follow-ups

- What is the difference between logical and physical sharding?
- How do you handle shard rebalancing with zero downtime?
- What are the strategies for global secondary indexes in sharded databases?

## Related Questions

### Prerequisites (Easier)
- [[q-sql-nosql-databases--system-design--medium]] - Database fundamentals
- [[q-caching-strategies--system-design--medium]] - Caching strategies

### Related (Same Level)
- [[q-horizontal-vertical-scaling--system-design--medium]] - Scaling strategies
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing

### Advanced (Harder)
- [[q-cap-theorem-distributed-systems--system-design--hard]] - CAP theorem
- [[q-microservices-vs-monolith--system-design--hard]] - Architecture patterns
