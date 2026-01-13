---
anki_cards:
- slug: q-kotlin-class-initializers--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-kotlin-class-initializers--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---id: lang-202
title: "Kotlin Class Initializers / Инициализаторы классов Kotlin"
aliases: ["Kotlin Class Initializers", "Инициализаторы классов Kotlin"]
topic: kotlin
subtopics: ["classes", "functions", "types"]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-actor-pattern--kotlin--hard]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/medium, kotlin]
---
# Вопрос (RU)
> Расскажи про инициализаторы в классах в Kotlin

# Question (EN)
> Tell me about class initializers in Kotlin

---

## Ответ (RU)

В Kotlin есть несколько механизмов инициализации:

### 1. Первичный Конструктор (Primary Constructor)

Объявляется в заголовке класса, используется для основной инициализации:

```kotlin
class Person(val name: String, val age: Int) {
    // Свойства инициализируются из первичного конструктора
}
```

### 2. Блоки Init

Выполняются как часть инициализации при вызове первичного конструктора. В классе может быть несколько блоков init.

```kotlin
class Person(val name: String) {
    init {
        println("First init block: $name")
    }

    val nameLength: Int

    init {
        nameLength = name.length
        println("Second init block")
    }
}
```

### 3. Вторичные Конструкторы (Secondary Constructors)

Объявляются с ключевым словом `constructor`. Если есть первичный конструктор, каждый вторичный конструктор обязан делегировать ему (напрямую или через другой вторичный конструктор):

```kotlin
class Person(val name: String) {
    var age: Int = 0

    constructor(name: String, age: Int) : this(name) {
        this.age = age
    }
}
```

**Порядок инициализации (в пределах одного класса):**

1. Вычисляются аргументы первичного конструктора.
2. Затем инициализаторы свойств и блоки init в теле класса выполняются строго в том порядке, в котором они объявлены сверху вниз.
3. После этого выполняется тело вторичного конструктора (если он используется).

**Пример, показывающий порядок:**
```kotlin
class Example(val param: String) {
    val prop1 = "Property 1".also { println("1: $it") }

    init {
        println("2: First init block")
    }

    val prop2 = "Property 2".also { println("3: $it") }

    init {
        println("4: Second init block")
    }

    constructor(param: String, extra: String) : this(param) {
        println("5: Secondary constructor")
    }
}

// Вывод при вызове вторичного конструктора:
// 1: Property 1
// 2: First init block
// 3: Property 2
// 4: Second init block
// 5: Secondary constructor
```

**Замечания про инициализацию при наследовании (уточненно):**
- При создании объекта подкласса сначала инициализируется базовый класс.
- Конструктор подкласса обязан делегировать одному из конструкторов суперкласса.
- Инициализаторы свойств и блоки `init` базового класса выполняются до инициализаторов свойств и блоков `init` подкласса, а затем выполняется тело конструктора подкласса.

**Важные правила:**
- Если есть первичный конструктор, каждый вторичный конструктор должен делегировать ему через `this(...)` (напрямую или цепочкой вторичных конструкторов).
- Блоки `init` и инициализаторы свойств выполняются в порядке объявления в теле класса, до тела вторичного конструктора.
- Свойства могут инициализироваться непосредственно при объявлении или в блоках `init`.

## Answer (EN)

Kotlin has several initialization mechanisms:

### 1. Primary Constructor

Declared in class header, used for main initialization:

```kotlin
class Person(val name: String, val age: Int) {
    // Properties initialized from primary constructor
}
```

### 2. Init Blocks

Execute as part of primary-constructor initialization. A class can have multiple init blocks.

```kotlin
class Person(val name: String) {
    init {
        println("First init block: $name")
    }

    val nameLength: Int

    init {
        nameLength = name.length
        println("Second init block")
    }
}
```

### 3. Secondary Constructors

Declared with `constructor` keyword. If a primary constructor exists, each secondary constructor must delegate to it (directly or via another secondary constructor):

```kotlin
class Person(val name: String) {
    var age: Int = 0

    constructor(name: String, age: Int) : this(name) {
        this.age = age
    }
}
```

**Initialization order (within a class):**

1. Primary constructor parameters are evaluated.
2. Then, property initializers and init blocks in the class body are executed in the exact order they appear top-to-bottom.
3. After that, the secondary constructor body (if used) is executed.

**Example showing order:**
```kotlin
class Example(val param: String) {
    val prop1 = "Property 1".also { println("1: $it") }

    init {
        println("2: First init block")
    }

    val prop2 = "Property 2".also { println("3: $it") }

    init {
        println("4: Second init block")
    }

    constructor(param: String, extra: String) : this(param) {
        println("5: Secondary constructor")
    }
}

// Output when calling secondary constructor:
// 1: Property 1
// 2: First init block
// 3: Property 2
// 4: Second init block
// 5: Secondary constructor
```

**Inheritance-related initialization notes (concise):**
- When a subclass is created, its base class is initialized first.
- A subclass constructor must delegate to one of the superclass constructors.
- The base class's property initializers and init blocks run before the subclass's property initializers and init blocks, and then the subclass constructor body is executed.

**Important rules:**
- If a primary constructor exists, each secondary constructor must delegate to it via `this(...)` (directly or through another secondary constructor).
- Init blocks and property initializers are executed in the order they appear in the class body, before the body of a secondary constructor.
- Properties can be initialized directly at declaration or inside init blocks.

## Дополнительные Вопросы (Follow-ups, RU)

- Как взаимодействуют делегированные свойства и ленивые инициализаторы с порядком инициализации в классах Kotlin?
- Как ведет себя порядок инициализации в `open` классах и при переопределении свойств?
- Как инициализаторы взаимодействуют с `companion object` инициализацией?

## Follow-ups

- How do property delegation and lazy initialization interact with the initialization order in Kotlin classes?
- How does initialization order behave with `open` classes and overridden properties?
- How do class initializers interact with `companion object` initialization?

## Связанные Вопросы (RU)

- [[q-actor-pattern--kotlin--hard]]

## Related Questions

- [[q-actor-pattern--kotlin--hard]]

