---
id: kotlin-075
title: "Suspend Functions Basics / Основы suspend функций"
aliases: ["Suspend Functions Basics", "Основы suspend функций"]

# Classification
topic: kotlin
subtopics: [c-kotlin-coroutines-basics, coroutines, functions]
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
related: [c-coroutines, c-kotlin, q-launch-vs-async-vs-runblocking--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [coroutines, difficulty/easy, kotlin]
date created: Saturday, October 18th 2025, 12:37:51 pm
date modified: Tuesday, November 25th 2025, 8:53:48 pm
---
# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140028

---

# Question (EN)
> Kotlin Coroutines advanced topic 140028

## Ответ (RU)

Suspend-функции являются основой корутин в Kotlin. Это специальные функции, которые могут быть приостановлены и возобновлены без блокировки потока, обеспечивая эффективное асинхронное программирование.

### Базовый Синтаксис

Suspend-функция объявляется с модификатором `suspend`:

```kotlin
suspend fun fetchData(): String {
    delay(1000)  // Приостанавливает корутину на 1 секунду (не блокируя поток)
    return "Data loaded"
}
```

### Ключевые Характеристики

1. **Могут вызываться только из корутин или других suspend-функций** (напрямую из обычного кода — только через корутинные билдеры вроде `launch`, `async`, `runBlocking`):
```kotlin
suspend fun loadUser(): User {
    // Можно вызывать другие suspend-функции
    val data = fetchData()
    return parseUser(data)
}

// Ошибка: suspend-функцию нельзя вызвать как обычную функцию вне корутины
// fun main() {
//     loadUser()  // Ошибка компиляции!
// }

// Правильно: запуск в корутине через билдер
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

3. **Основаны на `Continuation`**: Под капотом suspend-функции компилируются в функции с дополнительным параметром `Continuation` и машиной состояний:
```kotlin
// Что вы пишете:
suspend fun example(): String {
    return "Hello"
}

// Что компилятор генерирует (упрощенно):
fun example(continuation: Continuation<String>): Any {
    // Реализация state machine
}
```

### Распространенные Suspend-функции

**Из стандартных корутинных библиотек (`kotlinx.coroutines`)**:
- `delay(ms)` - Приостанавливает на указанное время
- `yield()` - Передает выполнение другим корутинам
- `withContext(dispatcher)` - Переключает контекст корутины

**Из внешних API**:
```kotlin
suspend fun fetchFromApi(): ApiResponse {
    return apiClient.get("/endpoint")  // Suspend-функция из библиотеки
}
```

### Практические Примеры

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

### Важные Правила

1. **Suspend-функции сами по себе не создают корутины** — они выполняются внутри уже созданной корутины (которая обычно запускается через билдеры `launch`, `async`, `runBlocking` и т.п.).
2. **Поддержка структурированной конкуренции**: корректное распространение отмены и управление жизненным циклом обеспечиваются корутинными скоупами и билдерами; suspend-функции должны быть кооперативными (проверять `coroutineContext`, использовать `suspend` API), чтобы вписываться в эту модель.
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

## Answer (EN)

Suspend functions are the foundation of Kotlin coroutines. They are special functions that can be paused and resumed without blocking a thread, enabling efficient asynchronous programming.

### Basic Syntax

A suspend function is declared with the `suspend` modifier:

```kotlin
suspend fun fetchData(): String {
    delay(1000)  // Suspends the coroutine for 1 second (without blocking the thread)
    return "Data loaded"
}
```

### Key Characteristics

1. **Can only be called from coroutines or other suspend functions** (directly from regular code only via coroutine builders like `launch`, `async`, `runBlocking`):
```kotlin
suspend fun loadUser(): User {
    // Can call other suspend functions
    val data = fetchData()
    return parseUser(data)
}

// Error: a suspend function cannot be called like a normal function outside a coroutine
// fun main() {
//     loadUser()  // Compilation error!
// }

// Correct: run inside a coroutine via a builder
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

3. **Continuation-based**: Under the hood, suspend functions are compiled to functions with an extra `Continuation` parameter and a state machine:
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

**From coroutine libraries (`kotlinx.coroutines`)**:
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

1. **Suspend functions do not by themselves create coroutines** — they run inside an already created coroutine (which is typically started via builders like `launch`, `async`, `runBlocking`, etc.).
2. **Structured concurrency support**: proper cancellation propagation and lifecycle management are provided by coroutine scopes and builders; suspend functions should be cooperative (checking `coroutineContext`, using suspending APIs) to integrate correctly with this model.
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

## Дополнительные Вопросы (RU)

1. Объясните различие между `suspend`-функцией и обычной функцией с точки зрения блокировки потоков.
2. Почему `suspend`-функции должны вызываться только из корутин или других `suspend`-функций?
3. Как `withContext` используется внутри `suspend`-функций для смены диспетчера и почему это важно?
4. Какие подводные камни существуют при использовании `suspend`-функций во внешних библиотеках?
5. Как реализована машина состояний для `suspend`-функций на уровне байткода Kotlin?

## Follow-ups

1. Explain the difference between a `suspend` function and a regular function in terms of thread blocking.
2. Why must `suspend` functions be invoked only from coroutines or other `suspend` functions?
3. How is `withContext` used inside `suspend` functions to switch dispatchers, and why does it matter?
4. What pitfalls should you watch for when using library-provided `suspend` functions?
5. How is the state machine for `suspend` functions implemented at the Kotlin bytecode level?

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)
- [[c-kotlin]]
- [[c-coroutines]]

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
- Cancellation basics

### Advanced (Harder)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-select-expression-channels--kotlin--hard]] - Coroutines
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction
