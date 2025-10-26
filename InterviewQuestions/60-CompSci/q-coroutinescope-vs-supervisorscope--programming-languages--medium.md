---
id: 20251012-1227111121
title: "CoroutineScope vs SupervisorScope / CoroutineScope против SupervisorScope"
aliases: ["CoroutineScope vs SupervisorScope", "CoroutineScope против SupervisorScope"]
topic: cs
subtopics: [coroutines, kotlin, error-handling, programming-languages]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-coroutine-context, q-coroutine-context-essence--programming-languages--medium, q-concurrency-fundamentals--computer-science--hard]
created: 2025-10-15
updated: 2025-01-25
tags: [coroutines, kotlin, coroutinescope, supervisorscope, error-handling, programming-languages, difficulty/medium]
sources: [https://kotlinlang.org/docs/exception-handling.html]
---

# Вопрос (RU)
> В чем разница между coroutineScope и supervisorScope? Когда использовать каждый из них?

# Question (EN)
> What is the difference between coroutineScope and supervisorScope? When to use each of them?

---

## Ответ (RU)

**Теория Scope Builders:**
`coroutineScope` и `supervisorScope` - suspend functions, создающие новый scope для structured concurrency. Оба ожидают завершения всех child корутин. Ключевое различие - в error propagation: `coroutineScope` использует обычный Job (failure одной child корутины отменяет все siblings), `supervisorScope` использует SupervisorJob (failures независимы).

**coroutineScope - Кооперативный Failure:**

*Теория:* `coroutineScope` создаёт scope с обычным Job. Если любая child корутина fails, Job отменяется, что отменяет все siblings. Exception propagates к parent. Используется для dependent tasks, где failure одной задачи делает результат невалидным.

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
    // Если любой запрос fails, все отменяются (нужны все данные)
}

// ❌ Пример failure
suspend fun coroutineScopeFailure() = coroutineScope {
    launch {
        delay(100)
        println("Task 1")
        throw Exception("Task 1 failed!")  // Fails
    }

    launch {
        delay(200)
        println("Task 2")  // Никогда не выполнится - cancelled
    }
}
// Output: Task 1, Exception: Task 1 failed!
```

**supervisorScope - Независимый Failure:**

*Теория:* `supervisorScope` создаёт scope с SupervisorJob. Failure одной child корутины не влияет на siblings. Exception НЕ propagates к parent автоматически. Используется для independent tasks, где failure одной задачи не должен влиять на другие.

```kotlin
// ✅ supervisorScope: failures независимы
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
    // Если один widget fails, другие продолжают работать
}

// ✅ Пример независимого failure
suspend fun supervisorScopeFailure() = supervisorScope {
    launch {
        delay(100)
        println("Task 1")
        throw Exception("Task 1 failed!")  // Fails
    }

    launch {
        delay(200)
        println("Task 2")  // Выполнится - не cancelled
    }
}
// Output: Task 1, Task 2
```

**Exception Propagation:**

*Теория:* `coroutineScope` propagates exceptions к caller. `supervisorScope` НЕ propagates exceptions от child корутин - нужен explicit CoroutineExceptionHandler. `async` в обоих scopes не propagates exceptions до `await()`.

```kotlin
// ✅ coroutineScope propagates exceptions
suspend fun coroutineScopePropagation() {
    try {
        coroutineScope {
            launch { throw Exception("Error!") }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // Ловит exception
    }
}

// ❌ supervisorScope НЕ propagates от launch
suspend fun supervisorScopePropagation() {
    try {
        supervisorScope {
            launch { throw Exception("Error!") }  // Silent failure
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // НЕ ловит!
    }
}

// ✅ supervisorScope с exception handler
suspend fun supervisorWithHandler() {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Handler caught: ${exception.message}")
    }

    supervisorScope {
        launch(handler) {
            throw Exception("Error!")  // Ловится handler
        }
    }
}
```

**Structured Concurrency:**

*Теория:* Оба scope builders обеспечивают structured concurrency - suspend до завершения всех child корутин. Parent scope не завершится, пока все children не завершатся или не будут cancelled. Это гарантирует отсутствие leaked корутин.

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

*Теория:* Используйте `coroutineScope` для dependent tasks, где все результаты необходимы. Если одна задача fails, нет смысла продолжать другие. Типичные случаи: fetching related data, multi-step transactions, atomic operations.

```kotlin
// ✅ Dependent tasks - нужны все результаты
suspend fun fetchCompleteUser(id: Int): User = coroutineScope {
    val basicInfo = async { fetchBasicInfo(id) }
    val permissions = async { fetchPermissions(id) }
    val preferences = async { fetchPreferences(id) }

    User(
        basicInfo.await(),
        permissions.await(),
        preferences.await()
    )
    // Если любой fails, User невалиден - отменяем всё
}
```

**Когда использовать supervisorScope:**

*Теория:* Используйте `supervisorScope` для independent tasks, где failure одной задачи не влияет на другие. Каждая задача имеет fallback или может быть пропущена. Типичные случаи: loading widgets, parallel independent operations, app initialization.

```kotlin
// ✅ Independent tasks - каждая задача опциональна
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
    // Каждая задача может fail независимо
}
```

**Сравнительная таблица:**

| Характеристика | coroutineScope | supervisorScope |
|----------------|----------------|-----------------|
| **Job type** | Job | SupervisorJob |
| **Error propagation** | Один failure отменяет всех | Failures независимы |
| **Exception handling** | Propagates к parent | Нужен explicit handler |
| **Use case** | Dependent tasks | Independent tasks |
| **Waiting** | Ждёт всех children | Ждёт всех children |
| **Typical usage** | Atomic operations | Optional operations |

**Ключевые концепции:**

1. **Structured Concurrency** - оба обеспечивают structured concurrency
2. **Error Propagation** - ключевое различие в error handling
3. **Job vs SupervisorJob** - разные типы Jobs определяют поведение
4. **Explicit Error Handling** - supervisorScope требует explicit handlers
5. **Task Dependencies** - выбор зависит от dependencies между tasks

## Answer (EN)

**Scope Builders Theory:**
`coroutineScope` and `supervisorScope` - suspend functions creating new scope for structured concurrency. Both wait for all child coroutines completion. Key difference - error propagation: `coroutineScope` uses regular Job (failure of one child coroutine cancels all siblings), `supervisorScope` uses SupervisorJob (failures independent).

**coroutineScope - Cooperative Failure:**

*Theory:* `coroutineScope` creates scope with regular Job. If any child coroutine fails, Job cancelled, which cancels all siblings. Exception propagates to parent. Used for dependent tasks, where failure of one task makes result invalid.

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
    // If any request fails, all cancelled (need all data)
}

// ❌ Failure example
suspend fun coroutineScopeFailure() = coroutineScope {
    launch {
        delay(100)
        println("Task 1")
        throw Exception("Task 1 failed!")  // Fails
    }

    launch {
        delay(200)
        println("Task 2")  // Never executes - cancelled
    }
}
// Output: Task 1, Exception: Task 1 failed!
```

