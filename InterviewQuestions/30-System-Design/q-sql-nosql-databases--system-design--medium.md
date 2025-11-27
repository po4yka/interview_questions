---
id: sysdes-002
title: "SQL vs NoSQL Databases / SQL vs NoSQL базы данных"
aliases: ["SQL vs NoSQL базы данных", "SQL vs NoSQL"]
topic: system-design
subtopics: [data-modeling, nosql, scalability]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [q-cap-theorem-distributed-systems--system-design--hard, q-database-sharding-partitioning--system-design--hard]
created: 2025-10-12
updated: 2025-11-11
tags: [databases, difficulty/medium, nosql, scalability, sql, system-design]
sources: ["https://en.wikipedia.org/wiki/NoSQL"]

date created: Sunday, October 12th 2025, 8:29:41 pm
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---
# Вопрос (RU)
> Каковы ключевые различия между SQL и NoSQL базами данных? Когда следует использовать каждый тип, и каковы компромиссы?

# Question (EN)
> What are the key differences between SQL and NoSQL databases? When should you use each type, and what are the trade-offs?

---

## Ответ (RU)

### Требования

**Функциональные:**
- Хранение данных с различными моделями (табличная, документная, key-value, графовая и т.д.).
- Поддержка транзакций и операций чтения/записи под конкретные паттерны доступа.
- Возможность выбора подходящей модели данных под требования домена.

**Нефункциональные:**
- Масштабируемость (вертикальная и/или горизонтальная).
- Консистентность (strong/eventual/tunable) в зависимости от требований.
- Доступность и отказоустойчивость.
- Производительность под целевые нагрузки.

**Теория баз данных:**
Выбор между SQL и NoSQL — одно из важнейших решений в system design. SQL (реляционные БД) традиционно ассоциируются с ACID-транзакциями и сильной моделью консистентности, но их горизонтальное масштабирование сложнее и часто требует шардирования/репликации. Многие NoSQL-системы изначально спроектированы для горизонтального масштабирования и более гибкой схемы, часто используют eventual или настраиваемую консистентность, но конкретные гарантии зависят от движка и конфигурации. См. также [[q-cap-theorem-distributed-systems--system-design--hard]].

### Архитектура

На уровне архитектуры это обычно выглядит как выбор или комбинация:
- Реляционной БД (SQL) в качестве источника истины для критичных транзакционных данных.
- NoSQL-хранилищ для:
  - кеширования,
  - журналов событий и аналитики,
  - высоконагруженных чтений,
  - специфических моделей (графы, документо-ориентированное хранение).
- Polyglot persistence: использование нескольких хранилищ для разных частей системы с чётко определёнными границами и механизмами синхронизации.

**SQL (Реляционные) базы данных:**

*Теория:* Данные хранятся в таблицах с декларированной схемой. Отношения между таблицами через foreign keys. ACID-транзакции обеспечивают предсказуемое поведение и инварианты данных в рамках одной БД/кластера при корректной настройке. Масштабирование традиционно через вертикальный рост (scale up), но поддерживаются и механизмы партиционирования и репликации. SQL — стандартизированный язык запросов.

*Примеры:* PostgreSQL, MySQL, Oracle, SQL Server

