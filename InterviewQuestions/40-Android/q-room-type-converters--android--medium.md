---
id: android-354
title: Room Type Converters / TypeConverters в Room
aliases: [Room Type Converters, Room конвертеры типов, TypeConverters в Room]

# Classification
topic: android
subtopics: [room, serialization]
question_kind: android
difficulty: medium

# Language
original_language: en
language_tags: [en, ru]

# Workflow
status: draft

# Links
moc: moc-android
related: [c-room, q-room-library-definition--android--easy, q-room-vs-sqlite--android--medium]
sources: []

# Timestamps
created: 2025-10-15
updated: 2025-10-28

# Tags
tags: [android/room, android/serialization, database, difficulty/medium, room, typeconverter]
---

# Вопрос (RU)

Что вы знаете о TypeConverters в Room?

# Question (EN)

What do you know about Converters in Room?

---

## Ответ (RU)

**Room TypeConverters** — это механизм преобразования пользовательских типов данных в примитивные типы, которые Room умеет сохранять в SQLite. Они позволяют работать с Date, Enum, List и сложными объектами как с обычными полями Entity.

### Основной Принцип

Room знает только примитивы (Int, Long, String, Boolean, etc). Для кастомных типов нужны конвертеры.

**Простой пример:**

```kotlin
class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }  // ✅ Long → Date

    @TypeConverter
    fun toTimestamp(date: Date?): Long? = date?.time  // ✅ Date → Long
}

@Database(entities = [User::class], version = 1)
@TypeConverters(Converters::class)  // ✅ Регистрация конвертеров
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

### Области Видимости

Конвертеры можно применять на 4 уровнях:

```kotlin
// 1. Уровень БД — доступны всем Entity и DAO
@Database(entities = [User::class], version = 1)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase()

// 2. Уровень Entity — только для этой сущности
@Entity
@TypeConverters(Converters::class)
data class Event(val date: Date)

// 3. Уровень DAO — только для методов DAO
@Dao
@TypeConverters(Converters::class)
interface EventDao

// 4. Уровень поля — самая узкая область
@Entity
data class User(
    @TypeConverters(Converters::class) val birthday: Date?  // ❌ Избыточно, если есть на уровне БД
)
```

### Распространённые Примеры

**Enum:**

```kotlin
enum class Status { ACTIVE, INACTIVE }

class Converters {
    @TypeConverter
    fun fromStatus(value: Status?): String? = value?.name  // ✅ ACTIVE → "ACTIVE"

    @TypeConverter
    fun toStatus(value: String?): Status? =
        value?.let { Status.valueOf(it) }  // ✅ "ACTIVE" → ACTIVE
}
```

**List через JSON:**

```kotlin
class Converters {
    private val gson = Gson()

    @TypeConverter
    fun fromList(list: List<String>?): String? =
        gson.toJson(list)  // ✅ ["a","b"] → "[\"a\",\"b\"]"

    @TypeConverter
    fun toList(json: String?): List<String>? {
        val type = object : TypeToken<List<String>>() {}.type
        return gson.fromJson(json, type)  // ✅ "[\"a\",\"b\"]" → ["a","b"]
    }
}
```

### ProvidedTypeConverter — Инъекция Зависимостей

Когда конвертеру нужны зависимости (например, Gson):

```kotlin
@ProvidedTypeConverter  // ✅ Указывает, что экземпляр создаётся вручную
class JsonConverter(private val gson: Gson) {
    @TypeConverter
    fun toJson(obj: Address?): String? = gson.toJson(obj)

    @TypeConverter
    fun fromJson(json: String?): Address? =
        json?.let { gson.fromJson(it, Address::class.java) }
}

// Регистрация
val db = Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .addTypeConverter(JsonConverter(Gson()))  // ✅ Передача готового экземпляра
    .build()
```

### Ограничения И Best Practices

1. **Избегайте тяжёлых операций** — конвертеры вызываются на каждой операции чтения/записи
2. **Не для связей** — Room запрещает хранить ссылки на другие Entity (используйте Foreign Keys + @Relation)
3. **Обрабатывайте null** — используйте nullable типы (`Long?`, `Date?`)
4. **Тестируйте двусторонность** — `toX(fromX(value)) == value`

**Почему Room не поддерживает Object References:**

```kotlin
// ❌ ЗАПРЕЩЕНО — Room не сохранит вложенный объект
@Entity
data class Post(
    @PrimaryKey val id: Int,
    val author: User  // ❌ Компилятор выдаст ошибку
)

// ✅ ПРАВИЛЬНО — связь через Foreign Key
@Entity
data class Post(
    @PrimaryKey val id: Int,
    val authorId: Int  // ✅ Ссылка через ID
)

