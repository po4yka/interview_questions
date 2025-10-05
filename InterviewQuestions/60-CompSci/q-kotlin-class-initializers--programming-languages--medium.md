---
tags:
  - kotlin
  - constructors
  - init
  - initialization
  - oop
  - primary-constructor
  - secondary-constructor
  - easy_kotlin
  - programming-languages
difficulty: medium
---

# Расскажи про инициализаторы в классах в Kotlin

**English**: Tell me about class initializers in Kotlin

## Answer

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

## Ответ

В Kotlin инициализаторы используются для выполнения кода при создании экземпляра класса. Первичный конструктор объявляется в заголовке класса и используется для основной инициализации. Вторичные конструкторы объявляются с помощью constructor...