*Ключевые характеристики:*
- **ACID транзакции** (Atomicity, Consistency, Isolation, Durability)
- **Чёткая схема** (schema-based)
- **Отношения** через foreign keys
- **JOINs** между таблицами
- Как правило, **сильная согласованность** в пределах одного узла/кластера при синхронной репликации
- Традиционно **вертикальное масштабирование**, с поддержкой шардирования/репликации для горизонтального масштабирования

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
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Complex JOIN query
SELECT u.name, o.id, o.total_amount
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.created_at > NOW() - INTERVAL '30 days';
```

**ACID транзакции:**

*Теория:* ACID гарантирует надёжность транзакций. Atomicity — всё или ничего. Consistency — БД переходит из одного валидного состояния в другое при соблюдении ограничений. Isolation — транзакции не видят неконсистентные промежуточные состояния друг друга (уровень изоляции настраивается). Durability — зафиксированные данные сохраняются даже при сбоях согласно настройке журнала/репликации.

```kotlin
// ACID транзакция: перевод денег
@Transactional
fun transfer(fromAccount: Long, toAccount: Long, amount: BigDecimal) {
    // Atomicity: всё или ничего
    accountRepo.debit(fromAccount, amount)  // -amount
    accountRepo.credit(toAccount, amount)   // +amount
    // В случае ошибки произойдёт rollback обеих операций
    // Consistency: проверяются constraints и инварианты
    // Isolation: другие транзакции не видят промежуточное состояние
    // Durability: после commit данные надёжно сохранены
}
```

**NoSQL базы данных:**

*Теория:* Общее название для нереляционных систем хранения данных. Часто предоставляют гибкую схему (schema-less или schema-on-read), проектируются для горизонтального масштабирования (scale out) и высокой доступности. Многие используют eventual или настраиваемую консистентность и ориентируются на BASE-принципы, однако конкретные гарантии (до уровня транзакций) зависят от типа и реализации.

Четыре распространённых типа: Document (MongoDB), Key-Value (Redis), Column-Family (Cassandra), Graph (Neo4j).

**1. Document Stores (MongoDB, CouchDB):**

*Теория:* Хранят JSON-подобные документы. Гибкая схема — документы одной коллекции могут иметь разные поля. Поддерживают вложенные структуры данных. Часто используется денормализация вместо JOINs.

*Сценарии:* Content management, каталоги продуктов, user profiles, гибкие схемы.

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
// Нет JOINs на уровне языка запросов - всё в одном документе
```

**2. Key-Value Stores (Redis, DynamoDB):**

*Теория:* Простейшая модель — ключ → значение. Для обычных операций чтения/записи по ключу обеспечивают очень низкую задержку, часто близкую к O(1) по времени, при этом детали зависят от структуры данных и реализации. Как правило, ограниченные возможности запросов (по ключу или небольшому набору предикатов). Redis обычно in-memory, DynamoDB — управляемое распределённое хранилище с возможностью выбора уровня консистентности (eventual или strongly consistent reads для отдельных операций).

*Сценарии:* Кеширование, session storage, rate limiting, real-time analytics.

```kotlin
// Redis: Key-Value операции
redis.set("user:123:session", sessionData, ttl = 3600)  // амортизированно O(1) для простой операции
val session = redis.get("user:123:session")              // амортизированно O(1)
redis.incr("api:rate-limit:user:123")                   // атомарный счётчик
```

**3. Column-Family (Cassandra, HBase):**

*Теория:* Wide-column хранилища. Оптимизированы для распределённых записей и чтения по ключам/диапазонам. Часто используются для time-series данных. Горизонтальное масштабирование через автоматическое партиционирование. Обычно предоставляют eventual или настраиваемую консистентность.

*Сценарии:* Time-series data, IoT sensors, logs, analytics.

```cql
-- Cassandra: Column-family для time-series
CREATE TABLE sensor_data (
    sensor_id UUID,
    timestamp TIMESTAMP,
    temperature DOUBLE,
    PRIMARY KEY (sensor_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
-- Оптимизировано для записи и чтения большого объёма событий
```

**4. Graph Databases (Neo4j, Amazon Neptune):**

*Теория:* Хранят данные в виде графа: nodes (вершины) и relationships (рёбра). Оптимизированы для обходов графа и запросов по связям.

*Сценарии:* Social networks, recommendation engines, knowledge graphs, fraud detection.

```cypher
// Neo4j: Graph query
MATCH (user:User {id: 123})-[:FOLLOWS]->(friend)-[:LIKES]->(product)
WHERE NOT (user)-[:PURCHASED]->(product)
RETURN product
// Рекомендации на основе интересов друзей
```

**Сравнительная таблица:**

| Характеристика | SQL | NoSQL |
|----------------|-----|-------|
| Схема | Фиксированная / чётко объявленная | Гибкая (schema-less / schema-on-read) |
| Масштабирование | Преимущественно вертикальное, возможно горизонтальное (шардинг, репликация) | Горизонтальное масштабирование как ключевая цель |
| Транзакции | Полноценные ACID (зависят от СУБД/настроек) | Часто ограниченные или локальные транзакции; BASE-подходы распространены |
| Отношения | Native (JOINs, внешние ключи) | Обычно через денормализацию или ссылочные поля на уровне приложения |
| Язык запросов | SQL (стандарт, вариации) | Различные: проприетарные языки, API |
| Консистентность | Обычно сильная в пределах узла/кластера при синхронной репликации | Часто eventual или настраиваемая (tunable) |
| Производительность | Сложные запросы и агрегаты, оптимизированные индексы | Простые lookups/записи на большом масштабе |
| Типичные сценарии | Транзакционные системы, финансы, ERP | Big data, высоконагруженные, распределённые и гибкие по схеме системы |

