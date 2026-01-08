---\
id: kotlin-069
title: "Debugging Kotlin coroutines: tools and techniques / Отладка Kotlin корутин: инструменты и техники"
topic: kotlin
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-11-09
tags: [coroutines, debugging, difficulty/medium, kotlin, profiling, tools, troubleshooting]
moc: moc-kotlin
aliases: []
question_kind: coding
related: [c-kotlin, q-common-coroutine-mistakes--kotlin--medium, q-coroutine-exception-handler--kotlin--medium, q-kotlin-null-safety--kotlin--medium, q-produce-actor-builders--kotlin--medium]
subtopics: [coroutines, debugging, profiling]

---\
# Вопрос (RU)
> Какие инструменты и техники доступны для отладки Kotlin корутин? Как идентифицировать deadlock, утечки и проблемы производительности?

---

# Question (EN)
> What tools and techniques are available for debugging Kotlin coroutines? How do you identify deadlocks, leaks, and performance issues?

## Ответ (RU)

Отладка корутин сложна, потому что традиционные инструменты отладки разработаны для потоков, а не для `suspend`-функций. Корутины могут приостанавливаться, возобновляться на разных потоках и иметь сложные иерархии. Понимание эффективной отладки корутин критично для production-готовности. См. также [[c-coroutines]].

### 1. Включение Режима Отладки

**Первый шаг:** включите режим отладки `kotlinx.coroutines`, чтобы добавить информацию о корутинах в имена потоков.

```kotlin
// JVM-аргумент:
-Dkotlinx.coroutines.debug

// Или программно (до запуска любых корутин):
System.setProperty("kotlinx.coroutines.debug", "on")
```

**Эффект:** имена потоков включают информацию о корутинах:

```text
// Без режима отладки:
Thread: DefaultDispatcher-worker-1

// С режимом отладки:
Thread: DefaultDispatcher-worker-1 @coroutine#2
```

Пример:

```kotlin
import kotlinx.coroutines.*

fun main() {
    System.setProperty("kotlinx.coroutines.debug", "on")

    runBlocking {
        launch {
            println("Running on: ${Thread.currentThread().name}")
        }
    }
}

// Возможный вывод:
// Running on: main @coroutine#2
```

### 2. CoroutineName Для Отладки

Используйте `CoroutineName` для идентификации корутин в логах и отладчике:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    System.setProperty("kotlinx.coroutines.debug", "on")

    launch(CoroutineName("DataLoader")) {
        println("Загрузка данных на: ${Thread.currentThread().name}")
        // loadData()
    }

    launch(CoroutineName("ImageDownloader")) {
        println("Загрузка изображений на: ${Thread.currentThread().name}")
        // downloadImages()
    }
}

// Пример вывода:
// Загрузка данных на: main @DataLoader#2
// Загрузка изображений на: main @ImageDownloader#3
```

Продакшен-пример использования:

```kotlin
import kotlinx.coroutines.*

class UserRepository {
    suspend fun loadUser(userId: String): User =
        withContext(Dispatchers.IO + CoroutineName("LoadUser-$userId")) {
            println("Loading user $userId on ${Thread.currentThread().name}")
            api.getUser(userId)
        }
}

// Логи:
// Loading user 123 on DefaultDispatcher-worker-2 @LoadUser-123#5
```

### 3. Чтение Стек-трейсов Корутин

Стек-трейсы корутин показывают цепочку вызовов через точки приостановки. Включенный debug-режим и `CoroutineName` помогают понять, в каком контексте произошла ошибка.

Пример:

```kotlin
import kotlinx.coroutines.*

suspend fun functionA() { functionB() }

suspend fun functionB() { functionC() }

suspend fun functionC() {
    delay(100)
    throw RuntimeException("Error in C")
}

