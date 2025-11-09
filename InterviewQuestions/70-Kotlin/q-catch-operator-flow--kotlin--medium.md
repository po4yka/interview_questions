---
id: kotlin-070
title: "Catch Operator in Kotlin Flow / Оператор catch в Kotlin Flow"
aliases:
    - Catch Operator in Kotlin Flow
    - Оператор catch в Kotlin Flow
topic: kotlin
subtopics: [flow, coroutines, error-handling]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: internal
source_note: Deep dive into catch operator in Kotlin Flow
status: draft
moc: moc-kotlin
related:
    [
        q-flow-basics--kotlin--easy,
        q-flow-exception-handling--kotlin--medium,
        q-retry-operators-flow--kotlin--medium,
    ]
created: 2025-10-12
updated: 2025-11-07
tags:
    [
        difficulty/medium,
        lang/kotlin,
        topic/kotlin,
        flow,
        coroutines,
        error-handling,
    ]
---

# Вопрос (RU)

> Как работает оператор `catch` в Kotlin Flow? Что такое прозрачность исключений и где размещать `catch` в конвейере?

---

# Question (EN)

> How does the `catch` operator work in Kotlin Flow? What is exception transparency and where should `catch` live in the pipeline?

---

## Ответ (RU)

**Краткое резюме**: `catch` перехватывает только `upstream`-исключения в `Flow`, поддерживая принцип прозрачности исключений и позволяя либо излучить значение восстановления, либо перевыбросить ошибку.

-   Конвейер остаётся декларативным; обработка ошибок читается так же, как и основная логика.
-   `catch` не видит ошибки, возникшие после него (в `collect`, `onEach`, `stateIn`).
-   Для согласованности используйте `emit`, `throw` или преобразование ошибок (например, в `Result`).

### Прозрачность исключений

Исключения в Kotlin Flow текут вниз по конвейеру так же, как значения. `catch` работает поверх этого принципа: он может логировать, преобразовывать или повторно выбрасывать исключения, но не должен их «глотать».

```kotlin
val usersFlow = flow {
    emit(fetchUsers())
    emit(fetchCached())
}.catch { throwable ->
    logger.warn("Network failed", throwable)
    emit(emptyList())
}
```

Дополнительно см. [[c-flow]] и [[c-coroutines]] для базовых понятий.

### Где располагать `catch`

-   Размещайте оператор сразу после блока, потенциально выбрасывающего исключения (`flow {}`, `map`, `transform`).
-   Используйте отдельные `catch` для независимых участков конвейера.
-   Для ошибок в `collect` применяйте обёртки вроде `runCatching` или `onCompletion`.

```kotlin
repository.getUsers()
    .map { user -> user.toUiModel() }
    .catch { emit(emptyList()) }
    .stateIn(scope = viewModelScope, started = SharingStarted.WhileSubscribed(), initialValue = emptyList())
```

### Типовые шаблоны

-   **Восстановление**: излучайте кеш/дефолт либо конструируйте `Result.Error`.
-   **Повторные попытки**: комбинируйте с `retry` до `catch`, чтобы `catch` обрабатывал финальный провал.
-   **Диагностика**: логируйте, но избегайте молчаливого подавления.

```kotlin
fun loadProduct(id: String): Flow<Result<Product>> = flow {
    emit(Result.Success(api.load(id)))
}.retry(2) { it is IOException }
 .catch { emit(Result.Error(it.message ?: "Unknown error")) }
```

### Отличия от `try-catch`

-   `try-catch` внутри `flow {}` локален и императивен; `catch` охватывает весь upstream и остаётся декларативным.
-   `catch` облегчает повторное использование и компоновку операторов.
-   Для сложного блокирующего кода комбинируйте оба подхода, но придерживайтесь прозрачности исключений.

### Практические советы

-   Используйте специализированные типы ошибок или обёртки (`Result`, `Either`).
-   Поддерживайте неизменность состояния: излучайте значения однотипного домена.
-   Документируйте контракт конвейера рядом с `catch`, чтобы ожидания были очевидны.
-   Для потоков UI избегайте блокирующих вызовов в `catch`; переносите тяжёлую работу на `Dispatchers.IO`.

Больше рекомендаций в [[c-structured-concurrency]].

---

## Answer (EN)

**TL;DR**: `catch` intercepts only upstream exceptions in a `Flow`, preserves exception transparency, and lets you either emit a recovery value or rethrow the error.

-   Error handling stays declarative and colocated with the pipeline.
-   `catch` cannot see downstream failures (e.g., inside `collect`, `onEach`, `stateIn`).
-   Prefer emitting domain-safe values, rethrowing, or wrapping errors into a sealed result.

### Exception transparency

Exceptions move downstream just like data. `catch` observes that stream: log, transform, or rethrow, but avoid swallowing errors silently.

```kotlin
val usersFlow = flow {
    emit(fetchUsers())
    emit(fetchCached())
}.catch { throwable ->
    logger.warn("Network failed", throwable)
    emit(emptyList())
}
```

See [[c-flow]] and [[c-coroutines]] for foundational context.

### Placing `catch`

-   Place it immediately after operators that may throw (`flow {}`, `map`, `transform`).
-   Use multiple `catch` blocks when independent stages have different recovery logic.
-   For collector-side failures, wrap `collect` in `runCatching` or lean on `onCompletion`.

```kotlin
repository.getUsers()
    .map { user -> user.toUiModel() }
    .catch { emit(emptyList()) }
    .stateIn(scope = viewModelScope, started = SharingStarted.WhileSubscribed(), initialValue = emptyList())
```

### Common patterns

-   **Recovery**: emit cached/default data or map to `Result.Error`.
-   **Retry combo**: place `retry` before `catch` so `catch` handles the terminal failure.
-   **Diagnostics**: log and propagate; avoid silent failures.

```kotlin
fun loadProduct(id: String): Flow<Result<Product>> = flow {
    emit(Result.Success(api.load(id)))
}.retry(2) { it is IOException }
 .catch { emit(Result.Error(it.message ?: "Unknown error")) }
```

### How it differs from `try-catch`

-   `try-catch` inside `flow {}` is local and imperative; `catch` remains declarative and covers the upstream chain.
-   `catch` keeps pipelines composable; multiple operators can share the same policy.
-   Combine both when block-level cleanup is clearer, but honour exception transparency.

### Practical guidance

-   Use domain-specific error wrappers (`Result`, `Either`) for clarity.
-   Emit consistent types to keep collectors simple.
-   Co-locate documentation/comments with `catch` so the contract is discoverable.
-   Offload heavy recovery work to `Dispatchers.IO` and keep UI collectors lightweight.

Additional best practices live in [[c-structured-concurrency]].

---

## Follow-ups

-   How do you pair `catch` with `retry` or `retryWhen` for resilient pipelines?
-   When is it better to transform exceptions into sealed results versus rethrowing?
-   How can `catch` cooperate with `stateIn`/`shareIn` to avoid stuck UI state?
-   What strategies help test flows that rely on `catch`-driven recovery?

## References

-   [[c-flow]]
-   [[c-coroutines]]
-   [[c-structured-concurrency]]
-   [Kotlin Flow Exception Transparency](https://kotlinlang.org/docs/flow.html#exception-transparency)
-   [Flow catch operator API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/catch.html)

## Related Questions

-   [[q-flow-basics--kotlin--easy]]
-   [[q-flow-exception-handling--kotlin--medium]]
-   [[q-retry-operators-flow--kotlin--medium]]
-   [[q-flowon-operator-context-switching--kotlin--hard]]

## MOC Links

-   [[moc-kotlin]]
