---
id: kotlin-241
title: "What is a Job and its lifecycle in Kotlin coroutines? / Job и его жизненный цикл"
aliases: [Job Lifecycle, Job и его жизненный цикл]
topic: kotlin
difficulty: medium
original_language: en
language_tags: [en, ru]
question_kind: theory
status: draft
created: "2025-10-12"
updated: "2025-11-09"
tags: ["cancellation", "coroutines", "difficulty/medium", "job", "kotlin", "lifecycle"]
description: "A comprehensive guide to understanding Job and its lifecycle states in Kotlin coroutines, including parent-child relationships and cancellation mechanisms"
moc: moc-kotlin
related: [c-coroutines, c-kotlin]
subtopics: [coroutines, lifecycle]
---
# Вопрос (RU)

> Что такое `Job` и как устроен его жизненный цикл в корутинах Kotlin?

# Question (EN)

> What is a `Job` and its lifecycle in Kotlin coroutines?

## Ответ (RU)

Понимание интерфейса `Job` и его жизненного цикла является фундаментальным для эффективной работы с корутинами Kotlin. `Job` представляет собой отменяемую задачу с жизненным циклом, который заканчивается в одном из терминальных состояний (`COMPLETED` или `CANCELLED`). Это один из ключевых элементов `CoroutineContext` и основной строительный блок structured concurrency (структурированной конкуррентности). Какие существуют состояния `Job`, и как работают отношения родитель–потомок?

**Краткий ответ:** `Job` — это отменяемая сущность с жизненным циклом, который завершается в одном из двух терминальных состояний: успешное завершение (`COMPLETED`) или отмена (`CANCELLED`). Он управляет выполнением корутин, поддерживает иерархию родитель–потомок и распространение отмены в рамках structured concurrency.

Все детальные примеры и пояснения ниже (русская часть) соответствуют английским разделам по структуре и коду. См. также [[c-kotlin]] и [[c-coroutines]].

### Описание Проблемы

Понимание интерфейса `Job` и его жизненного цикла является фундаментальным для эффективной работы с корутинами Kotlin. `Job` представляет отменяемую задачу с жизненным циклом, который завершается её успешным завершением или отменой (включая завершение с ошибкой как отмену). Это один из ключевых элементов `CoroutineContext` и основа structured concurrency. Какие существуют состояния `Job`, и как работают отношения родитель–потомок?

### Решение

`Job` — это отменяемая сущность с жизненным циклом, который заканчивается в одном из терминальных состояний (`COMPLETED` или `CANCELLED`). Это основной строительный блок structured concurrency в корутинах Kotlin.

#### Состояния Job

Job проходит через несколько наблюдаемых состояний в течение своего жизненного цикла:

```kotlin
import kotlinx.coroutines.*

fun demonstrateJobStates() = runBlocking {
    // Состояние 1: NEW (только для ленивых корутин до start())
    val lazyJob = launch(start = CoroutineStart.LAZY) {
        println("Ленивая задача запущена")
        delay(1000)
    }

    println("Ленивая задача: isActive=${lazyJob.isActive}, " +
            "isCompleted=${lazyJob.isCompleted}, " +
            "isCancelled=${lazyJob.isCancelled}") // false, false, false

    // Состояние 2: ACTIVE (после запуска)
    lazyJob.start()
    println("После start(): isActive=${lazyJob.isActive}, " +
            "isCompleted=${lazyJob.isCompleted}") // true, false (пока выполняется)

    // Состояние 3: COMPLETING (тело завершилось, ждём потомков)
    val parentJob = launch {
        val childJob = launch {
            delay(2000)
            println("Потомок завершён")
        }
        println("Тело родителя завершено")
        // Родитель переходит во внутреннее состояние COMPLETING, ожидая childJob
    }

    delay(100)
    println("Родитель во время работы потомка: isActive=${parentJob.isActive}, " +
            "isCompleted=${parentJob.isCompleted}") // обычно true, false

    // Состояние 4: COMPLETED
    parentJob.join()
    println("Родитель COMPLETED: isActive=${parentJob.isActive}, " +
            "isCompleted=${parentJob.isCompleted}") // false, true

    // Состояния CANCELLING/CANCELLED (при отмене)
    val cancellingJob = launch {
        try {
            delay(5000)
        } finally {
            println("Очистка в finally")
            // По умолчанию очистка тоже может быть отменена; для критичных секций используйте NonCancellable
            delay(500)
            println("Очистка завершена")
        }
    }

    delay(100)
    cancellingJob.cancel() // переходит в CANCELLING, затем в CANCELLED
    println("После cancel(): isActive=${cancellingJob.isActive}, " +
            "isCancelled=${cancellingJob.isCancelled}")

    cancellingJob.join()
    println("Итоговое состояние: isCompleted=${cancellingJob.isCompleted}") // true
}
```

#### Полная Диаграмма Состояний (Концептуально)

