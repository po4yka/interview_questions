---
id: 20251012-12271111133
title: "Kotlin Init Block Features / Возможности блока init в Kotlin"
topic: computer-science
difficulty: easy
status: draft
moc: moc-kotlin
related: [q-noncancellable-context-cleanup--kotlin--medium, q-room-coroutines-flow--kotlin--medium, q-kotlin-favorite-features--programming-languages--easy]
created: 2025-10-15
tags:
  - constructors
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


Init blocks in Kotlin execute initialization code when a class instance is created. They run in the order they appear in the class body.

### Basic Usage
```kotlin
class Person(val name: String) {
    init {
        println("Creating person: $name")
        require(name.isNotBlank()) { "Name cannot be blank" }
    }
}

val person = Person("Alice")
// Prints: Creating person: Alice
```

### Execution Order
```kotlin
class Example(val value: Int) {
    val doubled: Int
    
    init {
        println("First init block")
        doubled = value * 2
    }
    
    val tripled = value * 3
    
    init {
        println("Second init block")
        println("doubled = $doubled, tripled = $tripled")
    }
}

// Order: Primary constructor → properties → init blocks (in order)
```

### Common Use Cases

**1. Validation**
```kotlin
class Email(val address: String) {
    init {
        require("@" in address) { "Invalid email" }
    }
}
```

**2. Initialization Logic**
```kotlin
class Database(val url: String) {
    val connection: Connection
    
    init {
        connection = DriverManager.getConnection(url)
        connection.autoCommit = false
    }
}
```

**3. Logging**
```kotlin
class Service {
    init {
        logger.info("Service initialized")
    }
}
```

### Multiple Init Blocks
```kotlin
class Complex {
    init { step1() }
    val prop1 = compute1()
    init { step2() }
    val prop2 = compute2()
    init { step3() }
}
```

---
---

## Ответ (RU)


Init блоки в Kotlin выполняют код инициализации когда создается экземпляр класса. Они выполняются в порядке появления в теле класса.

### Базовое использование
```kotlin
class Person(val name: String) {
    init {
        println("Creating person: $name")
        require(name.isNotBlank()) { "Name cannot be blank" }
    }
}

val person = Person("Alice")
// Выводит: Creating person: Alice
```

### Порядок выполнения
```kotlin
class Example(val value: Int) {
    val doubled: Int
    
    init {
        println("First init block")
        doubled = value * 2
    }
    
    val tripled = value * 3
    
    init {
        println("Second init block")
        println("doubled = $doubled, tripled = $tripled")
    }
}

// Порядок: Первичный конструктор → свойства → init блоки (по порядку)
```

### Распространенные применения

**1. Валидация**
```kotlin
class Email(val address: String) {
    init {
        require("@" in address) { "Invalid email" }
    }
}
```

**2. Логика инициализации**
```kotlin
class Database(val url: String) {
    val connection: Connection
    
    init {
        connection = DriverManager.getConnection(url)
        connection.autoCommit = false
    }
}
```

**3. Логирование**
```kotlin
class Service {
    init {
        logger.info("Service initialized")
    }
}
```

### Множественные Init блоки
```kotlin
class Complex {
    init { step1() }
    val prop1 = compute1()
    init { step2() }
    val prop2 = compute2()
    init { step3() }
}
```

---

## Related Questions

- [[q-noncancellable-context-cleanup--kotlin--medium]]
- [[q-room-coroutines-flow--kotlin--medium]]
- [[q-kotlin-favorite-features--programming-languages--easy]]

