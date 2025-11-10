---
id: android-452
title: Database Optimization Android / Оптимизация базы данных Android
aliases:
- Database Optimization Android
- Оптимизация базы данных Android
topic: android
subtopics:
- performance-memory
- room
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- c-room-database
- c-database-design
- c-performance-optimization
- q-performance-optimization-android--android--medium
- q-room-library-definition--android--easy
- q-room-vs-sqlite--android--medium
created: 2025-10-20
updated: 2025-11-02
tags:
- android/performance-memory
- android/room
- database
- difficulty/medium
- indexing
- optimization
- performance
- sql
sources:
- https://developer.android.com/training/data-storage/room
---

# Вопрос (RU)
> Какие лучшие практики и техники для оптимизации базы данных в Android приложениях?

# Question (EN)
> What are the best practices and techniques for database optimization in Android applications?

## Ответ (RU)

Оптимизация базы данных в Android требует комплексного подхода: правильная индексация, пакетные операции, асинхронное выполнение и кэширование. Основная цель — обеспечить быстрый отклик UI, минимизировать потребление памяти и предотвратить `ANR` (Application Not Responding).

### 1. Индексация

Индексы ускоряют чтение (`SELECT`), но замедляют запись (`INSERT`/`UPDATE`). Создавайте индексы для часто запрашиваемых полей:

```kotlin
@Entity(
    tableName = "users",
    indices = [
        Index(value = ["email"], unique = true),  // ✅ Для точного поиска
        Index(value = ["last_name", "first_name"]),  // ✅ Составной индекс
        Index(value = ["created_at"])  // ✅ Для сортировки/фильтрации
    ]
)
data class User(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val email: String,
    // ❌ Не индексируйте редко запрашиваемые поля - это замедляет INSERT
)
```

**Trade-offs:** индексы занимают дополнительную память и замедляют `INSERT`/`UPDATE`, так как при каждой записи нужно обновлять структуру индекса. В типичных сценариях накладные расходы могут быть заметны (например, рост размера таблицы и замедление вставок), поэтому индексы имеет смысл добавлять только для часто используемых колонок и избегать избыточной индексации. Конкретные цифры зависят от данных и нагрузки, их нужно проверять профилированием.

### 2. Пакетные Операции

Группируйте операции в транзакции для снижения overhead:

```kotlin
@Dao
interface UserDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<User>)  // ✅ Одна транзакция для списка

    @Transaction  // ✅ Гарантирует атомарность
    suspend fun syncUsers(local: List<User>, remote: List<User>) {
        deleteUsers(local)
        insertUsers(remote)
    }

    @Delete
    suspend fun deleteUsers(users: List<User>)
}

// ❌ Плохо: каждый insert - отдельная транзакция
users.forEach { dao.insertUser(it) }

// ✅ Хорошо: одна транзакция для всех записей
dao.insertUsers(users)
```

**Производительность:** пакетная вставка большого количества записей обычно на порядок быстрее поштучной (меньше открытых транзакций и fsync). Точный выигрыш (например, 10x–50x) зависит от устройства и размера данных, поэтому его нужно измерять на целевой среде.

### 3. Асинхронность И Реактивность

Используйте `suspend` функции и `Flow` (Room KTX) для предотвращения `ANR`, чтобы не выполнять операции с БД на главном потоке:

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getUsers(): List<User>  // ✅ Для одноразовых запросов (Room выполняет на рабочем потоке)

    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>>  // ✅ Для автоматических обновлений UI
}
```

Room для `suspend` и `Flow` DAO-методов использует собственный пул потоков и предотвращает выполнение этих запросов на главном потоке, но он не переключает корутины на `Dispatchers.IO` автоматически. Вызовы необходимо делать из подходящего контекста (обычно `Dispatchers.IO` или `viewModelScope` с off-main контекстом), а при необходимости дополнительного контроля использовать `flowOn(...)`.

### 4. Оптимизация Запросов

Минимизируйте объем считываемых данных:

```kotlin
@Dao
interface UserDao {
    // ❌ Читает все поля, даже ненужные
    @Query("SELECT * FROM users WHERE active = 1")
    suspend fun getActiveUsers(): List<User>

    // ✅ Только нужные поля (отдельный DTO)
    @Query("SELECT id, name FROM users WHERE active = 1 LIMIT 100")
    suspend fun getActiveUserNames(): List<UserName>

