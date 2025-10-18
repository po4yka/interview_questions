---
id: 20251016-162557
title: "Databases Android / Базы данных в Android"
topic: android
difficulty: easy
status: draft
created: 2025-10-13
tags: [android/data-storage, data-storage, database, realm, room, sqlite, difficulty/easy]
moc: moc-android
related: [q-how-to-add-custom-attributes-to-custom-view--programming-languages--medium, q-play-app-signing--android--medium, q-recomposition-choreographer--android--hard]
---
# Какие базы данных можно использовать в Android?

**English**: What databases can be used in Android?

## Answer (EN)
Android applications can use **three main database options**: **SQLite**, **Room**, and **Realm**.

## 1. SQLite

**Built-in relational database** for Android. Lightweight, serverless, self-contained.

**Characteristics:**
-  Built into Android
-  Requires manual SQL queries
-  Low-level API
-  More boilerplate code

**Example:**

```kotlin
class DatabaseHelper(context: Context) : SQLiteOpenHelper(
    context,
    "app_database.db",
    null,
    1
) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS users")
        onCreate(db)
    }
}

// Insert
fun insertUser(name: String, email: String) {
    val db = dbHelper.writableDatabase
    val values = ContentValues().apply {
        put("name", name)
        put("email", email)
    }
    db.insert("users", null, values)
}

// Query
fun getUsers(): List<User> {
    val db = dbHelper.readableDatabase
    val cursor = db.rawQuery("SELECT * FROM users", null)
    val users = mutableListOf<User>()

    with(cursor) {
        while (moveToNext()) {
            val id = getInt(getColumnIndexOrThrow("id"))
            val name = getString(getColumnIndexOrThrow("name"))
            val email = getString(getColumnIndexOrThrow("email"))
            users.add(User(id, name, email))
        }
    }
    cursor.close()
    return users
}
```

**Pros:**
-  Built-in, no dependencies
-  Full SQL power
-  Lightweight

**Cons:**
-  Lots of boilerplate
-  No compile-time SQL validation
-  Manual cursor handling
-  No type safety

---

## 2. Room

**Abstraction layer over SQLite** from Android Jetpack. Recommended by Google.

**Characteristics:**
-  Type-safe database access
-  Compile-time SQL validation
-  LiveData/Flow support
-  Annotation-based

**Example:**

```kotlin
// Entity
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val name: String,
    val email: String
)

// DAO
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: Int): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)
}

// Database
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

// Setup
val db = Room.databaseBuilder(
    context,
    AppDatabase::class.java,
    "app_database"
).build()

// Usage
val userDao = db.userDao()

// Insert
viewModelScope.launch {
    userDao.insertUser(User(name = "John", email = "john@example.com"))
}

// Observe data
viewLifecycleOwner.lifecycleScope.launch {
    userDao.getAllUsers().collect { users ->
        // Update UI
    }
}
```

**Pros:**
-  Type-safe API
-  Compile-time SQL validation
-  Less boilerplate
-  LiveData/Flow integration
-  Automatic migrations
-  Coroutines support

**Cons:**
-  Annotation processing overhead
-  Learning curve
-  Still uses SQLite under the hood

---

## 3. Realm

**Modern mobile database** - object-oriented, fast, reactive.

**Characteristics:**
-  Fast performance
-  Reactive queries
-  Mobile-first design
-  Cloud sync support

**Example:**

```kotlin
// Model
open class User : RealmObject() {
    @PrimaryKey
    var id: Int = 0
    var name: String = ""
    var email: String = ""
}

// Setup
Realm.init(context)
val config = RealmConfiguration.Builder()
    .name("app.realm")
    .schemaVersion(1)
    .build()

Realm.setDefaultConfiguration(config)

// Insert
val realm = Realm.getDefaultInstance()
realm.executeTransaction {
    val user = it.createObject(User::class.java, 1)
    user.name = "John"
    user.email = "john@example.com"
}

// Query
val users = realm.where(User::class.java).findAll()

// Reactive queries
realm.where(User::class.java)
    .findAllAsync()
    .addChangeListener { results ->
        // Auto-updates when data changes
    }

// Close
realm.close()
```

**Pros:**
-  Very fast (faster than SQLite for some operations)
-  Object-oriented (no SQL)
-  Reactive queries
-  Cross-platform (iOS, Android, etc.)
-  Built-in encryption
-  Cloud sync (Realm Sync)

**Cons:**
-  External dependency
-  Larger library size
-  Proprietary format
-  Migration can be complex

**Dependencies:**

```kotlin
// build.gradle (project)
buildscript {
    dependencies {
        classpath "io.realm:realm-gradle-plugin:10.15.1"
    }
}

// build.gradle (app)
apply plugin: 'realm-android'
```

