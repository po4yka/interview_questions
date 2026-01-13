---
anki_cards:
- slug: q-extension-properties--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-extension-properties--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---id: lang-077
title: "Extension Properties / Расширяющие свойства"
aliases: [Extension Properties, Extension Properties RU]
topic: kotlin
subtopics: [extensions, properties]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, kotlin, programming-languages]
---
# Вопрос (RU)
> Свойства какого вида можно добавить как расширение?

# Question (EN)
> What kind of properties can be added as extensions?

## Ответ (RU)

В Kotlin можно объявлять свойства-расширения (`extension properties`) как `val`, так и `var`, но они не могут иметь собственного backing field. Такие свойства всегда реализуются через функции доступа: `val` — только с кастомным `get()`, `var` — с кастомными `get()` и `set()` (если это требуется). То есть свойства-расширения всегда вычисляемые и не могут хранить состояние внутри самого расширения.

## Answer (EN)

In Kotlin, you can declare extension properties as both `val` and `var`, but they cannot have their own backing field. These properties are always implemented via accessors: `val` with a custom `get()` only, and `var` with custom `get()` and `set()` (if needed). In other words, extension properties are always computed and cannot store state inside the extension itself.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия от Java?
- Когда это стоит использовать на практике?
- Какие распространенные подводные камни стоит учитывать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-what-is-coroutinescope--kotlin--medium]]
- [[q-how-suspend-function-detects-suspension--kotlin--hard]]
- [[q-error-handling-in-coroutines--kotlin--medium]]

## Related Questions

- [[q-what-is-coroutinescope--kotlin--medium]]
- [[q-how-suspend-function-detects-suspension--kotlin--hard]]
- [[q-error-handling-in-coroutines--kotlin--medium]]
