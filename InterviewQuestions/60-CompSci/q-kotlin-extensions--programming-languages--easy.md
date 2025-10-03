---
id: 20251003-140002
title: Kotlin Extensions / Расширения в Kotlin
aliases: [Extensions, Extension Functions, Расширения Kotlin, Функции расширения]

# Classification
topic: programming-languages
subtopics: [kotlin, extensions]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/765
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-extensions
  - c-extension-functions
  - c-extension-properties

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags (EN only; no leading #)
tags: [kotlin, extensions, extension-functions, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What are Extensions?

# Вопрос (RU)
> Что такое Extensions?

---

## Answer (EN)

The term **'Extensions'** refers to functionality that allows adding new capabilities to existing classes without modifying their source code.

### Key Concepts

**Extension Functions** allow you to add new functions to existing classes:
```kotlin
fun String.removeSpaces(): String {
    return this.replace(" ", "")
}

// Usage
val text = "Hello World"
val result = text.removeSpaces()  // "HelloWorld"
```

**Extension Properties** allow you to add new properties:
```kotlin
val String.lastChar: Char
    get() = this[length - 1]

// Usage
val text = "Hello"
println(text.lastChar)  // 'o'
```

### Benefits

1. **Clean code**: Add functionality without inheritance or wrappers
2. **Readable**: Extension functions can be called like regular methods
3. **Type-safe**: Resolved at compile time
4. **Library-friendly**: Extend third-party classes you can't modify

### Important Notes

- Extensions are resolved **statically** (at compile time)
- Cannot override existing members
- Useful for adding utility functions to standard library classes

**Example with standard library**:
```kotlin
fun List<Int>.average(): Double {
    return this.sum().toDouble() / this.size
}

val numbers = listOf(1, 2, 3, 4, 5)
println(numbers.average())  // 3.0
```

## Ответ (RU)

Термин **'Extensions'** используется для обозначения функциональности, которая позволяет добавлять новые возможности к существующим классам без изменения их исходного кода.

### Ключевые концепции

**Функции расширения** позволяют добавлять новые функции к существующим классам:
```kotlin
fun String.removeSpaces(): String {
    return this.replace(" ", "")
}

// Использование
val text = "Hello World"
val result = text.removeSpaces()  // "HelloWorld"
```

**Свойства расширения** позволяют добавлять новые свойства:
```kotlin
val String.lastChar: Char
    get() = this[length - 1]

// Использование
val text = "Hello"
println(text.lastChar)  // 'o'
```

### Преимущества

1. **Чистый код**: Добавление функциональности без наследования или обёрток
2. **Читаемость**: Функции расширения вызываются как обычные методы
3. **Типобезопасность**: Разрешаются во время компиляции
4. **Дружественность к библиотекам**: Расширение сторонних классов, которые нельзя изменить

### Важные замечания

- Расширения разрешаются **статически** (во время компиляции)
- Не могут переопределять существующие члены
- Полезны для добавления утилитарных функций к классам стандартной библиотеки

**Пример со стандартной библиотекой**:
```kotlin
fun List<Int>.average(): Double {
    return this.sum().toDouble() / this.size
}

val numbers = listOf(1, 2, 3, 4, 5)
println(numbers.average())  // 3.0
```

---

## Follow-ups
- Can extensions access private members of a class?
- What's the difference between extension functions and member functions?
- How do extensions work with inheritance?
- Can you create generic extension functions?

## References
- [[c-kotlin-extensions]]
- [[c-extension-functions]]
- [[c-extension-properties]]
- [Kotlin Extensions Documentation](https://kotlinlang.org/docs/extensions.html)

## Related Questions
- [[q-kotlin-scope-functions--programming-languages--medium]]
- [[q-kotlin-generics--programming-languages--medium]]