```kotlin
import kotlinx.coroutines.*

/**
 * Упрощённые переходы состояний Job (по реализации kotlinx.coroutines):
 *
 * NEW (ленивая или ещё не запущенная)
 *   |
 *   v (start/join и запуск)
 * ACTIVE
 *   |
 *   v (тело завершилось, ждём потомков)
 * COMPLETING
 *   |
 *   v (все потомки завершены успешно)
 * COMPLETED (терминальное успешное)
 *
 * Пока Job не в терминальном состоянии, можно запросить отмену:
 *   NEW/ACTIVE/COMPLETING --cancel--> CANCELLING
 *   CANCELLING --после обработчиков/потомков--> CANCELLED (терминальное отменённое)
 *
 * COMPLETED и CANCELLED — терминальные состояния, переходов из них нет.
 */

data class JobState(
    val isNew: Boolean,
    val isActive: Boolean,
    val isCompleting: Boolean,
    val isCompleted: Boolean,
    val isCancelled: Boolean
)

fun Job.getDetailedState(): String {
    // Важно: публичный API не даёт прямого доступа к COMPLETING/CANCELLING, это лишь грубая классификация.
    return when {
        !isActive && !isCompleted && !isCancelled -> "NEW"
        isActive && !isCompleted && !isCancelled -> "ACTIVE (возможно внутреннее COMPLETING)"
        !isActive && isCompleted && !isCancelled -> "COMPLETED"
        !isActive && isCancelled -> "CANCELLED (до этого был CANCELLING)"
        else -> "UNKNOWN"
    }
}
```

#### Создание И Управление Job

```kotlin
import kotlinx.coroutines.*

fun jobCreationExamples() = runBlocking {
    // 1. Job из coroutine builder (предпочтительно)
    val job1 = launch {
        delay(1000)
        println("Job из launch")
    }

    // 2. Отдельный Job как родитель (нуждается в явном управлении жизненным циклом)
    val job2 = Job()
    val childOfJob2 = launch(job2) {
        delay(1000)
        println("Задача с явным родителем")
    }

    childOfJob2.join()
    job2.complete() // или job2.cancel()

    // 3. Job из CoroutineScope
    val scope = CoroutineScope(Dispatchers.Default)
    val job3 = scope.launch {
        delay(1000)
        println("Job из scope")
    }

    // 4. Получение текущего Job
    val job4 = launch {
        val currentJob = coroutineContext[Job]
        println("Текущий job: $currentJob")
    }

    joinAll(job1, job3, job4)
    scope.cancel()
}
```

#### Отношения Родитель–Потомок

```kotlin
import kotlinx.coroutines.*

fun parentChildRelationships() = runBlocking {
    println("=== Родитель–Потомок ===")

    // 1. Автоматические связи в одном scope
    val parent = launch {
        println("Родитель стартовал")

        val child1 = launch {
            delay(1000)
            println("Потомок 1 завершён")
        }

        val child2 = launch {
            delay(1500)
            println("Потомок 2 завершён")
        }

        println("Тело родителя завершено, но он ждёт потомков")
    }

    delay(500)
    println("Состояние родителя: ${parent.isActive}, ${parent.isCompleted}")

    parent.join() // Ждёт родителя и всех его потомков
    println("Родитель и все потомки завершены")

    // 2. Ручное задание родителя через standalone Job
    val manualParent = Job()

    launch(manualParent) {
        delay(500)
        println("Ручной потомок 1")
    }

    launch(manualParent) {
        delay(1000)
        println("Ручной потомок 2")
    }

    manualParent.children.forEach { child ->
        println("Потомок: $child")
    }

    // Дождаться потомков и явно завершить родителя
    manualParent.children.forEach { it.join() }
    manualParent.complete()
    manualParent.join()
}
```

#### Распространение Отмены

```kotlin
import kotlinx.coroutines.*

fun cancellationPropagation() = runBlocking {
    println("=== Распространение отмены ===")

    // Отмена родителя отменяет всех потомков
    val parent = launch {
        val child1 = launch {
            try {
                delay(2000)
                println("Потомок 1 завершён")
            } catch (e: CancellationException) {
                println("Потомок 1 отменён")
            }
        }

        val child2 = launch {
            try {
                delay(3000)
                println("Потомок 2 завершён")
            } catch (e: CancellationException) {
                println("Потомок 2 отменён")
            }
        }

        delay(5000)
    }

    delay(500)
    parent.cancel()
    parent.join()

    println("\n=== Ошибка потомка отменяет родителя (обычный Job) ===")

    val parent2 = launch {
        launch {
            delay(500)
            throw RuntimeException("Потомок упал!")
        }

        launch {
            try {
                delay(2000)
                println("Соседний потомок завершился")
            } catch (e: CancellationException) {
                println("Соседний потомок отменён из-за отмены родителя")
            }
        }

        try {
            delay(3000)
        } catch (e: CancellationException) {
            println("Родитель отменён из-за ошибки потомка")
        }
    }

    parent2.join()

    println("\n=== SupervisorJob: ошибка потомка не отменяет братьев ===")

    val supervisor = SupervisorJob()
    val scope = CoroutineScope(supervisor)

    val failingChild = scope.launch {
        delay(500)
        throw RuntimeException("Ошибка под SupervisorJob")
    }

    val sibling = scope.launch {
        try {
            delay(2000)
            println("Соседний потомок выжил под SupervisorJob")
        } catch (e: CancellationException) {
            println("Соседний потомок отменён")
        }
    }

    joinAll(failingChild, sibling)
    scope.cancel()
}
```

