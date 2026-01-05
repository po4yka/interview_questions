---
id: lang-084
title: "When Coroutine Cannot Be Cancelled / Когда корутина не может быть отменена"
aliases: [When Coroutine Cannot Be Cancelled, Когда корутина не может быть отменена]
topic: kotlin
subtopics: [cancellation, coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin]
created: 2025-10-15
updated: 2025-11-10
tags: [cancellation, coroutines, difficulty/medium, kotlin, programming-languages]

---
# Вопрос (RU)
> Когда корутина не может быть отменена?

---

# Question (EN)
> When can a coroutine not be cancelled?

## Ответ (RU)

Да, есть несколько типичных случаев, когда обычная кооперативная отмена в `kotlinx.coroutines` фактически не срабатывает (корутина не завершается вовремя или вовсе):

### Случай 1: Блокирующий Код

Если внутри корутины используется блокирующая операция (например, `Thread.sleep()`, длительный синхронный вызов, бесконечный `while (true) {}` без проверок), выполнение не возвращается в диспетчер корутин, и сигнал отмены не обрабатывается, пока блокирующий участок не завершится.

```kotlin
import kotlinx.coroutines.*

// - Нельзя кооперативно отменить, пока выполняется Thread.sleep (блокирует поток)
fun blockingExample() = runBlocking {
    val job = launch {
        try {
            repeat(5) { i ->
                println("Iteration $i")
                Thread.sleep(1000)  // Блокирующий вызов: не проверяет отмену корутины
            }
        } finally {
            println("Finally block")
        }
    }

    delay(2500)
    println("Cancelling...")
    job.cancelAndJoin()  // Отмена запрошена, но одного cancel для Thread.sleep недостаточно
    println("Done")
}

// - РЕШЕНИЕ: использовать delay (кооперативная отмена)
fun cooperativeExample() = runBlocking {
    val job = launch {
        try {
            repeat(5) { i ->
                println("Iteration $i")
                delay(1000)  // Точка приостановки, проверяет отмену
            }
        } finally {
            println("Finally block")
        }
    }

    delay(2500)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Done")
}
```

### Случай 2: Контекст `NonCancellable`

Если корутина или блок кода запускается в контексте `NonCancellable`, он игнорирует сигнал отмены по дизайну (частый кейс — защищённая очистка в `finally`).

```kotlin
import kotlinx.coroutines.*

// - Запуск напрямую с NonCancellable: этот Job не реагирует на Job.cancel
fun nonCancellableExample() = runBlocking {
    val job = launch(NonCancellable) {
        repeat(5) { i ->
            println("Iteration $i")
            delay(1000)
        }
        println("Completed")
    }

    delay(2500)
    println("Trying to cancel...")
    job.cancel()       // Запрос на отмену
    job.join()         // NonCancellable игнорирует отмену
    println("Done")
}

// Рекомендуемое применение NonCancellable: критичная очистка в finally
suspend fun performCleanup() {
    try {
        // Основная работа
        doWork()
    } finally {
        // Гарантировать выполнение очистки даже при отмене родителя
        withContext(NonCancellable) {
            saveState()
            closeResources()
        }
    }
}
```

### Случай 3: Нет Кооперации — CPU-интенсивный Цикл

Если длительные вычисления выполняются без точек приостановки и без проверок отмены (`isActive`, `yield()`, `ensureActive()` или других отменяемых `suspend`-функций), корутина не реагирует на отмену, пока цикл не завершится.

```kotlin
import kotlinx.coroutines.*

// - Нет кооперативной отмены: нет точек приостановки и проверок
fun cpuIntensiveNonCooperative() = runBlocking {
    val job = launch {
        var i = 0
        while (i < 1_000_000_000) {
            i++
            // нет suspension point
            // нет isActive / ensureActive / yield
        }
        println("Completed: $i")
    }

    delay(100)
    println("Cancelling...")
    job.cancelAndJoin()  // Запрос на отмену, но цикл не сотрудничает
    println("Done")
}

// - РЕШЕНИЕ 1: проверять isActive
fun cpuIntensiveCooperative1() = runBlocking {
    val job = launch {
        var i = 0
        while (i < 1_000_000_000 && isActive) {
            i++
        }
        println("Completed: $i")
    }

    delay(100)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Done")
}

// - РЕШЕНИЕ 2: периодически вызывать yield()
fun cpuIntensiveCooperative2() = runBlocking {
    val job = launch {
        var i = 0
        while (i < 1_000_000_000) {
            i++
            if (i % 1_000_000 == 0) {
                yield()  // Точка приостановки + проверка отмены
            }
        }
        println("Completed: $i")
    }

    delay(100)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Done")
}

// - РЕШЕНИЕ 3: использовать ensureActive()
fun cpuIntensiveCooperative3() = runBlocking {
    val job = launch {
        var i = 0
        while (i < 1_000_000_000) {
            i++
            if (i % 1_000_000 == 0) {
                ensureActive()  // Бросает CancellationException при отмене
            }
        }
        println("Completed: $i")
    }

    delay(100)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Done")
}
```

