---
---
---id: lang-024
title: "Runtime Generic Access / Доступ к дженерикам во время выполнения"
aliases: [Runtime Generic Access, Доступ к дженерикам во время выполнения]
topic: kotlin
subtopics: [generics, reification, type-system]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml, q-kotlin-generics--kotlin--hard, q-kotlin-reified-types--kotlin--hard, q-reified-type-parameters--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/hard, generics, kotlin, programming-languages, reified, type-erasure]

---
# Вопрос (RU)
> Можно ли получить в runtime доступ к типу дженерика?

---

# Question (EN)
> Can you access generic type at runtime?

## Ответ (RU)

По умолчанию — нельзя (на JVM), так как дженерики стираются (type erasure) во время компиляции: в runtime `List<String>` и `List<Int>` выглядят одинаково как `List`.

В Kotlin (на JVM) есть исключения и обходные пути:

- В `inline`-функциях можно объявлять `reified` type parameter: `inline fun <reified T> ...`. Для таких параметров компилятор подставляет конкретный тип, и в теле функции можно обращаться к `T::class`, `T::class.java` и вызывать `typeOf<T>()`.
- В объявлениях (например, `class Box<T>(val value: T)` или `val property: List<String>`) сигнатуры с дженериками (generic signatures) сохраняются в метаданных байткода, и через reflection можно получить информацию о аргументах типа у свойств, полей, суперклассов и интерфейсов. Но фактический runtime-тип объекта по-прежнему стерт: экземпляр `List<String>` в рантайме имеет raw-тип `List`, а не отдельный `List<String>`.
- Можно явно передавать `KClass<*>` или `Class<*>` / `KClass<T>` параметром (например, `fun <T: Any> parse(json: String, type: KClass<T>)`), но это обычно даёт доступ только к классу, а не к полным параметрам сложных дженериков без дополнительных оберток (type tokens).
- Для сложных дженериков (например, `List<T>`, `Map<K, V>`) `typeOf<T>()` в сочетании с `reified` и `inline` позволяет получить `KType` с информацией о параметрах типа на месте вызова.

Ключевая идея (для JVM): без специальных механизмов (`reified` в `inline`-функциях, reflection над декларациями, явная передача type tokens) тип параметра дженерика `T` недоступен в runtime из-за type erasure. См. также .

## Answer (EN)

By default (on the JVM), no: generics use type erasure during compilation, so at runtime `List<String>` and `List<Int>` both appear as raw `List`.

In Kotlin (on the JVM) there are exceptions and workarounds:

- In `inline` functions you can declare a `reified` type parameter: `inline fun <reified T> ...`. For such parameters the compiler substitutes the concrete type, so inside the function you can use `T::class`, `T::class.java`, and call `typeOf<T>()`.
- For declarations (e.g., `class Box<T>(val value: T)` or `val property: List<String>`) generic signatures are stored in the bytecode metadata, and via reflection you can inspect type arguments of properties, fields, supertypes, and interfaces. However, the actual runtime type of an instance is still erased: an instance of `List<String>` has the raw runtime type `List`, not a distinct `List<String>`.
- You can explicitly pass a `KClass<*>` or `KClass<T>` / `Class<*>` argument (e.g., `fun <T: Any> parse(json: String, type: KClass<T>)`), but this usually gives you only the class, not full generic arguments of complex types, unless you introduce additional wrappers (type tokens).
- For complex generics (e.g., `List<T>`, `Map<K, V>`) `typeOf<T>()` combined with `reified` and `inline` allows you to obtain a `KType` including type argument information at the call site.

Key idea (for JVM): without special mechanisms (reified inline functions, reflection on declarations, or explicitly passing type tokens), a generic type parameter `T` is not available at runtime because of type erasure.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия от Java?
- Когда это используется на практике?
- Каковы типичные подводные камни?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

### Понятия
- [[c-kotlin]]

### Связанные (Тот же уровень)
- [[q-kotlin-reified-types--kotlin--hard]]
- [[q-kotlin-generics--kotlin--hard]]

### Предпосылки (Легче)
- [[q-reified-type-parameters--kotlin--medium]]

## Related Questions

### Concepts
- [[c-kotlin]]

### Related (Same Level)
- [[q-kotlin-reified-types--kotlin--hard]]
- [[q-kotlin-generics--kotlin--hard]]

### Prerequisites (Easier)
- [[q-reified-type-parameters--kotlin--medium]]
