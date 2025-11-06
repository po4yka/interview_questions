---
id: kotlin-051
title: "Coroutine Cancellation Cooperation / Кооперативная отмена корутин"
aliases: ["Coroutine Cancellation Cooperation, Кооперативная отмена корутин"]

# Classification
topic: kotlin
subtopics: [cancellation, cooperation, coroutines]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Phase 1 Coroutines & Flow Advanced Questions

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-coroutine-cancellation-mechanisms--kotlin--medium, q-kotlin-coroutines-introduction--kotlin--medium]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [cancellation, cooperation, coroutines, difficulty/medium, ensureActive, kotlin, yield]
---
# Вопрос (RU)
> Реализуйте долгоиграющие операции с поддержкой отмены. Правильно используйте yield(), ensureActive() и isActive. Корректно обрабатывайте CancellationException.

---

# Question (EN)
> Implement cancellation-aware long-running operations. Use yield(), ensureActive(), and isActive properly. Handle CancellationException correctly.

## Ответ (RU)

Отмена корутин **кооперативная** - корутины должны проверять отмену и реагировать соответственно.

### Методы Проверки Отмены

#### 1. ensureActive()

Бросает `CancellationException` сразу если корутина отменена.

```kotlin
suspend fun processData(items: List<Item>) {
    for (item in items) {
        ensureActive() // Бросает если отменено
        processItem(item)
    }
}
```

#### 2. yield()

Приостанавливает и проверяет отмену, дает другим корутинам шанс выполниться.

```kotlin
suspend fun heavyComputation(data: List<Int>): Int {
    var result = 0
    for (value in data) {
        yield() // Кооперативная отмена + многозадачность
        result += calculate(value)
    }
    return result
}
```

#### 3. isActive Свойство

```kotlin
launch {
    while (isActive) {
        val data = fetchData()
        processData(data)
        delay(1000)
    }
}
```

### Обработка CancellationException

```kotlin
//  Правильно - перебросить CancellationException
try {
    doWork()
} catch (e: CancellationException) {
    cleanup()
    throw e // ОБЯЗАТЕЛЬНО перебросить!
} catch (e: Exception) {
    handleError(e)
}

//  Неправильно - проглатывает отмену
try {
    doWork()
} catch (e: Exception) { // Ловит CancellationException!
    log(e)
}
```

### NonCancellable Context

```kotlin
try {
    doWork()
} finally {
    withContext(NonCancellable) {
        // Можем вызывать suspend функции
        closeConnection()
        saveState()
    }
}
```

### Реальные Примеры

#### Обработка Изображений

```kotlin
suspend fun processImages(images: List<Image>): List<ProcessedImage> {
    val results = mutableListOf<ProcessedImage>()

    for ((index, image) in images.withIndex()) {
        ensureActive() // Проверка отмены

        if (index % 10 == 0) {
            yield() // Дать другим корутинам поработать
        }

        val processed = processImage(image)
        results.add(processed)
    }

    return results
}
```

#### Сетевой Запрос С Очисткой

```kotlin
suspend fun fetchData(endpoint: String): Data {
    val connection = openConnection(endpoint)

    try {
        return connection.read()
    } catch (e: CancellationException) {
        println("Запрос отменен")
        throw e
    } finally {
        withContext(NonCancellable) {
            connection.close()
        }
    }
}
```

#### Фоновая Синхронизация

```kotlin
suspend fun startSync() = coroutineScope {
    while (isActive) {
        try {
            syncData()
        } catch (e: CancellationException) {
            println("Синхронизация отменена")
            throw e
        }

        delay(60_000)
    }
}
```

### Лучшие Практики

1. **Всегда проверяйте отмену в циклах**:
   ```kotlin
   while (isActive) {
       doWork()
   }
   ```

2. **Используйте yield() в CPU-intensive коде**:
   ```kotlin
   repeat(1000000) {
       yield()
       calculate()
   }
   ```

