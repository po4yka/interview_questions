---
id: 20251012-12271122
title: "SQLDelight в KMM / SQLDelight in KMM"
aliases: ["SQLDelight в KMM", "SQLDelight in KMM", "SQLDelight для мультиплатформы"]
topic: android
subtopics: [kmm, databases, multiplatform]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-annotation-processing-android--android--medium, q-gradle-kotlin-dsl-vs-groovy--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/kmm, android/databases, Database, difficulty/medium, KMM, Kotlin, SQLDelight, multiplatform]
date created: Tuesday, October 28th 2025, 9:23:21 pm
date modified: Thursday, October 30th 2025, 3:11:49 pm
---

# Вопрос (RU)

> Как использовать SQLDelight для кросс-платформенного управления БД в KMM? Как определять схемы, выполнять миграции, работать с транзакциями и оптимизировать запросы для Android и iOS?

## Ответ (RU)

SQLDelight генерирует type-safe Kotlin API из SQL-запросов, обеспечивая compile-time верификацию и использование platform-specific драйверов (SQLite на Android, SQLite.swift на iOS) при sharing общей database-логики.

#### Настройка и Конфигурация

**Gradle Configuration**:
```kotlin
// shared/build.gradle.kts
plugins {
    kotlin("multiplatform")
    id("app.cash.sqldelight")
}

sqldelight {
    databases {
        create("TaskDatabase") {
            packageName.set("com.example.db")
            generateAsync.set(true)
            verifyMigrations.set(true)
        }
    }
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("app.cash.sqldelight:runtime:2.0+")
            implementation("app.cash.sqldelight:coroutines-extensions:2.0+")
        }
        androidMain.dependencies {
            // ✅ Platform-specific driver
            implementation("app.cash.sqldelight:android-driver:2.0+")
        }
        iosMain.dependencies {
            implementation("app.cash.sqldelight:native-driver:2.0+")
        }
    }
}
```

#### Определение Схемы

**SQL Schema** (`Task.sq`):
```sql
-- shared/src/commonMain/sqldelight/com/example/db/Task.sq

CREATE TABLE Task (
    id TEXT NOT NULL PRIMARY KEY,
    title TEXT NOT NULL,
    completed INTEGER AS Boolean NOT NULL DEFAULT 0,
    priority INTEGER NOT NULL DEFAULT 0,
    dueDate INTEGER,
    userId TEXT NOT NULL,
    FOREIGN KEY (userId) REFERENCES User(id) ON DELETE CASCADE
);

CREATE INDEX task_userId ON Task(userId);
CREATE INDEX task_completed_priority ON Task(completed, priority)
WHERE completed = 0;  -- ✅ Partial index для активных задач

-- Named Queries
selectAll:
SELECT * FROM Task
ORDER BY
    CASE WHEN completed = 0 THEN 0 ELSE 1 END,
    priority DESC,
    dueDate ASC NULLS LAST;

selectByUserId:
SELECT * FROM Task
WHERE userId = :userId
ORDER BY priority DESC;

insertTask:
INSERT INTO Task (id, title, completed, priority, dueDate, userId)
VALUES (?, ?, ?, ?, ?, ?);

updateTask:
UPDATE Task SET
    title = :title,
    priority = :priority,
    completed = :completed
WHERE id = :id;
```

#### Platform-Specific Drivers

**Android Driver**:
```kotlin
// androidMain
actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(
            schema = TaskDatabase.Schema,
            context = context,
            name = "task.db",
            callback = object : AndroidSqliteDriver.Callback(TaskDatabase.Schema) {
                override fun onOpen(db: SupportSQLiteDatabase) {
                    super.onOpen(db)
                    // ✅ Enable WAL for better concurrency
                    db.execSQL("PRAGMA journal_mode=WAL;")
                    db.execSQL("PRAGMA foreign_keys=ON;")
                }
            }
        )
    }
}
```

**iOS Driver**:
```kotlin
// iosMain
actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = TaskDatabase.Schema,
            name = "task.db",
            onConfiguration = { config ->
                config.copy(
                    extendedConfig = DatabaseConfiguration.Extended(
                        foreignKeyConstraints = true
                    )
                )
            }
        )
    }
}
```

#### Использование Type-Safe API

