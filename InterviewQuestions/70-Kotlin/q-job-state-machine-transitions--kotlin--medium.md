---\
id: kotlin-105
title: "Job state machine and state transitions / Job машина состояний и переходы"
aliases: ["Job state machine", "Job state transitions", "Kotlin Job states"]
topic: kotlin
subtopics: [coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-fan-in-fan-out--kotlin--hard, q-inline-function-limitations--kotlin--medium]
created: 2025-10-12
updated: 2025-11-11
tags: [difficulty/medium]

---\
# Вопрос (RU)

> Объясните машину состояний `Job` в Kotlin корутинах: какие есть состояния (`New`, `Active`, `Completing`, `Completed`, `Cancelling`, `Cancelled`), допустимые переходы между ними, как ведут себя свойства `isActive`, `isCompleted`, `isCancelled` в каждом состоянии, как работают правила распространения состояний между родителем и потомками, и как `join()` и `cancel()` взаимодействуют с различными состояниями. Проиллюстрируйте ответ подробными примерами, включая реальные сценарии (логирование состояний и `ViewModel`-подобное использование).

# Question (EN)

> Explain the `Job` state machine in Kotlin coroutines: what states exist (`New`, `Active`, `Completing`, `Completed`, `Cancelling`, `Cancelled`), which transitions are valid between them, how `isActive`, `isCompleted`, and `isCancelled` behave in each state, how parent-child state propagation works, and how `join()` and `cancel()` interact with different states. Illustrate the answer with detailed examples, including real-world scenarios (state logging and `ViewModel`-like usage).

## Ответ (RU)

### Обзор

`Job` в Kotlin корутинах (см. [[c-coroutines]]) ведёт себя как конечный автомат с чётко определёнными этапами жизненного цикла. Понимание этих этапов, переходов между ними и поведения свойств `isActive`, `isCompleted` и `isCancelled` критически важно для управления жизненным циклом корутин, отладки и предотвращения распространённых ошибок.

Здесь рассматривается практическая, концептуальная модель жизненного цикла `Job` (6 удобных для обсуждения наблюдаемых состояний), допустимые переходы, поведение свойств в каждом состоянии, правила распространения состояний между родителем и потомками, а также то, как `join()` и `cancel()` взаимодействуют с различными состояниями.

Важно: конкретные внутренние состояния — деталь реализации `kotlinx.coroutines`. Описанные далее состояния — удобная модель, а не жёсткий публичный контракт по комбинациям трёх булевых флагов.

### 6 Состояний `Job`

Концептуально `Job` можно мыслить в одном из следующих состояний (по его публичным свойствам и поведению):

1. `New` (только для `CoroutineStart.LAZY`)
2. `Active` (нормальное выполнение)
3. `Completing` (тело завершено, ожидание потомков)
4. `Completed` (полностью успешно завершён)
5. `Cancelling` (отмена в процессе, выполнение обработчиков/finally, ожидание потомков)
6. `Cancelled` (терминальное отменённое состояние)

Важно: это концептуальные стадии жизненного цикла. Внутренняя реализация может иметь больше состояний/вариантов, но модель отражает наблюдаемое поведение API `Job`.

### Поведение Свойств Состояния

| Состояние | isActive | isCompleted | isCancelled |
|-----------|----------|-------------|-------------|
| `New` | false | false | false |
| `Active` | true | false | false |
| `Completing` | true | false | false |
| `Completed` | false | true | false |
| `Cancelling` | false | false | true |
| `Cancelled` | false | true | true |

Важно: таблица отражает логическую модель. Реально наблюдаемые комбинации могут быть кратковременно переходными, и по трём флагам нельзя надёжно различить все внутренние стадии.

### Диаграмма Переходов Состояний (текстовая)

```text

                           New      (только LAZY)
                       (начальное)

                              start()

            Active
                     (выполнение)

                             тело завершено

                      Completing
                     (ожид. детей)

                             все дети
                             завершены

                       Completed
                        (успех)

           cancel()

                Cancelling
               (finally,
                ожид. детей) дети завершены

                       finally выполнен

                 Cancelled
               (терминальное)

```

### Состояние 1: New (`CoroutineStart.LAZY`)

Состояние `New` существует только для корутин, созданных с `CoroutineStart.LAZY`: корутина создана, но ещё не запущена.

Свойства:
- `isActive = false`
- `isCompleted = false`
- `isCancelled = false`

Переходы:
- В `Active`: вызов `start()` или `join()` (для LAZY `join()` запускает `Job` и ждёт её завершения)
- В `Cancelled`: вызов `cancel()` до запуска; `Job` немедленно помечается отменённым и завершённым:
  - `isActive = false`, `isCompleted = true`, `isCancelled = true`

```kotlin
import kotlinx.coroutines.*

fun demonstrateNewState() = runBlocking {
    println("=== New State Demo ===")

    val job = launch(start = CoroutineStart.LAZY) {
        println("Coroutine body executing")
        delay(100)
    }

    // In New state
    println("After creation:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // false
    println("  isCancelled: ${job.isCancelled}")   // false

    delay(50) // Wait a bit

    println("\nAfter 50ms (still not started):")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // false

    // Transition to Active
    job.start()
    println("\nAfter start():")
    println("  isActive: ${job.isActive}")         // true (while running)
    println("  isCompleted: ${job.isCompleted}")   // false

    job.join()
    println("\nAfter completion:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
}
```

### Состояние 2: Active (нормальное выполнение)

Состояние `Active` означает, что корутина выполняется или ещё не завершилась после запуска. Это нормальное рабочее состояние.

Свойства:
- `isActive = true`
- `isCompleted = false`
- `isCancelled = false`

Переходы:
- В `Completing`: тело завершилось, но у `Job` есть активные потомки
- В `Completed`: тело завершилось и потомков нет (или все уже завершены)
- В `Cancelling`: вызвано `cancel()` или отмена/ошибка пришла от родителя/потомка

```kotlin
import kotlinx.coroutines.*

fun demonstrateActiveState() = runBlocking {
    println("=== Active State Demo ===")

    val job = launch {
        println("Starting execution")
        println("  isActive: ${coroutineContext[Job]?.isActive}")       // true
        println("  isCompleted: ${coroutineContext[Job]?.isCompleted}") // false

        repeat(3) { i ->
            delay(100)
            println("Iteration $i - still active: ${coroutineContext[Job]?.isActive}")
        }

        println("Body finished")
    }

    delay(50)
    println("\nFrom parent scope:")
    println("  isActive: ${job.isActive}")         // likely true
    println("  isCompleted: ${job.isCompleted}")   // false

    job.join()
    println("\nAfter join:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
}
```

### Состояние 3: Completing (ожидание потомков)

Состояние `Completing` возникает, когда тело корутины завершилось, но у неё всё ещё есть активные потомки. Родитель ждёт всех потомков, прежде чем перейти в терминальное состояние.

Свойства:
- `isActive = true` (с точки зрения API `Job` всё ещё активен)
- `isCompleted = false`
- `isCancelled = false`

Ключевой момент: `isActive` остаётся `true` в состоянии `Completing`, потому что работа `Job` ещё не полностью завершена и её итог зависит от потомков.

