---
id: 20251012-300005
title: "SQL vs NoSQL Databases / SQL vs NoSQL базы данных"
slug: sql-nosql-databases-system-design-medium
topic: system-design
subtopics:
  - databases
  - sql
  - nosql
  - data-modeling
  - scalability
status: draft
difficulty: medium
moc: moc-system-design
date_created: 2025-10-12
date_updated: 2025-10-12
related_questions:
  - q-database-sharding--system-design--hard
  - q-cap-theorem-distributed-systems--system-design--hard
  - q-database-indexing--system-design--medium
tags:
  - system-design
  - databases
  - sql
  - nosql
  - scalability
---

# SQL vs NoSQL Databases

## English Version

### Problem Statement

Choosing between SQL and NoSQL databases is one of the most important decisions in system design. Each has distinct strengths, weaknesses, and ideal use cases. Understanding these trade-offs helps you select the right database for your application's requirements.

**The Question:** What are the key differences between SQL and NoSQL databases? When should you use each type, and what are the trade-offs?

### Detailed Answer

#### SQL (Relational) Databases

**Examples:** PostgreSQL, MySQL, Oracle, SQL Server, MariaDB

**Key Characteristics:**
-  **ACID** transactions (Atomicity, Consistency, Isolation, Durability)
-  **Schema-based** - fixed table structure
-  **Relationships** via foreign keys
-  **SQL** query language (standardized)
-  **Joins** across tables
-  **Strong consistency**

```sql
-- SQL Example: E-commerce schema
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT REFERENCES orders(id),
    product_id BIGINT REFERENCES products(id),
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- Complex JOIN query
SELECT 
    u.name,
    o.id AS order_id,
    o.total_amount,
    SUM(oi.quantity) AS total_items
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
WHERE o.created_at > NOW() - INTERVAL '30 days'
GROUP BY u.name, o.id, o.total_amount
ORDER BY o.total_amount DESC;
```

---

#### NoSQL Databases

**Types:**

**1. Document Stores** (MongoDB, CouchDB)
- Store JSON-like documents
- Flexible schema
- Nested data structures

**2. Key-Value Stores** (Redis, DynamoDB)
- Simple key → value mapping
- Extremely fast
- Limited query capabilities

**3. Column-Family** (Cassandra, HBase)
- Wide column storage
- Optimized for writes
- Time-series data

**4. Graph Databases** (Neo4j, Amazon Neptune)
- Nodes and relationships
- Social networks, recommendations

---

### Comparison Matrix

| Feature | SQL | NoSQL |
|---------|-----|-------|
| **Schema** | Fixed, predefined | Flexible, schema-less |
| **Scalability** | Vertical (scale up) | Horizontal (scale out) |
| **Transactions** | ACID (strong) | BASE (eventual consistency) |
| **Relationships** | Native (JOINs) | Denormalized/embedded |
| **Query Language** | SQL (standardized) | Varied (API-based) |
| **Data Integrity** | High (constraints) | Application-level |
| **Consistency** | Strong | Eventual (tunable) |
| **Performance** | Good for complex queries | Excellent for simple lookups |
| **Use Cases** | Financial, ERP, CRM | Big data, real-time, social |

---

### SQL Deep Dive

#### ACID Properties

