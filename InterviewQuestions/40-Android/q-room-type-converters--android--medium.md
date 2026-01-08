---\
id: android-354
title: Room Type Converters / TypeConverters в Room
aliases: [Room Type Converters, Room конвертеры типов, TypeConverters в Room]
topic: android
subtopics: [room]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-room-library-definition--android--easy, q-room-vs-sqlite--android--medium]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/room, difficulty/medium]
---\
# Вопрос (RU)

> Что вы знаете о TypeConverters в `Room`?

# Question (EN)

> What do you know about TypeConverters in `Room`?

## Ответ (RU)

**`Room` TypeConverters** — это механизм преобразования пользовательских типов данных в примитивные типы и иные поддерживаемые типы (например, `String`, `Int`, `Long`), которые `Room` умеет сохранять в `SQLite`. Они позволяют работать с `Date`, `Enum`, `List` и сложными объектами как с обычными полями `Entity`, если есть корректные конвертеры.

### Основной Принцип

`Room` напрямую поддерживает ограниченный набор типов (`Int`, `Long`, `String`, `Boolean`, `Double`, `byte[]`, и некоторые другие). Для остальных (кастомных) типов нужны конвертеры.

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

**`List` через JSON:**

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

Когда конвертеру нужны зависимости (например, `Gson`):

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

1. Избегайте тяжёлых операций — конвертеры вызываются при чтении/записи соответствующих полей.
2. Не для связей — `Room` не должен хранить ссылки на другие `Entity` как вложенные объекты (используйте Foreign Keys + @Relation или отдельные таблицы).
3. Обрабатывайте null — используйте nullable типы (`Long?`, `Date?`), учитывая, что `SQLite` допускает NULL.
4. Тестируйте двусторонность — для симметричных конвертеров проверяйте, что `toX(fromX(value)) == value`.

**Почему не стоит хранить объектные ссылки напрямую:**

```kotlin
// ❌ Не рекомендуется — Room попытается применить конвертер или сообщит об ошибке,
// хранить Entity как вложенный объект без явной схемы неверно с точки зрения модели данных
@Entity
data class Post(
    @PrimaryKey val id: Int,
    val author: User
)

// ✅ Правильно — связь через внешний ключ или колонку-идентификатор
@Entity
data class Post(
    @PrimaryKey val id: Int,
    val authorId: Int  // ✅ Ссылка через ID
)

data class PostWithAuthor(
    @Embedded val post: Post,
    @Relation(parentColumn = "authorId", entityColumn = "id")
    val author: User  // ✅ Загрузка через JOIN
)
```

Причины такого подхода:
- Явная схема и нормализация данных
- Предсказуемые запросы и отсутствие скрытой ленивой загрузки
- Контроль ресурсов и зависимостей между сущностями

## Answer (EN)

**`Room` TypeConverters** are a mechanism for converting custom data types into primitive and other supported types (e.g., `String`, `Int`, `Long`) that `Room` can persist in `SQLite`. They allow you to use `Date`, `Enum`, `List`, and complex objects as entity fields, as long as corresponding converters are defined.

### Core Principle

`Room` natively supports only a limited set of types (`Int`, `Long`, `String`, `Boolean`, `Double`, `byte[]`, and a few others). Custom types require converters.

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

**`List` via JSON:**

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

When converters need dependencies (e.g., `Gson`):

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

1. Avoid heavy operations — converters are invoked on read/write of the mapped fields.
2. Not for relationships — you should not store entity references as nested objects; use Foreign Keys + @Relation or separate tables.
3. Handle nullability — use nullable types (`Long?`, `Date?`) appropriately, considering `SQLite` allows NULL.
4. Test bidirectionality — for symmetric converters, validate `toX(fromX(value)) == value`.

**Why you shouldn't store object references directly:**

```kotlin
// ❌ Not recommended — Room will either require a converter or fail,
// and persisting another Entity as a nested object breaks proper schema design
@Entity
data class Post(
    @PrimaryKey val id: Int,
    val author: User
)

// ✅ Correct — relationship via foreign key or identifier column
@Entity
data class Post(
    @PrimaryKey val id: Int,
    val authorId: Int  // ✅ Reference via ID
)

data class PostWithAuthor(
    @Embedded val post: Post,
    @Relation(parentColumn = "authorId", entityColumn = "id")
    val author: User  // ✅ Loaded via JOIN
)
```

Reasons for this approach:
- Explicit schema and normalized data
- Predictable queries without hidden lazy loading
- Better control over resources and entity relationships

## Дополнительные Вопросы (RU)

1. Как реализовать конвертер для сложных вложенных объектов (например, `List<Address>`)?
2. Что произойдет, если `TypeConverter` выбросит исключение во время чтения значения?
3. Можно ли использовать Kotlin Serialization вместо `Gson` в конвертерах?
4. Как выполнять миграции базы данных при изменении реализации `TypeConverter`?
5. Как оценить и минимизировать влияние JSON-сериализации в конвертерах на производительность?

## Follow-ups

1. How do you convert complex nested objects (e.g., `List<Address>`)?
2. What happens if a `TypeConverter` throws an exception during read?
3. Can you use Kotlin Serialization instead of `Gson` for converters?
4. How to migrate the database when changing a `TypeConverter` implementation?
5. What is the performance impact of JSON serialization in converters and how can it be minimized?

## Ссылки (RU)

- [Room Referencing Complex Data](https://developer.android.com/training/data-storage/room/referencing-data) — официальная документация

## References

- [Room Referencing Complex Data](https://developer.android.com/training/data-storage/room/referencing-data) - Official docs

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-room-library-definition--android--easy]] — Что такое `Room`?

### Связанные (средний уровень)
- [[q-room-vs-sqlite--android--medium]] — `Room` против «сырого» `SQLite`
- [[q-room-code-generation-timing--android--medium]] — В какое время выполняется генерация кода `Room`?

### Продвинутые (сложнее)
- [[q-room-database-migrations--android--medium]] — Миграции схемы базы данных

## Related Questions

### Prerequisites (Easier)
- [[q-room-library-definition--android--easy]] - What is `Room`?

### Related (Medium)
- [[q-room-vs-sqlite--android--medium]] - `Room` vs raw `SQLite`
- [[q-room-code-generation-timing--android--medium]] - `Room` annotation processing timing

### Advanced (Harder)
- [[q-room-database-migrations--android--medium]] - `Database` schema migrations
