---
tags:
  - classes
  - constructor
  - constructors
  - initialization
  - kotlin
  - primary-constructor
  - programming-languages
  - secondary-constructor
  - syntax
difficulty: easy
status: draft
---

# Какое ключевое слово используется для объявления параметров конструктора в Kotlin?

# Question (EN)
> Which keyword is used to declare constructor parameters in Kotlin?

# Вопрос (RU)
> Какое ключевое слово используется для объявления параметров конструктора в Kotlin?

---

## Answer (EN)

In Kotlin, the **`constructor` keyword** is used to declare **secondary constructors**. However, for **primary constructors**, no keyword is needed — the parameters are declared directly in the class header.

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

// With explicit constructor keyword (rarely needed)
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

**When `constructor` keyword is required:**
- For all secondary constructors
- For primary constructor with annotations or visibility modifiers:

```kotlin
class User @Inject constructor(val repository: Repository)

class Internal private constructor(val id: Int)
```

**Summary:**
- Primary constructor: Usually no `constructor` keyword
- Secondary constructor: Always use `constructor` keyword
- Use `constructor` for primary only when adding annotations/modifiers

---

## Ответ (RU)

В Kotlin ключевое слово `constructor` используется для объявления вторичных конструкторов. Для первичного конструктора ключевое слово не требуется — параметры объявляются непосредственно в заголовке класса.