```kotlin
// SQL Transaction Example
class BankService(private val dataSource: DataSource) {
    
    fun transfer(fromAccount: Long, toAccount: Long, amount: BigDecimal) {
        dataSource.connection.use { conn ->
            conn.autoCommit = false
            try {
                // Atomicity: All or nothing
                val debitStmt = conn.prepareStatement(
                    "UPDATE accounts SET balance = balance - ? WHERE id = ? AND balance >= ?"
                )
                debitStmt.setBigDecimal(1, amount)
                debitStmt.setLong(2, fromAccount)
                debitStmt.setBigDecimal(3, amount)
                
                val debitRows = debitStmt.executeUpdate()
                if (debitRows == 0) {
                    throw InsufficientFundsException()
                }
                
                val creditStmt = conn.prepareStatement(
                    "UPDATE accounts SET balance = balance + ? WHERE id = ?"
                )
                creditStmt.setBigDecimal(1, amount)
                creditStmt.setLong(2, toAccount)
                creditStmt.executeUpdate()
                
                // Commit: Durability guaranteed
                conn.commit()
                
                // Consistency: Database constraints enforced
                // Isolation: Other transactions see old or new state, not intermediate
            } catch (e: Exception) {
                // Rollback on any error
                conn.rollback()
                throw e
            }
        }
    }
}
```

#### When to Use SQL

 **Strong Consistency Required:**
- Financial transactions
- Inventory management
- Booking systems
- Order processing

 **Complex Relationships:**
- Multiple JOINs needed
- Referential integrity important
- Normalized data model

 **Ad-hoc Queries:**
- Business intelligence
- Reporting
- Analytics

 **ACID Guarantees:**
- Data integrity critical
- Transactions required

**Example Use Cases:**
```
- Banking systems
- E-commerce platforms
- ERP systems
- CRM applications
- Booking engines
- Accounting software
```

---

### NoSQL Deep Dive

#### 1. Document Databases (MongoDB)

**Best for:** Flexible schemas, nested data, rapid development

```javascript
// MongoDB Document Example
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "name": "John Doe",
  "email": "john@example.com",
  "addresses": [  // Embedded documents
    {
      "type": "home",
      "street": "123 Main St",
      "city": "New York",
      "zip": "10001"
    },
    {
      "type": "work",
      "street": "456 Office Blvd",
      "city": "New York",
      "zip": "10002"
    }
  ],
  "orders": [  // Denormalized data
    {
      "order_id": "ORD-001",
      "total": 99.99,
      "status": "shipped",
      "items": [
        { "product": "Widget", "quantity": 2, "price": 49.99 }
      ]
    }
  ],
  "preferences": {  // Flexible schema
    "newsletter": true,
    "notifications": {
      "email": true,
      "sms": false
    }
  },
  "created_at": ISODate("2023-01-15T10:00:00Z"),
  "updated_at": ISODate("2023-10-12T15:30:00Z")
}
```

**Querying:**
```javascript
// Find users with shipped orders in New York
db.users.find({
  "addresses.city": "New York",
  "orders.status": "shipped"
})

// Aggregation pipeline
db.users.aggregate([
  { $match: { "created_at": { $gte: ISODate("2023-01-01") } } },
  { $unwind: "$orders" },
  { $group: {
      _id: "$orders.status",
      count: { $sum: 1 },
      totalRevenue: { $sum: "$orders.total" }
  }}
])
```

**Kotlin Implementation:**
```kotlin
data class User(
    @BsonId
    val id: ObjectId = ObjectId(),
    val name: String,
    val email: String,
    val addresses: List<Address> = emptyList(),
    val orders: List<Order> = emptyList(),
    val preferences: Preferences = Preferences(),
    val createdAt: Instant = Instant.now(),
    val updatedAt: Instant = Instant.now()
)

data class Address(
    val type: String,
    val street: String,
    val city: String,
    val zip: String
)

data class Order(
    val orderId: String,
    val total: BigDecimal,
    val status: String,
    val items: List<OrderItem>
)

class UserRepository(private val database: MongoDatabase) {
    private val users = database.getCollection<User>("users")
    
    suspend fun findUsersByCity(city: String): List<User> {
        return users.find(User::addresses / Address::city eq city).toList()
    }
    
    suspend fun addOrder(userId: ObjectId, order: Order) {
        users.updateOne(
            User::id eq userId,
            push(User::orders, order),
            set(User::updatedAt, Instant.now())
        )
    }
}
```

** Pros:**
- Flexible schema (add fields anytime)
- Fast reads (denormalized)
- Intuitive data model
- Horizontal scaling (sharding)

** Cons:**
- Data duplication
- No JOIN support
- Weak consistency by default
- Application-level integrity

---

#### 2. Key-Value Stores (Redis, DynamoDB)

**Best for:** Caching, sessions, real-time data

```kotlin
// Redis Example
class CacheService(private val redis: RedisClient) {
    
    suspend fun cacheUser(user: User) {
        redis.setex(
            key = "user:${user.id}",
            seconds = 3600,
            value = Json.encodeToString(user)
        )
    }
    
    suspend fun getUser(userId: Long): User? {
        val cached = redis.get("user:$userId") ?: return null
        return Json.decodeFromString(cached)
    }
    
    // Atomic operations
    suspend fun incrementPageViews(pageId: String): Long {
        return redis.incr("page:$pageId:views")
    }
    
    // Pub/Sub
    suspend fun publishNotification(userId: Long, message: String) {
        redis.publish("notifications:$userId", message)
    }
}
```

**DynamoDB Example:**
```kotlin
data class Product(
    @DynamoDbPartitionKey
    val productId: String,
    @DynamoDbSortKey
    val category: String,
    val name: String,
    val price: BigDecimal,
    val inventory: Int,
    val metadata: Map<String, String> = emptyMap()
)

class ProductRepository(private val dynamoDb: DynamoDbClient) {
    
    suspend fun getProduct(productId: String, category: String): Product? {
        return dynamoDb.getItem {
            tableName = "products"
            key = mapOf(
                "productId" to AttributeValue.S(productId),
                "category" to AttributeValue.S(category)
            )
        }.item?.let { /* deserialize */ }
    }
    
    // Query with secondary index
    suspend fun findProductsByPrice(
        minPrice: BigDecimal,
        maxPrice: BigDecimal
    ): List<Product> {
        return dynamoDb.query {
            tableName = "products"
            indexName = "price-index"
            keyConditionExpression = "price BETWEEN :min AND :max"
            expressionAttributeValues = mapOf(
                ":min" to AttributeValue.N(minPrice.toString()),
                ":max" to AttributeValue.N(maxPrice.toString())
            )
        }.items.map { /* deserialize */ }
    }
}
```

** Pros:**
- Extremely fast (sub-millisecond)
- Simple data model
- Infinite scalability
- Low latency

** Cons:**
- Limited query capabilities
- No complex queries
- Data duplication needed
- Key design critical

---

#### 3. Column-Family (Cassandra)

**Best for:** Time-series, write-heavy workloads, big data

```kotlin
// Cassandra Schema
/*
CREATE TABLE sensor_data (
    sensor_id UUID,
    timestamp TIMESTAMP,
    temperature DOUBLE,
    humidity DOUBLE,
    pressure DOUBLE,
    PRIMARY KEY ((sensor_id), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
*/

data class SensorReading(
    val sensorId: UUID,
    val timestamp: Instant,
    val temperature: Double,
    val humidity: Double,
    val pressure: Double
)

class SensorRepository(private val session: CqlSession) {
    
    suspend fun insertReading(reading: SensorReading) {
        session.executeAsync(
            SimpleStatement.newInstance(
                "INSERT INTO sensor_data (sensor_id, timestamp, temperature, humidity, pressure) " +
                "VALUES (?, ?, ?, ?, ?)",
                reading.sensorId,
                reading.timestamp,
                reading.temperature,
                reading.humidity,
                reading.pressure
            )
        ).await()
    }
    
    suspend fun getRecentReadings(
        sensorId: UUID,
        limit: Int = 100
    ): List<SensorReading> {
        return session.executeAsync(
            SimpleStatement.newInstance(
                "SELECT * FROM sensor_data WHERE sensor_id = ? LIMIT ?",
                sensorId,
                limit
            )
        ).await().map { /* deserialize */ }
    }
}
```

