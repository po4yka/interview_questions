---
id: android-230
title: "Room Database Migrations / Миграции базы данных Room"
aliases: ["Room Database Migrations", "Миграции базы данных Room"]
topic: android
subtopics: [room, testing-instrumented]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-room, q-room-transactions-dao--android--medium, q-room-type-converters-advanced--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/room, android/testing-instrumented, database, difficulty/medium, migrations, persistence]
date created: Saturday, November 1st 2025, 12:47:02 pm
date modified: Saturday, November 1st 2025, 5:43:29 pm
---

# Вопрос (RU)

Реализуйте сложные миграции базы данных Room с версии 1 до 3. Обработайте деструктивные и недеструктивные миграции с тестированием.

# Question (EN)

Implement complex Room database migrations from version 1 to 3. Handle destructive and non-destructive migrations with testing.

## Ответ (RU)

**Миграции Room** — SQL-скрипты для обновления схемы БД с сохранением пользовательских данных. Критично для production приложений для предотвращения потери данных и крашей. См. [[c-room|Room Database]] для основ работы с Room.

### Основные Принципы

При изменении схемы:
1. Увеличиваем версию БД
2. Предоставляем путь миграции
3. Тестируем миграции
4. Обрабатываем fallback-стратегии

### Пример Эволюции Схемы

```kotlin
// v1: Начальная схема
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String
)

// v2: Добавляем phoneNumber (nullable) и createdAt (NOT NULL)
// v3: Разделяем name → firstName + lastName
```

### Реализация Миграций

#### Миграция 1→2: Добавление Колонок

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // ✅ Nullable колонка не требует DEFAULT
        db.execSQL("ALTER TABLE users ADD COLUMN phoneNumber TEXT")

        // ✅ NOT NULL требует DEFAULT значение
        db.execSQL(
            "ALTER TABLE users ADD COLUMN createdAt INTEGER NOT NULL DEFAULT 0"
        )
    }
}
```

#### Миграция 2→3: Сложное Изменение (пересоздание таблицы)

SQLite не поддерживает ALTER COLUMN — нужно пересоздать таблицу:

```kotlin
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // 1. Новая таблица с обновлённой схемой
        db.execSQL("""
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY NOT NULL,
                firstName TEXT NOT NULL,
                lastName TEXT NOT NULL,
                email TEXT NOT NULL,
                phoneNumber TEXT
            )
        """)

        // 2. Копируем данные с трансформацией
        db.execSQL("""
            INSERT INTO users_new (id, firstName, lastName, email, phoneNumber)
            SELECT id,
                   substr(name, 1, instr(name, ' ')-1) as firstName,  -- ✅ Разделение name
                   substr(name, instr(name, ' ')+1) as lastName,
                   email, phoneNumber
            FROM users
        """)

        // 3. Меняем таблицы
        db.execSQL("DROP TABLE users")
        db.execSQL("ALTER TABLE users_new RENAME TO users")
    }
}
```

### Настройка БД С Миграциями

```kotlin
@Database(
    entities = [User::class],
    version = 3,
    exportSchema = true  // ✅ Обязательно для тестирования
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun build(context: Context) = Room.databaseBuilder(
            context, AppDatabase::class.java, "app.db"
        )
            .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
            .fallbackToDestructiveMigration()  // ❌ Только для debug
            .build()
    }
}
```

### Тестирование Миграций

```kotlin
@RunWith(AndroidJUnit4::class)
class MigrationTest {
    @get:Rule
    val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test
    fun migrate1To2_preservesData() {
        // Создаём БД v1
        helper.createDatabase("test.db", 1).apply {
            execSQL("INSERT INTO users (id, name, email) VALUES (1, 'John Doe', 'j@ex.com')")
            close()
        }

        // Мигрируем на v2
        helper.runMigrationsAndValidate("test.db", 2, true, MIGRATION_1_2)

        // ✅ Проверяем сохранность данных
        helper.openDatabase("test.db").use { db ->
            val cursor = db.query("SELECT * FROM users WHERE id = 1")
            assertTrue(cursor.moveToFirst())
            assertEquals("John Doe", cursor.getString(cursor.getColumnIndex("name")))
            assertTrue(cursor.getColumnIndex("phoneNumber") >= 0)  // новая колонка
        }
    }

