---
id: lang-033
title: "Kotlin Init Block Features / Возможности блока init в Kotlin"
aliases: [Kotlin Init Block Features, Возможности блока init в Kotlin]
topic: kotlin
subtopics: [initialization, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-noncancellable-context-cleanup--kotlin--medium, q-room-coroutines-flow--kotlin--medium]
created: 2024-10-15
updated: 2025-11-09
tags: [constructors, difficulty/easy, init, initialization, oop, kotlin]
---
# Вопрос (RU)
> Есть какие-то особенности использования `init` блока?

# Question (EN)
> Are there any features of using `init` block?

## Ответ (RU)

Init блоки в Kotlin выполняют код инициализации, когда создается экземпляр класса. Они являются частью первичного конструктора и выполняются вместе с инициализацией свойств в порядке, в котором объявлены в теле класса (инициализаторы свойств и init блоки перемежаются). См. также [[c-kotlin]].

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

// Важно: инициализаторы свойств и init блоки выполняются сверху вниз
// в порядке объявления в классе. Это часть логики первичного конструктора.
```

### Распространенные Применения

**1. Валидация аргументов конструктора**
```kotlin
class Email(val address: String) {
    init {
        require("@" in address) { "Invalid email" }
    }
}
```

**2. Логика инициализации сложных свойств**
```kotlin
class Database(val url: String) {
    val connection: Connection
    
    init {
        connection = DriverManager.getConnection(url)
        connection.autoCommit = false
    }
}
```

**3. Логирование создания экземпляра**
```kotlin
class Service {
    init {
        logger.info("Service initialized")
    }
}
```

### Множественные Init Блоки и Подводные Камни
```kotlin
class Complex {
    init { step1() }
    val prop1 = compute1()
    init { step2() }
    val prop2 = compute2()
    init { step3() }
}

// Разрешено иметь несколько init блоков, но их выполнение тоже идет сверху вниз
// вместе с инициализаторами свойств. Слишком много init блоков ухудшают читаемость.
// Важно не обращаться в init к свойствам, которые объявлены ниже и зависят от еще
// не выполненной инициализации.
```

## Answer (EN)

Init blocks in Kotlin execute initialization code when a class instance is created. They are part of the primary constructor and are executed together with property initializers in the order they are declared in the class body (property initializers and init blocks are interleaved top-down). See also [[c-kotlin]].

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

// Important: property initializers and init blocks are executed top-down
// in the order they appear in the class. This is part of primary constructor logic.
```

### Common Use Cases

**1. Constructor argument validation**
```kotlin
class Email(val address: String) {
    init {
        require("@" in address) { "Invalid email" }
    }
}
```

**2. Complex property initialization**
```kotlin
class Database(val url: String) {
    val connection: Connection
    
    init {
        connection = DriverManager.getConnection(url)
        connection.autoCommit = false
    }
}
```

**3. Instance creation logging**
```kotlin
class Service {
    init {
        logger.info("Service initialized")
    }
}
```

### Multiple Init Blocks and Pitfalls
```kotlin
class Complex {
    init { step1() }
    val prop1 = compute1()
    init { step2() }
    val prop2 = compute2()
    init { step3() }
}

// Having multiple init blocks is allowed; they also run top-down with property
// initializers. Too many init blocks can hurt readability. Be careful not to
// rely in an init block on properties whose initialization has not run yet.
```

## Дополнительные вопросы (RU)

- В чем ключевые отличия от подхода в Java?
- Когда вы бы использовали `init` блок на практике?
- Какие распространенные подводные камни стоит учитывать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-noncancellable-context-cleanup--kotlin--medium]]
- [[q-room-coroutines-flow--kotlin--medium]]
- [[q-kotlin-favorite-features--programming-languages--easy]]

## Related Questions

- [[q-noncancellable-context-cleanup--kotlin--medium]]
- [[q-room-coroutines-flow--kotlin--medium]]
- [[q-kotlin-favorite-features--programming-languages--easy]]
