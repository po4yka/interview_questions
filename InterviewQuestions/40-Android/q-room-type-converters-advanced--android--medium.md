---
id: android-220
title: Room Advanced Type Converters / Продвинутые Type Converters в Room
aliases:
- Room Advanced Type Converters
- Продвинутые Type Converters в Room
topic: android
subtopics:
- room
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-room
- q-how-to-animate-adding-removing-items-in-recyclerview--android--medium
- q-tasks-back-stack--android--medium
- q-what-is-broadcastreceiver--android--easy
created: 2025-10-15
updated: 2025-11-10
tags:
- android/room
- difficulty/medium

---

# Вопрос (RU)
> Продвинутые Type Converters в Room

# Question (EN)
> Room Advanced Type Converters

---

## Ответ (RU)
**Продвинутые Type Converters** в Room позволяют хранить сложные типы данных (пользовательские объекты, коллекции, enum-ы, UUID, BigDecimal, типы `java.time`) с сохранением типобезопасности и контролем производительности.

### Базовые принципы

Room может напрямую хранить только ограниченный набор типов. Для остальных нужны `@TypeConverter`-ы, которые:

- Определяют двунаправленное преобразование между кастомным типом и поддерживаемым типом (примитивы, `String`, `ByteArray` и т.п.).
- Должны быть чистыми и детерминированными.

### Базовые конвертеры (обзор)

```kotlin
class BasicConverters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? = date?.time

    @TypeConverter
    fun fromBoolean(value: Boolean?): Int? = value?.let { if (it) 1 else 0 }

    @TypeConverter
    fun toBoolean(value: Int?): Boolean? = value?.let { it == 1 }
}
```

### Продвинутые конвертеры даты/времени

```kotlin
class DateTimeConverters {
    @TypeConverter
    fun fromLocalDateTime(value: LocalDateTime?): String? = value?.toString()

    @TypeConverter
    fun toLocalDateTime(value: String?): LocalDateTime? =
        value?.let { LocalDateTime.parse(it) }

    @TypeConverter
    fun fromLocalDate(value: LocalDate?): String? = value?.toString()

    @TypeConverter
    fun toLocalDate(value: String?): LocalDate? =
        value?.let { LocalDate.parse(it) }

    @TypeConverter
    fun fromInstant(value: Instant?): Long? = value?.toEpochMilli()

    @TypeConverter
    fun toInstant(value: Long?): Instant? =
        value?.let { Instant.ofEpochMilli(it) }

    @TypeConverter
    fun fromZonedDateTime(value: ZonedDateTime?): String? =
        value?.format(DateTimeFormatter.ISO_ZONED_DATE_TIME)

    @TypeConverter
    fun toZonedDateTime(value: String?): ZonedDateTime? =
        value?.let { ZonedDateTime.parse(it, DateTimeFormatter.ISO_ZONED_DATE_TIME) }

    @TypeConverter
    fun fromDuration(value: Duration?): Long? = value?.toMillis()

    @TypeConverter
    fun toDuration(value: Long?): Duration? =
        value?.let { Duration.ofMillis(it) }
}
```

### Конвертеры Enum

```kotlin
enum class UserStatus { ACTIVE, INACTIVE, SUSPENDED, DELETED }

enum class Priority(val value: Int) { LOW(1), MEDIUM(2), HIGH(3), URGENT(4) }

class EnumConverters {
    // Стратегия 1: хранить name (String)
    @TypeConverter
    fun fromUserStatus(status: UserStatus?): String? = status?.name

    @TypeConverter
    fun toUserStatus(value: String?): UserStatus? =
        value?.let {
            try {
                UserStatus.valueOf(it)
            } catch (e: IllegalArgumentException) {
                null
            }
        }

    // Стратегия 2: хранить свой Int-код
    @TypeConverter
    fun fromPriority(priority: Priority?): Int? = priority?.value

    @TypeConverter
    fun toPriority(value: Int?): Priority? =
        value?.let { intValue -> Priority.values().find { it.value == intValue } }

    // Стратегия 3: ordinal (компактно, но ломается при смене порядка)
    @TypeConverter
    fun fromUserStatusOrdinal(status: UserStatus?): Int? = status?.ordinal

    @TypeConverter
    fun toUserStatusOrdinal(value: Int?): UserStatus? =
        value?.let { UserStatus.values().getOrNull(it) }
}
```

### Конвертеры UUID

```kotlin
class UuidConverters {
    @TypeConverter
    fun fromUUID(uuid: UUID?): String? = uuid?.toString()

    @TypeConverter
    fun toUUID(value: String?): UUID? = value?.let {
        try {
            UUID.fromString(it)
        } catch (e: IllegalArgumentException) {
            null
        }
    }

    @TypeConverter
    fun fromUUIDBytes(uuid: UUID?): ByteArray? = uuid?.let {
        val buffer = ByteBuffer.wrap(ByteArray(16))
        buffer.putLong(it.mostSignificantBits)
        buffer.putLong(it.leastSignificantBits)
        buffer.array()
    }

    @TypeConverter
    fun toUUIDBytes(value: ByteArray?): UUID? = value?.let {
        if (it.size != 16) return null
        val buffer = ByteBuffer.wrap(it)
        UUID(buffer.long, buffer.long)
    }
}
```

### BigDecimal

