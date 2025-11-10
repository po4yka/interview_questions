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
status: draft
moc: moc-android
related:
- c-database-design
- q-database-encryption-android--android--medium
- q-database-optimization-android--android--medium
created: 2025-10-20
updated: 2025-11-10
tags: [android/datastore, android/room, database, difficulty/easy]
sources:
- "https://developer.android.com/training/data-storage"

---

# Вопрос (RU)
> Какие базы данных можно использовать в Android?

# Question (EN)
> What databases can be used in Android?

## Ответ (RU)

В Android на практике часто используют следующие решения для персистентности структурированных данных в приложении: SQLite (нативная), [[c-room]] (рекомендуемая надстройка над SQLite от Google), и Realm/MongoDB (альтернативная объектная NoSQL-БД).

### Основные Концепции

**SQLite** — встроенная реляционная БД без внешних зависимостей, требует ручного SQL и работы с Cursor API.

**Room** — типобезопасная обёртка над SQLite (ORM/DAO слой) с compile-time валидацией запросов, генерацией кода и нативной поддержкой корутин/`Flow`.

**Realm/MongoDB** — объектная БД с собственным движком (не SQL), поддерживает реактивные запросы и (в некоторых конфигурациях) синхронизацию с облаком, но увеличивает размер APK.

> Примечание: Для ключ-значение/настроек Google рекомендует использовать DataStore, но это не полноценная реляционная БД и обычно упоминается отдельно.

### 1. SQLite — Низкоуровневый API

Прямой доступ через SQLiteOpenHelper и Cursor API. **Недостатки**: boilerplate, ручное управление ресурсами Cursor, runtime SQL-ошибки.

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

### 2. Room — Официальный абстракционный слой над SQLite (рекомендуется)

Генерирует имплементации DAO на этапе компиляции через annotation processing. Предоставляет безопасные suspend-функции и `Flow` для реактивных обновлений.

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

Объектная БД с zero-copy архитектурой (live objects), встроенной поддержкой реактивных данных и опциональной синхронизацией с MongoDB Atlas. **Минусы**: +3–5 MB к APK, проприетарный формат данных, миграции и переход на другие решения требуют аккуратной ручной настройки.

```kotlin
// Пример с классическим Realm Java API (для Kotlin/Multiplatform используется современный Realm Kotlin API).
class User : RealmObject() {
    @PrimaryKey var id: String = UUID.randomUUID().toString()
    var name: String = ""
}

// ✅ Реактивные запросы без дополнительных библиотек
realm.where<User>().findAllAsync().asFlow().collect { users ->
    // Автообновление при изменениях в БД
}

// ❌ Объекты привязаны к Realm-треду, для передачи между потоками нужен copyFromRealm()/менеджмент по API
```

### Критерии Выбора

| Фактор | SQLite | Room | Realm |
|--------|--------|------|-------|
| APK размер | +0 KB | ≈ +50 KB | +3–5 MB |
| Безопасность типов | ❌ runtime | ✅ compile-time | ✅ compile-time (собственная модель) |
| Кривая обучения | Высокая (Cursor API) | Средняя (SQL + аннотации) | Низкая (OOP) |
| Миграции | Ручные скрипты | Декларативные Migration | Требует явной миграции API |
| Реактивность | ❌ | ✅ `Flow`/`LiveData` | ✅ встроенная |

**Рекомендации:**
- **Room** — дефолтный выбор для большинства production-приложений (официальная поддержка Google, интеграция с Jetpack).
- **SQLite** — подходит для случаев, где нужен полный контроль, минимальные зависимости или уже есть существующий SQL-слой (не только для legacy).
- **Realm** — если критична интеграция с MongoDB Atlas, нужны live-объекты/реактивность "из коробки" или рассматривается кросс-платформа.

## Answer (EN)

In Android, the following options are commonly used for persisting structured app data: SQLite (native), [[c-room]] (recommended abstraction over SQLite by Google), and Realm/MongoDB (alternative object NoSQL database).

### Core Concepts

**SQLite** — built-in relational database with no external dependencies, requires manual SQL and Cursor API handling.

**Room** — type-safe abstraction layer over SQLite (ORM/DAO style) with compile-time query validation, code generation, and native coroutines/`Flow` support.

**Realm/MongoDB** — object database with its own engine (not SQL), supports reactive queries and (in some setups) cloud sync, but increases APK size.

> Note: For key-value / preferences-like data Google recommends DataStore, but it is not a full relational database and is usually discussed separately.

### 1. SQLite — Low-Level API

Direct access via SQLiteOpenHelper and Cursor API. **Drawbacks**: boilerplate, manual Cursor/resource management, runtime SQL errors.

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

### 2. Room — Official Abstraction over SQLite (Recommended)

Generates DAO implementations at compile time via annotation processing. Provides safe suspend functions and `Flow` for reactive updates.

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

Object database with zero-copy architecture (live objects), built-in reactive data support and optional sync with MongoDB Atlas. **Cons**: +3–5 MB to APK, proprietary data format, migrations and migration to other solutions require explicit handling.

```kotlin
// Example with classic Realm Java API (for Kotlin/Multiplatform use the modern Realm Kotlin API).
class User : RealmObject() {
    @PrimaryKey var id: String = UUID.randomUUID().toString()
    var name: String = ""
}

// ✅ Reactive queries without additional libraries
realm.where<User>().findAllAsync().asFlow().collect { users ->
    // Auto-updates on DB changes
}

// ❌ Objects are tied to the Realm thread; use copyFromRealm()/appropriate API when passing across threads
```

### Selection Criteria

| Factor | SQLite | Room | Realm |
|--------|--------|------|-------|
| APK size | +0 KB | ≈ +50 KB | +3–5 MB |
| Type safety | ❌ runtime | ✅ compile-time | ✅ compile-time (own model) |
| Learning curve | High (Cursor API) | Medium (SQL + annotations) | Low (OOP) |
| Migrations | Manual scripts | Declarative Migration | Requires explicit migration API |
| Reactivity | ❌ | ✅ `Flow`/`LiveData` | ✅ built-in |

**Recommendations:**
- **Room** — default choice for most production apps (official Google support, Jetpack integration).
- **SQLite** — suitable when you need full control, minimal dependencies, or already have an SQL layer (not only for legacy).
- **Realm** — when MongoDB Atlas sync, built-in live objects/reactivity, or cross-platform needs are important.


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
