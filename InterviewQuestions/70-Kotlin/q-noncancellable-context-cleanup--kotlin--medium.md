---\
id: kotlin-119
title: "NonCancellable context for critical cleanup operations / NonCancellable контекст для критических операций"
aliases: [Cancellation, Cleanup, NonCancellable, NonCancellable контекст, Resource Management]
topic: kotlin
subtopics: [coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-sealed-class-sealed-interface--kotlin--medium]
created: 2025-10-12
updated: 2025-11-09
tags: [cancellation, cleanup, coroutines, difficulty/medium, kotlin, noncancellable, resource-management]
---\
# Вопрос (RU)

> Что такое `NonCancellable` в корутинах Kotlin? Когда следует его использовать? Объясните, как использовать его в блоках `finally` для критической очистки, связанные риски и лучшие практики с реальными примерами.

---

# Question (EN)

> What is `NonCancellable` in Kotlin coroutines? When should you use it? Explain how to use it in `finally` blocks for critical cleanup, the risks involved, and best practices with real-world examples.

## Ответ (RU)

#### Что Такое `NonCancellable`?

`NonCancellable` — это специальный элемент `CoroutineContext` (тип `Job`), который делает блок кода выполняющимся в контексте, игнорирующем отмену. Он позволяет suspend-функциям внутри этого контекста выполняться даже тогда, когда окружающая корутина была отменена.

```kotlin
import kotlinx.coroutines.*

public object NonCancellable : AbstractCoroutineContextElement(Job), Job {
    // Job, который не переходит в состояние отмены
    // Все операции отмены Job игнорируются
}
```

**Ключевые характеристики:**
- **Job, который игнорирует отмену**: вызов `cancel()` на этом `Job` не меняет его состояние.
- **Позволяет suspend-функции в `finally`**: можно безопасно вызывать suspend-функции для очистки после отмены внутри `withContext(NonCancellable) { ... }`.
- **Не вводит автоматических лимитов по времени**: он игнорирует отмену, но если внутри использовать `withTimeout` и подобные механизмы, эти таймауты продолжают работать.
- **Используйте экономно**: только для критической, короткой и ограниченной по времени очистки.

#### Когда Использовать `NonCancellable`

Используйте `NonCancellable` **только** для критических операций очистки, когда:
- работа короткая и предсказуемо ограничена,
- пропуск очистки приведёт к утечкам ресурсов, повреждению состояния или нарушению инвариантов.

Примеры:
1. Закрытие ресурсов (файлы, сетевые соединения, дескрипторы БД)
2. Сохранение важного состояния перед завершением
3. Финализация/откат транзакций, которые нельзя оставить в неконсистентном состоянии
4. Отправка минимальной аналитики/аудита об отмене (если дёшево и важно)
5. Освобождение блокировок или семафоров

Не используйте для:
- обычной бизнес-логики,
- длительных операций,
- операций, которые по смыслу должны быть отменяемыми,
- оборачивания больших участков «на всякий случай».

#### Использование `NonCancellable` В Блоках `finally`

```kotlin
import kotlinx.coroutines.*

suspend fun demonstrateNonCancellable() = coroutineScope {
    val job = launch {
        try {
            println("Работаем...")
            delay(1000)
            println("Работа завершена")
        } finally {
            // С `NonCancellable` очистка может использовать suspend-функции
            withContext(NonCancellable) {
                println("Начало очистки...")
                delay(500) // Короткая допустимая задержка
                println("Очистка завершена")
            }
        }
    }

    delay(100)
    job.cancel()
    job.join()
}
```

**Почему нужно**: После отмены `Job` корутины находится в состоянии отмены, и обычные отменяемые suspend-функции выбросят `CancellationException`. `withContext(NonCancellable)` выполняет очистку в контексте, игнорирующем эту отмену, чтобы короткая критичная suspend-очистка могла завершиться.

#### Реальный Пример: Закрытие Ресурсов

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
            // В реальном коде используйте цикл, который может вызывать suspend-функции напрямую
        }
    } finally {
        // КРИТИЧНО: Должны закрыть файл даже если отменено
        withContext(NonCancellable) {
            println("Закрытие файла...")
            reader.close()
            println("Файл закрыт")
        }
    }
}

