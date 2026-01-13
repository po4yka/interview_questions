---
---
---id: lang-026
title: "Kotlin Nullable String Declaration / Объявление nullable String в Kotlin"
aliases: [Kotlin Nullable String Declaration, Объявление nullable String в Kotlin]
topic: kotlin
subtopics: [null-safety, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml, q-coroutine-job-lifecycle--kotlin--medium, q-kotlin-operator-overloading--kotlin--medium, q-launch-vs-async--kotlin--easy]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/easy, null-safety, nullable, programming-languages, string, syntax]
---
# Вопрос (RU)
> Как правильно объявить переменную типа nullable `String` в Kotlin?

# Question (EN)
> How to correctly declare a nullable `String` variable in Kotlin?

## Ответ (RU)

В Kotlin для объявления переменной типа nullable `String` используется **оператор `?`** после типа данных.

**Синтаксис:**
```kotlin
var name: String? = null
```

**Ключевые моменты:**
- `String` — ненулевой тип (не может быть `null`)
- `String?` — nullable тип (может быть `null`)
- Без `?` компилятор не позволит присвоить `null`

**Примеры:**
```kotlin
// Nullable переменные
var nullable: String? = "Hello"
nullable = null  // OK

// Ненулевые переменные
var nonNullable: String = "Hello"
nonNullable = null  // Ошибка компиляции!
```

## Answer (EN)

In Kotlin, to declare a nullable `String` variable, use the **`?` operator** after the data type.

**Syntax:**
```kotlin
var name: String? = null
```

**Key points:**
- `String` - non-nullable type (cannot be `null`)
- `String?` - nullable type (can be `null`)
- Without `?`, compiler won't allow assigning `null`

**Examples:**
```kotlin
// Nullable variables
var nullable: String? = "Hello"
nullable = null  // OK

// Non-nullable variables
var nonNullable: String = "Hello"
nonNullable = null  // Compilation error!
```

## Дополнительные Вопросы (RU)

- Каковы ключевые отличия этого механизма от Java?
- Когда вы бы использовали nullable типы на практике?
- Какие распространенные ошибки следует избегать при работе с nullable типами?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-kotlin-operator-overloading--kotlin--medium]]
- [[q-launch-vs-async--kotlin--easy]]
- [[q-coroutine-job-lifecycle--kotlin--medium]]

## Related Questions

- [[q-kotlin-operator-overloading--kotlin--medium]]
- [[q-launch-vs-async--kotlin--easy]]
- [[q-coroutine-job-lifecycle--kotlin--medium]]
