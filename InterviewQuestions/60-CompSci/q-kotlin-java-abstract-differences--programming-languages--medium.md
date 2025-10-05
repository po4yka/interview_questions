---
tags:
  - kotlin
  - java
  - abstract
  - oop
  - inheritance
  - open
  - easy_kotlin
  - programming-languages
difficulty: medium
---

# Какое главное отличие между Java и Kotlin касательно абстрактных классов и методов?

**English**: What is the main difference between Java and Kotlin regarding abstract classes and methods?

## Answer

The main difference is how **overriding** is handled:

### Java
- **Abstract methods** implicitly allow overriding (no keyword needed)
- **Non-abstract methods** are final by default (cannot override without explicitly making them non-final)
- Must explicitly mark as `abstract` or `final`

```java
abstract class Animal {
    abstract void makeSound();     // Can override (implicit)
    void sleep() { }               // Cannot override (final by default)

    // Must explicitly allow overriding:
    public void eat() { }          // Still final!
}
```

### Kotlin
- **Abstract members** are `open` by default (can be overridden)
- **Non-abstract members** are `final` by default (must use `open` to allow overriding)
- More explicit about inheritance intentions

```kotlin
abstract class Animal {
    abstract fun makeSound()       // Can override (open by default)
    fun sleep() { }                // Cannot override (final by default)

    open fun eat() { }             // Must use 'open' to allow overriding
}
```

**Comparison table:**

| Member type | Java | Kotlin |
|-------------|------|--------|
| Abstract method | Implicitly overridable | `open` by default |
| Regular method | Final unless overridden | `final` unless marked `open` |
| Abstract class | Can be extended | Can be extended |

**Philosophy difference:**
- **Java**: Abstract methods are automatically overridable
- **Kotlin**: Explicit `open` keyword required for non-abstract methods

This makes Kotlin's inheritance model **more explicit and intentional**.

## Ответ

В Kotlin абстрактные классы и методы по умолчанию open, что позволяет их переопределять без явного указания модификатора open. В Java абстрактные методы всегда подразумевают переопределение, а обычные методы должны быть явно помечены abstract или final.