suspend fun demonstrateFileCleanup() {
    val job = CoroutineScope(Dispatchers.IO).launch {
        processFile("data.txt")
    }

    delay(250)
    job.cancel()
    job.join()
}
```

#### Реальный Пример: Сохранение Состояния

```kotlin
import kotlinx.coroutines.*

data class AppState(val unsavedChanges: List<String>)

class StateManager {
    private var state = AppState(emptyList())

    suspend fun saveState() {
        delay(200)
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
            withContext(NonCancellable) {
                println("Сохранение несохранённых изменений при отмене...")
                saveState()
                println("Сохранение завершено")
            }
        }
    }
}

suspend fun demonstrateStateSave() {
    val manager = StateManager()
    val job = CoroutineScope(Dispatchers.Default).launch {
        manager.doWork()
    }

    delay(350)
    println("Отмена...")
    job.cancelAndJoin()
    println("Job отменён и очистка завершена")
}
```

#### Реальный Пример: Коммит/откат Транзакции Базы Данных

```kotlin
import kotlinx.coroutines.*

class DatabaseTransaction {
    private val uncommittedChanges = mutableListOf<String>()

    suspend fun executeQuery(query: String) {
        delay(50)
        uncommittedChanges.add(query)
        println("Выполнено: $query")
    }

    suspend fun commit() {
        delay(100)
        println("Закоммичено ${uncommittedChanges.size} изменений")
        uncommittedChanges.clear()
    }

    suspend fun rollback() {
        delay(50)
        println("Откат ${uncommittedChanges.size} изменений")
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

        transaction.commit()
    } catch (e: CancellationException) {
        withContext(NonCancellable) {
            println("Транзакция отменена, откат...")
            transaction.rollback()
        }
        throw e
    } finally {
        withContext(NonCancellable) {
            println("Закрытие транзакции...")
            delay(50)
            println("Транзакция закрыта")
        }
    }
}

suspend fun demonstrateTransaction() {
    val job = CoroutineScope(Dispatchers.IO).launch {
        performTransaction()
    }

    delay(150)
    println("Отмена транзакции...")
    job.cancelAndJoin()
}
```

#### Реальный Пример: Аналитика При Отмене

```kotlin
import kotlinx.coroutines.*

object Analytics {
    suspend fun logEvent(event: String, properties: Map<String, Any>) {
        delay(100)
        println("Аналитика: $event - $properties")
    }
}

suspend fun longRunningTask(taskId: String) {
    val startTime = System.currentTimeMillis()

    try {
        println("Запуск задачи $taskId")
        delay(5000)
        println("Задача $taskId завершена")

        Analytics.logEvent("task_completed", mapOf("taskId" to taskId))
    } finally {
        val duration = System.currentTimeMillis() - startTime

        withContext(NonCancellable) {
            println("Логирование события отмены...")
            Analytics.logEvent(
                "task_cancelled",
                mapOf(
                    "taskId" to taskId,
                    "duration_ms" to duration,
                    "reason" to "user_cancellation"
                )
            )
            println("Аналитика отправлена")
        }
    }
}

