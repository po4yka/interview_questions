---
id: lang-042
title: "Kotlin Serialization / Сериализация в Kotlin"
aliases: [Kotlin Serialization, Сериализация в Kotlin]
topic: kotlin
subtopics: [serialization, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-functional-interfaces-vs-type-aliases--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [data-persistence, difficulty/easy, json, kotlin, serialization]

---
# Вопрос (RU)
> Что такое сериализация?

# Question (EN)
> What is serialization?

## Ответ (RU)

**Сериализация** — это процесс преобразования объекта в формат, который можно сохранить или передать (обычно в поток байтов или текстовый формат), с возможностью последующего восстановления объекта (десериализация).

Это нужно, чтобы можно было хранить объекты в файлы, базы данных или передавать их между разными компонентами приложения или даже разными приложениями.

**Зачем сериализация:**

- **Сохранение состояния** в файлы или базу данных
- **Передача по сети** между клиентом и сервером
- **Кеширование** объектов для быстрого доступа
- **Глубокое копирование** объектов
- **Пауза/Возобновление** состояния приложения

**Распространённые форматы и подходы:**

**1. JSON** (самый распространённый для API, поддерживается `kotlinx.serialization`):
```kotlin
@Serializable
data class User(val id: Int, val name: String, val email: String)

val user = User(1, "Алиса", "alice@example.com")

// Сериализация в JSON
val json = Json.encodeToString(user)
// {"id":1,"name":"Алиса","email":"alice@example.com"}

// Десериализация из JSON
val userFromJson = Json.decodeFromString<User>(json)
```

**2. Binary** (Java `Serializable` — устаревший, используется для совместимости):
```kotlin
import java.io.*

data class Person(val name: String, val age: Int) : Serializable

// Сериализация
val person = Person("Боб", 30)
val fileOut = FileOutputStream("person.ser")
val objectOut = ObjectOutputStream(fileOut)
objectOut.writeObject(person)
objectOut.close()

// Десериализация
val fileIn = FileInputStream("person.ser")
val objectIn = ObjectInputStream(fileIn)
val loadedPerson = objectIn.readObject() as Person
objectIn.close()
```

**3. Kotlin Serialization (`kotlinx.serialization`)** — рекомендуемая библиотека для Kotlin, поддерживает различные форматы (JSON, CBOR, ProtoBuf и др.):
```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
data class Product(
    val id: Int,
    val name: String,
    val price: Double,
    val inStock: Boolean
)

val product = Product(101, "Ноутбук", 999.99, true)

// В JSON
val jsonString = Json.encodeToString(product)

// Из JSON
val decodedProduct = Json.decodeFromString<Product>(jsonString)
```

**4. `Parcelable`** (Android, для передачи данных между компонентами в рамках одного процесса/приложения):
```kotlin
import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class Message(
    val id: String,
    val text: String,
    val timestamp: Long
) : Parcelable

// Передача между Activities/Fragments в Android
intent.putExtra("message", message)
```

**Случаи использования:**

**Сохранение в файл:**
```kotlin
@Serializable
data class AppSettings(
    val theme: String,
    val fontSize: Int,
    val notifications: Boolean
)

// Сохранение
val settings = AppSettings("dark", 14, true)
File("settings.json").writeText(Json.encodeToString(settings))

// Загрузка
val loadedSettings = Json.decodeFromString<AppSettings>(
    File("settings.json").readText()
)
```

**Сетевой запрос:**
```kotlin
@Serializable
data class LoginRequest(val username: String, val password: String)

@Serializable
data class LoginResponse(val token: String, val userId: Int)

// Сериализация запроса
val request = LoginRequest("alice", "secret123")
val requestBody = Json.encodeToString(request)

// Отправка на сервер и десериализация ответа
val responseJson = sendHttpPost("/api/login", requestBody)
val response = Json.decodeFromString<LoginResponse>(responseJson)
```

**Кеширование:**
```kotlin
object UserCache {
    private val cacheFile = File("user_cache.json")

    fun saveUser(user: User) {
        cacheFile.writeText(Json.encodeToString(user))
    }

    fun loadUser(): User? {
        return if (cacheFile.exists()) {
            Json.decodeFromString<User>(cacheFile.readText())
        } else null
    }
}
```

**Сравнение методов сериализации:**

| Метод | Что это | Формат | Скорость | Размер | Применение |
|-------|---------|--------|----------|--------|------------|
| **JSON** | Формат | Текст | Средняя | Большой | API, конфиг файлы |
| **`kotlinx.serialization`** | Библиотека | Поддерживает разные (JSON, CBOR, ProtoBuf, …) | Быстро | Оптимизированно | Современные Kotlin приложения |
| **Java `Serializable`** | Механизм JVM | Бинарный | Медленно | Большой | Устаревшие Java приложения, совместимость |
| **`Parcelable`** | Android-механизм | Бинарный | Быстро | Маленький | Android IPC внутри приложения |
| **Protocol Buffers** | Формат/IDL | Бинарный | Очень быстро | Очень маленький | Высокая производительность, сетевые протоколы |

**Настройка Kotlin Serialization:**

```kotlin
// build.gradle.kts
plugins {
    kotlin("plugin.serialization") version "1.9.0"
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
}
```

**Резюме:**

- **Сериализация**: Объект → Формат для передачи/хранения (часто поток байтов или текст)
- **Десериализация**: Такой формат → Объект
- **Назначение**: Сохранение, передача, кеширование объектов
- **Распространённые форматы/механизмы**: JSON, бинарные форматы, `Parcelable`, Protocol Buffers
- **В Kotlin**: чаще используйте `kotlinx.serialization` с аннотацией `@Serializable`

## Answer (EN)

**Serialization** is the process of converting an object into a representation that can be stored or transmitted (typically a byte stream or a text format) and later reconstructed back into an object (deserialization).

This is needed so you can store objects in files, databases, or transfer them between different application components or even different applications.

**Why Serialization:**

- **Save state** to files or database
- **Network transfer** between client and server
- **Cache** objects for faster access
- **Deep copy** of objects
- **Pause/Resume** application state

**Common formats and approaches:**

**1. JSON** (most common for APIs, supported by `kotlinx.serialization`):
```kotlin
@Serializable
data class User(val id: Int, val name: String, val email: String)

val user = User(1, "Alice", "alice@example.com")

// Serialize to JSON
val json = Json.encodeToString(user)
// {"id":1,"name":"Alice","email":"alice@example.com"}

// Deserialize from JSON
val userFromJson = Json.decodeFromString<User>(json)
```

**2. Binary** (Java `Serializable` — legacy, mostly for compatibility):
```kotlin
import java.io.*

data class Person(val name: String, val age: Int) : Serializable

// Serialize
val person = Person("Bob", 30)
val fileOut = FileOutputStream("person.ser")
val objectOut = ObjectOutputStream(fileOut)
objectOut.writeObject(person)
objectOut.close()

// Deserialize
val fileIn = FileInputStream("person.ser")
val objectIn = ObjectInputStream(fileIn)
val loadedPerson = objectIn.readObject() as Person
objectIn.close()
```

**3. Kotlin Serialization (`kotlinx.serialization`)** — the recommended Kotlin library, supports multiple formats (JSON, CBOR, ProtoBuf, etc.):
```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
data class Product(
    val id: Int,
    val name: String,
    val price: Double,
    val inStock: Boolean
)

val product = Product(101, "Laptop", 999.99, true)

// To JSON
val jsonString = Json.encodeToString(product)

// From JSON
val decodedProduct = Json.decodeFromString<Product>(jsonString)
```

**4. `Parcelable`** (Android, for passing data between components within the same app/process):
```kotlin
import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class Message(
    val id: String,
    val text: String,
    val timestamp: Long
) : Parcelable

// Pass between Activities/Fragments in Android
intent.putExtra("message", message)
```

**Use Cases:**

**Saving to file:**
```kotlin
@Serializable
data class AppSettings(
    val theme: String,
    val fontSize: Int,
    val notifications: Boolean
)

// Save
val settings = AppSettings("dark", 14, true)
File("settings.json").writeText(Json.encodeToString(settings))

// Load
val loadedSettings = Json.decodeFromString<AppSettings>(
    File("settings.json").readText()
)
```

**Network request:**
```kotlin
@Serializable
data class LoginRequest(val username: String, val password: String)

@Serializable
data class LoginResponse(val token: String, val userId: Int)

// Serialize request
val request = LoginRequest("alice", "secret123")
val requestBody = Json.encodeToString(request)

// Send to server and deserialize response
val responseJson = sendHttpPost("/api/login", requestBody)
val response = Json.decodeFromString<LoginResponse>(responseJson)
```

**Caching:**
```kotlin
object UserCache {
    private val cacheFile = File("user_cache.json")

    fun saveUser(user: User) {
        cacheFile.writeText(Json.encodeToString(user))
    }

    fun loadUser(): User? {
        return if (cacheFile.exists()) {
            Json.decodeFromString<User>(cacheFile.readText())
        } else null
    }
}
```

**Comparison of Serialization Methods:**

| Method | What it is | Format | Speed | Size | Use Case |
|--------|------------|--------|-------|------|----------|
| **JSON** | Data format | Text | Medium | Large | APIs, config files |
| **`kotlinx.serialization`** | Library | Supports various (JSON, CBOR, ProtoBuf, …) | Fast | Optimized | Modern Kotlin apps |
| **Java `Serializable`** | JVM mechanism | Binary | Slow | Large | Legacy Java apps, compatibility |
| **`Parcelable`** | Android mechanism | Binary | Fast | Small | Android IPC within an app |
| **Protocol Buffers** | Format/IDL | Binary | Very Fast | Very Small | High-performance RPC, network protocols |

**Setup Kotlin Serialization:**

```kotlin
// build.gradle.kts
plugins {
    kotlin("plugin.serialization") version "1.9.0"
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
}
```

**Summary:**

- **Serialization**: Object → Representation suitable for transfer/storage (often a byte stream or text)
- **Deserialization**: That representation → Object
- **Purpose**: Save, transmit, cache objects
- **Common formats/mechanisms**: JSON, binary formats, `Parcelable`, Protocol Buffers
- **In Kotlin**: prefer `kotlinx.serialization` with the `@Serializable` annotation

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions

- [[q-kotlin-non-inheritable-class--kotlin--easy]]
- [[q-kotlin-singleton-creation--kotlin--easy]]
- [[q-functional-interfaces-vs-type-aliases--kotlin--medium]]

## Дополнительные Вопросы (RU)
- Каковы ключевые отличия этого подхода от Java?
- Когда вы бы использовали это на практике?
- Какие распространённые подводные камни следует избегать?
## Ссылки (RU)
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
## Связанные Вопросы (RU)