---
id: 20251012-12271111113
title: "Kotlin Class Initializers / Инициализаторы классов Kotlin"
aliases: []
topic: computer-science
subtopics: [class-features]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-actor-pattern--kotlin--hard, q-zip-parallelism-guarantee--programming-languages--medium, q-channelflow-callbackflow-flow--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - 
  - difficulty/medium
---
# Расскажи про инициализаторы в классах в Kotlin

# Question (EN)
> Tell me about class initializers in Kotlin

# Вопрос (RU)
> Расскажи про инициализаторы в классах в Kotlin

---

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

Execute when primary constructor is called, can have multiple:

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

Declared with `constructor` keyword, must call primary constructor:

```kotlin
class Person(val name: String) {
    var age: Int = 0

    constructor(name: String, age: Int) : this(name) {
        this.age = age
    }
}
```

**Initialization order:**

1. Primary constructor parameters
2. Property initializers (in declaration order)
3. Init blocks (in declaration order)
4. Secondary constructor body

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

**Important rules:**
- If primary constructor exists, secondary must call it via `this(...)`
- Init blocks run before secondary constructor body
- Properties can be initialized in init blocks

---

## Ответ (RU)

В Kotlin есть несколько механизмов инициализации:

### 1. Первичный конструктор (Primary Constructor)

Объявляется в заголовке класса, используется для основной инициализации:

```kotlin
class Person(val name: String, val age: Int) {
    // Свойства инициализируются из первичного конструктора
}
```

### 2. Блоки init

Выполняются при вызове первичного конструктора, может быть несколько:

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

### 3. Вторичные конструкторы (Secondary Constructors)

Объявляются с ключевым словом `constructor`, должны вызывать первичный конструктор:

```kotlin
class Person(val name: String) {
    var age: Int = 0

    constructor(name: String, age: Int) : this(name) {
        this.age = age
    }
}
```

**Порядок инициализации:**

1. Параметры первичного конструктора
2. Инициализаторы свойств (в порядке объявления)
3. Блоки init (в порядке объявления)
4. Тело вторичного конструктора

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

**Важные правила:**
- Если есть первичный конструктор, вторичный должен вызвать его через `this(...)`
- Блоки init выполняются до тела вторичного конструктора
- Свойства могут быть инициализированы в блоках init

## Related Questions

- [[q-actor-pattern--kotlin--hard]]
- [[q-zip-parallelism-guarantee--programming-languages--medium]]
- [[q-channelflow-callbackflow-flow--kotlin--medium]]
