---
topic: kotlin
id: "20251012-170005"
title: "NonCancellable context for critical cleanup operations / NonCancellable контекст для критических операций"
description: "Complete guide to using NonCancellable context for cleanup, when to use it, risks, and best practices with real examples"
topic: kotlin
subtopics: ["coroutines", "cancellation", "noncancellable", "cleanup", "finally"]
difficulty: medium
status: draft
created: 2025-10-12
updated: 2025-10-12
category: "coroutines-advanced"
tags: ["noncancellable", "cancellation", "cleanup", "finally", "resource-management"]
moc: "moc-kotlin"
related: [q-sealed-class-sealed-interface--kotlin--medium, q-kotlin-final-modifier--programming-languages--easy, q-java-kotlin-abstract-classes-difference--programming-languages--medium]
contributors: []
---

# NonCancellable context for critical cleanup operations / NonCancellable контекст для критических операций

## English Version

### Question
What is `NonCancellable` in Kotlin coroutines? When should you use it? Explain how to use it in finally blocks for critical cleanup, the risks involved, and best practices with real-world examples.

### Answer

#### What is NonCancellable?

`NonCancellable` is a special `CoroutineContext` that makes a coroutine **non-cancellable**. It allows suspend functions to execute even when the coroutine has been cancelled.

```kotlin
import kotlinx.coroutines.*

public object NonCancellable : AbstractCoroutineContextElement(Job), Job {
    // Job that cannot be cancelled
    // All Job operations are no-ops
}
```

**Key characteristics:**
- **Job that ignores cancellation**: `cancel()` does nothing
- **Allows suspend functions in finally**: Can call suspend functions after cancellation
- **Time-limited**: Even NonCancellable has limits (timeouts still work)
- **Use sparingly**: Only for critical cleanup

#### When to Use NonCancellable

Use NonCancellable **only** for critical cleanup operations:

1. **Closing resources** (files, network connections, database)
2. **Saving state** before shutdown
3. **Committing transactions** that must complete
4. **Sending analytics** about cancellation
5. **Releasing locks** or semaphores

**Do NOT use for:**
- Regular business logic
- Long-running operations
- Operations that should be cancellable
- "Just in case" scenarios

#### Using NonCancellable in finally Blocks

```kotlin
import kotlinx.coroutines.*

suspend fun demonstrateNonCancellable() = coroutineScope {
    val job = launch {
        try {
            println("Working...")
            delay(1000)
            println("Work completed")
        } finally {
            // WITHOUT NonCancellable - this throws CancellationException
            // delay(500) // Would throw!

            // WITH NonCancellable - cleanup can use suspend functions
            withContext(NonCancellable) {
                println("Cleanup starting...")
                delay(500) // Now safe to call
                println("Cleanup completed")
            }
        }
    }

    delay(100)
    job.cancel()
    job.join()
}

// Output:
// Working...
// Cleanup starting...
// Cleanup completed
```

**Why needed**: After cancellation, the coroutine is in a cancelled state. Normally, calling suspend functions throws `CancellationException`. NonCancellable suppresses this.

#### Real Example: Closing Resources

```kotlin
import kotlinx.coroutines.*
import java.io.*

suspend fun processFile(path: String) {
    val file = File(path)
    val reader = file.bufferedReader()

    try {
        // Process file
        reader.lineSequence().forEach { line ->
            println("Processing: $line")
            delay(100) // Simulate processing
        }
    } finally {
        // Critical: Must close file even if cancelled
        withContext(NonCancellable) {
            println("Closing file...")
            delay(50) // Simulated flush/close
            reader.close()
            println("File closed")
        }
    }
}

suspend fun demonstrateFileCleanup() {
    val job = CoroutineScope(Dispatchers.IO).launch {
        processFile("data.txt")
    }

    delay(250) // Let some processing happen
    job.cancel() // Cancel while processing
    job.join()
}

// Output:
// Processing: line1
// Processing: line2
// Closing file...
// File closed
```

