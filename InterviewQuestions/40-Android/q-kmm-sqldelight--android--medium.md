---
id: android-416
title: SQLDelight в KMM / SQLDelight in KMM
aliases:
- SQLDelight in KMM
- SQLDelight в KMM
- SQLDelight для мультиплатформы
topic: android
subtopics:
- kmp
- room
- sqldelight
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-room
- q-annotation-processing-android--android--medium
- q-gradle-kotlin-dsl-vs-groovy--android--medium
created: 2025-10-15
updated: 2025-10-31
sources: []
tags:
- android/kmp
- android/room
- android/sqldelight
- Database
- difficulty/medium
- KMM
- Kotlin
- multiplatform
- SQLDelight
---

# Вопрос (RU)

> Как использовать SQLDelight для кросс-платформенного управления БД в KMM? Как определять схемы, выполнять миграции, работать с транзакциями и оптимизировать запросы для Android и iOS?


# Question (EN)

> How to use SQLDelight for cross-platform database management in KMM? How to define schemas, handle migrations, work with transactions, and optimize queries for Android and iOS?


---

## Ответ (RU)

SQLDelight генерирует type-safe Kotlin API из SQL-запросов, обеспечивая compile-time верификацию и использование platform-specific драйверов (AndroidSqliteDriver на Android, NativeSqliteDriver на iOS) при шаринге общей database-логики.

#### Настройка и конфигурация

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
        commonTest.dependencies {
            implementation("app.cash.sqldelight:sqlite-driver:2.0+") // для in-memory/JVM тестов
        }
    }
}
```

#### Определение схемы

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

selectById:
SELECT * FROM Task
WHERE id = :id;

insertTask:
INSERT INTO Task (id, title, completed, priority, dueDate, userId)
VALUES (:id, :title, :completed, :priority, :dueDate, :userId);

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
                    // ✅ Дополнительная настройка по необходимости
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
            name = "task.db"
        )
    }
}
```

#### Использование type-safe API

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

    // ✅ Transaction для bulk операций без suspend внутри блока транзакции
    suspend fun insertMultiple(tasks: List<Task>) = withContext(dispatchers.io) {
        queries.transaction {
            tasks.forEach { task ->
                queries.insertTask(
                    id = task.id,
                    title = task.title,
                    completed = task.completed,
                    priority = task.priority.toLong(),
                    dueDate = task.dueDate,
                    userId = task.userId
                )
            }
        }
    }
}
```

#### Миграции

Для SQLDelight 2.x миграции обычно задаются `.sqm` файлами. Пример:

**Migration Files** (`.sqm`):
```sql
-- src/commonMain/sqldelight/com/example/db/migrations/1.sqm
ALTER TABLE Task ADD COLUMN priority INTEGER NOT NULL DEFAULT 0;
CREATE INDEX task_priority ON Task(priority);

-- src/commonMain/sqldelight/com/example/db/migrations/2.sqm
ALTER TABLE Task ADD COLUMN dueDate INTEGER;
```

При включённом `verifyMigrations = true` SQLDelight проверяет согласованность схемы и миграций. Ручная реализация `onUpgrade` в драйвере при этом обычно не требуется и может конфликтовать с auto-generated миграциями.

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
        // ✅ Пример групповых вставок внутри одной транзакции
        tasks.forEach { task ->
            queries.insertTask(
                id = task.id,
                title = task.title,
                completed = task.completed,
                priority = task.priority.toLong(),
                dueDate = task.dueDate,
                userId = task.userId
            )
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
        // ✅ In-memory database для unit-тестов (JVM)
        val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
        TaskDatabase.Schema.create(driver)
        repository = TaskRepository(
            driverFactory = object : DatabaseDriverFactory(/* platform stub if needed */) {
                fun createDriver(): SqlDriver = driver
            },
            dispatchers = TestDispatchers
        )
    }

    @Test
    fun insertAndRetrieveTask() = runTest {
        val task = Task(id = "1", title = "Test", /* ... */)
        repository.insertTask(task)
        val retrieved = repository.getTaskById("1")
        assertEquals(task, retrieved)
    }
}
```

(Тестовый пример концептуальный; в реальном KMM-проекте `DatabaseDriverFactory` обычно объявляется как `expect`/`actual`, и для JVM-тестов можно использовать отдельную реализацию.)

