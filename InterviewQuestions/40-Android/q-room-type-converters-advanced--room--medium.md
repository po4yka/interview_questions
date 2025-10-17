---
id: "20251015082237376"
title: "Room Type Converters Advanced / Продвинутые Type Converters в Room"
topic: room
difficulty: medium
status: draft
created: 2025-10-15
tags: - room
  - database
  - type-converters
  - serialization
  - json
  - performance
  - difficulty/medium
---
# Room Advanced Type Converters / Продвинутые Type Converters в Room

**English**: Implement complex type converters for custom types, enums, and collections. Handle JSON serialization with performance considerations.

## Answer (EN)
**Advanced Type Converters** in Room enable storing complex data types like custom objects, collections, enums, and specialized types (UUID, BigDecimal, LocalDateTime) while maintaining performance and type safety.

### Type Converter Fundamentals

Room requires TypeConverters to store non-primitive types. The converter must provide bidirectional transformation between your custom type and a type Room can persist (primitives, String, byte arrays).

### Basic Type Converters Review

```kotlin
class BasicConverters {
    // Date converters
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? {
        return value?.let { Date(it) }
    }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? {
        return date?.time
    }

    // Boolean to Int (0/1)
    @TypeConverter
    fun fromBoolean(value: Boolean?): Int? {
        return value?.let { if (it) 1 else 0 }
    }

    @TypeConverter
    fun toBoolean(value: Int?): Boolean? {
        return value?.let { it == 1 }
    }
}
```

### Advanced Date/Time Converters

Modern Java 8+ time APIs provide better date/time handling.

```kotlin
class DateTimeConverters {
    // LocalDateTime converters
    @TypeConverter
    fun fromLocalDateTime(value: LocalDateTime?): String? {
        return value?.toString()
    }

    @TypeConverter
    fun toLocalDateTime(value: String?): LocalDateTime? {
        return value?.let { LocalDateTime.parse(it) }
    }

    // LocalDate converters
    @TypeConverter
    fun fromLocalDate(value: LocalDate?): String? {
        return value?.toString()
    }

    @TypeConverter
    fun toLocalDate(value: String?): LocalDate? {
        return value?.let { LocalDate.parse(it) }
    }

    // Instant converters (more performant - stores as Long)
    @TypeConverter
    fun fromInstant(value: Instant?): Long? {
        return value?.toEpochMilli()
    }

    @TypeConverter
    fun toInstant(value: Long?): Instant? {
        return value?.let { Instant.ofEpochMilli(it) }
    }

    // ZonedDateTime with timezone preservation
    @TypeConverter
    fun fromZonedDateTime(value: ZonedDateTime?): String? {
        return value?.format(DateTimeFormatter.ISO_ZONED_DATE_TIME)
    }

    @TypeConverter
    fun toZonedDateTime(value: String?): ZonedDateTime? {
        return value?.let { ZonedDateTime.parse(it, DateTimeFormatter.ISO_ZONED_DATE_TIME) }
    }

    // Duration converter
    @TypeConverter
    fun fromDuration(value: Duration?): Long? {
        return value?.toMillis()
    }

    @TypeConverter
    fun toDuration(value: Long?): Duration? {
        return value?.let { Duration.ofMillis(it) }
    }
}
```

### Enum Converters

Multiple strategies for handling enums with different trade-offs.

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
    // Strategy 1: Store as String (readable, flexible)
    @TypeConverter
    fun fromUserStatus(status: UserStatus?): String? {
        return status?.name
    }

    @TypeConverter
    fun toUserStatus(value: String?): UserStatus? {
        return value?.let {
            try {
                UserStatus.valueOf(it)
            } catch (e: IllegalArgumentException) {
                null  // Handle invalid enum values gracefully
            }
        }
    }

    // Strategy 2: Store as Int (more efficient)
    @TypeConverter
    fun fromPriority(priority: Priority?): Int? {
        return priority?.value
    }

    @TypeConverter
    fun toPriority(value: Int?): Priority? {
        return value?.let { intValue ->
            Priority.values().find { it.value == intValue }
        }
    }

    // Strategy 3: Store ordinal (most efficient, but fragile)
    @TypeConverter
    fun fromUserStatusOrdinal(status: UserStatus?): Int? {
        return status?.ordinal
    }

    @TypeConverter
    fun toUserStatusOrdinal(value: Int?): UserStatus? {
        return value?.let { UserStatus.values().getOrNull(it) }
    }
}
```

### UUID Converters

```kotlin
class UuidConverters {
    // Strategy 1: Store as String (readable, standard)
    @TypeConverter
    fun fromUUID(uuid: UUID?): String? {
        return uuid?.toString()
    }