3. **Всегда перебрасывайте CancellationException**:
   ```kotlin
   catch (e: CancellationException) {
       cleanup()
       throw e
   }
   ```

4. **Используйте NonCancellable для критичной очистки**:
   ```kotlin
   finally {
       withContext(NonCancellable) {
           saveState()
       }
   }
   ```

### Распространенные Ошибки

1. **Не проверка отмены**:
   ```kotlin
   //  Нельзя отменить
   while (true) { doWork() }

   //  Можно отменить
   while (isActive) { doWork() }
   ```

2. **Проглатывание CancellationException**:
   ```kotlin
   //  Ломает отмену
   try { doWork() }
   catch (e: Exception) { log(e) }

   //  Сохранить отмену
   catch (e: Exception) {
       if (e is CancellationException) throw e
       log(e)
   }
   ```

**Краткое содержание**: Отмена корутин кооперативная - корутины должны проверять отмену используя ensureActive(), yield() или isActive. Используйте ensureActive() для быстрых проверок, yield() для CPU-intensive циклов, isActive в while условиях. Всегда перебрасывайте CancellationException после очистки. Используйте NonCancellable для критичных операций очистки. Проверяйте отмену периодически в долгоиграющих операциях.

---

## Answer (EN)

Coroutine cancellation is **cooperative** - coroutines must check for cancellation and respond appropriately. Non-cooperative coroutines can't be cancelled.

### Why Cancellation is Cooperative

```kotlin
//  Non-cooperative - cannot be cancelled
val job = launch {
    var i = 0
    while (i < 1000000) {
        i++
        // Never checks cancellation!
    }
}

delay(100)
job.cancel() // Has no effect - coroutine continues!
job.join()
println("Job still running...")

//  Cooperative - can be cancelled
val job = launch {
    var i = 0
    while (i < 1000000) {
        ensureActive() // Check cancellation
        i++
    }
}

delay(100)
job.cancel()
job.join()
println("Job cancelled successfully")
```

### Cancellation Check Methods

#### 1. ensureActive()

Throws `CancellationException` immediately if coroutine is cancelled.

```kotlin
suspend fun processData(items: List<Item>) {
    for (item in items) {
        ensureActive() // Throws if cancelled
        processItem(item)
    }
}

// Usage
val job = launch {
    try {
        processData(largeList)
    } catch (e: CancellationException) {
        println("Processing cancelled")
        throw e // Must re-throw!
    }
}

delay(100)
job.cancelAndJoin()
```

#### 2. yield()

Suspends and checks cancellation, giving other coroutines chance to run.

```kotlin
suspend fun heavyComputation(data: List<Int>): Int {
    var result = 0
    for (value in data) {
        yield() // Cooperative cancellation + cooperative multitasking
        result += complexCalculation(value)
    }
    return result
}
```

**yield() vs ensureActive()**:
- `yield()` - Suspends, checks cancellation, allows other coroutines to run
- `ensureActive()` - Just checks cancellation, doesn't suspend

```kotlin
// yield() is more "polite" in CPU-intensive loops
launch {
    repeat(1000) {
        yield() // Let other coroutines run
        cpuIntensiveWork()
    }
}

// ensureActive() is lighter for quick checks
launch {
    for (item in items) {
        ensureActive() // Just check, don't suspend
        quickOperation(item)
    }
}
```

#### 3. isActive Property

Boolean flag to check if coroutine is still active.

```kotlin
suspend fun processLargeFile(file: File) {
    file.forEachLine { line ->
        if (!isActive) {
            println("Processing cancelled")
            return // Exit early
        }
        processLine(line)
    }
}

// Or use in while loop
launch {
    while (isActive) {
        val data = fetchData()
        processData(data)
        delay(1000)
    }
    println("Stopped gracefully")
}
```

### Handling CancellationException

