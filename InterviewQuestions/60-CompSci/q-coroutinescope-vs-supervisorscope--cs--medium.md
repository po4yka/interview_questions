---
id: cs-011
title: CoroutineScope vs SupervisorScope / CoroutineScope против SupervisorScope
aliases:
- CoroutineScope vs SupervisorScope
- CoroutineScope против SupervisorScope
topic: cs
subtopics:
- coroutines
- error-handling
- kotlin
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-cs
related:
- c-coroutines
- q-advanced-coroutine-patterns--kotlin--hard
created: 2025-10-15
updated: 2025-11-11
tags:
- coroutines
- coroutinescope
- difficulty/medium
- error-handling
- kotlin
- programming-languages
- supervisorscope
sources:
- https://kotlinlang.org/docs/exception-handling.html
anki_cards:
- slug: cs-011-0-en
  language: en
  anki_id: 1768454342388
  synced_at: '2026-01-15T09:43:17.028132'
- slug: cs-011-0-ru
  language: ru
  anki_id: 1768454342414
  synced_at: '2026-01-15T09:43:17.029670'
---
# Вопрос (RU)
> В чем разница между `coroutineScope` и `supervisorScope`? Когда использовать каждый из них?

# Question (EN)
> What is the difference between `coroutineScope` and `supervisorScope`? When to use each of them?

---

## Ответ (RU)

**Теория Scope Builders:**
`coroutineScope` и `supervisorScope` — suspend-функции, создающие новый scope для structured concurrency. Обе приостанавливают выполнение до завершения всех дочерних корутин. Ключевое различие — в поведении при ошибках: `coroutineScope` ведёт себя как scope с обычным `Job` (failure одной дочерней корутины отменяет всех siblings), `supervisorScope` — как scope с `SupervisorJob` (отмена и failure не распространяются от одного child к другим).

Важно: `supervisorScope` не отключает propagation ошибок вообще. Неперехваченные исключения внутри `supervisorScope` (например, в теле самого scope или из `async` при `await()`) всё равно приводят к завершению этого scope с исключением, которое возвращается вызывающему коду.

**coroutineScope — Кооперативный failure:**

*Теория:* `coroutineScope` создаёт scope с обычным `Job`. Если любая дочерняя корутина завершается с исключением, `Job` отменяется, что отменяет всех siblings. Исключение пробрасывается к родителю (вызывающей suspend-функции). Используется для зависимых задач, где failure одной задачи делает общий результат невалидным.

```kotlin
// ✅ coroutineScope: один failure отменяет всех
suspend fun fetchUserData(userId: Int): UserData = coroutineScope {
    val profile = async { fetchProfile(userId) }
    val settings = async { fetchSettings(userId) }
    val friends = async { fetchFriends(userId) }

    UserData(
        profile.await(),
        settings.await(),
        friends.await()
    )
    // Если любой запрос завершится с исключением, все будут отменены (нужны все данные)
}

// EXAMPLE: Пример failure
suspend fun coroutineScopeFailure() = coroutineScope {
    launch {
        delay(100)
        println("Task 1")
        throw Exception("Task 1 failed!")  // Fails
    }

    launch {
        delay(200)
        println("Task 2")  // Никогда не выполнится — будет отменена
    }
}
// Output: Task 1, Exception: Task 1 failed!
```

**supervisorScope — Независимый failure:**

*Теория:* `supervisorScope` создаёт scope с поведением `SupervisorJob` для дочерних корутин: failure или отмена одной дочерней корутины не приводит к отмене её siblings. Но если внутри `supervisorScope` есть неперехваченное исключение (включая исключение из `async` при `await()`), весь scope завершается с этим исключением, и оно пробрасывается вызывающему.

Используется для независимых задач, где failure одной задачи не должен отменять другие, при этом каждая задача должна обрабатывать свои ошибки локально (или через handler).

```kotlin
// ✅ supervisorScope: failures независимы между siblings
suspend fun loadDashboard(): DashboardData = supervisorScope {
    val news = async {
        try { fetchNews() }
        catch (e: Exception) { emptyList() }
    }

    val weather = async {
        try { fetchWeather() }
        catch (e: Exception) { Weather.Unknown }
    }

    val stocks = async {
        try { fetchStocks() }
        catch (e: Exception) { emptyList() }
    }

    DashboardData(
        news.await(),
        weather.await(),
        stocks.await()
    )
    // Если один widget fails, другие продолжают работать благодаря локальной обработке
}

// ✅ Пример независимого failure для launch
suspend fun supervisorScopeFailure() = supervisorScope {
    launch {
        delay(100)
        println("Task 1")
        throw Exception("Task 1 failed!")  // Ошибка отменяет только эту корутину
    }

    launch {
        delay(200)
        println("Task 2")  // Выполнится — не отменяется из-за Task 1
    }
}
// Output: Task 1, Task 2
```

**Exception Propagation:**

*Теория:*
- В `coroutineScope` неперехваченное исключение любой дочерней корутины отменяет scope и пробрасывается вызывающему коду.
- В `supervisorScope`:
  - неперехваченные исключения у дочерних `launch` не отменяют других siblings, но scope завершится с исключением, если это исключение "поднимается" до уровня scope (и тогда оно будет проброшено вызывающему);
  - для долговременно живущих корутин обычно используют `CoroutineExceptionHandler` или локальный try/catch;
  - `async` в обоих билдерах всегда откладывает проброс исключения до `await()`.

Ключевой момент: `supervisorScope` не делает исключения "тихими" и не "отключает" propagation, он лишь изолирует siblings друг от друга.

```kotlin
// ✅ coroutineScope propagates exceptions
suspend fun coroutineScopePropagation() {
    try {
        coroutineScope {
            launch { throw Exception("Error!") }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // Ловит исключение из дочерней корутины
    }
}

// NOTE: supervisorScope: siblings независимы, но исключения не игнорируются
suspend fun supervisorScopePropagation() {
    try {
        supervisorScope {
            launch { throw Exception("Error!") }  // Не отменит других детей, но исключение не будет поймано этим try/catch
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }
}
// В этом примере исключение из launch не перехватывается внешним try/catch,
// так как launch - fire-and-forget: его исключение обрабатывается как у корутины верхнего уровня.

// ✅ supervisorScope с exception handler для launch-child
suspend fun supervisorWithHandler() {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Handler caught: ${exception.message}")
    }

    supervisorScope {
        launch(handler) {
            throw Exception("Error!")  // Ловится handler, siblings не отменяются
        }
    }
}
```

**Structured Concurrency:**

*Теория:* Оба scope builder'а обеспечивают structured concurrency: вызывающая функция приостанавливается до завершения всех дочерних корутин в этом scope (или их отмены). Родительский scope не завершится, пока все его дети не завершатся. Это уменьшает риск утечек корутин.

```kotlin
// ✅ Оба ждут завершения всех children
suspend fun structuredExample() {
    println("Start")

    coroutineScope {  // или supervisorScope
        launch {
            delay(1000)
            println("Task 1")
        }
        launch {
            delay(2000)
            println("Task 2")
        }
    }

    println("End")  // Выполнится только после Task 1 и Task 2
}
// Output: Start, Task 1, Task 2, End
```

**Когда использовать coroutineScope:**

*Теория:* Используйте `coroutineScope` для зависимых задач, где нужны все результаты. Если одна задача завершается с ошибкой, нет смысла продолжать остальные.
Типичные случаи: совместная загрузка связных данных, многошаговые транзакции, операции, требующие целостности результата.

```kotlin
// ✅ Dependent tasks — нужны все результаты
suspend fun fetchCompleteUser(id: Int): User = coroutineScope {
    val basicInfo = async { fetchBasicInfo(id) }
    val permissions = async { fetchPermissions(id) }
    val preferences = async { fetchPreferences(id) }

    User(
        basicInfo.await(),
        permissions.await(),
        preferences.await()
    )
    // Если любой из вызовов завершится с ошибкой, пользовательский объект нельзя построить консистентно — scope завершится с исключением
}
```

**Когда использовать supervisorScope:**

*Теория:* Используйте `supervisorScope` для независимых задач, где failure одной задачи не должен отменять другие. Каждая задача должна иметь fallback или локальную обработку ошибок.
Типичные случаи: загрузка независимых widgets, параллельные независимые операции, инициализация подсистем приложения.

```kotlin
// ✅ Independent tasks — каждая задача опциональна/изолирована
suspend fun initializeApp() = supervisorScope {
    launch {
        try { initializeAnalytics() }
        catch (e: Exception) { logError("Analytics failed", e) }
    }

    launch {
        try { loadUserPreferences() }
        catch (e: Exception) { logError("Preferences failed", e) }
    }

    launch {
        try { syncData() }
        catch (e: Exception) { logError("Sync failed", e) }
    }
    // Каждая задача обрабатывает свои ошибки и не отменяет других
}
```

**Сравнительная таблица:**

| Характеристика         | coroutineScope                              | supervisorScope                                      |
|------------------------|---------------------------------------------|------------------------------------------------------|
| **Job type (модель)**  | Обычный Job (children взаимозависимы)      | SupervisorJob-поведение (children изолированы)       |
| **Error propagation**  | Один failure отменяет всех siblings        | Failure child не отменяет siblings                   |
| **Exception handling** | Неперехваченное исключение пробрасывается к вызвавшему | Неперехваченное исключение также пробрасывается к вызвавшему, но siblings не отменяются |
| **Use case**           | Зависимые задачи                           | Независимые/опциональные задачи                      |
| **Waiting**            | Ждёт всех children                          | Ждёт всех children                                   |
| **Typical usage**      | Atomic/целостные операции                  | Widgets, подсистемы, tolerant initialization         |