```kotlin
// commonMain
class TaskRepository(
    driverFactory: DatabaseDriverFactory,
    private val dispatchers: CoroutineDispatchers
) {
    private val database = TaskDatabase(driverFactory.createDriver())
    private val queries = database.taskQueries

    // ✅ Reactive Flow-based query
    fun observeTasks(): Flow<List<Task>> {
        return queries.selectAll()
            .asFlow()
            .mapToList(dispatchers.io)
    }

    suspend fun getTaskById(id: String): Task? = withContext(dispatchers.io) {
        queries.selectById(id).executeAsOneOrNull()
    }

    suspend fun insertTask(task: Task) = withContext(dispatchers.io) {
        queries.insertTask(
            id = task.id,
            title = task.title,
            completed = task.completed,
            priority = task.priority.toLong(),
            dueDate = task.dueDate,
            userId = task.userId
        )
    }

    // ✅ Transaction для bulk операций
    suspend fun insertMultiple(tasks: List<Task>) = withContext(dispatchers.io) {
        queries.transaction {
            tasks.forEach { insertTask(it) }
        }
    }
}
```

#### Миграции

**Migration Files** (`.sqm`):
```sql
-- migrations/1.sqm
ALTER TABLE Task ADD COLUMN priority INTEGER NOT NULL DEFAULT 0;
CREATE INDEX task_priority ON Task(priority);

-- migrations/2.sqm
ALTER TABLE Task ADD COLUMN dueDate INTEGER;
```

**Manual Migration Handler**:
```kotlin
// androidMain
override fun onUpgrade(
    db: SupportSQLiteDatabase,
    oldVersion: Int,
    newVersion: Int
) {
    when (oldVersion) {
        1 -> db.execSQL("ALTER TABLE Task ADD COLUMN priority INTEGER DEFAULT 0")
        2 -> db.execSQL("ALTER TABLE Task ADD COLUMN dueDate INTEGER")
    }
}
```

#### Оптимизация

**Pagination**:
```sql
selectTasksPaginated:
SELECT * FROM Task
WHERE userId = :userId
ORDER BY priority DESC
LIMIT :limit OFFSET :offset;
```

**Batching**:
```kotlin
suspend fun insertBatch(tasks: List<Task>) = withContext(dispatchers.io) {
    queries.transaction {
        // ✅ Chunk по 500 для избежания SQL variable limit
        tasks.chunked(500).forEach { batch ->
            batch.forEach { queries.insertTask(...) }
        }
    }
}
```

**Custom Type Adapters**:
```kotlin
object TaskPriorityAdapter : ColumnAdapter<TaskPriority, Long> {
    override fun decode(databaseValue: Long): TaskPriority {
        return TaskPriority.values()[databaseValue.toInt()]
    }

    override fun encode(value: TaskPriority): Long {
        return value.ordinal.toLong()
    }
}

val database = TaskDatabase(
    driver = driver,
    TaskAdapter = Task.Adapter(priorityAdapter = TaskPriorityAdapter)
)
```

#### Testing

```kotlin
class TaskRepositoryTest {
    private lateinit var repository: TaskRepository

    @BeforeTest
    fun setup() {
        // ✅ In-memory database для unit-тестов
        val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
        TaskDatabase.Schema.create(driver)
        repository = TaskRepository(
            object : DatabaseDriverFactory {
                override fun createDriver() = driver
            },
            TestDispatchers
        )
    }

    @Test
    fun insertAndRetrieveTask() = runTest {
        val task = Task(id = "1", title = "Test", ...)
        repository.insertTask(task)
        val retrieved = repository.getTaskById("1")
        assertEquals(task, retrieved)
    }
}
```

#### Best Practices

1. **Schema Design**: используйте foreign keys, indexes для frequently queried columns, partial indexes для filtered queries
2. **Transactions**: группируйте related operations, держите transactions короткими, handle errors properly
3. **Performance**: включайте WAL mode на Android, используйте batching для bulk operations, pagination для больших datasets
4. **Migrations**: тестируйте thoroughly, используйте `verifyMigrations` в development, документируйте schema changes

---

# Question (EN)

> How to use SQLDelight for cross-platform database management in KMM? How to define schemas, handle migrations, work with transactions, and optimize queries for Android and iOS?