fun main() = runBlocking {
    functionA()
}
```

### 4. IntelliJ IDEA / Android Studio Coroutine Debugger

Современные версии IntelliJ IDEA / Android Studio имеют встроенную поддержку отладки корутин:
- Панель `Coroutines`: просмотр активных корутин.
- Стек вызовов корутин: отображение точек приостановки и путей вызова.
- Состояния корутин: suspended, running, cancelled.
- Пошаговая отладка `suspend`-функций.

Шаги:
1. Поставьте breakpoint в `suspend`-функции.
2. Запустите приложение в debug-режиме.
3. Откройте панель `Coroutines` в окне Debug.

### 5. DebugProbes И Дамп Корутин

Модуль `kotlinx-coroutines-debug` предоставляет `DebugProbes` для инспекции корутин во время выполнения.

Простой пример использования (печать в лог):

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.debug.DebugProbes

fun main() {
    DebugProbes.install()

    runBlocking {
        repeat(5) { index ->
            launch(CoroutineName("Worker-$index")) {
                delay(1000)
            }
        }

        delay(100) // дать корутинам стартовать
        // Печатает информацию о состоянии и стеке корутин в stdout
        DebugProbes.dumpCoroutines()
    }

    DebugProbes.uninstall()
}
```

Это помогает увидеть, какие корутины активны, приостановлены или потенциально "зависли".

### 6. Поиск "зависших" Корутин И Псевдо-deadlock

Если корутина "застыла", важно отличать нормальную приостановку от взаимной блокировки:
- Используйте логирование и debug-режим, чтобы увидеть, на чём она приостановлена (`delay`, канал, `Mutex`).
- Используйте таймауты (`withTimeout`/`withTimeoutOrNull`) вокруг потенциально блокирующих операций.

```kotlin
import kotlinx.coroutines.withTimeout

suspend fun <T> withTimeoutCheck(name: String, timeoutMs: Long, block: suspend () -> T): T =
    withTimeout(timeoutMs) { block() }
```

Если таймаут стабильно срабатывает, проанализируйте `DebugProbes.dumpCoroutines()` и панель `Coroutines`, чтобы увидеть точку ожидания.

### 7. Deadlock С Mutex И Его Выявление

Классический пример взаимной блокировки с `Mutex`:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

val mutex1 = Mutex()
val mutex2 = Mutex()

fun main() = runBlocking {
    launch(CoroutineName("Coroutine-1")) {
        mutex1.withLock {
            println("C1: acquired mutex1")
            delay(100)
            mutex2.withLock {
                println("C1: acquired mutex2")
            }
        }
    }

    launch(CoroutineName("Coroutine-2")) {
        mutex2.withLock {
            println("C2: acquired mutex2")
            delay(100)
            mutex1.withLock { // риск deadlock при неправильном порядке
                println("C2: acquired mutex1")
            }
        }
    }
}
```

Для обнаружения и избежания:
- Соблюдайте единый порядок захвата ресурсов.
- Используйте таймауты вокруг последовательного захвата.

### 8. Выявление Утечек Корутин

Утечки корутин возникают, когда корутины продолжают работать после окончания их жизненного цикла (например, использование `GlobalScope` в Android `ViewModel`/`Activity`).

Правильные практики:
- Используйте `viewModelScope`, `lifecycleScope` и собственные `CoroutineScope` с правильно управляемым `Job`.
- В отладочном/тестовом коде регистрируйте активные `Job` и проверяйте, что они завершаются.

```kotlin
import kotlinx.coroutines.Job
import java.util.concurrent.ConcurrentHashMap

object CoroutineTracker {
    private val activeCoroutines = ConcurrentHashMap<String, Job>()

    fun track(name: String, job: Job) {
        activeCoroutines[name] = job
        job.invokeOnCompletion { activeCoroutines.remove(name) }
    }

    fun printActiveCoroutines() {
        println("Active coroutines: ${activeCoroutines.size}")
        activeCoroutines.forEach { (name, job) ->
            println("  - $name: ${if (job.isActive) "ACTIVE" else "COMPLETED"}")
        }
    }
}
```

В Android `LeakCanary` помогает находить утечки объектов (`Activity`, `Fragment` и т.п.), которые могут утекать из-за долгоживущих корутин, но он не отслеживает `Job` напрямую — он сигнализирует, что объект удерживается дольше, чем должен.

### 9. Логирование И Контекст Корутины

Структурированное логирование с использованием контекста корутины помогает сопоставлять события:

```kotlin
import kotlin.coroutines.coroutineContext
import kotlinx.coroutines.CoroutineName
import kotlinx.coroutines.Job

