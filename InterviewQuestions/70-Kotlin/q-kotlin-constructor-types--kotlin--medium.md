---id: lang-211
title: "Kotlin Constructor Types / Типы конструкторов Kotlin"
aliases: ["Kotlin constructor types", "Типы конструкторов Kotlin"]
topic: kotlin
subtopics: [type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-abstract-class-vs-interface--kotlin--medium, q-advanced-coroutine-patterns--kotlin--hard]
created: 2024-10-15
updated: 2025-11-11
tags: [difficulty/medium, kotlin/type-system]
---
# Вопрос (RU)
> Какие типы конструкторов есть у классов в Kotlin?

# Question (EN)
> What types of constructors do classes in Kotlin have?

---

## Ответ (RU)

В Kotlin есть два типа конструкторов: **первичный конструктор** и **вторичные конструкторы**.

**1. Первичный конструктор**

Объявляется в заголовке класса и может сразу объявлять и инициализировать свойства:

```kotlin
class User(val name: String, val age: Int)  // Первичный конструктор

// Использование:
val user = User("Alice", 30)
println(user.name)  // Alice
```

**С блоком init:**
```kotlin
class User(val name: String, val age: Int) {
    init {
        println("Пользователь создан: $name, возраст $age")
        require(age >= 0) { "Возраст должен быть неотрицательным" }
    }
}
```

**Со значениями по умолчанию:**
```kotlin
class User(val name: String, val age: Int = 0)

val user1 = User("Alice", 30)
val user2 = User("Bob")  // age по умолчанию 0
```

**2. Вторичные конструкторы**

Объявляются внутри тела класса с ключевым словом `constructor` и предоставляют дополнительные способы создания объекта:

```kotlin
class User {
    var name: String
    var age: Int

    // Вторичный конструктор
    constructor(name: String, age: Int) {
        this.name = name
        this.age = age
    }

    // Ещё один вторичный конструктор
    constructor(name: String) : this(name, 0)
}
```

**3. Первичный + вторичные конструкторы**

Если у класса есть первичный конструктор, каждый вторичный конструктор обязан делегировать ему напрямую или через другой вторичный конструктор:

```kotlin
class User(val name: String) {  // Первичный
    var age: Int = 0

    // Вторичный должен (напрямую или через другой) вызвать первичный через this()
    constructor(name: String, age: Int) : this(name) {
        this.age = age
    }

    // Ещё один вторичный конструктор
    constructor(name: String, age: Int, email: String) : this(name, age) {
        println("Email: $email")
    }
}
```

**Порядок выполнения:**

```kotlin
class User(val name: String) {
    val id: Int

    init {
        println("1. Init-блок")
        id = name.hashCode()
    }

    constructor(name: String, age: Int) : this(name) {
        println("2. Вторичный конструктор")
    }
}

val user = User("Alice", 30)
// Вывод:
// 1. Init-блок (первичный конструктор и init-блоки выполняются при делегации)
// 2. Вторичный конструктор (тело вторичного конструктора выполняется после делегации)
```

**Сравнение:**

| Характеристика | Первичный конструктор | Вторичный конструктор |
|----------------|------------------------|------------------------|
| Расположение | В заголовке класса | В теле класса |
| Ключевое слово | `constructor` может быть опущен | Требуется `constructor` |
| Объявление свойств | Можно объявлять свойства через `val`/`var` | Нельзя объявлять свойства прямо в списке параметров |
| Init-блоки | Выполняются при инициализации, в том числе при делегации из вторичных конструкторов | Должны делегировать другому конструктору; `init`-блоки выполняются как часть этой делегации |
| Количество | Только один первичный | Может быть несколько |
| Значения по умолчанию | Поддерживаются в параметрах | Дополнительные формы инициализации обычно реализуются через комбинацию вторичных конструкторов и/или значения по умолчанию в первичном |

**Рекомендуемые практики (Когда что использовать):**
- Предпочитать первичный конструктор как основной способ инициализации
- Использовать значения по умолчанию в первичном конструкторе вместо избыточных вторичных конструкторов
- Использовать вторичные конструкторы:
  - для дополнительных способов создания объектов (оверлоады),
  - для Java-/framework-интеропа и требуемых сигнатур,
  - когда ограничения по сигнатурам нельзя выразить только через аргументы по умолчанию
