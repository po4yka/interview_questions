---
tags:
  - classes
  - constructors
  - init-block
  - initialization
  - kotlin
  - primary-constructor
  - programming-languages
  - secondary-constructor
difficulty: medium
status: reviewed
---

# Какие типы конструкторов есть у классов в Kotlin?

**English**: What types of constructors do classes in Kotlin have?

## Answer

Kotlin has two types of constructors: **primary constructors** and **secondary constructors**.

**1. Primary Constructor**

Declared in the class header, can initialize class properties directly:

```kotlin
class User(val name: String, val age: Int)  // Primary constructor

// Usage:
val user = User("Alice", 30)
println(user.name)  // Alice
```

**With init block:**
```kotlin
class User(val name: String, val age: Int) {
    init {
        println("User created: $name, age $age")
        require(age >= 0) { "Age must be positive" }
    }
}
```

**With default values:**
```kotlin
class User(val name: String, val age: Int = 0)

val user1 = User("Alice", 30)
val user2 = User("Bob")  // age defaults to 0
```

**2. Secondary Constructor**

Declared inside the class body with `constructor` keyword:

```kotlin
class User {
    var name: String
    var age: Int

    // Secondary constructor
    constructor(name: String, age: Int) {
        this.name = name
        this.age = age
    }

    // Another secondary constructor
    constructor(name: String) : this(name, 0)
}
```

**3. Primary + Secondary Constructors**

Secondary constructors must delegate to the primary constructor:

```kotlin
class User(val name: String) {  // Primary
    var age: Int = 0

    // Secondary must call primary via this()
    constructor(name: String, age: Int) : this(name) {
        this.age = age
    }

    // Another secondary constructor
    constructor(name: String, age: Int, email: String) : this(name, age) {
        println("Email: $email")
    }
}
```

**Execution order:**
```kotlin
class User(val name: String) {
    val id: Int

    init {
        println("1. Init block")  // Runs first
        id = name.hashCode()
    }

    constructor(name: String, age: Int) : this(name) {
        println("2. Secondary constructor")  // Runs after init
    }
}

val user = User("Alice", 30)
// Output:
// 1. Init block
// 2. Secondary constructor
```

**Comparison:**

| Feature | Primary Constructor | Secondary Constructor |
|---------|--------------------|-----------------------|
| Location | Class header | Class body |
| Keyword | Optional `constructor` | Required `constructor` |
| Property declaration | Yes (`val`/`var`) | No |
| Init blocks | Runs automatically | Must delegate to primary |
| Multiple | Only one | Multiple allowed |
| Default values | Supported | Not directly (use overloads) |

**When to use each:**

**Primary constructor:**
- Default choice for most classes
- Simple initialization
- Direct property declaration

**Secondary constructor:**
- Multiple ways to create objects
- Complex initialization logic
- Delegating to other constructors
- Interop with Java (when primary constructor doesn't work)

**Best practices:**
- Prefer primary constructor with default values
- Use secondary constructors only when necessary
- Keep initialization logic in `init` blocks

## Ответ

В Kotlin есть первичные и вторичные конструкторы. Первичный конструктор объявляется вместе с классом и может принимать параметры для инициализации свойств класса. Вторичные конструкторы объявляются внутри класса с ключевым словом constructor и предоставляют дополнительные способы инициализации класса.