```kotlin
class BigDecimalConverters {
    @TypeConverter
    fun fromBigDecimal(value: BigDecimal?): String? = value?.toPlainString()

    @TypeConverter
    fun toBigDecimal(value: String?): BigDecimal? = value?.let { BigDecimal(it) }

    @TypeConverter
    fun fromBigDecimalCents(value: BigDecimal?): Long? =
        value?.multiply(BigDecimal(100))?.longValueExact()

    @TypeConverter
    fun toBigDecimalCents(value: Long?): BigDecimal? =
        value?.let { BigDecimal(it).divide(BigDecimal(100)) }
}
```

### Коллекции (простые и JSON)

#### Простые списки

```kotlin
class SimpleCollectionConverters {
    // String List через разделитель
    @TypeConverter
    fun fromStringList(list: List<String>?): String? = list?.joinToString(",")

    @TypeConverter
    fun toStringList(value: String?): List<String>? =
        value?.split(",")
            ?.map { it.trim() }
            ?.filter { it.isNotEmpty() }

    // Int List через разделитель
    @TypeConverter
    fun fromIntList(list: List<Int>?): String? = list?.joinToString(",")

    @TypeConverter
    fun toIntList(value: String?): List<Int>? =
        value?.split(",")
            ?.mapNotNull { it.trim().toIntOrNull() }

    // Long List через разделитель
    @TypeConverter
    fun fromLongList(list: List<Long>?): String? = list?.joinToString(",")

    @TypeConverter
    fun toLongList(value: String?): List<Long>? =
        value?.split(",")
            ?.mapNotNull { it.trim().toLongOrNull() }
}
```

#### JSON-базированные конвертеры коллекций и объектов

Для сложных структур удобнее использовать JSON.

##### Gson-конвертеры

```kotlin
class GsonConverters {
    private val gson = Gson()

    // Список строк
    @TypeConverter
    fun fromStringListJson(list: List<String>?): String? = gson.toJson(list)

    @TypeConverter
    fun toStringListJson(json: String?): List<String>? {
        if (json == null) return null
        val type = object : TypeToken<List<String>>() {}.type
        return gson.fromJson(json, type)
    }

    // Список AddressGson
    @TypeConverter
    fun fromAddressList(list: List<AddressGson>?): String? = gson.toJson(list)

    @TypeConverter
    fun toAddressList(json: String?): List<AddressGson>? {
        if (json == null) return null
        val type = object : TypeToken<List<AddressGson>>() {}.type
        return gson.fromJson(json, type)
    }

    // Map<String, String>
    @TypeConverter
    fun fromStringMap(map: Map<String, String>?): String? = gson.toJson(map)

    @TypeConverter
    fun toStringMap(json: String?): Map<String, String>? {
        if (json == null) return null
        val type = object : TypeToken<Map<String, String>>() {}.type
        return gson.fromJson(json, type)
    }

    // Один объект
    @TypeConverter
    fun fromAddress(address: AddressGson?): String? = gson.toJson(address)

    @TypeConverter
    fun toAddress(json: String?): AddressGson? =
        json?.let { gson.fromJson(it, AddressGson::class.java) }
}

data class AddressGson(
    val street: String,
    val city: String,
    val state: String,
    val zipCode: String,
    val country: String
)
```

##### Moshi-конвертеры

```kotlin
class MoshiConverters {
    private val moshi: Moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .build()

    private val stringListAdapter: JsonAdapter<List<String>> =
        moshi.adapter(Types.newParameterizedType(List::class.java, String::class.java))

    @TypeConverter
    fun fromStringList(list: List<String>?): String? = stringListAdapter.toJson(list)

    @TypeConverter
    fun toStringList(json: String?): List<String>? =
        json?.let { stringListAdapter.fromJson(it) }

    private val addressListAdapter: JsonAdapter<List<AddressMoshi>> = moshi.adapter(
        Types.newParameterizedType(List::class.java, AddressMoshi::class.java)
    )

    @TypeConverter
    fun fromAddressList(list: List<AddressMoshi>?): String? = addressListAdapter.toJson(list)

    @TypeConverter
    fun toAddressList(json: String?): List<AddressMoshi>? =
        json?.let { addressListAdapter.fromJson(it) }

    private val addressAdapter: JsonAdapter<AddressMoshi> = moshi.adapter(AddressMoshi::class.java)

    @TypeConverter
    fun fromAddress(address: AddressMoshi?): String? = addressAdapter.toJson(address)

    @TypeConverter
    fun toAddress(json: String?): AddressMoshi? =
        json?.let { addressAdapter.fromJson(it) }
}

data class AddressMoshi(
    val street: String,
    val city: String,
    val state: String,
    val zipCode: String,
    val country: String
)
```

##### kotlinx.serialization-конвертеры

```kotlin
@Serializable
data class AddressKx(
    val street: String,
    val city: String,
    val state: String,
    val zipCode: String,
    val country: String
)

class KotlinxSerializationConverters {
    private val json = Json {
        ignoreUnknownKeys = true
        encodeDefaults = true
    }

    // Список строк
    @TypeConverter
    fun fromStringList(list: List<String>?): String? =
        list?.let { json.encodeToString(ListSerializer(String.serializer()), it) }

    @TypeConverter
    fun toStringList(value: String?): List<String>? =
        value?.let { json.decodeFromString(ListSerializer(String.serializer()), it) }

    // Список AddressKx
    @TypeConverter
    fun fromAddressList(list: List<AddressKx>?): String? =
        list?.let { json.encodeToString(ListSerializer(AddressKx.serializer()), it) }

    @TypeConverter
    fun toAddressList(value: String?): List<AddressKx>? =
        value?.let { json.decodeFromString(ListSerializer(AddressKx.serializer()), it) }

    // Один AddressKx
    @TypeConverter
    fun fromAddress(address: AddressKx?): String? =
        address?.let { json.encodeToString(AddressKx.serializer(), it) }

    @TypeConverter
    fun toAddress(value: String?): AddressKx? =
        value?.let { json.decodeFromString(AddressKx.serializer(), it) }
}
```