#### Best Practices

1. **Schema Design**: используйте foreign keys, индексы для часто запрашиваемых колонок, partial indexes для фильтрованных запросов.
2. **Transactions**: группируйте связанные операции, держите транзакции короткими, обрабатывайте ошибки; избегайте `suspend` внутри блока `transaction {}`.
3. **Performance**: используйте batching для bulk операций, pagination для больших datasets; дополнительные PRAGMA-настройки применяйте осознанно.
4. **Migrations**: тестируйте миграции, используйте `verifyMigrations`, избегайте дублирования логики миграций между `.sqm` и ручным `onUpgrade`.

---

## Answer (EN)

SQLDelight generates type-safe Kotlin APIs from SQL statements, providing compile-time verification and platform-specific drivers (AndroidSqliteDriver on Android, NativeSqliteDriver on iOS) while sharing database logic across platforms.

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
        commonTest.dependencies {
            implementation("app.cash.sqldelight:sqlite-driver:2.0+") // for in-memory/JVM tests
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

selectById:
SELECT * FROM Task
WHERE id = :id;

insertTask:
INSERT INTO Task (id, title, completed, priority, dueDate, userId)
VALUES (:id, :title, :completed, :priority, :dueDate, :userId);

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
                    // ✅ Additional tuning if needed
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
            name = "task.db"
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

    // ✅ Transaction for bulk operations without suspend calls inside the transaction block
    suspend fun insertMultiple(tasks: List<Task>) = withContext(dispatchers.io) {
        queries.transaction {
            tasks.forEach { task ->
                queries.insertTask(
                    id = task.id,
                    title = task.title,
                    completed = task.completed,
                    priority = task.priority.toLong(),
                    dueDate = task.dueDate,
                    userId = task.userId
                )
            }
        }
    }
}
```

#### Migrations

For SQLDelight 2.x, migrations are typically defined via `.sqm` files. Example:

**Migration Files** (`.sqm`):
```sql
-- src/commonMain/sqldelight/com/example/db/migrations/1.sqm
ALTER TABLE Task ADD COLUMN priority INTEGER NOT NULL DEFAULT 0;
CREATE INDEX task_priority ON Task(priority);

-- src/commonMain/sqldelight/com/example/db/migrations/2.sqm
ALTER TABLE Task ADD COLUMN dueDate INTEGER;
```

With `verifyMigrations = true`, SQLDelight validates that migrations produce the expected schema. A manual `onUpgrade` implementation in the driver is generally not needed and can conflict with SQLDelight-managed migrations.

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
        // ✅ Example of batched inserts within a single transaction
        tasks.forEach { task ->
            queries.insertTask(
                id = task.id,
                title = task.title,
                completed = task.completed,
                priority = task.priority.toLong(),
                dueDate = task.dueDate,
                userId = task.userId
            )
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
        // ✅ In-memory database for JVM unit tests
        val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
        TaskDatabase.Schema.create(driver)
        repository = TaskRepository(
            driverFactory = object : DatabaseDriverFactory(/* platform stub if needed */) {
                fun createDriver(): SqlDriver = driver
            },
            dispatchers = TestDispatchers
        )
    }

    @Test
    fun insertAndRetrieveTask() = runTest {
        val task = Task(id = "1", title = "Test", /* ... */)
        repository.insertTask(task)
        val retrieved = repository.getTaskById("1")
        assertEquals(task, retrieved)
    }
}
```

(This test snippet is conceptual; in a real KMM setup, `DatabaseDriverFactory` is usually declared as `expect`/`actual`, and tests use a dedicated test driver implementation.)

#### Best Practices

1. **Schema Design**: use foreign keys, indexes for frequently queried columns, partial indexes for filtered queries.
2. **Transactions**: group related operations, keep transactions short, handle errors; avoid `suspend` calls inside `transaction {}` blocks.
3. **Performance**: use batching for bulk operations, pagination for large datasets; apply extra PRAGMA tuning only when appropriate.
4. **Migrations**: test migrations, use `verifyMigrations`, and avoid duplicating migration logic between `.sqm` files and manual `onUpgrade`.

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

### Prerequisites / Concepts

- [[c-room]]


### Related
- [[q-annotation-processing-android--android--medium]] - Code generation comparison with SQLDelight
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]] - Gradle configuration for multiplatform projects
