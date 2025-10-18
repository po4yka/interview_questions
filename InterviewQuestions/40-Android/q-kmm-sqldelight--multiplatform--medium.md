---
id: 20251012-12271122
title: "Kmm Sqldelight / SQLDelight в KMM"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-annotation-processing-android--android--medium, q-play-feature-delivery--android--medium, q-gradle-kotlin-dsl-vs-groovy--android--medium]
created: 2025-10-15
tags: [Kotlin, KMM, SQLDelight, Database, difficulty/medium]
---
# SQLDelight for Multiplatform Database

# Question (EN)
> 
Explain how to use SQLDelight for cross-platform database management in KMM. How do you define schemas, handle migrations, implement transactions, and optimize queries for both Android and iOS?

## Answer (EN)
SQLDelight generates type-safe Kotlin APIs from SQL statements, providing compile-time verification and platform-specific drivers (SQLite on Android, SQLite.swift on iOS) while sharing database logic across platforms.

#### SQLDelight Setup

**1. Dependencies and Configuration**
```kotlin
// build.gradle.kts (project level)
plugins {
    id("app.cash.sqldelight") version "2.0.1" apply false
}

// shared/build.gradle.kts
plugins {
    kotlin("multiplatform")
    id("app.cash.sqldelight")
}

sqldelight {
    databases {
        create("TaskDatabase") {
            packageName.set("com.example.taskapp.db")

            // Generate async extensions
            generateAsync.set(true)

            // Verify migrations
            verifyMigrations.set(true)

            // Source folders
            srcDirs.setFrom("src/commonMain/sqldelight")
        }
    }
}

kotlin {
    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("app.cash.sqldelight:runtime:2.0.1")
                implementation("app.cash.sqldelight:coroutines-extensions:2.0.1")
            }
        }

        val androidMain by getting {
            dependencies {
                implementation("app.cash.sqldelight:android-driver:2.0.1")
            }
        }

        val iosMain by getting {
            dependencies {
                implementation("app.cash.sqldelight:native-driver:2.0.1")
            }
        }
    }
}
```

