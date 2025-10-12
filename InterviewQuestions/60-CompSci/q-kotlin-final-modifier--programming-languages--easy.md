---
tags:
  - class-modifiers
  - classes
  - final
  - inheritance
  - kotlin
  - open
  - programming-languages
  - syntax
difficulty: easy
status: draft
---

# Какой модификатор в Kotlin делает класс нерасширяемым?

# Question (EN)
> Which modifier makes a class non-extendable in Kotlin?

# Вопрос (RU)
> Какой модификатор в Kotlin делает класс нерасширяемым?

---

## Answer (EN)

In Kotlin, the `final` modifier makes a class non-extendable. However, **all classes in Kotlin are `final` by default**. To make a class extendable, you must explicitly use the `open` keyword.

**Example:**
```kotlin
// Final class (default) - cannot be inherited
class FinalClass {
    // ...
}

// Open class - can be inherited
open class OpenClass {
    // ...
}

// This will compile:
class Derived : OpenClass()

// This will NOT compile:
// class Derived : FinalClass()  // Error: class is final
```

**Key points:**
- Unlike Java where classes are open by default, Kotlin classes are `final` by default
- Use `open` keyword to allow inheritance
- This design encourages composition over inheritance
- Sealed classes are another way to control inheritance hierarchy

---

## Ответ (RU)

В Kotlin модификатор `final` делает класс нерасширяемым. Однако все классы в Kotlin являются `final` по умолчанию. Чтобы сделать класс расширяемым, необходимо явно использовать ключевое слово `open`.