#### Завершение Job И Ожидание

```kotlin
import kotlinx.coroutines.*

fun jobCompletionExamples() = runBlocking {
    // 1. join() — приостанавливается до завершения
    val job1 = launch {
        delay(1000)
        println("Job 1 завершён")
    }
    job1.join()

    // 2. joinAll() — ожидание нескольких Job
    val jobs = List(5) { index ->
        launch {
            delay(1000L * index)
            println("Job $index завершён")
        }
    }
    joinAll(*jobs.toTypedArray())

    // 3. Job.complete() для standalone Job
    val manualJob = Job()
    val child = launch(manualJob) {
        delay(500)
        println("Потомок завершён")
    }
    child.join()
    manualJob.complete()
    manualJob.join()

    // 4. Job.completeExceptionally() — завершение с ошибкой
    val failingJob = Job()
    launch(failingJob) {
        try {
            delay(1000)
        } catch (e: CancellationException) {
            println("Отменено из-за завершения с исключением")
        }
    }
    failingJob.completeExceptionally(RuntimeException("Ошибка"))

    // 5. invokeOnCompletion — колбэк по завершении
    val job2 = launch {
        delay(1000)
        println("Работа Job 2 выполнена")
    }

    job2.invokeOnCompletion { cause ->
        when (cause) {
            null -> println("Job завершён успешно")
            is CancellationException -> println("Job был отменён")
            else -> println("Job завершён с ошибкой $cause")
        }
    }

    job2.join()
}
```

#### Иерархия Job И Инспекция

```kotlin
import kotlinx.coroutines.*

fun jobHierarchyInspection() = runBlocking {
    val grandparent = launch {
        println("Grandparent job: ${coroutineContext[Job]}")

        val parent = launch {
            println("Parent job: ${coroutineContext[Job]}")
            println("Родитель Parent: ${coroutineContext[Job]?.parent}")

            val child = launch {
                println("Child job: ${coroutineContext[Job]}")
                println("Родитель Child: ${coroutineContext[Job]?.parent}")
                delay(1000)
            }

            child.join()
        }

        delay(100)
        val children = coroutineContext[Job]?.children?.toList()
        println("У Grandparent ${children?.size} прямых потомков")

        parent.join()
    }

    grandparent.join()
}
```

#### Практические Паттерны Работы С Job

```kotlin
import kotlinx.coroutines.*

// Паттерн 1: joinOrTimeout — ожидание Job с таймаутом
suspend fun Job.joinOrTimeout(timeoutMillis: Long): Boolean {
    return try {
        withTimeout(timeoutMillis) {
            join()
        }
        true
    } catch (e: TimeoutCancellationException) {
        false
    }
}

// Паттерн 2: Отменяемый ресурс (scope привязан к lifecycle ресурса)
class CancellableResource {
    private val job = Job()
    private val scope = CoroutineScope(Dispatchers.Default + job)

    fun doWork() {
        scope.launch {
            while (isActive) {
                println("Работа...")
                delay(500)
            }
        }
    }

    fun cancel() {
        job.cancel()
    }
}

// Паттерн 3: Job как менеджер жизненного цикла (упрощённый ViewModel-подход)
class SimpleViewModel {
    private val viewModelJob = SupervisorJob()
    private val viewModelScope = CoroutineScope(Dispatchers.Default + viewModelJob)

    fun loadData() {
        viewModelScope.launch {
            // Загрузка данных
        }
    }

    fun onCleared() {
        viewModelJob.cancel()
    }
}

fun demonstrateJobPatterns() = runBlocking {
    val resource = CancellableResource()
    resource.doWork()
    delay(2000)
    resource.cancel()

    val longRunningJob = launch {
        delay(5000)
    }

    val completed = longRunningJob.joinOrTimeout(1000)
    println("Job успел завершиться: $completed")
    longRunningJob.cancel()
}
```

#### Исключения И Обработка Ошибок В Job