**2. Database Schema Definition**
```sql
-- shared/src/commonMain/sqldelight/com/example/taskapp/db/Task.sq

CREATE TABLE Task (
    id TEXT NOT NULL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    completed INTEGER AS Boolean NOT NULL DEFAULT 0,
    priority INTEGER NOT NULL DEFAULT 0,
    dueDate INTEGER,  -- Unix timestamp in milliseconds
    createdAt INTEGER NOT NULL,
    updatedAt INTEGER NOT NULL,
    categoryId TEXT,
    userId TEXT NOT NULL,
    FOREIGN KEY (categoryId) REFERENCES Category(id) ON DELETE SET NULL,
    FOREIGN KEY (userId) REFERENCES User(id) ON DELETE CASCADE
);

CREATE INDEX task_userId ON Task(userId);
CREATE INDEX task_categoryId ON Task(categoryId);
CREATE INDEX task_dueDate ON Task(dueDate);
CREATE INDEX task_completed ON Task(completed);

-- Category table
CREATE TABLE Category (
    id TEXT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    color TEXT NOT NULL,
    icon TEXT,
    createdAt INTEGER NOT NULL
);

-- User table
CREATE TABLE User (
    id TEXT NOT NULL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    avatarUrl TEXT,
    createdAt INTEGER NOT NULL
);

-- Queries

-- Get all tasks
selectAll:
SELECT * FROM Task
ORDER BY
    CASE WHEN completed = 0 THEN 0 ELSE 1 END,
    priority DESC,
    dueDate ASC NULLS LAST,
    createdAt DESC;

-- Get task by ID
selectById:
SELECT * FROM Task
WHERE id = :id;

-- Get tasks by user
selectByUserId:
SELECT * FROM Task
WHERE userId = :userId
ORDER BY createdAt DESC;

-- Get tasks by category
selectByCategory:
SELECT * FROM Task
WHERE categoryId = :categoryId
ORDER BY createdAt DESC;

-- Get active tasks (not completed)
selectActiveTasks:
SELECT * FROM Task
WHERE completed = 0 AND userId = :userId
ORDER BY
    priority DESC,
    dueDate ASC NULLS LAST;

-- Get completed tasks
selectCompletedTasks:
SELECT * FROM Task
WHERE completed = 1 AND userId = :userId
ORDER BY updatedAt DESC;

-- Get overdue tasks
selectOverdueTasks:
SELECT * FROM Task
WHERE completed = 0
  AND dueDate IS NOT NULL
  AND dueDate < :currentTime
  AND userId = :userId
ORDER BY dueDate ASC;

-- Get tasks due today
selectTasksDueToday:
SELECT * FROM Task
WHERE completed = 0
  AND dueDate >= :startOfDay
  AND dueDate < :endOfDay
  AND userId = :userId
ORDER BY dueDate ASC;

-- Search tasks
searchTasks:
SELECT * FROM Task
WHERE userId = :userId
  AND (
    title LIKE '%' || :query || '%'
    OR description LIKE '%' || :query || '%'
  )
ORDER BY createdAt DESC;

-- Count tasks by status
countByStatus:
SELECT
    COUNT(CASE WHEN completed = 0 THEN 1 END) AS activeCount,
    COUNT(CASE WHEN completed = 1 THEN 1 END) AS completedCount
FROM Task
WHERE userId = :userId;

-- Insert task
insertTask:
INSERT INTO Task (
    id, title, description, completed, priority,
    dueDate, createdAt, updatedAt, categoryId, userId
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);

-- Update task
updateTask:
UPDATE Task
SET
    title = :title,
    description = :description,
    completed = :completed,
    priority = :priority,
    dueDate = :dueDate,
    updatedAt = :updatedAt,
    categoryId = :categoryId
WHERE id = :id;

-- Toggle completion
toggleCompletion:
UPDATE Task
SET
    completed = NOT completed,
    updatedAt = :updatedAt
WHERE id = :id;

-- Delete task
deleteTask:
DELETE FROM Task
WHERE id = :id;

-- Delete completed tasks
deleteCompletedTasks:
DELETE FROM Task
WHERE completed = 1 AND userId = :userId;

-- Get task with category
selectTaskWithCategory:
SELECT
    Task.*,
    Category.name AS categoryName,
    Category.color AS categoryColor,
    Category.icon AS categoryIcon
FROM Task
LEFT JOIN Category ON Task.categoryId = Category.id
WHERE Task.id = :taskId;

-- Get tasks grouped by category
selectTasksGroupedByCategory:
SELECT
    Category.id AS categoryId,
    Category.name AS categoryName,
    Category.color AS categoryColor,
    COUNT(Task.id) AS taskCount
FROM Category
LEFT JOIN Task ON Category.id = Task.categoryId AND Task.userId = :userId
GROUP BY Category.id
ORDER BY taskCount DESC, Category.name ASC;
```

#### Database Driver Factory

**1. Platform-Specific Drivers**
```kotlin
// commonMain - Driver factory interface
expect class DatabaseDriverFactory {
    fun createDriver(): SqlDriver
}

// androidMain - Android implementation
actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(
            schema = TaskDatabase.Schema,
            context = context,
            name = "task.db",
            callback = object : AndroidSqliteDriver.Callback(TaskDatabase.Schema) {
                override fun onOpen(db: SupportSQLiteDatabase) {
                    super.onOpen(db)
                    // Enable foreign keys
                    db.execSQL("PRAGMA foreign_keys=ON;")
                    // Enable WAL mode for better concurrency
                    db.execSQL("PRAGMA journal_mode=WAL;")
                }
            }
        )
    }
}

// iosMain - iOS implementation
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

**2. Database Wrapper**
```kotlin
// commonMain/database/TaskDatabaseWrapper.kt
class TaskDatabaseWrapper(
    driverFactory: DatabaseDriverFactory
) {
    private val driver = driverFactory.createDriver()
    private val database = TaskDatabase(driver)

    val taskQueries = database.taskQueries
    val categoryQueries = database.categoryQueries
    val userQueries = database.userQueries

    // Close database
    fun close() {
        driver.close()
    }
}