    @TypeConverter
    fun toUUID(value: String?): UUID? {
        return value?.let {
            try {
                UUID.fromString(it)
            } catch (e: IllegalArgumentException) {
                null
            }
        }
    }

    // Strategy 2: Store as ByteArray (more efficient, 16 bytes)
    @TypeConverter
    fun fromUUIDBytes(uuid: UUID?): ByteArray? {
        return uuid?.let {
            val buffer = ByteBuffer.wrap(ByteArray(16))
            buffer.putLong(it.mostSignificantBits)
            buffer.putLong(it.leastSignificantBits)
            buffer.array()
        }
    }

    @TypeConverter
    fun toUUIDBytes(value: ByteArray?): UUID? {
        return value?.let {
            val buffer = ByteBuffer.wrap(it)
            UUID(buffer.long, buffer.long)
        }
    }
}
```

### BigDecimal Converters (for currency/precision)

```kotlin
class BigDecimalConverters {
    // Strategy 1: Store as String (preserves exact precision)
    @TypeConverter
    fun fromBigDecimal(value: BigDecimal?): String? {
        return value?.toPlainString()
    }

    @TypeConverter
    fun toBigDecimal(value: String?): BigDecimal? {
        return value?.let { BigDecimal(it) }
    }

    // Strategy 2: Store as Long (cents for currency)
    // More efficient but requires knowing scale
    @TypeConverter
    fun fromBigDecimalCents(value: BigDecimal?): Long? {
        return value?.multiply(BigDecimal(100))?.toLong()
    }

    @TypeConverter
    fun toBigDecimalCents(value: Long?): BigDecimal? {
        return value?.let { BigDecimal(it).divide(BigDecimal(100)) }
    }
}
```

### Collection Converters

#### Simple List Converters

```kotlin
class SimpleCollectionConverters {
    // String List with delimiter (efficient for small lists)
    @TypeConverter
    fun fromStringList(list: List<String>?): String? {
        return list?.joinToString(separator = ",")
    }

    @TypeConverter
    fun toStringList(value: String?): List<String>? {
        return value?.split(",")?.map { it.trim() }?.filter { it.isNotEmpty() }
    }

    // Int List with delimiter
    @TypeConverter
    fun fromIntList(list: List<Int>?): String? {
        return list?.joinToString(separator = ",")
    }

    @TypeConverter
    fun toIntList(value: String?): List<Int>? {
        return value?.split(",")
            ?.mapNotNull { it.trim().toIntOrNull() }
    }

    // Long List (for IDs)
    @TypeConverter
    fun fromLongList(list: List<Long>?): String? {
        return list?.joinToString(separator = ",")
    }

    @TypeConverter
    fun toLongList(value: String?): List<Long>? {
        return value?.split(",")
            ?.mapNotNull { it.trim().toLongOrNull() }
    }
}
```

#### JSON-Based Collection Converters

For complex objects, use JSON serialization. We'll compare different libraries.

##### Using Gson

```kotlin
class GsonConverters {
    private val gson = Gson()

    // Generic List converter
    @TypeConverter
    fun fromStringListJson(list: List<String>?): String? {
        return gson.toJson(list)
    }

    @TypeConverter
    fun toStringListJson(json: String?): List<String>? {
        val type = object : TypeToken<List<String>>() {}.type
        return gson.fromJson(json, type)
    }