** Pros:**
- Extremely high write throughput
- Horizontal scalability
- No single point of failure
- Time-series optimized

** Cons:**
- Limited query patterns
- Eventual consistency
- Data modeling complex
- No JOINs

---

### Decision Framework

```

  Do you need ACID transactions?         
  (banking, inventory, bookings)         

            
    
     YES            NO
                   
        
  SQL        Is data highly related?  
         (many JOINs needed)      
              
                      
              
               YES            NO
                             
                  
            SQL        What's primary workload? 
                  
                                
                    
                                          
                  Read      Write       Key-Value
                  Heavy     Heavy       Lookups
                                          
                                          
                  
                MongoDB  Cassandra  Redis/ 
                                    DynamoDB
                  
```

---

### Real-World Architecture

**E-commerce Platform (Polyglot Persistence):**

```

         Application Layer               

                                
                                
   
PostgreSQL MongoDB   Redis   Elasticsearch
                                      
Users     Product  Sessions Search    
Orders    Catalog  Cart     Index     
Payments  Reviews  Cache              
   
    SQL       NoSQL      KV Store    Search
```

**Implementation:**
```kotlin
@Service
class EcommerceService(
    private val userRepository: UserRepository,           // PostgreSQL
    private val productRepository: ProductRepository,     // MongoDB
    private val cacheService: CacheService,              // Redis
    private val searchService: SearchService              // Elasticsearch
) {
    
    suspend fun placeOrder(userId: Long, cart: Cart): Order {
        // 1. Get user from SQL (ACID for payments)
        val user = userRepository.findById(userId)
            ?: throw UserNotFoundException()
        
        // 2. Get products from MongoDB (flexible schema)
        val products = productRepository.findByIds(cart.productIds)
        
        // 3. Create order in SQL (transaction required)
        val order = userRepository.createOrder(user.id, products, cart)
        
        // 4. Clear cart from Redis
        cacheService.delete("cart:${user.id}")
        
        // 5. Update search index
        searchService.updateProductInventory(products)
        
        return order
    }
}
```

---

### Migration Strategies

#### SQL → NoSQL Migration

**Step 1: Add NoSQL alongside SQL**
```kotlin
class HybridRepository(
    private val sql: JdbcTemplate,
    private val mongo: MongoDatabase
) {
    suspend fun getUser(id: Long): User {
        // Read from both during migration
        val sqlUser = sql.queryForObject("SELECT * FROM users WHERE id = ?", id)
        val mongoUser = mongo.getCollection<User>("users").findOne(User::id eq id)
        
        // Compare and log differences
        if (sqlUser != mongoUser) {
            log.warn("Data mismatch for user $id")
        }
        
        return sqlUser
    }
}
```

**Step 2: Dual writes**
```kotlin
suspend fun updateUser(user: User) {
    // Write to both databases
    sql.update("UPDATE users SET name = ? WHERE id = ?", user.name, user.id)
    mongo.getCollection<User>("users").replaceOne(User::id eq user.id, user)
}
```

**Step 3: Switch reads to NoSQL**
**Step 4: Stop writing to SQL**
**Step 5: Decommission SQL**

---

### Key Takeaways

1. **SQL** = ACID, relationships, complex queries, strong consistency
2. **NoSQL** = Scalability, flexibility, high performance, eventual consistency
3. **Use SQL** for: Financial, inventory, bookings, complex JOINs
4. **Use NoSQL** for: Big data, real-time, flexible schema, high scale
5. **Document DB** (MongoDB) = Flexible schema, nested data
6. **Key-Value** (Redis) = Caching, sessions, simple lookups
7. **Column-Family** (Cassandra) = Time-series, write-heavy
8. **Graph** (Neo4j) = Social networks, relationships
9. **Polyglot Persistence** = Use multiple databases for different needs
10. **No silver bullet** - choose based on requirements