// Dependency injection
val databaseModule = module {
    single { DatabaseDriverFactory(androidContext()) }
    single { TaskDatabaseWrapper(get()) }
}
```

#### Type-Safe Queries

**1. Generated API Usage**
```kotlin
// commonMain/repository/TaskRepository.kt
class TaskRepository(
    private val database: TaskDatabaseWrapper,
    private val dispatchers: CoroutineDispatchers
) {
    private val queries = database.taskQueries

    // Get all tasks as Flow
    fun observeAllTasks(): Flow<List<Task>> {
        return queries.selectAll()
            .asFlow()
            .mapToList(dispatchers.io)
    }

    // Get single task
    suspend fun getTaskById(id: String): Task? = withContext(dispatchers.io) {
        queries.selectById(id).executeAsOneOrNull()
    }

    // Get tasks by user
    fun observeTasksByUser(userId: String): Flow<List<Task>> {
        return queries.selectByUserId(userId)
            .asFlow()
            .mapToList(dispatchers.io)
    }

    // Get active tasks
    fun observeActiveTasks(userId: String): Flow<List<Task>> {
        return queries.selectActiveTasks(userId)
            .asFlow()
            .mapToList(dispatchers.io)
    }

    // Get overdue tasks
    suspend fun getOverdueTasks(userId: String): List<Task> =
        withContext(dispatchers.io) {
            val currentTime = Clock.System.now().toEpochMilliseconds()
            queries.selectOverdueTasks(currentTime, userId).executeAsList()
        }

    // Search tasks
    fun searchTasks(userId: String, query: String): Flow<List<Task>> {
        return queries.searchTasks(userId, query)
            .asFlow()
            .mapToList(dispatchers.io)
    }

    // Insert task
    suspend fun insertTask(task: Task) = withContext(dispatchers.io) {
        queries.insertTask(
            id = task.id,
            title = task.title,
            description = task.description,
            completed = task.completed,
            priority = task.priority.toLong(),
            dueDate = task.dueDate,
            createdAt = task.createdAt,
            updatedAt = task.updatedAt,
            categoryId = task.categoryId,
            userId = task.userId
        )
    }

    // Update task
    suspend fun updateTask(task: Task) = withContext(dispatchers.io) {
        queries.updateTask(
            id = task.id,
            title = task.title,
            description = task.description,
            completed = task.completed,
            priority = task.priority.toLong(),
            dueDate = task.dueDate,
            updatedAt = Clock.System.now().toEpochMilliseconds(),
            categoryId = task.categoryId
        )
    }

    // Toggle completion
    suspend fun toggleTaskCompletion(taskId: String) = withContext(dispatchers.io) {
        queries.toggleCompletion(
            id = taskId,
            updatedAt = Clock.System.now().toEpochMilliseconds()
        )
    }

    // Delete task
    suspend fun deleteTask(taskId: String) = withContext(dispatchers.io) {
        queries.deleteTask(taskId)
    }

    // Get task counts
    suspend fun getTaskCounts(userId: String): TaskCounts =
        withContext(dispatchers.io) {
            queries.countByStatus(userId).executeAsOne().let {
                TaskCounts(
                    active = it.activeCount?.toInt() ?: 0,
                    completed = it.completedCount?.toInt() ?: 0
                )
            }
        }
}

data class TaskCounts(
    val active: Int,
    val completed: Int
)
```

**2. Complex Queries with Joins**
```kotlin
// Get tasks with category information
suspend fun getTasksWithCategory(userId: String): List<TaskWithCategory> =
    withContext(dispatchers.io) {
        // Custom query combining Task and Category
        database.taskQueries.selectTaskWithCategory(userId)
            .executeAsList()
            .map { row ->
                TaskWithCategory(
                    task = Task(
                        id = row.id,
                        title = row.title,
                        description = row.description,
                        completed = row.completed,
                        priority = row.priority.toInt(),
                        dueDate = row.dueDate,
                        createdAt = row.createdAt,
                        updatedAt = row.updatedAt,
                        categoryId = row.categoryId,
                        userId = row.userId
                    ),
                    categoryName = row.categoryName,
                    categoryColor = row.categoryColor,
                    categoryIcon = row.categoryIcon
                )
            }
        }

data class TaskWithCategory(
    val task: Task,
    val categoryName: String?,
    val categoryColor: String?,
    val categoryIcon: String?
)
```

#### Migrations

**1. Version Migration**
```kotlin
// shared/src/commonMain/sqldelight/migrations/1.sqm
-- Migration from version 1 to 2

-- Add priority column
ALTER TABLE Task ADD COLUMN priority INTEGER NOT NULL DEFAULT 0;

-- Add index for priority
CREATE INDEX task_priority ON Task(priority);

// shared/src/commonMain/sqldelight/migrations/2.sqm
-- Migration from version 2 to 3

-- Add dueDate column
ALTER TABLE Task ADD COLUMN dueDate INTEGER;