data class PostWithAuthor(
    @Embedded val post: Post,
    @Relation(parentColumn = "authorId", entityColumn = "id")
    val author: User  // ✅ Автоматическая загрузка через JOIN
)
```

Причины запрета:
- Избежание ленивой загрузки на UI-потоке
- Контроль потребления памяти
- Явное определение связей

---

## Answer (EN)

**Room TypeConverters** are a mechanism for converting custom data types to primitive types that Room can persist in SQLite. They enable working with Date, Enum, List, and complex objects as regular Entity fields.

### Core Principle

Room only understands primitives (Int, Long, String, Boolean, etc). Custom types require converters.

**Basic Example:**

```kotlin
class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }  // ✅ Long → Date

    @TypeConverter
    fun toTimestamp(date: Date?): Long? = date?.time  // ✅ Date → Long
}

@Database(entities = [User::class], version = 1)
@TypeConverters(Converters::class)  // ✅ Register converters
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

### Scoping Levels

Converters can be applied at 4 levels:

```kotlin
// 1. Database level — available to all Entities and DAOs
@Database(entities = [User::class], version = 1)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase()

// 2. Entity level — only for this entity
@Entity
@TypeConverters(Converters::class)
data class Event(val date: Date)

// 3. DAO level — only for DAO methods
@Dao
@TypeConverters(Converters::class)
interface EventDao

// 4. Field level — narrowest scope
@Entity
data class User(
    @TypeConverters(Converters::class) val birthday: Date?  // ❌ Redundant if set at DB level
)
```

### Common Examples

**Enum:**

```kotlin
enum class Status { ACTIVE, INACTIVE }

class Converters {
    @TypeConverter
    fun fromStatus(value: Status?): String? = value?.name  // ✅ ACTIVE → "ACTIVE"

    @TypeConverter
    fun toStatus(value: String?): Status? =
        value?.let { Status.valueOf(it) }  // ✅ "ACTIVE" → ACTIVE
}
```

**List via JSON:**

```kotlin
class Converters {
    private val gson = Gson()

    @TypeConverter
    fun fromList(list: List<String>?): String? =
        gson.toJson(list)  // ✅ ["a","b"] → "[\"a\",\"b\"]"

    @TypeConverter
    fun toList(json: String?): List<String>? {
        val type = object : TypeToken<List<String>>() {}.type
        return gson.fromJson(json, type)  // ✅ "[\"a\",\"b\"]" → ["a","b"]
    }
}
```

### ProvidedTypeConverter — Dependency Injection

When converters need dependencies (e.g., Gson):

```kotlin
@ProvidedTypeConverter  // ✅ Indicates manual instantiation
class JsonConverter(private val gson: Gson) {
    @TypeConverter
    fun toJson(obj: Address?): String? = gson.toJson(obj)

    @TypeConverter
    fun fromJson(json: String?): Address? =
        json?.let { gson.fromJson(it, Address::class.java) }
}

// Registration
val db = Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .addTypeConverter(JsonConverter(Gson()))  // ✅ Pass instance
    .build()
```

### Constraints and Best Practices

1. **Avoid heavy operations** — converters run on every read/write
2. **Not for relationships** — Room forbids storing Entity references (use Foreign Keys + @Relation)
3. **Handle nullability** — use nullable types (`Long?`, `Date?`)
4. **Test bidirectionality** — `toX(fromX(value)) == value`

**Why Room Disallows Object References:**

```kotlin
// ❌ FORBIDDEN — Room won't save nested object
@Entity
data class Post(
    @PrimaryKey val id: Int,
    val author: User  // ❌ Compiler error
)

// ✅ CORRECT — relationship via Foreign Key
@Entity
data class Post(
    @PrimaryKey val id: Int,
    val authorId: Int  // ✅ Reference via ID
)

data class PostWithAuthor(
    @Embedded val post: Post,
    @Relation(parentColumn = "authorId", entityColumn = "id")
    val author: User  // ✅ Automatic JOIN loading
)
```

Reasons:
- Avoid lazy loading on UI thread
- Control memory consumption
- Explicit relationship definition

---

## Follow-ups

1. How do you convert complex nested objects (e.g., `List<Address>`)?
2. What happens if TypeConverter throws an exception during read?
3. Can you use Kotlin serialization instead of Gson for converters?
4. How to migrate database when changing TypeConverter implementation?
5. What's the performance impact of JSON serialization in converters?

## References

- [[c-room]] - Room persistence library
- [Room Referencing Complex Data](https://developer.android.com/training/data-storage/room/referencing-data) - Official docs

## Related Questions

### Prerequisites (Easier)
- [[q-room-library-definition--android--easy]] - What is Room?

### Related (Medium)
- [[q-room-vs-sqlite--android--medium]] - Room vs raw SQLite
- [[q-room-code-generation-timing--android--medium]] - Room annotation processing

### Advanced (Harder)
- [[q-room-database-migrations--android--medium]] - Database schema migrations
