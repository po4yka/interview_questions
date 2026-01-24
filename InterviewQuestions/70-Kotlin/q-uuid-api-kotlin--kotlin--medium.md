---
anki_cards:
- slug: q-uuid-api-kotlin--kotlin--medium-0-en
  language: en
  anki_id: 1769173376387
  synced_at: '2026-01-23T17:03:50.476881'
- slug: q-uuid-api-kotlin--kotlin--medium-0-ru
  language: ru
  anki_id: 1769173376409
  synced_at: '2026-01-23T17:03:50.478835'
---
# Вопрос (RU)
> Объясните Kotlin UUID API. Как генерировать и работать с UUID в Kotlin Multiplatform?

# Question (EN)
> Explain the Kotlin UUID API. How do you generate and work with UUIDs in Kotlin Multiplatform?

## Ответ (RU)

**Введено в Kotlin 2.0, стабильно с 2.1**

Пакет `kotlin.uuid` предоставляет кроссплатформенный API для работы с UUID (Universally Unique Identifier). Это мультиплатформенная альтернатива `java.util.UUID`.

---

### Класс Uuid

```kotlin
import kotlin.uuid.Uuid

// Генерация случайного UUID (v4)
val randomUuid = Uuid.random()
println(randomUuid)  // 550e8400-e29b-41d4-a716-446655440000

// Парсинг строки
val parsed = Uuid.parse("550e8400-e29b-41d4-a716-446655440000")

// Создание из байтов
val bytes = ByteArray(16) { it.toByte() }
val fromBytes = Uuid.fromByteArray(bytes)
```

---

### Основные методы

```kotlin
val uuid = Uuid.random()

// Преобразование в строку
val str = uuid.toString()  // "550e8400-e29b-41d4-a716-446655440000"

// Преобразование в байты
val bytes = uuid.toByteArray()  // ByteArray размером 16

// Получение компонентов
val mostSigBits = uuid.toLongs().first   // старшие 64 бита
val leastSigBits = uuid.toLongs().second // младшие 64 бита

// Сравнение
val uuid1 = Uuid.random()
val uuid2 = Uuid.parse(uuid1.toString())
println(uuid1 == uuid2)  // true
```

---

### Форматы строк

```kotlin
val uuid = Uuid.random()

// Стандартный формат (с дефисами)
println(uuid.toString())
// 550e8400-e29b-41d4-a716-446655440000

// Формат без дефисов
println(uuid.toHexString())
// 550e8400e29b41d4a716446655440000
```

---

### Практические примеры

**Генерация идентификаторов:**

```kotlin
data class Entity(
    val id: Uuid = Uuid.random(),
    val name: String
)

fun createEntity(name: String): Entity {
    return Entity(name = name)
}

val entity = createEntity("Product")
println("Created: ${entity.id}")
```

**Работа с базой данных:**

```kotlin
interface Repository {
    suspend fun save(id: Uuid, data: String)
    suspend fun findById(id: Uuid): String?
}

class InMemoryRepository : Repository {
    private val storage = mutableMapOf<Uuid, String>()

    override suspend fun save(id: Uuid, data: String) {
        storage[id] = data
    }

    override suspend fun findById(id: Uuid): String? {
        return storage[id]
    }
}
```

**API запросы:**

```kotlin
data class Request(
    val requestId: Uuid = Uuid.random(),
    val timestamp: Long,
    val payload: String
)

suspend fun sendRequest(payload: String): Response {
    val request = Request(
        timestamp = System.currentTimeMillis(),
        payload = payload
    )
    println("Sending request: ${request.requestId}")
    return api.send(request)
}
```

---

### Мультиплатформенность

```kotlin
// common
expect fun platformUuid(): Uuid

// jvm
actual fun platformUuid(): Uuid {
    return Uuid.random()  // использует SecureRandom
}

// js
actual fun platformUuid(): Uuid {
    return Uuid.random()  // использует crypto.getRandomValues
}

// native
actual fun platformUuid(): Uuid {
    return Uuid.random()  // использует platform-specific CSPRNG
}
```

---

### UUID версии (Kotlin 2.3+)

В Kotlin 2.3 добавлена поддержка UUID v7 (time-ordered):

```kotlin
// UUID v4 (случайный) - по умолчанию
val v4 = Uuid.random()

// UUID v7 (time-ordered) - Kotlin 2.3+
// val v7 = Uuid.randomV7()  // отсортирован по времени создания

// Проверка версии
println(v4.version)  // 4
```

---

### Сериализация

```kotlin
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class User(
    @Serializable(with = UuidSerializer::class)
    val id: Uuid,
    val name: String
)

// Кастомный сериализатор
object UuidSerializer : KSerializer<Uuid> {
    override val descriptor = PrimitiveSerialDescriptor("Uuid", PrimitiveKind.STRING)

    override fun serialize(encoder: Encoder, value: Uuid) {
        encoder.encodeString(value.toString())
    }

    override fun deserialize(decoder: Decoder): Uuid {
        return Uuid.parse(decoder.decodeString())
    }
}
```

---

### Сравнение с java.util.UUID

