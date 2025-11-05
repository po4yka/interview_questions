---
id: lang-033
title: "Kotlin Init Block Features / Возможности блока init в Kotlin"
aliases: [Kotlin Init Block Features, Возможности блока init в Kotlin]
topic: programming-languages
subtopics: [initialization, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-favorite-features--programming-languages--easy, q-noncancellable-context-cleanup--kotlin--medium, q-room-coroutines-flow--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [constructors, difficulty/easy, init, initialization, oop, programming-languages]
date created: Friday, October 31st 2025, 6:29:34 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---
# Есть Какие-то Особенности Использования Init Block?

# Вопрос (RU)
> Есть какие-то особенности использования init block?

---

# Question (EN)
> Are there any features of using init block?

## Ответ (RU)


Init блоки в Kotlin выполняют код инициализации когда создается экземпляр класса. Они выполняются в порядке появления в теле класса.

### Базовое Использование
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

### Порядок Выполнения
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

### Распространенные Применения

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

### Множественные Init Блоки
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

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-noncancellable-context-cleanup--kotlin--medium]]
- [[q-room-coroutines-flow--kotlin--medium]]
- [[q-kotlin-favorite-features--programming-languages--easy]]