-- Add index for dueDate
CREATE INDEX task_dueDate ON Task(dueDate);

// shared/src/commonMain/sqldelight/migrations/3.sqm
-- Migration from version 3 to 4

-- Add Category table
CREATE TABLE Category (
    id TEXT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    color TEXT NOT NULL,
    icon TEXT,
    createdAt INTEGER NOT NULL
);

-- Add categoryId to Task
ALTER TABLE Task ADD COLUMN categoryId TEXT REFERENCES Category(id);

-- Add index
CREATE INDEX task_categoryId ON Task(categoryId);
```

**2. Manual Migration Handler**
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
                    db.execSQL("PRAGMA foreign_keys=ON;")
                    db.execSQL("PRAGMA journal_mode=WAL;")
                }

                override fun onUpgrade(
                    db: SupportSQLiteDatabase,
                    oldVersion: Int,
                    newVersion: Int
                ) {
                    // Custom migration logic if needed
                    when (oldVersion) {
                        1 -> {
                            // Migrate from v1 to v2
                            db.execSQL("ALTER TABLE Task ADD COLUMN priority INTEGER NOT NULL DEFAULT 0")
                        }
                        2 -> {
                            // Migrate from v2 to v3
                            db.execSQL("ALTER TABLE Task ADD COLUMN dueDate INTEGER")
                        }
                    }
                }
            }
        )
    }
}
```

#### Transactions

**1. Basic Transactions**
```kotlin
class TaskRepository(
    private val database: TaskDatabaseWrapper,
    private val dispatchers: CoroutineDispatchers
) {
    suspend fun insertMultipleTasks(tasks: List<Task>) =
        withContext(dispatchers.io) {
            database.taskQueries.transaction {
                tasks.forEach { task ->
                    database.taskQueries.insertTask(
                        id = task.id,
                        title = task.title,
                        description = task.description,
                        completed = task.completed,
                        priority = task.priority.toLong(),
                        dueDate = task.dueDate,
                        createdAt = task.createdAt,
                        updatedAt = task.updatedAt,
                        categoryId = task.categoryId,
                        userId = task.userId
                    )
                }
            }
        }

    // Transaction with rollback
    suspend fun moveTaskToCategory(
        taskId: String,
        newCategoryId: String
    ): Result<Unit> = withContext(dispatchers.io) {
        try {
            database.taskQueries.transaction {
                // Verify category exists
                val category = database.categoryQueries
                    .selectById(newCategoryId)
                    .executeAsOneOrNull()
                    ?: throw IllegalArgumentException("Category not found")

                // Update task
                database.taskQueries.updateTask(
                    id = taskId,
                    categoryId = newCategoryId,
                    updatedAt = Clock.System.now().toEpochMilliseconds()
                )
            }
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

**2. Nested Transactions**
```kotlin
suspend fun syncTasksFromServer(
    serverTasks: List<TaskDto>,
    userId: String
) = withContext(dispatchers.io) {
    database.taskQueries.transaction {
        // Delete all local tasks for user
        database.taskQueries.deleteByUserId(userId)

        // Insert tasks from server
        serverTasks.forEach { dto ->
            database.taskQueries.insertTask(
                id = dto.id,
                title = dto.title,
                description = dto.description,
                completed = dto.completed,
                priority = dto.priority.toLong(),
                dueDate = dto.dueDate,
                createdAt = dto.createdAt,
                updatedAt = dto.updatedAt,
                categoryId = dto.categoryId,
                userId = userId
            )
        }

        // Update sync timestamp
        database.userQueries.updateLastSyncTime(
            userId = userId,
            lastSyncTime = Clock.System.now().toEpochMilliseconds()
        )
    }
}
```

#### Query Optimization

**1. Pagination**
```kotlin
// Task.sq
selectTasksPaginated:
SELECT * FROM Task
WHERE userId = :userId
ORDER BY createdAt DESC
LIMIT :limit OFFSET :offset;