    @Test
    fun migrate1To3_throughAllVersions() {
        helper.createDatabase("test.db", 1).apply {
            execSQL("INSERT INTO users (id, name, email) VALUES (1, 'Jane Smith', 'jane@ex.com')")
            close()
        }

        // ✅ Мигрируем через все версии
        helper.runMigrationsAndValidate("test.db", 3, true, MIGRATION_1_2, MIGRATION_2_3)

        helper.openDatabase("test.db").use { db ->
            val cursor = db.query("SELECT * FROM users WHERE id = 1")
            assertTrue(cursor.moveToFirst())
            assertEquals("Jane", cursor.getString(cursor.getColumnIndex("firstName")))
            assertEquals("Smith", cursor.getString(cursor.getColumnIndex("lastName")))
        }
    }
}
```

### Деструктивные Миграции

```kotlin
// ❌ Удаляет все данные при изменении версии — ТОЛЬКО для debug
Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .fallbackToDestructiveMigration()
    .build()

// Деструктивная миграция только для конкретных версий
Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .fallbackToDestructiveMigrationFrom(1, 2)  // v1,v2 → wipe
    .addMigrations(MIGRATION_3_4)  // v3→4 → safe
    .build()
```

### Best Practices

1. **exportSchema = true** — версионирование схем для тестов
2. **Тестировать миграции** — каждый путь миграции
3. **Инкрементальные миграции** — путь для каждой версии (1→2, 2→3, не 1→3)
4. **Избегать деструктивных** — в production всегда сохранять данные
5. **NULL → NOT NULL** — требует пересоздания таблицы
6. **Трансформация данных** — в SQL или через temporary columns

## Answer (EN)

**Room Migrations** are SQL scripts to update database schema while preserving user data. Critical for production apps to prevent data loss and crashes. See [[c-room|Room Database]] for Room basics.

### Core Principles

When changing schema:
1. Increment database version
2. Provide migration path
3. Test migrations thoroughly
4. Handle fallback strategies

### Schema Evolution Example

```kotlin
// v1: Initial schema
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String
)

// v2: Add phoneNumber (nullable) and createdAt (NOT NULL)
// v3: Split name → firstName + lastName
```

### Implementing Migrations

#### Migration 1→2: Adding Columns

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // ✅ Nullable column doesn't require DEFAULT
        db.execSQL("ALTER TABLE users ADD COLUMN phoneNumber TEXT")

        // ✅ NOT NULL requires DEFAULT value
        db.execSQL(
            "ALTER TABLE users ADD COLUMN createdAt INTEGER NOT NULL DEFAULT 0"
        )
    }
}
```

#### Migration 2→3: Complex Change (Table Recreation)

SQLite doesn't support ALTER COLUMN — need to recreate table:

```kotlin
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // 1. New table with updated schema
        db.execSQL("""
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY NOT NULL,
                firstName TEXT NOT NULL,
                lastName TEXT NOT NULL,
                email TEXT NOT NULL,
                phoneNumber TEXT
            )
        """)

        // 2. Copy data with transformation
        db.execSQL("""
            INSERT INTO users_new (id, firstName, lastName, email, phoneNumber)
            SELECT id,
                   substr(name, 1, instr(name, ' ')-1) as firstName,  -- ✅ Split name
                   substr(name, instr(name, ' ')+1) as lastName,
                   email, phoneNumber
            FROM users
        """)

        // 3. Swap tables
        db.execSQL("DROP TABLE users")
        db.execSQL("ALTER TABLE users_new RENAME TO users")
    }
}
```

### Database Setup with Migrations