### Случай 4: Бесконечный Цикл Без Проверок

Бесконечный цикл без точек приостановки и без проверок отмены (`isActive` и т.п.) не завершится при отмене `Job`.

```kotlin
import kotlinx.coroutines.*

// - Нельзя кооперативно отменить: бесконечный цикл с блокировкой и без проверок
fun infiniteBlockingLoop() = runBlocking {
    val job = launch {
        while (true) {
            println("Working...")
            Thread.sleep(1000)  // Блокирующий вызов: игнорирует отмену корутины
        }
    }

    delay(3000)
    job.cancel()  // Запрос отмены, но цикл не сотрудничает
}

// - РЕШЕНИЕ: использовать delay и isActive
fun infiniteCooperativeLoop() = runBlocking {
    val job = launch {
        while (isActive) {
            println("Working...")
            delay(1000)  // Приостановка + проверка отмены
        }
    }

    delay(3000)
    job.cancelAndJoin()
    println("Cancelled successfully")
}
```

### Случай 5: Блокирующий I/O

Блокирующий ввод-вывод, который не учитывает состояние `Job`, также не будет кооперативно отменяться.

```kotlin
import kotlinx.coroutines.*
import java.io.File

// - Не реагирует на cancel во время блокирующего I/O
fun blockingIO() = runBlocking {
    val job = launch(Dispatchers.IO) {
        val file = File("large_file.txt")
        file.readLines()  // Блокирующее чтение: не учитывает отмену
        println("Read complete")
    }

    delay(100)
    job.cancel()  // Запрос отмены, но readLines завершится полностью
}

// - РЕШЕНИЕ: использовать отменяемый / построчный I/O с проверками
fun interruptibleIO() = runBlocking {
    val job = launch(Dispatchers.IO) {
        File("large_file.txt").useLines { lines ->
            lines.forEach { line ->
                ensureActive()  // Периодическая проверка отмены
                processLine(line)
            }
        }
    }

    delay(100)
    job.cancelAndJoin()
}
```

### Паттерны Кооперации С Отменой

```kotlin
import kotlinx.coroutines.*

// Паттерн 1: свойство isActive
suspend fun cooperativeWork1() = coroutineScope {
    while (isActive) {
        performTask()
    }
}

// Паттерн 2: функция yield()
suspend fun cooperativeWork2() {
    repeat(1000) {
        yield()          // Точка приостановки + проверка отмены
        performTask()
    }
}

// Паттерн 3: функция ensureActive()
suspend fun cooperativeWork3() {
    repeat(1000) {
        ensureActive()   // Бросает при отмене
        performTask()
    }
}

// Паттерн 4: delay() автоматически проверяет отмену
suspend fun cooperativeWork4() {
    repeat(1000) {
        delay(100)       // Проверка отмены
        performTask()
    }
}

// Паттерн 5: отменяемые suspend-функции (из kotlinx.coroutines и др.)
suspend fun cooperativeWork5() {
    repeat(1000) {
        withContext(Dispatchers.Default) {
            performTask()
        }
    }
}
```

### Реальный Пример: Обработка Изображений

```kotlin
import kotlinx.coroutines.*
import android.graphics.Bitmap

// - Некоперативная обработка: долгий блокирующий вызов без проверок
suspend fun processImagesNonCooperative(images: List<Bitmap>) {
    for (image in images) {
        val processed = processImage(image)  // Длительная операция без учёта отмены
        saveImage(processed)
    }
}

// - Кооперативная обработка: проверки между единицами работы
suspend fun processImagesCooperative(images: List<Bitmap>) {
    for (image in images) {
        ensureActive()  // Проверка перед обработкой
        val processed = withContext(Dispatchers.Default) {
            processImage(image)
        }
        ensureActive()  // Проверка перед сохранением
        saveImage(processed)
    }
}

// - Ещё лучше: проверки во время обработки
suspend fun processImageCooperative(image: Bitmap): Bitmap = withContext(Dispatchers.Default) {
    val width = image.width
    val height = image.height
    val result = Bitmap.createBitmap(width, height, image.config)

    for (y in 0 until height) {
        ensureActive()  // Проверка отмены на каждую строку
        for (x in 0 until width) {
            result.setPixel(x, y, processPixel(image.getPixel(x, y)))
        }
    }
    result
}
```

