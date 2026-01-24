---
anki_cards:
- slug: q-coroutine-resource-cleanup--kotlin--medium-0-en
  language: en
  anki_id: 1768326291780
  synced_at: '2026-01-23T17:03:51.525425'
- slug: q-coroutine-resource-cleanup--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326291806
  synced_at: '2026-01-23T17:03:51.526279'
---
# Question (EN)
> How do you ensure proper resource cleanup when a coroutine is cancelled?
## Ответ (RU)

**Очистка ресурсов в корутинах** требует тщательной обработки, потому что отмена является кооперативной и асинхронной. Паттерн `try-finally` и контекст `NonCancellable` — ключевые инструменты для обеспечения правильного освобождения ресурсов.

### Проблема: Ресурсы и Отмена

```kotlin
// - ПРОБЛЕМА: Утечка ресурсов при отмене
val job = lifecycleScope.launch {
    val file = File("data.txt").outputStream()

    // Если отменено здесь, файл никогда не закроется!
    repeat(1000) { i ->
        file.write("Line $i\n".toByteArray())
        delay(100)
    }

    file.close() // Никогда не достигается при отмене!
}

// Предполагается вызов внутри suspend-функции или корутины
delay(500)
job.cancel() // Файл остается открытым → утечка ресурсов!
```

**Проблемы**:
- Файловый дескриптор не закрыт
- Утечка памяти
- Исчерпание ресурсов ОС
- Возможное повреждение данных

### Решение 1: Паттерн try-finally (Обязательно)

**Базовый паттерн**: Используйте `try-finally` для гарантированной очистки.

Важно: сам блок `finally` выполняется всегда, но если внутри него есть приостанавливающиеся вызовы, они могут быть отменены. Для критически важной приостанавливающейся очистки используйте `NonCancellable` (см. ниже).

```kotlin
// - ХОРОШО: Гарантированная очистка
val job = lifecycleScope.launch {
    val file = File("data.txt").outputStream()

    try {
        repeat(1000) { i ->
            file.write("Line $i\n".toByteArray())
            delay(100) // Отмена может произойти здесь
        }
    } finally {
        // ВСЕГДА выполняется в этой корутине, даже при отмене
        file.close()
        println("Файл закрыт")
    }
}

// Предполагается вызов внутри suspend-функции или корутины
delay(500)
job.cancel() // Файл корректно закрыт!
job.join()   // Ждем завершения очистки
```

**Как это работает**:
1. Корутина начинает запись в файл.
2. Вызывается `cancel()`.
3. В следующей точке приостановки (`delay(100)`) обнаруживается отмена.
4. Выбрасывается `CancellationException`.
5. Выполняется блок `finally` → файл закрыт.
6. Корутина завершается.

### Решение 2: Расширение use() (Автоматическая очистка)

**`use()` из Kotlin**: Автоматически закрывает ресурсы `Closeable`.

```kotlin
// - ЛУЧШЕ ВСЕГО: Автоматическое управление ресурсами
val job = lifecycleScope.launch {
    File("data.txt").outputStream().use { file ->
        repeat(1000) { i ->
            file.write("Line $i\n".toByteArray())
            delay(100)
        }
    } // Автоматически закрывается здесь, даже при отмене
}

// Предполагается вызов внутри suspend-функции или корутины
delay(500)
job.cancel()
job.join()
```

**Преимущества**:
- Лаконичный, идиоматичный Kotlin
- Обрабатывает исключения автоматически
- Работает с любым `Closeable` ресурсом
- Эквивалентно `try-finally`, но чище

### Решение 3: Контекст NonCancellable (Очистка должна завершиться)

**Проблема**: Код очистки, который приостанавливается, может быть отменен.

```kotlin
// - ПРОБЛЕМА: Сама очистка может быть отменена
val job = lifecycleScope.launch {
    val connection = openDatabaseConnection()

    try {
        performDatabaseOperations()
    } finally {
        // Если очистка занимает время и приостанавливается...
        delay(1000) // Очистка может быть прервана, соединение не закрыто
        connection.close()
    }
}

job.cancel()
```

**Решение**: Используйте контекст `NonCancellable` для приостанавливающейся очистки.

