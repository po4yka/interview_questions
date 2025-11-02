---
id: ivc-20251030-140000
title: Room Database / Room Database
aliases: [Android Room, Room, Room Database, Room Persistence]
kind: concept
summary: SQLite abstraction layer providing compile-time verification and easier database access
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [android, concept, database, persistence, room, sqlite]
date created: Thursday, October 30th 2025, 12:30:16 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Summary (EN)

Room is an Android persistence library that provides an abstraction layer over SQLite. It consists of three main components: Entity (data class representing a table), DAO (Data Access Object with query methods), and Database (holder class that manages the database instance). Room offers compile-time SQL verification, seamless integration with LiveData/Flow for reactive data, and type-safe database access through annotations.

# Сводка (RU)

Room — это библиотека для работы с базами данных в Android, предоставляющая абстракцию над SQLite. Состоит из трех основных компонентов: Entity (класс данных, представляющий таблицу), DAO (Data Access Object с методами запросов) и Database (класс-держатель, управляющий экземпляром БД). Room обеспечивает проверку SQL на этапе компиляции, бесшовную интеграцию с LiveData/Flow для реактивных данных и типобезопасный доступ к БД через аннотации.

---

## Core Components (EN)

### Entity
Represents a database table. Each instance is a row.

```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    @ColumnInfo(name = "user_name") val name: String,
    val email: String
)
```

### DAO (Data Access Object)
Defines database operations. Room generates implementation at compile-time.

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: Long): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User): Long

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)

    @Query("SELECT * FROM users ORDER BY user_name")
    fun observeAllUsers(): Flow<List<User>>
}
```

### Database
Abstract class that extends RoomDatabase. Singleton holder for DAO instances.

```kotlin
@Database(entities = [User::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
```

## Основные Компоненты (RU)

### Entity
Представляет таблицу БД. Каждый экземпляр — это строка.

### DAO (Data Access Object)
Определяет операции с БД. Room генерирует реализацию на этапе компиляции.

### Database
Абстрактный класс, наследующий RoomDatabase. Singleton-держатель для экземпляров DAO.

---

## Key Benefits (EN)

**Compile-time verification**: SQL queries are checked at compile-time, preventing runtime crashes from typos.

**Reactive data**: Native integration with LiveData, Flow, RxJava for observing database changes.

**Type safety**: No need to parse Cursor manually. Room handles object mapping automatically.

**Migration support**: Structured approach to schema changes with Migration objects.

**Transaction support**: `@Transaction` annotation for atomic operations.

## Ключевые Преимущества (RU)

**Проверка на этапе компиляции**: SQL-запросы проверяются при компиляции, предотвращая runtime-ошибки из-за опечаток.

**Реактивные данные**: Нативная интеграция с LiveData, Flow, RxJava для наблюдения за изменениями в БД.

**Типобезопасность**: Не нужно вручную парсить Cursor. Room автоматически маппит объекты.

**Поддержка миграций**: Структурированный подход к изменениям схемы через объекты Migration.

**Поддержка транзакций**: Аннотация `@Transaction` для атомарных операций.

---

## Migrations & Type Converters (EN)

### Migrations
Handle schema changes between versions:

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("ALTER TABLE users ADD COLUMN age INTEGER NOT NULL DEFAULT 0")
    }
}

Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
    .addMigrations(MIGRATION_1_2)
    .build()
```

### Type Converters
Store custom types (Date, enums, lists):

```kotlin
class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? {
        return value?.let { Date(it) }
    }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? {
        return date?.time
    }
}

@Database(entities = [User::class], version = 1)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase()
```

## Миграции И Конвертеры Типов (RU)

### Миграции
Обрабатывают изменения схемы между версиями БД.

### Конвертеры Типов
Хранят кастомные типы (Date, enum, списки).

---

## Use Cases / Trade-offs

**Use Room when**:
- Need structured local storage with relations
- Want compile-time SQL verification
- Need reactive queries (Flow, LiveData)
- Working with complex queries and joins

**Trade-offs**:
- Overhead for simple key-value storage (use DataStore instead)
- Learning curve for migrations
- Annotation processing increases build time slightly
- Not suitable for large binary data (use files + paths in DB)

**Best with**: MVVM architecture, Repository pattern, Hilt dependency injection

---

## References

- [Official Room Documentation](https://developer.android.com/training/data-storage/room)
- [Room Migration Guide](https://developer.android.com/training/data-storage/room/migrating-db-versions)
- [Room with Flow and Coroutines](https://developer.android.com/codelabs/android-room-with-a-view-kotlin)
