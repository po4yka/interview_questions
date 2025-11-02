---
id: android-475
title: Databases Android / Базы данных в Android
aliases: [Databases Android, Базы данных в Android]
topic: android
subtopics:
  - datastore
  - room
question_kind: theory
difficulty: easy
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-database-encryption-android--android--medium
  - q-database-optimization-android--android--medium
created: 2025-10-20
updated: 2025-10-27
tags: [android/datastore, android/room, database, difficulty/easy]
sources:
  - https://developer.android.com/training/data-storage
date created: Monday, October 27th 2025, 10:28:31 pm
date modified: Sunday, November 2nd 2025, 7:36:49 pm
---

# Вопрос (RU)
> Какие базы данных можно использовать в Android?

# Question (EN)
> What databases can be used in Android?

## Ответ (RU)

В Android используются **три основных решения для персистентности данных**: SQLite (нативная), [[c-room]] (рекомендуемая ORM от Google), и Realm/MongoDB (альтернативная NoSQL).

### Основные Концепции

**SQLite** — встроенная реляционная БД без внешних зависимостей, требует ручного SQL и работы с Cursor API.

**Room** — типобезопасная ORM-обёртка над SQLite с compile-time валидацией запросов, генерацией кода и нативной поддержкой корутин/Flow.

**Realm/MongoDB** — объектная БД с собственным движком (не SQL), поддерживает автоматическую синхронизацию, реактивные запросы, но увеличивает размер APK.

### 1. SQLite — Низкоуровневый API

Прямой доступ через SQLiteOpenHelper и Cursor API. **Недостатки**: boilerplate, ручное управление памятью, runtime SQL-ошибки.

```kotlin
class DbHelper(ctx: Context) : SQLiteOpenHelper(ctx, "app.db", null, 1) {
    override fun onCreate(db: SQLiteDatabase) {
        // ❌ SQL-строка без compile-time проверки
        db.execSQL("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    }
    // ❌ Деструктивная миграция в production
    override fun onUpgrade(db: SQLiteDatabase, old: Int, new: Int) {
        db.execSQL("DROP TABLE users")
        onCreate(db)
    }
}
```

### 2. Room — Официальная ORM (рекомендуется)

Генерирует имплементации DAO на этапе компиляции через annotation processing. Предоставляет безопасные suspend-функции и Flow для реактивных обновлений.

```kotlin
@Entity(tableName = "users")
data class User(@PrimaryKey(autoGenerate = true) val id: Long = 0, val name: String)

@Dao
interface UserDao {
    // ✅ Compile-time валидация SQL
    @Query("SELECT * FROM users WHERE name LIKE :query")
    fun search(query: String): Flow<List<User>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(user: User)
}

@Database(entities = [User::class], version = 1, exportSchema = true)
abstract class AppDb : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

### 3. Realm (MongoDB Mobile) — Альтернатива NoSQL

Объектная БД с zero-copy архитектурой (live objects), встроенной синхронизацией с облаком. **Минусы**: +3–5 MB к APK, проприетарный формат данных, сложная миграция на другие решения.

```kotlin
class User : RealmObject() {
    @PrimaryKey var id: String = UUID.randomUUID().toString()
    var name: String = ""
}

// ✅ Реактивные запросы без дополнительных библиотек
realm.where<User>().findAllAsync().asFlow().collect { users ->
    // Автообновление при изменениях в БД
}