suspend fun demonstrateAnalytics() {
    val job = CoroutineScope(Dispatchers.Default).launch {
        longRunningTask("task-123")
    }

    delay(1000)
    job.cancelAndJoin()
}
```

#### Риски Использования `NonCancellable`

1. Блокирование отмены слишком долго

2. Сокрытие багов (использование для бизнес-логики вместо исправления отменяемости)

3. Потенциальное истощение ресурсов при зависании операций без таймаутов

#### `NonCancellable` Не Предотвращает Отмену

`NonCancellable` не предотвращает отмену исходного `Job`; он позволяет suspend-функциям в своём контексте выполниться несмотря на отмену. Родительская корутина остаётся отменённой.

#### Лучшая Практика

- Использовать только для короткой, критичной очистки.
- При необходимости добавлять явные таймауты внутри `NonCancellable`.
- Для простой синхронной очистки использовать обычный блок `finally` без suspend-функций.

## Дополнительные Вопросы

1. Как `NonCancellable` взаимодействует с `CoroutineExceptionHandler`? Отличается ли обработка исключений внутри таких блоков?
2. Можно ли вкладывать несколько блоков `withContext(NonCancellable)`? Каковы последствия?
3. Как реализовать собственный элемент контекста, похожий на `NonCancellable`, но с ограничением по времени?
4. Что происходит, если запустить новую корутину внутри блока `NonCancellable`? Будет ли дочерняя корутина отменяемой?
5. Как использование `NonCancellable` влияет на принципы структурированной конкуренции?
6. Можно ли применять `NonCancellable` с операторами `Flow`? Когда это может быть полезно?
7. Как протестировать, что код очистки корректно использует `NonCancellable` в сложной иерархии корутин?

## Follow-ups

1. How does `NonCancellable` interact with `CoroutineExceptionHandler`? Are exceptions in `NonCancellable` blocks handled differently?
2. Can you nest multiple `withContext(NonCancellable)` blocks? What are the implications?
3. How would you implement a custom context element similar to `NonCancellable` but with a time budget?
4. What happens if you launch a new coroutine inside a `NonCancellable` block? Is the child coroutine cancellable?
5. How does `NonCancellable` affect structured concurrency principles? Does it violate them?
6. Can you use `NonCancellable` with `Flow` operators? What would be the use case?
7. How would you test that cleanup code properly uses `NonCancellable` in a complex coroutine hierarchy?

## Ссылки

- [[c-kotlin]]
- [[c-coroutines]]
- [Kotlin Coroutines Guide - Cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [NonCancellable API Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-non-cancellable/)
- [Coroutine `Context` Documentation](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [Roman Elizarov - Cancellation in Coroutines](https://medium.com/@elizarov/cancellation-in-coroutines-aa6b90163629)
- [Exception Handling in Coroutines](https://kotlinlang.org/docs/exception-handling.html)

## References

- [[c-kotlin]]
- [[c-coroutines]]
- [Kotlin Coroutines Guide - Cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [NonCancellable API Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-non-cancellable/)
- [Coroutine `Context` Documentation](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [Roman Elizarov - Cancellation in Coroutines](https://medium.com/@elizarov/cancellation-in-coroutines-aa6b90163629)
- [Exception Handling in Coroutines](https://kotlinlang.org/docs/exception-handling.html)

## Связанные Вопросы

- [[q-job-state-machine-transitions--kotlin--medium]]
- [[q-structured-concurrency-violations--kotlin--hard]]
- [[q-coroutine-memory-leak-detection--kotlin--hard]]
- [[q-testing-coroutine-timing-control--kotlin--medium]]
- [[q-deferred-async-patterns--kotlin--medium]]

## Related Questions

- [[q-job-state-machine-transitions--kotlin--medium]]
- [[q-structured-concurrency-violations--kotlin--hard]]
- [[q-coroutine-memory-leak-detection--kotlin--hard]]
- [[q-testing-coroutine-timing-control--kotlin--medium]]
- [[q-deferred-async-patterns--kotlin--medium]]

## Answer (EN)

#### What is `NonCancellable`?

`NonCancellable` is a special `CoroutineContext` element (a `Job`) that makes a block of code run in a context that ignores cancellation. It allows suspend functions inside that context to execute even when the surrounding coroutine has been cancelled.

```kotlin
import kotlinx.coroutines.*