### @ProvidedTypeConverter и DI

Когда конвертер зависит от внешних экземпляров (например, `Gson`, `Moshi`, `Json`), используйте `@ProvidedTypeConverter` и регистрируйте через `.addTypeConverter(...)`.

```kotlin
@ProvidedTypeConverter
class ProvidedConverters(
    private val gson: Gson
) {
    @TypeConverter
    fun fromAddressList(list: List<AddressGson>?): String? = gson.toJson(list)

    @TypeConverter
    fun toAddressList(json: String?): List<AddressGson>? {
        if (json == null) return null
        val type = object : TypeToken<List<AddressGson>>() {}.type
        return gson.fromJson(json, type)
    }
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun create(context: Context, gson: Gson): AppDatabase {
            return Room.databaseBuilder(
                context,
                AppDatabase::class.java,
                "app_database"
            )
                .addTypeConverter(ProvidedConverters(gson))
                .build()
        }
    }
}

// Пример с Hilt
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideGson(): Gson = GsonBuilder()
        .setDateFormat("yyyy-MM-dd'T'HH:mm:ss")
        .create()

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context,
        gson: Gson
    ): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        )
            .addTypeConverter(ProvidedConverters(gson))
            .build()
    }
}
```

### Сравнение производительности (пример)

Простой локальный бенчмарк для сравнения сериализаторов; результаты зависят от окружения и набора данных.

```kotlin
class TypeConverterBenchmark {

    @Serializable
    data class TestObject(
        val id: Long,
        val name: String,
        val values: List<Int>,
        val metadata: Map<String, String>
    )

    private val testData = TestObject(
        id = 1L,
        name = "Test",
        values = (1..100).toList(),
        metadata = mapOf("key1" to "value1", "key2" to "value2")
    )

    fun benchmarkSerializers() {
        val iterations = 10_000

        // Gson
        val gson = Gson()
        val gsonStart = System.currentTimeMillis()
        repeat(iterations) {
            val jsonStr = gson.toJson(testData)
            gson.fromJson(jsonStr, TestObject::class.java)
        }
        val gsonTime = System.currentTimeMillis() - gsonStart

        // Moshi
        val moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
        val moshiAdapter = moshi.adapter(TestObject::class.java)
        val moshiStart = System.currentTimeMillis()
        repeat(iterations) {
            val jsonStr = moshiAdapter.toJson(testData)
            moshiAdapter.fromJson(jsonStr)
        }
        val moshiTime = System.currentTimeMillis() - moshiStart

        // kotlinx.serialization
        val json = Json
        val kotlinxStart = System.currentTimeMillis()
        repeat(iterations) {
            val jsonStr = json.encodeToString(testData)
            json.decodeFromString<TestObject>(jsonStr)
        }
        val kotlinxTime = System.currentTimeMillis() - kotlinxStart

        println(
            """
            Serialization Benchmark ($iterations iterations, пример):
            Gson: $gsonTime ms
            Moshi: $moshiTime ms
            kotlinx.serialization: $kotlinxTime ms
            """.trimIndent()
        )
    }
}
```

(На практике производительность зависит от окружения и структуры данных; Moshi и kotlinx.serialization часто быстрее Gson, но всегда измеряйте в своём контексте.)

### Стратегии оптимизации производительности

1. Для простых данных используйте простые представления (разделённые строки, примитивы).
2. Избегайте тяжёлого JSON там, где достаточно примитивов.
3. Переиспользуйте экземпляры сериализаторов (`Gson`, `Moshi`, `Json`).
4. При необходимости используйте ленивую инициализацию тяжёлых объектов.
5. Для больших/сложных структур рассмотрите компактные бинарные форматы (например, protobuf) с генерацией типов и управлением схемой.

Пример:

```kotlin
// Плохо: новый Gson на каждый вызов
class BadConverters {
    @TypeConverter
    fun fromAddress(address: AddressGson?): String? = Gson().toJson(address)
}

// Хорошо: один экземпляр
class GoodConverters {
    private val gson = Gson()

    @TypeConverter
    fun fromAddress(address: AddressGson?): String? = gson.toJson(address)
}
```

#### BinaryConverters (protobuf / бинарные форматы)

```kotlin
class BinaryConverters {
    // Требуется сгенерированный UserProto из protobuf-схемы
    @TypeConverter
    fun fromUserProto(user: UserProto?): ByteArray? = user?.toByteArray()

    @TypeConverter
    fun toUserProto(bytes: ByteArray?): UserProto? =
        bytes?.let { UserProto.parseFrom(it) }
}
```

### Полный пример из реального проекта

