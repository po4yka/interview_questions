---
id: cs-036
title: "Database Fundamentals / 4fdff04121"
aliases: ["04fdff04121", "Database Fundamentals"]
topic: cs
subtopics: [databases, indexing, transactions]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-database-design, c-relational-databases, q-sql-nosql-databases--system-design--medium]
created: "2025-10-13"
updated: "2025-11-11"
tags: [acid, database, difficulty/hard, indexing, normalization, nosql, sql, transactions]
sources: ["https://en.wikipedia.org/wiki/Database"]

---
# Вопрос (RU)
> Объясните фундаментальные концепции баз данных. Что такое ACID, транзакции, индексы, нормализация? Когда использовать SQL vs NoSQL?

# Question (EN)
> Explain fundamental database concepts. What are ACID, transactions, indexes, normalization? When to use SQL vs NoSQL?

---

## Ответ (RU)

**Теория баз данных:**
База данных — организованная структура для хранения и управления данными. Основные концепции: ACID (атомарность, согласованность, изолированность, долговечность), транзакции (атомарные единицы работы), индексы (ускорение поиска), нормализация (устранение избыточности и аномалий). SQL-базы — реляционные; NoSQL-базы — нереляционные с различными моделями данных.

**1. SQL vs NoSQL:**

*Теория:* SQL-базы данных используют реляционную модель (таблицы, строки, столбцы), как правило, фиксированную схему, ACID-транзакции и сложные запросы с `JOIN`. NoSQL-базы используют различные модели (document, key-value, graph, column-family), предлагают гибкую схему и часто обеспечивают eventual или настраиваемую (`tunable`) согласованность (часть систем поддерживает сильную согласованность), а также ориентированы на горизонтальное масштабирование.

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

// ✅ NoSQL (гибкая схема)
data class UserDocument(
    val id: String = "",
    val name: String = "",
    val metadata: Map<String, Any> = emptyMap()  // Гибкая структура
)
```

**Когда использовать SQL:**
- Сложные запросы с `JOIN`
- Критичны сильные ACID-гарантии
- Относительно стабильная схема
- Сильно реляционные данные

**Когда использовать NoSQL:**
- Нужна гибкая/эволюционирующая схема
- Требуется горизонтальное масштабирование
- Простые шаблоны доступа
- Очень высокий поток записей / большие объемы данных

**2. ACID Properties:**

*Теория:* ACID — свойства, ожидаемые от транзакций в СУБД:
- Atomicity (атомарность): всё или ничего.
- Consistency (согласованность): каждая зафиксированная транзакция сохраняет все ограничения; БД переходит из одного корректного состояния в другое.
- Isolation (изолированность): конкурентные транзакции (в той или иной степени, в зависимости от уровня изоляции) не видят промежуточных состояний друг друга.
- Durability (долговечность): после `COMMIT` изменения переживают сбои, как реализовано движком хранения.

Важно: аннотации фреймворков (например, `@Transaction` в Room) лишь используют механизмы конкретной СУБД и не создают дополнительных гарантий долговечности/изоляции сверх того, что поддерживает сам движок.

```kotlin
// ✅ Атомарный перевод, опирающийся на транзакционную семантику БД
@Database(entities = [Account::class], version = 1)
abstract class BankDatabase : RoomDatabase() {
    abstract fun accountDao(): AccountDao
}

@Dao
interface AccountDao {
    @Transaction
    suspend fun transfer(fromId: String, toId: String, amount: Int) {
        updateBalance(fromId, -amount)
        updateBalance(toId, amount)
    }

    @Query("UPDATE Account SET balance = balance + :delta WHERE id = :id")
    suspend fun updateBalance(id: String, delta: Int)
}

