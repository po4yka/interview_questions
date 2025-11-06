---
id: cs-036
title: "Database Fundamentals / Фундаментальные основы баз данных"
aliases: ["Database Fundamentals", "Фундаментальные основы баз данных"]
topic: cs
subtopics: [databases, indexing, nosql, sql, transactions]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-database-design, c-relational-databases, q-sql-nosql-databases--system-design--medium]
created: "2025-10-13"
updated: 2025-01-25
tags: [acid, database, difficulty/hard, indexing, normalization, nosql, sql, transactions]
sources: [https://en.wikipedia.org/wiki/Database]
---

# Вопрос (RU)
> Объясните фундаментальные концепции баз данных. Что такое ACID, транзакции, индексы, нормализация? Когда использовать SQL vs NoSQL?

# Question (EN)
> Explain fundamental database concepts. What are ACID, transactions, indexes, normalization? When to use SQL vs NoSQL?

---

## Ответ (RU)

**Теория баз данных:**
База данных - организованная структура для хранения и управления данными. Основные концепции: ACID (атомарность, согласованность, изолированность, долговечность), транзакции (атомарные операции), индексы (ускорение поиска), нормализация (устранение избыточности). SQL базы - реляционные, NoSQL - нереляционные с различными моделями данных.

**1. SQL vs NoSQL:**

*Теория:* SQL базы данных используют реляционную модель (таблицы, строки, столбцы), строгий schema, ACID транзакции, сложные запросы с JOINs. NoSQL базы используют различные модели (document, key-value, graph, column-family), flexible schema, eventual consistency, горизонтальное масштабирование.

```kotlin
// ✅ SQL (Room/SQLite)
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    val age: Int
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE age > :minAge")
    suspend fun getUsersOlderThan(minAge: Int): List<User>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)
}

// ✅ NoSQL (Flexible schema)
data class UserDocument(
    val id: String = "",
    val name: String = "",
    val metadata: Map<String, Any> = emptyMap()  // Flexible!
)
```

**Когда использовать SQL:**
- Сложные запросы с JOINs
- ACID транзакции критичны
- Фиксированный schema
- Реляционные данные

**Когда использовать NoSQL:**
- Гибкий schema нужен
- Горизонтальное масштабирование
- Простые запросы
- Высокий write throughput

**2. ACID Properties:**

*Теория:* ACID - набор свойств транзакций в БД: **Atomicity** (всё или ничего - транзакция выполняется полностью или не выполняется), **Consistency** (валидное состояние БД до и после), **Isolation** (конкурентные транзакции не видят промежуточных изменений), **Durability** (изменения сохраняются после commit).

```kotlin
// ✅ Atomicity: либо все операции, либо ни одна
@Database(entities = [Account::class], version = 1)
abstract class BankDatabase : RoomDatabase() {
    abstract fun accountDao(): AccountDao
}

@Dao
interface AccountDao {
    @Transaction
    suspend fun transfer(fromId: String, toId: String, amount: Int) {
        // Всё выполняется атомарно
        updateBalance(fromId, -amount)
        updateBalance(toId, amount)
    }
}

// ✅ Isolation: конкурентные транзакции изолированы
// ✅ Consistency: балансы всегда корректны
// ✅ Durability: изменения сохраняются на диск
```

**3. Transactions и Concurrency Control:**

*Теория:* Транзакция - последовательность операций, выполняемых как атомарная единица. Isolation levels определяют видимость промежуточных состояний между транзакциями. Read Uncommitted (грязное чтение), Read Committed (грязное чтение невозможно), Repeatable Read (фантомное чтение возможно), Serializable (полная изоляция).

```kotlin
// ✅ Room transactions
suspend fun performComplexOperation() {
    database.withTransaction {
        val user = userDao.getUser("123")
        userDao.updateUser(user.copy(name = "Updated"))
        productDao.insertProducts(listOf(...))
        // Все операции в одной транзакции
    }
}

// ✅ Pessimistic locking
@Query("SELECT * FROM User WHERE id = :id FOR UPDATE")
suspend fun getUserWithLock(id: String): User

// ✅ Optimistic locking с version
@Entity
data class Product(
    @PrimaryKey val id: String,
    val name: String,
    @ColumnInfo(defaultValue = "0") val version: Int
)
```

**4. Indexing и Query Optimization:**

*Теория:* Индекс - структура данных, ускоряющая поиск в таблице. Создаёт ordered structure на основе indexed columns. Поиск O(log n) вместо O(n). Trade-off: замедляет INSERT/UPDATE/DELETE, занимает дополнительную память. Используется для columns в WHERE, foreign keys, columns для JOINs.

```kotlin
// ✅ Индексы в Room
@Entity(
    indices = [
        Index("userId"),  // Single column index
        Index(value = ["userId", "status"], unique = true)  // Composite index
    ]
)
data class Task(
    @PrimaryKey val id: String,
    val userId: String,
    val status: String
)

@Dao
interface TaskDao {
    // ✅ Использование индекса
    @Query("SELECT * FROM Task WHERE userId = :userId")
    suspend fun getTasksByUser(userId: String): List<Task>

    // ✅ Index order matters!
    @Query("SELECT * FROM Task WHERE userId = :userId AND status = :status")
    suspend fun getTasks(userId: String, status: String): List<Task>

    // ❌ Неправильный порядок - индекс менее эффективен
    @Query("SELECT * FROM Task WHERE status = :status AND userId = :userId")
    suspend fun getTasksWrongOrder(userId: String, status: String): List<Task>
}
```

**Индексы - trade-offs:**
| Операция | Без индекса | С индексом |
|----------|------------|------------|
| SELECT | O(n) | O(log n) |
| INSERT | O(1) | O(log n) |
| UPDATE | O(n) | O(log n) |
| DELETE | O(n) | O(log n) |

**5. Normalization и Denormalization:**

*Теория:* Нормализация - процесс упорядочивания data в БД для устранения redundancy и anomalies. 1NF (atomic values, no repeating groups), 2NF (1NF + no partial dependencies on composite key), 3NF (2NF + no transitive dependencies). Денормализация - умышленное добавление redundancy для улучшения read performance.

```kotlin
// ❌ Unnormalized: избыточность данных
data class OrderUnnormalized(
    val orderId: String,
    val customerName: String,
    val customerEmail: String,
    val productName: String,
    val productPrice: Double
)
// Проблема: данные customer повторяются для каждого товара

// ✅ 1NF: atomic values, no repeating groups
@Entity
data class Order1NF(
    @PrimaryKey val orderId: String,
    val customerId: String,
    val productId: String
)

// ✅ 2NF: no partial dependencies
@Entity
data class Customer(
    @PrimaryKey val id: String,
    val name: String,
    val email: String
)

@Entity
data class Product(
    @PrimaryKey val id: String,
    val name: String,
    val price: Double
)

@Entity(foreignKeys = [ForeignKey(...)])
data class Order2NF(
    @PrimaryKey val id: String,
    val customerId: String,
    val productId: String
)
// ✅ Нет частичных зависимостей от composite key

// ✅ 3NF: no transitive dependencies
@Entity
data class City(
    @PrimaryKey val id: String,
    val name: String,
    val countryId: String
)

@Entity
data class Country(
    @PrimaryKey val id: String,
    val name: String
)

@Entity
data class Customer3NF(
    @PrimaryKey val id: String,
    val cityId: String  // ✅ Нет countryId (transitive dependency удалён)
)
```

**6. Database Design Principles:**

*Теория:* Принципы проектирования БД: выбор правильных data types, использование foreign keys для integrity, правильная нормализация (баланс между 3NF и performance), индексы для частых запросов, partitioning для больших таблиц, backup strategies, security considerations.

```kotlin
// ✅ Правильный дизайн
@Entity(
    foreignKeys = [
        ForeignKey(
            entity = Customer::class,
            parentColumns = ["id"],
            childColumns = ["customerId"],
            onDelete = ForeignKey.CASCADE  // Cascade delete
        )
    ],
    indices = [Index("customerId")]  // Index foreign key
)
data class Order(
    @PrimaryKey val id: String,
    val customerId: String,
    @ColumnInfo(typeAffinity = ColumnInfo.REAL) val total: Double
)
```

**7. Room Database Best Practices:**

*Теория:* Room - SQLite abstraction layer для Android. Используется для local data storage, caching, offline-first подходов. Ключевые компоненты: Entity (таблицы), DAO (database access objects), Database (главный класс). Flow для reactive queries, транзакции для atomicity, migrations для schema changes.

```kotlin
// ✅ Room setup
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun create(context: Context): AppDatabase {
            return Room.databaseBuilder(
                context,
                AppDatabase::class.java,
                "app.db"
            ).build()
        }
    }
}

// ✅ Reactive queries с Flow
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>  // Автоматически обновляется!
}

// ✅ Migrations
@Database(entities = [User::class], version = 2)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(database: SupportSQLiteDatabase) {
                database.execSQL("ALTER TABLE users ADD COLUMN avatar TEXT")
            }
        }

        fun create(context: Context): AppDatabase {
            return Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
                .addMigrations(MIGRATION_1_2)
                .build()
        }
    }
}
```

**Ключевые концепции:**

1. **ACID** - гарантии корректности транзакций
2. **Indexing** - trade-off между read и write performance
3. **Normalization** - устранение anomalies, улучшение integrity
4. **SQL vs NoSQL** - разные use cases и trade-offs
5. **Transactions** - atomicity и isolation для consistency

## Answer (EN)

**Database Theory:**
Database - organized structure for storing and managing data. Main concepts: ACID (atomicity, consistency, isolation, durability), transactions (atomic operations), indexes (search speedup), normalization (eliminate redundancy). SQL databases - relational, NoSQL - non-relational with different data models.

**1. SQL vs NoSQL:**

*Theory:* SQL databases use relational model (tables, rows, columns), strict schema, ACID transactions, complex queries with JOINs. NoSQL databases use various models (document, key-value, graph, column-family), flexible schema, eventual consistency, horizontal scaling.

```kotlin
// ✅ SQL (Room/SQLite)
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    val age: Int
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE age > :minAge")
    suspend fun getUsersOlderThan(minAge: Int): List<User>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)
}

// ✅ NoSQL (Flexible schema)
data class UserDocument(
    val id: String = "",
    val name: String = "",
    val metadata: Map<String, Any> = emptyMap()  // Flexible!
)
```

**When to use SQL:**
- Complex queries with JOINs
- ACID transactions critical
- Fixed schema
- Relational data

**When to use NoSQL:**
- Flexible schema needed
- Horizontal scaling
- Simple queries
- High write throughput

**2. ACID Properties:**

*Theory:* ACID - set of transaction properties in databases: **Atomicity** (all or nothing - transaction executes fully or not), **Consistency** (valid database state before and after), **Isolation** (concurrent transactions don't see intermediate changes), **Durability** (changes persisted after commit).

```kotlin
// ✅ Atomicity: either all operations or none
@Database(entities = [Account::class], version = 1)
abstract class BankDatabase : RoomDatabase() {
    abstract fun accountDao(): AccountDao
}

@Dao
interface AccountDao {
    @Transaction
    suspend fun transfer(fromId: String, toId: String, amount: Int) {
        // Everything executes atomically
        updateBalance(fromId, -amount)
        updateBalance(toId, amount)
    }
}

// ✅ Isolation: concurrent transactions isolated
// ✅ Consistency: balances always correct
// ✅ Durability: changes saved to disk
```

**3. Transactions and Concurrency Control:**

*Theory:* Transaction - sequence of operations executed as atomic unit. Isolation levels determine visibility of intermediate states between transactions. Read Uncommitted (dirty read), Read Committed (no dirty read), Repeatable Read (phantom read possible), Serializable (full isolation).

```kotlin
// ✅ Room transactions
suspend fun performComplexOperation() {
    database.withTransaction {
        val user = userDao.getUser("123")
        userDao.updateUser(user.copy(name = "Updated"))
        productDao.insertProducts(listOf(...))
        // All operations in one transaction
    }
}

// ✅ Pessimistic locking
@Query("SELECT * FROM User WHERE id = :id FOR UPDATE")
suspend fun getUserWithLock(id: String): User

// ✅ Optimistic locking with version
@Entity
data class Product(
    @PrimaryKey val id: String,
    val name: String,
    @ColumnInfo(defaultValue = "0") val version: Int
)
```

**4. Indexing and Query Optimization:**

*Theory:* Index - data structure speeding up search in table. Creates ordered structure based on indexed columns. Search O(log n) instead of O(n). Trade-off: slows INSERT/UPDATE/DELETE, uses additional memory. Used for columns in WHERE, foreign keys, columns for JOINs.

```kotlin
// ✅ Indexes in Room
@Entity(
    indices = [
        Index("userId"),  // Single column index
        Index(value = ["userId", "status"], unique = true)  // Composite index
    ]
)
data class Task(
    @PrimaryKey val id: String,
    val userId: String,
    val status: String
)

@Dao
interface TaskDao {
    // ✅ Using index
    @Query("SELECT * FROM Task WHERE userId = :userId")
    suspend fun getTasksByUser(userId: String): List<Task>

    // ✅ Index order matters!
    @Query("SELECT * FROM Task WHERE userId = :userId AND status = :status")
    suspend fun getTasks(userId: String, status: String): List<Task>
}
```

**Index trade-offs:**
| Operation | Without Index | With Index |
|-----------|---------------|------------|
| SELECT | O(n) | O(log n) |
| INSERT | O(1) | O(log n) |
| UPDATE | O(n) | O(log n) |
| DELETE | O(n) | O(log n) |

**5. Normalization and Denormalization:**

*Theory:* Normalization - process of organizing data in database to eliminate redundancy and anomalies. 1NF (atomic values, no repeating groups), 2NF (1NF + no partial dependencies on composite key), 3NF (2NF + no transitive dependencies). Denormalization - intentional adding of redundancy to improve read performance.

```kotlin
// ❌ Unnormalized: data redundancy
data class OrderUnnormalized(
    val orderId: String,
    val customerName: String,
    val customerEmail: String,
    val productName: String,
    val productPrice: Double
)
// Problem: customer data repeated for each product

// ✅ 1NF: atomic values, no repeating groups
@Entity
data class Order1NF(
    @PrimaryKey val orderId: String,
    val customerId: String,
    val productId: String
)

// ✅ 2NF: no partial dependencies
@Entity
data class Customer(
    @PrimaryKey val id: String,
    val name: String,
    val email: String
)

@Entity
data class Product(
    @PrimaryKey val id: String,
    val name: String,
    val price: Double
)

@Entity(foreignKeys = [ForeignKey(...)])
data class Order2NF(
    @PrimaryKey val id: String,
    val customerId: String,
    val productId: String
)
// ✅ No partial dependencies on composite key

// ✅ 3NF: no transitive dependencies
@Entity
data class City(
    @PrimaryKey val id: String,
    val name: String,
    val countryId: String
)

@Entity
data class Country(
    @PrimaryKey val id: String,
    val name: String
)

@Entity
data class Customer3NF(
    @PrimaryKey val id: String,
    val cityId: String  // ✅ No countryId (transitive dependency removed)
)
```

**6. Database Design Principles:**

*Theory:* Database design principles: choosing right data types, using foreign keys for integrity, proper normalization (balance between 3NF and performance), indexes for frequent queries, partitioning for large tables, backup strategies, security considerations.

```kotlin
// ✅ Proper design
@Entity(
    foreignKeys = [
        ForeignKey(
            entity = Customer::class,
            parentColumns = ["id"],
            childColumns = ["customerId"],
            onDelete = ForeignKey.CASCADE  // Cascade delete
        )
    ],
    indices = [Index("customerId")]  // Index foreign key
)
data class Order(
    @PrimaryKey val id: String,
    val customerId: String,
    @ColumnInfo(typeAffinity = ColumnInfo.REAL) val total: Double
)
```

**7. Room Database Best Practices:**

*Theory:* Room - SQLite abstraction layer for Android. Used for local data storage, caching, offline-first approaches. Key components: Entity (tables), DAO (database access objects), Database (main class). Flow for reactive queries, transactions for atomicity, migrations for schema changes.

```kotlin
// ✅ Room setup
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun create(context: Context): AppDatabase {
            return Room.databaseBuilder(
                context,
                AppDatabase::class.java,
                "app.db"
            ).build()
        }
    }
}

// ✅ Reactive queries with Flow
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>  // Auto-updates!
}

// ✅ Migrations
@Database(entities = [User::class], version = 2)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(database: SupportSQLiteDatabase) {
                database.execSQL("ALTER TABLE users ADD COLUMN avatar TEXT")
            }
        }

        fun create(context: Context): AppDatabase {
            return Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
                .addMigrations(MIGRATION_1_2)
                .build()
        }
    }
}
```

**Key Concepts:**

1. **ACID** - guarantees for transaction correctness
2. **Indexing** - trade-off between read and write performance
3. **Normalization** - eliminate anomalies, improve integrity
4. **SQL vs NoSQL** - different use cases and trade-offs
5. **Transactions** - atomicity and isolation for consistency

---

## Follow-ups

- How do you handle database migrations in production?
- What is the difference between optimistic and pessimistic locking?
- When should you denormalize a database?

## Related Questions

### Prerequisites (Easier)
- Basic database concepts
- SQL fundamentals

### Related (Same Level)
- [[q-sql-nosql-databases--system-design--medium]] - SQL vs NoSQL detailed
- [[c-relational-databases]] - Relational database concepts

### Advanced (Harder)
- Database sharding and partitioning
- Distributed database systems
- Advanced indexing strategies
