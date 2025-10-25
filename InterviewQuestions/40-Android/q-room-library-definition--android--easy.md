---
id: 20251012-12271188
title: "Room Library Definition / Определение библиотеки Room"
aliases:
  - "Room Library Definition"
  - "Определение библиотеки Room"
topic: android
subtopics: [data-storage, room]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-room-library, q-room-basics--android--easy, q-sqlite-vs-room--android--medium]
created: 2025-10-13
updated: 2025-01-25
tags: [android/data-storage, android/room, room, database, orm, sqlite, difficulty/easy]
sources: [https://developer.android.com/training/data-storage/room]
---

# Вопрос (RU)
> Что такое библиотека Room?

# Question (EN)
> What is the Room library?

---

## Ответ (RU)

**Теория Room:**
Room - это библиотека управления базами данных, которая служит абстрактным слоем над SQLite. Она обеспечивает типобезопасность, уменьшает шаблонный код и предоставляет удобную интеграцию с современными архитектурными компонентами Android.

**Основные преимущества:**
- Типобезопасность на этапе компиляции
- Проверка SQL-запросов во время компиляции
- Интеграция с LiveData, Flow, RxJava
- Автоматические миграции базы данных
- Уменьшение шаблонного кода

**Три основных компонента:**

**1. Entity (Сущность):**
```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val name: String,
    val email: String
)
```

**2. DAO (Data Access Object):**
```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)
}
```

**3. Database (База данных):**
```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

**Использование в ViewModel:**
```kotlin
class UserViewModel(private val userDao: UserDao) : ViewModel() {
    val allUsers: Flow<List<User>> = userDao.getAllUsers()

    fun addUser(name: String, email: String) {
        viewModelScope.launch {
            val user = User(name = name, email = email)
            userDao.insertUser(user)
        }
    }
}
```

## Answer (EN)

**Room Theory:**
Room is a database management library that serves as an abstraction layer over SQLite. It provides type safety, reduces boilerplate code, and offers convenient integration with modern Android architectural components.

**Main advantages:**
- Compile-time type safety
- SQL query validation at compile time
- Integration with LiveData, Flow, RxJava
- Automatic database migrations
- Reduced boilerplate code

**Three main components:**

**1. Entity:**
```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val name: String,
    val email: String
)
```

**2. DAO (Data Access Object):**
```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)
}
```

**3. Database:**
```kotlin
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

**Usage in ViewModel:**
```kotlin
class UserViewModel(private val userDao: UserDao) : ViewModel() {
    val allUsers: Flow<List<User>> = userDao.getAllUsers()

    fun addUser(name: String, email: String) {
        viewModelScope.launch {
            val user = User(name = name, email = email)
            userDao.insertUser(user)
        }
    }
}
```

---

## Follow-ups

- How does Room compare to raw SQLite?
- What are the benefits of using Room over other ORMs?
- How do you handle database migrations in Room?

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-data-storage-basics--android--easy]] - Data storage basics

### Related (Same Level)
- [[q-room-basics--android--easy]] - Room basics
- [[q-sqlite-vs-room--android--medium]] - SQLite vs Room
- [[q-data-persistence--android--medium]] - Data persistence

### Advanced (Harder)
- [[q-room-advanced--android--hard]] - Room advanced
- [[q-database-optimization--android--hard]] - Database optimization