```kotlin
@Serializable
data class ProductAddress(
    val street: String,
    val city: String,
    val zipCode: String
)

enum class ProductStatus {
    DRAFT, PUBLISHED, ARCHIVED
}

@Entity(tableName = "products")
data class Product(
    @PrimaryKey
    val id: UUID,
    val name: String,
    val price: BigDecimal,
    val images: List<String>,
    val tags: List<String>,
    val specifications: Map<String, String>,
    val address: ProductAddress,
    val status: ProductStatus,
    val createdAt: Instant,
    val updatedAt: Instant
)

class ProductConverters {
    private val json = Json {
        ignoreUnknownKeys = true
        encodeDefaults = true
    }

    // UUID
    @TypeConverter
    fun fromUUID(uuid: UUID?): String? = uuid?.toString()

    @TypeConverter
    fun toUUID(value: String?): UUID? = value?.let { UUID.fromString(it) }

    // BigDecimal
    @TypeConverter
    fun fromBigDecimal(value: BigDecimal?): String? = value?.toPlainString()

    @TypeConverter
    fun toBigDecimal(value: String?): BigDecimal? = value?.let { BigDecimal(it) }

    // Список строк (простой)
    @TypeConverter
    fun fromStringList(list: List<String>?): String? = list?.joinToString(",")

    @TypeConverter
    fun toStringList(value: String?): List<String>? =
        value?.split(",")?.map { it.trim() }?.filter { it.isNotEmpty() }

    // Map (JSON)
    @TypeConverter
    fun fromStringMap(map: Map<String, String>?): String? =
        map?.let { json.encodeToString(it) }

    @TypeConverter
    fun toStringMap(value: String?): Map<String, String>? =
        value?.let { json.decodeFromString(it) }

    // Address (JSON)
    @TypeConverter
    fun fromAddress(address: ProductAddress?): String? =
        address?.let { json.encodeToString(ProductAddress.serializer(), it) }

    @TypeConverter
    fun toAddress(value: String?): ProductAddress? =
        value?.let { json.decodeFromString(ProductAddress.serializer(), it) }

    // Enum
    @TypeConverter
    fun fromProductStatus(status: ProductStatus?): String? = status?.name

    @TypeConverter
    fun toProductStatus(value: String?): ProductStatus? =
        value?.let { runCatching { ProductStatus.valueOf(it) }.getOrNull() }

    // Instant
    @TypeConverter
    fun fromInstant(instant: Instant?): Long? = instant?.toEpochMilli()

    @TypeConverter
    fun toInstant(value: Long?): Instant? = value?.let { Instant.ofEpochMilli(it) }
}

@Database(entities = [Product::class], version = 1)
@TypeConverters(ProductConverters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun productDao(): ProductDao
}
```

### Лучшие практики

1. Выбирать формат хранения по типу данных:
   - Разделённые строки или примитивы для простых типов.
   - JSON для сложных/вложенных объектов.
   - Бинарные форматы для больших структур при жёстких требованиях к размеру/скорости.
2. Переиспользовать экземпляры сериализаторов.
3. Явно обрабатывать null в обе стороны.
4. Безопасно обрабатывать ошибки (JSON, enum-ы и т.д.), избегая падений.
5. Использовать `@ProvidedTypeConverter` для конвертеров с внешними зависимостями.
6. Держать конвертеры чистыми и без побочных эффектов.
7. Покрывать конвертеры юнит-тестами (round-trip проверки).
8. Мониторить производительность и размер БД; не злоупотреблять JSON там, где лучше нормализованные таблицы.
9. Осторожно относиться к ordinal enum-ов и эволюции схемы.

### Типичные ошибки

1. Создание тяжёлых сериализаторов на каждый вызов.
2. Игнорирование null и получение NPE.
3. Отсутствие обработки некорректного JSON или невалидных enum-значений.
4. Использование JSON для примитивов там, где достаточно простого формата.
5. Хранение ordinal enum-ов и изменение порядка значений.
6. Сохранение огромных объектов в одном JSON вместо нормализации в таблицы.
7. Неконсистентные конвертеры (нет обратимости).
8. Забытые регистрации конвертеров на нужном уровне (БД/DAO/поле).

### Сравнительная таблица: варианты сериализации (высокоуровнево)

| Библиотека / подход    | Плюсы                         | Минусы                               | Типичные случаи использования            |
|------------------------|-------------------------------|--------------------------------------|------------------------------------------|
| Gson                   | Простая, зрелая              | Рефлексия, часто медленнее           | Легаси и существующие проекты            |
| Moshi                  | Дружественна к Kotlin, быстра | Чуть больше настроек                 | Современные продакшн-приложения          |
| kotlinx.serialization  | Компиляторная поддержка, быстра| Требует плагин/аннотации             | Новые Kotlin-first приложения            |
| Разделённые строки     | Очень просто и компактно      | Только для простых типов             | Небольшие коллекции примитивов           |
| Protobuf / бинарные    | Компактно, явная схема        | Доп. инструменты, бинарный формат    | Большие / производительно критичные данные |

### Резюме

Продвинутые Type Converters в Room позволяют:

- Отображать кастомные и сложные типы (UUID, BigDecimal, `java.time`, enum-ы, коллекции).
- Использовать JSON или бинарные форматы там, где это оправдано.
- Интегрироваться с DI через `@ProvidedTypeConverter`.
- Контролировать производительность и размер хранилища за счёт выбора представления.
- Повышать надёжность за счёт явной обработки `null`, ошибок и тестов.

Стратегию хранения нужно выбирать исходя из сложности модели данных, требований к эволюции схемы и измеренной производительности в конкретном приложении.

---

