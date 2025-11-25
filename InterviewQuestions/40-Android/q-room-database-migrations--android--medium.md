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
related: [c-android-components, q-room-transactions-dao--android--medium, q-room-type-converters-advanced--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/room, android/testing-instrumented, difficulty/medium]
date created: Saturday, November 1st 2025, 12:47:02 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---

# Вопрос (RU)

> Реализуйте сложные миграции базы данных Room с версии 1 до 3. Обработайте деструктивные и недеструктивные миграции с тестированием.

# Question (EN)

> Implement complex Room database migrations from version 1 to 3. Handle destructive and non-destructive migrations with testing.

## Ответ (RU)

**Миграции Room** — SQL-скрипты и программная логика для обновления схемы БД без потери пользовательских данных. Критично для production-приложений для предотвращения потери данных и крашей.

### Основные Принципы

При изменении схемы:
1. Увеличиваем версию БД
2. Предоставляем путь миграции (инкрементальный или объединённый)
3. Тестируем миграции
4. Обрабатываем fallback-стратегии

### Пример Эволюции Схемы

```kotlin
// v1: Начальная схема
@Entity(tableName = "users")
data class UserV1(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String
)

// v2: Добавляем phoneNumber (nullable) и createdAt (NOT NULL)
@Entity(tableName = "users")
data class UserV2(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String,
    val phoneNumber: String?,
    val createdAt: Long // предполагаем NOT NULL
)

// v3: Разделяем name → firstName + lastName, удаляем name
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Long,
    val firstName: String,
    val lastName: String,
    val email: String,
    val phoneNumber: String?,
    val createdAt: Long
)
```

(Типы и поля показаны для иллюстрации. В реальном коде используйте актуальную entity для финальной версии схемы.)

### Реализация Миграций