```kotlin
import kotlinx.coroutines.*

fun demonstrateCompletingState() = runBlocking {
    println("=== Completing State Demo ===")

    val parentJob = launch {
        println("Parent body started")

        // Launch child coroutines
        launch {
            println("  Child 1 started")
            delay(200)
            println("  Child 1 finished")
        }

        launch {
            println("  Child 2 started")
            delay(400)
            println("  Child 2 finished")
        }

        println("Parent body finished (but children still running)")
        // Parent enters Completing-like state here
    }

    delay(250) // Parent body done, child 1 done, child 2 still running

    println("\nParent likely waiting for children:")
    println("  isActive: ${parentJob.isActive}")       // true
    println("  isCompleted: ${parentJob.isCompleted}") // false
    println("  isCancelled: ${parentJob.isCancelled}") // false

    parentJob.join() // Wait for child 2 to finish

    println("\nAfter all children complete:")
    println("  isActive: ${parentJob.isActive}")       // false
    println("  isCompleted: ${parentJob.isCompleted}") // true
}
```

### Состояние 4: Completed (успешное завершение)

`Completed` — терминальное состояние, указывающее на успешное завершение: тело `Job` завершилось, все потомки завершены, нет необработанной отмены или ошибки.

Свойства:
- `isActive = false`
- `isCompleted = true`
- `isCancelled = false`

Переходы: нет (терминальное состояние).

```kotlin
import kotlinx.coroutines.*

fun demonstrateCompletedState() = runBlocking {
    println("=== Completed State Demo ===")

    val job = launch {
        println("Doing work...")
        delay(100)
        println("Work done!")
    }

    job.join()

    println("\nJob in Completed state:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
    println("  isCancelled: ${job.isCancelled}")   // false

    // join() on completed job returns immediately
    println("\nCalling join() again...")
    job.join()
    println("join() returned immediately")

    // cancel() on completed job has no effect (no state change)
    println("\nCalling cancel()...")
    job.cancel()
    println("cancel() had no effect (already completed)")
    println("  isCancelled: ${job.isCancelled}")   // still false
}
```

### Состояние 5: Cancelling (отмена В процессе)

Состояние `Cancelling` возникает, когда отмена запрошена. `Job` помечен как отменённый (`isCancelled = true`), выполняются блоки `finally` и обработчики, а также отменяются/дожидаются потомки. До завершения этой фазы `isCompleted` остаётся `false`.

Свойства (логическая модель):
- `isActive = false`
- `isCompleted = false`
- `isCancelled = true`

Переходы:
- В `Cancelled`: после завершения очистки (`finally`/обработчики) и всех потомков.

```kotlin
import kotlinx.coroutines.*

fun demonstrateCancellingState() = runBlocking {
    println("=== Cancelling State Demo ===")

    val job = launch(Dispatchers.Default) { // use Default to avoid blocking main
        try {
            println("Starting work...")
            repeat(5) { i ->
                println("  Iteration $i")
                delay(100)
            }
        } finally {
            println("Finally block started")
            println("  isActive: ${coroutineContext[Job]?.isActive}")       // typically false during cancelling
            println("  isCancelled: ${coroutineContext[Job]?.isCancelled}") // true

            // Cleanup work; avoid blocking threads in real code.
            delay(150)
            println("  Cleanup done")

            println("Finally block finished")
        }
    }

    delay(250) // Let it run for a bit

    println("\nCancelling job...")
    job.cancel()

    // After cancel(), this Job is already marked as cancelled.
    println("Job right after cancel():")
    println("  isActive: ${job.isActive}")       // false
    println("  isCompleted: ${job.isCompleted}") // false (until finally completes)
    println("  isCancelled: ${job.isCancelled}") // true

    job.join() // Wait for cancellation to complete

    println("\nAfter cancellation complete:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
    println("  isCancelled: ${job.isCancelled}")   // true
}
```

### Состояние 6: Cancelled (терминальное Отменённое состояние)

Состояние `Cancelled` — терминальное: отмена завершена, все необходимые обработчики выполнены, потомки завершены.

Свойства:
- `isActive = false`
- `isCompleted = true`
- `isCancelled = true`

Ключевой момент: `isCompleted = true` и для успешно завершённых, и для отменённых `Job`; различать нужно по `isCancelled` и причине.

Переходы: нет (терминальное состояние).

```kotlin
import kotlinx.coroutines.*

fun demonstrateCancelledState() = runBlocking {
    println("=== Cancelled State Demo ===")

    val job = launch {
        try {
            repeat(10) { i ->
                println("Working... $i")
                delay(100)
            }
        } finally {
            println("Cleanup in finally")
        }
    }

    delay(250)
    job.cancel()
    job.join()

    println("\nJob in Cancelled state:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
    println("  isCancelled: ${job.isCancelled}")   // true

    // Subsequent operations have no effect
    job.cancel() // No-op
    job.join()   // Returns immediately

    println("\nAfter additional cancel/join:")
    println("  isCompleted: ${job.isCompleted}")   // still true
    println("  isCancelled: ${job.isCancelled}")   // still true
}
```

### Правила Распространения Состояний Родитель–Потомок

1. Отмена родителя → отмена потомков
   - При отмене родителя все его потомки рекурсивно отменяются.
   - Потомки проходят фазу отмены и затем переходят в терминальное отменённое состояние.

2. Ошибка потомка → отмена родителя (для обычного `Job`)
   - Невыловленное исключение в потомке по умолчанию отменяет родителя.
   - Сиблинги также отменяются.
   - Используйте `SupervisorJob` / `supervisorScope`, чтобы изолировать ошибки.

3. Родитель ждёт потомков
   - После завершения тела родитель ждёт всех потомков, прежде чем попасть в терминальное состояние.
   - Если все завершились успешно, родитель становится `Completed`; если кто-то отменён или упал — завершение (как правило) будет отменённым / с ошибкой.

```kotlin
import kotlinx.coroutines.*

fun demonstrateParentChildPropagation() = runBlocking {
    println("=== Parent-Child Propagation ===")

    val parent = launch {
        println("Parent started")

        val child1 = launch {
            try {
                println("  Child 1 started")
                delay(1000)
                println("  Child 1 finished")
            } finally {
                println("  Child 1 finally (cancelled: ${coroutineContext[Job]?.isCancelled})")
            }
        }

        val child2 = launch {
            try {
                println("  Child 2 started")
                delay(1000)
                println("  Child 2 finished")
            } finally {
                println("  Child 2 finally (cancelled: ${coroutineContext[Job]?.isCancelled})")
            }
        }

        println("Parent body finished (waiting for children)")
    }

    delay(200)
    println("\nCancelling parent...")
    parent.cancel()

    parent.join()

    println("\nAll jobs cancelled")
    println("Parent:")
    println("  isCompleted: ${parent.isCompleted}") // true
    println("  isCancelled: ${parent.isCancelled}") // true
}
```

### Поведение `join()` В Разных Состояниях

`join()` приостанавливает вызывающую корутину, пока `Job` не достигнет терминального состояния (`Completed` или `Cancelled`).