```kotlin
import kotlinx.coroutines.*

fun jobExceptionHandling() = runBlocking {
    // 1. Исключение внутри Job приводит к его отмене
    val failingJob = launch {
        throw RuntimeException("Job упал!")
    }

    failingJob.invokeOnCompletion { cause ->
        println("FailingJob завершён с причиной: $cause")
    }

    failingJob.join()
    println("FailingJob isCancelled=${failingJob.isCancelled}")

    // 2. CancellationException обычно означает нормальную отмену
    val parent = launch {
        val child = launch {
            throw CancellationException("Явная отмена")
        }

        child.join()
        println("Родитель пережил отмену потомка")
    }

    parent.join()

    // 3. Другие исключения отменяют обычного родителя, но не SupervisorJob
    val supervisorParent = CoroutineScope(SupervisorJob()).launch {
        launch {
            throw RuntimeException("Ошибка под SupervisorJob")
        }

        launch {
            try {
                delay(500)
                println("Соседний потомок выжил под SupervisorJob")
            } catch (e: CancellationException) {
                println("Соседний потомок отменён")
            }
        }
    }

    supervisorParent.join()

    // 4. invokeOnCompletion различает причины завершения
    val job = launch {
        throw RuntimeException("Ошибка")
    }

    job.invokeOnCompletion { cause ->
        when (cause) {
            null -> println("Нормальное завершение")
            is CancellationException -> println("Отмена")
            else -> println("Завершено с исключением: $cause")
        }
    }

    job.join()
}
```

#### Тестирование Жизненного Цикла Job (схема)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class JobLifecycleTest {
    @Test
    fun testJobStates() = runTest {
        val job = launch(start = CoroutineStart.LAZY) {
            delay(1000)
        }

        assertFalse(job.isActive)
        assertFalse(job.isCompleted)

        job.start()
        assertTrue(job.isActive)
        assertFalse(job.isCompleted)

        job.join()
        assertFalse(job.isActive)
        assertTrue(job.isCompleted)
    }

    @Test
    fun testCancellation() = runTest {
        val job = launch {
            try {
                delay(10_000)
            } finally {
                println("Очистка")
            }
        }

        advanceTimeBy(100)
        job.cancel()

        assertTrue(job.isCancelled)
        job.join()
        assertTrue(job.isCompleted)
    }

    @Test
    fun testParentChildCancellation() = runTest {
        val parent = launch {
            launch {
                delay(10_000)
            }
        }

        advanceTimeBy(100)
        parent.cancel()
        parent.join()

        assertTrue(parent.isCancelled)
    }
}
```

### Лучшие Практики

1. Не создавайте лишние standalone `Job` без необходимости
   ```kotlin
   // Плохо: отдельный Job без явного управления
   val job = Job()
   launch(job) { }

   // Хорошо: пусть builder создаёт и управляет Job
   val job = launch { }
   ```

2. Используйте `invokeOnCompletion` для очистки
   ```kotlin
   val job = launch {
       // работа
   }

   job.invokeOnCompletion { cause ->
       // очистка независимо от результата
   }
   ```

3. Проверяйте `isActive` в долгих циклах
   ```kotlin
   launch {
       while (isActive) {
           // отменяемая работа
           doWork()
       }
   }
   ```

4. Применяйте `SupervisorJob`, когда падение одного ребёнка не должно гасить остальных
   ```kotlin
   val scope = CoroutineScope(SupervisorJob())
   ```

5. Не "глотайте" `CancellationException`
   ```kotlin
   // Плохо
   try {
       delay(1000)
   } catch (e: Exception) {
       // перехватывает и CancellationException
   }

   // Хорошо
   try {
       delay(1000)
   } catch (e: CancellationException) {
       throw e
   } catch (e: Exception) {
       // обработать другие ошибки
   }
   ```

### Распространённые Ошибки

1. Игнорирование состояния COMPLETING
   ```kotlin
   val job = launch {
       launch { delay(5000) }
       println("Родительское тело завершено") // Job ещё не COMPLETED, ждёт потомка
   }
   ```

2. Неожиданный выход без ожидания потомков
   ```kotlin
   // Плохо
   fun loadData() = runBlocking {
       launch { /* работа */ }
       // Функция возвращает результат до завершения потомка
   }

   // Хорошо
   suspend fun loadData() = coroutineScope {
       launch { /* работа */ }
       // Возврат только после завершения всех детей
   }
   ```

3. Создание `Job` без работы и без завершения
   ```kotlin
   val job = Job()
   // Он не завершится сам по себе — нужно явно complete()/cancel() и/или управлять потомками
   ```

### Крайние Случаи

```kotlin
import kotlinx.coroutines.*

