---
id: sysdes-002
title: "SQL vs NoSQL Databases / SQL vs NoSQL базы данных"
aliases: ["SQL vs NoSQL базы данных", "SQL vs NoSQL"]
topic: system-design
subtopics: [data-modeling, databases, nosql, scalability, sql]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-databases, q-cap-theorem-distributed-systems--system-design--hard, q-database-sharding-partitioning--system-design--hard]
created: 2025-10-12
updated: 2025-01-25
tags: [databases, difficulty/medium, nosql, scalability, sql, system-design]
sources: [https://en.wikipedia.org/wiki/NoSQL]
date created: Sunday, October 12th 2025, 8:29:41 pm
date modified: Saturday, October 25th 2025, 8:32:44 pm
---

# Вопрос (RU)
> Каковы ключевые различия между SQL и NoSQL базами данных? Когда следует использовать каждый тип, и каковы компромиссы?

# Question (EN)
> What are the key differences between SQL and NoSQL databases? When should you use each type, and what are the trade-offs?

---

## Ответ (RU)

**Теория баз данных:**
Выбор между SQL и NoSQL - одно из важнейших решений в system design. SQL (реляционные БД) обеспечивают ACID транзакции и strong consistency, но сложнее масштабируются горизонтально. NoSQL обеспечивают горизонтальное масштабирование и гибкую схему, но жертвуют консистентностью (eventual consistency).

**SQL (Реляционные) базы данных:**

*Теория:* Данные хранятся в таблицах с фиксированной схемой. Отношения между таблицами через foreign keys. ACID транзакции гарантируют strong consistency. Вертикальное масштабирование (scale up). SQL - стандартизированный язык запросов.

*Примеры:* PostgreSQL, MySQL, Oracle, SQL Server

*Ключевые характеристики:*
- **ACID транзакции** (Atomicity, Consistency, Isolation, Durability)
- **Фиксированная схема** (schema-based)
- **Отношения** через foreign keys
- **JOINs** между таблицами
- **Strong consistency**
- **Вертикальное масштабирование**

*Сценарии использования:*
- Финансовые транзакции (банки, платежи)
- Inventory management (склад, товары)
- Booking systems (бронирования)
- ERP, CRM системы
- Когда нужны сложные JOINs
- Когда критична data integrity

```sql
-- SQL: E-commerce схема с отношениями
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),  -- Foreign key
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL
);

-- Complex JOIN query
SELECT u.name, o.id, o.total_amount
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.created_at > NOW() - INTERVAL '30 days';
```

**ACID транзакции:**

*Теория:* ACID гарантирует надёжность транзакций. Atomicity - всё или ничего. Consistency - БД всегда в валидном состоянии. Isolation - транзакции не видят промежуточные состояния друг друга. Durability - committed данные сохранены навсегда.

```kotlin
// ACID транзакция: перевод денег
@Transactional
fun transfer(fromAccount: Long, toAccount: Long, amount: BigDecimal) {
    // Atomicity: всё или ничего
    accountRepo.debit(fromAccount, amount)  // -100
    accountRepo.credit(toAccount, amount)   // +100
    // Если ошибка - rollback обеих операций
    // Consistency: constraints проверены
    // Isolation: другие транзакции не видят промежуточное состояние
    // Durability: после commit данные сохранены
}
```

**NoSQL базы данных:**

*Теория:* Гибкая схема (schema-less), горизонтальное масштабирование (scale out), eventual consistency. Четыре основных типа: Document (MongoDB), Key-Value (Redis), Column-Family (Cassandra), Graph (Neo4j). Жертвуют консистентностью ради availability и partition tolerance (CAP theorem).

**1. Document Stores (MongoDB, CouchDB):**

*Теория:* Хранят JSON-подобные документы. Гибкая схема - каждый документ может иметь разные поля. Вложенные структуры данных. Денормализация вместо JOINs.

*Сценарии:* Content management, каталоги продуктов, user profiles, гибкие схемы

```javascript
// MongoDB: Document с вложенными данными
{
  "_id": "user123",
  "name": "John Doe",
  "email": "john@example.com",
  "orders": [  // Денормализация - вложенные заказы
    {
      "orderId": "order456",
      "total": 99.99,
      "items": [
        { "productId": "prod1", "quantity": 2, "price": 49.99 }
      ]
    }
  ]
}
// Нет JOINs - всё в одном документе
```

**2. Key-Value Stores (Redis, DynamoDB):**

*Теория:* Простейшая модель - ключ → значение. Очень быстрые операции (O(1)). Ограниченные возможности запросов (только по ключу). In-memory (Redis) для низкой latency.

*Сценарии:* Кеширование, session storage, rate limiting, real-time analytics

```kotlin
// Redis: Key-Value операции
redis.set("user:123:session", sessionData, ttl = 3600)  // O(1)
val session = redis.get("user:123:session")  // O(1)
redis.incr("api:rate-limit:user:123")  // Atomic counter
```

**3. Column-Family (Cassandra, HBase):**

*Теория:* Wide column storage. Оптимизированы для записи (write-heavy). Time-series данные. Горизонтальное масштабирование через partitioning. Eventual consistency.

*Сценарии:* Time-series data, IoT sensors, logs, analytics

```cql
-- Cassandra: Column-family для time-series
CREATE TABLE sensor_data (
    sensor_id UUID,
    timestamp TIMESTAMP,
    temperature DOUBLE,
    PRIMARY KEY (sensor_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
-- Оптимизировано для записи миллионов событий/сек
```

**4. Graph Databases (Neo4j, Amazon Neptune):**

*Теория:* Nodes (вершины) и relationships (рёбра). Оптимизированы для traversal (обход графа). Социальные сети, рекомендации, fraud detection.

*Сценарии:* Social networks, recommendation engines, knowledge graphs

```cypher
// Neo4j: Graph query
MATCH (user:User {id: 123})-[:FOLLOWS]->(friend)-[:LIKES]->(product)
WHERE NOT (user)-[:PURCHASED]->(product)
RETURN product
// Рекомендации на основе друзей
```

**Сравнительная таблица:**

| Характеристика | SQL | NoSQL |
|----------------|-----|-------|
| Схема | Фиксированная | Гибкая (schema-less) |
| Масштабирование | Вертикальное | Горизонтальное |
| Транзакции | ACID (strong) | BASE (eventual) |
| Отношения | Native (JOINs) | Денормализация |
| Язык запросов | SQL (стандарт) | Различные (API) |
| Консистентность | Strong | Eventual (tunable) |
| Производительность | Сложные запросы | Простые lookups |
| Сценарии | Финансы, ERP | Big data, real-time |

**CAP Theorem и консистентность:**

*Теория:* CAP theorem - невозможно одновременно гарантировать Consistency, Availability, Partition Tolerance. SQL выбирают CP (consistency + partition tolerance), жертвуя availability. NoSQL выбирают AP (availability + partition tolerance), жертвуя consistency.

**SQL (CP):**
- Strong consistency (все видят одни данные)
- Жертвуют availability при network partition
- Пример: PostgreSQL с синхронной репликацией

**NoSQL (AP):**
- Eventual consistency (данные в конце концов синхронизируются)
- Высокая availability даже при network partition
- Пример: Cassandra, DynamoDB

**Когда использовать SQL:**

✅ **Используйте SQL:**
- Финансовые транзакции (банки, платежи)
- Strong consistency критична
- Сложные отношения (много JOINs)
- ACID гарантии обязательны
- Фиксированная схема данных
- Ad-hoc queries и reporting
- Data integrity критична

**Когда использовать NoSQL:**

✅ **Используйте NoSQL:**
- Горизонтальное масштабирование нужно
- Гибкая схема (часто меняется)
- Eventual consistency приемлема
- Простые queries (по ключу)
- Высокая throughput (миллионы ops/sec)
- Big data, real-time analytics
- Денормализованные данные

**Гибридный подход:**

*Теория:* Многие системы используют оба типа. SQL для критичных транзакций, NoSQL для масштабируемых операций. Polyglot persistence - разные БД для разных задач.

```kotlin
// Гибридный подход
class OrderService(
    private val postgresRepo: PostgresOrderRepository,  // SQL для транзакций
    private val redisCache: RedisCache,                 // Redis для кеша
    private val mongoRepo: MongoProductRepository       // MongoDB для каталога
) {
    suspend fun createOrder(order: Order): Order {
        // 1. Проверить inventory в PostgreSQL (ACID)
        postgresRepo.checkInventory(order.items)

        // 2. Создать заказ в PostgreSQL (транзакция)
        val savedOrder = postgresRepo.save(order)

        // 3. Кешировать в Redis
        redisCache.set("order:${savedOrder.id}", savedOrder)

        // 4. Обновить аналитику в MongoDB
        mongoRepo.updateProductStats(order.items)

        return savedOrder
    }
}
```

## Answer (EN)

**Database Theory:**
Choosing between SQL and NoSQL is one of the most important decisions in system design. SQL (relational DBs) provide ACID transactions and strong consistency, but harder to scale horizontally. NoSQL provides horizontal scaling and flexible schema, but sacrifices consistency (eventual consistency).

**SQL (Relational) Databases:**

*Theory:* Data stored in tables with fixed schema. Relationships between tables via foreign keys. ACID transactions guarantee strong consistency. Vertical scaling (scale up). SQL - standardized query language.

*Examples:* PostgreSQL, MySQL, Oracle, SQL Server

*Key Characteristics:*
- **ACID transactions** (Atomicity, Consistency, Isolation, Durability)
- **Fixed schema** (schema-based)
- **Relationships** via foreign keys
- **JOINs** between tables
- **Strong consistency**
- **Vertical scaling**

*Use cases:*
- Financial transactions (banking, payments)
- Inventory management (warehouse, products)
- Booking systems (reservations)
- ERP, CRM systems
- When complex JOINs needed
- When data integrity critical

```sql
-- SQL: E-commerce schema with relationships
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),  -- Foreign key
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL
);

-- Complex JOIN query
SELECT u.name, o.id, o.total_amount
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.created_at > NOW() - INTERVAL '30 days';
```

**ACID Transactions:**

*Theory:* ACID guarantees transaction reliability. Atomicity - all or nothing. Consistency - DB always in valid state. Isolation - transactions don't see each other's intermediate states. Durability - committed data saved forever.

```kotlin
// ACID transaction: money transfer
@Transactional
fun transfer(fromAccount: Long, toAccount: Long, amount: BigDecimal) {
    // Atomicity: all or nothing
    accountRepo.debit(fromAccount, amount)  // -100
    accountRepo.credit(toAccount, amount)   // +100
    // If error - rollback both operations
    // Consistency: constraints checked
    // Isolation: other transactions don't see intermediate state
    // Durability: after commit data saved
}
```

**NoSQL Databases:**

*Theory:* Flexible schema (schema-less), horizontal scaling (scale out), eventual consistency. Four main types: Document (MongoDB), Key-Value (Redis), Column-Family (Cassandra), Graph (Neo4j). Sacrifice consistency for availability and partition tolerance (CAP theorem).

**1. Document Stores (MongoDB, CouchDB):**

*Theory:* Store JSON-like documents. Flexible schema - each document can have different fields. Nested data structures. Denormalization instead of JOINs.

*Use cases:* Content management, product catalogs, user profiles, flexible schemas

```javascript
// MongoDB: Document with nested data
{
  "_id": "user123",
  "name": "John Doe",
  "email": "john@example.com",
  "orders": [  // Denormalization - nested orders
    {
      "orderId": "order456",
      "total": 99.99,
      "items": [
        { "productId": "prod1", "quantity": 2, "price": 49.99 }
      ]
    }
  ]
}
// No JOINs - everything in one document
```

**2. Key-Value Stores (Redis, DynamoDB):**

*Theory:* Simplest model - key → value. Very fast operations (O(1)). Limited query capabilities (only by key). In-memory (Redis) for low latency.

*Use cases:* Caching, session storage, rate limiting, real-time analytics

```kotlin
// Redis: Key-Value operations
redis.set("user:123:session", sessionData, ttl = 3600)  // O(1)
val session = redis.get("user:123:session")  // O(1)
redis.incr("api:rate-limit:user:123")  // Atomic counter
```

**3. Column-Family (Cassandra, HBase):**

*Theory:* Wide column storage. Optimized for writes (write-heavy). Time-series data. Horizontal scaling via partitioning. Eventual consistency.

*Use cases:* Time-series data, IoT sensors, logs, analytics

```cql
-- Cassandra: Column-family for time-series
CREATE TABLE sensor_data (
    sensor_id UUID,
    timestamp TIMESTAMP,
    temperature DOUBLE,
    PRIMARY KEY (sensor_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
-- Optimized for writing millions events/sec
```

**4. Graph Databases (Neo4j, Amazon Neptune):**

*Theory:* Nodes (vertices) and relationships (edges). Optimized for traversal (graph traversal). Social networks, recommendations, fraud detection.

*Use cases:* Social networks, recommendation engines, knowledge graphs

```cypher
// Neo4j: Graph query
MATCH (user:User {id: 123})-[:FOLLOWS]->(friend)-[:LIKES]->(product)
WHERE NOT (user)-[:PURCHASED]->(product)
RETURN product
// Recommendations based on friends
```

**Comparison Table:**

| Characteristic | SQL | NoSQL |
|----------------|-----|-------|
| Schema | Fixed | Flexible (schema-less) |
| Scaling | Vertical | Horizontal |
| Transactions | ACID (strong) | BASE (eventual) |
| Relationships | Native (JOINs) | Denormalization |
| Query Language | SQL (standard) | Various (API) |
| Consistency | Strong | Eventual (tunable) |
| Performance | Complex queries | Simple lookups |
| Use Cases | Finance, ERP | Big data, real-time |

**CAP Theorem and Consistency:**

*Theory:* CAP theorem - impossible to simultaneously guarantee Consistency, Availability, Partition Tolerance. SQL chooses CP (consistency + partition tolerance), sacrificing availability. NoSQL chooses AP (availability + partition tolerance), sacrificing consistency.

**SQL (CP):**
- Strong consistency (everyone sees same data)
- Sacrifice availability during network partition
- Example: PostgreSQL with synchronous replication

**NoSQL (AP):**
- Eventual consistency (data eventually synchronized)
- High availability even during network partition
- Example: Cassandra, DynamoDB

**When to Use SQL:**

✅ **Use SQL:**
- Financial transactions (banking, payments)
- Strong consistency critical
- Complex relationships (many JOINs)
- ACID guarantees mandatory
- Fixed data schema
- Ad-hoc queries and reporting
- Data integrity critical

**When to Use NoSQL:**

✅ **Use NoSQL:**
- Horizontal scaling needed
- Flexible schema (frequently changes)
- Eventual consistency acceptable
- Simple queries (by key)
- High throughput (millions ops/sec)
- Big data, real-time analytics
- Denormalized data

**Hybrid Approach:**

*Theory:* Many systems use both types. SQL for critical transactions, NoSQL for scalable operations. Polyglot persistence - different DBs for different tasks.

```kotlin
// Hybrid approach
class OrderService(
    private val postgresRepo: PostgresOrderRepository,  // SQL for transactions
    private val redisCache: RedisCache,                 // Redis for cache
    private val mongoRepo: MongoProductRepository       // MongoDB for catalog
) {
    suspend fun createOrder(order: Order): Order {
        // 1. Check inventory in PostgreSQL (ACID)
        postgresRepo.checkInventory(order.items)

        // 2. Create order in PostgreSQL (transaction)
        val savedOrder = postgresRepo.save(order)

        // 3. Cache in Redis
        redisCache.set("order:${savedOrder.id}", savedOrder)

        // 4. Update analytics in MongoDB
        mongoRepo.updateProductStats(order.items)

        return savedOrder
    }
}
```

---

## Follow-ups

- How do you handle eventual consistency in NoSQL?
- What is the difference between normalization and denormalization?
- How do you choose between different NoSQL types?

## Related Questions

### Prerequisites (Easier)
- [[q-caching-strategies--system-design--medium]] - Caching patterns
- [[q-horizontal-vertical-scaling--system-design--medium]] - Scaling strategies

### Related (Same Level)
- [[q-rest-api-design-best-practices--system-design--medium]] - API design
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Data distribution
- [[q-cap-theorem-distributed-systems--system-design--hard]] - CAP theorem
