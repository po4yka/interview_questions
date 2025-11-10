---
id: kotlin-001
title: "Init Block in Kotlin / Блок init в Kotlin"
aliases: ["Init Block in Kotlin", "Блок init в Kotlin"]

# Classification
topic: kotlin
subtopics: [constructors, initialization, init-block]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, q-flowon-operator-context-switching--kotlin--hard, q-kotlin-constructors--kotlin--easy, q-repeatonlifecycle-android--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [constructors, difficulty/easy, init-block, initialization, kotlin]
---
# Вопрос (RU)
> Что такое блок init в Kotlin?

---

# Question (EN)
> What is an init block in Kotlin?

## Ответ (RU)

Класс в Kotlin (см. [[c-kotlin]]) может иметь **первичный конструктор** и один или несколько **вторичных конструкторов**. Первичный конструктор не может содержать никакого исполняемого кода в своей декларации. Код инициализации можно поместить в **блоки инициализации**, которые обозначаются ключевым словом `init`.

### Ключевые Моменты

1. **Код в блоках инициализации фактически становится частью первичного конструктора** — блоки `init` выполняются как часть инициализации объекта сразу после инициализации параметров и свойств первичного конструктора.
2. **Во вторичных конструкторах сначала выполняется делегирование, затем код init** — каждый вторичный конструктор обязан делегировать к первичному (или другому вторичному); после делегирования выполняются инициализаторы свойств и блоки `init`, а потом уже тело вторичного конструктора.
3. **Блоки инициализации и инициализаторы свойств выполняются в порядке появления** — можно объявлять несколько блоков `init`; они выполняются в одном общем порядке с инициализаторами свойств, в соответствии с их текстовым расположением в теле класса.
4. **Блоки init можно использовать даже без явного первичного конструктора** — если первичный конструктор не указан явно, используется неявный конструктор по умолчанию, и блоки `init` все равно выполняются при создании экземпляра.

### Базовый Пример

```kotlin
class Person(val name: String, val age: Int) {
    init {
        println("Person created: $name, age $age")
        require(age >= 0) { "Age cannot be negative" }
    }
}

val person = Person("Alice", 25)
// Вывод: Person created: Alice, age 25
```

### Несколько Блоков Init

```kotlin
class User(val username: String) {
    val createdAt: Long

    init {
        println("First init block")
        createdAt = System.currentTimeMillis()
    }

    val id = generateId()  // Инициализатор свойства

    init {
        println("Second init block")
        println("User $username created at $createdAt with id $id")
    }

    private fun generateId(): String = java.util.UUID.randomUUID().toString()
}

// Порядок выполнения:
// 1. Первый блок init
// 2. Инициализатор свойства (id = generateId())
// 3. Второй блок init
```

### Блок Init Со Вторичным Конструктором

```kotlin
class Rectangle(val width: Int, val height: Int) {
    val area: Int

    init {
        println("Primary constructor - calculating area")
        area = width * height
    }

    // Вторичный конструктор
    constructor(side: Int) : this(side, side) {
        println("Secondary constructor - creating square")
    }
}

val square = Rectangle(5)
// Вывод:
// Primary constructor - calculating area
// Secondary constructor - creating square
```

### Общие Случаи Использования

#### 1. Валидация

```kotlin
class Email(val address: String) {
    init {
        require(address.contains("@")) {
            "Invalid email format"
        }
    }
}
```

#### 2. Вычисляемые Свойства

```kotlin
class Circle(val radius: Double) {
    val area: Double
    val circumference: Double

    init {
        area = Math.PI * radius * radius
        circumference = 2 * Math.PI * radius
    }
}
```

#### 3. Логирование И Отладка

```kotlin
class DatabaseConnection(val url: String) {
    init {
        println("Connecting to database at $url")
        // Логика подключения здесь
    }
}
```

#### 4. Сложная Логика Инициализации

```kotlin
class Configuration(val env: String) {
    val apiEndpoint: String
    val timeout: Int
    val retries: Int

    init {
        when (env) {
            "production" -> {
                apiEndpoint = "https://api.prod.com"
                timeout = 30000
                retries = 3
            }
            "staging" -> {
                apiEndpoint = "https://api.staging.com"
                timeout = 60000
                retries = 5
            }
            else -> {
                apiEndpoint = "http://localhost:8080"
                timeout = 120000
                retries = 10
            }
        }
    }
}
```