#### Real Example: Saving State

```kotlin
import kotlinx.coroutines.*

data class AppState(val unsavedChanges: List<String>)

class StateManager {
    private var state = AppState(emptyList())

    suspend fun saveState() {
        delay(200) // Simulate network save
        println("State saved: ${state.unsavedChanges.size} changes")
    }

    suspend fun doWork() {
        try {
            repeat(10) { i ->
                state = state.copy(unsavedChanges = state.unsavedChanges + "Change $i")
                println("Made change $i")
                delay(100)
            }
        } finally {
            // CRITICAL: Save unsaved changes even if cancelled
            withContext(NonCancellable) {
                println("Saving unsaved changes on cancellation...")
                saveState()
                println("Save complete")
            }
        }
    }
}

suspend fun demonstrateStateSave() {
    val manager = StateManager()
    val job = CoroutineScope(Dispatchers.Default).launch {
        manager.doWork()
    }

    delay(350) // Let some work happen
    println("Cancelling...")
    job.cancelAndJoin()
    println("Job cancelled and cleanup done")
}

// Output:
// Made change 0
// Made change 1
// Made change 2
// Cancelling...
// Saving unsaved changes on cancellation...
// State saved: 3 changes
// Save complete
// Job cancelled and cleanup done
```

#### Real Example: Database Transaction Commit

```kotlin
import kotlinx.coroutines.*

class DatabaseTransaction {
    private val uncommittedChanges = mutableListOf<String>()

    suspend fun executeQuery(query: String) {
        delay(50) // Simulate query
        uncommittedChanges.add(query)
        println("Executed: $query")
    }

    suspend fun commit() {
        delay(100) // Simulate commit
        println("Committed ${uncommittedChanges.size} changes")
        uncommittedChanges.clear()
    }

    suspend fun rollback() {
        delay(50)
        println("Rolled back ${uncommittedChanges.size} changes")
        uncommittedChanges.clear()
    }
}

suspend fun performTransaction() {
    val transaction = DatabaseTransaction()

    try {
        transaction.executeQuery("INSERT INTO users ...")
        delay(100)
        transaction.executeQuery("UPDATE users ...")
        delay(100)
        transaction.executeQuery("DELETE FROM sessions ...")

        // Normal commit
        transaction.commit()
    } catch (e: CancellationException) {
        // Cancelled - must rollback
        withContext(NonCancellable) {
            println("Transaction cancelled, rolling back...")
            transaction.rollback()
        }
        throw e // Re-throw to propagate cancellation
    } finally {
        // Additional cleanup if needed
        withContext(NonCancellable) {
            println("Closing transaction...")
            delay(50)
            println("Transaction closed")
        }
    }
}

suspend fun demonstrateTransaction() {
    val job = CoroutineScope(Dispatchers.IO).launch {
        performTransaction()
    }

    delay(150) // Cancel mid-transaction
    println("Cancelling transaction...")
    job.cancelAndJoin()
}

// Output:
// Executed: INSERT INTO users ...
// Executed: UPDATE users ...
// Cancelling transaction...
// Transaction cancelled, rolling back...
// Rolled back 2 changes
// Closing transaction...
// Transaction closed
```

#### Real Example: Analytics Event on Cancellation