**supervisorScope - Independent Failure:**

*Theory:* `supervisorScope` creates scope with SupervisorJob. Failure of one child coroutine doesn't affect siblings. Exception NOT propagates to parent automatically. Used for independent tasks, where failure of one task shouldn't affect others.

```kotlin
// ✅ supervisorScope: failures independent
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
    // If one widget fails, others continue working
}

// ✅ Independent failure example
suspend fun supervisorScopeFailure() = supervisorScope {
    launch {
        delay(100)
        println("Task 1")
        throw Exception("Task 1 failed!")  // Fails
    }

    launch {
        delay(200)
        println("Task 2")  // Executes - not cancelled
    }
}
// Output: Task 1, Task 2
```

**Exception Propagation:**

*Theory:* `coroutineScope` propagates exceptions to caller. `supervisorScope` NOT propagates exceptions from child coroutines - needs explicit CoroutineExceptionHandler. `async` in both scopes doesn't propagate exceptions until `await()`.

```kotlin
// ✅ coroutineScope propagates exceptions
suspend fun coroutineScopePropagation() {
    try {
        coroutineScope {
            launch { throw Exception("Error!") }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // Catches exception
    }
}

// ❌ supervisorScope NOT propagates from launch
suspend fun supervisorScopePropagation() {
    try {
        supervisorScope {
            launch { throw Exception("Error!") }  // Silent failure
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")  // NOT caught!
    }
}

// ✅ supervisorScope with exception handler
suspend fun supervisorWithHandler() {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("Handler caught: ${exception.message}")
    }

    supervisorScope {
        launch(handler) {
            throw Exception("Error!")  // Caught by handler
        }
    }
}
```

**Structured Concurrency:**

*Theory:* Both scope builders ensure structured concurrency - suspend until all child coroutines complete. Parent scope won't complete until all children complete or cancelled. This guarantees no leaked coroutines.

```kotlin
// ✅ Both wait for all children completion
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

*Theory:* Use `coroutineScope` for dependent tasks, where all results necessary. If one task fails, no point continuing others. Typical cases: fetching related data, multi-step transactions, atomic operations.

```kotlin
// ✅ Dependent tasks - need all results
suspend fun fetchCompleteUser(id: Int): User = coroutineScope {
    val basicInfo = async { fetchBasicInfo(id) }
    val permissions = async { fetchPermissions(id) }
    val preferences = async { fetchPreferences(id) }

    User(
        basicInfo.await(),
        permissions.await(),
        preferences.await()
    )
    // If any fails, User invalid - cancel everything
}
```

**When to use supervisorScope:**

*Theory:* Use `supervisorScope` for independent tasks, where failure of one task doesn't affect others. Each task has fallback or can be skipped. Typical cases: loading widgets, parallel independent operations, app initialization.

```kotlin
// ✅ Independent tasks - each task optional
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
    // Each task can fail independently
}
```

**Comparison Table:**

| Feature | coroutineScope | supervisorScope |
|---------|----------------|-----------------|
| **Job type** | Job | SupervisorJob |
| **Error propagation** | One failure cancels all | Failures independent |
| **Exception handling** | Propagates to parent | Needs explicit handler |
| **Use case** | Dependent tasks | Independent tasks |
| **Waiting** | Waits for all children | Waits for all children |
| **Typical usage** | Atomic operations | Optional operations |

**Key Concepts:**

1. **Structured Concurrency** - both ensure structured concurrency
2. **Error Propagation** - key difference in error handling
3. **Job vs SupervisorJob** - different Job types define behavior
4. **Explicit Error Handling** - supervisorScope requires explicit handlers
5. **Task Dependencies** - choice depends on dependencies between tasks

---

## Follow-ups

- What is the difference between SupervisorJob and regular Job?
- How to handle exceptions in supervisorScope properly?
- Can you nest coroutineScope inside supervisorScope?

## Related Questions

### Prerequisites (Easier)
- [[q-coroutine-context-essence--programming-languages--medium]] - CoroutineContext basics

### Related (Same Level)
- [[q-coroutine-dispatchers--programming-languages--medium]] - Dispatchers
- [[q-concurrency-fundamentals--computer-science--hard]] - Concurrency concepts

### Advanced (Harder)
- Custom Job implementations
- Advanced exception handling strategies
