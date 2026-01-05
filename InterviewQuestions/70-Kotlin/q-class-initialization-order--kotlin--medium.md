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
related: [c-kotlin, q-abstract-class-vs-interface--kotlin--medium]
created: "2025-10-12"
updated: "2025-11-11"
tags: [classes, difficulty/medium, initialization, kotlin, kotlin-features]
sources: ["https://kotlinlang.org/docs/inheritance.html"]
---
# Вопрос (RU)
> В каком порядке происходит инициализация класса в Kotlin?

# Question (EN)
> What is the order of class initialization in Kotlin?

---

## Ответ (RU)

**Теория инициализации в Kotlin:**
Порядок инициализации класса в Kotlin строго определён. Важные моменты:
- Тело первичного конструктора включает инициализаторы свойств и блоки `init`; они выполняются в порядке объявления сверху вниз.
- Сначала вычисляются аргументы первичного конструктора, затем выполняются инициализаторы свойств и блоки `init` в том порядке, в котором они объявлены в теле класса.
- Во вторичных конструкторах тело выполняется только после делегирования к первичному конструктору (либо к другому вторичному, в конечном счёте — к первичному), то есть после завершения основной инициализации.
- В иерархии наследования инициализация суперкласса полностью завершается до начала инициализации подкласса.

**Основные правила:**
1. **Порядок объявления**: Инициализаторы свойств и блоки `init` выполняются сверху вниз в том порядке, в котором они записаны в теле класса.
2. **Блок инициализации (`init`)**: Выполняется в точке объявления как часть тела первичного конструктора, сразу после соответствующих предыдущих инициализаций свойств.
3. **Первичный конструктор**: Его параметры сначала вычисляются, затем выполняется тело первичного конструктора (инициализаторы свойств + блоки `init`), как единое целое.
4. **Вторичный конструктор**: Должен делегировать к первичному (или цепочке), и его тело выполняется после завершения инициализации через этот делегирующий вызов.

**Простая инициализация:**
```kotlin
class Example(
    private val fromPrimary: String = "from primary"
) {
    // ✅ 1. Свойство инициализируется первым
    private val prop1 = "init first"

    // ✅ 2. Блок init выполняется после prop1
    init {
        println(prop1)
    }

    // ✅ 3. Следующее свойство инициализируется после init
    private val prop2 = "init second"

    // ✅ 4. Следующий init выполняется после prop2
    init {
        println(prop2)
    }
}
```

**Инициализация с наследованием:**
```kotlin
open class Parent(
    private val fromPrimary: String = "Parent ctor arg"
) {
    private val parentProp = "Parent".also { println("Parent property initialized") }

    init {
        println("Parent init block")
    }
}

class Child : Parent() {
    private val childProp = "Child".also { println("Child property initialized") }

    init {
        println("Child init block")
    }
}

// При создании Child():
// Parent property initialized
// Parent init block
// Child property initialized
// Child init block
```

**Важные моменты с вторичными конструкторами и super:**
```kotlin
open class Base(val x: Int) {
    init {
        println("Base init: x = $x")
    }
}

class Derived : Base {
    constructor(x: Int) : super(x) {
        // ✅ Это тело вторичного конструктора выполнится после init Base
        println("Derived secondary constructor body")
    }
}
```

**Избегание обращения к неинициализированным свойствам:**
```kotlin
class User {
    private val value: String = "Initialized"
    private val size = value.length // ✅ Можно: value уже инициализировано к этому моменту

    init {
        println("Size: $size") // ✅ Здесь и value, и size уже инициализированы
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
        println(expensive) // Вычисляется только здесь при первом обращении
    }
}
```

---

## Answer (EN)

**Kotlin Initialization Theory:**
Class initialization order in Kotlin is well-defined. Key points:
- The primary constructor body consists of property initializers and `init` blocks; they run in top-to-bottom order as written in the class body.
- First, primary constructor arguments are evaluated; then property initializers and `init` blocks are executed in declaration order.
- A secondary constructor must delegate to the primary (or another secondary that eventually calls the primary); its body runs only after that delegated call completes, i.e., after the main initialization.
- In an inheritance hierarchy, the supertype’s initialization fully completes before the subclass’s property initializers and `init` blocks run.

**Key Rules:**
1. **Declaration order**: Property initializers and `init` blocks execute in the order they appear in the class body.
2. **Init block**: Executes at its declaration position as part of the primary constructor body, after the preceding property initializers.
3. **Primary constructor**: Its parameters are evaluated first; then the primary constructor body (property initializers + `init` blocks) is executed as a single sequence.
4. **Secondary constructor**: Must delegate to the primary (directly or indirectly); its body executes after the delegated constructor call completes.

**Simple Initialization:**
```kotlin
class Example(
    private val fromPrimary: String = "from primary"
) {
    // ✅ 1. Property initialized first
    private val prop1 = "init first"

    // ✅ 2. Init block executes after prop1
    init {
        println(prop1)
    }

    // ✅ 3. Next property initialized after init
    private val prop2 = "init second"

    // ✅ 4. Next init executes after prop2
    init {
        println(prop2)
    }
}
```

**Initialization with Inheritance:**
```kotlin
open class Parent(
    private val fromPrimary: String = "Parent ctor arg"
) {
    private val parentProp = "Parent".also { println("Parent property initialized") }

    init {
        println("Parent init block")
    }
}

class Child : Parent() {
    private val childProp = "Child".also { println("Child property initialized") }

    init {
        println("Child init block")
    }
}

// Output when creating Child():
// Parent property initialized
// Parent init block
// Child property initialized
// Child init block
```

**Important notes about secondary constructors and super:**
```kotlin
open class Base(val x: Int) {
    init {
        println("Base init: x = $x")
    }
}

class Derived : Base {
    constructor(x: Int) : super(x) {
        // ✅ Secondary constructor body runs after Base init completes
        println("Derived secondary constructor body")
    }
}
```

**Avoiding Uninitialized Property Access:**
```kotlin
class User {
    private val value: String = "Initialized"
    private val size = value.length // ✅ OK: value is initialized before this initializer runs

    init {
        println("Size: $size") // ✅ Both value and size are initialized here
    }
}

class BadUser {
    // ❌ BAD: accessing value2 before it is initialized
    private val size2 = value2.length // value2 not initialized yet!
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
        println(expensive) // Computed only here on first access
    }
}
```

## Follow-ups

- How does initialization order differ with `lateinit`?
- What happens with delegated properties initialization order?
- How to debug initialization order issues?

## References

- [[c-kotlin]]
- https://kotlinlang.org/docs/classes.html

## Related Questions

### Prerequisites (Easier)

### Related (Medium)

### Advanced (Harder)
- [[q-abstract-class-vs-interface--kotlin--medium]]