**Краткое содержание**: Блоки init — это специальные блоки кода с ключевым словом `init`, которые выполняются во время инициализации объекта. Они выполняются в порядке появления в теле класса совместно с инициализаторами свойств, логически являются частью первичного конструктора и выполняются до выполнения тел вторичных конструкторов.

---

## Answer (EN)

A class in Kotlin (see [[c-kotlin]]) can have a **primary constructor** and one or more **secondary constructors**. The primary constructor cannot contain executable code in its declaration. Initialization code can be placed in **initializer blocks**, which are prefixed with the `init` keyword.

### Key Points

1. **Code in initializer blocks effectively becomes part of the primary constructor** — init blocks run as part of object initialization, immediately after initializing primary constructor parameters and properties.
2. **In secondary constructors, delegation runs first, then init and property initialization, then the body** — every secondary constructor must delegate to the primary (or another secondary); after that delegation, property initializers and init blocks execute, followed by the secondary constructor body.
3. **Initializer blocks and property initializers are executed in the order they appear** — you can define multiple init blocks; they execute in a single sequence interleaved with property initializers, according to their textual order in the class body.
4. **Init blocks can be used even without an explicit primary constructor** — if a primary constructor is not explicitly declared, a default one is implied, and init blocks still execute on each instance creation.

### Basic Example

```kotlin
class Person(val name: String, val age: Int) {
    init {
        println("Person created: $name, age $age")
        require(age >= 0) { "Age cannot be negative" }
    }
}

val person = Person("Alice", 25)
// Output: Person created: Alice, age 25
```

### Multiple Init Blocks

```kotlin
class User(val username: String) {
    val createdAt: Long

    init {
        println("First init block")
        createdAt = System.currentTimeMillis()
    }

    val id = generateId()  // Property initializer

    init {
        println("Second init block")
        println("User $username created at $createdAt with id $id")
    }

    private fun generateId(): String = java.util.UUID.randomUUID().toString()
}

// Execution order:
// 1. First init block
// 2. Property initializer (id = generateId())
// 3. Second init block
```

### Init Block with Secondary Constructor

```kotlin
class Rectangle(val width: Int, val height: Int) {
    val area: Int

    init {
        println("Primary constructor - calculating area")
        area = width * height
    }

    // Secondary constructor
    constructor(side: Int) : this(side, side) {
        println("Secondary constructor - creating square")
    }
}

val square = Rectangle(5)
// Output:
// Primary constructor - calculating area
// Secondary constructor - creating square
```

### Common Use Cases

#### 1. Validation

```kotlin
class Email(val address: String) {
    init {
        require(address.contains("@")) {
            "Invalid email format"
        }
    }
}
```

#### 2. Computed Properties

```kotlin
class Circle(val radius: Double) {
    val area: Double
    val circumference: Double

    init {
        area = Math.PI * radius * radius
        circumference = 2 * Math.PI * radius
    }
}
```

#### 3. Logging and Debugging

```kotlin
class DatabaseConnection(val url: String) {
    init {
        println("Connecting to database at $url")
        // Connection logic here
    }
}
```

#### 4. Complex Initialization Logic

```kotlin
class Configuration(val env: String) {
    val apiEndpoint: String
    val timeout: Int
    val retries: Int

    init {
        when (env) {
            "production" -> {
                apiEndpoint = "https://api.prod.com"
                timeout = 30000
                retries = 3
            }
            "staging" -> {
                apiEndpoint = "https://api.staging.com"
                timeout = 60000
                retries = 5
            }
            else -> {
                apiEndpoint = "http://localhost:8080"
                timeout = 120000
                retries = 10
            }
        }
    }
}
```

**English Summary**: Init blocks are special code blocks prefixed with the `init` keyword that execute during object initialization. They run in the order they appear in the class body together with property initializers, conceptually form part of the primary constructor's initialization logic, and execute before any secondary constructor body. They're useful for validation, complex initialization logic, and computed properties.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Classes - Kotlin Documentation](https://kotlinlang.org/docs/reference/classes.html)
- [Kotlin Constructors - Programiz](https://www.programiz.com/kotlin-programming/constructors)

## Related Questions
- [[q-kotlin-constructors--kotlin--easy]]
- [[q-kotlin-properties--kotlin--easy]]
