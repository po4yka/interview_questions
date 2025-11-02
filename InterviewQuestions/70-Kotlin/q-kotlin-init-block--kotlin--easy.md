---
id: kotlin-001
title: "Init Block in Kotlin / Блок init в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [class-initialization, constructors, init-block, initialization]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-flowon-operator-context-switching--kotlin--hard, q-kotlin-constructors--kotlin--easy, q-repeatonlifecycle-android--kotlin--medium, q-statein-sharein-flow--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-18

tags: [constructors, difficulty/easy, init-block, initialization, kotlin]
date created: Saturday, October 18th 2025, 3:12:23 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---

# Question (EN)
> What is an init block in Kotlin?
# Вопрос (RU)
> Что такое блок init в Kotlin?

---

## Answer (EN)

A class in Kotlin can have a **primary constructor** and one or more **secondary constructors**. The primary constructor cannot contain any code. Initialization code can be placed in **initializer blocks**, which are prefixed with the `init` keyword.

### Key Points

1. **Code in initializer blocks effectively becomes part of the primary constructor** - The init block runs as part of object initialization
2. **Delegation to the primary constructor happens as the first statement** - Even in secondary constructors, init blocks run first
3. **Initializer blocks are executed in the same order as they appear** - You can have multiple init blocks
4. **Init blocks execute even if there's no primary constructor** - The delegation happens implicitly

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

**English Summary**: Init blocks are special code blocks prefixed with the `init` keyword that execute during object initialization. They run in the order they appear in the class body, become part of the primary constructor, and execute before secondary constructor bodies. They're useful for validation, complex initialization logic, and computed properties.

## Ответ (RU)

Класс в Kotlin может иметь **первичный конструктор** и один или несколько **вторичных конструкторов**. Первичный конструктор не может содержать никакого кода. Код инициализации можно поместить в **блоки инициализации**, которые обозначаются ключевым словом `init`.

### Ключевые Моменты

1. **Код в блоках инициализации фактически становится частью первичного конструктора** - Блок init выполняется как часть инициализации объекта
2. **Делегирование к первичному конструктору происходит как первый оператор** - Даже во вторичных конструкторах блоки init выполняются первыми
3. **Блоки инициализации выполняются в том порядке, в котором они появляются** - Вы можете иметь несколько блоков init
4. **Блоки init выполняются, даже если нет первичного конструктора** - Делегирование происходит неявно

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

**Краткое содержание**: Блоки init — это специальные блоки кода с ключевым словом `init`, которые выполняются во время инициализации объекта. Они выполняются в порядке появления в теле класса, становятся частью первичного конструктора и выполняются перед телами вторичных конструкторов. Они полезны для валидации, сложной логики инициализации и вычисляемых свойств.

---

## References
- [Classes - Kotlin Documentation](https://kotlinlang.org/docs/reference/classes.html)
- [Kotlin Constructors - Programiz](https://www.programiz.com/kotlin-programming/constructors)

## Related Questions
- [[q-kotlin-constructors--kotlin--easy]]
- [[q-kotlin-properties--kotlin--easy]]
