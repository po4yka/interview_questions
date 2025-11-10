---
id: lang-041
title: "Kotlin Extensions / Расширения Kotlin"
aliases: [Kotlin Extensions, Расширения Kotlin]
topic: kotlin
subtopics: [extensions, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-flow-basics--kotlin--easy, q-kotlin-extensions-overview--programming-languages--medium]
created: 2024-10-15
updated: 2025-11-09
tags: [difficulty/easy, extension-functions, extensions, programming-languages]
---
# Вопрос (RU)
> Что такое Extensions?

---

# Question (EN)
> What are Extensions?

## Ответ (RU)

Термин **"Extensions"** используется для обозначения функциональности в Kotlin, которая позволяет добавлять новые возможности к существующим классам без изменения их исходного кода. См. также [[c-kotlin]].

### Ключевые Концепции

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

### Важные Замечания

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

## Answer (EN)

The term **"Extensions"** refers to functionality in Kotlin that allows adding new capabilities to existing classes without modifying their source code. See also [[c-kotlin]].

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

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия extensions от подхода в Java?
- Когда на практике стоит использовать extensions?
- Какие распространенные ошибки и подводные камни при использовании extensions?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-kotlin-extensions-overview--programming-languages--medium]]
- [[q-flow-basics--kotlin--easy]]

## Related Questions

- [[q-kotlin-extensions-overview--programming-languages--medium]]
- [[q-flow-basics--kotlin--easy]]