---

## Comparison Table

| Feature | SQLite | Room | Realm |
|---------|--------|------|-------|
| **Type** | Relational | Relational (ORM) | Object DB |
| **Boilerplate** | High | Low | Low |
| **Type Safety** |  No |  Yes |  Yes |
| **SQL Knowledge** | Required | Required | Not required |
| **Reactive** |  No |  Flow/LiveData |  Yes |
| **Performance** | Good | Good | Excellent |
| **Size** | Built-in | Small | Large |
| **Learning Curve** | Medium | Medium | Medium |
| **Cloud Sync** |  No |  No |  Yes |

## Which to Choose?

**Use SQLite if:**
- You need full control
- No external dependencies
- Simple use case

**Use Room if:**  **Recommended**
- Building modern Android app
- Want type safety and less boilerplate
- Using Jetpack components
- Need LiveData/Flow integration

**Use Realm if:**
- Need maximum performance
- Want reactive queries
- Cross-platform project
- Need cloud sync

## Migration Comparison

**SQLite:**
```kotlin
override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
    db.execSQL("ALTER TABLE users ADD COLUMN age INTEGER")
}
```

**Room:**
```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("ALTER TABLE users ADD COLUMN age INTEGER NOT NULL DEFAULT 0")
    }
}

Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .addMigrations(MIGRATION_1_2)
    .build()
```

**Realm:**
```kotlin
val config = RealmConfiguration.Builder()
    .schemaVersion(2)
    .migration { realm, oldVersion, newVersion ->
        if (oldVersion == 1L) {
            realm.schema.get("User")?.addField("age", Int::class.java)
        }
    }
    .build()
```

## Summary

**Three main databases for Android:**

1. **SQLite** - Built-in relational database, manual SQL
2. **Room** - Abstraction over SQLite, type-safe, recommended 
3. **Realm** - Modern object database, fast, reactive

**Recommendation:** Use **Room** for most Android projects. It provides the best balance of ease of use, performance, and integration with Android architecture components.

## Ответ (RU)


Android-приложения могут использовать **три основных варианта баз данных**: **SQLite**, **Room** и **Realm**.


## 1. SQLite

**Встроенная реляционная база данных** для Android. Легковесная, безсерверная, самодостаточная.

**Характеристики:**
- Встроена в Android
- Требует ручных SQL-запросов
- Низкоуровневый API
- Больше шаблонного кода

**Пример:**

```kotlin
class DatabaseHelper(context: Context) : SQLiteOpenHelper(
    context,
    "app_database.db",
    null,
    1
) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS users")
        onCreate(db)
    }
}

// Вставка
fun insertUser(name: String, email: String) {
    val db = dbHelper.writableDatabase
    val values = ContentValues().apply {
        put("name", name)
        put("email", email)
    }
    db.insert("users", null, values)
}

// Запрос
fun getUsers(): List<User> {
    val db = dbHelper.readableDatabase
    val cursor = db.rawQuery("SELECT * FROM users", null)
    val users = mutableListOf<User>()

    with(cursor) {
        while (moveToNext()) {
            val id = getInt(getColumnIndexOrThrow("id"))
            val name = getString(getColumnIndexOrThrow("name"))
            val email = getString(getColumnIndexOrThrow("email"))
            users.add(User(id, name, email))
        }
    }
    cursor.close()
    return users
}
```

**Преимущества:**
- Встроена, без зависимостей
- Полная мощь SQL
- Легковесная

**Недостатки:**
- Много шаблонного кода
- Нет проверки SQL на этапе компиляции
- Ручное управление курсорами
- Нет типобезопасности

---

## 2. Room

**Слой абстракции поверх SQLite** из Android Jetpack. Рекомендуется Google.

**Характеристики:**
- Типобезопасный доступ к БД
- Проверка SQL на этапе компиляции
- Поддержка LiveData/Flow
- Основан на аннотациях

**Пример:**

```kotlin
// Entity
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val name: String,
    val email: String
)

// DAO
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: Int): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)
}

// Database
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

// Настройка
val db = Room.databaseBuilder(
    context,
    AppDatabase::class.java,
    "app_database"
).build()

// Использование
val userDao = db.userDao()

// Вставка
viewModelScope.launch {
    userDao.insertUser(User(name = "John", email = "john@example.com"))
}

// Наблюдение за данными
viewLifecycleOwner.lifecycleScope.launch {
    userDao.getAllUsers().collect { users ->
        // Обновление UI
    }
}
```

