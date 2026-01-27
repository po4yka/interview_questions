---
id: kotlin-kmp-006
title: KMP Persistence / Хранение данных в KMP
aliases:
- SQLDelight KMP
- DataStore KMP
- Cross-Platform Storage
topic: kotlin
subtopics:
- kmp
- multiplatform
- persistence
- database
- storage
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- kmp
- multiplatform
- sqldelight
- datastore
- persistence
- difficulty/medium
anki_cards:
- slug: kotlin-kmp-006-0-en
  language: en
  anki_id: 1769344151991
  synced_at: '2026-01-25T16:29:12.042406'
- slug: kotlin-kmp-006-0-ru
  language: ru
  anki_id: 1769344152040
  synced_at: '2026-01-25T16:29:12.044197'
---
# Question (EN)
> How do you implement shared data persistence in Kotlin Multiplatform using SQLDelight and DataStore?

# Vopros (RU)
> Как реализовать общее хранение данных в Kotlin Multiplatform с использованием SQLDelight и DataStore?

## Answer (EN)

Kotlin Multiplatform offers several options for shared data persistence. The two most popular are **SQLDelight** for structured relational data and **DataStore** for key-value preferences.

### SQLDelight - Relational Database

SQLDelight generates typesafe Kotlin APIs from SQL statements. It works with SQLite on Android and iOS.

#### Setup

```kotlin
// build.gradle.kts (shared module)
plugins {
    kotlin("multiplatform")
    id("app.cash.sqldelight") version "2.0.0"
}

sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.db")
            generateAsync.set(true)
        }
    }
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.sqldelight.runtime)
            implementation(libs.sqldelight.coroutines)
        }

        androidMain.dependencies {
            implementation(libs.sqldelight.android.driver)
        }

        iosMain.dependencies {
            implementation(libs.sqldelight.native.driver)
        }
    }
}
```

#### Schema Definition (.sq files)

```sql
-- commonMain/sqldelight/com/example/db/User.sq

CREATE TABLE User (
    id TEXT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

-- Named queries generate Kotlin functions
selectAll:
SELECT * FROM User ORDER BY name;

selectById:
SELECT * FROM User WHERE id = ?;

selectByEmail:
SELECT * FROM User WHERE email = ?;

insert:
INSERT INTO User (id, name, email, created_at, updated_at)
VALUES (?, ?, ?, ?, ?);

update:
UPDATE User SET name = ?, email = ?, updated_at = ? WHERE id = ?;

delete:
DELETE FROM User WHERE id = ?;

-- Queries with Flow support
selectAllAsFlow:
SELECT * FROM User ORDER BY name;
```

#### Driver Creation

```kotlin
// commonMain
expect class DatabaseDriverFactory {
    fun createDriver(): SqlDriver
}

class DatabaseHelper(driverFactory: DatabaseDriverFactory) {
    private val driver = driverFactory.createDriver()
    val database = AppDatabase(driver)

    val userQueries = database.userQueries
}

// androidMain
actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(
            schema = AppDatabase.Schema,
            context = context,
            name = "app.db"
        )
    }
}

// iosMain
actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = AppDatabase.Schema,
            name = "app.db"
        )
    }
}
```

#### Repository Implementation

```kotlin
// commonMain
class UserRepository(private val db: DatabaseHelper) {

    private val queries = db.userQueries

    fun getAllUsers(): Flow<List<User>> {
        return queries.selectAll()
            .asFlow()
            .mapToList(Dispatchers.IO)
    }

    suspend fun getUserById(id: String): User? {
        return withContext(Dispatchers.IO) {
            queries.selectById(id).executeAsOneOrNull()
        }
    }

    suspend fun insertUser(user: User) {
        withContext(Dispatchers.IO) {
            queries.insert(
                id = user.id,
                name = user.name,
                email = user.email,
                created_at = user.createdAt,
                updated_at = user.updatedAt
            )
        }
    }

    suspend fun updateUser(user: User) {
        withContext(Dispatchers.IO) {
            queries.update(
                name = user.name,
                email = user.email,
                updated_at = Clock.System.now().toEpochMilliseconds(),
                id = user.id
            )
        }
    }

    suspend fun deleteUser(id: String) {
        withContext(Dispatchers.IO) {
            queries.delete(id)
        }
    }

    // Transaction support
    suspend fun replaceAllUsers(users: List<User>) {
        withContext(Dispatchers.IO) {
            db.database.transaction {
                queries.deleteAll()
                users.forEach { user ->
                    queries.insert(
                        id = user.id,
                        name = user.name,
                        email = user.email,
                        created_at = user.createdAt,
                        updated_at = user.updatedAt
                    )
                }
            }
        }
    }
}
```