// Repository
class TaskRepository(
    private val database: TaskDatabaseWrapper,
    private val dispatchers: CoroutineDispatchers
) {
    suspend fun getTasksPaginated(
        userId: String,
        page: Int,
        pageSize: Int = 20
    ): List<Task> = withContext(dispatchers.io) {
        val offset = page * pageSize
        database.taskQueries.selectTasksPaginated(
            userId = userId,
            limit = pageSize.toLong(),
            offset = offset.toLong()
        ).executeAsList()
    }

    // Flow-based pagination
    fun observeTasksPaginated(
        userId: String,
        limit: Int = 20
    ): Flow<List<Task>> {
        return database.taskQueries.selectTasksPaginated(
            userId = userId,
            limit = limit.toLong(),
            offset = 0
        )
        .asFlow()
        .mapToList(dispatchers.io)
    }
}
```

**2. Batching**
```kotlin
suspend fun insertTasksBatch(tasks: List<Task>) = withContext(dispatchers.io) {
    database.taskQueries.transaction {
        // Batch inserts in chunks to avoid SQL variable limit
        tasks.chunked(500).forEach { batch ->
            batch.forEach { task ->
                database.taskQueries.insertTask(
                    id = task.id,
                    title = task.title,
                    description = task.description,
                    completed = task.completed,
                    priority = task.priority.toLong(),
                    dueDate = task.dueDate,
                    createdAt = task.createdAt,
                    updatedAt = task.updatedAt,
                    categoryId = task.categoryId,
                    userId = task.userId
                )
            }
        }
    }
}
```

**3. Indexing Strategy**
```sql
-- Composite index for common query pattern
CREATE INDEX task_user_status_date ON Task(userId, completed, dueDate);

-- Partial index for active tasks only
CREATE INDEX task_active ON Task(userId, priority, dueDate)
WHERE completed = 0;

-- Index for full-text search (if using FTS)
CREATE VIRTUAL TABLE TaskFts USING fts5(
    title,
    description,
    content=Task,
    content_rowid=rowid
);
```

#### Custom Type Adapters

**1. Enum Adapter**
```kotlin
// Domain model
enum class TaskPriority {
    LOW, MEDIUM, HIGH, URGENT
}

// Adapter
object TaskPriorityAdapter : ColumnAdapter<TaskPriority, Long> {
    override fun decode(databaseValue: Long): TaskPriority {
        return TaskPriority.values()[databaseValue.toInt()]
    }

    override fun encode(value: TaskPriority): Long {
        return value.ordinal.toLong()
    }
}

// Register adapter
val database = TaskDatabase(
    driver = driver,
    TaskAdapter = Task.Adapter(
        priorityAdapter = TaskPriorityAdapter
    )
)
```

**2. DateTime Adapter**
```kotlin
// Using kotlinx-datetime
object InstantAdapter : ColumnAdapter<Instant, Long> {
    override fun decode(databaseValue: Long): Instant {
        return Instant.fromEpochMilliseconds(databaseValue)
    }

    override fun encode(value: Instant): Long {
        return value.toEpochMilliseconds()
    }
}

// Using LocalDate
object LocalDateAdapter : ColumnAdapter<LocalDate, String> {
    override fun decode(databaseValue: String): LocalDate {
        return LocalDate.parse(databaseValue)
    }

    override fun encode(value: LocalDate): String {
        return value.toString()
    }
}
```

#### Testing

**1. In-Memory Database for Tests**
```kotlin
// commonTest
class TaskRepositoryTest {
    private lateinit var database: TaskDatabaseWrapper
    private lateinit var repository: TaskRepository

    @BeforeTest
    fun setup() {
        // Create in-memory database
        val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
        TaskDatabase.Schema.create(driver)

        database = TaskDatabaseWrapper(
            object : DatabaseDriverFactory {
                override fun createDriver() = driver
            }
        )

        repository = TaskRepository(
            database = database,
            dispatchers = TestDispatchers
        )
    }

    @AfterTest
    fun tearDown() {
        database.close()
    }

    @Test
    fun `insertTask and getTaskById returns correct task`() = runTest {
        val task = Task(
            id = "1",
            title = "Test Task",
            description = "Description",
            completed = false,
            priority = 1,
            dueDate = null,
            createdAt = 1000L,
            updatedAt = 1000L,
            categoryId = null,
            userId = "user1"
        )

        repository.insertTask(task)
        val retrieved = repository.getTaskById("1")

        assertEquals(task, retrieved)
    }