```kotlin
// - ХОРОШО: Очистка не может быть отменена
val job = lifecycleScope.launch {
    val connection = openDatabaseConnection()

    try {
        performDatabaseOperations()
    } finally {
        withContext(NonCancellable) {
            // Этот блок не может быть отменен
            delay(1000) // Выполняется до конца
            connection.close()
            println("Очистка завершена")
        }
    }
}

job.cancel()
job.join() // Ждем завершения блока NonCancellable
```

**Когда использовать NonCancellable**:
- Очистка требует приостанавливающих функций
- Необходимо отправить логи краша
- Необходимо сохранить критическое состояние
- Транзакции базы данных должны завершиться

### Резюме

**Очистка ресурсов в корутинах**:
- **try-finally**: гарантированная очистка при отмене
- **use()**: автоматическая очистка для `Closeable` ресурсов
- **NonCancellable**: очистка, которую нельзя прервать, если она приостанавливается
- **job.join()**: ждать завершения очистки после отмены
- **Вложенная очистка**: корректно обрабатывать несколько ресурсов
- **Перебрасывать CancellationException**: не проглатывать его

**Ключевой паттерн**:
```kotlin
// Внутри подходящего CoroutineScope
launch {
    resource.use { res ->
        // Работа с ресурсом
    }
} // Ресурс всегда очищен

// Или с try-finally и NonCancellable:
launch {
    try {
        work()
    } finally {
        withContext(NonCancellable) {
            cleanup() // Не может быть отменено
        }
    }
}
```

---

## Answer (EN)

**Resource cleanup in coroutines** requires careful handling because cancellation is cooperative and asynchronous. The `try-finally` pattern and `NonCancellable` context are key tools for ensuring resources are properly released.

### The Problem: Resources and Cancellation

```kotlin
// - PROBLEM: Resource leak on cancellation
val job = lifecycleScope.launch {
    val file = File("data.txt").outputStream()

    // If cancelled here, file is never closed!
    repeat(1000) { i ->
        file.write("Line $i\n".toByteArray())
        delay(100)
    }

    file.close() // Never reached if cancelled!
}

// Intended to be called from a suspend function or coroutine
delay(500)
job.cancel() // File remains open → resource leak!
```

**Issues**:
- File handle not closed
- Memory leak
- OS resource exhaustion
- Possible data corruption

### Solution 1: try-finally Pattern (Essential)

**Basic pattern**: Use `try-finally` to guarantee cleanup.

Note: The `finally` block itself always runs for that coroutine, but any suspending calls inside it are still cancellation-aware. For critical suspending cleanup, wrap it in `NonCancellable`.

```kotlin
// - GOOD: Guaranteed cleanup
val job = lifecycleScope.launch {
    val file = File("data.txt").outputStream()

    try {
        repeat(1000) { i ->
            file.write("Line $i\n".toByteArray())
            delay(100) // Cancellation can happen here
        }
    } finally {
        // ALWAYS runs in this coroutine, even if cancelled
        file.close()
        println("File closed")
    }
}

// Intended to be called from a suspend function or coroutine
delay(500)
job.cancel() // File is properly closed!
job.join()   // Wait for cleanup to complete
```

**How It Works**:
1. `Coroutine` starts writing to file.
2. `cancel()` is called.
3. At next suspension point (`delay(100)`), cancellation is detected.
4. `CancellationException` is thrown.
5. `finally` block executes → file closed.
6. `Coroutine` terminates.

### Solution 2: use() Extension (Automatic Cleanup)

**Kotlin's `use()`**: Automatically closes `Closeable` resources.

```kotlin
// - BEST: Automatic resource management
val job = lifecycleScope.launch {
    File("data.txt").outputStream().use { file ->
        repeat(1000) { i ->
            file.write("Line $i\n".toByteArray())
            delay(100)
        }
    } // Automatically closed here, even if cancelled
}

// Intended to be called from a suspend function or coroutine
delay(500)
job.cancel()
job.join()
```

**Benefits**:
- Concise, idiomatic Kotlin
- Handles exceptions automatically
- Works with any `Closeable` resource
- Equivalent to `try-finally` but cleaner