**CAP Theorem и консистентность:**

*Теория:* Теорема CAP: в условиях сетевого разделения (partition) система не может одновременно обеспечивать и строгую Consistency, и полную Availability — приходится выбирать между CP и AP. Классификация зависит от конкретной распределённой реализации и настроек.

**SQL (часто CP в распределённых конфигурациях):**
- При синхронной репликации и строгой консистентности могут жертвовать availability при сетевых проблемах
- Пример: кластер PostgreSQL с синхронной репликацией, где при потере связи часть узлов становится недоступной

**NoSQL (часто AP или tunable):**
- Многие системы обеспечивают high availability и partition tolerance, допускают eventual consistency
- Некоторые (например, Cassandra) позволяют настраивать уровень консистентности (tunable consistency)
- Управляемые сервисы вроде DynamoDB также предлагают выбор между eventual и strongly consistent чтениями

**Когда использовать SQL:**

✅ **Используйте SQL:**
- Финансовые транзакции (банки, платежи)
- Strong consistency критична
- Сложные отношения (много JOINs)
- ACID гарантии обязательны
- Схема данных относительно стабильна и чётко определена
- Нужны ad-hoc queries, аналитика и отчётность
- Data integrity критична

**Когда использовать NoSQL:**

✅ **Используйте NoSQL:**
- Нужен масштаб по горизонтали и распределённость по регионам
- Гибкая или быстро меняющаяся схема
- Приемлема eventual или настраиваемая консистентность
- Преобладают простые паттерны доступа (по ключу, по паре ключ-диапазон)
- Высокий throughput (сотни тысяч/миллионы ops/sec)
- Big data, real-time analytics
- Удобна денормализация и хранение агрегированных структур

**Гибридный подход:**

*Теория:* Многие системы используют оба типа. SQL — для критичных транзакций и строгой целостности, NoSQL — для высоконагруженных, кеширующих и аналитических сценариев. Подход polyglot persistence: разные БД для разных типов нагрузок.

```kotlin
// Гибридный подход
class OrderService(
    private val postgresRepo: PostgresOrderRepository,  // SQL для транзакций
    private val redisCache: RedisCache,                 // Redis для кеша
    private val mongoRepo: MongoProductRepository       // MongoDB для каталога/аналитики
) {
    suspend fun createOrder(order: Order): Order {
        // 1. Проверить inventory в PostgreSQL (ACID)
        postgresRepo.checkInventory(order.items)

        // 2. Создать заказ в PostgreSQL (транзакция)
        val savedOrder = postgresRepo.save(order)

        // 3. Кешировать в Redis
        redisCache.set("order:${'$'}{savedOrder.id}", savedOrder)

        // 4. Обновить аналитику / витрины в MongoDB
        mongoRepo.updateProductStats(order.items)

        return savedOrder
    }
}
```

## Answer (EN)

### Requirements

**Functional:**
- Support storing data in different models (relational tables, documents, key-value, graph, etc.).
- Provide transactions and read/write operations optimized for specific access patterns.
- Allow choosing the right data model for the domain requirements.

**Non-functional:**
- Scalability (vertical and/or horizontal).
- Consistency (strong/eventual/tunable) as required.
- High availability and fault tolerance.
- Performance suitable for target workloads.

**Database Theory:**
Choosing between SQL and NoSQL is one of the key decisions in system design. SQL (relational DBs) are traditionally associated with ACID transactions and strong consistency models, but horizontal scaling is more complex and usually involves sharding/replication. Many NoSQL systems are designed for horizontal scaling and flexible schemas, often use eventual or tunable consistency, but guarantees vary by engine and configuration. See also [[q-cap-theorem-distributed-systems--system-design--hard]].

### Architecture

At a high level, typical architectures use one or a combination of:
- A relational DB (SQL) as the source of truth for critical transactional data.
- NoSQL stores for:
  - caching,
  - event logs and analytics,
  - high-throughput reads,
  - specialized models (graphs, document stores, etc.).
- Polyglot persistence: multiple datastores for different workloads with clear boundaries and synchronization mechanisms.

**SQL (Relational) Databases:**