// Детали isolation/consistency/durability зависят от конкретной СУБД (например, настроек SQLite).
```

**3. Transactions и Concurrency Control:**

*Теория:* Транзакция — последовательность операций, выполняемых как единое атомарное целое. Уровни изоляции определяют, когда изменения одной транзакции становятся видимы другим:
- Read Uncommitted: допускает «грязные» чтения.
- Read Committed: грязные чтения запрещены.
- Repeatable Read: повторное чтение одной и той же строки в транзакции возвращает те же значения; фантомные чтения ещё возможны.
- `Serializable`: максимальная изоляция, эквивалент сериализованному выполнению.

```kotlin
// ✅ Транзакция в Room (использует транзакции SQLite)
suspend fun performComplexOperation() {
    database.withTransaction {
        val user = userDao.getUser("123")
        userDao.updateUser(user.copy(name = "Updated"))
        productDao.insertProducts(listOf(/* ... */))
        // Все операции выполняются в одной транзакции
    }
}

// Концепция пессимистичной блокировки (пример SQL; в SQLite/Room SELECT ... FOR UPDATE в таком виде не используется)
// SELECT * FROM Users WHERE id = :id FOR UPDATE;

// ✅ Оптимистичная блокировка с версией
@Entity
data class Product(
    @PrimaryKey val id: String,
    val name: String,
    @ColumnInfo(defaultValue = "0") val version: Int
)
```

**4. Indexing и Query Optimization:**

*Теория:* Индекс — структура данных (часто B-tree или его вариант), ускоряющая поиск за счёт дополнительных операций записи и потребления памяти. Поддерживает упорядоченное (или иное эффективно ищущееся) представление по одному или нескольким столбцам.
- Типичный сценарий: переход от линейного сканирования O(n) к поиску порядка O(log n) или лучше.
- Trade-off: каждая операция INSERT/UPDATE/DELETE по индексируемым столбцам должна обновлять индекс; индексы занимают место.
- Практика: индексировать столбцы из WHERE, условия JOIN и внешние ключи.

```kotlin
// ✅ Индексы в Room
@Entity(
    indices = [
        Index("userId"),  // Индекс по одному столбцу
        Index(value = ["userId", "status"], unique = true)  // Составной индекс
    ]
)
data class Task(
    @PrimaryKey val id: String,
    val userId: String,
    val status: String
)

@Dao
interface TaskDao {
    // Использует индекс по userId
    @Query("SELECT * FROM Task WHERE userId = :userId")
    suspend fun getTasksByUser(userId: String): List<Task>

    // Составной индекс (userId, status) хорошо подходит под этот предикат
    @Query("SELECT * FROM Task WHERE userId = :userId AND status = :status")
    suspend fun getTasks(userId: String, status: String): List<Task>

    // Если бы составной индекс был (status, userId), оптимальный предикат должен начинаться с status
}
```

**Индексы — ключевые trade-offs (интуитивно, не строгие оценки для всех движков):**
- SELECT: может перейти от полного сканирования к логарифмическому или более эффективному поиску при подходящем индексе.
- INSERT/UPDATE/DELETE: становятся несколько дороже из-за поддержки индексов.

**5. Normalization и Denormalization:**

*Теория:* Нормализация — организация данных для снижения избыточности и предотвращения аномалий.
- 1NF: атомарные значения, без повторяющихся групп.
- 2NF: 1NF и отсутствие частичных зависимостей неключевых атрибутов от части составного ключа.
- 3NF: 2NF и отсутствие транзитивных зависимостей неключевых атрибутов от первичного ключа.
Денормализация — осознанное введение избыточности ради производительности чтения под конкретные паттерны доступа.

```kotlin
// ❌ Ненормализовано: избыточность
data class OrderUnnormalized(
    val orderId: String,
    val customerName: String,
    val customerEmail: String,
    val productName: String,
    val productPrice: Double
)
// Проблема: данные клиента и товара дублируются.

// ✅ 1NF
@Entity
data class Order1NF(
    @PrimaryKey val orderId: String,
    val customerId: String,
    val productId: String
)

// ✅ Разделение сущностей
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

@Entity(
    foreignKeys = [
        ForeignKey(entity = Customer::class, parentColumns = ["id"], childColumns = ["customerId"]),
        ForeignKey(entity = Product::class, parentColumns = ["id"], childColumns = ["productId"])
    ]
)
data class OrderNormalized(
    @PrimaryKey val id: String,
    val customerId: String,
    val productId: String
)