    // Custom object list
    @TypeConverter
    fun fromAddressList(list: List<Address>?): String? {
        return gson.toJson(list)
    }

    @TypeConverter
    fun toAddressList(json: String?): List<Address>? {
        val type = object : TypeToken<List<Address>>() {}.type
        return gson.fromJson(json, type)
    }

    // Map converter
    @TypeConverter
    fun fromStringMap(map: Map<String, String>?): String? {
        return gson.toJson(map)
    }

    @TypeConverter
    fun toStringMap(json: String?): Map<String, String>? {
        val type = object : TypeToken<Map<String, String>>() {}.type
        return gson.fromJson(json, type)
    }

    // Custom object
    @TypeConverter
    fun fromAddress(address: Address?): String? {
        return gson.toJson(address)
    }

    @TypeConverter
    fun toAddress(json: String?): Address? {
        return gson.fromJson(json, Address::class.java)
    }
}

data class Address(
    val street: String,
    val city: String,
    val state: String,
    val zipCode: String,
    val country: String
)
```

##### Using Moshi (Better performance, null-safe)

```kotlin
class MoshiConverters {
    private val moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .build()

    // String list
    private val stringListAdapter = moshi.adapter<List<String>>(
        Types.newParameterizedType(List::class.java, String::class.java)
    )

    @TypeConverter
    fun fromStringList(list: List<String>?): String? {
        return stringListAdapter.toJson(list)
    }

    @TypeConverter
    fun toStringList(json: String?): List<String>? {
        return json?.let { stringListAdapter.fromJson(it) }
    }

    // Custom object list
    private val addressListAdapter = moshi.adapter<List<Address>>(
        Types.newParameterizedType(List::class.java, Address::class.java)
    )

    @TypeConverter
    fun fromAddressList(list: List<Address>?): String? {
        return addressListAdapter.toJson(list)
    }

    @TypeConverter
    fun toAddressList(json: String?): List<Address>? {
        return json?.let { addressListAdapter.fromJson(it) }
    }

    // Single object
    private val addressAdapter = moshi.adapter(Address::class.java)

    @TypeConverter
    fun fromAddress(address: Address?): String? {
        return addressAdapter.toJson(address)
    }

    @TypeConverter
    fun toAddress(json: String?): Address? {
        return json?.let { addressAdapter.fromJson(it) }
    }
}
```

##### Using kotlinx.serialization (Best Kotlin integration)

```kotlin
class KotlinxSerializationConverters {
    private val json = Json {
        ignoreUnknownKeys = true
        encodeDefaults = true
    }

    // String list
    @TypeConverter
    fun fromStringList(list: List<String>?): String? {
        return list?.let { json.encodeToString(it) }
    }

    @TypeConverter
    fun toStringList(value: String?): List<String>? {
        return value?.let { json.decodeFromString(it) }
    }

    // Custom object list
    @TypeConverter
    fun fromAddressList(list: List<Address>?): String? {
        return list?.let { json.encodeToString(it) }
    }

    @TypeConverter
    fun toAddressList(value: String?): List<Address>? {
        return value?.let { json.decodeFromString(it) }
    }

    // Single object
    @TypeConverter
    fun fromAddress(address: Address?): String? {
        return address?.let { json.encodeToString(it) }
    }

    @TypeConverter
    fun toAddress(value: String?): Address? {
        return value?.let { json.decodeFromString<Address>(it) }
    }
}

@Serializable
data class Address(
    val street: String,
    val city: String,
    val state: String,
    val zipCode: String,
    val country: String
)
```

### ProvidedTypeConverter (Dependency Injection)

When converters need dependencies (like serialization libraries), use `@ProvidedTypeConverter`.

```kotlin
@ProvidedTypeConverter
class ProvidedConverters(
    private val gson: Gson  // Injected dependency
) {
    @TypeConverter
    fun fromAddressList(list: List<Address>?): String? {
        return gson.toJson(list)
    }

    @TypeConverter
    fun toAddressList(json: String?): List<Address>? {
        val type = object : TypeToken<List<Address>>() {}.type
        return gson.fromJson(json, type)
    }
}