### DataStore - Key-Value Storage

DataStore provides a modern replacement for SharedPreferences with full Kotlin and coroutines support.

#### Setup

```kotlin
// build.gradle.kts (shared module)
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.androidx.datastore.preferences.core)
        }
    }
}

// libs.versions.toml
[versions]
datastore = "1.1.0"

[libraries]
androidx-datastore-preferences-core = { module = "androidx.datastore:datastore-preferences-core", version.ref = "datastore" }
```

#### DataStore Implementation

```kotlin
// commonMain
expect fun createDataStore(context: Any?): DataStore<Preferences>

object PreferencesKeys {
    val USER_TOKEN = stringPreferencesKey("user_token")
    val USER_ID = stringPreferencesKey("user_id")
    val IS_ONBOARDED = booleanPreferencesKey("is_onboarded")
    val THEME_MODE = stringPreferencesKey("theme_mode")
    val LAST_SYNC = longPreferencesKey("last_sync")
}

class SettingsRepository(private val dataStore: DataStore<Preferences>) {

    val userToken: Flow<String?> = dataStore.data
        .map { preferences -> preferences[PreferencesKeys.USER_TOKEN] }

    val isOnboarded: Flow<Boolean> = dataStore.data
        .map { preferences -> preferences[PreferencesKeys.IS_ONBOARDED] ?: false }

    val themeMode: Flow<ThemeMode> = dataStore.data
        .map { preferences ->
            val value = preferences[PreferencesKeys.THEME_MODE]
            ThemeMode.entries.find { it.name == value } ?: ThemeMode.SYSTEM
        }

    suspend fun setUserToken(token: String?) {
        dataStore.edit { preferences ->
            if (token != null) {
                preferences[PreferencesKeys.USER_TOKEN] = token
            } else {
                preferences.remove(PreferencesKeys.USER_TOKEN)
            }
        }
    }

    suspend fun setOnboarded(completed: Boolean) {
        dataStore.edit { preferences ->
            preferences[PreferencesKeys.IS_ONBOARDED] = completed
        }
    }

    suspend fun setThemeMode(mode: ThemeMode) {
        dataStore.edit { preferences ->
            preferences[PreferencesKeys.THEME_MODE] = mode.name
        }
    }

    suspend fun clearAll() {
        dataStore.edit { it.clear() }
    }
}

enum class ThemeMode { LIGHT, DARK, SYSTEM }

// androidMain
actual fun createDataStore(context: Any?): DataStore<Preferences> {
    require(context is Context)
    return PreferenceDataStoreFactory.createWithPath(
        produceFile = { context.filesDir.resolve("settings.preferences_pb").absolutePath.toPath() }
    )
}

// iosMain
actual fun createDataStore(context: Any?): DataStore<Preferences> {
    return PreferenceDataStoreFactory.createWithPath(
        produceFile = {
            val documentDirectory = NSFileManager.defaultManager.URLForDirectory(
                directory = NSDocumentDirectory,
                inDomain = NSUserDomainMask,
                appropriateForURL = null,
                create = false,
                error = null
            )!!
            "${documentDirectory.path}/settings.preferences_pb".toPath()
        }
    )
}
```

### Room-style Approach with SQLDelight