// ✅ 3NF: избегаем транзитивных зависимостей
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
    val cityId: String  // countryId выводится через связь город → страна
)
```

**6. Принципы проектирования БД:**

*Теория:* Ключевые принципы:
- Выбор подходящих типов данных.
- Использование внешних ключей (где поддерживается) для ссылочной целостности.
- Нормализация как минимум до 3NF; денормализация только при явном обосновании паттернами доступа и производительностью.
- Создание индексов под частые и критичные запросы.
- Рассмотрение partitioning для очень больших таблиц.
- Планирование backup/restore и обеспечение безопасности (аутентификация, контроль доступа, шифрование).

```kotlin
// ✅ Пример аккуратного дизайна
@Entity(
    foreignKeys = [
        ForeignKey(
            entity = Customer::class,
            parentColumns = ["id"],
            childColumns = ["customerId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("customerId")]
)
data class Order(
    @PrimaryKey val id: String,
    val customerId: String,
    @ColumnInfo(typeAffinity = ColumnInfo.REAL) val total: Double
)
```

**7. Room Database Best Practices:**

*Теория:* Room — абстракция над SQLite для Android, используемая как конкретный пример реляционного хранилища в приложениях. Ключевые компоненты: `Entity` (таблицы), `DAO` (Data Access Object), `RoomDatabase`. Рекомендации:
- Использовать `Flow`/`LiveData` для реактивных запросов.
- Использовать `@Transaction` / `withTransaction` для атомарных операций.
- Настраивать `Migration` для изменений схемы между версиями.

```kotlin
// ✅ Настройка Room
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

// ✅ Реактивные запросы с Flow
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>  // Наблюдатели получают обновления при изменениях БД
}

// ✅ Пример миграции
@Database(entities = [User::class], version = 2)
abstract class AppDatabaseV2 : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(database: SupportSQLiteDatabase) {
                database.execSQL("ALTER TABLE users ADD COLUMN avatar TEXT")
            }
        }

        fun create(context: Context): AppDatabaseV2 {
            return Room.databaseBuilder(context, AppDatabaseV2::class.java, "app.db")
                .addMigrations(MIGRATION_1_2)
                .build()
        }
    }
}
```

**Ключевые концепции:**

1. ACID — гарантии транзакций (в том виде, как их реализует конкретная СУБД).
2. Indexing — ускоряет чтение ценой более дорогих операций записи и доп. памяти.
3. Normalization — уменьшает аномалии и повышает согласованность; денормализуем осознанно.
4. SQL vs NoSQL — разные модели данных и гарантии; NoSQL не обязательно «без ACID» и не всегда только eventual consistency.
5. Transactions — обеспечивают атомарность и изоляцию; поведение зависит от настроек уровня изоляции.

## Answer (EN)

**Database Theory:**
Database is an organized structure for storing and managing data. Main concepts: ACID (atomicity, consistency, isolation, durability), transactions (atomic units of work), indexes (speed up lookups), normalization (reduce redundancy and anomalies). SQL databases are relational; NoSQL databases are non-relational with various data models.

**1. SQL vs NoSQL:**

*Theory:* SQL databases use the relational model (tables, rows, columns), typically a defined schema, ACID transactions, and support complex queries with JOINs. NoSQL databases use various models (document, key-value, graph, column-family), offer flexible schemas, and often provide eventual or tunable consistency (some also support strong consistency), and are designed for horizontal scalability.

```kotlin
// SQL (Room/SQLite) — concrete relational example
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