```kotlin
import kotlinx.coroutines.*

object Analytics {
    suspend fun logEvent(event: String, properties: Map<String, Any>) {
        delay(100) // Simulate network call
        println("Analytics: $event - $properties")
    }
}

suspend fun longRunningTask(taskId: String) {
    val startTime = System.currentTimeMillis()

    try {
        println("Starting task $taskId")
        delay(5000) // Long operation
        println("Task $taskId completed")

        // Log success
        Analytics.logEvent("task_completed", mapOf("taskId" to taskId))
    } finally {
        val duration = System.currentTimeMillis() - startTime

        // MUST log cancellation event even if cancelled
        withContext(NonCancellable) {
            println("Logging cancellation event...")
            Analytics.logEvent(
                "task_cancelled",
                mapOf(
                    "taskId" to taskId,
                    "duration_ms" to duration,
                    "reason" to "user_cancellation"
                )
            )
            println("Analytics sent")
        }
    }
}

suspend fun demonstrateAnalytics() {
    val job = CoroutineScope(Dispatchers.Default).launch {
        longRunningTask("task-123")
    }

    delay(1000) // Cancel after 1 second
    job.cancelAndJoin()
}

// Output:
// Starting task task-123
// Logging cancellation event...
// Analytics: task_cancelled - {taskId=task-123, duration_ms=1001, reason=user_cancellation}
// Analytics sent
```

#### Risks of Using NonCancellable

**1. Blocking cancellation too long**

```kotlin
// BAD: Long operation in NonCancellable
suspend fun badCleanup() {
    try {
        // work
    } finally {
        withContext(NonCancellable) {
            // This is BAD - takes too long
            repeat(1000) {
                processItem(it) // Each takes 100ms
                delay(100)
            }
            // Cleanup takes 100 seconds!
        }
    }
}

// GOOD: Keep NonCancellable short
suspend fun goodCleanup() {
    try {
        // work
    } finally {
        withContext(NonCancellable) {
            // Quick essential cleanup only
            closeResource() // 50ms
        }
    }
}
```

**2. Hiding bugs**

```kotlin
// BAD: Using NonCancellable to avoid fixing cancellation issues
suspend fun badUsage() {
    withContext(NonCancellable) {
        // This should be cancellable, but we're hiding the issue
        performBusinessLogic()
    }
}

// GOOD: Make code properly cancellable
suspend fun goodUsage() {
    // Business logic respects cancellation
    performCancellableBusinessLogic()

    // Only cleanup is non-cancellable
    try {
        // ...
    } finally {
        withContext(NonCancellable) {
            cleanup()
        }
    }
}
```

**3. Resource exhaustion**

```kotlin
// BAD: NonCancellable without time limit
suspend fun riskyCleanup() {
    try {
        // work
    } finally {
        withContext(NonCancellable) {
            // If this hangs, coroutine never finishes!
            saveToUnreliableServer()
        }
    }
}

// GOOD: Add timeout even with NonCancellable
suspend fun safeCleanup() {
    try {
        // work
    } finally {
        withContext(NonCancellable) {
            withTimeout(5000) {
                // Max 5 seconds for cleanup
                saveToUnreliableServer()
            }
        }
    }
}
```

#### NonCancellable Doesn't Prevent Cancellation

NonCancellable doesn't **prevent** cancellation; it allows suspend functions to **complete despite** cancellation:

```kotlin
suspend fun demonstrateCancellationStillHappens() {
    val job = launch {
        try {
            println("Working...")
            delay(1000)
        } finally {
            println("Cancelled: ${!isActive}")  // true - still cancelled

            withContext(NonCancellable) {
                println("In NonCancellable")
                println("Still cancelled: ${!isActive}")  // false - temporarily not cancelled
                delay(500)
                println("Cleanup done")
            }

            println("After NonCancellable, cancelled: ${!isActive}")  // true - cancelled again
        }
    }

    delay(100)
    job.cancelAndJoin()
}

// Output:
// Working...
// Cancelled: true
// In NonCancellable
// Still cancelled: false
// Cleanup done
// After NonCancellable, cancelled: true
```

**Key insight**: NonCancellable is a **temporary context override**, not permanent cancellation prevention.

#### Time Limits Even with NonCancellable

Even NonCancellable respects **timeouts**:

```kotlin
suspend fun demonstrateTimeout() {
    try {
        withTimeout(500) {
            try {
                delay(1000) // Will timeout
            } finally {
                withContext(NonCancellable) {
                    println("Cleanup starting...")
                    delay(200) // Allowed despite timeout
                    println("Cleanup done")
                }
            }
        }
    } catch (e: TimeoutCancellationException) {
        println("Timed out: ${e.message}")
    }
}

// Output:
// Cleanup starting...
// Cleanup done
// Timed out: Timed out waiting for 500 ms
```

