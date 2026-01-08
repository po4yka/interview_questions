---id: lang-060
title: "Kotlin IntRange / IntRange в Kotlin"
aliases: [IntRange в Kotlin, Kotlin IntRange]
topic: kotlin
subtopics: [collections, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml, q-kotlin-constructors--kotlin--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy, intrange, iteration, programming-languages, ranges]
---
# Вопрос (RU)
> Что такое `IntRange`?

---

# Question (EN)
> What is `IntRange`?

## Ответ (RU)

`IntRange` — это **диапазон целых чисел**, представляющий все целые значения от `start` до `endInclusive` с шагом `1` (наследуется от `IntProgression`). Чаще всего используется для итераций, проверки вхождения числа в диапазон и в условных выражениях.

Важно: выражения с `step` и `downTo` возвращают `IntProgression`, а не `IntRange`, хотя используются похожим образом в циклах.

См. также: [[c-kotlin]]

### Создание IntRange

**Используя оператор `..` (включительно):**
```kotlin
val range: IntRange = 1..10      // 1, 2, 3, ..., 10
```

**Используя конструктор (эквивалентно `..`):**
```kotlin
val range = IntRange(1, 10)      // 1, 2, 3, ..., 10
```

### Другие Диапазоны И Прогрессии

**Диапазон символов (`CharRange`):**
```kotlin
val charRange = 'a'..'z'         // Диапазон символов
```

**`until` (конец не включается, возвращает `IntRange`):**
```kotlin
val untilRange = 1 until 10      // 1, 2, 3, ..., 9 (не включает 10)
```

**`downTo` (по убыванию, возвращает `IntProgression`):**
```kotlin
val down = 10 downTo 1           // 10, 9, 8, ..., 1
```

**С шагом (`IntProgression`):**
```kotlin
val stepRange = 1..10 step 2         // 1, 3, 5, 7, 9 (IntProgression)
val desc = 10 downTo 1 step 2        // 10, 8, 6, 4, 2 (IntProgression)
```

### Использование

**В циклах:**
```kotlin
for (i in 1..5) {
    println(i)  // Выведет: 1 2 3 4 5
}

for (i in 10 downTo 1 step 2) {
    println(i)  // Выведет: 10 8 6 4 2
}
```

**Проверка вхождения:**
```kotlin
val range = 1..10
val isInRange = 5 in range      // true
val isNotInRange = 15 !in range // true
```

**Свойства `IntRange` / `IntProgression`:**
```kotlin
val range = 1..10
println(range.first)  // 1
println(range.last)   // 10
println(range.step)   // 1
```

### Распространённые Операции

```kotlin
val range = 1..10

// Преобразование в список (материализация значений)
val list = range.toList()  // [1, 2, 3, ..., 10]

// Проверка на пустоту
val isEmpty = range.isEmpty()  // false для 1..10

// filter/map работают через итерацию по прогрессии
val evens = range.filter { it % 2 == 0 }  // [2, 4, 6, 8, 10]
```

**`IntRange`** — это конкретная реализация целочисленного диапазона (наследник `IntProgression` с шагом 1) и часть семейства типов прогрессий Kotlin вместе с `LongRange`, `CharRange` и др.

## Answer (EN)

`IntRange` is a **range of integers** representing all integer values from `start` to `endInclusive` with a fixed step of `1` (it extends `IntProgression`). It is commonly used for iteration, membership checks, and conditional expressions.

Important: expressions using `step` or `downTo` produce an `IntProgression`, not an `IntRange`, even though they behave similarly in loops.

See also: [[c-kotlin]]

### Creating IntRange

**Using `..` operator (inclusive):**
```kotlin
val range: IntRange = 1..10      // 1, 2, 3, ..., 10
```

**Using the constructor (equivalent to `..`):**
```kotlin
val range = IntRange(1, 10)      // 1, 2, 3, ..., 10
```

### Other Ranges and Progressions

**Character range (`CharRange`):**
```kotlin
val charRange = 'a'..'z'         // Character range
```

**`until` (exclusive end, returns `IntRange`):**
```kotlin
val untilRange = 1 until 10      // 1, 2, 3, ..., 9 (excludes 10)
```

**`downTo` (descending, returns `IntProgression`):**
```kotlin
val down = 10 downTo 1           // 10, 9, 8, ..., 1
```

**With step (`IntProgression`):**
```kotlin
val stepRange = 1..10 step 2         // 1, 3, 5, 7, 9 (IntProgression)
val desc = 10 downTo 1 step 2        // 10, 8, 6, 4, 2 (IntProgression)
```

### Usage

**In loops:**
```kotlin
for (i in 1..5) {
    println(i)  // Prints: 1 2 3 4 5
}

for (i in 10 downTo 1 step 2) {
    println(i)  // Prints: 10 8 6 4 2
}
```

**Checking membership:**
```kotlin
val range = 1..10
val isInRange = 5 in range      // true
val isNotInRange = 15 !in range // true
```

**Range / progression properties:**
```kotlin
val range = 1..10
println(range.first)  // 1
println(range.last)   // 10
println(range.step)   // 1
```

### Common Operations

```kotlin
val range = 1..10

// Convert to list (materialize the values)
val list = range.toList()  // [1, 2, 3, ..., 10]

// Check if empty
val isEmpty = range.isEmpty()  // false for 1..10

// filter/map work by iterating over the progression
val evens = range.filter { it % 2 == 0 }  // [2, 4, 6, 8, 10]
```

**`IntRange`** is a specific integer range implementation (an `IntProgression` with step 1) and part of Kotlin's progression types family along with `LongRange`, `CharRange`, etc.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия `IntRange` от аналогичных конструкций в Java?
- Когда на практике стоит использовать `IntRange`?
- Какие распространенные ошибки и подводные камни связаны с использованием диапазонов?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-kotlin-constructors--kotlin--easy]]
- [[q-coroutine-context-elements--kotlin--hard]]

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-constructors--kotlin--easy]]
- [[q-coroutine-context-elements--kotlin--hard]]