fun jobEdgeCases() = runBlocking {
    // 1. Пустая корутина завершится сразу после выполнения тела
    val emptyJob = launch { }
    emptyJob.join()

    // 2. Отмена ленивой корутины до запуска
    val job = launch(start = CoroutineStart.LAZY) {
        println("Не будет выполнено")
    }
    job.cancel()

    // 3. Несколько invokeOnCompletion
    val job2 = launch { delay(100) }
    job2.invokeOnCompletion { println("Первый") }
    job2.invokeOnCompletion { println("Второй") }

    // 4. join() для уже завершённого Job возвращается сразу
    val job3 = launch { delay(100) }
    job3.join()
    job3.join()

    // 5. cancel() для завершённого Job не меняет состояние
    val job4 = launch { delay(100) }
    job4.join()
    job4.cancel()
}
```

---

## Answer (EN)

Understanding the `Job` interface and its lifecycle is fundamental to working effectively with Kotlin coroutines. A `Job` represents a cancellable task with a lifecycle, and it's one of the key elements of `CoroutineContext` and structured concurrency. What are the different states a `Job` can be in, and how do parent–child relationships work?

A `Job` is a cancellable thing with a lifecycle that always ends in one of two terminal states: successful completion (`COMPLETED`) or cancellation (`CANCELLED`). It's a core component of structured concurrency in Kotlin coroutines. See also [[c-kotlin]] and [[c-coroutines]].

### Problem Statement

Understanding the `Job` interface and its lifecycle is fundamental to working effectively with Kotlin coroutines. A `Job` represents a cancellable task with a lifecycle, and it's one of the key elements of `CoroutineContext`. What are the different states a `Job` can be in, and how do parent–child relationships work?

### Solution

A `Job` is a cancellable thing with a lifecycle that culminates in a terminal state: either `COMPLETED` (successful) or `CANCELLED` (cancelled/failed). It's a core component of structured concurrency in Kotlin coroutines.

#### Job States

A `Job` goes through several observable states during its lifecycle:

```kotlin
import kotlinx.coroutines.*

fun demonstrateJobStates() = runBlocking {
    // State 1: NEW (only for lazy coroutines before start)
    val lazyJob = launch(start = CoroutineStart.LAZY) {
        println("Lazy job started")
        delay(1000)
    }

    println("Lazy job state: isActive=${lazyJob.isActive}, " +
            "isCompleted=${lazyJob.isCompleted}, " +
            "isCancelled=${lazyJob.isCancelled}") // false, false, false

    // State 2: ACTIVE (after start)
    lazyJob.start()
    println("After start: isActive=${lazyJob.isActive}, " +
            "isCompleted=${lazyJob.isCompleted}") // true, false (or briefly while running)

    // State 3: COMPLETING (body finished, waiting for children)
    val parentJob = launch {
        val childJob = launch {
            delay(2000)
            println("Child completed")
        }
        println("Parent body finished")
        // Parent will move to COMPLETING while waiting for childJob
    }

    delay(100)
    println("Parent during children: isActive=${parentJob.isActive}, " +
            "isCompleted=${parentJob.isCompleted}") // typically true, false (may be in COMPLETING)

    // State 4: COMPLETED
    parentJob.join()
    println("Parent completed: isActive=${parentJob.isActive}, " +
            "isCompleted=${parentJob.isCompleted}") // false, true

    // State 5: CANCELLING (cancelling but not yet fully completed)
    val cancellingJob = launch {
        try {
            delay(5000)
        } finally {
            println("Cleanup in finally")
            // By default cleanup is cancellable; use NonCancellable if needed
            delay(500)
            println("Cleanup complete")
        }
    }

    delay(100)
    cancellingJob.cancel() // moves to CANCELLING, then to CANCELLED when done
    println("After cancel request: isActive=${cancellingJob.isActive}, " +
            "isCancelled=${cancellingJob.isCancelled}")

    // State 6: CANCELLED (terminal)
    cancellingJob.join()
    println("Fully cancelled: isCompleted=${cancellingJob.isCompleted}") // true
}
```

#### Complete State Diagram (Conceptual)

```kotlin
import kotlinx.coroutines.*

/**
 * Job State Transitions (simplified view based on kotlinx.coroutines implementation):
 *
 * NEW (lazy or not-started)
 *   |
 *   v (start/join/await start)
 * ACTIVE
 *   |
 *   v (body completes, waiting for children if any)
 * COMPLETING
 *   |
 *   v (all children complete successfully)
 * COMPLETED (terminal, successful)
 *
 * At any time before reaching a terminal state, cancellation can be requested:
 *   ACTIVE/COMPLETING/NEW --cancel--> CANCELLING
 *   CANCELLING --after handlers/children--> CANCELLED (terminal, cancelled)
 *
 * Once in COMPLETED or CANCELLED, the Job is terminal; no further transitions occur.
 */

data class JobState(
    val isNew: Boolean,
    val isActive: Boolean,
    val isCompleting: Boolean,
    val isCompleted: Boolean,
    val isCancelled: Boolean
)

fun Job.getDetailedState(): String {
    // Note: Job does not expose COMPLETING/CANCELLING as public flags; this is heuristic.
    return when {
        !isActive && !isCompleted && !isCancelled -> "NEW"
        isActive && !isCompleted && !isCancelled -> "ACTIVE (possibly COMPLETING internally)"
        !isActive && isCompleted && !isCancelled -> "COMPLETED"
        !isActive && isCancelled -> "CANCELLED (or was CANCELLING before handlers finished)"
        else -> "UNKNOWN"
    }
}
```

#### Creating and Managing Jobs

```kotlin
import kotlinx.coroutines.*

