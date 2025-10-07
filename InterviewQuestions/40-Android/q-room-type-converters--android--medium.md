---
topic: android
tags:
  - android
  - room
  - typeconverter
  - database
  - custom-types
  - difficulty/medium
difficulty: medium
status: draft
---

# Room TypeConverters / TypeConverters в Room

**English**: What do you know about Converters in Room?

## Answer

**Room TypeConverters** are methods that tell Room how to convert **custom types to and from known types** that Room can persist in the database. They enable you to store custom data types in a single database column.

Room doesn't know how to persist custom types by default, so you need to provide type converters using the `@TypeConverter` annotation.

**Basic Example - Converting Date:**

Suppose you need to persist instances of `Date` in your Room database. Room doesn't know how to persist `Date` objects, so you need to define type converters:

```kotlin
class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? {
        return value?.let { Date(it) }
    }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? {
        return date?.time?.toLong()
    }
}
```

This example defines two type converter methods:
- One that converts a `Date` object to a `Long` object
- One that performs the inverse conversion from `Long` to `Date`

Because Room knows how to persist `Long` objects, it can use these converters to persist `Date` objects.

**Registering TypeConverters:**

Next, you add the `@TypeConverters` annotation to the `AppDatabase` class so that Room knows about the converter class:

```kotlin
@Database(entities = [User::class], version = 1)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

**Using Custom Types in Entities and DAOs:**

With these type converters defined, you can use your custom type in your entities and DAOs just as you would use primitive types:

```kotlin
@Entity
data class User(
    @PrimaryKey val id: Int,
    val name: String,
    val birthday: Date?  // Custom type now supported!
)

@Dao
interface UserDao {
    @Query("SELECT * FROM user WHERE birthday = :targetDate")
    fun findUsersBornOnDate(targetDate: Date): List<User>
}
```

**Scoping TypeConverters:**

You can scope type converters to different levels:

**1. Database level (entire app):**

```kotlin
@Database(entities = [User::class, Event::class], version = 1)
@TypeConverters(Converters::class)  // Available to all entities and DAOs
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun eventDao(): EventDao
}
```

**2. Entity level:**

```kotlin
@Entity
@TypeConverters(Converters::class)  // Only for this entity
data class Event(
    @PrimaryKey val id: Int,
    val title: String,
    val date: Date
)
```

**3. DAO level:**

```kotlin
@Dao
@TypeConverters(Converters::class)  // Only for this DAO
interface EventDao {
    @Query("SELECT * FROM event WHERE date > :fromDate")
    fun getEventsAfter(fromDate: Date): List<Event>
}
```

**4. Property level:**

```kotlin
@Entity
data class User(
    @PrimaryKey val id: Int,
    val name: String,
    @TypeConverters(Converters::class)  // Only for this field
    val birthday: Date?
)
```

**Common TypeConverter Examples:**

**1. List/Array Converters:**

```kotlin
class Converters {
    @TypeConverter
    fun fromStringList(value: List<String>?): String? {
        return value?.joinToString(",")
    }

    @TypeConverter
    fun toStringList(value: String?): List<String>? {
        return value?.split(",")?.map { it.trim() }
    }
}

// Usage
@Entity
data class User(
    @PrimaryKey val id: Int,
    val tags: List<String>  // Stored as comma-separated string
)
```

**2. JSON Object Converters (using Gson):**

```kotlin
class Converters {
    private val gson = Gson()

    @TypeConverter
    fun fromAddress(address: Address?): String? {
        return gson.toJson(address)
    }

    @TypeConverter
    fun toAddress(json: String?): Address? {
        return json?.let { gson.fromJson(it, Address::class.java) }
    }
}

// Usage
@Entity
data class User(
    @PrimaryKey val id: Int,
    val name: String,
    val address: Address  // Stored as JSON string
)

data class Address(
    val street: String,
    val city: String,
    val zipCode: String
)
```

**3. Enum Converters:**

```kotlin
enum class UserStatus {
    ACTIVE, INACTIVE, SUSPENDED
}

class Converters {
    @TypeConverter
    fun fromUserStatus(status: UserStatus?): String? {
        return status?.name
    }