    // ✅ Используйте LIMIT для пагинации
    @Query("SELECT * FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    suspend fun getUsersPage(limit: Int, offset: Int): List<User>
}
```

### 5. Кэширование

LRU-кэш для горячих данных:

```kotlin
class UserRepository @Inject constructor(
    private val dao: UserDao
) {
    private val cache = LruCache<Long, User>(100)  // ✅ ~100 записей в памяти

    suspend fun getUser(id: Long): User? {
        val cached = cache.get(id)
        if (cached != null) return cached
        val fromDb = dao.getUserById(id)
        if (fromDb != null) {
            cache.put(id, fromDb)
        }
        return fromDb
    }
}
```

**Trade-off:** использует память (объем зависит от размера объектов). Регулируйте размер кэша в зависимости от доступной памяти устройства. `LruCache` автоматически удаляет наименее используемые элементы при достижении лимита.

## Answer (EN)

Database optimization in Android requires a comprehensive approach: proper indexing, batch operations, asynchronous execution, and caching. Main goals: ensure fast UI responsiveness, minimize memory consumption, and prevent `ANR` (Application Not Responding).

### 1. Indexing

Indexes speed up reads (`SELECT`) but slow down writes (`INSERT`/`UPDATE`). Create indexes for frequently queried fields:

```kotlin
@Entity(
    tableName = "users",
    indices = [
        Index(value = ["email"], unique = true),  // ✅ For exact lookups
        Index(value = ["last_name", "first_name"]),  // ✅ Composite index
        Index(value = ["created_at"])  // ✅ For sorting/filtering
    ]
)
data class User(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val email: String,
    // ❌ Don't index rarely queried fields - it slows down INSERT
)
```

**Trade-offs:** indexes consume additional space and add overhead to `INSERT`/`UPDATE` because index structures must be updated on each write. In typical scenarios, this overhead can be significant (larger DB file, slower writes), so add indexes only for frequently used columns and avoid over-indexing. Exact impact is data- and workload-dependent and should be verified via profiling.

### 2. Batch Operations

Group operations into transactions to reduce overhead:

```kotlin
@Dao
interface UserDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<User>)  // ✅ Single transaction for the list

    @Transaction  // ✅ Guarantees atomicity
    suspend fun syncUsers(local: List<User>, remote: List<User>) {
        deleteUsers(local)
        insertUsers(remote)
    }

    @Delete
    suspend fun deleteUsers(users: List<User>)
}

// ❌ Bad: each insert is a separate transaction
users.forEach { dao.insertUser(it) }

// ✅ Good: single transaction for all records
dao.insertUsers(users)
```

**Performance:** bulk inserting many records is usually an order of magnitude faster than inserting them one by one (fewer transactions and fsync calls). The exact speedup (e.g., 10x–50x) depends on device and data size, so always measure on the target environment.

### 3. Asynchronicity And Reactivity

Use `suspend` functions and `Flow` (Room KTX) to avoid running DB work on the main thread and prevent `ANR`:

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getUsers(): List<User>  // ✅ For one-time queries (Room runs on a background thread for suspend DAO)

    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>>  // ✅ For automatic UI updates
}
```

For `suspend` and `Flow` DAO methods, Room uses its own background executors and disallows main-thread access by default, but it does not automatically switch coroutines to `Dispatchers.IO`. Call these APIs from an appropriate coroutine context (commonly `Dispatchers.IO` or `viewModelScope` with off-main context) and apply `flowOn(...)` when you need additional control.

### 4. Query Optimization

Minimize the amount of data read:

```kotlin
@Dao
interface UserDao {
    // ❌ Reads all fields, even unnecessary ones
    @Query("SELECT * FROM users WHERE active = 1")
    suspend fun getActiveUsers(): List<User>

    // ✅ Only needed fields (separate DTO)
    @Query("SELECT id, name FROM users WHERE active = 1 LIMIT 100")
    suspend fun getActiveUserNames(): List<UserName>

    // ✅ Use LIMIT for pagination
    @Query("SELECT * FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    suspend fun getUsersPage(limit: Int, offset: Int): List<User>
}
```

### 5. Caching

LRU cache for hot data:

```kotlin
class UserRepository @Inject constructor(
    private val dao: UserDao
) {
    private val cache = LruCache<Long, User>(100)  // ✅ ~100 records in memory

    suspend fun getUser(id: Long): User? {
        val cached = cache.get(id)
        if (cached != null) return cached
        val fromDb = dao.getUserById(id)
        if (fromDb != null) {
            cache.put(id, fromDb)
        }
        return fromDb
    }
}
```

**Trade-off:** consumes memory (depends on object size). Adjust cache size according to available device memory. `LruCache` automatically evicts least recently used items when the limit is reached.


## Follow-ups

- How would you profile `Room` database performance to identify slow queries?
- When would you choose `DataStore` over `Room` for persistence?
- How do you handle database migrations without losing user data?
- What's the impact of `FTS` (Full-Text Search) on database size and performance?
- How do you implement pagination with `Room` and `Paging 3` library?
- How to optimize database queries using `EXPLAIN QUERY PLAN`?

## References

- [Android Room Documentation](https://developer.android.com/training/data-storage/room)
- [SQLite Performance Best Practices](https://sqlite.org/performance.html)

## Related Questions

### Prerequisites / Concepts

- [[c-room-database]]
- [[c-database-design]]
- [[c-performance-optimization]]


### Prerequisites (Easier)
- [[q-room-library-definition--android--easy]] — Understanding `Room` basics
- Basic knowledge of SQL and database concepts

### Related (Same Level)
- [[q-room-vs-sqlite--android--medium]] — `Room` vs raw SQLite comparison
- [[q-room-database-migrations--android--medium]] — Handling schema changes
- [[q-performance-optimization-android--android--medium]] — General Android performance optimization

### Advanced (Harder)
- `FTS` (Full-Text Search) implementation with `Room`
- `Paging 3` integration for efficient pagination patterns
- Database profiling and query optimization techniques
