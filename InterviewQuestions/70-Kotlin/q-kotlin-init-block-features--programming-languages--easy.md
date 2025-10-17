---
id: 20251012-12271111133
title: "Kotlin Init Block Features / Возможности блока init в Kotlin"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - constructors
  - init
  - initialization
  - kotlin
  - oop
  - programming-languages
---
# Есть какие-то особенности использования init block?

# Question (EN)
> Are there any features of using init block?

# Вопрос (RU)
> Есть какие-то особенности использования init block?

---

## Answer (EN)

The `init` block in Kotlin has several important features:

### 1. Executes When Creating Class Instance

**Runs during object construction:**
```kotlin
class User(val name: String) {
    init {
        println("User created: $name")
    }
}

val user = User("John")  // Output: User created: John
```

**Used for initialization logic:**
```kotlin
class Person(val name: String, val age: Int) {
    val isAdult: Boolean

    init {
        isAdult = age >= 18
        require(age >= 0) { "Age cannot be negative" }
    }
}
```

### 2. Can Have Multiple Init Blocks

**Executed in declaration order:**
```kotlin
class Example(val value: Int) {
    init {
        println("First init block: $value")
    }

    val doubled = value * 2

    init {
        println("Second init block: doubled = $doubled")
    }
}

// Output:
// First init block: 5
// Second init block: doubled = 10
```

### 3. Runs Before Secondary Constructor Body

**Execution order:**
```kotlin
class Person(val name: String) {
    init {
        println("1. Init block")
    }

    constructor(name: String, age: Int) : this(name) {
        println("2. Secondary constructor")
    }
}

val person = Person("John", 30)
// Output:
// 1. Init block
// 2. Secondary constructor
```

**Full initialization order:**
1. Primary constructor parameters
2. Property initializers (in order)
3. Init blocks (in order)
4. Secondary constructor body

### 4. Has Access to Primary Constructor Parameters

**Can use constructor parameters:**
```kotlin
class User(name: String, email: String) {
    val username: String
    val domain: String

    init {
        // Access constructor parameters
        require(name.isNotBlank()) { "Name cannot be blank" }
        require(email.contains("@")) { "Invalid email" }

        // Initialize properties based on parameters
        username = email.substringBefore("@")
        domain = email.substringAfter("@")
    }
}
```

### Common Use Cases

**1. Validation:**
```kotlin
class Age(val value: Int) {
    init {
        require(value >= 0) { "Age must be non-negative" }
        require(value <= 150) { "Age must be realistic" }
    }
}
```

**2. Property initialization:**
```kotlin
class Rectangle(val width: Int, val height: Int) {
    val area: Int
    val perimeter: Int

    init {
        area = width * height
        perimeter = 2 * (width + height)
    }
}
```

**3. Logging/debugging:**
```kotlin
class Service(val name: String) {
    init {
        println("Initializing service: $name")
    }
}
```

**4. Setup work:**
```kotlin
class Database(val url: String) {
    init {
        connectToDatabase()
        migrateSchema()
    }

    private fun connectToDatabase() { /* ... */ }
    private fun migrateSchema() { /* ... */ }
}
```

---

## Ответ (RU)

1. init выполняется при создании экземпляра класса и используется для инициализации. 2. Может быть несколько init блоков выполняемых по порядку. 3. Выполняется перед телом вторичного конструктора. 4. Имеет доступ к параметрам первичного конструктора.