fun jobCreationExamples() = runBlocking {
    // 1. Job from coroutine builder (preferred)
    val job1 = launch {
        delay(1000)
        println("Job from launch")
    }

    // 2. Standalone Job as parent (requires explicit lifecycle management)
    val job2 = Job()
    val childOfJob2 = launch(job2) {
        delay(1000)
        println("Job with explicit parent")
    }

    // You must complete or cancel such a Job when appropriate:
    childOfJob2.join()
    job2.complete() // or job2.cancel()

    // 3. Job from CoroutineScope
    val scope = CoroutineScope(Dispatchers.Default)
    val job3 = scope.launch {
        delay(1000)
        println("Job from scope")
    }

    // 4. Getting current Job
    val job4 = launch {
        val currentJob = coroutineContext[Job]
        println("Current job: $currentJob")
    }

    // Wait for all
    joinAll(job1, job3, job4)
    scope.cancel()
}
```

#### Parent-Child Relationships

```kotlin
import kotlinx.coroutines.*

fun parentChildRelationships() = runBlocking {
    println("=== Parent-Child Relationships ===")

    // 1. Automatic parent-child relationship within the same scope
    val parent = launch {
        println("Parent started")

        val child1 = launch {
            delay(1000)
            println("Child 1 completed")
        }

        val child2 = launch {
            delay(1500)
            println("Child 2 completed")
        }

        println("Parent body finished, but will not complete until children complete")
    }

    delay(500)
    println("Parent state: ${parent.isActive}, ${parent.isCompleted}")

    parent.join() // Waits for parent AND all its children
    println("Parent and all children completed")

    // 2. Manual parent specification using a standalone Job
    val manualParent = Job()

    launch(manualParent) {
        delay(500)
        println("Manual child 1")
    }

    launch(manualParent) {
        delay(1000)
        println("Manual child 2")
    }

    manualParent.children.forEach { child ->
        println("Child: $child")
    }

    // Wait for children and then complete the parent explicitly
    manualParent.children.forEach { it.join() }
    manualParent.complete()
    manualParent.join()
}
```

#### Cancellation Propagation

```kotlin
import kotlinx.coroutines.*

fun cancellationPropagation() = runBlocking {
    println("=== Cancellation Propagation ===")

    // Parent cancellation cancels all children
    val parent = launch {
        val child1 = launch {
            try {
                delay(2000)
                println("Child 1 completed")
            } catch (e: CancellationException) {
                println("Child 1 cancelled")
            }
        }

        val child2 = launch {
            try {
                delay(3000)
                println("Child 2 completed")
            } catch (e: CancellationException) {
                println("Child 2 cancelled")
            }
        }

        delay(5000)
    }

    delay(500)
    parent.cancel() // Cancels parent and all its children
    parent.join()

    println("\n=== Child Failure Cancels Parent (regular Job) ===")

    // With a regular parent Job, unhandled child exception cancels parent and siblings
    val parent2 = launch {
        launch {
            delay(500)
            throw RuntimeException("Child failed!")
        }

        launch {
            try {
                delay(2000)
                println("Sibling completed")
            } catch (e: CancellationException) {
                println("Sibling cancelled due to parent cancellation")
            }
        }

        try {
            delay(3000)
        } catch (e: CancellationException) {
            println("Parent cancelled due to child failure")
        }
    }

    parent2.join()

    println("\n=== SupervisorJob: child failure does NOT cancel siblings ===")

    val supervisor = SupervisorJob()
    val scope = CoroutineScope(supervisor)

    val failingChild = scope.launch {
        delay(500)
        throw RuntimeException("Child failed under supervisor")
    }

    val sibling = scope.launch {
        try {
            delay(2000)
            println("Sibling completed under supervisor")
        } catch (e: CancellationException) {
            println("Sibling cancelled")
        }
    }

    joinAll(failingChild, sibling)
    scope.cancel()
}
```

#### Job Completion and Waiting

```kotlin
import kotlinx.coroutines.*

fun jobCompletionExamples() = runBlocking {
    // 1. join() - suspends until completion
    val job1 = launch {
        delay(1000)
        println("Job 1 completed")
    }
    job1.join() // Suspends until job1 completes

    // 2. joinAll() - wait for multiple jobs
    val jobs = List(5) { index ->
        launch {
            delay(1000L * index)
            println("Job $index completed")
        }
    }
    joinAll(*jobs.toTypedArray())

    // 3. Job.complete() - manual completion of a standalone Job
    val manualJob = Job()
    val child = launch(manualJob) {
        delay(500)
        println("Child completed")
    }
    child.join()
    manualJob.complete() // No new children can be attached; moves to completed
    manualJob.join()

    // 4. Job.completeExceptionally() - complete with exception
    val failingJob = Job()
    launch(failingJob) {
        try {
            delay(1000)
        } catch (e: CancellationException) {
            println("Cancelled due to exceptional completion")
        }
    }
    failingJob.completeExceptionally(RuntimeException("Failed"))

    // 5. invokeOnCompletion - callback on completion
    val job2 = launch {
        delay(1000)
        println("Job 2 work done")
    }

    job2.invokeOnCompletion { cause ->
        when (cause) {
            null -> println("Job completed successfully")
            is CancellationException -> println("Job was cancelled")
            else -> println("Job failed with $cause")
        }
    }

    job2.join()
}
```

#### Job Hierarchy and Inspection

```kotlin
import kotlinx.coroutines.*

