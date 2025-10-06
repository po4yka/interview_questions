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
---

# Как в Kotlin определить класс, который не может быть унаследован?

**English**: How to define a class in Kotlin that cannot be inherited?

## Answer

In Kotlin, to define a class that **cannot be inherited**, you simply declare it **without the `open` keyword**. All classes in Kotlin are `final` by default.

**Default behavior (final):**
```kotlin
class FinalClass  // Cannot be inherited (final by default)

// Attempting to inherit will cause a compilation error:
// class Derived : FinalClass()  // Error: This type is final
```

**Explicit `final` keyword (optional, already default):**
```kotlin
final class ExplicitlyFinalClass  // Redundant, but allowed

// Same as:
class ImplicitlyFinalClass  // final by default
```

**To allow inheritance, use `open`:**
```kotlin
open class OpenClass  // Can be inherited

class Derived : OpenClass()  // OK
```

**Preventing further inheritance:**
```kotlin
open class Base

open class Middle : Base()  // Can be inherited further

class Final : Middle()  // Cannot be inherited (final by default)

// This will NOT compile:
// class MoreDerived : Final()  // Error
```

**Explicitly preventing override of inherited methods:**
```kotlin
open class Base {
    open fun foo() {}
}

class Derived : Base() {
    final override fun foo() {}  // Prevent further overriding
}

class MoreDerived : Derived() {
    // override fun foo() {}  // Error: foo is final
}
```

**Summary:**

| Approach | Syntax | Inheritable? |
|----------|--------|-------------|
| Default (final) | `class MyClass` | ❌ No |
| Explicit final | `final class MyClass` | ❌ No (redundant) |
| Open | `open class MyClass` | ✅ Yes |
| Abstract | `abstract class MyClass` | ✅ Yes (always open) |
| Sealed | `sealed class MyClass` | ✅ Limited (same file/package) |

**Best practice:**
- Don't use explicit `final` keyword (it's the default)
- Just omit `open` to make a class non-inheritable
- This is the recommended approach for most classes

## Ответ

В Kotlin для определения класса, который не может быть унаследован, используется ключевое слово 'final'. По умолчанию все классы в Kotlin являются финальными и не могут быть унаследованы без явного указания 'open'. Таким образом, чтобы определить класс который не может быть унаследован достаточно просто объявить его без ключевого слова 'open'.