#### Миграция 1→2: Добавление Колонок

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // ✅ Nullable колонка не требует DEFAULT
        db.execSQL("ALTER TABLE users ADD COLUMN phoneNumber TEXT")

        // ✅ NOT NULL требует DEFAULT значение на момент добавления,
        // чтобы не нарушить constraint для уже существующих строк
        db.execSQL(
            "ALTER TABLE users ADD COLUMN createdAt INTEGER NOT NULL DEFAULT 0"
        )
    }
}
```

#### Миграция 2→3: Сложное Изменение (пересоздание таблицы)

SQLite не поддерживает изменение существующих колонок (ALTER COLUMN), поэтому при изменении структуры часто нужно пересоздать таблицу.

Важно: нижеупрощённый пример предполагает, что поле `name` всегда содержит ровно два токена: "First Last". В реальном приложении логику разбора ФИО нужно сделать более надёжной (обработка отсутствия пробела, нескольких слов, локали и т.д.).

```kotlin
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // 1. Новая таблица с обновлённой схемой
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS users_new (
                id INTEGER PRIMARY KEY NOT NULL,
                firstName TEXT NOT NULL,
                lastName TEXT NOT NULL,
                email TEXT NOT NULL,
                phoneNumber TEXT,
                createdAt INTEGER NOT NULL
            )
            """.trimIndent()
        )

        // 2. Копируем данные с простой трансформацией name → firstName/lastName
        db.execSQL(
            """
            INSERT INTO users_new (id, firstName, lastName, email, phoneNumber, createdAt)
            SELECT id,
                   substr(name, 1, instr(name, ' ') - 1) AS firstName,
                   substr(name, instr(name, ' ') + 1) AS lastName,
                   email,
                   phoneNumber,
                   createdAt
            FROM users
            WHERE instr(name, ' ') > 0
            """.trimIndent()
        )

        // (опционально: обработать записи без пробела в name отдельно)

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
    exportSchema = true  // ✅ Рекомендуется для snapshot'ов схемы и тестирования
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun build(context: Context): AppDatabase = Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app.db"
        )
            .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
            // ❌ В production избегайте глобального fallbackToDestructiveMigration,
            // используйте его только осознанно (например, в debug сборках)
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
        AppDatabase::class.java.canonicalName,
        FrameworkSQLiteOpenHelperFactory()
    )

    @Test
    fun migrate1To2_preservesData() {
        // Создаём БД v1 (схема соответствует версии 1)
        helper.createDatabase("test.db", 1).apply {
            execSQL("INSERT INTO users (id, name, email) VALUES (1, 'John Doe', 'j@ex.com')")
            close()
        }

        // Мигрируем на v2 и валидируем схему через exportSchema
        helper.runMigrationsAndValidate(
            "test.db",
            2,
            true,
            MIGRATION_1_2
        )
    }

    @Test
    fun migrate1To3_throughAllVersions() {
        helper.createDatabase("test.db", 1).apply {
            execSQL("INSERT INTO users (id, name, email) VALUES (1, 'Jane Smith', 'jane@ex.com')")
            close()
        }

        // ✅ Миграция проходит через все промежуточные версии (1→2→3)
        helper.runMigrationsAndValidate(
            "test.db",
            3,
            true,
            MIGRATION_1_2,
            MIGRATION_2_3
        )
    }
}
```

(Для детальной проверки содержимого можно открывать SupportSQLiteDatabase, возвращаемый `createDatabase` или `runMigrationsAndValidate`, и выполнять выборки с использованием `getColumnIndexOrThrow`.)

### Деструктивные Миграции

```kotlin
// ❌ Удаляет все данные при изменении версии, если нет подходящих миграций.
// Использовать только осознанно (например, в debug или при допустимой потере данных).
Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .fallbackToDestructiveMigration()
    .build()

// Деструктивная миграция только для конкретных старых версий:
// при апгрейде с любой из указанных версий (1 или 2) данные будут очищены,
// для остальных версий применяются обычные миграции.
Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .fallbackToDestructiveMigrationFrom(1, 2)
    .addMigrations(MIGRATION_3_4)
    .build()
```

### Best Practices

1. **exportSchema = true** — ведите историю схемы для валидации миграций.
2. **Тестировать миграции** — покрывайте каждый реальный путь (например, 1→2→3).
3. **Инкрементальные миграции** — определяйте отдельную Migration для каждой пары версий; Room сам свяжет цепочку.
4. **Избегать деструктивных миграций в production** — по возможности всегда сохраняйте данные.
5. **NULL → NOT NULL** — изменение существующего столбца обычно требует пересоздания таблицы; добавление нового NOT NULL-столбца допустимо с корректным DEFAULT.
6. **Трансформация данных** — делайте её явно: через SQL (INSERT SELECT) или временные таблицы/колонки, учитывая edge cases.

## Answer (EN)

**Room Migrations** are SQL and code-based transformations to update the database schema while preserving user data. They are critical for production apps to avoid data loss and crashes.

### Core Principles

When changing schema:
1. Increment the database version.
2. Provide a migration path (incremental or composed).
3. Test migrations thoroughly.
4. Handle fallback strategies explicitly.

### Schema Evolution Example

```kotlin
// v1: Initial schema
@Entity(tableName = "users")
data class UserV1(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String
)

// v2: Add phoneNumber (nullable) and createdAt (NOT NULL)
@Entity(tableName = "users")
data class UserV2(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String,
    val phoneNumber: String?,
    val createdAt: Long
)

// v3: Split name → firstName + lastName, remove name
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Long,
    val firstName: String,
    val lastName: String,
    val email: String,
    val phoneNumber: String?,
    val createdAt: Long
)
```

(Types/entities are illustrative; in real code define only the latest entity version matching `version = 3`.)

### Implementing Migrations

#### Migration 1→2: Adding Columns

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // ✅ Nullable column doesn't require DEFAULT
        db.execSQL("ALTER TABLE users ADD COLUMN phoneNumber TEXT")

        // ✅ NOT NULL requires a DEFAULT at the time of adding the column
        // so existing rows satisfy the constraint
        db.execSQL(
            "ALTER TABLE users ADD COLUMN createdAt INTEGER NOT NULL DEFAULT 0"
        )
    }
}
```

#### Migration 2→3: Complex Change (Table Recreation)

SQLite does not support altering existing column types/constraints directly, so complex changes typically require table recreation.

Note: the following is a simplified example assuming `name` is always "First Last". Real-world apps must handle missing spaces, multiple words, locale-specific names, etc.

```kotlin
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // 1. New table with updated schema
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS users_new (
                id INTEGER PRIMARY KEY NOT NULL,
                firstName TEXT NOT NULL,
                lastName TEXT NOT NULL,
                email TEXT NOT NULL,
                phoneNumber TEXT,
                createdAt INTEGER NOT NULL
            )
            """.trimIndent()
        )

        // 2. Copy data with simple name → firstName/lastName transformation
        db.execSQL(
            """
            INSERT INTO users_new (id, firstName, lastName, email, phoneNumber, createdAt)
            SELECT id,
                   substr(name, 1, instr(name, ' ') - 1) AS firstName,
                   substr(name, instr(name, ' ') + 1) AS lastName,
                   email,
                   phoneNumber,
                   createdAt
            FROM users
            WHERE instr(name, ' ') > 0
            """.trimIndent()
        )

        // (optionally handle rows without a space in `name` separately)

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
    exportSchema = true  // ✅ Recommended for schema snapshots and migration tests
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun build(context: Context): AppDatabase = Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app.db"
        )
            .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
            // ❌ Do not enable global destructive fallback in production by default.
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
        AppDatabase::class.java.canonicalName,
        FrameworkSQLiteOpenHelperFactory()
    )

    @Test
    fun migrate1To2_preservesData() {
        // Create DB v1
        helper.createDatabase("test.db", 1).apply {
            execSQL("INSERT INTO users (id, name, email) VALUES (1, 'John Doe', 'j@ex.com')")
            close()
        }

        // Migrate to v2 and validate against schema
        helper.runMigrationsAndValidate(
            "test.db",
            2,
            true,
            MIGRATION_1_2
        )
    }

    @Test
    fun migrate1To3_throughAllVersions() {
        helper.createDatabase("test.db", 1).apply {
            execSQL("INSERT INTO users (id, name, email) VALUES (1, 'Jane Smith', 'jane@ex.com')")
            close()
        }

        // ✅ Migrate through all intermediate versions (1→2→3)
        helper.runMigrationsAndValidate(
            "test.db",
            3,
            true,
            MIGRATION_1_2,
            MIGRATION_2_3
        )
    }
}
```

(For content assertions, inspect the `SupportSQLiteDatabase` returned from `createDatabase`/`runMigrationsAndValidate` and query using `getColumnIndexOrThrow`.)

### Destructive Migrations

```kotlin
// ❌ Wipes all data on version change when no matching migrations exist.
// Use only intentionally (e.g., debug builds or when data loss is acceptable).
Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .fallbackToDestructiveMigration()
    .build()

// Destructive migration only from specific versions:
// when upgrading from any of the specified versions (1 or 2), data is wiped;
// from other versions, normal migrations (e.g., 3→4) are applied.
Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .fallbackToDestructiveMigrationFrom(1, 2)
    .addMigrations(MIGRATION_3_4)
    .build()
```

### Best Practices

1. **exportSchema = true** — keep schema history JSON for validating migrations.
2. **Test migrations** — cover each realistic upgrade path (e.g., 1→2, 2→3, 1→3 via chain).
3. **Incremental migrations** — define `Migration` for each version step; Room composes them.
4. **Avoid destructive strategies in production** — prefer preserving and transforming data.
5. **NULL → NOT NULL** — changing an existing column usually requires table recreation; adding a new NOT NULL column is valid with an appropriate DEFAULT.
6. **Data transformation** — do it explicitly via SQL or temporary tables/columns and handle edge cases.

## Follow-ups

1. How do you handle migration failures in production and ensure safe rollbacks?
2. What is the difference between `fallbackToDestructiveMigration()` and `fallbackToDestructiveMigrationFrom()` and when would you use each?
3. How can you design migrations to support cross-module or multi-process architectures?
4. How would you implement and test data migrations that include complex transformations (e.g., denormalization or splitting tables)?
5. How do you ensure backward compatibility or safe downgrades when schema version decreases?

## References

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