| Аспект | `java.util.UUID` | `kotlin.uuid.Uuid` |
|--------|------------------|-------------------|
| Платформы | Только JVM | Все (JVM, JS, Native, Wasm) |
| Создание | `UUID.randomUUID()` | `Uuid.random()` |
| Парсинг | `UUID.fromString()` | `Uuid.parse()` |
| Типобезопасность | Java class | Kotlin value class |
| Null-safety | Nullable | Non-null |

---

## Answer (EN)

**Introduced in Kotlin 2.0, stable since 2.1**

The `kotlin.uuid` package provides a cross-platform API for working with UUIDs (Universally Unique Identifiers). It's a multiplatform alternative to `java.util.UUID`.

---

### Uuid Class

```kotlin
import kotlin.uuid.Uuid

// Generate random UUID (v4)
val randomUuid = Uuid.random()
println(randomUuid)  // 550e8400-e29b-41d4-a716-446655440000

// Parse from string
val parsed = Uuid.parse("550e8400-e29b-41d4-a716-446655440000")

// Create from bytes
val bytes = ByteArray(16) { it.toByte() }
val fromBytes = Uuid.fromByteArray(bytes)
```

---

### Core Methods

```kotlin
val uuid = Uuid.random()

// Convert to string
val str = uuid.toString()  // "550e8400-e29b-41d4-a716-446655440000"

// Convert to bytes
val bytes = uuid.toByteArray()  // ByteArray of size 16

// Get components
val mostSigBits = uuid.toLongs().first   // upper 64 bits
val leastSigBits = uuid.toLongs().second // lower 64 bits

// Comparison
val uuid1 = Uuid.random()
val uuid2 = Uuid.parse(uuid1.toString())
println(uuid1 == uuid2)  // true
```

---

### String Formats

```kotlin
val uuid = Uuid.random()

// Standard format (with hyphens)
println(uuid.toString())
// 550e8400-e29b-41d4-a716-446655440000

// Format without hyphens
println(uuid.toHexString())
// 550e8400e29b41d4a716446655440000
```

---

### Practical Examples

**Generating Identifiers:**

```kotlin
data class Entity(
    val id: Uuid = Uuid.random(),
    val name: String
)

fun createEntity(name: String): Entity {
    return Entity(name = name)
}

val entity = createEntity("Product")
println("Created: ${entity.id}")
```

**Database Operations:**

```kotlin
interface Repository {
    suspend fun save(id: Uuid, data: String)
    suspend fun findById(id: Uuid): String?
}

class InMemoryRepository : Repository {
    private val storage = mutableMapOf<Uuid, String>()

    override suspend fun save(id: Uuid, data: String) {
        storage[id] = data
    }

    override suspend fun findById(id: Uuid): String? {
        return storage[id]
    }
}
```

**API Requests:**

```kotlin
data class Request(
    val requestId: Uuid = Uuid.random(),
    val timestamp: Long,
    val payload: String
)

suspend fun sendRequest(payload: String): Response {
    val request = Request(
        timestamp = System.currentTimeMillis(),
        payload = payload
    )
    println("Sending request: ${request.requestId}")
    return api.send(request)
}
```

---

### Multiplatform Support

```kotlin
// common
expect fun platformUuid(): Uuid

// jvm
actual fun platformUuid(): Uuid {
    return Uuid.random()  // uses SecureRandom
}

// js
actual fun platformUuid(): Uuid {
    return Uuid.random()  // uses crypto.getRandomValues
}

// native
actual fun platformUuid(): Uuid {
    return Uuid.random()  // uses platform-specific CSPRNG
}
```

---

### UUID Versions (Kotlin 2.3+)

Kotlin 2.3 adds support for UUID v7 (time-ordered):

```kotlin
// UUID v4 (random) - default
val v4 = Uuid.random()

// UUID v7 (time-ordered) - Kotlin 2.3+
// val v7 = Uuid.randomV7()  // sorted by creation time

// Check version
println(v4.version)  // 4
```

---

### Serialization

```kotlin
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class User(
    @Serializable(with = UuidSerializer::class)
    val id: Uuid,
    val name: String
)

// Custom serializer
object UuidSerializer : KSerializer<Uuid> {
    override val descriptor = PrimitiveSerialDescriptor("Uuid", PrimitiveKind.STRING)

    override fun serialize(encoder: Encoder, value: Uuid) {
        encoder.encodeString(value.toString())
    }

    override fun deserialize(decoder: Decoder): Uuid {
        return Uuid.parse(decoder.decodeString())
    }
}
```

---

### Comparison with java.util.UUID

| Aspect | `java.util.UUID` | `kotlin.uuid.Uuid` |
|--------|------------------|-------------------|
| Platforms | JVM only | All (JVM, JS, Native, Wasm) |
| Creation | `UUID.randomUUID()` | `Uuid.random()` |
| Parsing | `UUID.fromString()` | `Uuid.parse()` |
| Type safety | Java class | Kotlin value class |
| Null-safety | Nullable | Non-null |

---

## Follow-ups

- What is the difference between UUID v4 and v7?
- How does Uuid.random() ensure cryptographic security?
- Can you convert between java.util.UUID and kotlin.uuid.Uuid?

## Related Questions

- [[q-kotlin-serialization--kotlin--easy]]
- [[q-value-classes-inline-classes--kotlin--medium]]

## References

- https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.uuid/-uuid/
- https://kotlinlang.org/docs/whatsnew21.html#kotlin-uuid