`CancellationException` is special - it must be re-thrown after cleanup.

```kotlin
//  Correct - re-throw CancellationException
suspend fun downloadFile(url: String): File = coroutineScope {
    val tempFile = createTempFile()

    try {
        val data = fetchData(url)
        tempFile.writeBytes(data)
        tempFile
    } catch (e: CancellationException) {
        // Cleanup resources
        tempFile.delete()
        println("Download cancelled, cleaned up temp file")
        throw e // MUST re-throw!
    } catch (e: Exception) {
        tempFile.delete()
        throw e
    }
}

//  Wrong - swallows CancellationException
suspend fun broken() {
    try {
        doWork()
    } catch (e: Exception) { // Catches CancellationException!
        println("Error: $e")
        // Not re-thrown - breaks cancellation!
    }
}
```

### NonCancellable Context

Sometimes you need to perform cleanup even after cancellation:

```kotlin
suspend fun processWithCleanup() {
    try {
        doWork()
    } finally {
        // This block runs even on cancellation
        // But suspending functions will throw CancellationException!

        withContext(NonCancellable) {
            // Now we can call suspending functions
            closeConnection()
            saveState()
            println("Cleanup complete")
        }
    }
}
```

### Real-World Examples

#### Example 1: Image Processing

```kotlin
class ImageProcessor {
    suspend fun processImages(images: List<Image>): List<ProcessedImage> {
        val results = mutableListOf<ProcessedImage>()

        for ((index, image) in images.withIndex()) {
            // Check cancellation periodically
            ensureActive()

            // Progress reporting
            if (index % 10 == 0) {
                yield() // Let other coroutines run
                println("Processed $index/${images.size}")
            }

            val processed = processImage(image)
            results.add(processed)
        }

        return results
    }

    private suspend fun processImage(image: Image): ProcessedImage {
        // CPU-intensive work
        repeat(1000) {
            yield() // Cooperative cancellation in tight loop
            // ... heavy computation ...
        }
        return ProcessedImage(image)
    }
}

// Usage with cancellation
val job = launch {
    try {
        val results = processor.processImages(largeImageList)
        displayResults(results)
    } catch (e: CancellationException) {
        println("Image processing cancelled")
        throw e
    }
}

// Cancel if user navigates away
delay(5000)
job.cancel()
```

#### Example 2: Network Request with Timeout and Cleanup

```kotlin
class ApiClient {
    private var activeConnections = 0

    suspend fun fetchData(endpoint: String): Data {
        activeConnections++
        val connection = openConnection(endpoint)

        try {
            return withTimeout(5000) {
                connection.read()
            }
        } catch (e: TimeoutCancellationException) {
            println("Request timed out")
            throw e
        } catch (e: CancellationException) {
            println("Request cancelled")
            throw e
        } catch (e: Exception) {
            println("Request failed: ${e.message}")
            throw e
        } finally {
            // Cleanup even on cancellation
            withContext(NonCancellable) {
                connection.close()
                activeConnections--
                println("Connection closed, active: $activeConnections")
            }
        }
    }
}
```

#### Example 3: Database Migration

```kotlin
class DatabaseMigrator {
    suspend fun migrateData(
        records: List<Record>,
        onProgress: (Int, Int) -> Unit
    ) {
        var migratedCount = 0
        val errors = mutableListOf<MigrationError>()

        for (record in records) {
            // Check cancellation
            if (!isActive) {
                println("Migration cancelled at record $migratedCount")
                rollback(migratedCount)
                return
            }

            try {
                migrateRecord(record)
                migratedCount++

                // Progress update
                if (migratedCount % 100 == 0) {
                    onProgress(migratedCount, records.size)
                    yield() // Let other work happen
                }
            } catch (e: Exception) {
                errors.add(MigrationError(record.id, e))
            }
        }

        if (errors.isNotEmpty()) {
            println("Migration completed with ${errors.size} errors")
        } else {
            println("Migration successful: $migratedCount records")
        }
    }

    private suspend fun rollback(count: Int) {
        withContext(NonCancellable) {
            println("Rolling back $count records...")
            // Rollback logic
        }
    }
}
```

