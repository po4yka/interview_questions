---
id: lang-029
title: "Kotlin Extensions Overview / Обзор расширений Kotlin"
aliases: [Kotlin Extensions Overview, Обзор расширений Kotlin]
topic: kotlin
subtopics: [extensions, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-channel-pipelines--kotlin--hard, q-supervisor-scope-vs-coroutine-scope--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, extension-functions, extension-properties, extensions, kotlin]
---
# Вопрос (RU)
> Что известно про extension?

# Question (EN)
> What do you know about extensions?

## Ответ (RU)

Extension-функции и свойства в Kotlin позволяют объявлять дополнительную функциональность для существующих типов без их модификации или наследования. Важно: расширения не изменяют сам класс и его бинарный API (они не добавляют реальные методы в класс и не участвуют в виртуальной таблице); это синтаксический сахар, который компилируется в обычные статические функции с параметром-получателем.

Extension-функции объявляются с указанием типа-получателя перед именем функции и вызываются как обычные методы:

```kotlin
fun String.lastChar(): Char = this[this.length - 1]

val c = "test".lastChar()
```

Extension-свойства объявляются похожим образом, но не могут иметь собственного хранимого состояния (нет backing field) — только getter (и, при необходимости, setter):

```kotlin
val String.firstChar: Char
    get() = this[0]
```

Ключевые свойства:
- Расширения не могут получать доступ к private или protected членам исходного класса, только к его публичному/видимому API.
- Разрешение extension-функций происходит статически по типу ссылки, а не по реальному типу объекта (в отличие от виртуальных методов).
- Если имя совпадает у member-функции и extension-функции с подходящей сигнатурой, при вызове приоритет всегда у member-функции.
- Можно объявлять расширения для nullable-типов (например, `fun String?.isNullOrEmpty(): Boolean`), что удобно для безопасной обработки `null`.

Преимущества: улучшение читаемости и выразительности кода, удобная организация утилитарной логики рядом с типами, которые она расширяет, и повышение гибкости без вмешательства в исходные классы.

## Answer (EN)

Extension functions and properties in Kotlin let you declare additional functionality for existing types without modifying them or using inheritance. Important: extensions do not actually change the class or its binary API (they do not add real methods to the class or affect its vtable); they are syntactic sugar compiled into static functions with a receiver parameter.

Extension functions are declared by putting the receiver type before the function name and are called like regular methods:

```kotlin
fun String.lastChar(): Char = this[this.length - 1]

val c = "test".lastChar()
```

Extension properties are declared similarly but cannot have their own backing field (no stored state) — only a getter (and optionally a setter):

```kotlin
val String.firstChar: Char
    get() = this[0]
```

Key characteristics:
- Extensions cannot access private or protected members of the original class; they work only with its visible public API.
- Extension function resolution is static and based on the declared type of the expression, not the runtime type (unlike virtual methods).
- If a member function and an extension function have the same signature, the member function always takes precedence at the call site.
- You can declare extensions on nullable types (e.g., `fun String?.isNullOrEmpty(): Boolean`), which is convenient for safe null handling.

Benefits: improved readability and expressiveness, better organization of utility logic close to the types it relates to, and increased flexibility without modifying third-party or standard library classes.

## Дополнительные вопросы (RU)

- Каковы ключевые отличия расширений в Kotlin от подходов в Java?
- Когда вы бы использовали расширения на практике?
- Каковы распространенные подводные камни при использовании расширений?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-supervisor-scope-vs-coroutine-scope--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]
- [[q-channel-pipelines--kotlin--hard]]

## Related Questions

- [[q-supervisor-scope-vs-coroutine-scope--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]
- [[q-channel-pipelines--kotlin--hard]]