    @TypeConverter
    fun toUserStatus(value: String?): UserStatus? {
        return value?.let { UserStatus.valueOf(it) }
    }
}
```

**4. UUID Converters:**

```kotlin
class Converters {
    @TypeConverter
    fun fromUUID(uuid: UUID?): String? {
        return uuid?.toString()
    }

    @TypeConverter
    fun toUUID(value: String?): UUID? {
        return value?.let { UUID.fromString(it) }
    }
}
```

**Controlling TypeConverter Initialization:**

Ordinarily, Room handles instantiation of type converters. However, sometimes you might need to pass additional dependencies to your type converter classes. In that case, annotate your converter class with `@ProvidedTypeConverter`:

```kotlin
@ProvidedTypeConverter
class ExampleConverter(private val gson: Gson) {
    @TypeConverter
    fun fromAddress(address: Address?): String? {
        return gson.toJson(address)
    }

    @TypeConverter
    fun toAddress(json: String?): Address? {
        return json?.let { gson.fromJson(it, Address::class.java) }
    }
}
```

Then, use the `RoomDatabase.Builder.addTypeConverter()` method to pass an instance of your converter class to the `RoomDatabase` builder:

```kotlin
val gson = Gson()
val converter = ExampleConverter(gson)

val db = Room.databaseBuilder(context, AppDatabase::class.java, "app-db")
    .addTypeConverter(converter)
    .build()
```

**Complete Real-World Example:**

```kotlin
// Converters.kt
class Converters {
    private val gson = Gson()

    // Date converters
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? {
        return value?.let { Date(it) }
    }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? {
        return date?.time
    }

    // List<String> converters
    @TypeConverter
    fun fromStringList(list: List<String>?): String? {
        return gson.toJson(list)
    }

    @TypeConverter
    fun toStringList(json: String?): List<String>? {
        val type = object : TypeToken<List<String>>() {}.type
        return gson.fromJson(json, type)
    }

    // Enum converters
    @TypeConverter
    fun fromUserStatus(status: UserStatus?): String? {
        return status?.name
    }

    @TypeConverter
    fun toUserStatus(value: String?): UserStatus? {
        return value?.let { UserStatus.valueOf(it) }
    }
}

// Entity using converters
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: Int,
    val name: String,
    val birthday: Date,
    val tags: List<String>,
    val status: UserStatus,
    val createdAt: Date = Date()
)

// Database
@Database(entities = [User::class], version = 1)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

**Why Room Doesn't Allow Object References:**

Room deliberately doesn't support object references to avoid:
- **Performance issues**: Lazy loading on the UI thread (usually 16ms to draw a frame)
- **Memory consumption**: Fetching more data than needed
- **Complexity**: Difficult to maintain as UI changes

Instead, Room encourages:
- Using POJOs with explicit JOINs
- Defining clear data relationships
- Loading only what's needed

**Best Practices:**

1. **Keep converters simple** — avoid heavy computations
2. **Use appropriate scope** — apply converters at the right level
3. **Handle nullability** — consider nullable types
4. **Be consistent** — use the same conversion approach throughout
5. **Consider serialization library** — use Gson, Moshi, or kotlinx.serialization for complex objects
6. **Test your converters** — ensure bidirectional conversion works correctly

**Common Use Cases:**

- ✅ Date/Time types (Date, LocalDateTime, Instant)
- ✅ Enums
- ✅ UUIDs
- ✅ Lists and Sets
- ✅ Custom objects (via JSON)
- ✅ BigDecimal for currency
- ✅ Custom value classes

**Summary:**

- **TypeConverters**: Methods to convert custom types to/from database-compatible types
- **Annotation**: `@TypeConverter` on conversion methods, `@TypeConverters` to register
- **Scope**: Database, Entity, DAO, or property level
- **Use cases**: Date, Enum, List, JSON objects, UUID
- **Custom initialization**: Use `@ProvidedTypeConverter` with dependencies
- **Performance**: Keep conversions lightweight

