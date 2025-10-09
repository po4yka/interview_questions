---
tags:
  - class-design
  - classes
  - final
  - inheritance
  - keywords
  - kotlin
  - open
  - programming-languages
difficulty: easy
status: reviewed
---

# Какой тип наследования по умолчанию используется для классов в Kotlin?

**English**: What is the default inheritance type for classes in Kotlin?

## Answer

In Kotlin, **all classes are `final` by default**, meaning they cannot be inherited. To make a class inheritable, you must explicitly mark it with the **`open` keyword**.

**Default (final):**
```kotlin
class FinalClass  // Cannot be inherited

// This will NOT compile:
// class Derived : FinalClass()  // Error: This type is final, so it cannot be inherited from
```

**Open for inheritance:**
```kotlin
open class BaseClass  // Can be inherited

class Derived : BaseClass()  // OK
```

**Why final by default?**

1. **Effective Java recommendation**: "Design for inheritance or prohibit it"
2. **Safety**: Prevents unexpected behavior from inheritance
3. **Performance**: Final classes allow compiler optimizations
4. **Explicit intent**: Forces developers to explicitly design for inheritance

**Comparison with Java:**

| Language | Default | To allow inheritance |
|----------|---------|---------------------|
| Kotlin | `final` (closed) | Mark with `open` |
| Java | Open (can be inherited) | Mark with `final` to prevent |

**Methods also follow this rule:**
```kotlin
open class Base {
    fun finalMethod() {}  // Cannot be overridden (final by default)

    open fun openMethod() {}  // Can be overridden
}

class Derived : Base() {
    // override fun finalMethod() {}  // Error

    override fun openMethod() {}  // OK
}
```

**Abstract classes are always open:**
```kotlin
abstract class AbstractBase  // No need for 'open' keyword

class Derived : AbstractBase()  // OK
```

**Sealed classes (restricted inheritance):**
```kotlin
sealed class Result  // Subclasses must be in same file/package

class Success : Result()
class Error : Result()
```

**Best practice:**
- Keep classes `final` by default
- Use `open` only when inheritance is intentional
- Consider `sealed` for controlled hierarchies
- Use `abstract` when subclasses must implement behavior

## Ответ

В Kotlin все классы по умолчанию являются финальными, то есть они не могут быть наследованы. Для того чтобы класс можно было наследовать, его необходимо объявить с ключевым словом `open`.