**Important**: NonCancellable allows cleanup to complete, but doesn't prevent the parent timeout from firing.

#### Best Practice: Keep It Short

```kotlin
// GOOD: Short, focused cleanup
suspend fun shortCleanup() {
    try {
        // work
    } finally {
        withContext(NonCancellable) {
            resource.close()  // < 100ms
            saveState()       // < 200ms
        }
        // Total: ~300ms - acceptable
    }
}

// BAD: Long, complex cleanup
suspend fun longCleanup() {
    try {
        // work
    } finally {
        withContext(NonCancellable) {
            syncAllDataToServer()   // 10 seconds
            regenerateCaches()      // 5 seconds
            sendEmailNotifications() // 3 seconds
        }
        // Total: 18 seconds - unacceptable!
    }
}
```

**Guideline**: NonCancellable operations should complete in **< 1 second** ideally, **< 5 seconds** maximum.

#### Alternative: Use Regular Blocking Code in finally

For very simple cleanup, consider **not using suspend functions**:

```kotlin
suspend fun cleanupWithoutSuspend() {
    val file = File("data.txt")

    try {
        // Suspend work
        delay(1000)
    } finally {
        // Simple blocking cleanup - no NonCancellable needed
        file.delete()  // Regular blocking call
        println("File deleted")
    }
}

// When to use each:
// - Blocking cleanup: Simple, synchronous operations (file.close(), map.clear())
// - NonCancellable: When cleanup requires suspend functions (network, delay)
```

#### Testing Cleanup with Cancellation

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class NonCancellableTests {
    @Test
    fun testCleanupExecutesOnCancellation() = runTest {
        var cleanupExecuted = false

        val job = launch {
            try {
                delay(1000)
            } finally {
                withContext(NonCancellable) {
                    delay(100)
                    cleanupExecuted = true
                }
            }
        }

        advanceTimeBy(100)
        job.cancel()
        job.join()

        assertTrue(cleanupExecuted)
    }

    @Test
    fun testCleanupCompletesWithTimeout() = runTest {
        var cleanupDone = false

        try {
            withTimeout(500) {
                try {
                    delay(1000)
                } finally {
                    withContext(NonCancellable) {
                        delay(200)
                        cleanupDone = true
                    }
                }
            }
        } catch (e: TimeoutCancellationException) {
            // Expected
        }

        assertTrue(cleanupDone)
    }

    @Test
    fun testNonCancellableDoesNotPreventCancellation() = runTest {
        val job = launch {
            try {
                delay(1000)
            } finally {
                withContext(NonCancellable) {
                    delay(100)
                }
            }
        }

        job.cancel()
        job.join()

        assertTrue(job.isCancelled)
    }
}
```

### Common Pitfalls

**1. Forgetting to re-throw CancellationException**

```kotlin
// BAD: Swallowing cancellation
try {
    work()
} catch (e: CancellationException) {
    withContext(NonCancellable) {
        cleanup()
    }
    // Missing: throw e
}

// GOOD: Re-throwing cancellation
try {
    work()
} catch (e: CancellationException) {
    withContext(NonCancellable) {
        cleanup()
    }
    throw e // Propagate cancellation
}
```

**2. Using NonCancellable for non-cleanup code**

```kotlin
// BAD: Business logic in NonCancellable
withContext(NonCancellable) {
    processUserRequest() // Should be cancellable!
}

// GOOD: Only cleanup in NonCancellable
try {
    processUserRequest() // Cancellable
} finally {
    withContext(NonCancellable) {
        releaseResources() // Non-cancellable
    }
}
```

**3. No timeout on NonCancellable operations**

```kotlin
// BAD: No timeout
withContext(NonCancellable) {
    sendToUnreliableServer() // Might hang forever
}