## Answer (EN)
**Advanced Type Converters** in Room enable storing complex data types like custom objects, collections, enums, and specialized types (UUID, BigDecimal, LocalDateTime) while maintaining type safety and appropriate performance.

### Type Converter Fundamentals

Room requires `@TypeConverter`s to store types it cannot directly persist. A converter must provide a bidirectional transformation between your custom type and a type Room can store (primitives, `String`, `ByteArray`, etc.).

- Converters must be pure and deterministic.
- For each custom type you store, you need both `fromX` and `toX` directions.

### Basic Type Converters Review

```kotlin
class BasicConverters {
    // Date converters (legacy java.util.Date)
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? = date?.time

    // Boolean to Int (0/1) — example of custom mapping
    @TypeConverter
    fun fromBoolean(value: Boolean?): Int? = value?.let { if (it) 1 else 0 }

    @TypeConverter
    fun toBoolean(value: Int?): Boolean? = value?.let { it == 1 }
}
```

### Advanced Date/Time Converters

Java 8+ time APIs (`java.time.*`) are preferred for better correctness and clarity.

```kotlin
class DateTimeConverters {
    // LocalDateTime converters (stored as ISO-8601 string)
    @TypeConverter
    fun fromLocalDateTime(value: LocalDateTime?): String? = value?.toString()

    @TypeConverter
    fun toLocalDateTime(value: String?): LocalDateTime? = value?.let { LocalDateTime.parse(it) }

    // LocalDate converters (stored as ISO-8601 string)
    @TypeConverter
    fun fromLocalDate(value: LocalDate?): String? = value?.toString()

    @TypeConverter
    fun toLocalDate(value: String?): LocalDate? = value?.let { LocalDate.parse(it) }

    // Instant converters (stored as epoch millis)
    @TypeConverter
    fun fromInstant(value: Instant?): Long? = value?.toEpochMilli()

    @TypeConverter
    fun toInstant(value: Long?): Instant? = value?.let { Instant.ofEpochMilli(it) }

    // ZonedDateTime with timezone preservation (stored as ISO string)
    @TypeConverter
    fun fromZonedDateTime(value: ZonedDateTime?): String? =
        value?.format(DateTimeFormatter.ISO_ZONED_DATE_TIME)

    @TypeConverter
    fun toZonedDateTime(value: String?): ZonedDateTime? =
        value?.let { ZonedDateTime.parse(it, DateTimeFormatter.ISO_ZONED_DATE_TIME) }

    // Duration converter (stored as millis)
    @TypeConverter
    fun fromDuration(value: Duration?): Long? = value?.toMillis()

    @TypeConverter
    fun toDuration(value: Long?): Duration? = value?.let { Duration.ofMillis(it) }
}
```

### Enum Converters

Multiple strategies exist, with different trade-offs.

```kotlin
enum class UserStatus {
    ACTIVE,
    INACTIVE,
    SUSPENDED,
    DELETED
}

enum class Priority(val value: Int) {
    LOW(1),
    MEDIUM(2),
    HIGH(3),
    URGENT(4)
}

class EnumConverters {
    // Strategy 1: Store as String (readable, stable if names don't change)
    @TypeConverter
    fun fromUserStatus(status: UserStatus?): String? = status?.name

    @TypeConverter
    fun toUserStatus(value: String?): UserStatus? = value?.let {
        try {
            UserStatus.valueOf(it)
        } catch (e: IllegalArgumentException) {
            null // Handle invalid enum values gracefully
        }
    }

    // Strategy 2: Store custom Int code (compact, explicit mapping)
    @TypeConverter
    fun fromPriority(priority: Priority?): Int? = priority?.value

    @TypeConverter
    fun toPriority(value: Int?): Priority? =
        value?.let { intValue -> Priority.values().find { it.value == intValue } }

    // Strategy 3: Store ordinal (compact but fragile when enum order changes)
    @TypeConverter
    fun fromUserStatusOrdinal(status: UserStatus?): Int? = status?.ordinal

    @TypeConverter
    fun toUserStatusOrdinal(value: Int?): UserStatus? =
        value?.let { UserStatus.values().getOrNull(it) }
}
```

### UUID Converters

```kotlin
class UuidConverters {
    // Strategy 1: Store as String (simple, standard)
    @TypeConverter
    fun fromUUID(uuid: UUID?): String? = uuid?.toString()

    @TypeConverter
    fun toUUID(value: String?): UUID? = value?.let {
        try {
            UUID.fromString(it)
        } catch (e: IllegalArgumentException) {
            null
        }
    }

    // Strategy 2: Store as ByteArray (16 bytes, compact)
    @TypeConverter
    fun fromUUIDBytes(uuid: UUID?): ByteArray? = uuid?.let {
        val buffer = ByteBuffer.wrap(ByteArray(16))
        buffer.putLong(it.mostSignificantBits)
        buffer.putLong(it.leastSignificantBits)
        buffer.array()
    }

    @TypeConverter
    fun toUUIDBytes(value: ByteArray?): UUID? = value?.let {
        if (it.size != 16) return null
        val buffer = ByteBuffer.wrap(it)
        UUID(buffer.long, buffer.long)
    }
}
```

### BigDecimal Converters (for currency/precision)

