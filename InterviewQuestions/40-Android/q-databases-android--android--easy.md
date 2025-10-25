---
id: 20251020-200000
title: Databases Android / Базы данных в Android
aliases:
- Databases Android
- Базы данных в Android
topic: android
subtopics:
- room
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-room-database-basics--android--easy
- q-database-optimization-android--android--medium
- q-database-encryption-android--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
- android/room
- database
- realm
- room
- sqlite
- difficulty/easy
source: https://developer.android.com/training/data-storage
source_note: Android Data Storage documentation
---

# Вопрос (RU)
> Какие базы данных можно использовать в Android?

# Question (EN)
> What databases can be used in Android?

## Ответ (RU)

Android приложения могут использовать **три основных варианта баз данных**: **SQLite**, **Room**, и **Realm**.

### Теория: Типы баз данных в Android

**Основные концепции:**
- **SQLite** - встроенная реляционная база данных
- **Room** - абстракция над SQLite с компиляционной проверкой
- **Realm** - объектно-ориентированная база данных
- **Выбор базы данных** - зависит от требований проекта
- **Производительность** - различные характеристики для разных типов данных

**Принципы работы:**
- SQLite встроена в Android и не требует дополнительных зависимостей
- Room предоставляет типизированный API над SQLite
- Realm использует собственный движок базы данных
- Все варианты поддерживают локальное хранение данных

### 1. SQLite

**Теоретические основы:**
SQLite - это встроенная реляционная база данных, которая поставляется с Android. Она легковесная, не требует сервера и полностью автономна.

**Характеристики:**
- Встроена в Android
- Требует ручных SQL запросов
- Низкоуровневый API
- Больше boilerplate кода

**Компактная реализация:**
```kotlin
class DatabaseHelper(context: Context) : SQLiteOpenHelper(context, "app_database.db", null, 1) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL)")
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS users")
        onCreate(db)
    }
}
```

### 2. Room

**Теоретические основы:**
Room - это библиотека персистентности, которая предоставляет абстракцию над SQLite. Она обеспечивает компиляционную проверку SQL запросов и упрощает работу с базой данных.

**Преимущества:**
- Компиляционная проверка SQL запросов
- Типизированный API
- Автоматическая генерация кода
- Поддержка RxJava и корутин
- Миграции базы данных

**Компактная реализация:**
```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val name: String,
    val email: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>

    @Insert
    suspend fun insertUser(user: User)

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

### 3. Realm

**Теоретические основы:**
Realm - это объектно-ориентированная база данных, которая использует собственный движок. Она предоставляет простой API для работы с объектами без необходимости в SQL.

**Преимущества:**
- Простой объектно-ориентированный API
- Высокая производительность
- Автоматические обновления UI
- Поддержка сложных типов данных
- Кроссплатформенность

**Компактная реализация:**
```kotlin
open class User : RealmObject() {
    @PrimaryKey
    var id: Long = 0
    var name: String = ""
    var email: String = ""
}

class RealmManager {
    private val realm: Realm by lazy { Realm.getDefaultInstance() }

    fun saveUser(user: User) {
        realm.executeTransaction { realm.copyToRealmOrUpdate(user) }
    }

    fun getUsers(): RealmResults<User> {
        return realm.where(User::class.java).findAll()
    }
}
```

### Сравнение баз данных

| Критерий | SQLite | Room | Realm |
|----------|--------|------|-------|
| Сложность | Высокая | Средняя | Низкая |
| Производительность | Хорошая | Хорошая | Отличная |
| Размер APK | Минимальный | Средний | Большой |
| Поддержка | Встроенная | Google | Realm |
| Типизация | Ручная | Автоматическая | Автоматическая |

### Выбор базы данных

**SQLite подходит для:**
- Простых приложений с минимальными требованиями
- Когда размер APK критически важен
- Опытных разработчиков, знакомых с SQL

**Room подходит для:**
- Большинства Android приложений
- Когда нужна типизация и безопасность типов
- Проектов с командной разработкой

**Realm подходит для:**
- Приложений с высокой производительностью
- Сложных объектных моделей
- Кроссплатформенных проектов

## Answer (EN)

Android applications can use **three main database options**: **SQLite**, **Room**, and **Realm**.

### Theory: Database Types in Android

**Core Concepts:**
- **SQLite** - built-in relational database
- **Room** - abstraction over SQLite with compile-time checking
- **Realm** - object-oriented database
- **Database Selection** - depends on project requirements
- **Performance** - different characteristics for different data types

**Working Principles:**
- SQLite is built into Android and requires no additional dependencies
- Room provides typed API over SQLite
- Realm uses its own database engine
- All options support local data storage

### 1. SQLite

**Theoretical Foundations:**
SQLite is a built-in relational database that comes with Android. It's lightweight, serverless, and completely self-contained.

**Characteristics:**
- Built into Android
- Requires manual SQL queries
- Low-level API
- More boilerplate code

**Compact Implementation:**
```kotlin
class DatabaseHelper(context: Context) : SQLiteOpenHelper(context, "app_database.db", null, 1) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL)")
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS users")
        onCreate(db)
    }
}
```

### 2. Room

**Theoretical Foundations:**
Room is a persistence library that provides an abstraction over SQLite. It ensures compile-time verification of SQL queries and simplifies database work.

**Benefits:**
- Compile-time verification of SQL queries
- Typed API
- Automatic code generation
- RxJava and coroutine support
- Database migrations

**Compact Implementation:**
```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val name: String,
    val email: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>

    @Insert
    suspend fun insertUser(user: User)

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

### 3. Realm

**Theoretical Foundations:**
Realm is an object-oriented database that uses its own engine. It provides a simple API for working with objects without the need for SQL.

**Benefits:**
- Simple object-oriented API
- High performance
- Automatic UI updates
- Complex data type support
- Cross-platform compatibility

**Compact Implementation:**
```kotlin
open class User : RealmObject() {
    @PrimaryKey
    var id: Long = 0
    var name: String = ""
    var email: String = ""
}

class RealmManager {
    private val realm: Realm by lazy { Realm.getDefaultInstance() }

    fun saveUser(user: User) {
        realm.executeTransaction { realm.copyToRealmOrUpdate(user) }
    }

    fun getUsers(): RealmResults<User> {
        return realm.where(User::class.java).findAll()
    }
}
```

### Database Comparison

| Criterion | SQLite | Room | Realm |
|-----------|--------|------|-------|
| Complexity | High | Medium | Low |
| Performance | Good | Good | Excellent |
| APK Size | Minimal | Medium | Large |
| Support | Built-in | Google | Realm |
| Typing | Manual | Automatic | Automatic |

### Database Selection

**SQLite is suitable for:**
- Simple applications with minimal requirements
- When APK size is critical
- Experienced developers familiar with SQL

**Room is suitable for:**
- Most Android applications
- When typing and type safety are needed
- Team development projects

**Realm is suitable for:**
- High-performance applications
- Complex object models
- Cross-platform projects

**See also:** c-sqlite, c-database-basics


## Follow-ups

- How do you choose between different database options?
- What are the performance implications of each database type?
- How do you handle database migrations?

## Related Questions

### Advanced (Harder)
- [[q-database-optimization-android--android--medium]]
- [[q-database-encryption-android--android--medium]]