// GOOD: Timeout even with NonCancellable
withContext(NonCancellable) {
    withTimeout(5000) {
        sendToUnreliableServer()
    }
}
```

### Summary

**NonCancellable** allows suspend functions to execute during cleanup after cancellation:

- **Use for**: Critical cleanup (close resources, save state, commit transactions)
- **Don't use for**: Business logic, long operations, "just in case"
- **Keep short**: < 1 second ideally, < 5 seconds maximum
- **Add timeouts**: Even NonCancellable should have time limits
- **Alternative**: Use regular blocking code for simple cleanup
- **Remember**: NonCancellable doesn't prevent cancellation, it allows cleanup despite cancellation

**Pattern:**
```kotlin
try {
    // Regular cancellable work
} finally {
    withContext(NonCancellable) {
        // Short, critical cleanup only
    }
}
```

---

## Russian Version / Русская версия

### Вопрос
Что такое `NonCancellable` в корутинах Kotlin? Когда следует его использовать? Объясните как использовать его в блоках finally для критической очистки, связанные риски и лучшие практики с реальными примерами.

### Ответ

#### Что такое NonCancellable?

`NonCancellable` - это специальный `CoroutineContext`, который делает корутину **не отменяемой**. Он позволяет suspend функциям выполняться даже когда корутина была отменена.

**Ключевые характеристики:**
- **Job который игнорирует отмену**: `cancel()` ничего не делает
- **Позволяет suspend функции в finally**: Можно вызывать suspend функции после отмены
- **Ограничен по времени**: Даже NonCancellable имеет лимиты (таймауты всё равно работают)
- **Используйте экономно**: Только для критической очистки

#### Когда использовать NonCancellable

Используйте NonCancellable **только** для критических операций очистки:

1. **Закрытие ресурсов** (файлы, сетевые соединения, база данных)
2. **Сохранение состояния** перед завершением
3. **Коммит транзакций** которые должны завершиться
4. **Отправка аналитики** об отмене
5. **Освобождение блокировок** или семафоров

**НЕ используйте для:**
- Обычной бизнес-логики
- Длительных операций
- Операций которые должны быть отменяемыми
- Сценариев "на всякий случай"

#### Использование NonCancellable в блоках finally

```kotlin
import kotlinx.coroutines.*

suspend fun demonstrateNonCancellable() = coroutineScope {
    val job = launch {
        try {
            println("Работаем...")
            delay(1000)
            println("Работа завершена")
        } finally {
            // БЕЗ NonCancellable - это выбросит CancellationException
            // delay(500) // Выбросит!

            // С NonCancellable - очистка может использовать suspend функции
            withContext(NonCancellable) {
                println("Начало очистки...")
                delay(500) // Теперь безопасно вызывать
                println("Очистка завершена")
            }
        }
    }

    delay(100)
    job.cancel()
    job.join()
}
```

**Почему нужно**: После отмены корутина находится в отменённом состоянии. Обычно вызов suspend функций выбрасывает `CancellationException`. NonCancellable подавляет это.

#### Реальный пример: Закрытие ресурсов

```kotlin
import kotlinx.coroutines.*
import java.io.*

suspend fun processFile(path: String) {
    val file = File(path)
    val reader = file.bufferedReader()

    try {
        // Обработка файла
        reader.lineSequence().forEach { line ->
            println("Обработка: $line")
            delay(100)
        }
    } finally {
        // КРИТИЧНО: Должны закрыть файл даже если отменено
        withContext(NonCancellable) {
            println("Закрытие файла...")
            delay(50) // Имитация flush/close
            reader.close()
            println("Файл закрыт")
        }
    }
}
```

#### Реальный пример: Сохранение состояния

```kotlin
import kotlinx.coroutines.*

data class AppState(val unsavedChanges: List<String>)

class StateManager {
    private var state = AppState(emptyList())