```kotlin
class BigDecimalConverters {
    // Strategy 1: Store as String (preserves exact precision)
    @TypeConverter
    fun fromBigDecimal(value: BigDecimal?): String? = value?.toPlainString()

    @TypeConverter
    fun toBigDecimal(value: String?): BigDecimal? = value?.let { BigDecimal(it) }

    // Strategy 2: Store as Long (e.g., cents) — requires fixed known scale
    @TypeConverter
    fun fromBigDecimalCents(value: BigDecimal?): Long? =
        value?.multiply(BigDecimal(100))?.longValueExact()

    @TypeConverter
    fun toBigDecimalCents(value: Long?): BigDecimal? =
        value?.let { BigDecimal(it).divide(BigDecimal(100)) }
}
```

### Collection Converters

#### Simple `List` Converters

For primitive types and small collections, a delimited string is often sufficient.

```kotlin
class SimpleCollectionConverters {
    // String List with delimiter
    @TypeConverter
    fun fromStringList(list: List<String>?): String? =
        list?.joinToString(separator = ",")

    @TypeConverter
    fun toStringList(value: String?): List<String>? =
        value?.split(",")
            ?.map { it.trim() }
            ?.filter { it.isNotEmpty() }

    // Int List with delimiter
    @TypeConverter
    fun fromIntList(list: List<Int>?): String? =
        list?.joinToString(separator = ",")

    @TypeConverter
    fun toIntList(value: String?): List<Int>? =
        value?.split(",")
            ?.mapNotNull { it.trim().toIntOrNull() }

    // Long List with delimiter
    @TypeConverter
    fun fromLongList(list: List<Long>?): String? =
        list?.joinToString(separator = ",")

    @TypeConverter
    fun toLongList(value: String?): List<Long>? =
        value?.split(",")
            ?.mapNotNull { it.trim().toLongOrNull() }
}
```

#### JSON-Based Collection and Object Converters

For complex objects and nested structures, JSON is more robust.

##### Using Gson

```kotlin
class GsonConverters {
    private val gson = Gson()

    // String list
    @TypeConverter
    fun fromStringListJson(list: List<String>?): String? = gson.toJson(list)

    @TypeConverter
    fun toStringListJson(json: String?): List<String>? {
        if (json == null) return null
        val type = object : TypeToken<List<String>>() {}.type
        return gson.fromJson(json, type)
    }

    // Custom object list
    @TypeConverter
    fun fromAddressList(list: List<AddressGson>?): String? = gson.toJson(list)

    @TypeConverter
    fun toAddressList(json: String?): List<AddressGson>? {
        if (json == null) return null
        val type = object : TypeToken<List<AddressGson>>() {}.type
        return gson.fromJson(json, type)
    }

    // Map converter
    @TypeConverter
    fun fromStringMap(map: Map<String, String>?): String? = gson.toJson(map)

    @TypeConverter
    fun toStringMap(json: String?): Map<String, String>? {
        if (json == null) return null
        val type = object : TypeToken<Map<String, String>>() {}.type
        return gson.fromJson(json, type)
    }

    // Single object
    @TypeConverter
    fun fromAddress(address: AddressGson?): String? = gson.toJson(address)

    @TypeConverter
    fun toAddress(json: String?): AddressGson? =
        json?.let { gson.fromJson(it, AddressGson::class.java) }
}

data class AddressGson(
    val street: String,
    val city: String,
    val state: String,
    val zipCode: String,
    val country: String
)
```

##### Using Moshi

```kotlin
class MoshiConverters {
    private val moshi: Moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .build()

    private val stringListAdapter: JsonAdapter<List<String>> =
        moshi.adapter(Types.newParameterizedType(List::class.java, String::class.java))

    @TypeConverter
    fun fromStringList(list: List<String>?): String? = stringListAdapter.toJson(list)

    @TypeConverter
    fun toStringList(json: String?): List<String>? =
        json?.let { stringListAdapter.fromJson(it) }

    private val addressListAdapter: JsonAdapter<List<AddressMoshi>> = moshi.adapter(
        Types.newParameterizedType(List::class.java, AddressMoshi::class.java)
    )

    @TypeConverter
    fun fromAddressList(list: List<AddressMoshi>?): String? = addressListAdapter.toJson(list)

    @TypeConverter
    fun toAddressList(json: String?): List<AddressMoshi>? =
        json?.let { addressListAdapter.fromJson(it) }

    private val addressAdapter: JsonAdapter<AddressMoshi> = moshi.adapter(AddressMoshi::class.java)

    @TypeConverter
    fun fromAddress(address: AddressMoshi?): String? = addressAdapter.toJson(address)

    @TypeConverter
    fun toAddress(json: String?): AddressMoshi? =
        json?.let { addressAdapter.fromJson(it) }
}

data class AddressMoshi(
    val street: String,
    val city: String,
    val state: String,
    val zipCode: String,
    val country: String
)
```

##### Using kotlinx.serialization

```kotlin
@Serializable
data class AddressKx(
    val street: String,
    val city: String,
    val state: String,
    val zipCode: String,
    val country: String
)

class KotlinxSerializationConverters {
    private val json = Json {
        ignoreUnknownKeys = true
        encodeDefaults = true
    }

    // String list
    @TypeConverter
    fun fromStringList(list: List<String>?): String? =
        list?.let { json.encodeToString(ListSerializer(String.serializer()), it) }

    @TypeConverter
    fun toStringList(value: String?): List<String>? =
        value?.let { json.decodeFromString(ListSerializer(String.serializer()), it) }

    // Custom object list
    @TypeConverter
    fun fromAddressList(list: List<AddressKx>?): String? =
        list?.let { json.encodeToString(ListSerializer(AddressKx.serializer()), it) }

    @TypeConverter
    fun toAddressList(value: String?): List<AddressKx>? =
        value?.let { json.decodeFromString(ListSerializer(AddressKx.serializer()), it) }

    // Single object
    @TypeConverter
    fun fromAddress(address: AddressKx?): String? =
        address?.let { json.encodeToString(AddressKx.serializer(), it) }

    @TypeConverter
    fun toAddress(value: String?): AddressKx? =
        value?.let { json.decodeFromString(AddressKx.serializer(), it) }
}
```