### Try-finally И Отмена

```kotlin
import kotlinx.coroutines.*

// Отмена генерирует CancellationException внутри корутины
suspend fun withCleanup() = coroutineScope {
    val job = launch {
        try {
            repeat(5) { i ->
                println("Step $i")
                delay(1000)
            }
        } catch (e: CancellationException) {
            println("Caught cancellation")
            throw e  // Пробрасываем для корректной пропагации отмены
        } finally {
            println("Cleanup")
        }
    }

    delay(2500)
    job.cancelAndJoin()
}
```

### NonCancellable Для Критичной Очистки

```kotlin
import kotlinx.coroutines.*

suspend fun withCriticalCleanup() = coroutineScope {
    val job = launch {
        try {
            repeat(5) { i ->
                println("Working $i")
                delay(1000)
            }
        } finally {
            // Даже при отмене гарантируем завершение очистки
            withContext(NonCancellable) {
                println("Saving state...")
                delay(500)  // Эта задержка не будет отменена
                println("State saved")
            }
        }
    }

    delay(2500)
    job.cancelAndJoin()
    println("Job fully finished")
}
```

### Тестирование Отмены

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.runTest
import org.junit.Test

class CancellationTest {
    @Test
    fun `cooperative coroutine cancels quickly`() = runTest {
        val job = launch {
            while (isActive) {
                yield()
            }
        }

        job.cancelAndJoin()
        // Корутина быстро завершается, т.к. использует кооперативную отмену
    }

    @Test
    fun `non-cooperative coroutine does not complete until loop ends`() = runTest {
        val job = launch {
            var i = 0
            while (i < 10_000) {  // Ограниченный цикл, чтобы не подвесить тест
                i++               // Нет кооперации внутри тела цикла
            }
        }

        job.cancel()
        job.join()  // Отмена почти не влияет, но цикл конечен, чтобы тест завершился
    }
}
```

### Лучшие Практики

```kotlin
import kotlinx.coroutines.*

class CancellationBestPractices {
    // - DO: использовать delay вместо Thread.sleep в корутинах
    suspend fun good1() {
        delay(1000)  // Проверяет отмену
    }

    // - DON'T: использовать блокирующий sleep в suspend-контекстах без выделенных потоков
    suspend fun bad1() {
        Thread.sleep(1000)  // Игнорирует отмену корутины
    }

    // - DO: проверять isActive в долгих циклах
    suspend fun good2() = coroutineScope {
        while (isActive) {
            doWork()
        }
    }

    // - DON'T: игнорировать отмену в бесконечных циклах
    suspend fun bad2() {
        while (true) {  // Нет проверок отмены
            doWork()
        }
    }

    // - DO: вызывать yield() (или ensureActive()) в CPU-интенсивной работе
    suspend fun good3() {
        repeat(1_000_000) { i ->
            if (i % 1000 == 0) yield()
            compute()
        }
    }

    // - DON'T: длительные CPU-задачи без кооперации
    suspend fun bad3() {
        repeat(1_000_000) {
            compute()  // Без проверок отмены
        }
    }

    // - DO: использовать NonCancellable только для необходимой очистки
    suspend fun good4() {
        try {
            doWork()
        } finally {
            withContext(NonCancellable) {
                cleanup()  // Должно завершиться
            }
        }
    }

