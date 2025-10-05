---
tags:
  - kotlin
  - extensions
  - extension-functions
  - easy_kotlin
  - programming-languages
difficulty: easy
---

# Что такое Extensions?

**English**: What are Extensions?

## Answer

**Extensions** are functionality that allows **adding new capabilities to existing classes** without modifying their source code or using inheritance.

**Key characteristics:**

- Add methods/properties to existing classes
- No need to inherit or modify original class
- Resolved statically (compile-time)
- Cannot access private members

**Extension functions:**
```kotlin
// Add function to String class
fun String.addExclamation(): String {
    return this + "!"
}

// Usage
val result = "Hello".addExclamation()  // "Hello!"
```

**Extension properties:**
```kotlin
// Add property to String
val String.firstChar: Char
    get() = this[0]

// Usage
val first = "Hello".firstChar  // 'H'
```

**Why extensions are useful:**

1. **Extend existing classes**: Add utility methods to standard library classes
2. **No inheritance needed**: Works with final classes
3. **Better code organization**: Group related functions
4. **DSL creation**: Build domain-specific languages

**Example with standard library:**
```kotlin
// These are extension functions!
val list = listOf(1, 2, 3)
list.filter { it > 1 }    // Extension on List
list.map { it * 2 }       // Extension on List

"hello".capitalize()       // Extension on String
```

**Limitations:**
- Cannot override existing members
- Resolved statically (not polymorphic)
- Cannot access private members of the class

## Ответ

Термин 'Extensions' используется для обозначения функциональности, которая позволяет добавлять новые возможности к существующим классам без изменения их исходного кода.