### Solution 3: NonCancellable Context (Cleanup Must Complete)

**Problem**: Cleanup code that suspends can be cancelled.

```kotlin
// - PROBLEM: Cleanup itself can be cancelled
val job = lifecycleScope.launch {
    val connection = openDatabaseConnection()

    try {
        performDatabaseOperations()
    } finally {
        // If cleanup takes time and suspends...
        delay(1000) // Cleanup may be cancelled, connection not closed
        connection.close()
    }
}

job.cancel()
```

**Solution**: Use `NonCancellable` context for suspending cleanup.

```kotlin
// - GOOD: Cleanup cannot be cancelled
val job = lifecycleScope.launch {
    val connection = openDatabaseConnection()

    try {
        performDatabaseOperations()
    } finally {
        withContext(NonCancellable) {
            // This block CANNOT be cancelled
            delay(1000) // Runs to completion
            connection.close()
            println("Cleanup completed")
        }
    }
}

job.cancel()
job.join() // Waits for NonCancellable block to finish
```

**When to Use NonCancellable**:
- Cleanup requires suspending functions
- Must upload crash logs
- Must save critical state
- `Database` transactions must complete

### Solution 4: Multiple Resources

**Pattern**: Nested `try-finally` or multiple `use` blocks.

```kotlin
// - GOOD: Multiple resources with use()
val job = lifecycleScope.launch {
    FileInputStream("input.txt").use { input ->
        FileOutputStream("output.txt").use { output ->
            // Both files automatically closed
            input.copyTo(output)
        }
    }
}

// - GOOD: Multiple resources with nested try-finally
val job = lifecycleScope.launch {
    val input = FileInputStream("input.txt")
    try {
        val output = FileOutputStream("output.txt")
        try {
            input.copyTo(output)
        } finally {
            output.close()
        }
    } finally {
        input.close()
    }
}
```

### Solution 5: Custom Resource Management

**Pattern**: Create custom resource holder with cleanup.

```kotlin
// Custom resource with guaranteed cleanup
class DatabaseConnection : Closeable {
    private val connection = openRawConnection()

    suspend fun executeQuery(sql: String): List<Row> {
        // Assume this is a suspending or non-blocking call in real code
        return connection.query(sql)
    }

    override fun close() {
        connection.close()
        println("Database connection closed")
    }
}

// Usage with automatic cleanup
suspend fun performDatabaseWork() {
    DatabaseConnection().use { db ->
        val results = db.executeQuery("SELECT * FROM users")
        delay(1000) // Can be cancelled here
        processResults(results)
    } // Always closed
}
```

### Real-World Example: Network + Database

```kotlin
class DataSyncViewModel : ViewModel() {
    fun syncData() {
        viewModelScope.launch {
            val database = AppDatabase.getInstance()
            val networkClient = NetworkClient()

            try {
                // Fetch from network
                val remoteData = networkClient.fetchData()

                // Save to database
                database.userDao().insertAll(remoteData)

            } finally {
                withContext(NonCancellable) {
                    // Ensure cleanup even if cancelled
                    networkClient.close()
                    println("Network client closed")
                }
            }
        }
    }
}
```

### Solution 6: Cancellation-Aware Cleanup

**Pattern**: Ensure all acquired resources are cleaned up, even on cancellation.

```kotlin
val job = lifecycleScope.launch {
    val resources = mutableListOf<Resource>()

    try {
        // Acquire multiple resources
        repeat(10) { i ->
            resources.add(acquireResource(i))
            delay(100)
        }
    } finally {
        // Clean up all acquired resources
        resources.forEach { resource ->
            try {
                resource.close()
            } catch (e: Exception) {
                // Log but don't fail cleanup
                println("Error closing resource: $e")
            }
        }
    }
}
```

### Common Patterns

**Pattern 1: File Operations**:
```kotlin
// - Reading file with cleanup
suspend fun readFile(path: String): String {
    return File(path).inputStream().use { stream ->
        stream.bufferedReader().use { reader ->
            reader.readText()
        }
    }
}

// - Writing file with cleanup
suspend fun writeFile(path: String, content: String) {
    File(path).outputStream().use { stream ->
        stream.bufferedWriter().use { writer ->
            writer.write(content)
        }
    }
}
```

