---
id: 20251012-12271111109
title: "Kotlin Access Modifiers / Модификаторы доступа Kotlin"
aliases: []
topic: computer-science
subtopics: [functions, access-modifiers, class-features]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-intrange--programming-languages--easy, q-suspend-functions-deep-dive--kotlin--medium, q-semaphore-rate-limiting--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - 
  - difficulty/medium
---
# Что известно про модификатор доступа?

# Question (EN)
> What is known about access modifiers?

# Вопрос (RU)
> Что известно про модификатор доступа?

---

## Answer (EN)

Access modifiers control the visibility of classes, methods, interfaces, and variables in your code. They are essential language features that help manage encapsulation by limiting data and method visibility.

**Kotlin Access Modifiers:**

**1. `public` (default)**
- Visible everywhere
- Default if no modifier specified

```kotlin
class PublicClass  // Visible everywhere
public fun publicFunction() {}  // Explicitly public
```

**2. `private`**
- **Top-level:** Visible only in the same file
- **Class member:** Visible only inside the class

```kotlin
// File: Example.kt
private class PrivateClass  // Only in this file

class Outer {
    private val privateField = 42  // Only in Outer

    fun access() {
        println(privateField)  // OK
    }
}

fun test() {
    val outer = Outer()
    // outer.privateField  // Error: private
}
```

**3. `protected`**
- **Only for class members** (not for top-level declarations)
- Visible in the class and its subclasses

```kotlin
open class Base {
    protected val protectedField = 42
}

class Derived : Base() {
    fun access() {
        println(protectedField)  // OK in subclass
    }
}

fun test() {
    val base = Base()
    // base.protectedField  // Error: protected
}
```

**4. `internal`**
- Visible within the same **module** (unique to Kotlin)
- Module = set of files compiled together (e.g., Gradle module)

```kotlin
internal class InternalClass  // Visible in same module
internal fun internalFunction() {}  // Visible in same module
```

**Comparison: Kotlin vs Java**

| Modifier | Kotlin | Java |
|----------|--------|------|
| `public` | Default, visible everywhere | Visible everywhere |
| `private` | File-level or class-only | Class-only |
| `protected` | Class + subclasses | Class + subclasses + package |
| `internal` | Module-level | - No equivalent |
| (no modifier) | Same as `public` | Package-private (default) |

**Visibility Table:**

| Modifier | Same Class | Same File | Subclass | Same Module | Outside Module |
|----------|------------|-----------|----------|-------------|----------------|
| `private` | - | - (top-level) | - | - | - |
| `protected` | - | - | - | - | - |
| `internal` | - | - | - | - | - |
| `public` | - | - | - | - | - |

**Best Practices:**
- Use the most restrictive modifier possible
- Prefer `private` for implementation details
- Use `internal` for module-internal APIs
- Use `public` only for public APIs
- Use `protected` sparingly (breaks encapsulation)

---

## Ответ (RU)

Модификаторы доступа используются для управления доступом к классам, методам, интерфейсам и переменным в вашем коде. Это важные элементы языка, которые помогают управлять инкапсуляцией в программе, ограничивая видимость данных и методов. Существуют четыре основных модификатора доступа: public, private, protected, internal.

## Related Questions

- [[q-kotlin-intrange--programming-languages--easy]]
- [[q-suspend-functions-deep-dive--kotlin--medium]]
- [[q-semaphore-rate-limiting--kotlin--medium]]