*Theory:* Data is stored in tables with a declared schema. Relationships between tables are expressed via foreign keys. ACID transactions provide predictable behavior and data invariants within a database/cluster when configured correctly. Scaling is traditionally vertical (scale up), with additional options like partitioning and replication for horizontal scaling. SQL is a standardized query language.

*Examples:* PostgreSQL, MySQL, Oracle, SQL Server

*Key Characteristics:*
- **ACID transactions** (Atomicity, Consistency, Isolation, Durability)
- **Well-defined schema** (schema-based)
- **Relationships** via foreign keys
- **JOINs** between tables
- Typically **strong consistency** within a node/cluster when using synchronous replication
- Traditionally **vertical scaling**, with sharding/replication available for horizontal scale

*Use cases:*
- Financial transactions (banking, payments)
- Inventory management (warehouse, products)
- Booking systems (reservations)
- ERP, CRM systems
- When complex JOINs are needed
- When data integrity is critical

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
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Complex JOIN query
SELECT u.name, o.id, o.total_amount
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.created_at > NOW() - INTERVAL '30 days';
```

**ACID Transactions:**

*Theory:* ACID guarantees transactional reliability. Atomicity - all or nothing. Consistency - moves the DB from one valid state to another while enforcing constraints. Isolation - transactions do not see each other's inconsistent intermediate states (isolation level is configurable). Durability - committed data is preserved even in the face of failures, according to logging/replication settings.

```kotlin
// ACID transaction: money transfer
@Transactional
fun transfer(fromAccount: Long, toAccount: Long, amount: BigDecimal) {
    // Atomicity: all or nothing
    accountRepo.debit(fromAccount, amount)  // -amount
    accountRepo.credit(toAccount, amount)   // +amount
    // On error, both operations are rolled back
    // Consistency: constraints and invariants are enforced
    // Isolation: other transactions don't see intermediate states
    // Durability: after commit, data is reliably stored
}
```

**NoSQL Databases:**

*Theory:* An umbrella term for non-relational data stores. Often provide flexible schemas (schema-less or schema-on-read), are built for horizontal scalability (scale out) and high availability. Many use eventual or tunable consistency and are inspired by BASE principles, but concrete guarantees (including transactional ones) depend heavily on the specific technology.

Four common categories: Document (MongoDB), Key-Value (Redis), Column-Family (Cassandra), Graph (Neo4j).

**1. Document Stores (MongoDB, CouchDB):**

*Theory:* Store JSON-like documents. Flexible schema - documents within a collection can have different fields. Support nested structures. Often rely on denormalization instead of JOINs.

*Use cases:* Content management, product catalogs, user profiles, flexible schemas.

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
// No JOINs in the query language here - everything in one document
```

**2. Key-Value Stores (Redis, DynamoDB):**

*Theory:* The simplest model - key → value. For basic key-based reads/writes they offer very low latency, typically close to O(1) time, though actual complexity depends on data structures and implementation. Query capabilities are limited (by key or a small set of predicates). Redis is typically in-memory; DynamoDB is a managed distributed store that allows choosing consistency level (eventual or strongly consistent reads for some operations).

*Use cases:* Caching, session storage, rate limiting, real-time analytics.

```kotlin
// Redis: Key-Value operations
redis.set("user:123:session", sessionData, ttl = 3600)  // amortized O(1) for simple set
val session = redis.get("user:123:session")              // amortized O(1)
redis.incr("api:rate-limit:user:123")                   // atomic counter
```

**3. Column-Family (Cassandra, HBase):**

*Theory:* Wide-column stores. Optimized for distributed writes and keyed/range reads. Commonly used for time-series data. Provide horizontal scaling via automatic partitioning. Typically offer eventual or tunable consistency.

*Use cases:* Time-series data, IoT sensors, logs, analytics.

```cql
-- Cassandra: Column-family for time-series
CREATE TABLE sensor_data (
    sensor_id UUID,
    timestamp TIMESTAMP,
    temperature DOUBLE,
    PRIMARY KEY (sensor_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
-- Optimized for high-volume writes and reads
```

**4. Graph Databases (Neo4j, Amazon Neptune):**

*Theory:* Represent data as graphs: nodes (vertices) and relationships (edges). Optimized for graph traversals and relationship-centric queries.

*Use cases:* Social networks, recommendation engines, knowledge graphs, fraud detection.

```cypher
// Neo4j: Graph query
MATCH (user:User {id: 123})-[:FOLLOWS]->(friend)-[:LIKES]->(product)
WHERE NOT (user)-[:PURCHASED]->(product)
RETURN product
// Recommendations based on friends' interests
```

