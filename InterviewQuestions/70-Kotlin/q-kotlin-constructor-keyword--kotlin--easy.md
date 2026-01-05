---
id: lang-209
title: "Kotlin Constructor Keyword / Ключевое слово constructor в Kotlin"
aliases: []
topic: kotlin
subtopics: [classes, functions, types]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-abstract-class-vs-interface--kotlin--medium, q-lifecyclescope-viewmodelscope--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/easy, kotlin/classes, kotlin/functions]
---
# Вопрос (RU)
> Какое ключевое слово используется в Kotlin при объявлении параметров конструктора и когда необходимо явно указывать `constructor`?

# Question (EN)
> Which keyword is used to declare constructor parameters in Kotlin and when is it necessary to explicitly specify `constructor`?

---

## Ответ (RU)

В Kotlin ключевое слово `constructor`:
- обязательно для объявления всех вторичных конструкторов;
- является необязательным для первичного конструктора (обычно параметры объявляются прямо в заголовке класса без него);
- обязательно для первичного конструктора, если к нему добавляются аннотации или модификаторы видимости.

То есть для типичного первичного конструктора отдельное ключевое слово не требуется — параметры задаются в заголовке класса.

**Первичный конструктор (ключевое слово `constructor` не нужно):**
```kotlin
class User(val name: String, val age: Int)  // Первичный конструктор
```

**Вторичный конструктор (используется ключевое слово `constructor`):**
```kotlin
class User(val name: String, val age: Int) {
    // Вторичный конструктор
    constructor(name: String) : this(name, 0) {
        println("Вторичный конструктор вызван")
    }
}
```

**Различные типы конструкторов:**

**1. Первичный конструктор:**
```kotlin
// Простой первичный конструктор
class Person(val name: String, val age: Int)

// С init-блоком
class Person(val name: String) {
    init {
        println("Person создан: $name")
    }
}

// С явным ключевым словом constructor (допустимо, но редко нужно)
class Person constructor(val name: String)
```

**2. Вторичный конструктор:**
```kotlin
class Person {
    var name: String
    var age: Int

    // Вторичный конструктор
    constructor(name: String, age: Int) {
        this.name = name
        this.age = age
    }

    // Другой вторичный конструктор
    constructor(name: String) : this(name, 0)
}
```

**3. Первичный и вторичный вместе:**
```kotlin
class Person(val name: String) {  // Первичный
    // Вторичный должен делегировать первичному
    constructor(name: String, age: Int) : this(name) {
        println("Age: $age")
    }
}
```

**Когда требуется или используется ключевое слово `constructor`:**
- Всегда для всех вторичных конструкторов.
- Для первичного конструктора при наличии аннотаций или модификаторов видимости:

```kotlin
class User @Inject constructor(val repository: Repository)

class Internal private constructor(val id: Int)
```

**Резюме:**
- Первичный конструктор: параметры объявляются в заголовке класса; `constructor` необязателен и в основном нужен при добавлении аннотаций/модификаторов к первичному конструктору.
- Вторичный конструктор: ключевое слово `constructor` всегда используется.

## Answer (EN)

In Kotlin, the `constructor` keyword is:
- required for declaring all secondary constructors;
- optional for primary constructors (parameters are usually declared directly in the class header without it);
- required on a primary constructor when you add annotations or visibility modifiers to that constructor.

So for a typical primary constructor, no keyword is needed — the parameters are declared directly in the class header.

**Primary Constructor (no `constructor` keyword needed):**
```kotlin
class User(val name: String, val age: Int)  // Primary constructor
```

**Secondary Constructor (uses `constructor` keyword):**
```kotlin
class User(val name: String, val age: Int) {
    // Secondary constructor
    constructor(name: String) : this(name, 0) {
        println("Secondary constructor called")
    }
}
```

**Different Constructor Types:**

**1. Primary Constructor:**
```kotlin
// Simple primary constructor
class Person(val name: String, val age: Int)

// With init block
class Person(val name: String) {
    init {
        println("Person created: $name")
    }
}

// With explicit constructor keyword (allowed but rarely needed)
class Person constructor(val name: String)
```

**2. Secondary Constructor:**
```kotlin
class Person {
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

**3. Both Primary and Secondary:**
```kotlin
class Person(val name: String) {  // Primary
    // Secondary must delegate to primary
    constructor(name: String, age: Int) : this(name) {
        println("Age: $age")
    }
}
```

**When `constructor` keyword is required or used:**
- Always for all secondary constructors.
- For a primary constructor when it has annotations or visibility modifiers:

```kotlin
class User @Inject constructor(val repository: Repository)

class Internal private constructor(val id: Int)
```

**Summary:**
- Primary constructor: Parameters are declared in the class header; `constructor` is optional and mainly needed when adding annotations/modifiers to the primary constructor.
- Secondary constructor: Always use the `constructor` keyword.

## Дополнительные Вопросы (RU)

- В чем разница между первичным и вторичными конструкторами в Kotlin?
- Когда предпочтительно использовать только первичный конструктор без вторичных?
- Как аннотации и модификаторы видимости влияют на необходимость явного указания `constructor`?
- Чем `constructor` отличается от `init`-блоков по ответственности?
- Как использовать вторичные конструкторы для делегирования логики между разными вариантами инициализации?

## Follow-ups

- What is the difference between primary and secondary constructors in Kotlin?
- When is it preferable to use only a primary constructor without secondary ones?
- How do annotations and visibility modifiers affect the need to explicitly use the `constructor` keyword?
- How do `constructor` and `init` blocks differ in terms of responsibility?
- How can secondary constructors be used to delegate logic between different initialization options?

## Related Questions

- [[q-abstract-class-vs-interface--kotlin--medium]]
- [[q-lifecyclescope-viewmodelscope--kotlin--medium]]