---
id: 20251012-12271111115
title: "Kotlin Constants / Константы в Kotlin"
topic: computer-science
difficulty: easy
status: draft
moc: moc-kotlin
related: [q-inline-function-limitations--kotlin--medium, q-kotlin-native--kotlin--hard, q-kotlin-extensions-overview--programming-languages--medium]
created: 2025-10-15
tags:
  - const
  - constants
  - fundamentals
  - immutability
  - kotlin
  - programming-languages
  - val
---
# Что такое константы и можно ли их изменять?

# Question (EN)
> What are constants and can they be changed?

# Вопрос (RU)
> Что такое константы и можно ли их изменять?

---

## Answer (EN)

Constants are fixed values that cannot be changed after their definition. They are used to define values that remain unchanged throughout program execution.

**In Kotlin:**

- **`val`**: Immutable variable (read-only), value assigned once at runtime
```kotlin
val name = "John" // Cannot reassign
```

- **`const val`**: Compile-time constant (must be top-level or in object, primitive or String)
```kotlin
const val MAX_SIZE = 100 // Known at compile time
```

**Key differences:**
- `val` can be initialized at runtime
- `const val` must be known at compile time
- `const val` can only be used with primitive types and String

Constants are **immutable** - their value cannot be changed after definition.

---

## Ответ (RU)

Константы — это фиксированные значения, которые не могут быть изменены после их определения. Они используются для определения значений, которые остаются неизменными на протяжении всего выполнения программы.

**В Kotlin:**

- **`val`**: Неизменяемая переменная (только для чтения), значение присваивается один раз во время выполнения
```kotlin
val name = "John" // Нельзя переназначить
```

- **`const val`**: Константа времени компиляции (должна быть на верхнем уровне или в object, только примитивы или String)
```kotlin
const val MAX_SIZE = 100 // Известна во время компиляции
```

**Ключевые различия:**
- `val` может быть инициализирована во время выполнения
- `const val` должна быть известна во время компиляции
- `const val` может использоваться только с примитивными типами и String

Константы **неизменяемы** — их значение не может быть изменено после определения.

## Related Questions

- [[q-inline-function-limitations--kotlin--medium]]
- [[q-kotlin-native--kotlin--hard]]
- [[q-kotlin-extensions-overview--programming-languages--medium]]