**Comparison Table:**

| Characteristic | SQL | NoSQL |
|----------------|-----|-------|
| Schema | Fixed / strongly defined | Flexible (schema-less / schema-on-read) |
| Scaling | Primarily vertical; horizontal via sharding/replication | Horizontal scaling as a primary design goal |
| Transactions | Full ACID (DB/setting-dependent) | Often limited or local transactions; BASE-style patterns common |
| Relationships | Native (JOINs, foreign keys) | Typically via denormalization or app-level references |
| Query Language | SQL (standardized variants) | Various proprietary query languages / APIs |
| Consistency | Typically strong within node/cluster with sync replication | Often eventual or tunable consistency |
| Performance | Strong for complex queries/aggregations | Strong for simple lookups/writes at large scale |
| Use Cases | Transactional systems, finance, ERP | Big data, high-scale, flexible-schema systems |

**CAP Theorem and Consistency:**

*Theory:* CAP theorem: under a network partition, a distributed system cannot provide both strong Consistency and full Availability; systems choose trade-offs (CP vs AP). This classification is about specific distributed deployments, not about "SQL vs NoSQL" as query languages.

**SQL (often CP in distributed setups):**
- With synchronous replication and strong consistency, may sacrifice availability under partitions
- Example: a PostgreSQL cluster configured so that nodes refuse writes without quorum

**NoSQL (often AP or tunable):**
- Many are designed for high availability and partition tolerance, allowing eventual consistency
- Some, like Cassandra, offer tunable consistency per operation
- Services like DynamoDB let you choose between eventual and strongly consistent reads for certain APIs

**When to Use SQL:**

✅ **Use SQL when:**
- Financial transactions (banking, payments)
- Strong consistency and integrity are critical
- Complex relationships (many JOINs)
- ACID guarantees are required
- Schema is relatively stable and well-defined
- You need ad-hoc queries, analytics, reporting

**When to Use NoSQL:**

✅ **Use NoSQL when:**
- You need large-scale horizontal distribution (including multi-region)
- Schema is flexible or evolves rapidly
- Eventual or tunable consistency is acceptable
- Access patterns are simple (by key, key-range)
- High throughput (hundreds of thousands/millions ops/sec) is required
- Big data, real-time analytics, event/behavior data
- Denormalized aggregates fit your read patterns

**Hybrid Approach:**

*Theory:* Many real-world systems use both. SQL for critical transactional data and strong integrity; NoSQL for scalable reads/writes, caching, and analytics. This is called polyglot persistence: choosing the best storage for each workload.

```kotlin
// Hybrid approach
class OrderService(
    private val postgresRepo: PostgresOrderRepository,  // SQL for transactions
    private val redisCache: RedisCache,                 // Redis for cache
    private val mongoRepo: MongoProductRepository       // MongoDB for catalog/analytics
) {
    suspend fun createOrder(order: Order): Order {
        // 1. Check inventory in PostgreSQL (ACID)
        postgresRepo.checkInventory(order.items)

        // 2. Create order in PostgreSQL (transaction)
        val savedOrder = postgresRepo.save(order)

        // 3. Cache in Redis
        redisCache.set("order:${'$'}{savedOrder.id}", savedOrder)

        // 4. Update analytics / product stats in MongoDB
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

## References

- "NoSQL" on Wikipedia: https://en.wikipedia.org/wiki/NoSQL

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

## Дополнительные Вопросы (RU)
- Как обрабатывать eventual consistency в NoSQL?
- В чём разница между нормализацией и денормализацией?
- Как выбирать между разными типами NoSQL-хранилищ?

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-caching-strategies--system-design--medium]] - Паттерны кеширования
- [[q-horizontal-vertical-scaling--system-design--medium]] - Стратегии масштабирования

### Связанные (средний уровень)
- [[q-rest-api-design-best-practices--system-design--medium]] - Проектирование API
- [[q-load-balancing-strategies--system-design--medium]] - Балансировка нагрузки

### Продвинутые (сложнее)
- [[q-database-sharding-partitioning--system-design--hard]] - Распределение данных
- [[q-cap-theorem-distributed-systems--system-design--hard]] - Теорема CAP

## Ссылки (RU)
- "NoSQL" в Википедии: https://en.wikipedia.org/wiki/NoSQL