```kotlin
// Complex queries and relationships
-- commonMain/sqldelight/com/example/db/Post.sq

CREATE TABLE Post (
    id TEXT NOT NULL PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE INDEX post_user_idx ON Post(user_id);

-- Join query
selectPostsWithAuthors:
SELECT
    Post.*,
    User.name AS author_name,
    User.email AS author_email
FROM Post
INNER JOIN User ON Post.user_id = User.id
ORDER BY Post.created_at DESC;

-- Aggregation
countPostsByUser:
SELECT user_id, COUNT(*) AS post_count
FROM Post
GROUP BY user_id;
```

### Migration Support

```kotlin
// build.gradle.kts
sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.db")
            // Migrations are automatic from .sqm files
            deriveSchemaFromMigrations.set(true)
        }
    }
}

// 1.sqm - First migration
ALTER TABLE User ADD COLUMN avatar_url TEXT;

// 2.sqm - Second migration
CREATE TABLE IF NOT EXISTS Settings (
    key TEXT NOT NULL PRIMARY KEY,
    value TEXT NOT NULL
);
```

### Choosing Between SQLDelight and DataStore

| Use Case | SQLDelight | DataStore |
|----------|------------|-----------|
| **Structured data** | Yes | No |
| **Complex queries** | Yes | No |
| **Relationships** | Yes | No |
| **Simple key-value** | Overkill | Yes |
| **User preferences** | Overkill | Yes |
| **Large datasets** | Yes | No |
| **Type safety** | Strong (SQL) | Strong (Keys) |

### Best Practices

1. **Use SQLDelight for domain data** - entities, relationships, complex queries
2. **Use DataStore for settings** - preferences, feature flags, simple state
3. **Generate async queries** - for coroutines integration
4. **Implement proper migrations** - version your schema changes
5. **Use transactions** - for batch operations
6. **Flow for reactivity** - observe database changes

---

## Otvet (RU)

Kotlin Multiplatform предлагает несколько вариантов для общего хранения данных. Два наиболее популярных - **SQLDelight** для структурированных реляционных данных и **DataStore** для key-value настроек.

### SQLDelight - Реляционная база данных

SQLDelight генерирует типобезопасные Kotlin API из SQL выражений. Работает с SQLite на Android и iOS.

#### Настройка

```kotlin
// build.gradle.kts (shared модуль)
plugins {
    kotlin("multiplatform")
    id("app.cash.sqldelight") version "2.0.0"
}

sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.db")
            generateAsync.set(true)
        }
    }
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.sqldelight.runtime)
            implementation(libs.sqldelight.coroutines)
        }

        androidMain.dependencies {
            implementation(libs.sqldelight.android.driver)
        }

        iosMain.dependencies {
            implementation(libs.sqldelight.native.driver)
        }
    }
}
```

#### Определение схемы (.sq файлы)

```sql
-- commonMain/sqldelight/com/example/db/User.sq

CREATE TABLE User (
    id TEXT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

-- Именованные запросы генерируют Kotlin функции
selectAll:
SELECT * FROM User ORDER BY name;

selectById:
SELECT * FROM User WHERE id = ?;

insert:
INSERT INTO User (id, name, email, created_at, updated_at)
VALUES (?, ?, ?, ?, ?);

update:
UPDATE User SET name = ?, email = ?, updated_at = ? WHERE id = ?;

delete:
DELETE FROM User WHERE id = ?;
```

#### Создание драйвера

```kotlin
// commonMain
expect class DatabaseDriverFactory {
    fun createDriver(): SqlDriver
}

class DatabaseHelper(driverFactory: DatabaseDriverFactory) {
    private val driver = driverFactory.createDriver()
    val database = AppDatabase(driver)
    val userQueries = database.userQueries
}

// androidMain
actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(
            schema = AppDatabase.Schema,
            context = context,
            name = "app.db"
        )
    }
}

// iosMain
actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = AppDatabase.Schema,
            name = "app.db"
        )
    }
}
```

#### Реализация репозитория

