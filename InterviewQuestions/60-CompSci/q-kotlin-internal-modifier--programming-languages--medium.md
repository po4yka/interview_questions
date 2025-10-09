---
tags:
  - access-modifiers
  - internal
  - kotlin
  - module
  - programming-languages
  - visibility
difficulty: medium
status: reviewed
---

# Что известно про internal?

**English**: What is known about internal?

## Answer

`internal` is an access modifier for **module-level visibility**.

**Module** is usually a compilation unit: one Gradle module, Maven module, or IntelliJ module.

Code with `internal` will **not be visible in other modules**, even if the class or function is public.

Useful for hiding implementation between layers or when using multi-module architecture.

**Key Features:**

- - Visible **within the same module**
- - **Not visible** in other modules
- 🏗️ **Module** = Gradle/Maven/IntelliJ module
- 🔒 **Encapsulation** between modules

**Example:**

```kotlin
// Module: :app
internal class DatabaseHelper {
    fun connect() = println("Connected")
}

internal fun log(message: String) {
    println("[LOG] $message")
}

class UserRepository {
    private val db = DatabaseHelper()  // - OK - same module

    fun getUser(id: Int) {
        log("Getting user $id")  // - OK - same module
        db.connect()
    }
}
```

**Multi-Module Example:**

```
project/
├── core/  (module)
│   └── NetworkClient.kt
└── app/  (module)
    └── MainActivity.kt
```

**core/NetworkClient.kt:**
```kotlin
// This is visible only within :core module
internal class NetworkClient {
    fun makeRequest(url: String): String {
        return "Response from $url"
    }
}

// Public API of the module
class ApiService {
    private val client = NetworkClient()  // - OK - same module

    fun getData(): String {
        return client.makeRequest("https://api.example.com")
    }
}
```

**app/MainActivity.kt:**
```kotlin
class MainActivity {
    fun loadData() {
        val api = ApiService()  // - OK - public class
        api.getData()

        // - ERROR - NetworkClient is internal to :core module
        val client = NetworkClient()  // Compilation error
    }
}
```

**Comparison with Other Modifiers:**

| Modifier | Visibility | Example |
|----------|-----------|---------|
| **private** | Same file/class only | Implementation details |
| **protected** | Class + subclasses | Inheritance API |
| **internal** | Same module only | Module implementation |
| **public** | Everywhere | Public API |

**Use Cases:**

**1. Hide Implementation:**
```kotlin
// Library module
internal class CacheImpl {
    private val cache = mutableMapOf<String, Any>()

    fun get(key: String): Any? = cache[key]
    fun put(key: String, value: Any) {
        cache[key] = value
    }
}

// Public API
class CacheManager {
    private val cache = CacheImpl()

    fun getData(key: String): Any? = cache.get(key)
    fun saveData(key: String, value: Any) = cache.put(key, value)
}
```

**2. Multi-Module Architecture:**
```kotlin
// :data module
internal interface UserLocalDataSource {
    fun getUser(id: Int): User
}

internal class UserDatabase : UserLocalDataSource {
    override fun getUser(id: Int): User {
        // Database implementation
    }
}

// Public repository
class UserRepository(
    private val localSource: UserLocalDataSource = UserDatabase()
) {
    fun getUser(id: Int): User {
        return localSource.getUser(id)
    }
}
```

**3. Internal Utilities:**
```kotlin
// :utils module
internal object StringUtils {
    fun capitalize(str: String): String {
        return str.replaceFirstChar { it.uppercase() }
    }
}

// Public API uses internal utils
class TextFormatter {
    fun formatName(name: String): String {
        return StringUtils.capitalize(name)  // - OK
    }
}
```

**internal vs private:**

```kotlin
// File: Utils.kt

// private - visible only in this file
private fun helperFunction() = "Helper"

// internal - visible in entire module
internal fun utilityFunction() = "Utility"

class MyClass {
    // private - visible only in this class
    private val secret = "Secret"

    // internal - visible in entire module
    internal val config = "Config"
}
```

**Java Interoperability:**

In Java, `internal` members are visible as **public** but with name mangling:

```kotlin
// Kotlin
internal fun processData() = "Data"
```

```java
// Java - internal becomes public with mangled name
MyClass.processData$module_name();  // Mangled name
```

**Best Practices:**

- **Use internal when:**
- Building multi-module project
- Want to hide implementation from other modules
- Creating library with public API

- **Don't use internal when:**
- Single-module project (use private instead)
- Need visibility across modules (use public)
- Targeting Java consumers (use public or private)

**Summary:**

- `internal` = **module-level visibility**
- Visible **within module**, invisible outside
- **Module** = Gradle/Maven/IntelliJ module
- Useful for **multi-module architecture**
- **Encapsulates** implementation details

## Ответ

`internal` — это уровень доступа для всего модуля. Модуль — это обычно компиляционная единица: одна сборка Gradle, Maven или IntelliJ.

Код с `internal` не будет виден в других модулях, даже если класс или функция — public. Полезно для сокрытия реализации между слоями или при использовании многомодульной архитектуры.

