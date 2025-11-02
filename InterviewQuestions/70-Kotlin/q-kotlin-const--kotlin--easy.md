---
id: kotlin-017
title: "Const Keyword in Kotlin / Ключевое слово const в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [compile-time-constants, const, properties]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-java-primitives--programming-languages--medium, q-structured-concurrency-kotlin--kotlin--medium, q-visibility-modifiers-kotlin--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [compile-time-constants, const, difficulty/easy, kotlin, properties]
date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---

# Question (EN)
> What is the `const` keyword in Kotlin?
# Вопрос (RU)
> Что такое ключевое слово `const` в Kotlin?

---

## Answer (EN)

If the value of a read-only property is known at the compile time, mark it as a **compile time constant** using the `const` modifier. Such properties need to fulfil the following requirements:

### Requirements for Const

1. **Top-level, or member of an `object declaration` or a `companion object`** - The constant must be declared at the top level of a file, inside an object, or inside a companion object
2. **Initialized with a value of type `String` or a primitive type** - Can only be String or primitive types (Int, Long, Float, Double, Boolean, Char, Byte, Short)
3. **No custom getter** - The property cannot have a custom getter

### Example

```kotlin
// Top-level const
const val MAX_USERS = 100
const val API_KEY = "your-api-key-here"

class Configuration {
    companion object {
        // Const in companion object
        const val TIMEOUT = 5000
        const val BASE_URL = "https://api.example.com"
    }
}

object AppConstants {
    // Const in object
    const val VERSION = "1.0.0"
    const val DEBUG_MODE = true
}
```

### Const Val Vs Val

The main difference between `const val` and `val`:

```kotlin
// Compile-time constant - value is inlined at compile time
const val COMPILE_TIME = 100

// Runtime constant - value is determined at runtime
val RUNTIME = calculateValue()

class Example {
    companion object {
        const val CONST_VALUE = 42  // Inlined everywhere it's used
        val REGULAR_VALUE = 42      // Field access at runtime
    }
}
```

### When to Use Const

- **Configuration values** that never change (API endpoints, timeouts, etc.)
- **Magic numbers** that need meaningful names
- **String constants** used throughout the application
- When you want the **best performance** - values are inlined at compile time

### Performance Benefit

```kotlin
const val MAX_SIZE = 1000

fun checkSize(size: Int) {
    if (size > MAX_SIZE) {  // MAX_SIZE is inlined as literal 1000
        throw IllegalArgumentException()
    }
}

// After compilation, effectively becomes:
// if (size > 1000) { ... }
```

**English Summary**: The `const` modifier marks a property as a compile-time constant. It can only be used with primitive types or String, must be top-level or in an object/companion object, and cannot have a custom getter. The value is inlined at compile time for better performance.

## Ответ (RU)

Если значение свойства только для чтения известно во время компиляции, пометьте его как **константу времени компиляции**, используя модификатор `const`. Такие свойства должны соответствовать следующим требованиям:

### Требования К Const

1. **Верхнего уровня, или член `object declaration` или `companion object`** - Константа должна быть объявлена на верхнем уровне файла, внутри object или внутри companion object
2. **Инициализирована значением типа `String` или примитивного типа** - Может быть только String или примитивные типы (Int, Long, Float, Double, Boolean, Char, Byte, Short)
3. **Без пользовательского getter** - Свойство не может иметь пользовательский getter

### Пример

```kotlin
// Const верхнего уровня
const val MAX_USERS = 100
const val API_KEY = "your-api-key-here"

class Configuration {
    companion object {
        // Const в companion object
        const val TIMEOUT = 5000
        const val BASE_URL = "https://api.example.com"
    }
}

object AppConstants {
    // Const в object
    const val VERSION = "1.0.0"
    const val DEBUG_MODE = true
}
```

### Const Val Vs Val

Основное различие между `const val` и `val`:

```kotlin
// Константа времени компиляции - значение встраивается во время компиляции
const val COMPILE_TIME = 100

// Константа времени выполнения - значение определяется во время выполнения
val RUNTIME = calculateValue()

class Example {
    companion object {
        const val CONST_VALUE = 42  // Встраивается везде где используется
        val REGULAR_VALUE = 42      // Доступ к полю во время выполнения
    }
}
```

### Когда Использовать Const

- **Значения конфигурации**, которые никогда не меняются (API endpoints, таймауты и т.д.)
- **Магические числа**, которым нужны осмысленные имена
- **Строковые константы**, используемые во всем приложении
- Когда нужна **лучшая производительность** - значения встраиваются во время компиляции

### Преимущество Производительности

```kotlin
const val MAX_SIZE = 1000

fun checkSize(size: Int) {
    if (size > MAX_SIZE) {  // MAX_SIZE встраивается как литерал 1000
        throw IllegalArgumentException()
    }
}

// После компиляции фактически становится:
// if (size > 1000) { ... }
```

**Краткое содержание**: Модификатор `const` помечает свойство как константу времени компиляции. Он может использоваться только с примитивными типами или String, должен быть верхнего уровня или в object/companion object, и не может иметь пользовательский getter. Значение встраивается во время компиляции для лучшей производительности.

---

## References
- [Properties - Kotlin Documentation](https://kotlinlang.org/docs/reference/properties.html)

## Related Questions
- [[q-kotlin-val-vs-var--kotlin--easy]]
- [[q-object-companion-object--kotlin--medium]]
