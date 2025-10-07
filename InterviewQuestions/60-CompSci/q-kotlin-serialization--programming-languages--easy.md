---
tags:
  - data-persistence
  - json
  - kotlin
  - programming-languages
  - serialization
difficulty: easy
status: draft
---

# Что такое сериализация?

**English**: What is serialization?

## Answer

**Serialization** is the process of converting an object into a byte stream to save its state or transmit it over a network.

This is needed so you can store objects in files, databases, or transfer them between different application components or even different applications.

**Why Serialization:**

- 💾 **Save state** to files or database
- 🌐 **Network transfer** between client and server
- 📦 **Cache** objects for faster access
- 🔄 **Deep copy** of objects
- ⏸️ **Pause/Resume** application state

**Common Formats:**

**1. JSON** (most common for APIs):
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

**2. Binary** (Java Serializable):
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

**3. Kotlin Serialization** (recommended):
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

**4. Parcelable** (Android):
```kotlin
import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class Message(
    val id: String,
    val text: String,
    val timestamp: Long
) : Parcelable

// Pass between Activities/Fragments
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
            Json.decodeFromString(cacheFile.readText())
        } else null
    }
}
```

**Comparison of Serialization Methods:**

| Method | Format | Speed | Size | Use Case |
|--------|--------|-------|------|----------|
| **JSON** | Text | Medium | Large | APIs, config files |
| **Kotlin Serialization** | Various | Fast | Optimized | Modern Kotlin apps |
| **Java Serializable** | Binary | Slow | Large | Legacy Java apps |
| **Parcelable** | Binary | Fast | Small | Android IPC |
| **Protocol Buffers** | Binary | Very Fast | Very Small | High performance |

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

- **Serialization**: Object → Byte stream
- **Deserialization**: Byte stream → Object
- **Purpose**: Save, transmit, cache objects
- **Common formats**: JSON, Binary, Parcelable
- **Kotlin**: Use `@Serializable` annotation

## Ответ

Сериализация – это процесс преобразования объекта в поток байтов для сохранения его состояния или передачи его через сеть. Это нужно, чтобы можно было хранить объекты в файлы, базы данных или передавать их между разными компонентами приложения или даже разными приложениями.