---

## Russian Version

### Постановка задачи

Выбор между SQL и NoSQL базами данных - одно из самых важных решений в проектировании систем. У каждого типа есть свои сильные и слабые стороны и идеальные сценарии использования.

**Вопрос:** Каковы ключевые различия между SQL и NoSQL базами данных? Когда следует использовать каждый тип, и каковы компромиссы?

### Детальный ответ

#### SQL (Реляционные) базы данных

**Примеры:** PostgreSQL, MySQL, Oracle, SQL Server, MariaDB

**Ключевые характеристики:**
-  **ACID** транзакции
-  **Schema-based** - фиксированная структура таблиц
-  **Связи** через внешние ключи
-  **SQL** язык запросов (стандартизированный)
-  **JOIN** между таблицами
-  **Строгая консистентность**

#### NoSQL базы данных

**Типы:**

**1. Document Stores** (MongoDB, CouchDB)
- Хранят JSON-подобные документы
- Гибкая схема
- Вложенные структуры данных

**2. Key-Value Stores** (Redis, DynamoDB)
- Простое key → value отображение
- Чрезвычайно быстрые
- Ограниченные возможности запросов

**3. Column-Family** (Cassandra, HBase)
- Широкое колоночное хранение
- Оптимизированы для записи
- Временные ряды данных

**4. Graph базы** (Neo4j, Amazon Neptune)
- Узлы и связи
- Социальные сети, рекомендации

### Матрица сравнения

| Особенность | SQL | NoSQL |
|-------------|-----|-------|
| **Схема** | Фиксированная | Гибкая |
| **Масштабируемость** | Вертикальная | Горизонтальная |
| **Транзакции** | ACID | BASE |
| **Связи** | Нативные (JOIN) | Денормализованные |
| **Язык запросов** | SQL | Различные API |
| **Консистентность** | Строгая | Eventual |

### Ключевые выводы

1. **SQL** = ACID, связи, сложные запросы, строгая консистентность
2. **NoSQL** = Масштабируемость, гибкость, высокая производительность
3. **Используйте SQL** для: Финансов, инвентаря, бронирования, сложных JOIN
4. **Используйте NoSQL** для: Big data, real-time, гибкой схемы, высокого масштаба
5. **Document DB** = Гибкая схема, вложенные данные
6. **Key-Value** = Кеширование, сессии, простой lookup
7. **Column-Family** = Временные ряды, много записей
8. **Polyglot Persistence** = Используйте несколько БД для разных нужд

## Follow-ups

1. What is database normalization and when should you denormalize?
2. How do you implement transactions in NoSQL databases?
3. What is the difference between sharding and replication?
4. Explain eventual consistency vs strong consistency with examples
5. How do you migrate from SQL to NoSQL database?
6. What are the CAP theorem implications for database choice?
7. How do you model many-to-many relationships in NoSQL?
8. What is polyglot persistence and when to use it?
9. How do secondary indexes work in NoSQL databases?
10. What are the security considerations for SQL vs NoSQL?

---

## Related Questions

### Related (Medium)
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-design-url-shortener--system-design--medium]] - design url shortener   system
- [[q-load-balancing-strategies--system-design--medium]] - load balancing strategies   system
- [[q-horizontal-vertical-scaling--system-design--medium]] - horizontal vertical scaling   system

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system
### Related (Medium)
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-design-url-shortener--system-design--medium]] - design url shortener   system
- [[q-load-balancing-strategies--system-design--medium]] - load balancing strategies   system
- [[q-horizontal-vertical-scaling--system-design--medium]] - horizontal vertical scaling   system

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system
### Related (Medium)
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-design-url-shortener--system-design--medium]] - design url shortener   system
- [[q-load-balancing-strategies--system-design--medium]] - load balancing strategies   system
- [[q-horizontal-vertical-scaling--system-design--medium]] - horizontal vertical scaling   system

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system
