---
id: android-083
title: Room Library Definition / Определение библиотеки Room
aliases:
- Room Library Definition
- Определение библиотеки Room
topic: android
subtopics:
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
- q-android-jetpack-overview--android--easy
created: 2025-10-13
updated: 2025-11-10
tags:
- android/room
- difficulty/easy
sources:
- https://developer.android.com/codelabs/android-room-with-a-view-kotlin
- https://developer.android.com/training/data-storage/room
anki_cards:
- slug: android-083-0-en
  language: en
  anki_id: 1768382134765
  synced_at: '2026-01-23T16:45:05.910040'
- slug: android-083-0-ru
  language: ru
  anki_id: 1768382134786
  synced_at: '2026-01-23T16:45:05.912329'
---
# Вопрос (RU)
> Что такое библиотека `Room`?

# Question (EN)
> What is the `Room` library?

---

## Ответ (RU)

`Room` — это ORM-библиотека от Google, предоставляющая абстракцию над `SQLite` с типобезопасностью на этапе компиляции и проверкой SQL-запросов.

См. также: [[c-database-design]].

**Ключевые преимущества:**
- Проверка SQL во время компиляции
- Интеграция с `Flow`, `LiveData`, Coroutines
- Поддержка миграций схемы (включая autoMigrations для ограниченного набора изменений)
- Минимум шаблонного кода

**Три компонента архитектуры:**

**1. `Entity` (таблица):**
```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,  // ✅ автогенерация ID
    @ColumnInfo(name = "user_name") val name: String,
    val email: String
)
```

**2. DAO (доступ к данным):**
```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE email = :email")
    suspend fun getUserByEmail(email: String): User?  // ✅ suspend для корутин

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: User)  // ✅ обработка конфликтов
}
```

**3. `Database` (точка входа):**
```kotlin
@Database(entities = [User::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        @Volatile private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase =
            INSTANCE ?: synchronized(this) {  // ✅ потокобезопасный singleton
                INSTANCE ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                ).build().also { INSTANCE = it }
            }
    }
}
```

## Answer (EN)

`Room` is Google's ORM library providing an abstraction over `SQLite` with compile-time type safety and SQL query validation.

See also: [[c-database-design]].

**Key advantages:**
- SQL verification at compile time
- Integration with `Flow`, `LiveData`, Coroutines
- Schema migrations support (including autoMigrations for a limited set of changes)
- Minimal boilerplate code

**Three architecture components:**

**1. `Entity` (table):**
```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,  // ✅ auto-generated ID
    @ColumnInfo(name = "user_name") val name: String,
    val email: String
)
```

**2. DAO (data access):**
```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE email = :email")
    suspend fun getUserByEmail(email: String): User?  // ✅ suspend for coroutines

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: User)  // ✅ conflict handling
}
```

**3. `Database` (entry point):**
```kotlin
@Database(entities = [User::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        @Volatile private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase =
            INSTANCE ?: synchronized(this) {  // ✅ thread-safe singleton
                INSTANCE ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                ).build().also { INSTANCE = it }
            }
    }
}
```

---

## Дополнительные Вопросы (RU)

- Как `Room` обрабатывает миграции базы данных между версиями схемы?
- Каковы правила работы с потоками (threading rules) для операций `Room`?
- Как реализовать сложные запросы с отношениями (one-to-many, many-to-many)?
- В чем разница между `@Insert`, `@Update` и `@Upsert`?
- Как `Room` поддерживает RxJava и Kotlin `Flow` для реактивных запросов?

## Follow-ups

- How does `Room` handle database migrations between schema versions?
- What are the threading rules for `Room` operations?
- How do you implement complex queries with relationships (one-to-many, many-to-many)?
- What's the difference between `@Insert`, `@Update`, and `@Upsert`?
- How does `Room` support RxJava and Kotlin `Flow` for reactive queries?

## Ссылки (RU)

- https://developer.android.com/training/data-storage/room - Официальная документация по `Room`
- https://developer.android.com/codelabs/android-room-with-a-view-kotlin - Codelab по `Room`

## References

- https://developer.android.com/training/data-storage/room - Official `Room` documentation
- https://developer.android.com/codelabs/android-room-with-a-view-kotlin - `Room` codelab

## Связанные Вопросы (RU)

### Предварительные (проще)
- Android варианты хранения данных (см. вопрос об общих вариантах хранения данных в Android)
- Основы `SQLite` (см. вопрос об основах `SQLite` в Android)

### Связанные (того Же уровня)
- Базовые операции `Room`
- Определение сущностей (`Entity`) в `Room`
- Паттерны реализации DAO в `Room`

### Продвинутые (сложнее)
- Миграции схемы базы данных в `Room`
- Моделирование связей таблиц в `Room`
- Тестирование баз данных `Room`

## Related Questions

### Prerequisites (Easier)
- Android data storage options
- `SQLite` fundamentals

### Related (Same Level)
- `Room` basic operations
- Defining `Room` entities
- DAO implementation patterns

### Advanced (Harder)
- `Room` database schema migrations
- Modeling table relationships in `Room`
- Testing `Room` databases