suspend fun logWithContext(message: String) {
    val context = coroutineContext
    val name = context[CoroutineName]?.name ?: "unnamed"
    val job = context[Job]
    val thread = Thread.currentThread().name
    println("[$name][${job?.hashCode()}][$thread] $message")
}
```

Это облегчает отслеживание конкретной корутины по логам.

### 10. Производительность И Профилирование

- Используйте профайлеры (CPU/Memory) в Android Studio/IntelliJ, чтобы увидеть активность потоков, allocation-спайки и косвенно связать их с корутинами.
- Используйте инспекторы БД/сети для корреляции запросов, инициированных из корутин.
- Избегайте долгих блокирующих операций на `Dispatchers.Default`/`Dispatchers.Main`.
- Понимайте, что профайлеры не отображают корутины как сущности первого класса, но в сочетании с debug-режимом и `Coroutine` Debugger позволяют сопоставлять активность потоков и корутин.
- Для тестов применяйте `kotlinx-coroutines-test`, чтобы контролировать виртуальное время и планирование.

### 11. Интерпретация Thread Dump

`Thread` dump полезен, когда приложение "подвисло" под нагрузкой или в production:

- При включённом `kotlinx.coroutines.debug` идентификаторы корутин появляются в именах потоков (например, `DefaultDispatcher-worker-1 @coroutine#2`).
- Снятие thread dump (через `jstack` или инструменты IDE) позволяет увидеть, где потоки диспетчеров блокируются или какие точки приостановки активны.
- В непроизводственной среде можно комбинировать это с `DebugProbes` для более полного представления о состоянии корутин.

---

## Answer (EN)

Debugging coroutines is challenging because traditional debugging tools are designed for threads, not suspending functions. `Coroutines` can suspend, resume on different threads, and have complex hierarchies. Understanding how to debug coroutines effectively is crucial for production readiness. See also [[c-coroutines]].

### 1. Enable Debug Mode

First step: enable `kotlinx.coroutines` debug mode to add coroutine info to thread names.

```kotlin
// Add JVM argument:
-Dkotlinx.coroutines.debug

// Or programmatically (must be done before any coroutines run):
System.setProperty("kotlinx.coroutines.debug", "on")
```

Effect: thread names include coroutine info:

```text
// Without debug mode:
Thread: DefaultDispatcher-worker-1

// With debug mode:
Thread: DefaultDispatcher-worker-1 @coroutine#2
```

Example:

```kotlin
import kotlinx.coroutines.*

fun main() {
    System.setProperty("kotlinx.coroutines.debug", "on")

    runBlocking {
        launch {
            println("Running on: ${Thread.currentThread().name}")
        }
    }
}

// Possible output:
// Running on: main @coroutine#2
```

### 2. CoroutineName for Debugging

Use `CoroutineName` to identify coroutines in logs and debugger:

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    System.setProperty("kotlinx.coroutines.debug", "on")

    launch(CoroutineName("DataLoader")) {
        println("Loading data on: ${Thread.currentThread().name}")
        // loadData()
    }

    launch(CoroutineName("ImageDownloader")) {
        println("Downloading images on: ${Thread.currentThread().name}")
        // downloadImages()
    }
}

// Output:
// Loading data on: main @DataLoader#2
// Downloading images on: main @ImageDownloader#3
```

Production-style usage:

```kotlin
import kotlinx.coroutines.*

class UserRepository {
    suspend fun loadUser(userId: String): User =
        withContext(Dispatchers.IO + CoroutineName("LoadUser-$userId")) {
            println("Loading user $userId on ${Thread.currentThread().name}")
            api.getUser(userId)
        }
}

// Logs:
// Loading user 123 on DefaultDispatcher-worker-2 @LoadUser-123#5
```

### 3. Reading Coroutine Stack Traces

`Coroutine` stack traces show suspension points and the logical call chain when debug mode is enabled. With debug mode and `CoroutineName`, the stack trace and thread name help you see which coroutine and context failed.

Example:

```kotlin
import kotlinx.coroutines.*

suspend fun functionA() { functionB() }

suspend fun functionB() { functionC() }

suspend fun functionC() {
    delay(100)
    throw RuntimeException("Error in C")
}