**Ключевые концепции:**

1. **Structured Concurrency** — оба обеспечивают структурированное управление жизненным циклом корутин.
2. **Error Propagation** — отличие в том, распространяется ли failure от одного child на остальных.
3. **Job vs SupervisorJob** — разные модели родительского Job определяют поведение при ошибках.
4. **Explicit Error Handling** — в `supervisorScope` важно явно обрабатывать ошибки дочерних корутин, если вы не хотите падения всего scope.
5. **Task Dependencies** — выбор зависит от зависимостей и требований к изоляции между задачами.

---

## Answer (EN)

**Scope Builders Theory:**
`coroutineScope` and `supervisorScope` are suspend functions that create a new scope for structured concurrency. Both suspend until all child coroutines in that scope complete. The key difference is failure behavior: `coroutineScope` behaves like a scope with a regular `Job` (failure of one child cancels all siblings), `supervisorScope` behaves like a scope with a `SupervisorJob` (failure/cancellation of one child does not cancel its siblings).

Important: `supervisorScope` does not disable exception propagation. Unhandled exceptions inside `supervisorScope` (for example, in the scope body or from `async` when `await()` is called) still cause the scope to complete with that exception, which is then returned to the caller.

**coroutineScope - Cooperative Failure:**

*Theory:* `coroutineScope` creates a scope with a regular `Job`. If any child coroutine fails, the `Job` is cancelled, which cancels all siblings. The exception is propagated to the parent (the suspending caller). Use it for dependent tasks where a failure of one task invalidates the combined result.

```kotlin
// ✅ coroutineScope: one failure cancels all
suspend fun fetchUserData(userId: Int): UserData = coroutineScope {
    val profile = async { fetchProfile(userId) }
    val settings = async { fetchSettings(userId) }
    val friends = async { fetchFriends(userId) }

    UserData(
        profile.await(),
        settings.await(),
        friends.await()
    )
    // If any request fails, all are cancelled (we need all data)
}

// EXAMPLE: Failure example
suspend fun coroutineScopeFailure() = coroutineScope {
    launch {
        delay(100)
        println("Task 1")
        throw Exception("Task 1 failed!")  // Fails
    }

    launch {
        delay(200)
        println("Task 2")  // Never executes — cancelled
    }
}
// Output: Task 1, Exception: Task 1 failed!
```

**supervisorScope - Independent Failure:**

*Theory:* `supervisorScope` creates a scope with `SupervisorJob`-like behavior for its children: failure or cancellation of one child does not affect its siblings. However, if there is an unhandled exception that reaches the scope itself (e.g., thrown in the scope body or from `async` when awaited), the whole `supervisorScope` completes with that exception and it is propagated to the caller.

Use it for independent tasks where one task's failure should not cancel others, and where each child is expected to handle its own failures or use an exception handler.

```kotlin
// ✅ supervisorScope: failures independent between siblings
suspend fun loadDashboard(): DashboardData = supervisorScope {
    val news = async {
        try { fetchNews() }
        catch (e: Exception) { emptyList() }
    }

    val weather = async {
        try { fetchWeather() }
        catch (e: Exception) { Weather.Unknown }
    }

    val stocks = async {
        try { fetchStocks() }
        catch (e: Exception) { emptyList() }
    }

    DashboardData(
        news.await(),
        weather.await(),
        stocks.await()
    )
    // If one widget fails, others keep working due to local handling
}

// ✅ Independent failure example for launch
suspend fun supervisorScopeFailure() = supervisorScope {
    launch {
        delay(100)
        println("Task 1")
        throw Exception("Task 1 failed!")  // Fails, cancels only this coroutine
    }

    launch {
        delay(200)
        println("Task 2")  // Executes — not cancelled by Task 1 failure
    }
}
// Output: Task 1, Task 2
```

**Exception Propagation:**

*Theory:*
- In `coroutineScope`, an unhandled exception in any child cancels the scope and is propagated to the caller.
- In `supervisorScope`:
  - unhandled exceptions in `launch` children do not cancel siblings, but if such an exception is treated as reaching the scope, the scope will complete with that exception and it will be propagated to the caller;
  - for long-running or fire-and-forget style children, you typically use `CoroutineExceptionHandler` or local try/catch;
  - `async` in both builders does not propagate its exception until `await()` is called.

The key point: `supervisorScope` isolates children from cancelling each other; it does not silently swallow exceptions.

```kotlin
// ✅ coroutineScope propagates exceptions
suspend fun coroutineScopePropagation() {
    try {
        coroutineScope {
            launch { throw Exception("Error!") }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // Catches exception from child
    }
}

// NOTE: supervisorScope: siblings independent, but exception not caught here
suspend fun supervisorScopePropagation() {
    try {
        supervisorScope {
            launch { throw Exception("Error!") }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }
}
// In this example, the exception from launch is not caught by the surrounding try/catch
// because launch is fire-and-forget; its exception is handled like a top-level coroutine exception.

// ✅ supervisorScope with exception handler for launch child
suspend fun supervisorWithHandler() {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Handler caught: ${exception.message}")
    }

    supervisorScope {
        launch(handler) {
            throw Exception("Error!")  // Caught by handler; siblings remain unaffected
        }
    }
}
```

**Structured Concurrency:**

*Theory:* Both builders ensure structured concurrency: the suspending function using them does not complete until all children in that scope complete (or are cancelled). This helps avoid leaked coroutines.

```kotlin
// ✅ Both wait for all children
suspend fun structuredExample() {
    println("Start")

    coroutineScope {  // or supervisorScope
        launch {
            delay(1000)
            println("Task 1")
        }
        launch {
            delay(2000)
            println("Task 2")
        }
    }

    println("End")  // Executes only after Task 1 and Task 2
}
// Output: Start, Task 1, Task 2, End
```

**When to use coroutineScope:**

*Theory:* Use `coroutineScope` for dependent tasks where all results are required. If one task fails, there is no point in continuing others.
Typical cases: fetching related data, multi-step transactions, operations that require result integrity.

```kotlin
// ✅ Dependent tasks — need all results
suspend fun fetchCompleteUser(id: Int): User = coroutineScope {
    val basicInfo = async { fetchBasicInfo(id) }
    val permissions = async { fetchPermissions(id) }
    val preferences = async { fetchPreferences(id) }

    User(
        basicInfo.await(),
        permissions.await(),
        preferences.await()
    )
    // If any fails, we cannot build a consistent User — the scope fails with that exception
}
```

**When to use supervisorScope:**

*Theory:* Use `supervisorScope` for independent tasks where failure of one task must not cancel others. Each task should have a fallback or local error handling.
Typical cases: loading independent widgets, parallel independent operations, app/module initialization.

```kotlin
// ✅ Independent tasks — each task optional/isolated
suspend fun initializeApp() = supervisorScope {
    launch {
        try { initializeAnalytics() }
        catch (e: Exception) { logError("Analytics failed", e) }
    }

    launch {
        try { loadUserPreferences() }
        catch (e: Exception) { logError("Preferences failed", e) }
    }

    launch {
        try { syncData() }
        catch (e: Exception) { logError("Sync failed", e) }
    }
    // Each task handles its own errors and does not cancel the others
}
```

**Comparison Table:**

| Feature               | coroutineScope                               | supervisorScope                                         |
|-----------------------|----------------------------------------------|---------------------------------------------------------|
| **Job type (model)**  | Regular Job (children interdependent)       | SupervisorJob-like (children isolated)                  |
| **Error propagation** | One failure cancels all siblings            | Child failure does not cancel siblings                  |
| **Exception handling**| Unhandled exception propagated to caller    | Unhandled exception also propagated; siblings unaffected|
| **Use case**          | Dependent tasks                             | Independent/optional tasks                              |
| **Waiting**           | Waits for all children                      | Waits for all children                                  |
| **Typical usage**     | Atomic/integrity-sensitive operations       | Widgets, subsystems, tolerant initialization            |

**Key Concepts:**

1. **Structured Concurrency** - both ensure structured lifecycle for coroutines.
2. **Error Propagation** - main difference is whether one child's failure cancels its siblings.
3. **Job vs SupervisorJob** - different parent job models define failure behavior.
4. **Explicit Error Handling** - in `supervisorScope`, it's important to handle child errors explicitly if you don't want the scope to fail.
5. **Task Dependencies** - choice depends on whether tasks are dependent or independent.

---

## Дополнительные Вопросы (Follow-ups, RU)

- В чём разница между `SupervisorJob` и обычным `Job`?
- Как правильно обрабатывать исключения в `supervisorScope`?
- Можно ли вкладывать `coroutineScope` внутри `supervisorScope`?

## Связанные Вопросы (Related Questions, RU)

### Предпосылки (Lighter / Easier)
- Базовые концепции `CoroutineContext`

### Продвинутое (Harder)
- Кастомные реализации `Job`
- Продвинутые стратегии обработки исключений

## Follow-ups

- What is the difference between `SupervisorJob` and regular `Job`?
- How to handle exceptions in `supervisorScope` properly?
- Can you nest `coroutineScope` inside `supervisorScope`?

## Related Questions

### Prerequisites (Easier)
- CoroutineContext basics

### Advanced (Harder)
- Custom Job implementations
- Advanced exception handling strategies

## References

- [[c-coroutines]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]
- "https://kotlinlang.org/docs/exception-handling.html"
