---
id: "20251015082237550"
title: "Room Database Migrations / Миграции базы данных Room"
topic: room
difficulty: medium
status: draft
created: 2025-10-15
tags: - room
  - database
  - migrations
  - persistence
  - testing
  - difficulty/medium
---
# Room Database Migrations / Миграции базы данных Room

**English**: Implement complex Room database migrations from version 1 to 3. Handle destructive and non-destructive migrations with testing.

## Answer (EN)
**Room Migrations** are SQL scripts that help you update your database schema while preserving existing user data. Proper migration strategy is critical for production apps to prevent data loss and crashes.

### Migration Basics

When you change your database schema (add/remove tables, modify columns), you must:
1. Increment database version
2. Provide migration path from old version to new
3. Test migrations thoroughly
4. Handle fallback strategies

### Schema Evolution Example

**Version 1 → Version 2 → Version 3**

```kotlin
// Version 1: Initial schema
@Entity(tableName = "users")
data class UserV1(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String
)

// Version 2: Add phone number and created_at
@Entity(tableName = "users")
data class UserV2(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String,
    val phoneNumber: String?,  // New column
    val createdAt: Long        // New column with default
)

// Version 3: Split name into firstName and lastName, add index
@Entity(
    tableName = "users",
    indices = [Index(value = ["email"], unique = true)]
)
data class UserV3(
    @PrimaryKey val id: Long,
    val firstName: String,     // Split from name
    val lastName: String,      // Split from name
    val email: String,
    val phoneNumber: String?,
    val createdAt: Long,
    val updatedAt: Long = System.currentTimeMillis()  // New column
)
```

### Implementing Migrations

