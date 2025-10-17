---
id: "20251015082237115"
title: "Kotlin Any Inheritance / Наследование от Any в Kotlin"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - any
  - inheritance
  - kotlin
  - object
  - programming-languages
  - type-hierarchy
  - type-system
---
# Все классы Kotlin наследуются от Any

# Question (EN)
> All Kotlin classes inherit from Any

# Вопрос (RU)
> Все классы Kotlin наследуются от Any

---

## Answer (EN)

In Kotlin, **all classes by default inherit from the `Any` class**. This class is the root (base) class for all other classes in Kotlin. It is analogous to the `Object` class in Java.

**Key points:**

- **Any** is the supertype of all non-nullable types
- Analogous to Java's `Object` class
- Every class implicitly extends `Any` (even without explicit declaration)

**Any provides three methods:**
```kotlin
open class Any {
    public open operator fun equals(other: Any?): Boolean
    public open fun hashCode(): Int
    public open fun toString(): String
}
```

**Example:**
```kotlin
class MyClass  // Implicitly extends Any

val obj: Any = MyClass()  // Can assign to Any
obj.toString()            // Methods from Any available
obj.equals(obj)
obj.hashCode()
```

**Type hierarchy:**
```
Any (root)
 String
 Int
 List<T>
 YourCustomClass
```

**Note**: For nullable types, the root is `Any?`

---

## Ответ (RU)

В Kotlin все классы по умолчанию наследуются от класса Any. Этот класс является корневым (базовым) классом для всех других классов в Kotlin. Он аналогичен классу Object в Java.