// ❌ Объекты привязаны к Realm-треду, требует copyFromRealm() для передачи
```

### Критерии Выбора

| Фактор | SQLite | Room | Realm |
|--------|--------|------|-------|
| APK размер | +0 KB | +50 KB | +3–5 MB |
| Безопасность типов | ❌ runtime | ✅ compile-time | ✅ compile-time |
| Кривая обучения | Высокая (Cursor API) | Средняя (SQL + аннотации) | Низкая (OOP) |
| Миграции | Ручные скрипты | Декларативные Migration | Автоматические (ограниченно) |
| Реактивность | ❌ | ✅ Flow/LiveData | ✅ встроенная |

**Рекомендации:**
- **Room** — стандарт для production (официальная поддержка Google, интеграция с Jetpack)
- **SQLite** — только для legacy-кода или микросервисов без ORM
- **Realm** — если критична синхронизация с MongoDB Atlas или нужна кросс-платформа (Kotlin Multiplatform)

## Answer (EN)

Android offers **three main persistence solutions**: SQLite (native), [[c-room]] (recommended ORM by Google), and Realm/MongoDB (alternative NoSQL).

### Core Concepts

**SQLite** — built-in relational DB with no external dependencies, requires manual SQL and Cursor API handling.

**Room** — type-safe ORM wrapper over SQLite with compile-time query validation, code generation, and native coroutines/Flow support.

**Realm/MongoDB** — object database with its own engine (not SQL), supports automatic cloud sync and reactive queries, but increases APK size.

### 1. SQLite — Low-Level API

Direct access via SQLiteOpenHelper and Cursor API. **Drawbacks**: boilerplate, manual memory management, runtime SQL errors.

```kotlin
class DbHelper(ctx: Context) : SQLiteOpenHelper(ctx, "app.db", null, 1) {
    override fun onCreate(db: SQLiteDatabase) {
        // ❌ SQL string without compile-time verification
        db.execSQL("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    }
    // ❌ Destructive migration in production
    override fun onUpgrade(db: SQLiteDatabase, old: Int, new: Int) {
        db.execSQL("DROP TABLE users")
        onCreate(db)
    }
}
```

### 2. Room — Official ORM (Recommended)

Generates DAO implementations at compile time via annotation processing. Provides safe suspend functions and Flow for reactive updates.

```kotlin
@Entity(tableName = "users")
data class User(@PrimaryKey(autoGenerate = true) val id: Long = 0, val name: String)

@Dao
interface UserDao {
    // ✅ Compile-time SQL validation
    @Query("SELECT * FROM users WHERE name LIKE :query")
    fun search(query: String): Flow<List<User>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(user: User)
}

@Database(entities = [User::class], version = 1, exportSchema = true)
abstract class AppDb : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

### 3. Realm (MongoDB Mobile) — NoSQL Alternative

Object database with zero-copy architecture (live objects), built-in cloud sync. **Cons**: +3–5 MB to APK, proprietary data format, difficult migration to other solutions.

```kotlin
class User : RealmObject() {
    @PrimaryKey var id: String = UUID.randomUUID().toString()
    var name: String = ""
}

// ✅ Reactive queries without additional libraries
realm.where<User>().findAllAsync().asFlow().collect { users ->
    // Auto-updates on DB changes
}

// ❌ Objects tied to Realm thread, requires copyFromRealm() for passing
```

### Selection Criteria

| Factor | SQLite | Room | Realm |
|--------|--------|------|-------|
| APK size | +0 KB | +50 KB | +3–5 MB |
| Type safety | ❌ runtime | ✅ compile-time | ✅ compile-time |
| Learning curve | High (Cursor API) | Medium (SQL + annotations) | Low (OOP) |
| Migrations | Manual scripts | Declarative Migration | Automatic (limited) |
| Reactivity | ❌ | ✅ Flow/LiveData | ✅ built-in |

**Recommendations:**
- **Room** — production standard (official Google support, Jetpack integration)
- **SQLite** — only for legacy code or microservices without ORM
- **Realm** — if MongoDB Atlas sync is critical or cross-platform needed (Kotlin Multiplatform)


## Follow-ups

- How do you implement database migrations in Room when schema changes?
- What are the threading constraints for each database solution?
- When would you use DataStore instead of a database?
- How do you handle database encryption and security?
- What's the impact of using in-memory vs file-based databases?

## References

- [[c-room]] — Room persistence library concepts
- [[c-database-design]] — Database design patterns
- [[c-database-performance]] — Performance optimization techniques
- [Android Data Storage](https://developer.android.com/training/data-storage)
- [Room Migration Guide](https://developer.android.com/training/data-storage/room/migrating-db-versions)

## Related Questions

### Prerequisites
- What is SQL and how does it differ from NoSQL?
- What are the ACID properties of databases?

### Related
- [[q-database-optimization-android--android--medium]] — Performance tuning strategies
- [[q-database-encryption-android--android--medium]] — Securing sensitive data

### Advanced
- How do you implement multi-database architecture in Android?
- What are the trade-offs between normalization and denormalization in mobile databases?
- How do you handle offline-first sync with remote databases?