fun jobHierarchyInspection() = runBlocking {
    val grandparent = launch {
        println("Grandparent job: ${coroutineContext[Job]}")

        val parent = launch {
            println("Parent job: ${coroutineContext[Job]}")
            println("Parent's parent: ${coroutineContext[Job]?.parent}")

            val child = launch {
                println("Child job: ${coroutineContext[Job]}")
                println("Child's parent: ${coroutineContext[Job]?.parent}")
                delay(1000)
            }

            child.join()
        }

        delay(100)

        val children = coroutineContext[Job]?.children?.toList()
        println("Grandparent has ${children?.size} direct children")

        parent.join()
    }

    grandparent.join()
}
```

#### Practical Job Patterns

```kotlin
import kotlinx.coroutines.*

// Pattern 1: Joining with timeout using existing APIs
suspend fun Job.joinOrTimeout(timeoutMillis: Long): Boolean {
    return try {
        withTimeout(timeoutMillis) {
            join()
        }
        true
    } catch (e: TimeoutCancellationException) {
        false
    }
}

// Pattern 2: Cancellable Resource (scope bound to resource lifecycle)
class CancellableResource {
    private val job = Job()
    private val scope = CoroutineScope(Dispatchers.Default + job)

    fun doWork() {
        scope.launch {
            while (isActive) {
                println("Working...")
                delay(500)
            }
        }
    }

    fun cancel() {
        job.cancel()
    }
}

// Pattern 3: Job as lifecycle manager (simplified ViewModel-style example)
class SimpleViewModel {
    private val viewModelJob = SupervisorJob()
    private val viewModelScope = CoroutineScope(Dispatchers.Default + viewModelJob)

    fun loadData() {
        viewModelScope.launch {
            // Load data
        }
    }

    fun onCleared() {
        viewModelJob.cancel()
    }
}

fun demonstrateJobPatterns() = runBlocking {
    // Using CancellableResource
    val resource = CancellableResource()
    resource.doWork()
    delay(2000)
    resource.cancel()

    // Using joinOrTimeout
    val longRunningJob = launch {
        delay(5000)
    }

    val completed = longRunningJob.joinOrTimeout(1000)
    println("Job completed in time: $completed")
    longRunningJob.cancel()
}
```

#### Job Exceptions and Error Handling

```kotlin
import kotlinx.coroutines.*

fun jobExceptionHandling() = runBlocking {
    // 1. Exception in job cancels it
    val failingJob = launch {
        throw RuntimeException("Job failed!")
    }

    failingJob.invokeOnCompletion { cause ->
        println("Failing job completed with cause: $cause")
    }

    failingJob.join()
    println("Failing job cancelled: ${failingJob.isCancelled}")

    // 2. CancellationException typically signals normal cancellation
    val parent = launch {
        val child = launch {
            throw CancellationException("Explicit cancellation")
        }

        child.join()
        println("Parent survived child cancellation")
    }

    parent.join()

    // 3. Other exceptions in child cancel a regular parent, but not SupervisorJob
    val supervisorParent = CoroutineScope(SupervisorJob()).launch {
        launch {
            throw RuntimeException("This fails but does not cancel siblings due to SupervisorJob")
        }

        launch {
            try {
                delay(500)
                println("Sibling survived under SupervisorJob")
            } catch (e: CancellationException) {
                println("Sibling cancelled")
            }
        }
    }

    supervisorParent.join()

    // 4. invokeOnCompletion distinguishes exceptions
    val job = launch {
        throw RuntimeException("Failed")
    }

    job.invokeOnCompletion { cause ->
        when (cause) {
            null -> println("Normal completion")
            is CancellationException -> println("Cancelled")
            else -> println("Failed with exception: $cause")
        }
    }

    job.join()
}
```

#### Testing Job Lifecycle (outline)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class JobLifecycleTest {
    @Test
    fun testJobStates() = runTest {
        val job = launch(start = CoroutineStart.LAZY) {
            delay(1000)
        }

        // NEW state
        assertFalse(job.isActive)
        assertFalse(job.isCompleted)

        // ACTIVE state
        job.start()
        assertTrue(job.isActive)
        assertFalse(job.isCompleted)

        // COMPLETED state
        job.join()
        assertFalse(job.isActive)
        assertTrue(job.isCompleted)
    }

    @Test
    fun testCancellation() = runTest {
        val job = launch {
            try {
                delay(10_000)
            } finally {
                println("Cleanup")
            }
        }

        advanceTimeBy(100)
        job.cancel()

        assertTrue(job.isCancelled)
        job.join()
        assertTrue(job.isCompleted)
    }

    @Test
    fun testParentChildCancellation() = runTest {
        val parent = launch {
            launch {
                delay(10_000)
            }
        }

        advanceTimeBy(100)
        parent.cancel()
        parent.join()

        assertTrue(parent.isCancelled)
    }
}
```

