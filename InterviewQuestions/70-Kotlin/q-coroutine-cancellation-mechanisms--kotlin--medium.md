---
id: kotlin-205
title: "Coroutine Cancellation Mechanisms / Механизмы Отмены Корутин"
aliases: [Coroutine Cancellation, Механизмы отмены корутин]
topic: kotlin
subtopics: [coroutines, cancellation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-structured-concurrency]
created: 2025-10-15
updated: 2025-10-31
tags: [kotlin, coroutines, cancellation, cooperative, isactive, cancellationexception, difficulty/medium]
source: Kotlin Coroutines Interview Questions PDF
---
# Вопрос (RU)
> Как работает отмена корутин и чем она отличается от отмены потока?

---

# Question (EN)
> How does coroutine cancellation work, and how is it different from canceling a Thread?
## Ответ (RU)

**Отмена корутин является кооперативной**, то есть корутина должна сотрудничать, проверяя отмену в точках приостановки или вручную. Это фундаментально отличается от небезопасного принудительного завершения потока и от устаревших механизмов типа `Thread.stop()`.

### Кооперативная Отмена

**Ключевой Принцип**: Корутины не отменяются немедленно автоматически — они проверяют отмену в определенных точках.

**Точки Отмены**:
```kotlin
// Корутина проверяет отмену в этих точках:
delay(1000)           // - Проверяет отмену
yield()               // - Проверяет отмену
withContext(Dispatchers.IO) { }   // - Проверяет отмену
// Любая приостанавливающая функция из kotlinx.coroutines,
// корректно поддерживающая cooperative cancellation
```

### Как Работает Отмена

**Базовый Пример**:
```kotlin
val job = lifecycleScope.launch {
    repeat(1000) { i ->
        println("Job: Работаю $i...")
        delay(500) // Здесь происходит проверка отмены
    }
}

delay(1300)
println("Отменяю job...")
job.cancel() // Запрос на отмену
job.join()   // Ожидание завершения отмены
println("Job отменен")

// Возможный вывод:
// Job: Работаю 0...
// Job: Работаю 1...
// Job: Работаю 2...
// Отменяю job...
// Job отменен
```

**Что Происходит При Отмене**:
1. Вызывается `job.cancel()`
2. Job помечается как отменяющийся
3. В следующей точке приостановки (например, `delay()`) корутина проверяет статус
4. Выбрасывается `CancellationException`
5. Корутина завершается (или выполняет `finally`, затем завершается)

### Ручные Проверки Отмены

**Проблема - CPU-интенсивный цикл**:
```kotlin
// - ПЛОХО: Не отменится быстро
val job = launch {
    var nextPrintTime = System.currentTimeMillis()
    var i = 0
    while (i < 5) { // Нет точек приостановки!
        if (System.currentTimeMillis() >= nextPrintTime) {
            println("Вычисляю $i...")
            nextPrintTime += 500
            i++
        }
    }
}

delay(1000)
job.cancel() // Отмена не сработает сразу!
```

**Решение 1 - Проверка isActive**:
```kotlin
// - ХОРОШО: Ручная проверка отмены
val job = launch {
    var nextPrintTime = System.currentTimeMillis()
    var i = 0
    while (i < 5 && isActive) { // Проверяем isActive
        if (System.currentTimeMillis() >= nextPrintTime) {
            println("Вычисляю $i...")
            nextPrintTime += 500
            i++
        }
    }
    println("Вычисления отменены!")
}

delay(1000)
job.cancel()
```

**Решение 2 - Использование yield()**:
```kotlin
// - ХОРОШО: Периодический yield() для отмены
val job = launch {
    repeat(1000) { i ->
        // Тяжелые вычисления
        performHeavyComputation()
        yield() // Даем шанс отмениться
    }
}

delay(100)
job.cancel()
```

### CancellationException

**Перехват Отмены**:
```kotlin
val job = launch {
    try {
        repeat(1000) { i ->
            println("Работаю $i...")
            delay(500)
        }
    } catch (e: CancellationException) {
        println("Корутина отменена: ${e.message}")
        // Обычно не следует бесследно проглатывать отмену
        throw e
    } finally {
        println("Код очистки выполняется здесь")
    }
}

delay(1300)
job.cancel()
```

**Важно**: `CancellationException` — особое исключение, сигнализирующее об отмене. Как правило, его нужно пропускать дальше (или перебрасывать), а не бесшумно проглатывать, чтобы не ломать кооперативную отмену.

### Очистка Ресурсов

