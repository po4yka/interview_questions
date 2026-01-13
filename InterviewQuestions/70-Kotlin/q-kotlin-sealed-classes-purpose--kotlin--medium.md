---
'---id': lang-082
title: Kotlin Sealed Classes Purpose / Назначение sealed классов в Kotlin
aliases:
- Kotlin Sealed Classes Purpose
- Назначение sealed классов в Kotlin
topic: kotlin
subtopics:
- sealed-classes
- type-system
question_kind: theory
difficulty: medium
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
- c-sealed-classes
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
- q-expect-actual-kotlin--kotlin--medium
- q-kotlin-reified-types--kotlin--hard
created: 2025-10-15
updated: 2025-11-10
tags:
- difficulty/medium
- oop
- programming-languages
- sealed-classes
- type-hierarchy
- when-expressions
anki_cards:
- slug: q-kotlin-sealed-classes-purpose--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-kotlin-sealed-classes-purpose--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Что Такое Sealed Классы И Зачем Они Нужны?

# Вопрос (RU)
> Что такое sealed классы и зачем они нужны?

---

# Question (EN)
> What are sealed classes and why are they needed?

## Ответ (RU)

Sealed классы в Kotlin (см. [[c-sealed-classes]]) позволяют **ограничить набор подклассов**, которые могут быть созданы для класса, обеспечивая контролируемую, закрытую иерархию: все разрешённые наследники должны находиться в том же модуле и в том же пакете, что и sealed-тип (при этом они могут быть в разных файлах).

Для sealed interface действуют те же правила (наследники в том же модуле и пакете, могут быть в разных файлах).

**Зачем они нужны:**

1. **Конечный набор состояний**: Идеально подходят для данных, которые могут иметь ограниченное число чётко определённых состояний.
```kotlin
sealed class Result<out T> {
    data class Success<out T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

2. **Исчерпывающие when-выражения**: Компилятор может проверять, что все случаи охвачены (без ветки `else`), если все возможные наследники sealed-типа находятся в том же модуле и видимы, и `when` используется как выражение.
```kotlin
when (result) {
    is Result.Success -> showData(result.data)
    is Result.Error -> showError(result.message)
    Result.Loading -> showLoading()
    // 'else' не нужен - компилятор знает все варианты в иерархии Result
}
```

3. **Типобезопасность**: Все возможные подтипы известны во время компиляции в пределах модуля, где определён sealed-тип, что помогает избежать непредусмотренных вариантов и позволяет компилятору поддерживать исчерпывающие проверки.

4. **Гибче, чем enum**: Каждый подкласс может иметь собственные свойства и методы; поддерживаются data классы, объекты и обычные классы.

**Преимущества:**
- Код более безопасен и понятен
- Компилятор помогает отловить пропущенные случаи в `when`
- Лучше, чем использовать несколько nullable полей для представления альтернатив
- Идеально для конечных автоматов, ответов API, навигации

## Answer (EN)

Sealed classes in Kotlin (see [[c-sealed-classes]]) allow you to **restrict the set of subclasses** that can be created for a class, providing a controlled, closed hierarchy: all permitted direct subclasses must be in the same module and the same package as the sealed type (they may live in different files).

The same rules apply to sealed interfaces (subclasses in the same module and package, possibly in different files).

**Why they're needed:**

1. **Finite set of states**: Perfect for data that can have a limited number of well-defined states.
```kotlin
sealed class Result<out T> {
    data class Success<out T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

2. **Exhaustive when expressions**: The compiler can verify that all cases are covered (without an `else` branch) when all sealed subclasses are known and visible in the same module and `when` is used as an expression.
```kotlin
when (result) {
    is Result.Success -> showData(result.data)
    is Result.Error -> showError(result.message)
    Result.Loading -> showLoading()
    // No 'else' needed - the compiler knows all variants in the Result hierarchy
}
```

3. **Type safety**: All possible subtypes are known at compile time within the defining module, which prevents unexpected variants and enables exhaustive compile-time checks.

4. **More flexible than enums**: Each subclass can have its own properties and behavior; you can use data classes, objects, and regular classes.

**Benefits:**
- Code is safer and more readable
- The compiler helps catch missing branches in `when`
- Better than using multiple nullable fields to model alternatives
- Great for state machines, API responses, navigation flows

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-null-checks-methods--kotlin--easy]]
- [[q-expect-actual-kotlin--kotlin--medium]]
- [[q-kotlin-reified-types--kotlin--hard]]