### Best Practices

1. Don't create unnecessary standalone `Job`s
   ```kotlin
   // Bad: unmanaged standalone Job
   val job = Job()
   launch(job) { }

   // Good - let coroutine builder create and manage the Job
   val job = launch { }
   ```

2. Use `invokeOnCompletion` for cleanup
   ```kotlin
   val job = launch {
       // work
   }

   job.invokeOnCompletion { cause ->
       // cleanup regardless of success or failure
   }
   ```

3. Check `isActive` in long-running loops
   ```kotlin
   launch {
       while (isActive) {
           // work that can be cancelled
           doWork()
       }
   }
   ```

4. Use `SupervisorJob` when appropriate
   ```kotlin
   val scope = CoroutineScope(SupervisorJob())
   // Children don't cancel each other on failure
   ```

5. Don't swallow `CancellationException`
   ```kotlin
   // Bad
   try {
       delay(1000)
   } catch (e: Exception) {
       // This also catches CancellationException!
   }

   // Good
   try {
       delay(1000)
   } catch (e: CancellationException) {
       throw e // Re-throw to respect cancellation
   } catch (e: Exception) {
       // Handle other exceptions
   }
   ```

### Common Pitfalls

1. Forgetting about COMPLETING state
   ```kotlin
   val job = launch {
       launch { delay(5000) }
       println("Parent finished body") // Job is not COMPLETED yet, it's waiting for child
   }
   ```

2. Not waiting for children
   ```kotlin
   // Bad
   fun loadData() = runBlocking {
       launch { /* child work */ }
       // Returns before child completes!
   }

   // Good
   suspend fun loadData() = coroutineScope {
       launch { /* child work */ }
       // Suspends until all children complete
   }
   ```

3. Creating `Job` without attaching work or completing it
   ```kotlin
   val job = Job()
   // It will not complete until manually completed/cancelled
   // or until all its child coroutines finish and you call complete().
   ```

### Edge Cases

```kotlin
import kotlinx.coroutines.*

fun jobEdgeCases() = runBlocking {
    // 1. Empty job completes when its body finishes
    val emptyJob = launch { }
    emptyJob.join() // Returns immediately after body

    // 2. Cancelled job before start
    val job = launch(start = CoroutineStart.LAZY) {
        println("Never executed")
    }
    job.cancel()
    // job is cancelled without ever becoming active

    // 3. Multiple invokeOnCompletion
    val job2 = launch { delay(100) }
    job2.invokeOnCompletion { println("First") }
    job2.invokeOnCompletion { println("Second") }
    // Both are called

    // 4. Join on completed job
    val job3 = launch { delay(100) }
    job3.join()
    job3.join() // Returns immediately

    // 5. Cancel completed job
    val job4 = launch { delay(100) }
    job4.join()
    job4.cancel() // No effect on state
}
```

---

## Follow-ups (RU)

1. Чем `SupervisorJob` отличается от обычного `Job` в контексте обработки сбоев потомков?
2. Что происходит с `Job`, если его родитель отменяется, пока он находится в состоянии `COMPLETING`?
3. Как предотвратить отмену корутины во время критических операций очистки?
4. В чём разница между `Job.cancel()` и `Job.cancelAndJoin()`?
5. Как соотносятся `Job` и `Deferred`?
6. Может ли `Job` перейти из состояния `CANCELLED` обратно в `ACTIVE`?
7. Как `NonCancellable`-контекст влияет на жизненный цикл `Job`?
8. Каковы последствия использования `Job()` как родителя по сравнению с использованием `coroutineScope` для организации иерархии?

## Follow-ups (EN)

1. How does `SupervisorJob` differ from a regular `Job` in terms of child failure handling?
2. What happens to a `Job` when its parent is cancelled while it's in the `COMPLETING` state?
3. How can you prevent a coroutine from being cancelled during critical cleanup operations?
4. What's the difference between `Job.cancel()` and `Job.cancelAndJoin()`?
5. How do `Job` and `Deferred` relate to each other?
6. Can a `Job` transition from `CANCELLED` back to `ACTIVE`?
7. How does `NonCancellable` context affect `Job` lifecycle?
8. What's the impact of using `Job()` as a parent vs using `coroutineScope` for parent-child relationships?

## References

- [Kotlin Coroutines Guide - Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [Job - kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-job/)
- [Roman Elizarov - Structured Concurrency](https://medium.com/@elizarov/structured-concurrency-722d765aa952)
- [Coroutines Guide - Cancellation and Timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html)

## Related Questions

- [[q-coroutine-supervisorjob-use-cases--kotlin--medium]]
- [[q-coroutine-context-elements--kotlin--hard]]
- [[q-coroutine-builders-comparison--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
