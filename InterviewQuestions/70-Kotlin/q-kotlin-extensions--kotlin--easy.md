---
'---id': lang-041
title: Kotlin Extensions / Расширения Kotlin
aliases:
- Kotlin Extensions
- Расширения Kotlin
topic: kotlin
subtopics:
- extensions
- type-system
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-aggregation
- c-app-signing
- c-backend
- c-binary-search
- c-binary-search-tree
- c-binder
- c-biometric-authentication
- c-bm25-ranking
- c-by-type
- c-cap-theorem
- c-ci-cd
- c-ci-cd-pipelines
- c-clean-code
- c-compiler-optimization
- c-compose-modifiers
- c-compose-phases
- c-compose-semantics
- c-computer-science
- c-concurrency
- c-cross-platform-development
- c-cross-platform-mobile
- c-cs
- c-data-classes
- c-data-loading
- c-debugging
- c-declarative-programming
- c-deep-linking
- c-density-independent-pixels
- c-dimension-units
- c-dp-sp-units
- c-dsl-builders
- c-dynamic-programming
- c-espresso-testing
- c-event-handling
- c-folder
- c-functional-programming
- c-gdpr-compliance
- c-gesture-detection
- c-gradle-build-cache
- c-gradle-build-system
- c-https-tls
- c-image-formats
- c-inheritance
- c-jit-aot-compilation
- c-kmm
- c-kotlin
- c-lambda-expressions
- c-lazy-grid
- c-lazy-initialization
- c-level
- c-load-balancing
- c-manifest
- c-memory-optimization
- c-memory-profiler
- c-microservices
- c-multipart-form-data
- c-multithreading
- c-mutablestate
- c-networking
- c-offline-first-architecture
- c-oop
- c-oop-concepts
- c-oop-fundamentals
- c-oop-principles
- c-play-console
- c-play-feature-delivery
- c-programming-languages
- c-properties
- c-real-time-communication
- c-references
- c-scaling-strategies
- c-scoped-storage
- c-security
- c-serialization
- c-server-sent-events
- c-shader-programming
- c-snapshot-system
- c-specific
- c-strictmode
- c-system-ui
- c-test-doubles
- c-test-sharding
- c-testing-pyramid
- c-testing-strategies
- c-theming
- c-to-folder
- c-token-management
- c-touch-input
- c-turbine-testing
- c-two-pointers
- c-ui-testing
- c-ui-ux-accessibility
- c-value-classes
- c-variable
- c-weak-references
- c-windowinsets
- c-xml
- q-flow-basics--kotlin--easy
created: 2024-10-15
updated: 2025-11-09
tags:
- difficulty/easy
- extension-functions
- extensions
- programming-languages
anki_cards:
- slug: q-kotlin-extensions--kotlin--easy-0-en
  language: en
  anki_id: 1769170294021
  synced_at: '2026-01-23T17:03:50.445964'
- slug: q-kotlin-extensions--kotlin--easy-0-ru
  language: ru
  anki_id: 1769170294046
  synced_at: '2026-01-23T17:03:50.448121'
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

## Дополнительные Вопросы (RU)

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

## Связанные Вопросы (RU)

- [[q-kotlin-extensions-overview--kotlin--medium]]
- [[q-flow-basics--kotlin--easy]]

## Related Questions

- [[q-kotlin-extensions-overview--kotlin--medium]]
- [[q-flow-basics--kotlin--easy]]