// NoSQL-style (flexible document) example
data class UserDocument(
    val id: String = "",
    val name: String = "",
    val metadata: Map<String, Any> = emptyMap()  // Flexible!
)
```

**When to use SQL:**
- Complex queries with JOINs
- Strong ACID guarantees are critical
- Relatively stable schema
- Highly relational data

**When to use NoSQL:**
- Flexible or evolving schema
- High horizontal scalability requirements
- Simple access patterns
- Very high write throughput / large-scale data

**2. ACID Properties:**

*Theory:* ACID is the set of properties expected from transactions in database systems:
- Atomicity: all-or-nothing execution.
- Consistency: each committed transaction preserves all defined constraints; database moves from one valid state to another.
- Isolation: concurrent transactions do not see each other's intermediate states (to the degree provided by the configured isolation level).
- Durability: once a transaction is committed, its changes survive crashes (as implemented by the underlying storage engine).

Note: Framework annotations (e.g., Room's @Transaction) rely on the underlying DB engine; they do not by themselves create durability or isolation guarantees beyond what the engine provides.

```kotlin
// Atomic transfer example, relying on DB transactional semantics
@Database(entities = [Account::class], version = 1)
abstract class BankDatabase : RoomDatabase() {
    abstract fun accountDao(): AccountDao
}

@Dao
interface AccountDao {
    @Transaction
    suspend fun transfer(fromId: String, toId: String, amount: Int) {
        updateBalance(fromId, -amount)
        updateBalance(toId, amount)
    }

    @Query("UPDATE Account SET balance = balance + :delta WHERE id = :id")
    suspend fun updateBalance(id: String, delta: Int)
}

// Isolation, consistency, and durability specifics depend on the concrete DB (e.g., SQLite settings).
```

**3. Transactions and Concurrency Control:**

*Theory:* A transaction is a sequence of operations executed as a single atomic unit. Isolation levels define how and when changes from one transaction become visible to others:
- Read Uncommitted: allows dirty reads.
- Read Committed: no dirty reads.
- Repeatable Read: same row read multiple times within a transaction does not change; phantom reads may still occur.
- `Serializable`: full isolation equivalent to serial execution.

```kotlin
// Room transaction (uses underlying SQLite transaction)
suspend fun performComplexOperation() {
    database.withTransaction {
        val user = userDao.getUser("123")
        userDao.updateUser(user.copy(name = "Updated"))
        productDao.insertProducts(listOf(/* ... */))
        // All operations are part of a single transaction
    }
}

// Pessimistic locking concept (example SQL; not supported as-is by SQLite/Room with SELECT ... FOR UPDATE)
// SELECT * FROM Users WHERE id = :id FOR UPDATE;

// Optimistic locking with version field
@Entity
data class Product(
    @PrimaryKey val id: String,
    val name: String,
    @ColumnInfo(defaultValue = "0") val version: Int
)
```

**4. Indexing and Query Optimization:**

*Theory:* An index is a data structure (commonly a B-tree or variant) that speeds up lookups at the cost of extra writes and storage. It maintains an ordered (or otherwise searchable) structure over one or more columns.
- Typical lookup via index: O(log n) instead of scanning all rows O(n).
- Trade-offs: each INSERT/UPDATE/DELETE affecting indexed columns must also update the index, adding overhead; indexes consume disk/memory.
- Use indexes on columns frequently used in WHERE, JOIN conditions, and as foreign keys.

```kotlin
// Indexes in Room
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
    // Uses index on userId
    @Query("SELECT * FROM Task WHERE userId = :userId")
    suspend fun getTasksByUser(userId: String): List<Task>

    // Composite index (userId, status) is well-suited for this predicate
    @Query("SELECT * FROM Task WHERE userId = :userId AND status = :status")
    suspend fun getTasks(userId: String, status: String): List<Task>

    // If the composite index were defined as (status, userId), the access pattern should lead with status
    // to fully benefit from index ordering.
}
```

**Index trade-offs (simplified intuition, not strict for all engines):**
- SELECT: can drop from O(n) scan to O(log n) or better with suitable index.
- INSERT/UPDATE/DELETE: become slightly more expensive when affected columns are indexed due to index maintenance.

**5. Normalization and Denormalization:**

*Theory:* Normalization is organizing data to reduce redundancy and avoid anomalies.
- 1NF: atomic column values, no repeating groups.
- 2NF: 1NF and no partial dependency of non-key attributes on part of a composite key.
- 3NF: 2NF and no transitive dependencies of non-key attributes on the primary key.
Denormalization intentionally adds some redundancy to improve read performance when justified by access patterns.

```kotlin
// Unnormalized: redundancy issues
data class OrderUnnormalized(
    val orderId: String,
    val customerName: String,
    val customerEmail: String,
    val productName: String,
    val productPrice: Double
)
// Problem: customer and product data repeated per order line.