fun main() = runBlocking {
    functionA()
}
```

### 4. IntelliJ IDEA / Android Studio Coroutine Debugger

Modern IntelliJ IDEA / Android Studio versions provide dedicated coroutine debugging support:

- `Coroutines` panel: view active coroutines.
- `Coroutine` call stack: see suspension points and call paths.
- `Coroutine` state: suspended, running, cancelled.
- Step through suspending functions similar to regular functions.

How to use:
1. `Set` a breakpoint in a suspending function.
2. Run in debug mode.
3. Open the `Coroutines` panel in the Debug tool window.

### 5. Coroutine Dump with DebugProbes

The `kotlinx-coroutines-debug` module provides `DebugProbes` to inspect coroutines.

Basic usage:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.debug.DebugProbes

fun main() {
    DebugProbes.install()

    runBlocking {
        repeat(5) { index ->
            launch(CoroutineName("Worker-$index")) {
                delay(1000)
            }
        }

        delay(100)
        // Prints coroutine information (state, stack) to stdout
        DebugProbes.dumpCoroutines()
    }

    DebugProbes.uninstall()
}
```

This is useful to see which coroutines are active, suspended, or potentially stuck.

### 6. Finding Stuck Coroutines Vs Deadlocks

When a coroutine seems "stuck":

- Use logging and debug mode to see whether it is suspended on a known primitive (e.g., `delay`, channel, `Mutex`).
- Use timeouts around potentially blocking or coordination logic to surface hangs:

```kotlin
import kotlinx.coroutines.withTimeout

suspend fun <T> withTimeoutCheck(name: String, timeoutMs: Long, block: suspend () -> T): T =
    withTimeout(timeoutMs) { block() }
```

If a timeout consistently fires, inspect `DebugProbes.dumpCoroutines()` / `Coroutines` panel to locate the wait point.

### 7. Detecting Deadlocks with Mutex

Example of a potential deadlock:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

val mutex1 = Mutex()
val mutex2 = Mutex()

fun main() = runBlocking {
    launch(CoroutineName("Coroutine-1")) {
        mutex1.withLock {
            println("C1: acquired mutex1")
            delay(100)
            mutex2.withLock {
                println("C1: acquired mutex2")
            }
        }
    }

    launch(CoroutineName("Coroutine-2")) {
        mutex2.withLock {
            println("C2: acquired mutex2")
            delay(100)
            mutex1.withLock {
                println("C2: acquired mutex1")
            }
        }
    }
}
```

Use consistent lock ordering or timeouts to detect and avoid such patterns.

### 8. Identifying Leaked Coroutines

`Coroutine` leaks happen when jobs outlive their intended scope (e.g., using `GlobalScope` or forgetting to cancel a custom scope tied to a lifecycle).

Bad example (Android `ViewModel`):

```kotlin
import androidx.lifecycle.ViewModel
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class LeakyViewModel : ViewModel() {
    fun loadData() {
        GlobalScope.launch {
            while (true) {
                fetchData()
                delay(1000)
            }
        }
    }
    // The coroutine continues even after ViewModel is cleared.
}
```

Better: use `viewModelScope` (or a well-managed scope) and optional tracking in debug builds:

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.CoroutineName
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import java.util.concurrent.ConcurrentHashMap

object CoroutineTracker {
    private val activeCoroutines = ConcurrentHashMap<String, Job>()

    fun track(name: String, job: Job) {
        activeCoroutines[name] = job
        job.invokeOnCompletion { activeCoroutines.remove(name) }
    }

    fun printActiveCoroutines() {
        println("Active coroutines: ${activeCoroutines.size}")
        activeCoroutines.forEach { (name, job) ->
            println("  - $name: ${if (job.isActive) "ACTIVE" else "COMPLETED"}")
        }
    }
}

class TrackedViewModel : ViewModel() {
    fun loadData() {
        val job = viewModelScope.launch(CoroutineName("LoadData")) {
            // Work
        }
        CoroutineTracker.track("ViewModel-LoadData", job)
    }
}
```

On Android, LeakCanary helps detect leaked `Activity`/`View`/`Fragment` instances that are kept alive by coroutines or other references. It does not directly track coroutine `Job` lifecycles, but is useful to surface leaks caused by long-running coroutines capturing UI references.