#### Migration 1 → 2: Adding Columns

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Add phoneNumber column (nullable)
        database.execSQL(
            """
            ALTER TABLE users
            ADD COLUMN phoneNumber TEXT
            """.trimIndent()
        )

        // Add createdAt column with default value
        database.execSQL(
            """
            ALTER TABLE users
            ADD COLUMN createdAt INTEGER NOT NULL DEFAULT ${System.currentTimeMillis()}
            """.trimIndent()
        )
    }
}
```

#### Migration 2 → 3: Complex Schema Change

```kotlin
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Step 1: Create new table with updated schema
        database.execSQL(
            """
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY NOT NULL,
                firstName TEXT NOT NULL,
                lastName TEXT NOT NULL,
                email TEXT NOT NULL,
                phoneNumber TEXT,
                createdAt INTEGER NOT NULL,
                updatedAt INTEGER NOT NULL DEFAULT ${System.currentTimeMillis()}
            )
            """.trimIndent()
        )

        // Step 2: Copy data from old table, splitting name
        database.execSQL(
            """
            INSERT INTO users_new (id, firstName, lastName, email, phoneNumber, createdAt, updatedAt)
            SELECT
                id,
                CASE
                    WHEN instr(name, ' ') > 0
                    THEN substr(name, 1, instr(name, ' ') - 1)
                    ELSE name
                END as firstName,
                CASE
                    WHEN instr(name, ' ') > 0
                    THEN substr(name, instr(name, ' ') + 1)
                    ELSE ''
                END as lastName,
                email,
                phoneNumber,
                createdAt,
                createdAt as updatedAt
            FROM users
            """.trimIndent()
        )

        // Step 3: Drop old table
        database.execSQL("DROP TABLE users")

        // Step 4: Rename new table
        database.execSQL("ALTER TABLE users_new RENAME TO users")

        // Step 5: Create unique index on email
        database.execSQL(
            """
            CREATE UNIQUE INDEX index_users_email
            ON users(email)
            """.trimIndent()
        )
    }
}
```

### Database Setup with Migrations

```kotlin
@Database(
    entities = [UserV3::class, Post::class, Comment::class],
    version = 3,
    exportSchema = true  // Important for migration testing
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun postDao(): PostDao
    abstract fun commentDao(): CommentDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                )
                    .addMigrations(
                        MIGRATION_1_2,
                        MIGRATION_2_3,
                        MIGRATION_3_4,
                        MIGRATION_4_5
                    )
                    // Fallback strategy
                    .fallbackToDestructiveMigration()  // For development only
                    // Or specific destructive migrations
                    .fallbackToDestructiveMigrationFrom(1, 2)
                    .build()

                INSTANCE = instance
                instance
            }
        }
    }
}
```

### Non-Destructive Migration Examples

#### Adding a New Table

```kotlin
val MIGRATION_3_4 = object : Migration(3, 4) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                userId INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                createdAt INTEGER NOT NULL,
                FOREIGN KEY(userId) REFERENCES users(id) ON DELETE CASCADE
            )
            """.trimIndent()
        )

        database.execSQL(
            """
            CREATE INDEX index_posts_userId
            ON posts(userId)
            """.trimIndent()
        )
    }
}
```

#### Adding Foreign Keys

```kotlin
val MIGRATION_4_5 = object : Migration(4, 5) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // SQLite doesn't support adding foreign keys to existing tables
        // Must recreate table

        // 1. Create new table with foreign key
        database.execSQL(
            """
            CREATE TABLE comments_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                postId INTEGER NOT NULL,
                userId INTEGER NOT NULL,
                text TEXT NOT NULL,
                createdAt INTEGER NOT NULL,
                FOREIGN KEY(postId) REFERENCES posts(id) ON DELETE CASCADE,
                FOREIGN KEY(userId) REFERENCES users(id) ON DELETE CASCADE
            )
            """.trimIndent()
        )

        // 2. Copy existing data
        database.execSQL(
            """
            INSERT INTO comments_new (id, postId, userId, text, createdAt)
            SELECT id, postId, userId, text, createdAt
            FROM comments
            """.trimIndent()
        )

        // 3. Drop old table
        database.execSQL("DROP TABLE comments")

        // 4. Rename new table
        database.execSQL("ALTER TABLE comments_new RENAME TO comments")

        // 5. Create indices
        database.execSQL("CREATE INDEX index_comments_postId ON comments(postId)")
        database.execSQL("CREATE INDEX index_comments_userId ON comments(userId)")
    }
}
```

### Destructive Migration Strategies

#### Complete Wipe (Development Only)

```kotlin
// Wipes database on version change - USE ONLY IN DEVELOPMENT
val database = Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .fallbackToDestructiveMigration()
    .build()
```

#### Selective Destructive Migration

```kotlin
// Wipe only when migrating from specific versions
val database = Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .fallbackToDestructiveMigrationFrom(1, 2)  // Wipe when coming from v1 or v2
    .addMigrations(MIGRATION_3_4, MIGRATION_4_5)  // But handle v3→4, v4→5
    .build()
```

#### Destructive Migration on Downgrade

```kotlin
val database = Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .fallbackToDestructiveMigrationOnDowngrade()  // Handle version downgrades
    .addMigrations(/* normal migrations */)
    .build()
```

### Testing Migrations

#### Migration Test Setup

```kotlin
@RunWith(AndroidJUnit4::class)
class MigrationTest {

    private val TEST_DB = "migration-test"

    @get:Rule
    val helper: MigrationTestHelper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java.canonicalName,
        FrameworkSQLiteOpenHelperFactory()
    )

    @Test
    fun migrate1To2() {
        // Create database with version 1 schema
        helper.createDatabase(TEST_DB, 1).apply {
            // Insert test data in version 1 format
            execSQL(
                """
                INSERT INTO users (id, name, email)
                VALUES (1, 'John Doe', 'john@example.com')
                """.trimIndent()
            )
            close()
        }

        // Run migration from 1 to 2
        helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)

        // Verify data integrity after migration
        helper.openDatabase(TEST_DB).use { db ->
            val cursor = db.query("SELECT * FROM users WHERE id = 1")
            assertTrue(cursor.moveToFirst())

            // Verify old columns still exist
            assertEquals("John Doe", cursor.getString(cursor.getColumnIndex("name")))
            assertEquals("john@example.com", cursor.getString(cursor.getColumnIndex("email")))

            // Verify new columns were added
            val phoneIndex = cursor.getColumnIndex("phoneNumber")
            assertTrue(phoneIndex >= 0)

            val createdAtIndex = cursor.getColumnIndex("createdAt")
            assertTrue(createdAtIndex >= 0)
            assertTrue(cursor.getLong(createdAtIndex) > 0)

            cursor.close()
        }
    }

    @Test
    fun migrate2To3() {
        // Create database with version 2
        helper.createDatabase(TEST_DB, 2).apply {
            execSQL(
                """
                INSERT INTO users (id, name, email, phoneNumber, createdAt)
                VALUES (1, 'Jane Smith', 'jane@example.com', '+1234567890', ${System.currentTimeMillis()})
                """.trimIndent()
            )
            close()
        }

        // Run migration
        helper.runMigrationsAndValidate(TEST_DB, 3, true, MIGRATION_2_3)

        // Verify name was split correctly
        helper.openDatabase(TEST_DB).use { db ->
            val cursor = db.query("SELECT * FROM users WHERE id = 1")
            assertTrue(cursor.moveToFirst())

            assertEquals("Jane", cursor.getString(cursor.getColumnIndex("firstName")))
            assertEquals("Smith", cursor.getString(cursor.getColumnIndex("lastName")))
            assertEquals("jane@example.com", cursor.getString(cursor.getColumnIndex("email")))

            cursor.close()
        }
    }

    @Test
    fun migrateAll() {
        // Create database at version 1
        helper.createDatabase(TEST_DB, 1).apply {
            execSQL(
                """
                INSERT INTO users (id, name, email)
                VALUES (1, 'Test User', 'test@example.com')
                """.trimIndent()
            )
            close()
        }

        // Migrate through all versions
        val db = helper.runMigrationsAndValidate(
            TEST_DB,
            3,
            true,
            MIGRATION_1_2,
            MIGRATION_2_3
        )

        // Verify final state
        val cursor = db.query("SELECT * FROM users WHERE id = 1")
        assertTrue(cursor.moveToFirst())
        assertEquals("Test", cursor.getString(cursor.getColumnIndex("firstName")))
        assertEquals("User", cursor.getString(cursor.getColumnIndex("lastName")))
        cursor.close()
    }
}
```

### Advanced Migration Patterns

#### Data Transformation During Migration

```kotlin
val MIGRATION_TRANSFORM = object : Migration(5, 6) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Example: Hash passwords that were previously plain text
        database.execSQL(
            """
            UPDATE users
            SET password = 'hashed_' || password
            WHERE password NOT LIKE 'hashed_%'
            """.trimIndent()
        )

        // Example: Normalize phone numbers
        database.execSQL(
            """
            UPDATE users
            SET phoneNumber = replace(replace(phoneNumber, '-', ''), ' ', '')
            WHERE phoneNumber IS NOT NULL
            """.trimIndent()
        )
    }
}
```

#### Handling NULL to NOT NULL Changes

```kotlin
val MIGRATION_NULL_TO_NOT_NULL = object : Migration(6, 7) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Can't directly change NULL to NOT NULL in SQLite
        // Must create new table

        database.execSQL(
            """
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY NOT NULL,
                firstName TEXT NOT NULL,
                lastName TEXT NOT NULL,
                email TEXT NOT NULL,
                phoneNumber TEXT NOT NULL DEFAULT '',  -- Changed from nullable
                createdAt INTEGER NOT NULL,
                updatedAt INTEGER NOT NULL
            )
            """.trimIndent()
        )

        // Copy data, replacing NULL with default value
        database.execSQL(
            """
            INSERT INTO users_new
            SELECT
                id,
                firstName,
                lastName,
                email,
                COALESCE(phoneNumber, '') as phoneNumber,  -- NULL → ''
                createdAt,
                updatedAt
            FROM users
            """.trimIndent()
        )

        database.execSQL("DROP TABLE users")
        database.execSQL("ALTER TABLE users_new RENAME TO users")
    }
}
```

### Best Practices

1. **Export Schema** - Set `exportSchema = true` for version tracking
2. **Test All Migrations** - Write tests for every migration path
3. **Backup Data** - Consider backup before migration in production
4. **Version Control Schemas** - Keep old schema files in version control
5. **Incremental Migrations** - Provide path for each version increment
6. **Validate After Migration** - Use `validateMigration()` in tests
7. **Handle Errors Gracefully** - Catch migration failures and inform users
8. **Document Changes** - Comment why each migration is needed
9. **Test on Real Devices** - Test with production-like data volumes
10. **Avoid Destructive Migrations** - In production, always preserve data

### Common Pitfalls

1. **Missing Migration Path** - Users can't update from old versions
2. **Incorrect SQL** - Syntax errors crash migrations
3. **Data Type Mismatches** - Changed types can cause data loss
4. **Index/Constraint Violations** - New constraints may fail on old data
5. **Performance Issues** - Large data migrations can take time
6. **Not Testing Migrations** - Broken migrations discovered in production

### Summary

Room migrations allow you to:
- **Update schema** while preserving user data
- **Version database** incrementally
- **Transform data** during migration
- **Test migrations** before production release
- **Handle failures** with fallback strategies

Always provide migration paths for production apps, test thoroughly, and never use destructive migrations in production unless absolutely necessary.

---

## Ответ (RU)
**Миграции Room** — это SQL скрипты, помогающие обновлять схему базы данных с сохранением существующих пользовательских данных. Правильная стратегия миграций критична для production приложений для предотвращения потери данных и падений.

### Основы миграций

При изменении схемы базы данных необходимо:
1. Увеличить версию базы данных
2. Предоставить путь миграции от старой версии к новой
3. Тщательно тестировать миграции
4. Обработать fallback стратегии

### Пример эволюции схемы

```kotlin
// Версия 1: Начальная схема
@Entity(tableName = "users")
data class UserV1(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String
)

// Версия 2: Добавление телефона и времени создания
@Entity(tableName = "users")
data class UserV2(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String,
    val phoneNumber: String?,  // Новая колонка
    val createdAt: Long        // Новая колонка с default
)

// Версия 3: Разделение name на firstName и lastName
@Entity(
    tableName = "users",
    indices = [Index(value = ["email"], unique = true)]
)
data class UserV3(
    @PrimaryKey val id: Long,
    val firstName: String,     // Разделено из name
    val lastName: String,      // Разделено из name
    val email: String,
    val phoneNumber: String?,
    val createdAt: Long,
    val updatedAt: Long = System.currentTimeMillis()
)
```

### Реализация миграций

#### Миграция 1 → 2: Добавление колонок

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Добавить колонку phoneNumber (nullable)
        database.execSQL(
            "ALTER TABLE users ADD COLUMN phoneNumber TEXT"
        )

        // Добавить колонку createdAt со значением по умолчанию
        database.execSQL(
            """
            ALTER TABLE users
            ADD COLUMN createdAt INTEGER NOT NULL DEFAULT ${System.currentTimeMillis()}
            """.trimIndent()
        )
    }
}
```

#### Миграция 2 → 3: Сложное изменение схемы

```kotlin
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Шаг 1: Создать новую таблицу с обновлённой схемой
        database.execSQL(
            """
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY NOT NULL,
                firstName TEXT NOT NULL,
                lastName TEXT NOT NULL,
                email TEXT NOT NULL,
                phoneNumber TEXT,
                createdAt INTEGER NOT NULL,
                updatedAt INTEGER NOT NULL DEFAULT ${System.currentTimeMillis()}
            )
            """.trimIndent()
        )

        // Шаг 2: Скопировать данные из старой таблицы, разделяя name
        database.execSQL(
            """
            INSERT INTO users_new (id, firstName, lastName, email, phoneNumber, createdAt, updatedAt)
            SELECT
                id,
                CASE
                    WHEN instr(name, ' ') > 0
                    THEN substr(name, 1, instr(name, ' ') - 1)
                    ELSE name
                END as firstName,
                CASE
                    WHEN instr(name, ' ') > 0
                    THEN substr(name, instr(name, ' ') + 1)
                    ELSE ''
                END as lastName,
                email,
                phoneNumber,
                createdAt,
                createdAt as updatedAt
            FROM users
            """.trimIndent()
        )

        // Шаг 3: Удалить старую таблицу
        database.execSQL("DROP TABLE users")

        // Шаг 4: Переименовать новую таблицу
        database.execSQL("ALTER TABLE users_new RENAME TO users")

        // Шаг 5: Создать уникальный индекс на email
        database.execSQL(
            "CREATE UNIQUE INDEX index_users_email ON users(email)"
        )
    }
}
```

### Настройка базы данных с миграциями

```kotlin
@Database(
    entities = [UserV3::class, Post::class],
    version = 3,
    exportSchema = true  // Важно для тестирования миграций
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun getDatabase(context: Context): AppDatabase {
            return Room.databaseBuilder(
                context.applicationContext,
                AppDatabase::class.java,
                "app_database"
            )
                .addMigrations(
                    MIGRATION_1_2,
                    MIGRATION_2_3
                )
                // Fallback стратегия (только для development)
                .fallbackToDestructiveMigration()
                .build()
        }
    }
}
```

### Тестирование миграций

```kotlin
@RunWith(AndroidJUnit4::class)
class MigrationTest {

    private val TEST_DB = "migration-test"

    @get:Rule
    val helper: MigrationTestHelper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java.canonicalName,
        FrameworkSQLiteOpenHelperFactory()
    )

    @Test
    fun migrate1To2() {
        // Создать БД с версией 1
        helper.createDatabase(TEST_DB, 1).apply {
            execSQL(
                """
                INSERT INTO users (id, name, email)
                VALUES (1, 'John Doe', 'john@example.com')
                """.trimIndent()
            )
            close()
        }

        // Выполнить миграцию 1 → 2
        helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)

        // Проверить целостность данных после миграции
        helper.openDatabase(TEST_DB).use { db ->
            val cursor = db.query("SELECT * FROM users WHERE id = 1")
            assertTrue(cursor.moveToFirst())

            // Проверить, что старые колонки остались
            assertEquals("John Doe", cursor.getString(cursor.getColumnIndex("name")))

            // Проверить, что новые колонки добавлены
            assertTrue(cursor.getColumnIndex("phoneNumber") >= 0)
            assertTrue(cursor.getColumnIndex("createdAt") >= 0)

            cursor.close()
        }
    }

    @Test
    fun migrateAll() {
        // Создать БД версии 1
        helper.createDatabase(TEST_DB, 1).apply {
            execSQL("INSERT INTO users (id, name, email) VALUES (1, 'Test User', 'test@example.com')")
            close()
        }

        // Мигрировать через все версии
        helper.runMigrationsAndValidate(TEST_DB, 3, true, MIGRATION_1_2, MIGRATION_2_3)
    }
}
```

### Best Practices

1. **Экспортировать схему** - установить `exportSchema = true`
2. **Тестировать все миграции** - писать тесты для каждого пути миграции
3. **Бэкап данных** - рассмотреть бэкап перед миграцией в production
4. **Версионировать схемы** - хранить старые файлы схем в version control
5. **Инкрементальные миграции** - предоставлять путь для каждого инкремента версии
6. **Валидировать после миграции** - использовать `validateMigration()` в тестах
7. **Обрабатывать ошибки** - ловить failures миграций и информировать пользователей
8. **Документировать изменения** - комментировать зачем нужна каждая миграция
9. **Избегать деструктивных миграций** - в production всегда сохранять данные

### Резюме

Миграции Room позволяют:
- **Обновлять схему** с сохранением пользовательских данных
- **Версионировать БД** инкрементально
- **Трансформировать данные** во время миграции
- **Тестировать миграции** перед production релизом
- **Обрабатывать failures** с fallback стратегиями

Всегда предоставляйте пути миграций для production приложений, тщательно тестируйте и никогда не используйте деструктивные миграции в production без крайней необходимости.

---

## Related Questions

### Prerequisites (Easier)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-room-library-definition--android--easy]] - Storage

### Related (Medium)
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--room--medium]] - Storage
- [[q-room-paging3-integration--room--medium]] - Storage
- [[q-room-type-converters-advanced--room--medium]] - Storage
- [[q-save-markdown-structure-database--android--medium]] - Storage

### Advanced (Harder)
- [[q-room-fts-full-text-search--room--hard]] - Storage