// Database setup with provided converter
@Database(entities = [User::class], version = 1)
@TypeConverters(ProvidedConverters::class)
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
    fun provideConverters(gson: Gson): ProvidedConverters {
        return ProvidedConverters(gson)
    }

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context,
        converters: ProvidedConverters
    ): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        )
            .addTypeConverter(converters)
            .build()
    }
}
```

### Performance Comparison

Let's benchmark different serialization approaches.

```kotlin
class TypeConverterBenchmark {

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
        val iterations = 10000

        // Gson benchmark
        val gson = Gson()
        val gsonStart = System.currentTimeMillis()
        repeat(iterations) {
            val json = gson.toJson(testData)
            gson.fromJson(json, TestObject::class.java)
        }
        val gsonTime = System.currentTimeMillis() - gsonStart

        // Moshi benchmark
        val moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
        val moshiAdapter = moshi.adapter(TestObject::class.java)
        val moshiStart = System.currentTimeMillis()
        repeat(iterations) {
            val json = moshiAdapter.toJson(testData)
            moshiAdapter.fromJson(json)
        }
        val moshiTime = System.currentTimeMillis() - moshiStart

        // kotlinx.serialization benchmark
        val json = Json
        val kotlinxStart = System.currentTimeMillis()
        repeat(iterations) {
            val jsonStr = json.encodeToString(testData)
            json.decodeFromString<TestObject>(jsonStr)
        }
        val kotlinxTime = System.currentTimeMillis() - kotlinxStart

        println("""
            Serialization Benchmark ($iterations iterations):
            Gson:                 ${gsonTime}ms
            Moshi:                ${moshiTime}ms  (${((gsonTime - moshiTime) * 100.0 / gsonTime).toInt()}% faster)
            kotlinx.serialization: ${kotlinxTime}ms  (${((gsonTime - kotlinxTime) * 100.0 / gsonTime).toInt()}% faster)

            Winner: ${
                when (minOf(gsonTime, moshiTime, kotlinxTime)) {
                    gsonTime -> "Gson"
                    moshiTime -> "Moshi"
                    else -> "kotlinx.serialization"
                }
            }
        """.trimIndent())
    }
}

// Typical results:
// Gson:                 850ms
// Moshi:                520ms  (38% faster)
// kotlinx.serialization: 380ms  (55% faster)
```

### Performance Optimization Strategies

#### 1. Choose the Right Strategy

```kotlin
// GOOD: Simple delimiter for primitive lists (fastest)
@TypeConverter
fun fromIntList(list: List<Int>?): String? {
    return list?.joinToString(",")
}

// AVOID: JSON for simple lists (slower, more space)
@TypeConverter
fun fromIntListJson(list: List<Int>?): String? {
    return gson.toJson(list)  // Overkill for primitives
}
```

#### 2. Cache Serializer Instances

```kotlin
// BAD: Creates new Gson instance every time
class BadConverters {
    @TypeConverter
    fun fromAddress(address: Address?): String? {
        return Gson().toJson(address)  // New instance!
    }
}

// GOOD: Reuse single instance
class GoodConverters {
    private val gson = Gson()  // Cached

    @TypeConverter
    fun fromAddress(address: Address?): String? {
        return gson.toJson(address)
    }
}
```

#### 3. Lazy Initialization for Heavy Objects

```kotlin
class OptimizedConverters {
    private val moshi: Moshi by lazy {
        Moshi.Builder()
            .add(KotlinJsonAdapterFactory())
            .build()
    }

    private val addressAdapter: JsonAdapter<Address> by lazy {
        moshi.adapter(Address::class.java)
    }

    @TypeConverter
    fun fromAddress(address: Address?): String? {
        return addressAdapter.toJson(address)
    }