    suspend fun saveState() {
        delay(200) // Имитация сохранения по сети
        println("Состояние сохранено: ${state.unsavedChanges.size} изменений")
    }

    suspend fun doWork() {
        try {
            repeat(10) { i ->
                state = state.copy(unsavedChanges = state.unsavedChanges + "Изменение $i")
                println("Сделано изменение $i")
                delay(100)
            }
        } finally {
            // КРИТИЧНО: Сохранить несохранённые изменения даже если отменено
            withContext(NonCancellable) {
                println("Сохранение несохранённых изменений при отмене...")
                saveState()
                println("Сохранение завершено")
            }
        }
    }
}
```

#### Риски использования NonCancellable

**1. Блокирование отмены слишком долго**

```kotlin
// ПЛОХО: Долгая операция в NonCancellable
suspend fun badCleanup() {
    try {
        // работа
    } finally {
        withContext(NonCancellable) {
            // Это ПЛОХО - занимает слишком долго
            repeat(1000) {
                processItem(it)
                delay(100)
            }
            // Очистка занимает 100 секунд!
        }
    }
}

// ХОРОШО: Держите NonCancellable коротким
suspend fun goodCleanup() {
    try {
        // работа
    } finally {
        withContext(NonCancellable) {
            // Только быстрая критическая очистка
            closeResource() // 50мс
        }
    }
}
```

#### Лучшая практика: Держите коротким

**Руководство**: Операции NonCancellable должны завершаться за **< 1 секунду** идеально, **< 5 секунд** максимум.

#### Альтернатива: Используйте обычный блокирующий код в finally

Для очень простой очистки рассмотрите **не использование suspend функций**:

```kotlin
suspend fun cleanupWithoutSuspend() {
    val file = File("data.txt")

    try {
        delay(1000)
    } finally {
        // Простая блокирующая очистка - NonCancellable не нужен
        file.delete()  // Обычный блокирующий вызов
        println("Файл удалён")
    }
}
```

### Резюме

**NonCancellable** позволяет suspend функциям выполняться во время очистки после отмены:

- **Используйте для**: Критическая очистка (закрытие ресурсов, сохранение состояния)
- **Не используйте для**: Бизнес-логика, длительные операции
- **Держите коротким**: < 1 секунды идеально, < 5 секунд максимум
- **Добавляйте таймауты**: Даже NonCancellable должен иметь временные лимиты
- **Помните**: NonCancellable не предотвращает отмену, он позволяет очистку несмотря на отмену

---

## Follow-ups

1. How does NonCancellable interact with CoroutineExceptionHandler? Are exceptions in NonCancellable blocks handled differently?

2. Can you nest multiple withContext(NonCancellable) blocks? What are the implications?

3. How would you implement a custom context element similar to NonCancellable but with a time budget?

4. What happens if you launch a new coroutine inside a NonCancellable block? Is the child coroutine cancellable?

5. How does NonCancellable affect structured concurrency principles? Does it violate them?

6. Can you use NonCancellable with Flow operators? What would be the use case?

7. How would you test that cleanup code properly uses NonCancellable in a complex coroutine hierarchy?

## References

- [Kotlin Coroutines Guide - Cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [NonCancellable API Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-non-cancellable/)
- [Coroutine Context Documentation](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [Roman Elizarov - Cancellation in Coroutines](https://medium.com/@elizarov/cancellation-in-coroutines-aa6b90163629)
- [Exception Handling in Coroutines](https://kotlinlang.org/docs/exception-handling.html)

## Related Questions

- [[q-job-state-machine-transitions--kotlin--medium]] - Job states during cancellation
- [[q-structured-concurrency-violations--kotlin--hard]] - Proper cancellation patterns
- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Resource cleanup and leaks
- [[q-testing-coroutine-timing-control--kotlin--medium]] - Testing cancellation
- [[q-deferred-async-patterns--kotlin--medium]] - Cancellation in async

## Tags
#kotlin #coroutines #noncancellable #cancellation #cleanup #finally #resource-management