**Преимущества:**
- Типобезопасный API
- Проверка SQL на этапе компиляции
- Меньше шаблонного кода
- Интеграция с LiveData/Flow
- Автоматические миграции
- Поддержка корутин

**Недостатки:**
- Накладные расходы на обработку аннотаций
- Кривая обучения
- Использует SQLite под капотом

---

## 3. Realm

**Современная мобильная база данных** - объектно-ориентированная, быстрая, реактивная.

**Характеристики:**
- Высокая производительность
- Реактивные запросы
- Дизайн для мобильных устройств
- Поддержка облачной синхронизации

**Пример:**

```kotlin
// Модель
open class User : RealmObject() {
    @PrimaryKey
    var id: Int = 0
    var name: String = ""
    var email: String = ""
}

// Настройка
Realm.init(context)
val config = RealmConfiguration.Builder()
    .name("app.realm")
    .schemaVersion(1)
    .build()

Realm.setDefaultConfiguration(config)

// Вставка
val realm = Realm.getDefaultInstance()
realm.executeTransaction {
    val user = it.createObject(User::class.java, 1)
    user.name = "John"
    user.email = "john@example.com"
}

// Запрос
val users = realm.where(User::class.java).findAll()

// Реактивные запросы
realm.where(User::class.java)
    .findAllAsync()
    .addChangeListener { results ->
        // Автообновление при изменении данных
    }

// Закрытие
realm.close()
```

**Преимущества:**
- Очень быстрая (быстрее SQLite для некоторых операций)
- Объектно-ориентированная (без SQL)
- Реактивные запросы
- Кроссплатформенная (iOS, Android и др.)
- Встроенное шифрование
- Облачная синхронизация (Realm Sync)

**Недостатки:**
- Внешняя зависимость
- Больший размер библиотеки
- Проприетарный формат
- Миграции могут быть сложными

**Зависимости:**

```kotlin
// build.gradle (project)
buildscript {
    dependencies {
        classpath "io.realm:realm-gradle-plugin:10.15.1"
    }
}

// build.gradle (app)
apply plugin: 'realm-android'
```

---

## Таблица сравнения

| Функция | SQLite | Room | Realm |
|---------|--------|------|-------|
| **Тип** | Реляционная | Реляционная (ORM) | Объектная БД |
| **Шаблонный код** | Много | Мало | Мало |
| **Типобезопасность** | Нет | Да | Да |
| **Знание SQL** | Требуется | Требуется | Не требуется |
| **Реактивность** | Нет | Flow/LiveData | Да |
| **Производительность** | Хорошая | Хорошая | Отличная |
| **Размер** | Встроена | Малый | Большой |
| **Кривая обучения** | Средняя | Средняя | Средняя |
| **Облачная синхронизация** | Нет | Нет | Да |

## Какую выбрать?

**Используйте SQLite если:**
- Нужен полный контроль
- Без внешних зависимостей
- Простой случай использования

**Используйте Room если:** **Рекомендуется**
- Создаёте современное Android приложение
- Хотите типобезопасность и меньше шаблонного кода
- Используете компоненты Jetpack
- Нужна интеграция с LiveData/Flow

**Используйте Realm если:**
- Нужна максимальная производительность
- Хотите реактивные запросы
- Кроссплатформенный проект
- Нужна облачная синхронизация

## Сравнение миграций

**SQLite:**
```kotlin
override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
    db.execSQL("ALTER TABLE users ADD COLUMN age INTEGER")
}
```

**Room:**
```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("ALTER TABLE users ADD COLUMN age INTEGER NOT NULL DEFAULT 0")
    }
}

Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .addMigrations(MIGRATION_1_2)
    .build()
```

**Realm:**
```kotlin
val config = RealmConfiguration.Builder()
    .schemaVersion(2)
    .migration { realm, oldVersion, newVersion ->
        if (oldVersion == 1L) {
            realm.schema.get("User")?.addField("age", Int::class.java)
        }
    }
    .build()
```

## Итог

**Три основные базы данных для Android:**

1. **SQLite** - Встроенная реляционная БД, ручные SQL-запросы
2. **Room** - Абстракция поверх SQLite, типобезопасная, рекомендуется
3. **Realm** - Современная объектная БД, быстрая, реактивная

**Рекомендация:** Используйте **Room** для большинства Android проектов. Она обеспечивает лучший баланс между простотой использования, производительностью и интеграцией с компонентами архитектуры Android.


---

## Related Questions

### Related (Easy)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-sharedpreferences-definition--android--easy]] - Storage
- [[q-room-library-definition--android--easy]] - Storage

### Advanced (Harder)
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--room--medium]] - Storage
- [[q-room-paging3-integration--room--medium]] - Storage
