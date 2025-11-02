---
id: kotlin-150
title: "Serialization Basics / Основы сериализации"
aliases: [Serialization, Data Serialization, JSON Serialization, Сериализация]
topic: kotlin
subtopics: [serialization]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-delegation--programming-languages--easy, q-suspend-cancellable-coroutine--kotlin--hard, q-kotlin-extension-functions--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - kotlin
  - serialization
  - json
  - data-formats
  - difficulty/medium
---
# What is serialization?

**English**: What is serialization in Kotlin and programming in general?

## Answer (EN)

Kotlin serialization converts objects to formats like JSON, Protocol Buffers, or CBOR for storage or network transmission.

### Setup
```kotlin
// build.gradle.kts
plugins {
    kotlin("plugin.serialization") version "1.9.0"
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
}
```

### Basic Usage
```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*

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
@Serializable
data class Date(
    @Serializable(with = DateSerializer::class)
    val timestamp: java.util.Date
)

object DateSerializer : KSerializer<java.util.Date> {
    override fun serialize(encoder: Encoder, value: java.util.Date) {
        encoder.encodeLong(value.time)
    }
    
    override fun deserialize(decoder: Decoder): java.util.Date {
        return java.util.Date(decoder.decodeLong())
    }
}
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

---
---

## Ответ (RU)

Kotlin serialization преобразует объекты в форматы как JSON, Protocol Buffers или CBOR для хранения или передачи по сети.

### Настройка
```kotlin
// build.gradle.kts
plugins {
    kotlin("plugin.serialization") version "1.9.0"
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
}
```

### Базовое использование
```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*

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

### Кастомные сериализаторы
```kotlin
@Serializable
data class Date(
    @Serializable(with = DateSerializer::class)
    val timestamp: java.util.Date
)

object DateSerializer : KSerializer<java.util.Date> {
    override fun serialize(encoder: Encoder, value: java.util.Date) {
        encoder.encodeLong(value.time)
    }
    
    override fun deserialize(decoder: Decoder): java.util.Date {
        return java.util.Date(decoder.decodeLong())
    }
}
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

---

## Related Questions

- [[q-kotlin-delegation--programming-languages--easy]]
- [[q-suspend-cancellable-coroutine--kotlin--hard]]
- [[q-kotlin-extension-functions--kotlin--medium]]

