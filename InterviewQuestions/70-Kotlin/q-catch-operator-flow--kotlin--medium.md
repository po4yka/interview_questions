---
id: kotlin-070
title: "Catch Operator in Kotlin Flow / Оператор catch в Kotlin Flow"
aliases: [Catch Operator in Kotlin Flow, Оператор catch в Kotlin Flow]
topic: kotlin
subtopics: [coroutines, error-handling, flow]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: internal
source_note: Deep dive into catch operator in Kotlin Flow
status: draft
moc: moc-kotlin
related: [c-flow, q-flow-basics--kotlin--easy, q-flow-exception-handling--kotlin--medium, q-retry-operators-flow--kotlin--medium]
created: 2025-10-12
updated: 2025-11-09
tags: [coroutines, difficulty/medium, error-handling, flow, lang/kotlin, topic/kotlin]
---
# Вопрос (RU)

> Как работает оператор `catch` в Kotlin `Flow`? Что такое прозрачность исключений и где размещать `catch` в конвейере?

---

# Question (EN)

> How does the `catch` operator work in Kotlin `Flow`? What is exception transparency and where should `catch` live in the pipeline?

---

## Ответ (RU)

**Краткое резюме**: `catch` перехватывает только исключения, возникшие "выше по течению" (`upstream`) в том же `Flow`, поддерживая принцип прозрачности исключений и позволяя либо излучить значение восстановления/альтернативный поток, либо перевыбросить ошибку.

- Конвейер остаётся декларативным; обработка ошибок читается так же, как и основная логика.
- `catch` не видит ошибки, возникшие после него (включая `collect`, терминальные операторы, `onEach`, `stateIn` и т. п.).
- Внутри `catch` используйте `emit`, преобразование ошибок в доменные типы или явный `throw`; избегайте молчаливого "проглатывания" исключений.

### Прозрачность Исключений

Прозрачность исключений в Kotlin Flow означает, что промежуточные операторы не должны скрывать исключения `downstream` и должны явно управлять `upstream`-ошибками. `catch` следует этому принципу: он
- перехватывает только исключения, выброшенные в предыдущих (upstream) операторах/блоках,
- может логировать, преобразовывать или повторно выбрасывать исключения,
- не должен неожиданно скрывать ошибки, из-за чего потребитель не узнает о сбое.

```kotlin
val usersFlow = flow {
    emit(fetchUsers())
    emit(fetchCached())
}.catch { throwable ->
    logger.warn("Loading users failed", throwable)
    emit(emptyList())
}
```

Дополнительно см. [[c-flow]] и [[c-coroutines]] для базовых понятий.

### Где Располагать `catch`

- Размещайте `catch` сразу после части конвейера, которая может бросать исключения (`flow {}`, `map`, `transform` и др.), чтобы явно ограничить область перехвата.
- Используйте отдельные `catch` для независимых участков конвейера с разной политикой восстановления.
- Исключения на стороне коллектора (внутри `collect { ... }`, UI-обновления, ошибки в `stateIn` / `onEach` и т. п.) `catch` не перехватывает — оборачивайте такие блоки в `try/catch` или используйте `runCatching`. `onCompletion` можно использовать для наблюдения за завершением и логирования `cause`, но не как замену `try/catch` вокруг `collect`.

```kotlin
repository.getUsers()
    .map { user -> user.toUiModel() }
    .catch { emit(emptyList()) }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(),
        initialValue = emptyList()
    )
```

### Типовые Шаблоны

- **Восстановление**: излучайте кеш/дефолт или переводите в доменный тип ошибки (например, `Result.Error`).
- **Повторные попытки**: комбинируйте с `retry` / `retryWhen` до `catch`, чтобы `catch` обрабатывал финальный провал после всех ретраев.
- **Диагностика**: логируйте и, при необходимости, транслируйте ошибку дальше; избегайте тихого подавления, которое ломает прозрачность исключений.

```kotlin
fun loadProduct(id: String): Flow<Result<Product>> = flow {
    emit(Result.Success(api.load(id)))
}.retry(2) { it is IOException }
 .catch { emit(Result.Error(it.message ?: "Unknown error")) }
```

### Отличия От `try-catch`

- `try-catch` внутри `flow {}` локален и императивен; `catch` — декларативный оператор, который охватывает весь upstream-участок конвейера.
- `catch` облегчает повторное использование и компоновку операторов, так как политика обработки ошибок задаётся как часть цепочки.
- Комбинируйте оба подхода для блоков с явным ресурс-менеджментом, но сохраняйте прозрачность исключений: не перехватывайте чужие ошибки так, чтобы их невозможно было наблюдать.