**Pattern 2: Network Connections**:
```kotlin
// - HTTP request with cleanup
suspend fun fetchData(url: String): String {
    val connection = URL(url).openConnection() as HttpURLConnection

    return try {
        connection.inputStream.use { stream ->
            stream.bufferedReader().use { reader ->
                reader.readText()
            }
        }
    } finally {
        connection.disconnect()
    }
}
```

**Pattern 3: Locks and Mutexes**:
```kotlin
val mutex = Mutex()

suspend fun criticalSection() {
    mutex.lock()
    try {
        // Critical code
        performCriticalOperation()
    } finally {
        mutex.unlock() // Always unlock
    }
}

// Or use withLock (automatic)
suspend fun criticalSectionClean() {
    mutex.withLock {
        performCriticalOperation()
    } // Automatically unlocked
}
```

### Handling CancellationException

```kotlin
val job = lifecycleScope.launch {
    val resource = acquireResource()

    try {
        performWork(resource)
    } catch (e: CancellationException) {
        // Log cancellation if needed
        println("Work cancelled")
        // Re-throw to propagate cancellation
        throw e
    } catch (e: Exception) {
        // Handle other errors
        handleError(e)
    } finally {
        // Cleanup runs regardless
        resource.close()
    }
}
```

In general, do not swallow `CancellationException` without rethrowing, or you may break structured cancellation semantics.

### Best Practices

```kotlin
// - DO: Use use() for Closeable resources
file.use { it.write(data) }

// - DO: Use try-finally for cleanup
try {
    work()
} finally {
    cleanup()
}

// - DO: Use NonCancellable for critical suspending cleanup
finally {
    withContext(NonCancellable) {
        criticalCleanup()
    }
}

// - DO: Close resources in reverse order of acquisition
try {
    val r1 = acquire1()
    try {
        val r2 = acquire2()
        try {
            work(r1, r2)
        } finally { r2.close() }
    } finally { r1.close() }
}

// - DON'T: Forget cleanup code
val file = openFile()
work(file) // If cancelled, file not closed!

// - DON'T: Swallow CancellationException in cleanup
catch (e: CancellationException) {
    // Don't ignore it — rethrow to propagate cancellation when appropriate
    throw e
}

// - DON'T: Perform long suspending operations in finally without NonCancellable
finally {
    // This can be cancelled; use NonCancellable if it must complete
    delay(5000)
    cleanup()
}
```

### Testing Resource Cleanup

```kotlin
class FileProcessorTest {
    @Test
    fun `resource closed on cancellation`() = runTest {
        val file = mockk<FileOutputStream>()
        every { file.close() } just Runs

        val job = launch {
            try {
                useFile(file)
            } finally {
                file.close()
            }
        }

        // Cancel and wait
        job.cancelAndJoin()

        // Verify cleanup happened
        verify { file.close() }
    }
}
```

### Summary

**Resource Cleanup in Coroutines**:
- **try-finally**: Guaranteed cleanup on cancellation
- **use()**: Automatic cleanup for `Closeable` resources
- **NonCancellable**: Cleanup that cannot be interrupted when it suspends
- **job.join()**: Wait for cleanup to complete after cancel
- **Nested cleanup**: Handle multiple resources correctly
- **Re-throw CancellationException**: Don't swallow it

**Key Pattern**:
```kotlin
// Inside an appropriate CoroutineScope
launch {
    resource.use { res ->
        // Work with resource
    }
} // Always cleaned up

// Or with try-finally and NonCancellable:
launch {
    try {
        work()
    } finally {
        withContext(NonCancellable) {
            cleanup() // Cannot be cancelled
        }
    }
}
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Cancellation and Timeouts - Kotlin Docs](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [use() function - Kotlin Standard Library](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.io/use.html)
- [NonCancellable - kotlinx.coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-non-cancellable/)

---

**Source**: Kotlin Coroutines Interview Questions for Android Developers PDF

## Related Questions

- [[q-data-class-requirements--kotlin--medium]]
- [[q-channel-buffer-strategies-comparison--kotlin--hard]]
- [[q-statein-sharein-flow--kotlin--medium]]