```kotlin
@Database(
    entities = [User::class],
    version = 3,
    exportSchema = true  // ✅ Required for testing
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun build(context: Context) = Room.databaseBuilder(
            context, AppDatabase::class.java, "app.db"
        )
            .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
            .fallbackToDestructiveMigration()  // ❌ Debug only
            .build()
    }
}
```

### Testing Migrations

```kotlin
@RunWith(AndroidJUnit4::class)
class MigrationTest {
    @get:Rule
    val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test
    fun migrate1To2_preservesData() {
        // Create DB v1
        helper.createDatabase("test.db", 1).apply {
            execSQL("INSERT INTO users (id, name, email) VALUES (1, 'John Doe', 'j@ex.com')")
            close()
        }

        // Migrate to v2
        helper.runMigrationsAndValidate("test.db", 2, true, MIGRATION_1_2)

        // ✅ Verify data preserved
        helper.openDatabase("test.db").use { db ->
            val cursor = db.query("SELECT * FROM users WHERE id = 1")
            assertTrue(cursor.moveToFirst())
            assertEquals("John Doe", cursor.getString(cursor.getColumnIndex("name")))
            assertTrue(cursor.getColumnIndex("phoneNumber") >= 0)  // new column
        }
    }

    @Test
    fun migrate1To3_throughAllVersions() {
        helper.createDatabase("test.db", 1).apply {
            execSQL("INSERT INTO users (id, name, email) VALUES (1, 'Jane Smith', 'jane@ex.com')")
            close()
        }

        // ✅ Migrate through all versions
        helper.runMigrationsAndValidate("test.db", 3, true, MIGRATION_1_2, MIGRATION_2_3)

        helper.openDatabase("test.db").use { db ->
            val cursor = db.query("SELECT * FROM users WHERE id = 1")
            assertTrue(cursor.moveToFirst())
            assertEquals("Jane", cursor.getString(cursor.getColumnIndex("firstName")))
            assertEquals("Smith", cursor.getString(cursor.getColumnIndex("lastName")))
        }
    }
}
```

### Destructive Migrations

```kotlin
// ❌ Wipes all data on version change — DEBUG ONLY
Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .fallbackToDestructiveMigration()
    .build()

// Destructive migration only for specific versions
Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .fallbackToDestructiveMigrationFrom(1, 2)  // v1,v2 → wipe
    .addMigrations(MIGRATION_3_4)  // v3→4 → safe
    .build()
```

### Best Practices

1. **exportSchema = true** — version tracking for tests
2. **Test migrations** — every migration path
3. **Incremental migrations** — path for each version (1→2, 2→3, not 1→3)
4. **Avoid destructive** — in production, always preserve data
5. **NULL → NOT NULL** — requires table recreation
6. **Data transformation** — in SQL or via temporary columns

## Follow-ups

1. How do you handle migration failures in production?
2. What's the difference between `fallbackToDestructiveMigration()` and `fallbackToDestructiveMigrationOnDowngrade()`?
3. How to migrate data from one table to another (e.g., splitting Users into Users + Profiles)?
4. Can you skip a migration version (e.g., migrate directly from v1 to v3)?
5. How to test migrations with large datasets (performance)?

## References

- [[c-room|Room Database]]
- https://developer.android.com/training/data-storage/room/migrating-db-versions
- https://developer.android.com/reference/androidx/room/migration/Migration
- https://developer.android.com/training/data-storage/room/testing-db

## Related Questions

### Prerequisites (Easier)
- [[q-room-library-definition--android--easy|Room Library Basics]]
- [[q-sharedpreferences-commit-vs-apply--android--easy|SharedPreferences vs Room]]

### Related (Medium)
- [[q-room-transactions-dao--android--medium|Room Transactions]]
- [[q-room-type-converters-advanced--android--medium|Room Type Converters]]
- [[q-room-paging3-integration--android--medium|Room Paging3 Integration]]

### Advanced (Harder)
- [[q-room-fts-full-text-search--android--hard|Room Full-Text Search]]
- Database schema versioning across multi-module projects
- Zero-downtime migrations for large databases
