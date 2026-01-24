---
anki_cards:
- slug: q-base64-hexformat-api--kotlin--easy-0-en
  language: en
  anki_id: 1769173407908
  synced_at: '2026-01-23T17:03:51.344834'
- slug: q-base64-hexformat-api--kotlin--easy-0-ru
  language: ru
  anki_id: 1769173407934
  synced_at: '2026-01-23T17:03:51.345954'
---
# Вопрос (RU)
> Объясните API Base64 и HexFormat в Kotlin. Как кодировать и декодировать данные?

# Question (EN)
> Explain the Base64 and HexFormat APIs in Kotlin. How do you encode and decode data?

## Ответ (RU)

**Стабильно с Kotlin 2.2**

Kotlin предоставляет встроенные мультиплатформенные API для Base64 и шестнадцатеричного кодирования в пакете `kotlin.io.encoding`.

---

### Base64

```kotlin
import kotlin.io.encoding.Base64
import kotlin.io.encoding.ExperimentalEncodingApi

@OptIn(ExperimentalEncodingApi::class)
fun main() {
    val data = "Hello, Kotlin!".encodeToByteArray()

    // Кодирование
    val encoded = Base64.encode(data)
    println(encoded)  // SGVsbG8sIEtvdGxpbiE=

    // Декодирование
    val decoded = Base64.decode(encoded)
    println(decoded.decodeToString())  // Hello, Kotlin!
}
```

---

### Варианты Base64

```kotlin
@OptIn(ExperimentalEncodingApi::class)
fun base64Variants() {
    val data = "Hello?World!".encodeToByteArray()

    // Стандартный Base64 (RFC 4648)
    val standard = Base64.Default.encode(data)
    println(standard)  // SGVsbG8/V29ybGQh

    // URL-safe Base64 (для URL и имен файлов)
    val urlSafe = Base64.UrlSafe.encode(data)
    println(urlSafe)  // SGVsbG8_V29ybGQh

    // MIME Base64 (с переносами строк каждые 76 символов)
    val mime = Base64.Mime.encode(data)
}
```

---

### HexFormat

```kotlin
@OptIn(ExperimentalStdlibApi::class)
fun hexFormatExample() {
    val bytes = byteArrayOf(0x48, 0x65, 0x6C, 0x6C, 0x6F)

    // Кодирование в hex
    val hex = bytes.toHexString()
    println(hex)  // 48656c6c6f

    // Декодирование из hex
    val decoded = "48656c6c6f".hexToByteArray()
    println(decoded.decodeToString())  // Hello
}
```

---

### Настройка HexFormat

```kotlin
@OptIn(ExperimentalStdlibApi::class)
fun customHexFormat() {
    val bytes = byteArrayOf(0x12, 0x34, 0xAB.toByte(), 0xCD.toByte())

    // Верхний регистр
    val upper = bytes.toHexString(HexFormat.UpperCase)
    println(upper)  // 1234ABCD

    // С разделителями
    val format = HexFormat {
        upperCase = true
        bytes {
            byteSeparator = " "
            bytesPerGroup = 2
            groupSeparator = "-"
        }
    }
    println(bytes.toHexString(format))  // 12 34-AB CD

    // Префикс для чисел
    val numberFormat = HexFormat {
        upperCase = true
        number {
            prefix = "0x"
        }
    }
    println(255.toHexString(numberFormat))  // 0xFF
}
```

---

### Практические примеры

**Хеширование и кодирование:**

```kotlin
import java.security.MessageDigest

@OptIn(ExperimentalStdlibApi::class)
fun hashToHex(input: String): String {
    val md = MessageDigest.getInstance("SHA-256")
    val hash = md.digest(input.encodeToByteArray())
    return hash.toHexString()
}

println(hashToHex("password"))
// 5e884898da28047d55d7c5...
```

**Работа с токенами:**

```kotlin
@OptIn(ExperimentalEncodingApi::class)
fun encodeToken(userId: Int, timestamp: Long): String {
    val data = "$userId:$timestamp".encodeToByteArray()
    return Base64.UrlSafe.encode(data)
}

fun decodeToken(token: String): Pair<Int, Long>? {
    return try {
        val data = Base64.UrlSafe.decode(token).decodeToString()
        val parts = data.split(":")
        parts[0].toInt() to parts[1].toLong()
    } catch (e: Exception) {
        null
    }
}
```

**Бинарные данные в JSON:**

```kotlin
@OptIn(ExperimentalEncodingApi::class)
@Serializable
data class BinaryPayload(
    val name: String,
    @Serializable(with = Base64Serializer::class)
    val data: ByteArray
)

object Base64Serializer : KSerializer<ByteArray> {
    override val descriptor = PrimitiveSerialDescriptor("ByteArray", PrimitiveKind.STRING)

    override fun serialize(encoder: Encoder, value: ByteArray) {
        encoder.encodeString(Base64.encode(value))
    }

    override fun deserialize(decoder: Decoder): ByteArray {
        return Base64.decode(decoder.decodeString())
    }
}
```

---

### Работа с потоками

```kotlin
@OptIn(ExperimentalEncodingApi::class)
fun streamEncode() {
    val input = "Large data...".encodeToByteArray()

    // Инкрементальное кодирование
    val encoder = Base64.Default
    val output = ByteArrayOutputStream()

    // Кодируем порциями
    encoder.encodeToAppendable(input, output)
}
```

---

### Сравнение с Java API