```kotlin
// commonMain
class UserRepository(private val db: DatabaseHelper) {

    private val queries = db.userQueries

    fun getAllUsers(): Flow<List<User>> {
        return queries.selectAll()
            .asFlow()
            .mapToList(Dispatchers.IO)
    }

    suspend fun getUserById(id: String): User? {
        return withContext(Dispatchers.IO) {
            queries.selectById(id).executeAsOneOrNull()
        }
    }

    suspend fun insertUser(user: User) {
        withContext(Dispatchers.IO) {
            queries.insert(
                id = user.id,
                name = user.name,
                email = user.email,
                created_at = user.createdAt,
                updated_at = user.updatedAt
            )
        }
    }

    // Поддержка транзакций
    suspend fun replaceAllUsers(users: List<User>) {
        withContext(Dispatchers.IO) {
            db.database.transaction {
                queries.deleteAll()
                users.forEach { user ->
                    queries.insert(/* ... */)
                }
            }
        }
    }
}
```

### DataStore - Key-Value хранилище

DataStore предоставляет современную замену SharedPreferences с полной поддержкой Kotlin и корутин.

#### Реализация DataStore

```kotlin
// commonMain
expect fun createDataStore(context: Any?): DataStore<Preferences>

object PreferencesKeys {
    val USER_TOKEN = stringPreferencesKey("user_token")
    val IS_ONBOARDED = booleanPreferencesKey("is_onboarded")
    val THEME_MODE = stringPreferencesKey("theme_mode")
}

class SettingsRepository(private val dataStore: DataStore<Preferences>) {

    val userToken: Flow<String?> = dataStore.data
        .map { preferences -> preferences[PreferencesKeys.USER_TOKEN] }

    val isOnboarded: Flow<Boolean> = dataStore.data
        .map { preferences -> preferences[PreferencesKeys.IS_ONBOARDED] ?: false }

    suspend fun setUserToken(token: String?) {
        dataStore.edit { preferences ->
            if (token != null) {
                preferences[PreferencesKeys.USER_TOKEN] = token
            } else {
                preferences.remove(PreferencesKeys.USER_TOKEN)
            }
        }
    }

    suspend fun setOnboarded(completed: Boolean) {
        dataStore.edit { preferences ->
            preferences[PreferencesKeys.IS_ONBOARDED] = completed
        }
    }
}
```

### Выбор между SQLDelight и DataStore

| Случай использования | SQLDelight | DataStore |
|---------------------|------------|-----------|
| **Структурированные данные** | Да | Нет |
| **Сложные запросы** | Да | Нет |
| **Связи между таблицами** | Да | Нет |
| **Простые key-value** | Избыточно | Да |
| **Пользовательские настройки** | Избыточно | Да |
| **Большие наборы данных** | Да | Нет |

### Лучшие практики

1. **Используйте SQLDelight для доменных данных** - сущности, связи, сложные запросы
2. **Используйте DataStore для настроек** - предпочтения, feature flags, простое состояние
3. **Генерируйте async запросы** - для интеграции с корутинами
4. **Реализуйте правильные миграции** - версионируйте изменения схемы
5. **Используйте транзакции** - для пакетных операций
6. **Flow для реактивности** - наблюдайте за изменениями в базе

---

## Follow-ups

- How do you handle database migrations in SQLDelight?
- What is the performance comparison between SQLDelight and Room?
- How do you implement database encryption in KMP?
- How do you test database code in KMP?

## Dopolnitelnye Voprosy (RU)

- Как обрабатывать миграции базы данных в SQLDelight?
- Как сравнивается производительность SQLDelight и Room?
- Как реализовать шифрование базы данных в KMP?
- Как тестировать код базы данных в KMP?

## References

- [SQLDelight Documentation](https://cashapp.github.io/sqldelight/)
- [DataStore Documentation](https://developer.android.com/topic/libraries/architecture/datastore)

## Ssylki (RU)

- [[c-kotlin]]
- [Документация SQLDelight](https://cashapp.github.io/sqldelight/)

## Related Questions

- [[q-kmp-networking--kmp--medium]]
- [[q-kmp-architecture--kmp--hard]]