**Паттерн Try-Finally**:
```kotlin
val job = launch {
    val resource = acquireResource()
    try {
        repeat(1000) { i ->
            println("Использую ресурс $i")
            delay(500)
        }
    } finally {
        // Всегда выполняется при нормальном завершении или отмене этой корутины
        resource.close()
        println("Ресурс закрыт")
    }
}

delay(1300)
job.cancel()
job.join()
```

### Отмена Родитель-Потомок

**Автоматическая Отмена Потомков**:
```kotlin
val parent = launch {
    val child1 = launch {
        repeat(1000) { i ->
            println("Потомок 1: $i")
            delay(500)
        }
    }

    val child2 = launch {
        repeat(1000) { i ->
            println("Потомок 2: $i")
            delay(500)
        }
    }

    delay(2000)
}

delay(1000)
parent.cancel() // Отменяет родителя И обоих потомков (в рамках структурированной конкуррентности)
parent.join()
```

### Резюме

**Отмена корутин**:
- **Кооперативная** — требует проверки корутиной
- **Безопасная** — предсказуемая, не повреждает состояние при корректном использовании
- **Структурированная** — родитель отменяет всех потомков
- **Чистая** — `finally` блоки выполняются при отмене корутин в рамках обычного жизненного цикла
- **Явная** — использует `isActive`, `yield()`, точки приостановки

**Отличия от потоков**:
- Потоки (современный подход): отмена через `interrupt()` тоже кооперативна и требует явных проверок; принудительное завершение (как `stop()`) считается небезопасным и не должно использоваться
- Корутины: встроенная кооперативная отмена, лучше интегрированная со структурированной конкуррентностью

---

## Answer (EN)

**Coroutine cancellation is cooperative**, meaning a coroutine must cooperate by checking for cancellation at suspension points or manually. This contrasts with unsafe forced thread termination mechanisms (like the deprecated `Thread.stop()`), and is similar in spirit to cooperative thread interruption.

### Cooperative Cancellation

**Key Principle**: Coroutines don't cancel themselves immediately; they observe cancellation at specific points.

**Cancellation Points**:
```kotlin
// Coroutine checks for cancellation at these points:
delay(1000)           // - Checks cancellation
yield()               // - Checks cancellation
withContext(Dispatchers.IO) { }   // - Checks cancellation
// Any suspending function from kotlinx.coroutines
// that is implemented to respect cooperative cancellation
```

### How Cancellation Works

**Basic Example**:
```kotlin
val job = lifecycleScope.launch {
    repeat(1000) { i ->
        println("Job: I'm working $i...")
        delay(500) // Cancellation check happens here
    }
}

delay(1300)
println("Canceling job...")
job.cancel() // Request cancellation
job.join()   // Wait for cancellation to complete
println("Job canceled")

// Possible output:
// Job: I'm working 0...
// Job: I'm working 1...
// Job: I'm working 2...
// Canceling job...
// Job canceled
```

**What Happens During Cancellation**:
1. `job.cancel()` is called
2. The job is marked as canceling
3. At the next suspension point (e.g., `delay()`), the coroutine checks its status
4. A `CancellationException` is thrown
5. The coroutine terminates (running `finally` before completion)

### Manual Cancellation Checks

**Problem - CPU-intensive loop**:
```kotlin
// - BAD: Won't cancel promptly
val job = launch {
    var nextPrintTime = System.currentTimeMillis()
    var i = 0
    while (i < 5) { // No suspension points!
        if (System.currentTimeMillis() >= nextPrintTime) {
            println("Computing $i...")
            nextPrintTime += 500
            i++
        }
    }
}

delay(1000)
job.cancel() // Cancellation won't take effect immediately!
```

**Solution 1 - Check isActive**:
```kotlin
// - GOOD: Manual cancellation check
val job = launch {
    var nextPrintTime = System.currentTimeMillis()
    var i = 0
    while (i < 5 && isActive) { // Check isActive
        if (System.currentTimeMillis() >= nextPrintTime) {
            println("Computing $i...")
            nextPrintTime += 500
            i++
        }
    }
    println("Computation canceled!")
}

delay(1000)
job.cancel()

// Output:
// Computing 0...
// Computing 1...
// Computation canceled!
```

**Solution 2 - Use yield()**:
```kotlin
// - GOOD: Periodic yield() for cancellation
val job = launch {
    repeat(1000) { i ->
        // Heavy computation here
        performHeavyComputation()
        yield() // Give a chance to cancel
    }
}

delay(100)
job.cancel()
```

### CancellationException