// 1NF: atomic values, no repeating groups
@Entity
data class Order1NF(
    @PrimaryKey val orderId: String,
    val customerId: String,
    val productId: String
)

// Further normalization: separate entities and relations
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

@Entity(
    foreignKeys = [
        ForeignKey(entity = Customer::class, parentColumns = ["id"], childColumns = ["customerId"]),
        ForeignKey(entity = Product::class, parentColumns = ["id"], childColumns = ["productId"])
    ]
)
data class OrderNormalized(
    @PrimaryKey val id: String,
    val customerId: String,
    val productId: String
)

// 3NF example: avoid transitive dependencies
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
    val cityId: String  // countryId derivable via city -> country
)
```

**6. Database Design Principles:**

*Theory:* Core principles:
- Choose appropriate data types.
- Use foreign keys (where supported) to enforce referential integrity.
- Normalize to at least 3NF where appropriate; denormalize only when access patterns and performance justify it.
- Create indexes for frequent and performance-critical queries.
- Consider partitioning for very large tables.
- Plan backup/restore, security (auth, access control, encryption).

```kotlin
// Example schema quality aspects
@Entity(
    foreignKeys = [
        ForeignKey(
            entity = Customer::class,
            parentColumns = ["id"],
            childColumns = ["customerId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("customerId")]
)
data class Order(
    @PrimaryKey val id: String,
    val customerId: String,
    @ColumnInfo(typeAffinity = ColumnInfo.REAL) val total: Double
)
```

**7. Room Database Best Practices:**

*Theory:* Room is an SQLite abstraction layer for Android used for local persistence and caching. It is included here as a concrete example of relational database usage in applications. Key components: Entity (tables), DAO (data access objects), Database (RoomDatabase). Use:
- `Flow`/`LiveData` for reactive queries.
- @Transaction / withTransaction for atomic operations.
- Migrations for schema changes across versions.

```kotlin
// Room setup
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

// Reactive queries with Flow
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>  // Observers get updates on DB changes
}

// Migrations example
@Database(entities = [User::class], version = 2)
abstract class AppDatabaseV2 : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(database: SupportSQLiteDatabase) {
                database.execSQL("ALTER TABLE users ADD COLUMN avatar TEXT")
            }
        }

        fun create(context: Context): AppDatabaseV2 {
            return Room.databaseBuilder(context, AppDatabaseV2::class.java, "app.db")
                .addMigrations(MIGRATION_1_2)
                .build()
        }
    }
}
```

**Key Concepts:**

1. ACID - transactional guarantees (as implemented by the specific DB engine).
2. Indexing - improves reads at the cost of slower writes and extra storage.
3. Normalization - reduces anomalies and improves consistency; denormalize selectively.
4. SQL vs NoSQL - different data models, guarantees, and trade-offs; NoSQL is not inherently "non-ACID" or "eventually consistent only".
5. Transactions - provide atomicity and isolation for correctness; behavior depends on configured isolation levels.

---

## Дополнительные Вопросы (RU)

- Как вы управляете миграциями базы данных в продакшене?
- В чем разница между оптимистичной и пессимистичной блокировкой?
- Когда имеет смысл денормализовать базу данных?

## Follow-ups

- How do you handle database migrations in production?
- What is the difference between optimistic and pessimistic locking?
- When should you denormalize a database?

## Связанные Вопросы (RU)

### Предпосылки (проще)
- Базовые концепции баз данных
- Основы SQL

### Связанные (тот Же уровень)
- [[q-sql-nosql-databases--system-design--medium]] — подробное сравнение SQL vs NoSQL
- [[c-relational-databases]] — реляционные базы данных

### Продвинутое (сложнее)
- Шардинг и партиционирование баз данных
- Распределенные системы управления базами данных
- Продвинутые стратегии индексирования

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

## References

- [[c-relational-databases]]
- [[c-database-design]]
- "https://en.wikipedia.org/wiki/Database"