- Не дублировать логику инициализации в разных конструкторах — выносить её в первичный конструктор и/или `init`-блоки

---

## Answer (EN)

Kotlin has two types of constructors: **primary constructors** and **secondary constructors**.

**1. Primary Constructor**

Declared in the class header, can initialize class properties directly:

```kotlin
class User(val name: String, val age: Int)  // Primary constructor

// Usage:
val user = User("Alice", 30)
println(user.name)  // Alice
```

**With init block:**
```kotlin
class User(val name: String, val age: Int) {
    init {
        println("User created: $name, age $age")
        require(age >= 0) { "Age must be non-negative" }
    }
}
```

**With default values:**
```kotlin
class User(val name: String, val age: Int = 0)

val user1 = User("Alice", 30)
val user2 = User("Bob")  // age defaults to 0
```

**2. Secondary Constructor**

Declared inside the class body with `constructor` keyword:

```kotlin
class User {
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

**3. Primary + Secondary Constructors**

If a class has a primary constructor, every secondary constructor must delegate to the primary constructor directly or indirectly via another secondary constructor:

```kotlin
class User(val name: String) {  // Primary
    var age: Int = 0

    // Secondary must (directly or indirectly) call the primary via this()
    constructor(name: String, age: Int) : this(name) {
        this.age = age
    }

    // Another secondary constructor
    constructor(name: String, age: Int, email: String) : this(name, age) {
        println("Email: $email")
    }
}
```

**Execution order:**

```kotlin
class User(val name: String) {
    val id: Int

    init {
        println("1. Init block")
        id = name.hashCode()
    }

    constructor(name: String, age: Int) : this(name) {
        println("2. Secondary constructor")
    }
}

val user = User("Alice", 30)
// Output:
// 1. Init block (primary constructor + init blocks run during delegation)
// 2. Secondary constructor (secondary constructor body runs after delegation)
```

**Comparison:**

| Feature | Primary Constructor | Secondary Constructor |
|---------|--------------------|-----------------------|
| Location | Class header | Class body |
| Keyword | Optional `constructor` | Required `constructor` |
| Property declaration | Yes (`val`/`var`) | No direct property declarations in the parameter list |
| Init blocks | Executed during initialization when called via primary; also run when secondary constructors delegate to the primary | Must delegate to another constructor; `init` blocks run as part of that delegation |
| Multiple | Only one | Multiple allowed |
| Default values | Supported in parameters | Typically rely on primary constructors with default parameters instead of many secondary constructors |

**When to use each:**

- Primary constructor:
  - Default choice for most classes
  - Simple initialization
  - Direct property declaration

- Secondary constructor:
  - Multiple ways to create objects (overloads)
  - Interop with Java or frameworks requiring specific signatures
  - When you need constructor overloads that cannot be expressed only via default arguments

**Best practices:**
- Prefer primary constructor with default values and `init` blocks for initialization
- Use secondary constructors only when necessary
- Ensure all secondary constructors correctly delegate and do not duplicate initialization logic

---

## Related Questions

- [[q-abstract-class-vs-interface--kotlin--medium]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]

---

## Дополнительные Вопросы (RU)

- Как `init`-блоки взаимодействуют с первичными и вторичными конструкторами в более сложных сценариях наследования?
- Когда стоит предпочесть фабричные функции или методы `companion object` вторичным конструкторам в Kotlin?
- Как сравнить использование аргументов по умолчанию и оверлоадов через вторичные конструкторы при проектировании API?

## Follow-ups

- How do `init` blocks interact with primary and secondary constructors in more complex inheritance scenarios?
- When should you prefer factory functions or companion object methods over secondary constructors in Kotlin?
- How do default arguments compare to overloading via secondary constructors in real-world API design?

## Ссылки (RU)

- [[moc-kotlin]]
- [[q-abstract-class-vs-interface--kotlin--medium]]

## References

- [[moc-kotlin]]
- [[q-abstract-class-vs-interface--kotlin--medium]]
