---
id: 20251012-300009
title: "Database Sharding and Partitioning / Шардирование и партиционирование баз данных"
topic: system-design
difficulty: hard
status: draft
created: 2025-10-12
tags:
  - system-design
  - database
  - sharding
  - partitioning
  - scalability
moc: moc-system-design
related: [q-message-queues-event-driven--system-design--medium, q-load-balancing-strategies--system-design--medium, q-rest-api-design-best-practices--system-design--medium]
  - q-sql-nosql-databases--system-design--medium
  - q-horizontal-vertical-scaling--system-design--medium
  - q-cap-theorem-distributed-systems--system-design--hard
subtopics:
  - database
  - sharding
  - partitioning
  - scalability
  - distributed-databases
---
# Question (EN)
> What is database sharding? How is it different from partitioning? What are the sharding strategies, and what are the trade-offs?

# Вопрос (RU)
> Что такое шардирование базы данных? Чем оно отличается от партиционирования? Каковы стратегии шардирования и какие компромиссы?

---

## Answer (EN)

As your database grows, a single server can't handle all the load. Sharding and partitioning are techniques to horizontally scale databases by distributing data across multiple servers.



### Partitioning vs Sharding

**Partitioning** = Splitting large table into smaller pieces on **same server**
**Sharding** = Splitting data across **multiple servers**

```
Partitioning (Vertical Scaling):

     Single Database Server   
         
  Part 1    Part 2       
  2020      2021         
         


Sharding (Horizontal Scaling):
    
 Shard 1     Shard 2     Shard 3  
 Users       Users       Users    
 1-1000     1001-2000   2001-3000 
    
 Server 1      Server 2      Server 3
```

---

### Partitioning Strategies

### 1. Range Partitioning

**Split by value range** (e.g., by date, ID range)

```sql
-- PostgreSQL Range Partitioning
CREATE TABLE orders (
    order_id BIGINT,
    user_id BIGINT,
    created_at TIMESTAMP,
    total DECIMAL(10, 2)
) PARTITION BY RANGE (created_at);

-- Partition by year
CREATE TABLE orders_2023 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE orders_2025 PARTITION OF orders
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

**Query automatically routes to correct partition:**
```sql
-- Queries only orders_2024 partition
SELECT * FROM orders 
WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31';
```

** Pros:**
- Easy to implement
- Simple queries
- Easy to add/remove partitions (drop old data)
- Good for time-series data

** Cons:**
- Can create hotspots (recent data gets all writes)
- Uneven distribution if ranges not balanced

---

### 2. Hash Partitioning

**Use hash function** to distribute data evenly

```sql
-- PostgreSQL Hash Partitioning
CREATE TABLE users (
    user_id BIGINT,
    email VARCHAR(255),
    name VARCHAR(255)
) PARTITION BY HASH (user_id);

-- Create 4 partitions
CREATE TABLE users_0 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE users_1 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE users_2 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE users_3 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

**Distribution:**
```
hash(user_id) % 4 = partition_number

user_id=100 → hash % 4 = 0 → users_0
user_id=101 → hash % 4 = 1 → users_1
user_id=102 → hash % 4 = 2 → users_2
user_id=103 → hash % 4 = 3 → users_3
```

** Pros:**
- Even distribution
- No hotspots
- Predictable performance

** Cons:**
- Range queries scan all partitions
- Hard to rebalance (adding partitions requires rehashing)

---

### 3. List Partitioning

**Partition by discrete values** (e.g., country, category)

```sql
CREATE TABLE products (
    product_id BIGINT,
    name VARCHAR(255),
    category VARCHAR(50)
) PARTITION BY LIST (category);

CREATE TABLE products_electronics PARTITION OF products
    FOR VALUES IN ('electronics', 'computers', 'phones');

CREATE TABLE products_clothing PARTITION OF products
    FOR VALUES IN ('clothing', 'shoes', 'accessories');

CREATE TABLE products_food PARTITION OF products
    FOR VALUES IN ('food', 'beverages', 'snacks');
```

** Pros:**
- Logical grouping
- Easy to query by category
- Can isolate important data

