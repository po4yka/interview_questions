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
related: []
created: 2025-10-15
updated: 2025-10-31
tags:
  - kotlin
  - coroutines
  - cancellation
  - cooperative
  - isactive
  - cancellationexception
  - difficulty/medium
original_language: en
source: Kotlin Coroutines Interview Questions PDF
subtopics:
  - coroutines
  - cancellation
  - cooperative-cancellation
---
# Question (EN)
> How does coroutine cancellation work, and how is it different from canceling a Thread?
# Вопрос (RU)
> Как работает отмена корутин и чем она отличается от отмены потока?

---

## Answer (EN)

**Coroutine cancellation is cooperative**, meaning a coroutine must cooperate by checking for cancellation at suspension points or manually. This differs fundamentally from thread interruption.

### Cooperative Cancellation

**Key Principle**: Coroutines don't cancel immediately - they check for cancellation at specific points.

**Cancellation Points**:
```kotlin
// Coroutine checks for cancellation at these points:
delay(1000)           // - Checks cancellation
yield()               // - Checks cancellation
withContext(IO) { }   // - Checks cancellation
// Any suspending function from kotlinx.coroutines
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

// Output:
// Job: I'm working 0...
// Job: I'm working 1...
// Job: I'm working 2...
// Canceling job...
// Job canceled
```

**What Happens During Cancellation**:
1. `job.cancel()` is called
2. Job is marked as canceling
3. At next suspension point (`delay()`), coroutine checks status
4. `CancellationException` is thrown
5. Coroutine terminates

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
job.cancel() // Cancellation won't work immediately!
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
        // Don't swallow! Re-throw or let it propagate
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

**Important**: `CancellationException` is special - it should be re-thrown, not swallowed.

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
        // Always runs, even if canceled
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
            // This block won't be cancelled
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
parent.cancel() // Cancels parent AND both children
parent.join()

// Both child1 and child2 are automatically canceled
```

### Coroutine vs Thread Cancellation

| Aspect | Coroutines | Threads |
|--------|-----------|---------|
| **Type** | Cooperative | Preemptive (interrupt) |
| **Mechanism** | Checks at suspension points | Can halt at any point |
| **Control** | Must reach cancellation point | Immediate (but unsafe) |
| **Safety** | Safe, predictable | Risky, can corrupt state |
| **Cleanup** | `finally` guaranteed to run | `finally` might not run |
| **Child handling** | Auto-cancels all children | Manual tracking needed |

**Thread Interruption (for comparison)**:
```kotlin
// Thread interruption (old way)
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
thread.interrupt() // Can interrupt at any point - risky!
```

**Coroutine Cancellation (modern way)**:
```kotlin
// Coroutine cancellation (better)
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

// - DO: Let CancellationException propagate
catch (e: CancellationException) {
    cleanup()
    throw e // Re-throw!
}

// - DON'T: Ignore cancellation
while (true) { // No cancellation check!
    doWork()
}

// - DON'T: Swallow CancellationException
catch (e: CancellationException) {
    // Don't just ignore it!
}
```

### Summary

**Coroutine cancellation** is:
- - **Cooperative** - requires coroutine to check
- - **Safe** - predictable, won't corrupt state
- - **Structured** - parent cancels all children
- - **Clean** - finally blocks always run
- - **Explicit** - uses `isActive`, `yield()`, suspension points

**Different from threads**:
- Threads: Preemptive, risky, immediate
- Coroutines: Cooperative, safe, at cancellation points

---

## Ответ (RU)

**Отмена корутин является кооперативной**, то есть корутина должна сотрудничать, проверяя отмену в точках приостановки или вручную. Это фундаментально отличается от прерывания потоков.

### Кооперативная Отмена

**Ключевой Принцип**: Корутины не отменяются немедленно - они проверяют отмену в определенных точках.

**Точки Отмены**:
```kotlin
// Корутина проверяет отмену в этих точках:
delay(1000)           // - Проверяет отмену
yield()               // - Проверяет отмену
withContext(IO) { }   // - Проверяет отмену
// Любая приостанавливающая функция из kotlinx.coroutines
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

// Вывод:
// Job: Работаю 0...
// Job: Работаю 1...
// Job: Работаю 2...
// Отменяю job...
// Job отменен
```

**Что Происходит При Отмене**:
1. Вызывается `job.cancel()`
2. Job помечается как отменяющийся
3. В следующей точке приостановки (`delay()`) корутина проверяет статус
4. Выбрасывается `CancellationException`
5. Корутина завершается

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
        // Не проглатывайте! Перебросьте или дайте распространиться
        throw e
    } finally {
        println("Код очистки выполняется здесь")
    }
}

delay(1300)
job.cancel()
```

**Важно**: `CancellationException` - особенное исключение, его нужно перебрасывать, а не проглатывать.

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
        // Всегда выполняется, даже при отмене
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
parent.cancel() // Отменяет родителя И обоих потомков
parent.join()
```

### Резюме

**Отмена корутин**:
- - **Кооперативная** - требует проверки корутиной
- - **Безопасная** - предсказуемая, не повреждает состояние
- - **Структурированная** - родитель отменяет всех потомков
- - **Чистая** - finally блоки всегда выполняются
- - **Явная** - использует `isActive`, `yield()`, точки приостановки

**Отличия от потоков**:
- Потоки: Преемптивная, рискованная, немедленная
- Корутины: Кооперативная, безопасная, в точках отмены

---

## References

- [Cancellation and Timeouts - Kotlin Docs](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)

---

**Source**: Kotlin Coroutines Interview Questions for Android Developers PDF

## Related Questions

- [[q-structured-concurrency-kotlin--kotlin--medium]]
- [[q-supervisor-scope-vs-coroutine-scope--kotlin--medium]]
