---
id: android-083
title: "Room Library Definition / Определение библиотеки Room"
aliases: ["Room Library Definition", "Определение библиотеки Room"]
topic: android
subtopics: [room]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-room-library, q-data-storage-options--android--easy]
created: 2025-10-13
updated: 2025-10-28
tags: [android/room, database, difficulty/easy, orm, room, sqlite]
sources: []
date created: Saturday, November 1st 2025, 1:04:42 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Вопрос (RU)
> Что такое библиотека Room?

# Question (EN)
> What is the Room library?

---

## Ответ (RU)

Room — это ORM-библиотека от Google, предоставляющая абстракцию над SQLite с типобезопасностью на этапе компиляции и проверкой SQL-запросов.

**Ключевые преимущества:**
- Проверка SQL во время компиляции
- Интеграция с Flow, LiveData, Coroutines
- Автоматические миграции схемы
- Минимум шаблонного кода

**Три компонента архитектуры:**

**1. Entity (таблица):**
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

**3. Database (точка входа):**
```kotlin
@Database(entities = [User::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        @Volatile private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase =
            INSTANCE ?: synchronized(this) {  // ✅ потокобезопасный singleton
                INSTANCE ?: buildDatabase(context).also { INSTANCE = it }
            }
    }
}
```

## Answer (EN)

Room is Google's ORM library providing an abstraction over SQLite with compile-time type safety and SQL query validation.

**Key advantages:**
- SQL verification at compile time
- Integration with Flow, LiveData, Coroutines
- Automatic schema migrations
- Minimal boilerplate code

**Three architecture components:**

**1. Entity (table):**
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

**3. Database (entry point):**
```kotlin
@Database(entities = [User::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        @Volatile private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase =
            INSTANCE ?: synchronized(this) {  // ✅ thread-safe singleton
                INSTANCE ?: buildDatabase(context).also { INSTANCE = it }
            }
    }
}
```

---

## Follow-ups

- How does Room handle database migrations between schema versions?
- What are the threading rules for Room operations?
- How do you implement complex queries with relationships (one-to-many, many-to-many)?
- What's the difference between `@Insert`, `@Update`, and `@Upsert`?
- How does Room support RxJava and Kotlin Flow for reactive queries?

## References

- [[c-room-library]] - Room library concept
- [[c-sqlite]] - SQLite database basics
- [[c-orm]] - Object-Relational Mapping patterns
- https://developer.android.com/training/data-storage/room - Official Room documentation
- https://developer.android.com/codelabs/android-room-with-a-view-kotlin - Room codelab

## Related Questions

### Prerequisites (Easier)
- [[q-data-storage-options--android--easy]] - Android data storage options
- [[q-sqlite-basics--android--easy]] - SQLite fundamentals

### Related (Same Level)
- [[q-room-basics--android--easy]] - Room basic operations
- [[q-room-entities--android--easy]] - Defining Room entities
- [[q-room-dao--android--medium]] - DAO implementation patterns

### Advanced (Harder)
- [[q-room-database-migrations--android--medium]] - Database schema migrations
- [[q-room-relationships--android--medium]] - Modeling table relationships
- [[q-room-testing--android--hard]] - Testing Room databases