    // - DON'T: использовать NonCancellable для обычной бизнес-логики
    suspend fun bad4() {
        withContext(NonCancellable) {
            doWork()  // Не может быть кооперативно отменена
        }
    }
}
```

### Рекомендации (Summary)

| Сценарий                       | Отменяемый? | Комментарий / решение                                   |
|--------------------------------|------------|---------------------------------------------------------|
| `delay()`                      | Да         | Встроенная кооперативная отмена                         |
| `Thread.sleep()`               | Нет        | Использовать `delay()` или отдельные потоки             |
| `while(isActive)`              | Да         | Явная проверка отмены                                   |
| `while(true)` (без проверок)   | Нет        | Добавить `isActive`, `yield()` или `ensureActive()`     |
| `NonCancellable` контекст      | Нет        | По дизайну; только для критичных секций/очистки         |
| CPU-интенсивный с проверками  | Да         | `yield()` / `ensureActive()` / отменяемые вызовы        |
| CPU-интенсивный без проверок  | Нет        | Добавить точки приостановки / проверки отмены           |
| Блокирующий I/O (без проверок)| Нет        | Использовать suspend/I/O + периодические проверки       |

Также см. [[c-kotlin]] и [[c-coroutines]] для общей теории корутин и отмены.

## Answer (EN)

Yes, there are several common cases when normal cooperative cancellation in `kotlinx.coroutines` effectively does not work (the coroutine does not finish in time or at all):

### Case 1: Blocking Code

If blocking operations are used inside a coroutine (e.g. `Thread.sleep()`, long synchronous calls, an endless `while (true) {}` without checks), it does not react to cancellation until control returns to the dispatcher.

```kotlin
import kotlinx.coroutines.*

// - Cannot cancel cooperatively while inside Thread.sleep (blocking)
fun blockingExample() = runBlocking {
    val job = launch {
        try {
            repeat(5) { i ->
                println("Iteration $i")
                Thread.sleep(1000)  // Blocking call: does not check coroutine cancellation
            }
        } finally {
            println("Finally block")
        }
    }

    delay(2500)
    println("Cancelling...")
    job.cancelAndJoin()  // Cancellation is requested, but Thread.sleep cannot be interrupted by coroutine cancel alone
    println("Done")
}

// - SOLUTION: Use delay instead (cooperative)
fun cooperativeExample() = runBlocking {
    val job = launch {
        try {
            repeat(5) { i ->
                println("Iteration $i")
                delay(1000)  // Suspension point - checks cancellation
            }
        } finally {
            println("Finally block")
        }
    }

    delay(2500)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Done")
}
```

### Case 2: NonCancellable Context

If a coroutine or a code block runs in `NonCancellable`, it ignores cancellation signals by design (commonly used in `finally` for guaranteed cleanup).

```kotlin
import kotlinx.coroutines.*

// - Launching directly with NonCancellable: this Job will not respond to Job.cancel
fun nonCancellableExample() = runBlocking {
    val job = launch(NonCancellable) {
        repeat(5) { i ->
            println("Iteration $i")
            delay(1000)
        }
        println("Completed")
    }

    delay(2500)
    println("Trying to cancel...")
    job.cancel()       // Cancellation requested
    job.join()         // But NonCancellable context ignores it
    println("Done")
}

// Recommended use case for NonCancellable: critical cleanup in finally
suspend fun performCleanup() {
    try {
        // Regular work
        doWork()
    } finally {
        // Ensure cleanup completes even if parent is cancelled
        withContext(NonCancellable) {
            saveState()       // Must complete
            closeResources()  // Must complete
        }
    }
}
```

### Case 3: No Cooperation - CPU-Intensive Loop

`Long`-running CPU-intensive loops without suspension points or cancellation checks (`isActive`, `yield()`, `ensureActive()`, or other cancellable suspending calls) effectively do not respond to cancellation.

```kotlin
import kotlinx.coroutines.*

// - Cannot cancel cooperatively - no suspension points or checks
fun cpuIntensiveNonCooperative() = runBlocking {
    val job = launch {
        var i = 0
        while (i < 1_000_000_000) {  // Long-running loop
            i++
            // No suspension point
            // No isActive / ensureActive / yield check
        }
        println("Completed: $i")
    }

    delay(100)
    println("Cancelling...")
    job.cancelAndJoin()  // Cancellation requested but loop doesn't cooperate
    println("Done")
}

// - SOLUTION 1: Check isActive (cooperative polling)
fun cpuIntensiveCooperative1() = runBlocking {
    val job = launch {
        var i = 0
        while (i < 1_000_000_000 && isActive) {  // Check isActive
            i++
        }
        println("Completed: $i")
    }

    delay(100)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Done")
}

// - SOLUTION 2: Call yield() periodically
fun cpuIntensiveCooperative2() = runBlocking {
    val job = launch {
        var i = 0
        while (i < 1_000_000_000) {
            i++
            if (i % 1_000_000 == 0) {
                yield()  // Suspension point + cancellation check
            }
        }
        println("Completed: $i")
    }

    delay(100)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Done")
}

// - SOLUTION 3: Use ensureActive()
fun cpuIntensiveCooperative3() = runBlocking {
    val job = launch {
        var i = 0
        while (i < 1_000_000_000) {
            i++
            if (i % 1_000_000 == 0) {
                ensureActive()  // Throws CancellationException if cancelled
            }
        }
        println("Completed: $i")
    }

    delay(100)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Done")
}
```

### Case 4: Infinite Loop Without Checks

```kotlin
import kotlinx.coroutines.*