### Практические Советы

- Используйте специализированные типы ошибок или обёртки (`Result`, `Either`) там, где важно явно кодировать результат.
- Поддерживайте согласованный доменный тип значений: излучайте во `Flow` однородные по типу элементы.
- Документируйте контракт конвейера рядом с `catch`, чтобы ожидания по поведению при ошибках были очевидны.
- Для UI-потоков избегайте блокирующих вызовов в `catch`; тяжёлую работу переносите на `Dispatchers.IO`.

Больше рекомендаций в [[c-structured-concurrency]].

---

## Answer (EN)

**TL;DR**: `catch` intercepts only exceptions thrown upstream in the same `Flow`, preserves exception transparency, and lets you either emit a recovery value/alternative flow or rethrow the error.

- Error handling stays declarative and colocated with the pipeline.
- `catch` does not see exceptions that happen after it (including inside `collect`, terminal operators, `onEach`, `stateIn`, etc.).
- Inside `catch`, prefer emitting domain-safe values or mapping to domain error types, or explicitly rethrowing; avoid silently swallowing failures.

### Exception Transparency

Exception transparency in Kotlin Flow means intermediate operators must not catch and hide exceptions from downstream operators, and should manage upstream errors explicitly. `catch` follows this rule:
- it intercepts only exceptions from preceding (upstream) operators/blocks,
- it may log, transform, or rethrow exceptions,
- it should not make failures invisible to collectors unintentionally.

```kotlin
val usersFlow = flow {
    emit(fetchUsers())
    emit(fetchCached())
}.catch { throwable ->
    logger.warn("Loading users failed", throwable)
    emit(emptyList())
}
```

See [[c-flow]] and [[c-coroutines]] for foundational context.

### Placing `catch`

- Place `catch` immediately after the pipeline segment that may throw (`flow {}`, `map`, `transform`, etc.) to scope what it handles.
- Use multiple `catch` operators when independent stages have different recovery policies.
- `catch` does not handle collector-side failures (inside `collect {}`, UI updates, or errors in `stateIn` / `onEach` etc.). Wrap those in `try/catch` or `runCatching`. You can use `onCompletion` to observe termination and the `cause`, but it does not replace `try/catch` for handling exceptions thrown during collection.

```kotlin
repository.getUsers()
    .map { user -> user.toUiModel() }
    .catch { emit(emptyList()) }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(),
        initialValue = emptyList()
    )
```

### Common Patterns

- **Recovery**: emit cached/default data or map failures to a domain `Result.Error`.
- **Retry combo**: place `retry` / `retryWhen` before `catch` so `catch` handles only the terminal failure after retries are exhausted.
- **Diagnostics**: log and (when appropriate) propagate; avoid silent failures that violate transparency.

```kotlin
fun loadProduct(id: String): Flow<Result<Product>> = flow {
    emit(Result.Success(api.load(id)))
}.retry(2) { it is IOException }
 .catch { emit(Result.Error(it.message ?: "Unknown error")) }
```

### How it Differs from `try-catch`

- A `try-catch` inside `flow {}` is local and imperative; `catch` is a declarative operator that covers the upstream chain.
- `catch` keeps pipelines composable by centralizing error-handling policy in the flow chain.
- Combine both where scoped resource management or cleanup is clearer, but preserve exception transparency: do not hide errors that downstream code expects to observe.

### Practical Guidance

- Use domain-specific wrappers (`Result`, `Either`) when explicit success/failure modeling is desired.
- Emit consistent element types to keep collectors simple and type-safe.
- Co-locate comments/docs with `catch` to make error-handling contracts discoverable.
- Offload heavy recovery work to `Dispatchers.IO`; keep UI collectors light and non-blocking.

Additional best practices live in [[c-structured-concurrency]].

---

## Follow-ups

- How do you pair `catch` with `retry` or `retryWhen` for resilient pipelines?
- When is it better to transform exceptions into sealed results versus rethrowing?
- How can `catch` cooperate with `stateIn`/`shareIn` to avoid stuck UI state?
- What strategies help test flows that rely on `catch`-driven recovery?

## References

- [[c-flow]]
- [[c-coroutines]]
- [[c-structured-concurrency]]
- [Kotlin Flow Exception Transparency](https://kotlinlang.org/docs/flow.html#exception-transparency)
- [Flow catch operator API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/catch.html)

## Related Questions

- [[q-flow-basics--kotlin--easy]]
- [[q-flow-exception-handling--kotlin--medium]]
- [[q-retry-operators-flow--kotlin--medium]]
- [[q-flowon-operator-context-switching--kotlin--hard]]

## MOC Links

- [[moc-kotlin]]