## Answer (EN)

SQLDelight generates type-safe Kotlin APIs from SQL statements, providing compile-time verification and platform-specific drivers (SQLite on Android, SQLite.swift on iOS) while sharing database logic across platforms.

#### Setup and Configuration

**Gradle Configuration**:
```kotlin
// shared/build.gradle.kts
plugins {
    kotlin("multiplatform")
    id("app.cash.sqldelight")
}

sqldelight {
    databases {
        create("TaskDatabase") {
            packageName.set("com.example.db")
            generateAsync.set(true)
            verifyMigrations.set(true)
        }
    }
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("app.cash.sqldelight:runtime:2.0+")
            implementation("app.cash.sqldelight:coroutines-extensions:2.0+")
        }
        androidMain.dependencies {
            // ✅ Platform-specific driver
            implementation("app.cash.sqldelight:android-driver:2.0+")
        }
        iosMain.dependencies {
            implementation("app.cash.sqldelight:native-driver:2.0+")
        }
    }
}
```

#### Schema Definition

**SQL Schema** (`Task.sq`):
```sql
-- shared/src/commonMain/sqldelight/com/example/db/Task.sq

CREATE TABLE Task (
    id TEXT NOT NULL PRIMARY KEY,
    title TEXT NOT NULL,
    completed INTEGER AS Boolean NOT NULL DEFAULT 0,
    priority INTEGER NOT NULL DEFAULT 0,
    dueDate INTEGER,
    userId TEXT NOT NULL,
    FOREIGN KEY (userId) REFERENCES User(id) ON DELETE CASCADE
);

CREATE INDEX task_userId ON Task(userId);
CREATE INDEX task_completed_priority ON Task(completed, priority)
WHERE completed = 0;  -- ✅ Partial index for active tasks

-- Named Queries
selectAll:
SELECT * FROM Task
ORDER BY
    CASE WHEN completed = 0 THEN 0 ELSE 1 END,
    priority DESC,
    dueDate ASC NULLS LAST;

selectByUserId:
SELECT * FROM Task
WHERE userId = :userId
ORDER BY priority DESC;

insertTask:
INSERT INTO Task (id, title, completed, priority, dueDate, userId)
VALUES (?, ?, ?, ?, ?, ?);

updateTask:
UPDATE Task SET
    title = :title,
    priority = :priority,
    completed = :completed
WHERE id = :id;
```

#### Platform-Specific Drivers

**Android Driver**:
```kotlin
// androidMain
actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(
            schema = TaskDatabase.Schema,
            context = context,
            name = "task.db",
            callback = object : AndroidSqliteDriver.Callback(TaskDatabase.Schema) {
                override fun onOpen(db: SupportSQLiteDatabase) {
                    super.onOpen(db)
                    // ✅ Enable WAL for better concurrency
                    db.execSQL("PRAGMA journal_mode=WAL;")
                    db.execSQL("PRAGMA foreign_keys=ON;")
                }
            }
        )
    }
}
```

**iOS Driver**:
```kotlin
// iosMain
actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = TaskDatabase.Schema,
            name = "task.db",
            onConfiguration = { config ->
                config.copy(
                    extendedConfig = DatabaseConfiguration.Extended(
                        foreignKeyConstraints = true
                    )
                )
            }
        )
    }
}
```

#### Type-Safe API Usage

```kotlin
// commonMain
class TaskRepository(
    driverFactory: DatabaseDriverFactory,
    private val dispatchers: CoroutineDispatchers
) {
    private val database = TaskDatabase(driverFactory.createDriver())
    private val queries = database.taskQueries

    // ✅ Reactive Flow-based query
    fun observeTasks(): Flow<List<Task>> {
        return queries.selectAll()
            .asFlow()
            .mapToList(dispatchers.io)
    }

    suspend fun getTaskById(id: String): Task? = withContext(dispatchers.io) {
        queries.selectById(id).executeAsOneOrNull()
    }

    suspend fun insertTask(task: Task) = withContext(dispatchers.io) {
        queries.insertTask(
            id = task.id,
            title = task.title,
            completed = task.completed,
            priority = task.priority.toLong(),
            dueDate = task.dueDate,
            userId = task.userId
        )
    }

    // ✅ Transaction for bulk operations
    suspend fun insertMultiple(tasks: List<Task>) = withContext(dispatchers.io) {
        queries.transaction {
            tasks.forEach { insertTask(it) }
        }
    }
}
```