| Состояние | Поведение `join()` |
|-----------|--------------------|
| `New` | Для LAZY job: запускает и ждёт завершения |
| `Active` | Ждёт завершения или отмены `Job` |
| `Completing` | Ждёт завершения всех потомков и терминального состояния |
| `Completed` | Возвращается немедленно |
| `Cancelling` | Ждёт завершения `finally`/обработчиков и потомков |
| `Cancelled` | Возвращается немедленно |

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

fun demonstrateJoinBehavior() = runBlocking {
    println("=== join() Behavior Demo ===")

    // 1. join() on LAZY job starts it
    val lazyJob = launch(start = CoroutineStart.LAZY) {
        println("Lazy job executing")
        delay(100)
    }

    println("1. join() on LAZY (New state) - starts and waits:")
    val time1 = measureTimeMillis {
        lazyJob.join()
    }
    println("   Took ${time1}ms\n")

    // 2. join() on Active job waits
    val activeJob = launch {
        delay(200)
    }

    delay(50)
    println("2. join() on Active job - waits for completion:")
    val time2 = measureTimeMillis {
        activeJob.join()
    }
    println("   Took ${time2}ms\n")

    // 3. join() on Completed job returns immediately
    val completedJob = launch {
        delay(100)
    }
    completedJob.join()

    println("3. join() on Completed job - immediate return:")
    val time3 = measureTimeMillis {
        completedJob.join()
    }
    println("   Took ${time3}ms\n")

    // 4. join() during Cancelling waits for cleanup
    val cancellingJob = launch(Dispatchers.Default) {
        try {
            delay(10_000)
        } finally {
            println("   Cleanup starting...")
            delay(150)
            println("   Cleanup done")
        }
    }

    delay(50)
    cancellingJob.cancel()

    println("4. join() on Cancelling job - waits for finally:")
    val time4 = measureTimeMillis {
        cancellingJob.join()
    }
    println("   Took ${time4}ms")
}
```

### Поведение `cancel()` В Разных Состояниях

`cancel()` запрашивает отмену `Job`.

| Состояние | Поведение `cancel()` |
|-----------|----------------------|
| `New` | Для LAZY: немедленно завершает `Job` как `Cancelled` (`isCompleted = true`, `isCancelled = true`), тело не выполняется |
| `Active` | Переход в фазу отмены (логически `Cancelling`): запуск `finally`/обработчиков, отмена потомков |
| `Completing` | Переход в фазу отмены, отмена оставшихся потомков |
| `Completed` | Без эффекта (идемпотентно, состояние не меняется) |
| `Cancelling` | Дополнительного эффекта нет |
| `Cancelled` | Без эффекта (идемпотентно) |

```kotlin
import kotlinx.coroutines.*

fun demonstrateCancelBehavior() = runBlocking {
    println("=== cancel() Behavior Demo ===")

    // 1. cancel() on LAZY job (New state)
    println("1. cancel() on LAZY (New state):")
    val lazyJob = launch(start = CoroutineStart.LAZY) {
        println("   This should not print")
    }
    lazyJob.cancel()
    lazyJob.join()
    println("   Job cancelled without execution")
    println("   isCompleted: ${lazyJob.isCompleted}")  // true
    println("   isCancelled: ${lazyJob.isCancelled}\n") // true

    // 2. cancel() on Active job
    println("2. cancel() on Active job:")
    val activeJob = launch {
        try {
            println("   Working...")
            delay(1000)
        } finally {
            println("   Finally block executed")
        }
    }
    delay(50)
    activeJob.cancel()
    activeJob.join()
    println("   Job cancelled and cleaned up\n")

    // 3. cancel() on Completed job
    println("3. cancel() on Completed job:")
    val completedJob = launch {
        delay(50)
    }
    completedJob.join()

    println("   Before cancel: isCancelled=${completedJob.isCancelled}")
    completedJob.cancel()
    println("   After cancel: isCancelled=${completedJob.isCancelled}")
    println("   (No effect - already completed)\n")

    // 4. cancel() multiple times
    println("4. Multiple cancel() calls:")
    val job = launch {
        delay(1000)
    }
    delay(50)

    job.cancel()
    println("   First cancel()")
    job.cancel()
    println("   Second cancel() - no additional effect")
    job.cancel()
    println("   Third cancel() - no additional effect")

    job.join()
    println("   All cancels completed")
}
```

### `invokeOnCompletion` Для Уведомлений О Состоянии

Используйте `invokeOnCompletion`, чтобы получать уведомление, когда `Job` достигает терминального состояния (`Completed` или `Cancelled`, либо завершился с ошибкой).

```kotlin
import kotlinx.coroutines.*

fun demonstrateInvokeOnCompletion() = runBlocking {
    println("=== invokeOnCompletion Demo ===")

    val job = launch {
        println("Job started")
        delay(200)
        println("Job finished")
    }

    // Register completion handler
    job.invokeOnCompletion { cause ->
        when (cause) {
            null -> println("Completed successfully")
            is CancellationException -> println("Cancelled: ${cause.message}")
            else -> println("Failed: ${cause.message}")
        }
    }

    delay(100)
    println("Job is active: ${job.isActive}")

    job.join()

    println("\n--- Cancellation Case ---")

    val cancelledJob = launch {
        try {
            delay(1000)
        } finally {
            println("Cleanup")
        }
    }

    cancelledJob.invokeOnCompletion { cause ->
        println("Completion handler: cause=$cause")
        println("  isCancelled: ${cancelledJob.isCancelled}")
        println("  isCompleted: ${cancelledJob.isCompleted}")
    }

    delay(50)
    cancelledJob.cancel("User requested cancellation")
    cancelledJob.join()
}
```

### Невозможные (или недопустимые) Переходы Состояний

1. Нельзя перейти из `Completed` в `Active` — терминальное состояние, вызов `start()` после завершения не меняет состояние (no-op).
2. Нельзя перейти из `Cancelled` в `Active`.
3. Нельзя из любого терминального состояния вернуться в `New`.
4. При отмене всегда проходит фаза логики завершения: обработчики и `finally` должны выполниться до того, как `Job` считается полностью завершённым.
5. Успешно завершившийся `Job` становится `Completed` только после завершения тела и всех потомков.

```kotlin
import kotlinx.coroutines.*

fun demonstrateImpossibleTransitions() = runBlocking {
    println("=== Impossible Transitions Demo ===")

    // 1. Cannot restart completed job
    val completedJob = launch {
        delay(50)
    }
    completedJob.join()

    println("1. Completed job:")
    println("   isCompleted: ${completedJob.isCompleted}")

    // completedJob.start() // Has no effect; cannot transition back to Active

    delay(100)
    println("   Still completed: ${completedJob.isCompleted}")
    println("   Cannot transition back to Active\n")

    // 2. Completion logic during cancellation
    var finallyExecuted = false
    val job = launch {
        try {
            delay(1000)
        } finally {
            finallyExecuted = true
            println("2. Finally executed during cancellation (or attempted)")
        }
    }

    delay(50)
    job.cancel()
    job.join()

    println("   finallyExecuted: $finallyExecuted")

    // 3. Parent waits for child
    val parentJob = launch {
        launch {
            delay(100)
        }
        println("3. Parent body done, but not completed until child finishes")
    }

    delay(50)
    println("   Parent isCompleted: ${parentJob.isCompleted}") // false

    delay(100)
    println("   After child done, parent isCompleted: ${parentJob.isCompleted}") // true
}
```

### Иллюстративный Пример: Логирование Состояний

Важно: по трём булевым (`isActive`, `isCompleted`, `isCancelled`) нельзя точно восстановить внутреннюю машину состояний, можно лишь приблизительно оценивать состояние для логирования. Состояние "Cancelling" (как отдельная стадия) надёжно не различается только по этим флагам.

```kotlin
import kotlinx.coroutines.*

