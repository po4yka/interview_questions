---\
id: android-475
title: Databases Android / Базы данных в Android
aliases: [Databases Android, Базы данных в Android]
topic: android
subtopics: [datastore, room]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-database-design, q-android-storage-types--android--medium, q-database-encryption-android--android--medium, q-database-optimization-android--android--medium, q-how-to-start-drawing-ui-in-android--android--easy]
created: 2025-10-20
updated: 2025-11-10
tags: [android/datastore, android/room, database, difficulty/easy]
sources:
  - "https://developer.android.com/training/data-storage"

---\
# Вопрос (RU)
> Какие базы данных можно использовать в Android?

# Question (EN)
> What databases can be used in Android?

## Ответ (RU)

В Android на практике для персистентности данных используют несколько подходов. Для структурированных/реляционных данных чаще всего применяют: `SQLite` (встроенная), [[c-room]] (рекомендуемая надстройка над `SQLite` от Google), и Realm/MongoDB (альтернативная объектная NoSQL-БД). Для простых ключ-значение и настроек обычно используют DataStore (современная замена `SharedPreferences`), но это не реляционная БД.

### Основные Концепции

**`SQLite`** — встроенная реляционная БД без внешних зависимостей, требует ручного SQL и работы с Cursor API.

**`Room`** — типобезопасная обёртка над `SQLite` (ORM/DAO слой) с compile-time валидацией запросов, генерацией кода, нативной поддержкой корутин/`Flow` и проверками, что долгие операции не выполняются на главном потоке.

**Realm/MongoDB** — объектная БД с собственным движком (не SQL), поддерживает реактивные запросы и (в некоторых конфигурациях) синхронизацию с облаком, но увеличивает размер APK.

> Примечание: Для ключ-значение/настроек Google рекомендует использовать DataStore (Preferences/Proto), но это не полноценная реляционная БД и обычно упоминается отдельно от SQLite/Room/Realm.

### 1. SQLite — Низкоуровневый API

Прямой доступ через SQLiteOpenHelper и Cursor API. **Недостатки**: boilerplate, ручное управление ресурсами Cursor, runtime SQL-ошибки, ответственность за выполнение тяжелых операций не на главном потоке лежит на разработчике.

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

### 2. Room — Официальный Абстракционный Слой Над SQLite (рекомендуется)

Генерирует имплементации DAO на этапе компиляции через annotation processing. Предоставляет безопасные suspend-функции и `Flow` для реактивных обновлений. По умолчанию запрещает блокирующие операции с БД на главном потоке.

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
// Пример модели для классического Realm Java API. Для Kotlin/Multiplatform используется современный Realm Kotlin API,
// который предоставляет интеграцию с корутинами и Flow.
class User : RealmObject() {
    @PrimaryKey var id: String = UUID.randomUUID().toString()
    var name: String = ""
}

// ✅ Реактивные запросы доступны в зависимости от используемого SDK (Rx, Kotlin Flow и т.п.).
// Конкретный API отличается между classic Realm Java и Realm Kotlin.

// ❌ Объекты привязаны к Realm-треду; для передачи между потоками требуется copyFromRealm()/или соответствующий API выбранного SDK.
```

### Критерии Выбора

| Фактор | `SQLite` | `Room` | Realm |
|--------|--------|------|-------|
| APK размер | +0 KB | ≈ +50 KB | +3–5 MB |
| Безопасность типов | ❌ runtime | ✅ compile-time | ✅ compile-time (собственная модель) |
| Кривая обучения | Высокая (Cursor API) | Средняя (SQL + аннотации) | Низкая (OOP) |
| Миграции | Ручные скрипты | Декларативные Migration | Требует явной миграции API |
| Реактивность | ❌ | ✅ `Flow`/`LiveData` | ✅ встроенная |

**Рекомендации:**
- **`Room`** — дефолтный выбор для большинства production-приложений (официальная поддержка Google, интеграция с Jetpack).
- **`SQLite`** — подходит для случаев, где нужен полный контроль, минимальные зависимости или уже есть существующий SQL-слой (не только для legacy).
- **Realm** — если критична интеграция с MongoDB Atlas, нужны live-объекты/реактивность "из коробки" или рассматривается кросс-платформа.

## Answer (EN)

In Android, several options are used in practice for data persistence. For structured/relational data, the most common ones are: `SQLite` (built-in), [[c-room]] (recommended abstraction over `SQLite` by Google), and Realm/MongoDB (alternative object NoSQL database). For simple key-value / preferences-like data, DataStore (the modern replacement for `SharedPreferences`) is typically used, but it is not a relational database.

### Core Concepts

**`SQLite`** — built-in relational database with no external dependencies, requires manual SQL and Cursor API handling.

**`Room`** — type-safe abstraction layer over `SQLite` (ORM/DAO style) with compile-time query validation, code generation, native coroutines/`Flow` support, and safeguards ensuring long-running operations are not performed on the main thread.

**Realm/MongoDB** — object database with its own engine (not SQL), supports reactive queries and (in some setups) cloud sync, but increases APK size.

> Note: For key-value / preferences-like data Google recommends DataStore (Preferences/Proto), but it is not a full relational database and is usually discussed separately from SQLite/Room/Realm.

### 1. SQLite — Low-Level API

Direct access via SQLiteOpenHelper and Cursor API. **Drawbacks**: boilerplate, manual Cursor/resource management, runtime SQL errors, and you are responsible for keeping heavy operations off the main thread.

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

Generates DAO implementations at compile time via annotation processing. `Provides` safe suspend functions and `Flow` for reactive updates. By default, disallows blocking database operations on the main thread.

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

Object database with zero-copy architecture (live objects), built-in reactive data support, and optional sync with MongoDB Atlas. **Cons**: +3–5 MB to APK, proprietary data format, migrations and migration to other solutions require explicit handling.

```kotlin
// Example model for the classic Realm Java API. For Kotlin/Multiplatform, use the modern Realm Kotlin API,
// which provides integration with coroutines and Flow.
class User : RealmObject() {
    @PrimaryKey var id: String = UUID.randomUUID().toString()
    var name: String = ""
}

// ✅ Reactive queries are available depending on the SDK in use (Rx, Kotlin Flow, etc.).
// The exact APIs differ between classic Realm Java and Realm Kotlin.

// ❌ Objects are thread-confined; use copyFromRealm()/or the appropriate API when passing across threads.
```

### Selection Criteria

| Factor | `SQLite` | `Room` | Realm |
|--------|--------|------|-------|
| APK size | +0 KB | ≈ +50 KB | +3–5 MB |
| Type safety | ❌ runtime | ✅ compile-time | ✅ compile-time (own model) |
| Learning curve | High (Cursor API) | Medium (SQL + annotations) | Low (OOP) |
| Migrations | Manual scripts | Declarative Migration | Requires explicit migration API |
| Reactivity | ❌ | ✅ `Flow`/`LiveData` | ✅ built-in |

**Recommendations:**
- **`Room`** — default choice for most production apps (official Google support, Jetpack integration).
- **`SQLite`** — suitable when you need full control, minimal dependencies, or already have an SQL layer (not only for legacy).
- **Realm** — when MongoDB Atlas sync, built-in live objects/reactivity, or cross-platform needs are important.

## Follow-ups

- How do you implement database migrations in `Room` when schema changes?
- What are the threading constraints for each database solution?
- When would you use DataStore instead of a database?
- How do you handle database encryption and security?
- What's the impact of using in-memory vs file-based databases?

## References

- [[c-room]] — `Room` persistence library concepts
- [[c-database-design]] — `Database` design patterns
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