**Catching Cancellation**:
```kotlin
val job = launch {
    try {
        repeat(1000) { i ->
            println("Working $i...")
            delay(500)
        }
    } catch (e: CancellationException) {
        println("Coroutine was cancelled: ${e.message}")
        // In most cases, don't swallow cancellation silently
        throw e
    } finally {
        println("Cleanup code runs here")
    }
}

delay(1300)
job.cancel()

// Output:
// Working 0...
// Working 1...
// Working 2...
// Coroutine was cancelled: ...
// Cleanup code runs here
```

**Important**: `CancellationException` is special — it indicates normal cancellation. Typically you should let it propagate (or rethrow) instead of swallowing it silently, unless you intentionally convert cancellation into another outcome.

### Resource Cleanup

**Try-Finally Pattern**:
```kotlin
val job = launch {
    val resource = acquireResource()
    try {
        repeat(1000) { i ->
            println("Using resource $i")
            delay(500)
        }
    } finally {
        // Always runs for this coroutine on completion or cancellation
        resource.close()
        println("Resource closed")
    }
}

delay(1300)
job.cancel()
job.join()
```

**NonCancellable Context** (for cleanup that must complete):
```kotlin
val job = launch {
    try {
        work()
    } finally {
        withContext(NonCancellable) {
            // This block itself will not be cancelled
            delay(1000) // Cleanup that takes time
            println("Cleanup completed")
        }
    }
}

job.cancel()
```

### Parent-Child Cancellation

**Automatic Child Cancellation**:
```kotlin
val parent = launch {
    val child1 = launch {
        repeat(1000) { i ->
            println("Child 1: $i")
            delay(500)
        }
    }

    val child2 = launch {
        repeat(1000) { i ->
            println("Child 2: $i")
            delay(500)
        }
    }

    delay(2000)
}

delay(1000)
parent.cancel() // Cancels parent AND both children (in structured concurrency)
parent.join()

// Both child1 and child2 are automatically canceled
```

### Coroutine vs Thread Cancellation

| Aspect | Coroutines | Threads (modern best practice) |
|--------|-----------|---------------------------------|
| **Type** | Cooperative | Cooperative via `interrupt()` |
| **Mechanism** | Checks at suspension points / `isActive` | Check interruption status or handle `InterruptedException` in blocking calls |
| **Control** | Integrated with structured concurrency | Manual management; no hierarchy by default |
| **Safety** | Safe, predictable; no forced kill | Forced termination APIs (`stop`) are unsafe and deprecated |
| **Cleanup** | `finally` runs on completion/cancellation of a coroutine | `finally` runs when thread exits normally or by cooperative interruption |

**Thread Interruption (for comparison)**:
```kotlin
// Thread interruption (cooperative)
val thread = Thread {
    try {
        while (!Thread.currentThread().isInterrupted) {
            // Work
        }
    } catch (e: InterruptedException) {
        // Handle interruption
    }
}

thread.start()
thread.interrupt() // Signals interruption; thread must cooperate
```

**Coroutine Cancellation (modern way)**:
```kotlin
// Coroutine cancellation (structured & cooperative)
val job = launch {
    while (isActive) {
        // Work
        yield() // Cooperative cancellation point
    }
}

job.cancel() // Safe, predictable cancellation
```

### Best Practices

```kotlin
// - DO: Check isActive in long-running loops
while (isActive) {
    performWork()
}

// - DO: Use yield() in CPU-intensive work
repeat(1000) {
    heavyComputation()
    yield()
}

// - DO: Clean up in finally blocks
try {
    useResource()
} finally {
    cleanupResource()
}

// - DO: Let CancellationException propagate (unless you have a clear policy)
catch (e: CancellationException) {
    cleanup()
    throw e // Re-throw in most cases
}

// - DON'T: Ignore cancellation in infinite loops
while (true) { // No cancellation check!
    doWork()
}

// - DON'T: Silently swallow CancellationException
catch (e: CancellationException) {
    // Don't just ignore it without reason!
}
```

### Summary

**Coroutine cancellation** is:
- **Cooperative** — requires the coroutine to check
- **Safe** — predictable when cancellation points are used correctly
- **Structured** — parent cancels all children within its scope
- **Clean** — `finally` blocks run for coroutine completion/cancellation
- **Explicit** — uses `isActive`, `yield()`, and suspension points

**Different from threads** (in practice):
- Threads: cooperative interruption without built-in structured hierarchy; forced termination APIs are unsafe
- Coroutines: built-in cooperative cancellation + structured concurrency and better integration with libraries

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Cancellation and Timeouts - Kotlin Docs](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)

---

**Source**: Kotlin Coroutines Interview Questions for Android Developers PDF

## Related Questions

- [[q-structured-concurrency-kotlin--kotlin--medium]]
- [[q-supervisor-scope-vs-coroutine-scope--kotlin--medium]]