### 9. Logging Best Practices

Pattern: structured logging with coroutine context.

```kotlin
import kotlin.coroutines.coroutineContext
import kotlinx.coroutines.CoroutineName
import kotlinx.coroutines.Job

suspend fun logWithContext(message: String) {
    val context = coroutineContext
    val name = context[CoroutineName]?.name ?: "unnamed"
    val job = context[Job]
    val thread = Thread.currentThread().name

    println("[$name][${job?.hashCode()}][$thread] $message")
}

suspend fun loadData() {
    logWithContext("Starting data load")
    val data = api.fetchData()
    logWithContext("Data loaded: ${data.size} items")
}
```

### 10. Android Studio Profiling and Tooling

- Use CPU/Memory profilers in Android Studio/IntelliJ to see thread activity, allocation spikes, and indirectly relate them to coroutine execution.
- Use database/network inspectors to correlate operations initiated from coroutines.
- Avoid long blocking operations on `Dispatchers.Default`/`Dispatchers.Main`.
- Understand that these profilers do not treat coroutines as first-class entities, but combined with debug mode and the `Coroutine` Debugger they help you map threads back to coroutines.
- For tests, use `kotlinx-coroutines-test` to control virtual time and scheduling.

### 11. Thread Dumps Interpretation

`Thread` dumps can help when the app is stuck in production or under load:

- With `kotlinx.coroutines.debug` enabled, coroutine identifiers appear in thread names (e.g., `DefaultDispatcher-worker-1 @coroutine#2`).
- Capturing a thread dump (e.g., via `jstack` or IDE tools) lets you see where dispatcher threads are blocked or what suspension points are active.
- Combine this with `DebugProbes` (in non-production or staging) for a more complete view of coroutine states.

---

## Дополнительные Вопросы (RU)

1. Как отлаживать корутины, которые приостанавливаются и продолжаются на разных потоках, сохраняя понятный контекст вызовов?
2. Какой оверхед и риски у включения debug-режима корутин в production-среде, и когда его стоит отключать?
3. Какие подходы позволяют собирать диагностическую информацию о корутинах в production, не раскрывая конфиденциальные данные и не ухудшая производительность?
4. Какие инструменты или подходы помогают визуализировать выполнение корутин и их зависимостей?
5. Как находить и отлаживать race condition, которые проявляются только под высокой нагрузкой при работе корутин?

---

## Follow-ups

1. How do you debug coroutines that suspend across multiple threads while keeping context understandable?
2. What is the performance overhead and risk of enabling coroutine debug mode in production, and in which scenarios should it be disabled?
3. How can you collect diagnostic information about coroutines in production safely, without exposing sensitive data or causing significant performance impact?
4. Which tools or patterns can you use to visualize coroutine execution flow and dependencies in complex systems?
5. How do you detect and debug race conditions that appear only under high load in coroutine-heavy codebases?

---

## Ссылки (RU)

- [Debugging `Coroutines`](https://kotlinlang.org/docs/debug-coroutines-with-idea.html)
- [kotlinx-coroutines-debug](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-debug/)
- [Android `Coroutine` testing and tools](https://developer.android.com/kotlin/coroutines/test)
- [LeakCanary](https://square.github.io/leakcanary/)

---

## References

- [Debugging `Coroutines`](https://kotlinlang.org/docs/debug-coroutines-with-idea.html)
- [kotlinx-coroutines-debug](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-debug/)
- [Android `Coroutine` testing and tools](https://developer.android.com/kotlin/coroutines/test)
- [LeakCanary](https://square.github.io/leakcanary/)

---

## Связанные Вопросы (RU)

- [[q-coroutine-exception-handler--kotlin--medium|Использование CoroutineExceptionHandler]]
- [[q-common-coroutine-mistakes--kotlin--medium|Типичные ошибки при работе с корутинами]]
- [[q-race-conditions-coroutines--kotlin--hard|Race condition в корутинах]]

---

## Related Questions

- [[q-coroutine-exception-handler--kotlin--medium|CoroutineExceptionHandler usage]]
- [[q-common-coroutine-mistakes--kotlin--medium|Common coroutine mistakes]]
- [[q-race-conditions-coroutines--kotlin--hard|Race conditions in coroutines]]