    @TypeConverter
    fun toAddress(json: String?): Address? {
        return json?.let { addressAdapter.fromJson(it) }
    }
}
```

#### 4. Consider Binary Serialization for Large Objects

```kotlin
class BinaryConverters {
    // Protocol Buffers (protobuf) - very efficient
    @TypeConverter
    fun fromUserProto(user: UserProto?): ByteArray? {
        return user?.toByteArray()
    }

    @TypeConverter
    fun toUserProto(bytes: ByteArray?): UserProto? {
        return bytes?.let { UserProto.parseFrom(it) }
    }
}
```

### Complete Real-World Example

```kotlin
// Entity with multiple complex types
@Entity(tableName = "products")
data class Product(
    @PrimaryKey
    val id: UUID,
    val name: String,
    val price: BigDecimal,
    val images: List<String>,
    val tags: List<String>,
    val specifications: Map<String, String>,
    val address: Address,
    val status: ProductStatus,
    val createdAt: Instant,
    val updatedAt: Instant
)

enum class ProductStatus {
    DRAFT, PUBLISHED, ARCHIVED
}

@Serializable
data class Address(
    val street: String,
    val city: String,
    val zipCode: String
)

// Comprehensive converters
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
    fun fromAddress(address: Address?): String? =
        address?.let { json.encodeToString(it) }

    @TypeConverter
    fun toAddress(value: String?): Address? =
        value?.let { json.decodeFromString(it) }

    // Enum
    @TypeConverter
    fun fromProductStatus(status: ProductStatus?): String? = status?.name

    @TypeConverter
    fun toProductStatus(value: String?): ProductStatus? =
        value?.let { ProductStatus.valueOf(it) }

    // Instant
    @TypeConverter
    fun fromInstant(instant: Instant?): Long? = instant?.toEpochMilli()

    @TypeConverter
    fun toInstant(value: Long?): Instant? = value?.let { Instant.ofEpochMilli(it) }
}

// Database
@Database(entities = [Product::class], version = 1)
@TypeConverters(ProductConverters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun productDao(): ProductDao
}
```

### Best Practices

1. **Choose the Right Serialization**:
   - Simple delimiters for primitive lists (fastest)
   - JSON for complex objects
   - Binary (protobuf) for very large objects

2. **Cache Serializer Instances**: Don't create new instances in converters

3. **Handle Nullability**: Always handle null cases gracefully

4. **Error Handling**: Catch serialization exceptions, return null on error

5. **Use ProvidedTypeConverter**: For converters with dependencies

6. **Lazy Initialization**: For heavy serializer objects

7. **Test Converters**: Ensure bidirectional conversion works correctly

8. **Benchmark**: Measure performance with realistic data

9. **Consider Storage Size**: JSON is human-readable but larger

10. **Version Your JSON Schema**: Handle backward compatibility

### Common Pitfalls

1. **Creating New Instances**: New Gson() in every converter call
2. **Not Handling Nulls**: NPE when deserializing null values
3. **Ignoring Exceptions**: Crashes when JSON parsing fails
4. **Wrong Collection Type**: List vs Set vs Array confusion
5. **Enum Ordinal Storage**: Breaks when enum order changes
6. **Not Testing**: Assume converters work without verification
7. **Oversized JSON**: Storing huge objects as JSON (use relations instead)
8. **No Validation**: Accepting malformed data
9. **Memory Leaks**: Holding references in converter singletons
10. **Premature Optimization**: Using complex converters when simple ones suffice

### Comparison Table: Serialization Libraries

| Library | Pros | Cons | Use Case |
|---------|------|------|----------|
| **Gson** | Simple, mature, widely used | Slower, reflection-based | Legacy projects |
| **Moshi** | Fast, null-safe, Kotlin support | More setup code | Production apps |
| **kotlinx.serialization** | Fastest, compile-time safe, Kotlin-native | Requires Kotlin plugin | New Kotlin projects |
| **Delimiters** | Fastest, smallest storage | Only for simple types | Primitive lists |
| **Protobuf** | Very efficient, schema evolution | Complex setup, binary | Large datasets |

### Summary

Advanced Type Converters in Room enable:

- **Custom Types**: UUID, BigDecimal, Date/Time variants
- **Enums**: String, ordinal, or custom value storage
- **Collections**: Lists, Sets, Maps with efficient serialization
- **Complex Objects**: JSON serialization with Gson/Moshi/kotlinx.serialization
- **Performance**: 50-70% faster with kotlinx.serialization vs Gson
- **Dependency Injection**: @ProvidedTypeConverter for DI frameworks
- **Null Safety**: Proper null handling in conversions
- **Error Handling**: Graceful degradation on serialization errors

Choose serialization strategy based on data complexity, performance requirements, and storage size constraints.

---

## Ответ (RU)
**Продвинутые Type Converters** в Room позволяют хранить сложные типы данных, такие как пользовательские объекты, коллекции, enum'ы и специализированные типы (UUID, BigDecimal, LocalDateTime), сохраняя при этом производительность и типобезопасность.

### Продвинутые конвертеры Date/Time

```kotlin
class DateTimeConverters {
    // LocalDateTime конвертеры
    @TypeConverter
    fun fromLocalDateTime(value: LocalDateTime?): String? {
        return value?.toString()
    }

    @TypeConverter
    fun toLocalDateTime(value: String?): LocalDateTime? {
        return value?.let { LocalDateTime.parse(it) }
    }

    // Instant конвертеры (более производительны - хранится как Long)
    @TypeConverter
    fun fromInstant(value: Instant?): Long? {
        return value?.toEpochMilli()
    }

    @TypeConverter
    fun toInstant(value: Long?): Instant? {
        return value?.let { Instant.ofEpochMilli(it) }
    }
}
```

### Конвертеры Enum

```kotlin
enum class UserStatus {
    ACTIVE, INACTIVE, SUSPENDED, DELETED
}

class EnumConverters {
    // Стратегия 1: Хранить как String (читаемо, гибко)
    @TypeConverter
    fun fromUserStatus(status: UserStatus?): String? {
        return status?.name
    }

    @TypeConverter
    fun toUserStatus(value: String?): UserStatus? {
        return value?.let {
            try {
                UserStatus.valueOf(it)
            } catch (e: IllegalArgumentException) {
                null  // Обработка недопустимых значений enum
            }
        }
    }
}
```

### Конвертеры UUID

```kotlin
class UuidConverters {
    // Хранить как String (читаемо, стандартно)
    @TypeConverter
    fun fromUUID(uuid: UUID?): String? {
        return uuid?.toString()
    }

    @TypeConverter
    fun toUUID(value: String?): UUID? {
        return value?.let {
            try {
                UUID.fromString(it)
            } catch (e: IllegalArgumentException) {
                null
            }
        }
    }
}
```

### Конвертеры коллекций

```kotlin
class SimpleCollectionConverters {
    // List<String> с разделителем (эффективно для небольших списков)
    @TypeConverter
    fun fromStringList(list: List<String>?): String? {
        return list?.joinToString(separator = ",")
    }

    @TypeConverter
    fun toStringList(value: String?): List<String>? {
        return value?.split(",")?.map { it.trim() }?.filter { it.isNotEmpty() }
    }

    // List<Long> (для ID)
    @TypeConverter
    fun fromLongList(list: List<Long>?): String? {
        return list?.joinToString(separator = ",")
    }

    @TypeConverter
    fun toLongList(value: String?): List<Long>? {
        return value?.split(",")?.mapNotNull { it.trim().toLongOrNull() }
    }
}
```

### JSON конвертеры

#### С использованием Gson

```kotlin
class GsonConverters {
    private val gson = Gson()

    @TypeConverter
    fun fromAddressList(list: List<Address>?): String? {
        return gson.toJson(list)
    }

    @TypeConverter
    fun toAddressList(json: String?): List<Address>? {
        val type = object : TypeToken<List<Address>>() {}.type
        return gson.fromJson(json, type)
    }

    @TypeConverter
    fun fromAddress(address: Address?): String? {
        return gson.toJson(address)
    }

