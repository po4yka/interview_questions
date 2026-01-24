---
'---id': kotlin-150
title: Serialization Basics / Основы сериализации
aliases:
- Data Serialization
- JSON Serialization
- Serialization
- Сериализация
topic: kotlin
subtopics:
- serialization
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-serialization
- q-kotlin-extension-functions--kotlin--medium
created: 2025-10-15
updated: 2025-11-09
tags:
- data-formats
- difficulty/medium
- json
- kotlin
- serialization
anki_cards:
- slug: q-serialization-basics--kotlin--medium-0-en
  language: en
  anki_id: 1768326280705
  synced_at: '2026-01-23T17:03:50.581041'
- slug: q-serialization-basics--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326280729
  synced_at: '2026-01-23T17:03:50.583155'
---
# Вопрос (RU)

> Что такое сериализация в Kotlin и в программировании в целом?

# Question (EN)

> What is serialization in Kotlin and programming in general?

## Ответ (RU)

Сериализация — это процесс преобразования объектов в памяти (и их состояния) в формат, пригодный для хранения или передачи (например, JSON, ProtoBuf, CBOR), а десериализация — обратное преобразование этого формата обратно в объекты.

В Kotlin часто используется библиотека `kotlinx.serialization`, которая генерирует сериализаторы на этапе компиляции и поддерживает несколько форматов через отдельные модули. См. также [[c-kotlin]].

### Настройка
```kotlin
// build.gradle.kts
plugins {
    kotlin("plugin.serialization") version "1.9.0"
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
    // Для других форматов (например, CBOR, ProtoBuf) добавляются отдельные артефакты:
    // implementation("org.jetbrains.kotlinx:kotlinx-serialization-cbor:<version>")
    // implementation("org.jetbrains.kotlinx:kotlinx-serialization-protobuf:<version>")
}
```

### Базовое Использование
```kotlin
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class User(
    val name: String,
    val age: Int,
    val email: String? = null
)

// Сериализация
val user = User("Alice", 25, "alice@example.com")
val json = Json.encodeToString(user)
// {"name":"Alice","age":25,"email":"alice@example.com"}

// Десериализация
val user2 = Json.decodeFromString<User>(json)
```

### Кастомные Сериализаторы
```kotlin
import kotlinx.serialization.KSerializer
import kotlinx.serialization.descriptors.PrimitiveKind
import kotlinx.serialization.descriptors.PrimitiveSerialDescriptor
import kotlinx.serialization.descriptors.SerialDescriptor
import kotlinx.serialization.encoding.Decoder
import kotlinx.serialization.encoding.Encoder

// Пример: кастомный сериализатор для java.util.Date
object DateAsLongSerializer : KSerializer<java.util.Date> {
    override val descriptor: SerialDescriptor =
        PrimitiveSerialDescriptor("DateAsLong", PrimitiveKind.LONG)

    override fun serialize(encoder: Encoder, value: java.util.Date) {
        encoder.encodeLong(value.time)
    }

    override fun deserialize(decoder: Decoder): java.util.Date {
        return java.util.Date(decoder.decodeLong())
    }
}

@Serializable
data class Event(
    @Serializable(with = DateAsLongSerializer::class)
    val timestamp: java.util.Date
)
```

### Конфигурация JSON
```kotlin
val json = Json {
    prettyPrint = true
    ignoreUnknownKeys = true
    encodeDefaults = false
    isLenient = true
}
```

## Answer (EN)

Serialization is the process of converting in-memory objects (and their state) into a format that can be stored or transmitted (e.g., JSON, ProtoBuf, CBOR), and deserialization is converting that data back into objects.

In Kotlin, a common solution is the `kotlinx.serialization` library, which provides compile-time generated serializers and supports multiple formats via separate modules.

### Setup
```kotlin
// build.gradle.kts
plugins {
    kotlin("plugin.serialization") version "1.9.0"
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
    // For other formats (e.g., CBOR, ProtoBuf), add corresponding artifacts:
    // implementation("org.jetbrains.kotlinx:kotlinx-serialization-cbor:<version>")
    // implementation("org.jetbrains.kotlinx:kotlinx-serialization-protobuf:<version>")
}
```

### Basic Usage
```kotlin
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class User(
    val name: String,
    val age: Int,
    val email: String? = null
)

// Serialize
val user = User("Alice", 25, "alice@example.com")
val json = Json.encodeToString(user)
// {"name":"Alice","age":25,"email":"alice@example.com"}

// Deserialize
val user2 = Json.decodeFromString<User>(json)
```

### Custom Serializers
```kotlin
import kotlinx.serialization.KSerializer
import kotlinx.serialization.descriptors.PrimitiveKind
import kotlinx.serialization.descriptors.PrimitiveSerialDescriptor
import kotlinx.serialization.descriptors.SerialDescriptor
import kotlinx.serialization.encoding.Decoder
import kotlinx.serialization.encoding.Encoder

// Example: custom serializer for java.util.Date
object DateAsLongSerializer : KSerializer<java.util.Date> {
    override val descriptor: SerialDescriptor =
        PrimitiveSerialDescriptor("DateAsLong", PrimitiveKind.LONG)

    override fun serialize(encoder: Encoder, value: java.util.Date) {
        encoder.encodeLong(value.time)
    }

    override fun deserialize(decoder: Decoder): java.util.Date {
        return java.util.Date(decoder.decodeLong())
    }
}

@Serializable
data class Event(
    @Serializable(with = DateAsLongSerializer::class)
    val timestamp: java.util.Date
)
```

### JSON Configuration
```kotlin
val json = Json {
    prettyPrint = true
    ignoreUnknownKeys = true
    encodeDefaults = false
    isLenient = true
}
```

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от механизмов сериализации в Java?
- Когда вы бы использовали этот подход на практике?
- Каковы распространенные подводные камни при использовании `kotlinx.serialization`?

## Follow-ups

- What are the key differences between this and Java serialization mechanisms?
- When would you use this in practice?
- What are common pitfalls to avoid when using `kotlinx.serialization`?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-suspend-cancellable-coroutine--kotlin--hard]]
- [[q-kotlin-extension-functions--kotlin--medium]]

## Related Questions

- [[q-suspend-cancellable-coroutine--kotlin--hard]]
- [[q-kotlin-extension-functions--kotlin--medium]]