#### Migrations

**Migration Files** (`.sqm`):
```sql
-- migrations/1.sqm
ALTER TABLE Task ADD COLUMN priority INTEGER NOT NULL DEFAULT 0;
CREATE INDEX task_priority ON Task(priority);

-- migrations/2.sqm
ALTER TABLE Task ADD COLUMN dueDate INTEGER;
```

**Manual Migration Handler**:
```kotlin
// androidMain
override fun onUpgrade(
    db: SupportSQLiteDatabase,
    oldVersion: Int,
    newVersion: Int
) {
    when (oldVersion) {
        1 -> db.execSQL("ALTER TABLE Task ADD COLUMN priority INTEGER DEFAULT 0")
        2 -> db.execSQL("ALTER TABLE Task ADD COLUMN dueDate INTEGER")
    }
}
```

#### Optimization

**Pagination**:
```sql
selectTasksPaginated:
SELECT * FROM Task
WHERE userId = :userId
ORDER BY priority DESC
LIMIT :limit OFFSET :offset;
```

**Batching**:
```kotlin
suspend fun insertBatch(tasks: List<Task>) = withContext(dispatchers.io) {
    queries.transaction {
        // ✅ Chunk by 500 to avoid SQL variable limit
        tasks.chunked(500).forEach { batch ->
            batch.forEach { queries.insertTask(...) }
        }
    }
}
```

**Custom Type Adapters**:
```kotlin
object TaskPriorityAdapter : ColumnAdapter<TaskPriority, Long> {
    override fun decode(databaseValue: Long): TaskPriority {
        return TaskPriority.values()[databaseValue.toInt()]
    }

    override fun encode(value: TaskPriority): Long {
        return value.ordinal.toLong()
    }
}

val database = TaskDatabase(
    driver = driver,
    TaskAdapter = Task.Adapter(priorityAdapter = TaskPriorityAdapter)
)
```

#### Testing

```kotlin
class TaskRepositoryTest {
    private lateinit var repository: TaskRepository

    @BeforeTest
    fun setup() {
        // ✅ In-memory database for unit tests
        val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
        TaskDatabase.Schema.create(driver)
        repository = TaskRepository(
            object : DatabaseDriverFactory {
                override fun createDriver() = driver
            },
            TestDispatchers
        )
    }

    @Test
    fun insertAndRetrieveTask() = runTest {
        val task = Task(id = "1", title = "Test", ...)
        repository.insertTask(task)
        val retrieved = repository.getTaskById("1")
        assertEquals(task, retrieved)
    }
}
```

#### Best Practices

1. **Schema Design**: use foreign keys, indexes for frequently queried columns, partial indexes for filtered queries
2. **Transactions**: group related operations, keep transactions short, handle errors properly
3. **Performance**: enable WAL mode on Android, use batching for bulk operations, pagination for large datasets
4. **Migrations**: test thoroughly, use `verifyMigrations` in development, document schema changes

---

## Follow-ups

- How to implement full-text search with SQLDelight FTS5 virtual tables?
- What are the trade-offs between SQLDelight and Room for KMM projects?
- How to handle schema conflicts during multi-way sync in SQLDelight?
- How to profile and optimize complex JOIN queries in SQLDelight?
- How to implement database encryption in KMM using SQLCipher?

## References

- SQLDelight official documentation
- KMM architecture best practices
- SQLite optimization guide
- Platform-specific database drivers comparison

## Related Questions

### Prerequisites
- [[q-kmm-architecture--android--easy]] - Understanding KMM project structure and expect/actual mechanism
- [[q-sqlite-basics--databases--easy]] - SQL fundamentals and SQLite-specific features

### Related
- [[q-annotation-processing-android--android--medium]] - Code generation comparison with SQLDelight
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]] - Gradle configuration for multiplatform projects
- [[q-room-migration--android--medium]] - Alternative database solution comparison

### Advanced
- [[q-kmm-testing-strategies--android--hard]] - Testing multiplatform database code
- [[q-database-encryption--android--hard]] - Securing SQLDelight databases with SQLCipher
