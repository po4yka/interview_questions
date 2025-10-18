---
id: 20251012-140028
title: "Suspend Functions Basics / Основы suspend функций"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, advanced, patterns]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140028

# Workflow & relations
status: draft
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, coroutines, difficulty/medium]
---
# Question (EN)
> Kotlin Coroutines advanced topic 140028

# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140028

---

## Answer (EN)

Suspend functions are the foundation of Kotlin coroutines. They are special functions that can be paused and resumed without blocking a thread, enabling efficient asynchronous programming.

### Basic Syntax

A suspend function is declared with the `suspend` modifier:

```kotlin
suspend fun fetchData(): String {
    delay(1000)  // Suspends the coroutine for 1 second
    return "Data loaded"
}
```

### Key Characteristics

1. **Can only be called from coroutines or other suspend functions**:
```kotlin
suspend fun loadUser(): User {
    // Can call other suspend functions
    val data = fetchData()
    return parseUser(data)
}

// Error: suspend function can't be called outside coroutine
// fun main() {
//     loadUser()  // Compilation error!
// }

// Correct: call from coroutine
fun main() = runBlocking {
    val user = loadUser()  // OK
}
```

2. **Non-blocking suspension**: The function can pause without blocking the thread:
```kotlin
suspend fun processData() {
    println("Starting on ${Thread.currentThread().name}")
    delay(1000)  // Suspends, thread is free to do other work
    println("Resumed on ${Thread.currentThread().name}")
}
```

3. **Continuation-based**: Under the hood, suspend functions use continuations:
```kotlin
// What you write:
suspend fun example(): String {
    return "Hello"
}

// What the compiler generates (simplified):
fun example(continuation: Continuation<String>): Any {
    // State machine implementation
}
```

### Common Suspend Functions

**From standard library**:
- `delay(ms)` - Suspends for specified time
- `yield()` - Yields execution to other coroutines
- `withContext(dispatcher)` - Switches coroutine context

**From external APIs**:
```kotlin
suspend fun fetchFromApi(): ApiResponse {
    return apiClient.get("/endpoint")  // Suspend function from library
}
```

### Practical Examples

**Example 1: Sequential execution**:
```kotlin
suspend fun loadUserData(userId: String): UserData {
    val profile = fetchUserProfile(userId)  // Suspends
    val settings = fetchUserSettings(userId)  // Suspends after profile
    return UserData(profile, settings)
}
```

**Example 2: Parallel execution with async**:
```kotlin
suspend fun loadUserDataParallel(userId: String): UserData = coroutineScope {
    val profileDeferred = async { fetchUserProfile(userId) }
    val settingsDeferred = async { fetchUserSettings(userId) }

    UserData(profileDeferred.await(), settingsDeferred.await())
}
```

**Example 3: Error handling**:
```kotlin
suspend fun safeLoadData(): Result<String> {
    return try {
        val data = fetchData()
        Result.success(data)
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

### Important Rules

1. **Suspend functions don't create coroutines** - they must be called from one
2. **They preserve structured concurrency** - cancellation propagates correctly
3. **They can be used as higher-order functions**:
```kotlin
suspend fun <T> retry(
    times: Int,
    block: suspend () -> T
): T {
    repeat(times - 1) {
        try {
            return block()
        } catch (e: Exception) {
            // Continue to next attempt
        }
    }
    return block()  // Last attempt
}

// Usage
val data = retry(3) { fetchData() }
```

---

## Ответ (RU)

Suspend-функции являются основой корутин в Kotlin. Это специальные функции, которые могут быть приостановлены и возобновлены без блокировки потока, обеспечивая эффективное асинхронное программирование.

### Базовый синтаксис

Suspend-функция объявляется с модификатором `suspend`:

```kotlin
suspend fun fetchData(): String {
    delay(1000)  // Приостанавливает корутину на 1 секунду
    return "Data loaded"
}
```

### Ключевые характеристики

1. **Могут вызываться только из корутин или других suspend-функций**:
```kotlin
suspend fun loadUser(): User {
    // Можно вызывать другие suspend-функции
    val data = fetchData()
    return parseUser(data)
}

// Ошибка: suspend-функцию нельзя вызвать вне корутины
// fun main() {
//     loadUser()  // Ошибка компиляции!
// }

// Правильно: вызов из корутины
fun main() = runBlocking {
    val user = loadUser()  // OK
}
```

2. **Неблокирующая приостановка**: Функция может приостановиться без блокировки потока:
```kotlin
suspend fun processData() {
    println("Starting on ${Thread.currentThread().name}")
    delay(1000)  // Приостанавливается, поток свободен для другой работы
    println("Resumed on ${Thread.currentThread().name}")
}
```

3. **Основаны на continuation**: Под капотом suspend-функции используют continuation:
```kotlin
// Что вы пишете:
suspend fun example(): String {
    return "Hello"
}

// Что генерирует компилятор (упрощенно):
fun example(continuation: Continuation<String>): Any {
    // Реализация state machine
}
```

### Распространенные suspend-функции

**Из стандартной библиотеки**:
- `delay(ms)` - Приостанавливает на указанное время
- `yield()` - Передает выполнение другим корутинам
- `withContext(dispatcher)` - Переключает контекст корутины

**Из внешних API**:
```kotlin
suspend fun fetchFromApi(): ApiResponse {
    return apiClient.get("/endpoint")  // Suspend-функция из библиотеки
}
```

### Практические примеры

**Пример 1: Последовательное выполнение**:
```kotlin
suspend fun loadUserData(userId: String): UserData {
    val profile = fetchUserProfile(userId)  // Приостанавливается
    val settings = fetchUserSettings(userId)  // Приостанавливается после profile
    return UserData(profile, settings)
}
```

**Пример 2: Параллельное выполнение с async**:
```kotlin
suspend fun loadUserDataParallel(userId: String): UserData = coroutineScope {
    val profileDeferred = async { fetchUserProfile(userId) }
    val settingsDeferred = async { fetchUserSettings(userId) }

    UserData(profileDeferred.await(), settingsDeferred.await())
}
```

**Пример 3: Обработка ошибок**:
```kotlin
suspend fun safeLoadData(): Result<String> {
    return try {
        val data = fetchData()
        Result.success(data)
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

### Важные правила

1. **Suspend-функции не создают корутины** - они должны вызываться из существующей
2. **Они сохраняют структурированную конкурентность** - отмена распространяется корректно
3. **Могут использоваться как функции высшего порядка**:
```kotlin
suspend fun <T> retry(
    times: Int,
    block: suspend () -> T
): T {
    repeat(times - 1) {
        try {
            return block()
        } catch (e: Exception) {
            // Продолжаем следующую попытку
        }
    }
    return block()  // Последняя попытка
}

// Использование
val data = retry(3) { fetchData() }
```

---

## Follow-ups

1. **Follow-up question 1**
2. **Follow-up question 2**

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

---

## Related Questions

### Related (Easy)
- [[q-coroutine-builders-basics--kotlin--easy]] - Coroutines
- [[q-coroutine-scope-basics--kotlin--easy]] - Coroutines
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines
- [[q-launch-vs-async--kotlin--easy]] - Coroutines

### Related (Medium)
- [[q-coroutine-dispatchers--kotlin--medium]] - Coroutine dispatchers overview
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs Context
- [[q-coroutine-context-explained--kotlin--medium]] - CoroutineContext explained
- [[q-coroutine-cancellation--kotlin--medium]] - Cancellation basics

### Advanced (Harder)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-select-expression-channels--kotlin--hard]] - Coroutines
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

