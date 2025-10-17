---
id: "20251015082236004"
title: "Serialization Basics / Основы сериализации"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags: - programming-languages
---
# What is serialization?

**English**: What is serialization in Kotlin and programming in general?

## Answer (EN)
Serialization is the process of converting an object into a stream of bytes to save its state or transmit it over a network. This is necessary to:
- Store objects in files or databases
- Transfer objects between different application components
- Send objects over the network between different applications
- Cache object state
- Create deep copies of objects

**Deserialization** is the reverse process - converting a byte stream back into an object.

**Common serialization formats:**
- JSON (JavaScript Object Notation)
- XML (eXtensible Markup Language)
- Protocol Buffers
- Binary formats
- YAML

### Code Examples

**Kotlin Serialization with kotlinx.serialization:**

```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val isActive: Boolean = true
)

fun main() {
    val user = User(
        id = 1,
        name = "Alice",
        email = "alice@example.com",
        isActive = true
    )

    // Serialize to JSON string
    val jsonString = Json.encodeToString(user)
    println("Serialized: $jsonString")
    // {"id":1,"name":"Alice","email":"alice@example.com","isActive":true}

    // Deserialize from JSON string
    val deserializedUser = Json.decodeFromString<User>(jsonString)
    println("Deserialized: $deserializedUser")
    // User(id=1, name=Alice, email=alice@example.com, isActive=true)

    println("Objects equal: ${user == deserializedUser}")  // true
}
```

**Complex nested objects:**

```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
data class Address(
    val street: String,
    val city: String,
    val country: String,
    val zipCode: String
)

@Serializable
data class Order(
    val orderId: String,
    val amount: Double,
    val timestamp: Long
)

@Serializable
data class Customer(
    val id: Int,
    val name: String,
    val email: String,
    val address: Address,
    val orders: List<Order>
)

fun main() {
    val customer = Customer(
        id = 42,
        name = "Bob Smith",
        email = "bob@example.com",
        address = Address(
            street = "123 Main St",
            city = "New York",
            country = "USA",
            zipCode = "10001"
        ),
        orders = listOf(
            Order("ORD-001", 99.99, System.currentTimeMillis()),
            Order("ORD-002", 149.50, System.currentTimeMillis())
        )
    )

    // Serialize with pretty printing
    val json = Json { prettyPrint = true }
    val jsonString = json.encodeToString(customer)
    println(jsonString)

    // Deserialize
    val restoredCustomer = json.decodeFromString<Customer>(jsonString)
    println("\nRestored customer: ${restoredCustomer.name}")
    println("Number of orders: ${restoredCustomer.orders.size}")
}
```

**Custom serialization with @SerialName:**

```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
data class ApiUser(
    @SerialName("user_id")
    val id: Int,

    @SerialName("full_name")
    val name: String,

    @SerialName("email_address")
    val email: String,

    @SerialName("is_verified")
    val isVerified: Boolean = false
)

fun main() {
    val user = ApiUser(
        id = 1,
        name = "Alice Johnson",
        email = "alice@example.com",
        isVerified = true
    )

    val jsonString = Json.encodeToString(user)
    println(jsonString)
    // {"user_id":1,"full_name":"Alice Johnson","email_address":"alice@example.com","is_verified":true}

    // Works with snake_case API responses
    val apiResponse = """
        {
            "user_id": 2,
            "full_name": "Bob Williams",
            "email_address": "bob@example.com",
            "is_verified": false
        }
    """.trimIndent()

    val deserializedUser = Json.decodeFromString<ApiUser>(apiResponse)
    println(deserializedUser)
}
```

**Handling nullable and optional fields:**