** Cons:**
- Uneven distribution if categories imbalanced
- Need to know values upfront

---

### Sharding Strategies

### 1. Range-Based Sharding

**Distribute by ID range**

```kotlin
// Shard routing logic
class RangeShardRouter(
    private val shards: List<DataSource>
) {
    fun getShard(userId: Long): DataSource {
        return when {
            userId <= 1_000_000 -> shards[0]  // Shard 1: 1-1M
            userId <= 2_000_000 -> shards[1]  // Shard 2: 1M-2M
            userId <= 3_000_000 -> shards[2]  // Shard 3: 2M-3M
            else -> shards[3]                 // Shard 4: 3M+
        }
    }
}

@Service
class UserService(private val shardRouter: RangeShardRouter) {
    
    suspend fun getUser(userId: Long): User? {
        val shard = shardRouter.getShard(userId)
        val connection = shard.connection
        
        return connection.prepareStatement(
            "SELECT * FROM users WHERE user_id = ?"
        ).use { stmt ->
            stmt.setLong(1, userId)
            stmt.executeQuery().toUser()
        }
    }
}
```

** Pros:**
- Simple to implement
- Range queries efficient (query single shard)

** Cons:**
- Hotspots on new data (all new users go to latest shard)
- Unbalanced load

---

### 2. Hash-Based Sharding

**Use hash function to determine shard**

```kotlin
class HashShardRouter(
    private val shards: List<DataSource>,
    private val numberOfShards: Int = shards.size
) {
    fun getShard(key: String): DataSource {
        val hash = key.hashCode()
        val shardIndex = abs(hash % numberOfShards)
        return shards[shardIndex]
    }
}

@Service
class OrderService(private val shardRouter: HashShardRouter) {
    
    suspend fun getOrder(orderId: String): Order? {
        val shard = shardRouter.getShard(orderId)
        // Query specific shard
        return shard.queryOrder(orderId)
    }
    
    suspend fun getUserOrders(userId: String): List<Order> {
        // Problem: Need to query ALL shards!
        return shards.map { shard ->
            shard.queryOrdersByUser(userId)
        }.flatten()
    }
}
```

** Pros:**
- Even distribution
- No hotspots
- Simple logic

** Cons:**
- Adding/removing shards requires data migration
- Queries by non-shard-key require querying all shards
- No range query support

---

### 3. Consistent Hashing

**Better for dynamic shard addition/removal**

```kotlin
class ConsistentHashRouter(
    private val shards: List<DataSource>,
    private val virtualNodes: Int = 150
) {
    private val ring = TreeMap<Int, DataSource>()

    init {
        // Add virtual nodes for each shard
        shards.forEach { shard ->
            repeat(virtualNodes) { i ->
                val hash = "${shard.id}-$i".hashCode()
                ring[hash] = shard
            }
        }
    }

    fun getShard(key: String): DataSource {
        if (ring.isEmpty()) throw IllegalStateException("No shards")
        
        val hash = key.hashCode()
        
        // Find next node clockwise on ring
        val entry = ring.ceilingEntry(hash) ?: ring.firstEntry()
        return entry.value
    }

    fun addShard(shard: DataSource) {
        repeat(virtualNodes) { i ->
            val hash = "${shard.id}-$i".hashCode()
            ring[hash] = shard
        }
        // Only ~1/N data needs to move (N = number of shards)
    }

    fun removeShard(shard: DataSource) {
        repeat(virtualNodes) { i ->
            val hash = "${shard.id}-$i".hashCode()
            ring.remove(hash)
        }
        // Redistribute data from removed shard
    }
}
```

**Benefits:**
```
Adding shard:
Before: 3 shards, each has 33% data
Add shard 4: Only ~25% of data needs rebalancing (1/4)
Not 100% like simple hash!

Ring visualization:
    0°
    
270°90°   Shards distributed around ring
           with virtual nodes
   180°
```

** Pros:**
- Minimal data movement when adding/removing shards
- Even distribution with virtual nodes
- Handles dynamic topology

** Cons:**
- More complex implementation
- Still can't do range queries easily

---

### 4. Geographic Sharding