(Above uses explicit serializers for clarity; in real code with the Kotlin serialization plugin, you can also use the inline `encodeToString`/`decodeFromString` reified extensions.)

### ProvidedTypeConverter (Dependency Injection)

When converters depend on external instances (e.g., JSON mappers), use `@ProvidedTypeConverter` and register via `.addTypeConverter(...)`.

```kotlin
@ProvidedTypeConverter
class ProvidedConverters(
    private val gson: Gson
) {
    @TypeConverter
    fun fromAddressList(list: List<AddressGson>?): String? = gson.toJson(list)

    @TypeConverter
    fun toAddressList(json: String?): List<AddressGson>? {
        if (json == null) return null
        val type = object : TypeToken<List<AddressGson>>() {}.type
        return gson.fromJson(json, type)
    }
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        fun create(context: Context, gson: Gson): AppDatabase {
            return Room.databaseBuilder(
                context,
                AppDatabase::class.java,
                "app_database"
            )
                // Provided type converter is registered here; no @TypeConverters on DB needed for it.
                .addTypeConverter(ProvidedConverters(gson))
                .build()
        }
    }
}

// With Hilt
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideGson(): Gson = GsonBuilder()
        .setDateFormat("yyyy-MM-dd'T'HH:mm:ss")
        .create()

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context,
        gson: Gson
    ): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        )
            .addTypeConverter(ProvidedConverters(gson))
            .build()
    }
}
```

### Performance Comparison (Illustrative)

Simple local benchmarks can help compare serializers; results depend on environment and data.

```kotlin
class TypeConverterBenchmark {

    @Serializable
    data class TestObject(
        val id: Long,
        val name: String,
        val values: List<Int>,
        val metadata: Map<String, String>
    )

    private val testData = TestObject(
        id = 1L,
        name = "Test",
        values = (1..100).toList(),
        metadata = mapOf("key1" to "value1", "key2" to "value2")
    )

    fun benchmarkSerializers() {
        val iterations = 10_000

        // Gson
        val gson = Gson()
        val gsonStart = System.currentTimeMillis()
        repeat(iterations) {
            val jsonStr = gson.toJson(testData)
            gson.fromJson(jsonStr, TestObject::class.java)
        }
        val gsonTime = System.currentTimeMillis() - gsonStart

        // Moshi
        val moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
        val moshiAdapter = moshi.adapter(TestObject::class.java)
        val moshiStart = System.currentTimeMillis()
        repeat(iterations) {
            val jsonStr = moshiAdapter.toJson(testData)
            moshiAdapter.fromJson(jsonStr)
        }
        val moshiTime = System.currentTimeMillis() - moshiStart

        // kotlinx.serialization
        val json = Json
        val kotlinxStart = System.currentTimeMillis()
        repeat(iterations) {
            val jsonStr = json.encodeToString(testData)
            json.decodeFromString<TestObject>(jsonStr)
        }
        val kotlinxTime = System.currentTimeMillis() - kotlinxStart

        println(
            """
            Serialization Benchmark ($iterations iterations, example only):
            Gson: $gsonTime ms
            Moshi: $moshiTime ms
            kotlinx.serialization: $kotlinxTime ms
            """.trimIndent()
        )
    }
}
```

(Anecdotally, Moshi and kotlinx.serialization are often faster than Gson, but always measure in your own context.)

### Performance Optimization Strategies

1. Prefer simple encodings (e.g., delimited strings or primitive longs) for simple data.
2. Avoid heavy JSON for trivial types.
3. Reuse serializer instances (e.g., single `Gson`, configured `Moshi`, shared `Json`).
4. Use lazy initialization for heavy objects if needed.
5. Consider compact binary formats (e.g., protobuf) for large/structured payloads, noting they require generated types (like `UserProto`) and schema management.

Example:

```kotlin
// BAD: Creates new Gson instance every time
class BadConverters {
    @TypeConverter
    fun fromAddress(address: AddressGson?): String? = Gson().toJson(address)
}

// GOOD: Reuse single instance
class GoodConverters {
    private val gson = Gson()

    @TypeConverter
    fun fromAddress(address: AddressGson?): String? = gson.toJson(address)
}
```

```kotlin
class BinaryConverters {
    // Requires generated UserProto from protobuf schema
    @TypeConverter
    fun fromUserProto(user: UserProto?): ByteArray? = user?.toByteArray()

    @TypeConverter
    fun toUserProto(bytes: ByteArray?): UserProto? =
        bytes?.let { UserProto.parseFrom(it) }
}
```

### Complete Real-World Example