```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
data class Product(
    val id: Int,
    val name: String,
    val description: String? = null,  // Nullable field
    val price: Double,
    val discount: Double? = null,     // Nullable field
    val tags: List<String> = emptyList()  // Default value
)

fun main() {
    // Product with all fields
    val product1 = Product(
        id = 1,
        name = "Laptop",
        description = "High-performance laptop",
        price = 999.99,
        discount = 50.0,
        tags = listOf("electronics", "computers")
    )

    // Product with minimal fields
    val product2 = Product(
        id = 2,
        name = "Mouse",
        price = 29.99
    )

    val json = Json {
        prettyPrint = true
        encodeDefaults = false  // Don't include default values
    }

    println("Product 1:")
    println(json.encodeToString(product1))

    println("\nProduct 2:")
    println(json.encodeToString(product2))

    // Deserialize from incomplete JSON
    val jsonString = """{"id": 3, "name": "Keyboard", "price": 79.99}"""
    val product3 = Json.decodeFromString<Product>(jsonString)
    println("\nProduct 3: $product3")
}
```

**Serialization to file:**

```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*
import java.io.File

@Serializable
data class AppConfig(
    val appName: String,
    val version: String,
    val apiUrl: String,
    val timeout: Int,
    val features: Map<String, Boolean>
)

fun saveConfig(config: AppConfig, filename: String) {
    val json = Json { prettyPrint = true }
    val jsonString = json.encodeToString(config)
    File(filename).writeText(jsonString)
    println("Config saved to $filename")
}

fun loadConfig(filename: String): AppConfig {
    val jsonString = File(filename).readText()
    return Json.decodeFromString<AppConfig>(jsonString)
}

fun main() {
    val config = AppConfig(
        appName = "MyApp",
        version = "1.0.0",
        apiUrl = "https://api.example.com",
        timeout = 30,
        features = mapOf(
            "dark_mode" to true,
            "notifications" to false,
            "analytics" to true
        )
    )

    // Save to file
    saveConfig(config, "config.json")

    // Load from file
    val loadedConfig = loadConfig("config.json")
    println("Loaded config: $loadedConfig")
    println("Dark mode enabled: ${loadedConfig.features["dark_mode"]}")
}
```

**Polymorphic serialization with sealed classes:**

```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
sealed class Response {
    @Serializable
    @SerialName("success")
    data class Success(val data: String, val timestamp: Long) : Response()

    @Serializable
    @SerialName("error")
    data class Error(val message: String, val code: Int) : Response()

    @Serializable
    @SerialName("loading")
    object Loading : Response()
}

fun main() {
    val json = Json {
        prettyPrint = true
        classDiscriminator = "type"
    }

    val responses = listOf<Response>(
        Response.Success("Data loaded", System.currentTimeMillis()),
        Response.Error("Not found", 404),
        Response.Loading
    )

    responses.forEach { response ->
        val jsonString = json.encodeToString(response)
        println(jsonString)
        println()

        // Deserialize back
        val restored = json.decodeFromString<Response>(jsonString)
        when (restored) {
            is Response.Success -> println("Success: ${restored.data}")
            is Response.Error -> println("Error ${restored.code}: ${restored.message}")
            Response.Loading -> println("Loading...")
        }
        println("---")
    }
}
```

**List and collection serialization:**

```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
data class Task(
    val id: Int,
    val title: String,
    val completed: Boolean
)

fun main() {
    val tasks = listOf(
        Task(1, "Buy groceries", false),
        Task(2, "Write code", true),
        Task(3, "Read book", false)
    )

    // Serialize list
    val jsonString = Json.encodeToString(tasks)
    println("Serialized list:")
    println(jsonString)

    // Deserialize list
    val restoredTasks = Json.decodeFromString<List<Task>>(jsonString)
    println("\nRestored tasks:")
    restoredTasks.forEach { task ->
        val status = if (task.completed) "" else ""
        println("$status ${task.title}")
    }

    // Serialize map
    val taskMap = tasks.associateBy { it.id }
    val mapJson = Json.encodeToString(taskMap)
    println("\nSerialized map:")
    println(mapJson)
}
```

---

## Ответ (RU)
# Вопрос (RU)
Что такое сериализация

## Ответ (RU)
Сериализация – это процесс преобразования объекта в поток байтов для сохранения его состояния или передачи его через сеть. Это нужно, чтобы можно было хранить объекты в файлы, базы данных или передавать их между разными компонентами приложения или даже разными приложениями.