**Shard by location** (for latency, compliance)

```kotlin
enum class Region {
    US_EAST, US_WEST, EU, ASIA
}

class GeoShardRouter(
    private val shards: Map<Region, DataSource>
) {
    fun getShard(userId: Long): DataSource {
        val userRegion = userRegionService.getRegion(userId)
        return shards[userRegion] 
            ?: throw IllegalStateException("No shard for $userRegion")
    }
}

// Usage
@Service
class UserService(private val geoRouter: GeoShardRouter) {
    suspend fun getUser(userId: Long): User? {
        val shard = geoRouter.getShard(userId)
        return shard.queryUser(userId)
    }
}
```

** Pros:**
- Low latency (data close to users)
- Regulatory compliance (GDPR - data in EU)
- Fault isolation by region

** Cons:**
- Uneven distribution by population
- Cross-region queries expensive
- Complex to manage

---

### Sharding Challenges & Solutions

### Challenge 1: Joins Across Shards

**Problem:** Can't JOIN across different databases

 **Bad (doesn't work):**
```sql
-- Can't join users and orders if on different shards
SELECT u.name, o.total
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE u.user_id = 123;
```

 **Solution: Application-level joins**
```kotlin
suspend fun getUserWithOrders(userId: Long): UserWithOrders {
    val userShard = userShardRouter.getShard(userId)
    val orderShard = orderShardRouter.getShard(userId)
    
    // Query both shards
    val user = userShard.getUser(userId)
    val orders = orderShard.getOrdersByUser(userId)
    
    // Join in application
    return UserWithOrders(user, orders)
}
```

 **Solution: Denormalization**
```kotlin
// Store user data in orders table (duplicate)
data class Order(
    val orderId: Long,
    val userId: Long,
    val userName: String,        // Denormalized!
    val userEmail: String,       // Denormalized!
    val total: BigDecimal
)

// No join needed
suspend fun getOrderWithUser(orderId: Long): Order {
    val shard = orderShardRouter.getShard(orderId)
    return shard.getOrder(orderId)  // Has user data already
}
```

---

### Challenge 2: Distributed Transactions

**Problem:** ACID transactions don't work across shards

 **Bad (doesn't work):**
```kotlin
// Can't have atomic transaction across shards
transaction {
    userShard.updateBalance(userId, -100)    // Shard 1
    orderShard.createOrder(orderId, 100)     // Shard 2
}
// If orderShard fails, userShard already committed!
```

 **Solution: Saga Pattern**
```kotlin
class TransferSaga(
    private val userShardRouter: ShardRouter,
    private val orderShardRouter: ShardRouter
) {
    suspend fun transfer(userId: Long, amount: BigDecimal) {
        try {
            // Step 1: Debit user
            userShardRouter.getShard(userId)
                .updateBalance(userId, -amount)
            
            // Step 2: Create order
            orderShardRouter.getShard(userId)
                .createOrder(userId, amount)
                
        } catch (e: Exception) {
            // Compensating transaction (rollback)
            userShardRouter.getShard(userId)
                .updateBalance(userId, +amount)  // Refund
            throw e
        }
    }
}
```

---

### Challenge 3: Auto-Increment IDs

**Problem:** Each shard has its own sequence

```
Shard 1: IDs 1, 2, 3, 4...
Shard 2: IDs 1, 2, 3, 4...  ← Collision!
Shard 3: IDs 1, 2, 3, 4...
```

 **Solution 1: UUID**
```kotlin
data class User(
    val id: UUID = UUID.randomUUID(),  // Globally unique
    val email: String,
    val name: String
)
```

 **Solution 2: Snowflake ID**
```kotlin
// Twitter Snowflake: 64-bit ID
// [Timestamp 41 bits][Datacenter 5 bits][Machine 5 bits][Sequence 12 bits]

class SnowflakeIdGenerator(
    private val datacenterId: Long,
    private val machineId: Long
) {
    private var sequence = 0L
    private var lastTimestamp = -1L

    @Synchronized
    fun nextId(): Long {
        var timestamp = System.currentTimeMillis()
        
        if (timestamp == lastTimestamp) {
            sequence = (sequence + 1) and 4095  // 12 bits
            if (sequence == 0L) {
                // Wait for next millisecond
                timestamp = waitNextMillis(lastTimestamp)
            }
        } else {
            sequence = 0
        }
        
        lastTimestamp = timestamp
        
        return ((timestamp - EPOCH) shl 22) or
                (datacenterId shl 17) or
                (machineId shl 12) or
                sequence
    }
}

// Usage
val idGen = SnowflakeIdGenerator(datacenterId = 1, machineId = 1)
val userId = idGen.nextId()  // 1234567890123456789
```

 **Solution 3: Database sequences with offset**
```sql
-- Shard 1: Sequence starts at 1, increments by 1000
CREATE SEQUENCE user_id_seq_1 START 1 INCREMENT BY 1000;

-- Shard 2: Sequence starts at 2, increments by 1000
CREATE SEQUENCE user_id_seq_2 START 2 INCREMENT BY 1000;

-- Shard 3: Sequence starts at 3, increments by 1000
CREATE SEQUENCE user_id_seq_3 START 3 INCREMENT BY 1000;

-- Result:
-- Shard 1: 1, 1001, 2001, 3001...
-- Shard 2: 2, 1002, 2002, 3002...
-- Shard 3: 3, 1003, 2003, 3003...
-- No collisions!
```

---

### Challenge 4: Resharding (Adding/Removing Shards)

**Problem:** Changing number of shards requires data migration

```kotlin
class ReshardingService(
    private val oldShards: List<DataSource>,
    private val newShards: List<DataSource>
) {
    suspend fun reshard() {
        // 1. Stop writes (or double-write to old + new)
        
        // 2. Migrate data
        oldShards.forEach { oldShard ->
            val users = oldShard.getAllUsers()
            
            users.forEach { user ->
                // Recalculate shard for new topology
                val newShard = hashShardRouter.getShard(user.id)
                newShard.insertUser(user)
            }
        }
        
        // 3. Switch reads to new shards
        
        // 4. Decommission old shards
    }
}
```

**Zero-downtime resharding:**
```kotlin
class DualWriteResharding {
    suspend fun migrateWithZeroDowntime() {
        // Phase 1: Dual writes (write to both old and new)
        enableDualWrites()
        
        // Phase 2: Backfill old data to new shards
        backfillData()
        
        // Phase 3: Switch reads to new shards
        switchReads()
        
        // Phase 4: Stop writing to old shards
        disableDualWrites()
        
        // Phase 5: Decommission old shards
        decommissionOldShards()
    }
}
```

---

### Real-World Example: Instagram Sharding

**Instagram's sharding strategy:**

```kotlin
// Instagram uses PostgreSQL with sharding
// Shard key: user_id (photos stored with user)

class InstagramShardRouter(
    private val shards: List<DataSource>
) {
    private val numberOfShards = 4096  // Power of 2

    fun getShard(userId: Long): DataSource {
        // Use consistent hashing
        val shardId = userId % numberOfShards
        val logicalShardId = shardId / (numberOfShards / shards.size)
        return shards[logicalShardId.toInt()]
    }
}

// Logical shards: 4096 (for future growth)
// Physical shards: Initially 10, can grow to 4096

// Benefits:
// - Can split logical shard without changing shard key
// - Logical shard 0-409 → Physical shard 1
// - Later split: 0-204 → Physical shard 1a
//                205-409 → Physical shard 1b
```

---

### Sharding Decision Matrix

| Factor | Range | Hash | Consistent Hash | Geographic |
|--------|-------|------|-----------------|------------|
| **Even distribution** |  |  |  |  |
| **Range queries** |  |  |  |  |
| **Add/remove shards** |  |  |  |  |
| **Complexity** | Low | Low | High | Medium |
| **Hotspots** |  Yes |  No |  No |  Yes |
| **Use case** | Time-series | Even load | Dynamic | Multi-region |

---

### Key Takeaways

1. **Partitioning** = Split data on same server
2. **Sharding** = Split data across multiple servers
3. **Range partitioning** = By date/ID range (time-series)
4. **Hash partitioning** = Even distribution, no range queries
5. **Consistent hashing** = Easier to add/remove shards
6. **Geographic sharding** = Low latency, compliance
7. **Challenges:** Cross-shard joins, distributed transactions, ID generation
8. **Solutions:** Denormalization, Saga pattern, UUID/Snowflake IDs
9. **Resharding is hard** - Plan ahead with logical shards
10. **Choose based on:** Query patterns, growth expectations, ops complexity

---

## Ответ (RU)

По мере роста вашей базы данных один сервер не может обработать всю нагрузку. Шардирование и партиционирование - техники горизонтального масштабирования баз данных путём распределения данных по нескольким серверам.



### Партиционирование vs Шардирование

**Партиционирование** = Разделение большой таблицы на меньшие части на **том же сервере**
**Шардирование** = Разделение данных по **нескольким серверам**

```
Партиционирование (Вертикальное масштабирование):

     Один сервер БД

  Часть 1    Часть 2
  2020       2021



Шардирование (Горизонтальное масштабирование):

 Шард 1      Шард 2      Шард 3
 Users       Users       Users
 1-1000     1001-2000   2001-3000

 Сервер 1      Сервер 2      Сервер 3
```

---

### Стратегии партиционирования

### 1. Range Partitioning (По диапазону)

**Разделение по диапазону значений** (например, по дате, диапазону ID)

```sql
-- PostgreSQL Range Partitioning
CREATE TABLE orders (
    order_id BIGINT,
    user_id BIGINT,
    created_at TIMESTAMP,
    total DECIMAL(10, 2)
) PARTITION BY RANGE (created_at);

-- Партиции по годам
CREATE TABLE orders_2023 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

**Запрос автоматически направляется в правильную партицию:**
```sql
-- Запрашивает только партицию orders_2024
SELECT * FROM orders
WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31';
```

** Плюсы:**
- Легко реализовать
- Простые запросы
- Легко добавлять/удалять партиции (удаление старых данных)
- Хорошо для time-series данных

** Минусы:**
- Может создавать hotspots (недавние данные получают все записи)
- Неравномерное распределение если диапазоны не сбалансированы

---

### 2. Hash Partitioning (По хешу)

**Использование хеш-функции** для равномерного распределения данных

```sql
-- PostgreSQL Hash Partitioning
CREATE TABLE users (
    user_id BIGINT,
    email VARCHAR(255),
    name VARCHAR(255)
) PARTITION BY HASH (user_id);

-- Создание 4 партиций
CREATE TABLE users_0 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE users_1 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
```

**Распределение:**
```
hash(user_id) % 4 = номер_партиции

user_id=100 → hash % 4 = 0 → users_0
user_id=101 → hash % 4 = 1 → users_1
```

** Плюсы:**
- Равномерное распределение
- Нет hotspots
- Предсказуемая производительность

** Минусы:**
- Range запросы сканируют все партиции
- Сложно ребалансировать (добавление партиций требует rehashing)

---

### 3. List Partitioning (По списку)

**Партиционирование по дискретным значениям** (например, страна, категория)

```sql
CREATE TABLE products (
    product_id BIGINT,
    name VARCHAR(255),
    category VARCHAR(50)
) PARTITION BY LIST (category);

CREATE TABLE products_electronics PARTITION OF products
    FOR VALUES IN ('electronics', 'computers', 'phones');

CREATE TABLE products_clothing PARTITION OF products
    FOR VALUES IN ('clothing', 'shoes', 'accessories');
```

** Плюсы:**
- Логическая группировка
- Легко запрашивать по категории
- Можно изолировать важные данные

** Минусы:**
- Неравномерное распределение если категории несбалансированы
- Нужно знать значения заранее

---

### Стратегии шардирования

### 1. Range-Based Sharding (По диапазону)

**Распределение по диапазону ID**

```kotlin
// Логика маршрутизации шардов
class RangeShardRouter(
    private val shards: List<DataSource>
) {
    fun getShard(userId: Long): DataSource {
        return when {
            userId <= 1_000_000 -> shards[0]  // Шард 1: 1-1M
            userId <= 2_000_000 -> shards[1]  // Шард 2: 1M-2M
            userId <= 3_000_000 -> shards[2]  // Шард 3: 2M-3M
            else -> shards[3]                 // Шард 4: 3M+
        }
    }
}
```

** Плюсы:**
- Просто реализовать
- Эффективные range queries (запрос к одному шарду)

** Минусы:**
- Hotspots на новых данных (все новые пользователи идут в последний шард)
- Несбалансированная нагрузка

---

### 2. Hash-Based Sharding (По хешу)

**Использование хеш-функции для определения шарда**

```kotlin
class HashShardRouter(
    private val shards: List<DataSource>,
    private val numberOfShards: Int = shards.size
) {
    fun getShard(key: String): DataSource {
        val hash = key.hashCode()
        val shardIndex = abs(hash % numberOfShards)
        return shards[shardIndex]
    }
}
```

** Плюсы:**
- Равномерное распределение
- Нет hotspots
- Простая логика

** Минусы:**
- Добавление/удаление шардов требует миграции данных
- Запросы по не-ключу-шарда требуют запроса всех шардов
- Нет поддержки range queries

---

### 3. Consistent Hashing (Консистентное хеширование)

**Лучше для динамического добавления/удаления шардов**

```kotlin
class ConsistentHashRouter(
    private val shards: List<DataSource>,
    private val virtualNodes: Int = 150
) {
    private val ring = TreeMap<Int, DataSource>()

    init {
        // Добавить виртуальные узлы для каждого шарда
        shards.forEach { shard ->
            repeat(virtualNodes) { i ->
                val hash = "${shard.id}-$i".hashCode()
                ring[hash] = shard
            }
        }
    }

    fun getShard(key: String): DataSource {
        if (ring.isEmpty()) throw IllegalStateException("No shards")

        val hash = key.hashCode()

        // Найти следующий узел по часовой стрелке на кольце
        val entry = ring.ceilingEntry(hash) ?: ring.firstEntry()
        return entry.value
    }
}
```

**Преимущества:**
```
Добавление шарда:
До: 3 шарда, каждый имеет 33% данных
Добавить шард 4: Только ~25% данных нужно ребалансировать (1/4)
Не 100% как при простом хешировании!
```

** Плюсы:**
- Минимальное перемещение данных при добавлении/удалении шардов
- Равномерное распределение с виртуальными узлами
- Обрабатывает динамическую топологию

** Минусы:**
- Более сложная реализация
- Все еще не может делать range queries легко

---

### 4. Geographic Sharding (Географическое шардирование)

**Шардирование по местоположению** (для latency, compliance)

```kotlin
enum class Region {
    US_EAST, US_WEST, EU, ASIA
}

class GeoShardRouter(
    private val shards: Map<Region, DataSource>
) {
    fun getShard(userId: Long): DataSource {
        val userRegion = userRegionService.getRegion(userId)
        return shards[userRegion]
            ?: throw IllegalStateException("No shard for $userRegion")
    }
}
```

** Плюсы:**
- Низкая задержка (данные близко к пользователям)
- Соответствие нормативным требованиям (GDPR - данные в ЕС)
- Изоляция отказов по регионам

** Минусы:**
- Неравномерное распределение по населению
- Межрегиональные запросы дорогие
- Сложно управлять

---

### Проблемы шардирования и решения

### Проблема 1: JOIN между шардами

**Проблема:** Невозможно делать JOIN между разными базами данных

 **Плохо (не работает):**
```sql
-- Нельзя соединить users и orders если они на разных шардах
SELECT u.name, o.total
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE u.user_id = 123;
```

 **Решение: JOIN на уровне приложения**
```kotlin
suspend fun getUserWithOrders(userId: Long): UserWithOrders {
    val userShard = userShardRouter.getShard(userId)
    val orderShard = orderShardRouter.getShard(userId)

    // Запросить оба шарда
    val user = userShard.getUser(userId)
    val orders = orderShard.getOrdersByUser(userId)

    // Соединить в приложении
    return UserWithOrders(user, orders)
}
```

 **Решение: Денормализация**
```kotlin
// Хранить данные пользователя в таблице заказов (дублировать)
data class Order(
    val orderId: Long,
    val userId: Long,
    val userName: String,        // Денормализовано!
    val userEmail: String,       // Денормализовано!
    val total: BigDecimal
)

// JOIN не нужен
suspend fun getOrderWithUser(orderId: Long): Order {
    val shard = orderShardRouter.getShard(orderId)
    return shard.getOrder(orderId)  // Уже содержит данные пользователя
}
```

---

### Проблема 2: Распределённые транзакции

**Проблема:** ACID транзакции не работают между шардами

 **Плохо (не работает):**
```kotlin
// Нельзя иметь атомарную транзакцию между шардами
transaction {
    userShard.updateBalance(userId, -100)    // Шард 1
    orderShard.createOrder(orderId, 100)     // Шард 2
}
// Если orderShard падает, userShard уже закоммичен!
```

 **Решение: Saga Pattern**
```kotlin
class TransferSaga(
    private val userShardRouter: ShardRouter,
    private val orderShardRouter: ShardRouter
) {
    suspend fun transfer(userId: Long, amount: BigDecimal) {
        try {
            // Шаг 1: Списать с пользователя
            userShardRouter.getShard(userId)
                .updateBalance(userId, -amount)

            // Шаг 2: Создать заказ
            orderShardRouter.getShard(userId)
                .createOrder(userId, amount)

        } catch (e: Exception) {
            // Компенсирующая транзакция (откат)
            userShardRouter.getShard(userId)
                .updateBalance(userId, +amount)  // Возврат средств
            throw e
        }
    }
}
```

---

### Проблема 3: Auto-Increment ID

**Проблема:** Каждый шард имеет свою последовательность

```
Шард 1: ID 1, 2, 3, 4...
Шард 2: ID 1, 2, 3, 4...  ← Коллизия!
Шард 3: ID 1, 2, 3, 4...
```

 **Решение 1: UUID**
```kotlin
data class User(
    val id: UUID = UUID.randomUUID(),  // Глобально уникальный
    val email: String,
    val name: String
)
```

 **Решение 2: Snowflake ID**
```kotlin
// Twitter Snowflake: 64-битный ID
// [Timestamp 41 бит][Datacenter 5 бит][Machine 5 бит][Sequence 12 бит]

class SnowflakeIdGenerator(
    private val datacenterId: Long,
    private val machineId: Long
) {
    private var sequence = 0L
    private var lastTimestamp = -1L

    @Synchronized
    fun nextId(): Long {
        var timestamp = System.currentTimeMillis()

        if (timestamp == lastTimestamp) {
            sequence = (sequence + 1) and 4095  // 12 бит
            if (sequence == 0L) {
                // Ждать следующей миллисекунды
                timestamp = waitNextMillis(lastTimestamp)
            }
        } else {
            sequence = 0
        }

        lastTimestamp = timestamp

        return ((timestamp - EPOCH) shl 22) or
                (datacenterId shl 17) or
                (machineId shl 12) or
                sequence
    }
}

// Использование
val idGen = SnowflakeIdGenerator(datacenterId = 1, machineId = 1)
val userId = idGen.nextId()  // 1234567890123456789
```

 **Решение 3: Последовательности БД со смещением**
```sql
-- Шард 1: Последовательность начинается с 1, увеличивается на 1000
CREATE SEQUENCE user_id_seq_1 START 1 INCREMENT BY 1000;

-- Шард 2: Последовательность начинается с 2, увеличивается на 1000
CREATE SEQUENCE user_id_seq_2 START 2 INCREMENT BY 1000;

-- Результат:
-- Шард 1: 1, 1001, 2001, 3001...
-- Шард 2: 2, 1002, 2002, 3002...
-- Нет коллизий!
```

---

### Проблема 4: Решардирование (Добавление/Удаление шардов)

**Проблема:** Изменение количества шардов требует миграции данных

```kotlin
class ReshardingService(
    private val oldShards: List<DataSource>,
    private val newShards: List<DataSource>
) {
    suspend fun reshard() {
        // 1. Остановить записи (или двойная запись в старые + новые)

        // 2. Мигрировать данные
        oldShards.forEach { oldShard ->
            val users = oldShard.getAllUsers()

            users.forEach { user ->
                // Пересчитать шард для новой топологии
                val newShard = hashShardRouter.getShard(user.id)
                newShard.insertUser(user)
            }
        }

        // 3. Переключить чтения на новые шарды
        // 4. Вывести из эксплуатации старые шарды
    }
}
```

**Решардирование без downtime:**
```kotlin
class DualWriteResharding {
    suspend fun migrateWithZeroDowntime() {
        // Фаза 1: Двойные записи (запись в старые и новые)
        enableDualWrites()

        // Фаза 2: Backfill старых данных в новые шарды
        backfillData()

        // Фаза 3: Переключить чтения на новые шарды
        switchReads()

        // Фаза 4: Прекратить запись в старые шарды
        disableDualWrites()

        // Фаза 5: Вывести из эксплуатации старые шарды
        decommissionOldShards()
    }
}
```

---

### Реальный пример: Шардирование Instagram

**Стратегия шардирования Instagram:**

```kotlin
// Instagram использует PostgreSQL с шардированием
// Ключ шарда: user_id (фото хранятся с пользователем)

class InstagramShardRouter(
    private val shards: List<DataSource>
) {
    private val numberOfShards = 4096  // Степень 2

    fun getShard(userId: Long): DataSource {
        // Использовать консистентное хеширование
        val shardId = userId % numberOfShards
        val logicalShardId = shardId / (numberOfShards / shards.size)
        return shards[logicalShardId.toInt()]
    }
}

// Логические шарды: 4096 (для будущего роста)
// Физические шарды: Изначально 10, могут расти до 4096

// Преимущества:
// - Можно разделить логический шард без изменения ключа шарда
// - Логический шард 0-409 → Физический шард 1
// - Позже разделить: 0-204 → Физический шард 1a
//                    205-409 → Физический шард 1b
```

---

### Матрица решений по шардированию

| Фактор | Range | Hash | Consistent Hash | Geographic |
|--------|-------|------|-----------------|------------|
| **Равномерное распределение** |  |  |  |  |
| **Range запросы** |  |  |  |  |
| **Добавление/удаление шардов** |  |  |  |  |
| **Сложность** | Низкая | Низкая | Высокая | Средняя |
| **Hotspots** |  Да |  Нет |  Нет |  Да |
| **Сценарий** | Time-series | Равная нагрузка | Динамическая | Мульти-регион |

---

### Ключевые выводы

1. **Партиционирование** = Разделение данных на том же сервере
2. **Шардирование** = Разделение данных по нескольким серверам
3. **Range partitioning** = По дате/диапазону ID (time-series)
4. **Hash partitioning** = Равномерное распределение, нет range queries
5. **Consistent hashing** = Проще добавлять/удалять шарды
6. **Geographic sharding** = Низкая задержка, compliance
7. **Проблемы:** Cross-shard joins, распределённые транзакции, генерация ID
8. **Решения:** Денормализация, Saga pattern, UUID/Snowflake IDs
9. **Решардирование сложное** - Планируйте заранее с логическими шардами
10. **Выбирайте на основе:** Паттернов запросов, ожиданий роста, операционной сложности

## Follow-ups

1. What is the difference between logical and physical sharding?
2. How do you handle shard rebalancing with zero downtime?
3. What is the Vitess sharding solution for MySQL?
4. How do you implement cross-shard queries efficiently?
5. What are the strategies for global secondary indexes in sharded databases?
6. How does MongoDB handle auto-sharding?
7. What is the difference between vertical and horizontal sharding?
8. How do you monitor and maintain sharded databases?
9. What are the backup and recovery strategies for sharded systems?
10. How do you handle hotspots in sharded databases?

---

## Related Questions

### Related (Hard)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system

### Prerequisites (Easier)
- [[q-sql-nosql-databases--system-design--medium]] - sql nosql databases   system
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-design-url-shortener--system-design--medium]] - design url shortener   system