| Аспект | Java | Kotlin |
|--------|------|--------|
| Base64 | `java.util.Base64` | `kotlin.io.encoding.Base64` |
| Hex | Сторонние библиотеки | `HexFormat` встроен |
| Платформы | Только JVM | Все (JVM, JS, Native, Wasm) |
| API | Encoder/Decoder объекты | Extension functions |

---

## Answer (EN)

**Stable since Kotlin 2.2**

Kotlin provides built-in multiplatform APIs for Base64 and hexadecimal encoding in the `kotlin.io.encoding` package.

---

### Base64

```kotlin
import kotlin.io.encoding.Base64
import kotlin.io.encoding.ExperimentalEncodingApi

@OptIn(ExperimentalEncodingApi::class)
fun main() {
    val data = "Hello, Kotlin!".encodeToByteArray()

    // Encoding
    val encoded = Base64.encode(data)
    println(encoded)  // SGVsbG8sIEtvdGxpbiE=

    // Decoding
    val decoded = Base64.decode(encoded)
    println(decoded.decodeToString())  // Hello, Kotlin!
}
```

---

### Base64 Variants

```kotlin
@OptIn(ExperimentalEncodingApi::class)
fun base64Variants() {
    val data = "Hello?World!".encodeToByteArray()

    // Standard Base64 (RFC 4648)
    val standard = Base64.Default.encode(data)
    println(standard)  // SGVsbG8/V29ybGQh

    // URL-safe Base64 (for URLs and filenames)
    val urlSafe = Base64.UrlSafe.encode(data)
    println(urlSafe)  // SGVsbG8_V29ybGQh

    // MIME Base64 (with line breaks every 76 chars)
    val mime = Base64.Mime.encode(data)
}
```

---

### HexFormat

```kotlin
@OptIn(ExperimentalStdlibApi::class)
fun hexFormatExample() {
    val bytes = byteArrayOf(0x48, 0x65, 0x6C, 0x6C, 0x6F)

    // Encode to hex
    val hex = bytes.toHexString()
    println(hex)  // 48656c6c6f

    // Decode from hex
    val decoded = "48656c6c6f".hexToByteArray()
    println(decoded.decodeToString())  // Hello
}
```

---

### Custom HexFormat

```kotlin
@OptIn(ExperimentalStdlibApi::class)
fun customHexFormat() {
    val bytes = byteArrayOf(0x12, 0x34, 0xAB.toByte(), 0xCD.toByte())

    // Upper case
    val upper = bytes.toHexString(HexFormat.UpperCase)
    println(upper)  // 1234ABCD

    // With separators
    val format = HexFormat {
        upperCase = true
        bytes {
            byteSeparator = " "
            bytesPerGroup = 2
            groupSeparator = "-"
        }
    }
    println(bytes.toHexString(format))  // 12 34-AB CD

    // Prefix for numbers
    val numberFormat = HexFormat {
        upperCase = true
        number {
            prefix = "0x"
        }
    }
    println(255.toHexString(numberFormat))  // 0xFF
}
```

---

### Practical Examples

**Hashing and Encoding:**

```kotlin
import java.security.MessageDigest

@OptIn(ExperimentalStdlibApi::class)
fun hashToHex(input: String): String {
    val md = MessageDigest.getInstance("SHA-256")
    val hash = md.digest(input.encodeToByteArray())
    return hash.toHexString()
}

println(hashToHex("password"))
// 5e884898da28047d55d7c5...
```

**Token Handling:**

```kotlin
@OptIn(ExperimentalEncodingApi::class)
fun encodeToken(userId: Int, timestamp: Long): String {
    val data = "$userId:$timestamp".encodeToByteArray()
    return Base64.UrlSafe.encode(data)
}

fun decodeToken(token: String): Pair<Int, Long>? {
    return try {
        val data = Base64.UrlSafe.decode(token).decodeToString()
        val parts = data.split(":")
        parts[0].toInt() to parts[1].toLong()
    } catch (e: Exception) {
        null
    }
}
```

**Binary Data in JSON:**

```kotlin
@OptIn(ExperimentalEncodingApi::class)
@Serializable
data class BinaryPayload(
    val name: String,
    @Serializable(with = Base64Serializer::class)
    val data: ByteArray
)

object Base64Serializer : KSerializer<ByteArray> {
    override val descriptor = PrimitiveSerialDescriptor("ByteArray", PrimitiveKind.STRING)

    override fun serialize(encoder: Encoder, value: ByteArray) {
        encoder.encodeString(Base64.encode(value))
    }

    override fun deserialize(decoder: Decoder): ByteArray {
        return Base64.decode(decoder.decodeString())
    }
}
```

---

### Stream Processing

```kotlin
@OptIn(ExperimentalEncodingApi::class)
fun streamEncode() {
    val input = "Large data...".encodeToByteArray()

    // Incremental encoding
    val encoder = Base64.Default
    val output = ByteArrayOutputStream()

    // Encode in chunks
    encoder.encodeToAppendable(input, output)
}
```

---

### Comparison with Java API

| Aspect | Java | Kotlin |
|--------|------|--------|
| Base64 | `java.util.Base64` | `kotlin.io.encoding.Base64` |
| Hex | Third-party libraries | `HexFormat` built-in |
| Platforms | JVM only | All (JVM, JS, Native, Wasm) |
| API | Encoder/Decoder objects | Extension functions |

---

## Follow-ups

- What is the difference between Base64.Default and Base64.UrlSafe?
- How do you handle invalid Base64 input?
- Can you use Base64 with streaming data?

## Related Questions

- [[q-kotlin-serialization--kotlin--easy]]

## References

- https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.io.encoding/-base64/
- https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-hex-format/
