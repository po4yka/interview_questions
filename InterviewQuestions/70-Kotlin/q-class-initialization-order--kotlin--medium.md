---
id: kotlin-230
title: "Class Initialization Order in Kotlin / Порядок инициализации класса в Kotlin"
aliases: ["Class Initialization Order", "Порядок инициализации класса"]
topic: kotlin
subtopics: [classes, initialization, kotlin-features]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-data-class-detailed--kotlin--medium, q-sealed-class-sealed-interface--kotlin--medium, q-inheritance-open-final--kotlin--medium]
created: "2025-10-12"
updated: 2025-01-25
tags: [kotlin, classes, initialization, kotlin-features, difficulty/medium]
sources: [https://kotlinlang.org/docs/inheritance.html]
---

# Вопрос (RU)
> В каком порядке происходит инициализация класса в Kotlin?

# Question (EN)
> What is the order of class initialization in Kotlin?

---

## Ответ (RU)

**Теория инициализации в Kotlin:**
Порядок инициализации класса в Kotlin строго определён. Свойства инициализируются по порядку сверху вниз в теле класса. Сначала выполняются переменные верхнего уровня и блоки инициализации, затем конструктор. В иерархии наследования родительская инициализация выполняется перед дочерней.

**Основные правила:**
1. **Порядок объявления**: Свойства инициализируются в порядке их объявления
2. **Блок инициализации** (`init`): Выполняется сразу после свойства, которое находится перед ним
3. **Первичный конструктор**: Выполняется после всех блоков инициализации
4. **Вторичный конструктор**: Выполняется после первичного, после всех инициализаций

**Простая инициализация:**
```kotlin
class Example {
    // ✅ 1. Свойство инициализируется первым
    private val prop1 = "init first"

    // ✅ 2. Блок init выполняется после prop1
    init {
        println(prop1)
    }

    // ✅ 3. Следующее свойство инициализируется после init
    private val prop2 = "init second"

    // ✅ 4. Второй init выполняется после prop2
    init {
        println(prop2)
    }
}
```

**Инициализация с наследованием:**
```kotlin
open class Parent {
    private val parentProp = "Parent".also { println("Parent property initialized") }

    init {
        println("Parent init block")
    }

    constructor() {
        println("Parent constructor")
    }
}

class Child : Parent() {
    private val childProp = "Child".also { println("Child property initialized") }

    init {
        println("Child init block")
    }

    constructor() : super() {
        println("Child constructor")
    }
}

// Вывод при создании Child():
// Parent property initialized
// Parent init block
// Parent constructor
// Child property initialized
// Child init block
// Child constructor
```

**Избегание обращения к неинициализированным свойствам:**
```kotlin
class User {
    // ❌ ПЛОХО: обращение к size до инициализации
    private val value: String = "Initialized"
    private val size = value.length // Может обращаться

    init {
        println("Size: $size") // ✅ ХОРОШО: value уже инициализирован
    }
}

class BadUser {
    // ❌ ПЛОХО: обращение к value2 до его инициализации
    private val size2 = value2.length // value2 ещё не инициализирован!
    private val value2: String = "Initialized"
}
```

**Использование `lazy` для ленивой инициализации:**
```kotlin
class Heavy {
    // ✅ Ленивая инициализация - свойство вычисляется только при первом обращении
    private val expensive: String by lazy {
        println("Computing expensive property")
        "Computed value"
    }

    fun useExpensive() {
        println(expensive) // Вычисляется только здесь
    }
}
```

---

## Answer (EN)

**Kotlin Initialization Theory:**
Class initialization order in Kotlin is strictly defined. Properties are initialized top-to-bottom in class body. First, top-level variables and init blocks execute, then constructor. In inheritance hierarchy, parent initialization executes before child.

**Key Rules:**
1. **Declaration order**: Properties initialize in order of declaration
2. **Init block**: Executes immediately after the property preceding it
3. **Primary constructor**: Executes after all init blocks
4. **Secondary constructor**: Executes after primary, after all initializations

**Simple Initialization:**
```kotlin
class Example {
    // ✅ 1. Property initialized first
    private val prop1 = "init first"

    // ✅ 2. Init block executes after prop1
    init {
        println(prop1)
    }

    // ✅ 3. Next property initialized after init
    private val prop2 = "init second"

    // ✅ 4. Second init executes after prop2
    init {
        println(prop2)
    }
}
```

**Initialization with Inheritance:**
```kotlin
open class Parent {
    private val parentProp = "Parent".also { println("Parent property initialized") }

    init {
        println("Parent init block")
    }

    constructor() {
        println("Parent constructor")
    }
}

class Child : Parent() {
    private val childProp = "Child".also { println("Child property initialized") }

    init {
        println("Child init block")
    }

    constructor() : super() {
        println("Child constructor")
    }
}

// Output when creating Child():
// Parent property initialized
// Parent init block
// Parent constructor
// Child property initialized
// Child init block
// Child constructor
```

**Avoiding Uninitialized Property Access:**
```kotlin
class User {
    // ❌ BAD: accessing size before initialization
    private val value: String = "Initialized"
    private val size = value.length // Can access

    init {
        println("Size: $size") // ✅ GOOD: value already initialized
    }
}

class BadUser {
    // ❌ BAD: accessing value2 before initialization
    private val size2 = value2.length // value2 not yet initialized!
    private val value2: String = "Initialized"
}
```

**Using `lazy` for Lazy Initialization:**
```kotlin
class Heavy {
    // ✅ Lazy initialization - property computed only on first access
    private val expensive: String by lazy {
        println("Computing expensive property")
        "Computed value"
    }

    fun useExpensive() {
        println(expensive) // Computed only here
    }
}
```

## Follow-ups

- How does initialization order differ with `lateinit`?
- What happens with delegated properties initialization order?
- How to debug initialization order issues?

## References

- [[c-oop-fundamentals]]
- https://kotlinlang.org/docs/classes.html

## Related Questions

### Prerequisites (Easier)
- [[q-data-class-variables--programming-languages--medium]] - Data class basics

### Related (Medium)
- [[q-data-class-detailed--kotlin--medium]] - Data classes in detail
- [[q-sealed-class-sealed-interface--kotlin--medium]] - Sealed classes
- [[q-inheritance-open-final--kotlin--medium]] - Inheritance concepts

### Advanced (Harder)
- [[q-lateinit-initialization--kotlin--medium]] - Lateinit properties