#### Example 4: Periodic Background Task

```kotlin
class BackgroundSync {
    suspend fun startSync() = coroutineScope {
        while (isActive) {
            try {
                syncData()
                println("Sync complete")
            } catch (e: CancellationException) {
                println("Sync cancelled")
                throw e
            } catch (e: Exception) {
                println("Sync error: ${e.message}")
                // Continue on error
            }

            // Wait for next cycle
            delay(60_000) // Will throw if cancelled
        }
    }

    private suspend fun syncData() {
        val data = fetchRemoteData()

        // Process in chunks with cancellation checks
        data.chunked(100).forEach { chunk ->
            ensureActive() // Check before each chunk
            saveToDatabase(chunk)
        }
    }
}

// Usage
val syncJob = launch {
    backgroundSync.startSync()
}

// Stop sync when app goes to background
onPause {
    syncJob.cancel()
}
```

### Best Practices

1. **Always check cancellation in loops**:
   ```kotlin
   //  Cancellable
   while (isActive) {
       doWork()
   }

   // Or
   for (item in items) {
       ensureActive()
       process(item)
   }
   ```

2. **Use yield() in CPU-intensive code**:
   ```kotlin
   repeat(1000000) {
       yield() // Cooperative cancellation + multitasking
       heavyCalculation()
   }
   ```

3. **Always re-throw CancellationException**:
   ```kotlin
   try {
       operation()
   } catch (e: CancellationException) {
       cleanup()
       throw e // MUST re-throw!
   }
   ```

4. **Use NonCancellable for critical cleanup**:
   ```kotlin
   finally {
       withContext(NonCancellable) {
           saveState()
           closeResources()
       }
   }
   ```

5. **Check cancellation periodically**:
   ```kotlin
   // Every 100 iterations
   for ((index, item) in items.withIndex()) {
       if (index % 100 == 0) {
           ensureActive()
       }
       process(item)
   }
   ```

### Common Pitfalls

1. **Never checking cancellation**:
   ```kotlin
   //  Cannot be cancelled
   while (true) {
       doWork()
   }

   //  Cancellable
   while (isActive) {
       doWork()
   }
   ```

2. **Swallowing CancellationException**:
   ```kotlin
   //  Breaks cancellation
   try {
       doWork()
   } catch (e: Exception) {
       log(e) // Catches CancellationException!
   }

   //  Preserve cancellation
   try {
       doWork()
   } catch (e: Exception) {
       if (e is CancellationException) throw e
       log(e)
   }
   ```

3. **Suspending in finally without NonCancellable**:
   ```kotlin
   //  Will throw CancellationException
   try {
       doWork()
   } finally {
       saveState() // Suspending function throws!
   }

   //  Use NonCancellable
   try {
       doWork()
   } finally {
       withContext(NonCancellable) {
           saveState()
       }
   }
   ```

4. **Not yielding in tight loops**:
   ```kotlin
   //  Starves other coroutines
   repeat(1000000) {
       calculate()
   }

   //  Cooperative
   repeat(1000000) {
       yield()
       calculate()
   }
   ```

**English Summary**: Coroutine cancellation is cooperative - coroutines must check for cancellation using ensureActive(), yield(), or isActive. Use ensureActive() for quick checks, yield() for CPU-intensive loops, isActive in while conditions. Always re-throw CancellationException after cleanup. Use NonCancellable context for critical cleanup operations that must complete. Check cancellation periodically in long-running operations, especially in loops.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Cancellation and timeouts - Kotlin](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [Cooperative cancellation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/ensure-active.html)

## Related Questions
- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
- [[q-kotlin-coroutines-introduction--kotlin--medium]]