// - Cannot cancel cooperatively - infinite loop with blocking and no checks
fun infiniteBlockingLoop() = runBlocking {
    val job = launch {
        while (true) {
            println("Working...")
            Thread.sleep(1000)  // Blocking: ignores coroutine cancellation
        }
    }

    delay(3000)
    job.cancel()  // Cancellation requested, but loop never cooperates
}

// - SOLUTION: Use delay and isActive (cooperative)
fun infiniteCooperativeLoop() = runBlocking {
    val job = launch {
        while (isActive) {
            println("Working...")
            delay(1000)  // Suspending + checks cancellation
        }
    }

    delay(3000)
    job.cancelAndJoin()
    println("Cancelled successfully")
}
```

### Case 5: Blocking I/O

```kotlin
import kotlinx.coroutines.*
import java.io.File

// - Cannot cancel cooperatively during blocking I/O that does not check Job state
fun blockingIO() = runBlocking {
    val job = launch(Dispatchers.IO) {
        val file = File("large_file.txt")
        file.readLines()  // Typical blocking read - does not observe coroutine cancellation
        println("Read complete")
    }

    delay(100)
    job.cancel()  // Cancellation requested, but readLines continues until it returns
}

// - SOLUTION: Use suspending / interruptible I/O + cancellation checks
fun interruptibleIO() = runBlocking {
    val job = launch(Dispatchers.IO) {
        File("large_file.txt").useLines { lines ->
            lines.forEach { line ->
                ensureActive()  // Check cancellation periodically
                processLine(line)
            }
        }
    }

    delay(100)
    job.cancelAndJoin()
}
```

### Cancellation Cooperation Patterns

```kotlin
import kotlinx.coroutines.*

// Pattern 1: isActive property
suspend fun cooperativeWork1() = coroutineScope {
    while (isActive) {
        performTask()
    }
}

// Pattern 2: yield() function
suspend fun cooperativeWork2() {
    repeat(1000) {
        yield()          // Suspension point + cancellation check
        performTask()
    }
}

// Pattern 3: ensureActive() function
suspend fun cooperativeWork3() {
    repeat(1000) {
        ensureActive()   // Throws if cancelled
        performTask()
    }
}

// Pattern 4: delay() naturally checks
suspend fun cooperativeWork4() {
    repeat(1000) {
        delay(100)       // Checks cancellation automatically
        performTask()
    }
}

// Pattern 5: Cancellable suspend functions (including many from kotlinx.coroutines)
suspend fun cooperativeWork5() {
    repeat(1000) {
        withContext(Dispatchers.Default) {
            performTask()
        }
    }
}
```

### Real-World Example: Image Processing

```kotlin
import kotlinx.coroutines.*
import android.graphics.Bitmap

// - Non-cooperative image processing (blocking, no checks)
suspend fun processImagesNonCooperative(images: List<Bitmap>) {
    for (image in images) {
        val processed = processImage(image)  // Long blocking operation; does not observe Job cancellation
        saveImage(processed)
    }
}

// - Cooperative image processing (checks between units of work)
suspend fun processImagesCooperative(images: List<Bitmap>) {
    for (image in images) {
        ensureActive()  // Check before processing each image
        val processed = withContext(Dispatchers.Default) {
            processImage(image)
        }
        ensureActive()  // Check before saving
        saveImage(processed)
    }
}

// - Even better: Check during processing
suspend fun processImageCooperative(image: Bitmap): Bitmap = withContext(Dispatchers.Default) {
    val width = image.width
    val height = image.height
    val result = Bitmap.createBitmap(width, height, image.config)

    for (y in 0 until height) {
        ensureActive()  // Check cancellation every row
        for (x in 0 until width) {
            result.setPixel(x, y, processPixel(image.getPixel(x, y)))
        }
    }
    result
}
```

### Try-finally with Cancellation

```kotlin
import kotlinx.coroutines.*

// Cancellation throws CancellationException inside the coroutine
suspend fun withCleanup() = coroutineScope {
    val job = launch {
        try {
            repeat(5) { i ->
                println("Step $i")
                delay(1000)
            }
        } catch (e: CancellationException) {
            println("Caught cancellation")
            throw e  // Rethrow to propagate cancellation
        } finally {
            println("Cleanup")
        }
    }

    delay(2500)
    job.cancelAndJoin()
}
```

### NonCancellable for Critical Cleanup

```kotlin
import kotlinx.coroutines.*