```kotlin
@Serializable
data class ProductAddress(
    val street: String,
    val city: String,
    val zipCode: String
)

enum class ProductStatus {
    DRAFT, PUBLISHED, ARCHIVED
}

@Entity(tableName = "products")
data class Product(
    @PrimaryKey
    val id: UUID,
    val name: String,
    val price: BigDecimal,
    val images: List<String>,
    val tags: List<String>,
    val specifications: Map<String, String>,
    val address: ProductAddress,
    val status: ProductStatus,
    val createdAt: Instant,
    val updatedAt: Instant
)

class ProductConverters {
    private val json = Json {
        ignoreUnknownKeys = true
        encodeDefaults = true
    }

    // UUID
    @TypeConverter
    fun fromUUID(uuid: UUID?): String? = uuid?.toString()

    @TypeConverter
    fun toUUID(value: String?): UUID? = value?.let { UUID.fromString(it) }

    // BigDecimal
    @TypeConverter
    fun fromBigDecimal(value: BigDecimal?): String? = value?.toPlainString()

    @TypeConverter
    fun toBigDecimal(value: String?): BigDecimal? = value?.let { BigDecimal(it) }

    // String List (simple)
    @TypeConverter
    fun fromStringList(list: List<String>?): String? = list?.joinToString(",")

    @TypeConverter
    fun toStringList(value: String?): List<String>? =
        value?.split(",")?.map { it.trim() }?.filter { it.isNotEmpty() }

    // Map (JSON)
    @TypeConverter
    fun fromStringMap(map: Map<String, String>?): String? =
        map?.let { json.encodeToString(it) }

    @TypeConverter
    fun toStringMap(value: String?): Map<String, String>? =
        value?.let { json.decodeFromString(it) }

    // Address (JSON)
    @TypeConverter
    fun fromAddress(address: ProductAddress?): String? =
        address?.let { json.encodeToString(ProductAddress.serializer(), it) }

    @TypeConverter
    fun toAddress(value: String?): ProductAddress? =
        value?.let { json.decodeFromString(ProductAddress.serializer(), it) }

    // Enum
    @TypeConverter
    fun fromProductStatus(status: ProductStatus?): String? = status?.name

    @TypeConverter
    fun toProductStatus(value: String?): ProductStatus? =
        value?.let { runCatching { ProductStatus.valueOf(it) }.getOrNull() }

    // Instant
    @TypeConverter
    fun fromInstant(instant: Instant?): Long? = instant?.toEpochMilli()

    @TypeConverter
    fun toInstant(value: Long?): Instant? = value?.let { Instant.ofEpochMilli(it) }
}

@Database(entities = [Product::class], version = 1)
@TypeConverters(ProductConverters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun productDao(): ProductDao
}
```

### Best Practices

1. Choose encoding based on data:
   - Delimited strings or primitive columns for simple types.
   - JSON for complex/nested objects.
   - Binary formats for large structured payloads when justified.
2. Cache and reuse serializer instances.
3. Handle nullability explicitly in both directions.
4. Handle errors (e.g., JSON parsing, enum mapping) gracefully instead of crashing.
5. Use `@ProvidedTypeConverter` for converters with external dependencies.
6. Keep converters pure and side-effect free.
7. Add unit tests to verify round-trip conversions.
8. Monitor both performance and storage size; avoid overusing JSON where relational modeling is more appropriate.
9. Be cautious with enum ordinals and schema evolution.

### Common Pitfalls

1. Creating heavy serializer instances for every call.
2. Ignoring nulls and causing NPEs.
3. Not catching malformed JSON or invalid enum values.
4. Using JSON for simple primitives where a simpler representation suffices.
5. Using enum ordinals and later reordering enums.
6. Storing huge objects as JSON instead of normalizing into related tables.
7. Inconsistent converters (non-invertible mappings).
8. Forgetting to register converters at the correct scope.

### Comparison Table: Serialization Options (High-Level)

| Library / Approach | Pros | Cons | Typical Use |
|--------------------|------|------|-------------|
| Gson               | Simple, mature | Reflection-based, often slower | Legacy / existing codebases |
| Moshi              | Kotlin-friendly, efficient | Slightly more setup | Modern production apps |
| kotlinx.serialization | Compile-time, often fast | Requires plugin/annotations | New Kotlin-first apps |
| Delimited strings  | Very small, simple | Only for simple types | Small primitive collections |
| Protobuf / binary  | Compact, explicit schema | Extra tooling, binary | Large / performance-critical data |

### Summary

Advanced Type Converters in Room enable:

- Mapping custom and complex types (UUID, BigDecimal, java.time, enums, collections).
- Using JSON or binary serialization where appropriate.
- Integrating with dependency injection via `@ProvidedTypeConverter`.
- Controlling performance and storage characteristics through careful encoding choices.
- Maintaining robustness via null handling, error handling, and tests.

Choose strategies based on data model complexity, schema evolution needs, and measured performance in your app.

---

## Follow-ups

- [[q-how-to-animate-adding-removing-items-in-recyclerview--android--medium]]
- [[q-tasks-back-stack--android--medium]]
- [[q-what-is-broadcastreceiver--android--easy]]

## References

- [Room Database](https://developer.android.com/training/data-storage/room)

## Related Questions

### Prerequisites / Concepts

- [[c-room]]

### Prerequisites (Easier)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-room-library-definition--android--easy]] - Storage

### Related (Medium)
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--android--medium]] - Storage
- [[q-room-paging3-integration--android--medium]] - Storage
- [[q-room-vs-sqlite--android--medium]] - Storage
- [[q-room-type-converters--android--medium]] - Storage

### Advanced (Harder)
- [[q-room-fts-full-text-search--android--hard]] - Storage