class StatefulJobMonitor {
    private var previousState: String = ""

    fun getState(job: Job): String {
        return when {
            !job.isActive && !job.isCompleted && !job.isCancelled -> "New" // LAZY
            job.isActive && !job.isCancelled && !job.isCompleted -> "Active or Completing"
            job.isCompleted && !job.isCancelled -> "Completed"
            job.isCompleted && job.isCancelled -> "Cancelled"
            // Промежуточные фазы отмены (Cancelling) по флагам не различимы надёжно
            else -> "Unknown"
        }
    }

    fun logStateChange(job: Job, label: String) {
        val currentState = getState(job)
        if (currentState != previousState) {
            println("[$label] State: $previousState → $currentState")
            println("  isActive=${job.isActive}, isCompleted=${job.isCompleted}, isCancelled=${job.isCancelled}")
            previousState = currentState
        }
    }
}

fun demonstrateStateLogging() = runBlocking {
    println("=== State Logging Demo ===")

    val monitor = StatefulJobMonitor()

    val job = launch(start = CoroutineStart.LAZY) {
        monitor.logStateChange(coroutineContext[Job]!!, "Inside coroutine")

        try {
            repeat(3) { i ->
                delay(100)
                println("Iteration $i")
            }
        } finally {
            monitor.logStateChange(coroutineContext[Job]!!, "In finally")
        }
    }

    monitor.logStateChange(job, "After creation")

    delay(50)
    job.start()
    monitor.logStateChange(job, "After start")

    delay(150)
    monitor.logStateChange(job, "During execution")

    delay(200)
    monitor.logStateChange(job, "After completion")
}
```

### Иллюстративный Пример: Android-подобный `ViewModel` С Отслеживанием Состояния

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

class DataViewModel {
    private val viewModelScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    private val _dataState = MutableStateFlow<DataState>(DataState.Idle)
    val dataState: StateFlow<DataState> = _dataState.asStateFlow()

    private var loadJob: Job? = null

    fun loadData() {
        // Cancel previous load if still running
        loadJob?.cancel()

        loadJob = viewModelScope.launch {
            _dataState.value = DataState.Loading

            try {
                val data = fetchDataFromNetwork()

                // Check if still active before updating state
                if (isActive) {
                    _dataState.value = DataState.Success(data)
                }
            } catch (e: CancellationException) {
                // Job was cancelled
                _dataState.value = DataState.Idle
                throw e // Rethrow to propagate cancellation
            } catch (e: Exception) {
                if (isActive) {
                    _dataState.value = DataState.Error(e.message ?: "Unknown error")
                }
            }
        }

        // Monitor job state
        loadJob?.invokeOnCompletion { cause ->
            println("Load job completed")
            println("  Cancelled: ${loadJob?.isCancelled}")
            println("  Cause: $cause")
        }
    }

    fun cancelLoad() {
        loadJob?.cancel("User cancelled")
    }

    fun getJobState(): String {
        val job = loadJob ?: return "No job"
        return when {
            job.isActive -> "Active"
            job.isCompleted && !job.isCancelled -> "Completed"
            job.isCompleted && job.isCancelled -> "Cancelled"
            else -> "Unknown"
        }
    }

    private suspend fun fetchDataFromNetwork(): String {
        delay(2000)
        return "Network data"
    }

    fun onCleared() {
        viewModelScope.cancel()
    }
}

sealed class DataState {
    object Idle : DataState()
    object Loading : DataState()
    data class Success(val data: String) : DataState()
    data class Error(val message: String) : DataState()
}

// Usage demo
fun demonstrateViewModelStateTracking() = runBlocking {
    println("=== ViewModel State Tracking ===")

    val viewModel = DataViewModel()

    // Collect state
    val job = launch {
        viewModel.dataState.collect { state ->
            println("UI State: $state")
        }
    }

    println("Starting load...")
    viewModel.loadData()
    println("Job state: ${viewModel.getJobState()}")

    delay(500)
    println("\nCancelling load...")
    viewModel.cancelLoad()

    delay(100)
    println("Job state after cancel: ${viewModel.getJobState()}")

    job.cancel()
    viewModel.onCleared()
}
```

### Лучшие Практики Проверки Состояния

1. Проверяйте `isActive` перед тяжёлой работой или коммитом результата:

   ```kotlin
   suspend fun doWork() {
       if (!isActive) return

       val result = heavyComputation()

       if (!isActive) return

       updateUI(result)
   }
   ```

2. Используйте `ensureActive()` для кооперативной отмены:

   ```kotlin
   suspend fun processItems(items: List<Item>) {
       for (item in items) {
           ensureActive() // Бросит CancellationException при отмене
           processItem(item)
       }
   }
   ```

3. Перед обновлением разделяемого состояния убеждайтесь, что `Job` ещё активен:

   ```kotlin
   val job = launch {
       val data = loadData()
       if (isActive) {
           _state.value = data
       }
   }
   ```

4. Используйте `invokeOnCompletion` для очистки, зависящей от финального состояния:

   ```kotlin
   val job = launch {
       // Work
   }

   job.invokeOnCompletion { cause ->
       if (cause != null) {
           // Cleanup on failure/cancellation
       }
   }
   ```

5. Не полагайтесь на условные проверки вида `if (!job.isCompleted) job.cancel()` — просто вызывайте `cancel()`, он идемпотентен.

6. При необходимости дождаться завершения `finally` после `cancel()` вызывайте `join()`:

   ```kotlin
   job.cancel()
   job.join() // Дождаться finally
   // Теперь безопасно освобождать ресурсы
   ```

### Распространённые Ошибки

1. Считать, что `isCompleted == true` гарантирует успех:

   ```kotlin
   // Плохо
   if (job.isCompleted) {
       // Может быть и отмена
   }

   // Хорошо
   if (job.isCompleted && !job.isCancelled) {
       // Успешное завершение
   }
   ```

2. Не ждать завершения отмены:

   ```kotlin
   // Плохо
   job.cancel()
   resource.release() // finally может ещё выполняться

   // Хорошо
   job.cancel()
   job.join()
   resource.release()
   ```

3. Интерпретировать `!isActive` как успешное завершение:

   ```kotlin
   // Плохо
   if (!job.isActive) {
       // Может быть New, Cancelling, Completed или Cancelled
   }

   // Хорошо
   if (job.isCompleted && !job.isCancelled) {
       // Успех
   }
   ```

4. Пытаться перезапустить завершённый `Job`:

   ```kotlin
   // Плохо
   job.start() // Не сработает для уже завершённого (no-op)

   // Лучше создать новый Job
   ```

### Соображения Производительности