**Source**: [Referencing complex data using Room](https://developer.android.com/training/data-storage/room/referencing-data)

## Ответ

**Room TypeConverters** — это методы, которые сообщают Room, как преобразовывать **пользовательские типы в известные типы** и обратно, чтобы Room мог сохранять их в базе данных. Они позволяют хранить пользовательские типы данных в одном столбце базы данных.

Room не знает, как сохранять пользовательские типы по умолчанию, поэтому необходимо предоставить конвертеры типов с помощью аннотации `@TypeConverter`.

**Базовый пример - конвертация Date:**

```kotlin
class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? {
        return value?.let { Date(it) }
    }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? {
        return date?.time?.toLong()
    }
}
```

Этот пример определяет два метода конвертера:
- Один преобразует объект `Date` в объект `Long`
- Другой выполняет обратное преобразование из `Long` в `Date`

**Регистрация TypeConverters:**

Добавьте аннотацию `@TypeConverters` к классу `AppDatabase`:

```kotlin
@Database(entities = [User::class], version = 1)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

**Использование пользовательских типов:**

```kotlin
@Entity
data class User(
    @PrimaryKey val id: Int,
    val name: String,
    val birthday: Date?  // Пользовательский тип теперь поддерживается!
)

@Dao
interface UserDao {
    @Query("SELECT * FROM user WHERE birthday = :targetDate")
    fun findUsersBornOnDate(targetDate: Date): List<User>
}
```

**Области видимости TypeConverters:**

Конвертеры типов можно применять на разных уровнях:
1. **Уровень базы данных** — доступны для всех сущностей и DAO
2. **Уровень сущности** — только для конкретной сущности
3. **Уровень DAO** — только для конкретного DAO
4. **Уровень свойства** — только для конкретного поля

**Распространённые примеры TypeConverter:**

**1. Конвертеры для List:**

```kotlin
class Converters {
    @TypeConverter
    fun fromStringList(value: List<String>?): String? {
        return value?.joinToString(",")
    }

    @TypeConverter
    fun toStringList(value: String?): List<String>? {
        return value?.split(",")?.map { it.trim() }
    }
}
```

**2. Конвертеры JSON объектов (с Gson):**

```kotlin
class Converters {
    private val gson = Gson()

    @TypeConverter
    fun fromAddress(address: Address?): String? {
        return gson.toJson(address)
    }

    @TypeConverter
    fun toAddress(json: String?): Address? {
        return json?.let { gson.fromJson(it, Address::class.java) }
    }
}
```

**3. Конвертеры для Enum:**

```kotlin
enum class UserStatus { ACTIVE, INACTIVE, SUSPENDED }

class Converters {
    @TypeConverter
    fun fromUserStatus(status: UserStatus?): String? = status?.name

    @TypeConverter
    fun toUserStatus(value: String?): UserStatus? =
        value?.let { UserStatus.valueOf(it) }
}
```

**Контроль инициализации TypeConverter:**

Для передачи зависимостей в конвертеры используйте `@ProvidedTypeConverter`:

```kotlin
@ProvidedTypeConverter
class ExampleConverter(private val gson: Gson) {
    @TypeConverter
    fun fromAddress(address: Address?): String? {
        return gson.toJson(address)
    }

    @TypeConverter
    fun toAddress(json: String?): Address? {
        return json?.let { gson.fromJson(it, Address::class.java) }
    }
}

// Регистрация
val db = Room.databaseBuilder(context, AppDatabase::class.java, "app-db")
    .addTypeConverter(ExampleConverter(Gson()))
    .build()
```

**Лучшие практики:**

1. Держите конвертеры простыми — избегайте тяжёлых вычислений
2. Используйте подходящую область видимости
3. Обрабатывайте nullable типы
4. Будьте последовательны в подходе к конвертации
5. Рассмотрите библиотеки сериализации для сложных объектов
6. Тестируйте конвертеры на корректность двунаправленного преобразования

**Распространённые случаи использования:**

- Date/Time типы (Date, LocalDateTime, Instant)
- Enum'ы
- UUID
- Списки и множества
- Пользовательские объекты (через JSON)
- BigDecimal для валюты
- Пользовательские value классы

**Резюме:**

TypeConverters — это методы для преобразования пользовательских типов в типы, совместимые с базой данных, и обратно. Используйте аннотацию @TypeConverter для методов преобразования и @TypeConverters для регистрации. Можно применять на уровне базы данных, сущности, DAO или свойства. Распространённые случаи: Date, Enum, List, JSON объекты, UUID.
