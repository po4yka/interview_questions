---
id: android-452
title: Database Optimization Android / Оптимизация базы данных Android
aliases: ["Database Optimization Android", "Оптимизация базы данных Android"]
topic: android
subtopics: [performance-memory, room]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-performance-optimization-android--android--medium, q-room-library-definition--android--easy, q-room-vs-sqlite--android--medium]
created: 2025-10-20
updated: 2025-10-27
tags: [android/performance-memory, android/room, database, difficulty/medium, indexing, optimization, performance, sql]
sources: [https://developer.android.com/training/data-storage/room]
date created: Monday, October 27th 2025, 10:27:30 pm
date modified: Thursday, October 30th 2025, 12:47:36 pm
---

# Вопрос (RU)
> Какие лучшие практики и техники для оптимизации базы данных в Android приложениях?

# Question (EN)
> What are the best practices and techniques for database optimization in Android applications?

## Ответ (RU)

Оптимизация базы данных в Android требует комплексного подхода: правильная индексация, пакетные операции, асинхронное выполнение и кэширование.

### 1. Индексация

Индексы ускоряют чтение, но замедляют запись. Создавайте индексы для часто запрашиваемых полей:

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

**Trade-offs:** индекс занимает дополнительную память (~10-20% размера таблицы) и замедляет INSERT/UPDATE на 15-30%.

### 2. Пакетные Операции

Группируйте операции в транзакции для снижения overhead:

```kotlin
@Dao
interface UserDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<User>)  // ✅ Одна транзакция

    @Transaction  // ✅ Гарантирует атомарность
    suspend fun syncUsers(local: List<User>, remote: List<User>) {
        deleteUsers(local)
        insertUsers(remote)
    }
}

// ❌ Плохо: каждый insert - отдельная транзакция
users.forEach { dao.insertUser(it) }

// ✅ Хорошо: одна транзакция для всех записей
dao.insertUsers(users)
```

**Производительность:** пакетная вставка 1000 записей ~50x быстрее поштучной.

### 3. Асинхронность И Реактивность

Используйте `suspend` функции и `Flow` для предотвращения ANR:

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getUsers(): List<User>  // ✅ Для одноразовых запросов

    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>>  // ✅ Для автоматических обновлений UI
}
```

Room автоматически выполняет операции на `Dispatchers.IO`.

### 4. Оптимизация Запросов

Минимизируйте объем считываемых данных:

```kotlin
@Dao
interface UserDao {
    // ❌ Читает все поля, даже ненужные
    @Query("SELECT * FROM users WHERE active = 1")
    suspend fun getActiveUsers(): List<User>

    // ✅ Только нужные поля
    @Query("SELECT id, name FROM users WHERE active = 1 LIMIT 100")
    suspend fun getActiveUserNames(): List<UserName>

    // ✅ Используйте LIMIT для пагинации
    @Query("SELECT * FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    suspend fun getUsersPage(limit: Int, offset: Int): List<User>
}
```

### 5. Кэширование

LRU кэш для горячих данных:

```kotlin
class UserRepository @Inject constructor(
    private val dao: UserDao
) {
    private val cache = LruCache<Long, User>(maxSize = 100)  // ✅ ~100 записей в памяти

    suspend fun getUser(id: Long): User? =
        cache[id] ?: dao.getUserById(id)?.also { cache.put(id, it) }
}
```

**Trade-off:** использует память (~10-100 KB в зависимости от размера объектов).

## Answer (EN)

Database optimization in Android requires a comprehensive approach: proper indexing, batch operations, asynchronous execution, and caching.

### 1. Indexing

Indexes speed up reads but slow down writes. Create indexes for frequently queried fields:

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

**Trade-offs:** indexes consume additional memory (~10-20% of table size) and slow down INSERT/UPDATE by 15-30%.

### 2. Batch Operations

Group operations into transactions to reduce overhead:

```kotlin
@Dao
interface UserDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<User>)  // ✅ Single transaction

    @Transaction  // ✅ Guarantees atomicity
    suspend fun syncUsers(local: List<User>, remote: List<User>) {
        deleteUsers(local)
        insertUsers(remote)
    }
}

// ❌ Bad: each insert is a separate transaction
users.forEach { dao.insertUser(it) }

// ✅ Good: single transaction for all records
dao.insertUsers(users)
```

**Performance:** batch insert of 1000 records is ~50x faster than individual inserts.

### 3. Asynchronicity And Reactivity

Use `suspend` functions and `Flow` to prevent ANR:

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getUsers(): List<User>  // ✅ For one-time queries

    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>>  // ✅ For automatic UI updates
}
```

Room automatically executes operations on `Dispatchers.IO`.

### 4. Query Optimization

Minimize the volume of data read:

```kotlin
@Dao
interface UserDao {
    // ❌ Reads all fields, even unnecessary ones
    @Query("SELECT * FROM users WHERE active = 1")
    suspend fun getActiveUsers(): List<User>

    // ✅ Only needed fields
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
    private val cache = LruCache<Long, User>(maxSize = 100)  // ✅ ~100 records in memory

    suspend fun getUser(id: Long): User? =
        cache[id] ?: dao.getUserById(id)?.also { cache.put(id, it) }
}
```

**Trade-off:** uses memory (~10-100 KB depending on object size).


## Follow-ups

- How would you profile Room database performance to identify slow queries?
- When would you choose DataStore over Room for persistence?
- How do you handle database migrations without losing user data?
- What's the impact of FTS (Full-Text Search) on database size and performance?
- How do you implement pagination with Room and Paging 3 library?

## References

- [[c-database-performance]]
- [[c-database-design]]
- Android Room Documentation: https://developer.android.com/training/data-storage/room
- SQLite Performance Best Practices: https://sqlite.org/performance.html

## Related Questions

### Prerequisites
- [[q-room-library-definition--android--easy]] - Understanding Room basics

### Related (Same Level)
- [[q-room-vs-sqlite--android--medium]] - Room vs raw SQLite comparison
- [[q-room-database-migrations--room--medium]] - Handling schema changes
- [[q-performance-optimization-android--android--medium]] - General Android performance

### Advanced
- [[q-room-fts-full-text-search--room--hard]] - Full-text search implementation
- [[q-room-paging3-integration--room--medium]] - Efficient pagination patterns