1. Проверки состояния (`isActive`, `isCompleted`, `isCancelled`) — O(1), их можно вызывать часто.
2. `invokeOnCompletion` добавляет небольшую накладную — не регистрируйте множество обработчиков без необходимости.
3. Фаза `Completing` может добавлять задержку при большом числе дочерних корутин.
4. Время в фазе отмены зависит от работы в `finally`/обработчиках — держите их быстрыми и не блокирующими.

### Тестирование Состояний `Job` (иллюстративно)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class JobStateTest {
    @Test
    fun testLazyJobStates() = runTest {
        val job = launch(start = CoroutineStart.LAZY) {
            delay(100)
        }

        // New state
        assertFalse(job.isActive)
        assertFalse(job.isCompleted)
        assertFalse(job.isCancelled)

        job.start()

        // Active state (or on the way to completion)
        assertTrue(job.isActive)
        assertFalse(job.isCompleted)

        job.join()

        // Completed state
        assertFalse(job.isActive)
        assertTrue(job.isCompleted)
        assertFalse(job.isCancelled)
    }

    @Test
    fun testCancelledStates() = runTest {
        val job = launch {
            delay(1000)
        }

        // Active
        assertTrue(job.isActive)

        job.cancel()

        // After cancel, this job is marked as cancelled
        assertTrue(job.isCancelled)

        job.join()

        // Cancelled terminal state
        assertFalse(job.isActive)
        assertTrue(job.isCompleted)
        assertTrue(job.isCancelled)
    }

    @Test
    fun testParentWaitsForChild() = runTest {
        var parentObservedActiveWhileWaiting = false

        val parent = launch {
            val child = launch {
                delay(200)
            }
            yield() // allow scheduling
            parentObservedActiveWhileWaiting = isActive && !isCompleted && !child.isCompleted
        }

        parent.join()
        assertTrue(parentObservedActiveWhileWaiting)
    }
}
```

## Answer (EN)

### Overview

The Kotlin coroutines `Job` (see [[c-coroutines]]) behaves as a state machine with well-defined lifecycle stages. Understanding these stages, their transitions, and the behavior of `isActive`, `isCompleted`, and `isCancelled` properties is critical for mastering coroutine lifecycle management, debugging, and preventing common bugs.

This answer explores the practical `Job` lifecycle model (6 commonly described observable states), valid transitions, property behavior in each state, parent-child propagation rules, and how `join()` and `cancel()` interact with different states.

Note: Internal states are an implementation detail of `kotlinx.coroutines`. The following is a conceptual model based on the public API and documentation, not a strict guarantee about all internal transitions.

### The 6 Job States

Conceptually, a `Job` can be thought of as being in one of the following states (based on its public properties and behavior):

1. `New` (only for `CoroutineStart.LAZY`)
2. `Active` (normal execution)
3. `Completing` (body finished, waiting for children)
4. `Completed` (fully finished successfully)
5. `Cancelling` (cancellation in progress, running handlers/finally, waiting for children)
6. `Cancelled` (terminal cancelled state)

Note: These are conceptual lifecycle stages. The actual internal representation may be more nuanced, but this model matches the observable behavior described in the official docs.

### State Properties Behavior

| State | isActive | isCompleted | isCancelled |
|-------|----------|-------------|-------------|
| `New` | false | false | false |
| `Active` | true | false | false |
| `Completing` | true | false | false |
| `Completed` | false | true | false |
| `Cancelling` | false | false | true |
| `Cancelled` | false | true | true |

Important: This table reflects the logical model. In practice, transient combinations may occur, and you cannot perfectly infer all internal sub-states from these three booleans alone.

### State Transition Diagram (Text-Based)

```text

                           New      (LAZY only)
                        (initial)

                              start()

            Active
                      (executing)

                             body done

                      Completing
                     (wait kids)

                             all children
                             complete

                       Completed
                       (success)

           cancel()

                Cancelling
               (finally,
                wait kids)   children done

                       finally done

                 Cancelled
                (terminal)

```

### State 1: New (`CoroutineStart.LAZY` only)

The `New` state exists only for coroutines started with `CoroutineStart.LAZY`. The coroutine is created but not started yet.

Properties:
- `isActive = false`
- `isCompleted = false`
- `isCancelled = false`

Transitions:
- To `Active`: calling `start()` or calling `join()` (which starts a lazy job and then suspends until completion)
- To `Cancelled`: calling `cancel()` before starting; it is immediately marked as cancelled and completed with:
  - `isActive = false`, `isCompleted = true`, `isCancelled = true`

```kotlin
import kotlinx.coroutines.*