    @Test
    fun `observeActiveTasks returns only incomplete tasks`() = runTest {
        val tasks = listOf(
            Task(id = "1", completed = false, userId = "user1", ...),
            Task(id = "2", completed = true, userId = "user1", ...),
            Task(id = "3", completed = false, userId = "user1", ...)
        )

        tasks.forEach { repository.insertTask(it) }

        val activeTasks = repository.observeActiveTasks("user1").first()

        assertEquals(2, activeTasks.size)
        assertTrue(activeTasks.all { !it.completed })
    }
}
```

#### Best Practices

1. **Schema Design**:
   - Use foreign keys for data integrity
   - Create indexes for frequently queried columns
   - Use composite indexes for multi-column queries
   - Consider partial indexes for filtered queries

2. **Queries**:
   - Name queries descriptively
   - Use parameters to prevent SQL injection
   - Leverage SQLDelight's type safety
   - Use Flow for reactive updates

3. **Transactions**:
   - Group related operations in transactions
   - Keep transactions short
   - Handle errors and rollbacks
   - Use nested transactions carefully

4. **Performance**:
   - Enable WAL mode on Android
   - Use batching for bulk operations
   - Implement pagination for large datasets
   - Profile queries with EXPLAIN QUERY PLAN

5. **Migrations**:
   - Test migrations thoroughly
   - Use verifyMigrations in development
   - Keep migrations backward compatible
   - Document schema changes

### Summary

SQLDelight provides type-safe multiplatform database management:
- **Type Safety**: Compile-time SQL verification
- **Platform Drivers**: SQLite (Android), SQLite.swift (iOS)
- **Reactive**: Flow-based queries
- **Migrations**: Automatic schema versioning
- **Transactions**: ACID-compliant operations
- **Performance**: Optimized with indexes and batching

Key considerations: proper schema design, migration strategy, transaction management, query optimization, and comprehensive testing.

---

# Вопрос (RU)
> 
Объясните как использовать SQLDelight для кросс-платформенного управления базой данных в KMM. Как определять схемы, обрабатывать миграции, реализовывать транзакции и оптимизировать запросы для Android и iOS?

## Ответ (RU)
SQLDelight генерирует type-safe Kotlin APIs из SQL statements, обеспечивая compile-time верификацию и platform-specific драйверы (SQLite на Android, SQLite.swift на iOS) при sharing database логики.

#### Ключевые возможности

**Type Safety**:
- Compile-time SQL verification
- Generated Kotlin APIs
- Type-safe parameters
- Null safety

**Platform Drivers**:
- Android: AndroidSqliteDriver (SQLite)
- iOS: NativeSqliteDriver (SQLite.swift)
- Автоматический выбор

**Reactive Queries**:
- Flow-based observables
- Automatic updates
- Lifecycle-aware

#### Schema Definition

**SQL файлы**:
- `.sq` файлы в commonMain
- CREATE TABLE statements
- Named queries
- Indexes и constraints

**Queries**:
- Named queries (selectAll, insertTask)
- Параметризованные запросы
- JOINs и aggregations
- Full-text search

#### Migrations

**Версионирование**:
- `.sqm` migration файлы
- Automatic schema updates
- verifyMigrations для тестирования
- Manual migrations для complex cases

**Best Practices**:
- Тестировать все миграции
- Backward compatibility
- Документировать изменения

#### Transactions

**ACID Operations**:
- transaction {} block
- Automatic rollback on error
- Nested transactions support
- Batch operations

**Use Cases**:
- Bulk inserts
- Multi-table updates
- Data synchronization
- Integrity constraints

#### Оптимизация

**Indexes**:
- Single-column indexes
- Composite indexes
- Partial indexes
- Full-text search indexes

**Pagination**:
- LIMIT/OFFSET queries
- Flow-based pagination
- Cursor-based pagination

**Batching**:
- Chunked inserts (500-1000 items)
- Transaction batching
- Reduced I/O operations

#### Testing

**In-Memory Database**:
- JdbcSqliteDriver.IN_MEMORY
- Fast unit tests
- Isolated test cases
- No cleanup needed

### Резюме

SQLDelight обеспечивает type-safe multiplatform database:
- **Type Safety**: Compile-time проверки
- **Platform Drivers**: Native SQLite
- **Reactive**: Flow queries
- **Migrations**: Automatic versioning
- **Transactions**: ACID guarantees
- **Performance**: Indexes, batching, WAL mode

Ключевые моменты: schema design, migration strategy, transaction management, query optimization, testing.

## Related Questions

- [[q-annotation-processing-android--android--medium]]
- [[q-play-feature-delivery--android--medium]]
- [[q-gradle-kotlin-dsl-vs-groovy--android--medium]]
