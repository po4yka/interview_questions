---
id: lang-059
title: "Kotlin Generic Function Syntax / Синтаксис обобщенных функций Kotlin"
aliases: [Kotlin Generic Function Syntax, Синтаксис обобщенных функций Kotlin]
topic: programming-languages
subtopics: [generics, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-sealed-classes-features--programming-languages--medium, q-retrofit-coroutines-best-practices--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy, functions, generics, programming-languages, syntax, type-parameters]
date created: Friday, October 31st 2025, 6:29:34 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---
# Какой Синтаксис Используется Для Объявления Обобщенной Функции В Kotlin?

# Вопрос (RU)
> Какой синтаксис используется для объявления обобщенной функции в Kotlin?

---

# Question (EN)
> What syntax is used to declare a generic function in Kotlin?

## Ответ (RU)

Для объявления обобщенной функции в Kotlin используются угловые скобки `<T>` перед именем функции:

**Синтаксис:**
```kotlin
fun <T> functionName(parameter: T): T {
    // тело функции
}
```

**Примеры:**
```kotlin
// Простая обобщенная функция
fun <T> identity(value: T): T {
    return value
}

// Несколько параметров типа
fun <K, V> mapOf(key: K, value: V): Map<K, V> {
    return mapOf(key to value)
}

// С ограничениями типа
fun <T : Comparable<T>> max(a: T, b: T): T {
    return if (a > b) a else b
}

// Использование
val result = identity(42)        // T выводится как Int
val name = identity("Hello")     // T выводится как String
```

**Размещение параметра типа:**
- Перед именем функции: `fun <T> name()`
- Перед extension receiver: `fun <T> T.extension()`

## Answer (EN)

To declare a generic function in Kotlin, use angle brackets `<T>` before the function name:

**Syntax:**
```kotlin
fun <T> functionName(parameter: T): T {
    // function body
}
```

**Examples:**
```kotlin
// Simple generic function
fun <T> identity(value: T): T {
    return value
}

// Multiple type parameters
fun <K, V> mapOf(key: K, value: V): Map<K, V> {
    return mapOf(key to value)
}

// With type constraints
fun <T : Comparable<T>> max(a: T, b: T): T {
    return if (a > b) a else b
}

// Usage
val result = identity(42)        // T inferred as Int
val name = identity("Hello")     // T inferred as String
```

**Type parameter placement:**
- Before function name: `fun <T> name()`
- Before extension receiver: `fun <T> T.extension()`

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

-
- [[q-kotlin-sealed-classes-features--programming-languages--medium]]
- [[q-retrofit-coroutines-best-practices--kotlin--medium]]