fun demonstrateNewState() = runBlocking {
    println("=== New State Demo ===")

    val job = launch(start = CoroutineStart.LAZY) {
        println("Coroutine body executing")
        delay(100)
    }

    // In New state
    println("After creation:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // false
    println("  isCancelled: ${job.isCancelled}")   // false

    delay(50) // Wait a bit

    println("\nAfter 50ms (still not started):")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // false

    // Transition to Active
    job.start()
    println("\nAfter start():")
    println("  isActive: ${job.isActive}")         // true (while running)
    println("  isCompleted: ${job.isCompleted}")   // false

    job.join()
    println("\nAfter completion:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
}
```

### State 2: Active (Normal Execution)

The `Active` state means the coroutine is currently executing or not yet completed after being started. This is the normal working state.

Properties:
- `isActive = true`
- `isCompleted = false`
- `isCancelled = false`

Transitions:
- To `Completing`: body finishes normally while children are still running
- To `Completed`: body finishes and there are no children (or all are already done)
- To `Cancelling`: `cancel()` called (or parent/child failure propagates cancellation)

```kotlin
import kotlinx.coroutines.*

fun demonstrateActiveState() = runBlocking {
    println("=== Active State Demo ===")

    val job = launch {
        println("Starting execution")
        println("  isActive: ${coroutineContext[Job]?.isActive}")       // true
        println("  isCompleted: ${coroutineContext[Job]?.isCompleted}") // false

        repeat(3) { i ->
            delay(100)
            println("Iteration $i - still active: ${coroutineContext[Job]?.isActive}")
        }

        println("Body finished")
    }

    delay(50)
    println("\nFrom parent scope:")
    println("  isActive: ${job.isActive}")         // likely true
    println("  isCompleted: ${job.isCompleted}")   // false

    job.join()
    println("\nAfter join:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
}
```

### State 3: Completing (Waiting for Children)

The `Completing` state occurs when the coroutine body has finished, but it still has active children. The parent waits for all children to complete before transitioning to a terminal state.

Properties:
- `isActive = true` (still considered active from the Job API perspective)
- `isCompleted = false`
- `isCancelled = false`

Key Insight: `isActive` remains `true` during the `Completing` state because the job is not yet fully done and its outcome still depends on its children.

```kotlin
import kotlinx.coroutines.*

fun demonstrateCompletingState() = runBlocking {
    println("=== Completing State Demo ===")

    val parentJob = launch {
        println("Parent body started")

        // Launch child coroutines
        launch {
            println("  Child 1 started")
            delay(200)
            println("  Child 1 finished")
        }

        launch {
            println("  Child 2 started")
            delay(400)
            println("  Child 2 finished")
        }

        println("Parent body finished (but children still running)")
        // Parent enters Completing-like state here
    }

    delay(250) // Parent body done, child 1 done, child 2 still running

    println("\nParent likely waiting for children:")
    println("  isActive: ${parentJob.isActive}")       // true
    println("  isCompleted: ${parentJob.isCompleted}") // false
    println("  isCancelled: ${parentJob.isCancelled}") // false

    parentJob.join() // Wait for child 2 to finish

    println("\nAfter all children complete:")
    println("  isActive: ${parentJob.isActive}")       // false
    println("  isCompleted: ${parentJob.isCompleted}") // true
}
```

### State 4: Completed (Success)

The `Completed` state is a terminal state indicating successful completion. The coroutine body finished, all children completed, and no unhandled cancellation or failure is pending.

Properties:
- `isActive = false`
- `isCompleted = true`
- `isCancelled = false`

Transitions: None (terminal state)

```kotlin
import kotlinx.coroutines.*

fun demonstrateCompletedState() = runBlocking {
    println("=== Completed State Demo ===")

    val job = launch {
        println("Doing work...")
        delay(100)
        println("Work done!")
    }

    job.join()

    println("\nJob in Completed state:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
    println("  isCancelled: ${job.isCancelled}")   // false

    // join() on completed job returns immediately
    println("\nCalling join() again...")
    job.join()
    println("join() returned immediately")

    // cancel() on completed job has no effect (no state change)
    println("\nCalling cancel()...")
    job.cancel()
    println("cancel() had no effect (already completed)")
    println("  isCancelled: ${job.isCancelled}")   // still false
}
```

### State 5: Cancelling (Running Finally Blocks)

The `Cancelling` state occurs when cancellation is in progress. The coroutine is marked as cancelled (`isCancelled = true`), runs `finally` blocks and completion handlers, and waits for its children to complete or cancel. During this phase `isCompleted` is still `false`.

Logical properties:
- `isActive = false`
- `isCompleted = false`
- `isCancelled = true`

Transitions:
- To `Cancelled`: cleanup (finally/handlers) complete and all children have finished.

```kotlin
import kotlinx.coroutines.*

fun demonstrateCancellingState() = runBlocking {
    println("=== Cancelling State Demo ===")

    val job = launch(Dispatchers.Default) { // use Default to avoid blocking main
        try {
            println("Starting work...")
            repeat(5) { i ->
                println("  Iteration $i")
                delay(100)
            }
        } finally {
            println("Finally block started")
            println("  isActive: ${coroutineContext[Job]?.isActive}")       // typically false during cancelling
            println("  isCancelled: ${coroutineContext[Job]?.isCancelled}") // true

            // Cleanup work; avoid blocking threads in real code.
            delay(150)
            println("  Cleanup done")

            println("Finally block finished")
        }
    }

    delay(250) // Let it run for a bit

    println("\nCancelling job...")
    job.cancel()

    // After cancel(), this Job is already marked as cancelled.
    println("Job right after cancel():")
    println("  isActive: ${job.isActive}")       // false
    println("  isCompleted: ${job.isCompleted}") // false (until finally completes)
    println("  isCancelled: ${job.isCancelled}") // true

    job.join() // Wait for cancellation to complete

    println("\nAfter cancellation complete:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
    println("  isCancelled: ${job.isCancelled}")   // true
}
```

### State 6: Cancelled (Terminal Cancelled State)

The `Cancelled` state is a terminal state indicating that cancellation completed. All relevant handlers and finally blocks have finished, and all children are done.

Properties:
- `isActive = false`
- `isCompleted = true`
- `isCancelled = true`

Key Insight: `isCompleted` is `true` in the `Cancelled` state because the job has finished (even though it was cancelled).

Transitions: None (terminal state)

```kotlin
import kotlinx.coroutines.*

fun demonstrateCancelledState() = runBlocking {
    println("=== Cancelled State Demo ===")

    val job = launch {
        try {
            repeat(10) { i ->
                println("Working... $i")
                delay(100)
            }
        } finally {
            println("Cleanup in finally")
        }
    }

    delay(250)
    job.cancel()
    job.join()

    println("\nJob in Cancelled state:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
    println("  isCancelled: ${job.isCancelled}")   // true

    // Subsequent operations have no effect
    job.cancel() // No-op
    job.join()   // Returns immediately

    println("\nAfter additional cancel/join:")
    println("  isCompleted: ${job.isCompleted}")   // still true
    println("  isCancelled: ${job.isCancelled}")   // still true
}
```

### Parent-Child State Propagation Rules

`Coroutine` state propagation follows structured concurrency principles:

1. Parent cancellation → Children cancellation
   - When a parent is cancelled, all its children are cancelled recursively.
   - Children go through the cancellation phase and then reach the terminal cancelled state.

2. Child failure → Parent cancellation (for regular `Job`)
   - When a child fails with an unhandled exception, its parent is cancelled by default.
   - Sibling coroutines are also cancelled.
   - Use `SupervisorJob`/`supervisorScope` to prevent a child failure from cancelling its parent and siblings.

3. Parent waits for children
   - After the parent body finishes, it waits for all its children before reaching a terminal state.
   - If all complete successfully, parent becomes `Completed`; if any is cancelled/failed, parent completes accordingly (often cancelled/failed).

```kotlin
import kotlinx.coroutines.*

fun demonstrateParentChildPropagation() = runBlocking {
    println("=== Parent-Child Propagation ===")

    val parent = launch {
        println("Parent started")

        val child1 = launch {
            try {
                println("  Child 1 started")
                delay(1000)
                println("  Child 1 finished")
            } finally {
                println("  Child 1 finally (cancelled: ${coroutineContext[Job]?.isCancelled})")
            }
        }

        val child2 = launch {
            try {
                println("  Child 2 started")
                delay(1000)
                println("  Child 2 finished")
            } finally {
                println("  Child 2 finally (cancelled: ${coroutineContext[Job]?.isCancelled})")
            }
        }

        println("Parent body finished (waiting for children)")
    }

    delay(200)
    println("\nCancelling parent...")
    parent.cancel()

    parent.join()

    println("\nAll jobs cancelled")
    println("Parent:")
    println("  isCompleted: ${parent.isCompleted}") // true
    println("  isCancelled: ${parent.isCancelled}") // true
}
```

### `join()` Behavior in Each State

The `join()` function suspends until the job reaches a terminal state (`Completed` or `Cancelled`).

| State | join() Behavior |
|-------|-----------------|
| `New` | For a LAZY job, starts it, then suspends until completion |
| `Active` | Suspends until job completes or is cancelled |
| `Completing` | Suspends until all children complete and a terminal state is reached |
| `Completed` | Returns immediately |
| `Cancelling` | Suspends until cancellation handlers/finally and children complete |
| `Cancelled` | Returns immediately |

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

fun demonstrateJoinBehavior() = runBlocking {
    println("=== join() Behavior Demo ===")

    // 1. join() on LAZY job starts it
    val lazyJob = launch(start = CoroutineStart.LAZY) {
        println("Lazy job executing")
        delay(100)
    }

    println("1. join() on LAZY (New state) - starts and waits:")
    val time1 = measureTimeMillis {
        lazyJob.join()
    }
    println("   Took ${time1}ms\n")

    // 2. join() on Active job waits
    val activeJob = launch {
        delay(200)
    }

    delay(50)
    println("2. join() on Active job - waits for completion:")
    val time2 = measureTimeMillis {
        activeJob.join()
    }
    println("   Took ${time2}ms\n")

    // 3. join() on Completed job returns immediately
    val completedJob = launch {
        delay(100)
    }
    completedJob.join()

    println("3. join() on Completed job - immediate return:")
    val time3 = measureTimeMillis {
        completedJob.join()
    }
    println("   Took ${time3}ms\n")

    // 4. join() during Cancelling waits for cleanup
    val cancellingJob = launch(Dispatchers.Default) {
        try {
            delay(10_000)
        } finally {
            println("   Cleanup starting...")
            delay(150)
            println("   Cleanup done")
        }
    }

    delay(50)
    cancellingJob.cancel()

    println("4. join() on Cancelling job - waits for finally:")
    val time4 = measureTimeMillis {
        cancellingJob.join()
    }
    println("   Took ${time4}ms")
}
```

### `cancel()` Behavior in Each State

The `cancel()` function requests cancellation of the job.

| State | cancel() Behavior |
|-------|-------------------|
| `New` | For a LAZY job, completes it immediately as `Cancelled` (`isCompleted = true`, `isCancelled = true`), body never runs |
| `Active` | Transitions into a cancellation phase (logically `Cancelling`): runs handlers/finally, cancels children |
| `Completing` | Transitions into cancellation phase, cancels remaining children |
| `Completed` | No effect (idempotent, state does not change) |
| `Cancelling` | No additional effect (already cancelling) |
| `Cancelled` | No effect (idempotent) |

```kotlin
import kotlinx.coroutines.*

fun demonstrateCancelBehavior() = runBlocking {
    println("=== cancel() Behavior Demo ===")

    // 1. cancel() on LAZY job (New state)
    println("1. cancel() on LAZY (New state):")
    val lazyJob = launch(start = CoroutineStart.LAZY) {
        println("   This should not print")
    }
    lazyJob.cancel()
    lazyJob.join()
    println("   Job cancelled without execution")
    println("   isCompleted: ${lazyJob.isCompleted}")  // true
    println("   isCancelled: ${lazyJob.isCancelled}\n") // true

    // 2. cancel() on Active job
    println("2. cancel() on Active job:")
    val activeJob = launch {
        try {
            println("   Working...")
            delay(1000)
        } finally {
            println("   Finally block executed")
        }
    }
    delay(50)
    activeJob.cancel()
    activeJob.join()
    println("   Job cancelled and cleaned up\n")

    // 3. cancel() on Completed job
    println("3. cancel() on Completed job:")
    val completedJob = launch {
        delay(50)
    }
    completedJob.join()

    println("   Before cancel: isCancelled=${completedJob.isCancelled}")
    completedJob.cancel()
    println("   After cancel: isCancelled=${completedJob.isCancelled}")
    println("   (No effect - already completed)\n")

    // 4. cancel() multiple times
    println("4. Multiple cancel() calls:")
    val job = launch {
        delay(1000)
    }
    delay(50)

    job.cancel()
    println("   First cancel()")
    job.cancel()
    println("   Second cancel() - no additional effect")
    job.cancel()
    println("   Third cancel() - no additional effect")

    job.join()
    println("   All cancels completed")
}
```

### `invokeOnCompletion` For State Notifications

Use `invokeOnCompletion` to be notified when a job reaches a terminal state (`Completed` or `Cancelled`, or failed with exception).

```kotlin
import kotlinx.coroutines.*

fun demonstrateInvokeOnCompletion() = runBlocking {
    println("=== invokeOnCompletion Demo ===")

    val job = launch {
        println("Job started")
        delay(200)
        println("Job finished")
    }

    // Register completion handler
    job.invokeOnCompletion { cause ->
        when (cause) {
            null -> println("Completed successfully")
            is CancellationException -> println("Cancelled: ${cause.message}")
            else -> println("Failed: ${cause.message}")
        }
    }

    delay(100)
    println("Job is active: ${job.isActive}")

    job.join()

    println("\n--- Cancellation Case ---")

    val cancelledJob = launch {
        try {
            delay(1000)
        } finally {
            println("Cleanup")
        }
    }

    cancelledJob.invokeOnCompletion { cause ->
        println("Completion handler: cause=$cause")
        println("  isCancelled: ${cancelledJob.isCancelled}")
        println("  isCompleted: ${cancelledJob.isCompleted}")
    }

    delay(50)
    cancelledJob.cancel("User requested cancellation")
    cancelledJob.join()
}
```

### Impossible (or Invalid) State Transitions

Certain transitions are not supported in the `Job` lifecycle:

1. Cannot go from `Completed` to `Active` — terminal state; calling `start()` is a no-op.
2. Cannot go from `Cancelled` to `Active` — terminal state.
3. Cannot go from any terminal state back to `New`.
4. Cancellation always runs completion logic: completion handlers and `finally` blocks run as part of cancellation before the job is fully finished.
5. A successfully `Completed` job only becomes `Completed` after its body and all children have finished.

```kotlin
import kotlinx.coroutines.*

fun demonstrateImpossibleTransitions() = runBlocking {
    println("=== Impossible Transitions Demo ===")

    // 1. Cannot restart completed job
    val completedJob = launch {
        delay(50)
    }
    completedJob.join()

    println("1. Completed job:")
    println("   isCompleted: ${completedJob.isCompleted}")

    // completedJob.start() // Has no effect; cannot transition back to Active

    delay(100)
    println("   Still completed: ${completedJob.isCompleted}")
    println("   Cannot transition back to Active\n")

    // 2. Completion logic during cancellation
    var finallyExecuted = false
    val job = launch {
        try {
            delay(1000)
        } finally {
            finallyExecuted = true
            println("2. Finally executed during cancellation (or attempted)")
        }
    }

    delay(50)
    job.cancel()
    job.join()

    println("   finallyExecuted: $finallyExecuted")

    // 3. Parent waits for child
    val parentJob = launch {
        launch {
            delay(100)
        }
        println("3. Parent body done, but not completed until child finishes")
    }

    delay(50)
    println("   Parent isCompleted: ${parentJob.isCompleted}") // false

    delay(100)
    println("   After child done, parent isCompleted: ${parentJob.isCompleted}") // true
}
```

### Real-World Example: State Logging (Illustrative)

Note: You cannot fully reconstruct the internal state machine from just `isActive`, `isCompleted`, and `isCancelled`. The following is an illustrative approximation for logging. The "Cancelling" phase is not reliably distinguishable using only these flags.

```kotlin
import kotlinx.coroutines.*

class StatefulJobMonitor {
    private var previousState: String = ""

    fun getState(job: Job): String {
        return when {
            !job.isActive && !job.isCompleted && !job.isCancelled -> "New" // LAZY
            job.isActive && !job.isCancelled && !job.isCompleted -> "Active or Completing"
            job.isCompleted && !job.isCancelled -> "Completed"
            job.isCompleted && job.isCancelled -> "Cancelled"
            // Transient cancelling phase cannot be reliably identified via flags alone
            else -> "Unknown"
        }
    }

    fun logStateChange(job: Job, label: String) {
        val currentState = getState(job)
        if (currentState != previousState) {
            println("[$label] State: $previousState → $currentState")
            println("  isActive=${job.isActive}, isCompleted=${job.isCompleted}, isCancelled=${job.isCancelled}")
            previousState = currentState
        }
    }
}

fun demonstrateStateLogging() = runBlocking {
    println("=== State Logging Demo ===")

    val monitor = StatefulJobMonitor()

    val job = launch(start = CoroutineStart.LAZY) {
        monitor.logStateChange(coroutineContext[Job]!!, "Inside coroutine")

        try {
            repeat(3) { i ->
                delay(100)
                println("Iteration $i")
            }
        } finally {
            monitor.logStateChange(coroutineContext[Job]!!, "In finally")
        }
    }

    monitor.logStateChange(job, "After creation")

    delay(50)
    job.start()
    monitor.logStateChange(job, "After start")

    delay(150)
    monitor.logStateChange(job, "During execution")

    delay(200)
    monitor.logStateChange(job, "After completion")
}
```

### Real-World Example: Android-like `ViewModel` with State Tracking

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

class DataViewModel {
    private val viewModelScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    private val _dataState = MutableStateFlow<DataState>(DataState.Idle)
    val dataState: StateFlow<DataState> = _dataState.asStateFlow()

    private var loadJob: Job? = null

    fun loadData() {
        // Cancel previous load if still running
        loadJob?.cancel()

        loadJob = viewModelScope.launch {
            _dataState.value = DataState.Loading

            try {
                val data = fetchDataFromNetwork()

                // Check if still active before updating state
                if (isActive) {
                    _dataState.value = DataState.Success(data)
                }
            } catch (e: CancellationException) {
                // Job was cancelled
                _dataState.value = DataState.Idle
                throw e // Rethrow to propagate cancellation
            } catch (e: Exception) {
                if (isActive) {
                    _dataState.value = DataState.Error(e.message ?: "Unknown error")
                }
            }
        }

        // Monitor job state
        loadJob?.invokeOnCompletion { cause ->
            println("Load job completed")
            println("  Cancelled: ${loadJob?.isCancelled}")
            println("  Cause: $cause")
        }
    }

    fun cancelLoad() {
        loadJob?.cancel("User cancelled")
    }

    fun getJobState(): String {
        val job = loadJob ?: return "No job"
        return when {
            job.isActive -> "Active"
            job.isCompleted && !job.isCancelled -> "Completed"
            job.isCompleted && job.isCancelled -> "Cancelled"
            else -> "Unknown"
        }
    }

    private suspend fun fetchDataFromNetwork(): String {
        delay(2000)
        return "Network data"
    }

    fun onCleared() {
        viewModelScope.cancel()
    }
}

sealed class DataState {
    object Idle : DataState()
    object Loading : DataState()
    data class Success(val data: String) : DataState()
    data class Error(val message: String) : DataState()
}

// Usage demo
fun demonstrateViewModelStateTracking() = runBlocking {
    println("=== ViewModel State Tracking ===")

    val viewModel = DataViewModel()

    // Collect state
    val job = launch {
        viewModel.dataState.collect { state ->
            println("UI State: $state")
        }
    }

    println("Starting load...")
    viewModel.loadData()
    println("Job state: ${viewModel.getJobState()}")

    delay(500)
    println("\nCancelling load...")
    viewModel.cancelLoad()

    delay(100)
    println("Job state after cancel: ${viewModel.getJobState()}")

    job.cancel()
    viewModel.onCleared()
}
```

### Best Practices for State Checking

1. Check `isActive` before doing expensive work or committing results.
2. Use `ensureActive()` for cooperative cancellation.
3. Check job activity/completion before updating shared state.
4. Use `invokeOnCompletion` for cleanup that depends on the final state.
5. Do not rely on `if (!job.isCompleted) job.cancel()`; just call `cancel()` — it's idempotent.
6. When resources depend on cancellation completion, use `cancel()` + `join()`.

### Common Pitfalls

1. Forgetting that `isCompleted == true` is also true for cancelled jobs.
2. Not waiting for cancellation to complete before releasing resources.
3. Assuming `!isActive` means successful completion (it may be New, Cancelling, Completed, or Cancelled).
4. Trying to restart a completed job instead of creating a new one (calling `start()` on a completed job is a no-op).

### Performance Considerations

1. State checks (`isActive`, `isCompleted`, `isCancelled`) are O(1) and cheap.
2. `invokeOnCompletion` adds slight overhead — avoid registering excessive handlers.
3. The `Completing` phase can add latency when many children must finish.
4. Cancellation duration depends on work in `finally`/handlers — keep them fast and non-blocking.

### Testing Job States (Illustrative)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class JobStateTest {
    @Test
    fun testLazyJobStates() = runTest {
        val job = launch(start = CoroutineStart.LAZY) {
            delay(100)
        }

        // New state
        assertFalse(job.isActive)
        assertFalse(job.isCompleted)
        assertFalse(job.isCancelled)

        job.start()

        // Active state (or on the way to completion)
        assertTrue(job.isActive)
        assertFalse(job.isCompleted)

        job.join()

        // Completed state
        assertFalse(job.isActive)
        assertTrue(job.isCompleted)
        assertFalse(job.isCancelled)
    }

    @Test
    fun testCancelledStates() = runTest {
        val job = launch {
            delay(1000)
        }

        // Active
        assertTrue(job.isActive)

        job.cancel()

        // After cancel, this job is marked as cancelled
        assertTrue(job.isCancelled)

        job.join()

        // Cancelled terminal state
        assertFalse(job.isActive)
        assertTrue(job.isCompleted)
        assertTrue(job.isCancelled)
    }

    @Test
    fun testParentWaitsForChild() = runTest {
        var parentObservedActiveWhileWaiting = false

        val parent = launch {
            val child = launch {
                delay(200)
            }
            yield() // allow scheduling
            parentObservedActiveWhileWaiting = isActive && !isCompleted && !child.isCompleted
        }

        parent.join()
        assertTrue(parentObservedActiveWhileWaiting)
    }
}
```

## Follow-ups

1. Что происходит с дочерними корутинами, когда родитель переходит в терминальное состояние `Completed`?
2. Как `SupervisorJob` влияет на распространение отмены и конечные состояния родителя и потомков?
3. Можно ли отменить `Job` в состоянии `New`, и какие будут значения `isCompleted` и `isCancelled`?
4. Почему в состоянии `Completing` `isActive == true`, а в фазе отмены (`Cancelling`) — `false`?
5. Чем `cancelAndJoin()` отличается от последовательных вызовов `cancel()` и `join()`?

## References

- "`Coroutine` context and dispatchers" — официальная документация Kotlin Coroutines
- "`Coroutine` cancellation and timeouts" — официальная документация Kotlin Coroutines
- "`Coroutine` scope and supervision" — официальная документация Kotlin Coroutines
- Исходный код библиотеки kotlinx.coroutines (`JobSupport` и связанные реализации модели состояний)
- Практические руководства по structured concurrency и обработке отмены в Kotlin coroutines

## Related Questions

- [[q-actor-pattern--kotlin--hard]]
- [[q-android-async-primitives--android--easy]]