public object NonCancellable : AbstractCoroutineContextElement(Job), Job {
    // Job that cannot be cancelled
    // All Job cancellation operations are ignored
}
```

Key characteristics:
- Job that ignores cancellation: `cancel()` on this `Job` has no effect; it never transitions to a cancelled state.
- Allows suspend functions in `finally`: Can safely call suspend functions for cleanup after cancellation inside `withContext(NonCancellable) { ... }`.
- Does not auto-enforce time limits: It ignores cancellation, but if you explicitly wrap work in `withTimeout` or similar inside it, those timeouts still apply.
- Use sparingly: Only for critical, short, and bounded cleanup.

#### When to Use `NonCancellable`

Use `NonCancellable` only for critical cleanup operations where:
- the work is short and bounded, and
- failing to run it would leave resources leaked, state corrupted, or invariants broken.

Examples:
1. Closing resources (files, network connections, database handles)
2. Saving essential state before shutdown
3. Rolling back or finalizing transactions that must not be left inconsistent
4. Sending minimal analytics/audit logs about cancellation (only if cheap and important)
5. Releasing locks or semaphores

Do NOT use for:
- regular business logic,
- long-running operations,
- operations that should be cancellable,
- large blocks "just in case".

#### Using `NonCancellable` in `finally` Blocks

```kotlin
import kotlinx.coroutines.*

suspend fun demonstrateNonCancellable() = coroutineScope {
    val job = launch {
        try {
            println("Working...")
            delay(1000)
            println("Work completed")
        } finally {
            withContext(NonCancellable) {
                println("Cleanup starting...")
                delay(500)
                println("Cleanup completed")
            }
        }
    }

    delay(100)
    job.cancel()
    job.join()
}
```

Why needed: After cancellation, the coroutine's `Job` is in a cancelled state. Normally, cancellable suspend functions will throw `CancellationException`. `withContext(NonCancellable)` runs cleanup in a context that ignores that cancellation so that short, critical suspend-based cleanup can complete.

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
            // In real code use a suspending-friendly loop instead of forEach with suspend
        }
    } finally {
        withContext(NonCancellable) {
            println("Closing file...")
            reader.close()
            println("File closed")
        }
    }
}

suspend fun demonstrateFileCleanup() {
    val job = CoroutineScope(Dispatchers.IO).launch {
        processFile("data.txt")
    }

    delay(250)
    job.cancel()
    job.join()
}
```

#### Real Example: Saving State

```kotlin
import kotlinx.coroutines.*

data class AppState(val unsavedChanges: List<String>)

class StateManager {
    private var state = AppState(emptyList())

    suspend fun saveState() {
        delay(200)
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

    delay(350)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Job cancelled and cleanup done")
}
```

#### Real Example: Database Transaction commit/rollback

```kotlin
import kotlinx.coroutines.*

class DatabaseTransaction {
    private val uncommittedChanges = mutableListOf<String>()

    suspend fun executeQuery(query: String) {
        delay(50)
        uncommittedChanges.add(query)
        println("Executed: $query")
    }

    suspend fun commit() {
        delay(100)
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

        transaction.commit()
    } catch (e: CancellationException) {
        withContext(NonCancellable) {
            println("Transaction cancelled, rolling back...")
            transaction.rollback()
        }
        throw e
    } finally {
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

    delay(150)
    println("Cancelling transaction...")
    job.cancelAndJoin()
}
```

#### Real Example: Analytics Event on Cancellation

```kotlin
import kotlinx.coroutines.*

object Analytics {
    suspend fun logEvent(event: String, properties: Map<String, Any>) {
        delay(100)
        println("Analytics: $event - $properties")
    }
}

suspend fun longRunningTask(taskId: String) {
    val startTime = System.currentTimeMillis()

    try {
        println("Starting task $taskId")
        delay(5000)
        println("Task $taskId completed")

        Analytics.logEvent("task_completed", mapOf("taskId" to taskId))
    } finally {
        val duration = System.currentTimeMillis() - startTime

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

    delay(1000)
    job.cancelAndJoin()
}
```

#### Risks of Using `NonCancellable`

1. Blocking cancellation for too long.
2. Hiding bugs by wrapping business logic instead of fixing cancellation.
3. Resource exhaustion if long or hanging operations run without additional timeouts.

#### `NonCancellable` Does not Prevent Cancellation

`NonCancellable` does not prevent cancellation of the original `Job`; it allows suspend functions in its context to run despite that cancellation.

#### Best Practices

- Use for short, critical cleanup only.
- Add explicit timeouts inside `NonCancellable` if cleanup might hang.
- For simple synchronous cleanup, rely on regular `finally` without suspend.