suspend fun withCriticalCleanup() = coroutineScope {
    val job = launch {
        try {
            repeat(5) { i ->
                println("Working $i")
                delay(1000)
            }
        } finally {
            // Even if cancelled, complete cleanup
            withContext(NonCancellable) {
                println("Saving state...")
                delay(500)  // This delay won't be cancelled
                println("State saved")
            }
        }
    }

    delay(2500)
    job.cancelAndJoin()
    println("Job fully finished")
}
```

### Testing Cancellation

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.runTest
import org.junit.Test

class CancellationTest {
    @Test
    fun `cooperative coroutine cancels quickly`() = runTest {
        val job = launch {
            while (isActive) {
                yield()
            }
        }

        job.cancelAndJoin()
        // Test completes quickly because coroutine cooperates with cancellation
    }

    @Test
    fun `non-cooperative coroutine does not complete until loop ends`() = runTest {
        val job = launch {
            var i = 0
            while (i < 10_000) {  // Bounded loop to avoid hanging the test
                i++               // No cooperation inside loop body
            }
        }

        job.cancel()
        job.join()  // Cancellation has little effect because loop ignores it, but loop is finite to keep test safe
    }
}
```

### Best Practices

```kotlin
import kotlinx.coroutines.*

class CancellationBestPractices {
    // - DO: Use delay instead of Thread.sleep in coroutines
    suspend fun good1() {
        delay(1000)  // Checks cancellation
    }

    // - DON'T: Use blocking sleep in suspend contexts unless on dedicated threads
    suspend fun bad1() {
        Thread.sleep(1000)  // Ignores coroutine cancellation
    }

    // - DO: Check isActive in long-running loops
    suspend fun good2() = coroutineScope {
        while (isActive) {
            doWork()
        }
    }

    // - DON'T: Ignore cancellation in infinite loops
    suspend fun bad2() {
        while (true) {  // No cancellation checks
            doWork()
        }
    }

    // - DO: Call yield() (or ensureActive()) in CPU-intensive work
    suspend fun good3() {
        repeat(1_000_000) { i ->
            if (i % 1000 == 0) yield()
            compute()
        }
    }

    // - DON'T: Long running CPU work without cooperation
    suspend fun bad3() {
        repeat(1_000_000) {
            compute()  // No cancellation checks
        }
    }

    // - DO: Use NonCancellable only for necessary cleanup
    suspend fun good4() {
        try {
            doWork()
        } finally {
            withContext(NonCancellable) {
                cleanup()  // Must complete
            }
        }
    }

    // - DON'T: Use NonCancellable for regular business logic
    suspend fun bad4() {
        withContext(NonCancellable) {
            doWork()  // Cannot be cancelled cooperatively
        }
    }
}
```

### Summary

| Scenario                    | Cancellable? | Notes / Solution                                     |
|----------------------------|-------------|------------------------------------------------------|
| `delay()`                  | Yes         | Built-in cooperative cancellation                    |
| `Thread.sleep()`           | No          | Use `delay()` or dedicated threads instead           |
| `while(isActive)`          | Yes         | Explicitly checks cancellation                       |
| `while(true)` (no checks)  | No          | Add `isActive`, `yield()`, or `ensureActive()`       |
| `NonCancellable` context   | No          | By design; reserve for cleanup/critical sections     |
| CPU-intensive with checks  | Yes         | Use `yield()` / `ensureActive()` / cancellable calls |
| CPU-intensive w/o checks   | No          | Add suspension points or cancellation checks         |
| Blocking I/O (no checks)   | No          | Use suspending/interruptible I/O + periodic checks   |

Also see [[c-kotlin]] and [[c-coroutines]] for coroutine and cancellation basics.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия механизма отмены корутин от потоков в Java?
- Когда на практике вы бы использовали эти паттерны кооперативной отмены?
- Какие типичные ошибки при работе с отменой корутин стоит избегать?

## Follow-ups

- What are the key differences between coroutine cancellation and Java thread interruption?
- When would you use these cooperative cancellation patterns in practice?
- What are common pitfalls with coroutine cancellation to avoid?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-coroutines]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-coroutines]]

## Связанные Вопросы (RU)

- [[q-how-suspend-function-detects-suspension--kotlin--hard]]

## Related Questions

- [[q-how-suspend-function-detects-suspension--kotlin--hard]]