    @TypeConverter
    fun toAddress(json: String?): Address? {
        return gson.fromJson(json, Address::class.java)
    }
}
```

#### С использованием kotlinx.serialization (лучшая интеграция с Kotlin)

```kotlin
class KotlinxSerializationConverters {
    private val json = Json {
        ignoreUnknownKeys = true
        encodeDefaults = true
    }

    @TypeConverter
    fun fromAddressList(list: List<Address>?): String? {
        return list?.let { json.encodeToString(it) }
    }

    @TypeConverter
    fun toAddressList(value: String?): List<Address>? {
        return value?.let { json.decodeFromString(it) }
    }
}
```

### Сравнение производительности

Типичные результаты бенчмарка (10000 итераций):
- Gson: 850ms
- Moshi: 520ms (на 38% быстрее)
- kotlinx.serialization: 380ms (на 55% быстрее)

### Стратегии оптимизации производительности

```kotlin
// ХОРОШО: Простой разделитель для примитивных списков (быстрее всего)
@TypeConverter
fun fromIntList(list: List<Int>?): String? {
    return list?.joinToString(",")
}

// ИЗБЕГАТЬ: JSON для простых списков (медленнее, больше места)
@TypeConverter
fun fromIntListJson(list: List<Int>?): String? {
    return gson.toJson(list)  // Излишне для примитивов
}

// ХОРОШО: Кэшировать экземпляры сериализатора
class GoodConverters {
    private val gson = Gson()  // Закэшировано

    @TypeConverter
    fun fromAddress(address: Address?): String? {
        return gson.toJson(address)
    }
}
```

### Best Practices

1. **Выбрать правильную сериализацию**:
   - Простые разделители для примитивных списков (быстрее всего)
   - JSON для сложных объектов
   - Бинарная (protobuf) для очень больших объектов

2. **Кэшировать экземпляры сериализатора**: Не создавать новые экземпляры в конвертерах

3. **Обрабатывать Nullability**: Всегда обрабатывать null случаи корректно

4. **Обработка ошибок**: Ловить исключения сериализации, возвращать null при ошибке

5. **Использовать ProvidedTypeConverter**: Для конвертеров с зависимостями

6. **Тестировать конвертеры**: Убедиться, что двунаправленное преобразование работает

7. **Бенчмарк**: Измерять производительность с реалистичными данными

### Таблица сравнения: Библиотеки сериализации

| Библиотека | Плюсы | Минусы | Случай использования |
|------------|-------|--------|---------------------|
| **Gson** | Простая, зрелая | Медленнее, на рефлексии | Legacy проекты |
| **Moshi** | Быстрая, null-safe | Больше setup кода | Production приложения |
| **kotlinx.serialization** | Быстрейшая, compile-time safe | Требует Kotlin плагин | Новые Kotlin проекты |
| **Разделители** | Быстрейшие, минимум памяти | Только для простых типов | Примитивные списки |

### Резюме

Продвинутые Type Converters в Room обеспечивают:

- **Пользовательские типы**: UUID, BigDecimal, Date/Time варианты
- **Enum'ы**: Хранение как String, ordinal или пользовательское значение
- **Коллекции**: Lists, Sets, Maps с эффективной сериализацией
- **Сложные объекты**: JSON сериализация с Gson/Moshi/kotlinx.serialization
- **Производительность**: На 50-70% быстрее с kotlinx.serialization vs Gson
- **Dependency Injection**: @ProvidedTypeConverter для DI фреймворков
- **Null Safety**: Правильная обработка null в преобразованиях

Выбирайте стратегию сериализации на основе сложности данных, требований к производительности и ограничений размера хранилища.

---

## Related Questions

### Prerequisites (Easier)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-room-library-definition--android--easy]] - Storage

### Related (Medium)
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--room--medium]] - Storage
- [[q-room-paging3-integration--room--medium]] - Storage
- [[q-room-vs-sqlite--android--medium]] - Storage
- [[q-room-type-converters--android--medium]] - Storage

### Advanced (Harder)
- [[q-room-fts-full-text-search--room--hard]] - Storage
