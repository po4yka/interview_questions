---\
id: kotlin-051
title: "Coroutine Cancellation Cooperation / Кооперативная отмена корутин"
aliases: ["Coroutine Cancellation Cooperation", "Кооперативная отмена корутин"]

# Classification
topic: kotlin
subtopics: [cancellation, coroutines, structured-concurrency]
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
related: [c-coroutines, c-kotlin, q-coroutine-cancellation-mechanisms--kotlin--medium]

# Timestamps
created: 2025-10-11
updated: 2025-11-09

tags: [cancellation, cooperation, coroutines, difficulty/medium, ensureActive, kotlin, yield]
---\
# Вопрос (RU)
> Реализуйте долгоиграющие операции с поддержкой отмены. Правильно используйте `yield()`, `ensureActive()` и `isActive`. Корректно обрабатывайте `CancellationException`.

***

# Question (EN)
> Implement cancellation-aware long-running operations. Use `yield()`, `ensureActive()`, and `isActive` properly. Handle `CancellationException` correctly.

## Ответ (RU)

Отмена корутин **кооперативная** — корутины должны периодически проверять отмену (через `isActive`, `ensureActive()`, `yield()`, точки приостановки) и корректно завершаться.

### Почему Отмена Кооперативная

```kotlin
// Некорректно: корутина не проверяет отмену и продолжит выполняться до конца
val job = launch {
    var i = 0
    while (i < 1_000_000) {
        i++
        // Нет проверки isActive / ensureActive() / yield()
    }
}

delay(100)
job.cancel() // Job помечен как отменённый, но тело цикла об этом "не знает"
job.join()

// Корректно: кооперативная отмена
val job2 = launch {
    var i = 0
    while (i < 1_000_000) {
        ensureActive() // Бросит CancellationException, если Job отменён
        i++
    }
}

delay(100)
job2.cancel()
job2.join()
```

### Методы Проверки Отмены

(Предполагается, что код выполняется внутри корутины / `CoroutineScope`, где доступны `isActive`, `ensureActive()` и `yield()` из `kotlinx.coroutines`.)

#### 1. ensureActive()

Бросает `CancellationException` сразу, если корутина уже отменена.

```kotlin
suspend fun processData(items: List<Item>) {
    for (item in items) {
        ensureActive() // Бросает, если отменено
        processItem(item)
    }
}
```

#### 2. yield()

Приостанавливает корутину, проверяет отмену и даёт другим корутинам шанс выполниться.

```kotlin
suspend fun heavyComputation(data: List<Int>): Int {
    var result = 0
    for (value in data) {
        yield() // Кооперативная отмена + справедливое планирование
        result += calculate(value)
    }
    return result
}
```

#### 3. Свойство isActive

Используется внутри корутин для явной проверки статуса.

```kotlin
launch {
    while (isActive) {
        val data = fetchData()
        processData(data)
        delay(1000) // Тоже проверяет отмену
    }
}
```

### `yield()` Vs `ensureActive()` (RU)

- `yield()` — приостанавливает выполнение, проверяет отмену и отдаёт управление другим корутинам.
- `ensureActive()` — только проверяет отмену и бросает `CancellationException`, не приостанавливаясь.

```kotlin
// yield() полезен в плотных CPU-связанных циклах
launch {
    repeat(1000) {
        yield()
        cpuIntensiveWork()
    }
}

// ensureActive() дешевле, когда нужна только быстрая проверка
launch {
    for (item in items) {
        ensureActive()
        quickOperation(item)
    }
}
```

### Обработка CancellationException

`CancellationException` — «нормальный» сигнал отмены, а не ошибка бизнес-логики. Обычно его нужно либо:
- пробросить дальше, сохраняя семантику отмены, после локальной очистки ресурсов;
- либо осознанно преобразовать в результат (например, вернуть статус отмены на границе уровня API), не продолжая обычную работу как будто отмены не было.

```kotlin
// Правильно — выполнить очистку и сохранить семантику отмены
try {
    doWork()
} catch (e: CancellationException) {
    cleanup()
    throw e // Обычно важно пробросить дальше, чтобы верхний уровень знал об отмене
} catch (e: Exception) {
    handleError(e)
}

// Неправильно — проглатывает отмену и продолжает как обычную ошибку
try {
    doWork()
} catch (e: Exception) { // Включая CancellationException
    log(e)
    // При этом корутина может "продолжить жить" вместо корректного завершения
}
```

#### Пример: Загрузка Файла С Временным Файлом

```kotlin
suspend fun downloadFile(url: String): File = coroutineScope {
    val tempFile = createTempFile()

    try {
        val data = fetchData(url)
        tempFile.writeBytes(data)
        tempFile
    } catch (e: CancellationException) {
        tempFile.delete()
        println("Загрузка отменена, временный файл удалён")
        throw e
    } catch (e: Exception) {
        tempFile.delete()
        throw e
    }
}
```

### NonCancellable Контекст

Используется для критичной очистки, которая должна завершиться даже при отмене, с возможностью вызывать suspend-функции.

```kotlin
try {
    doWork()
} finally {
    withContext(NonCancellable) {
        // Здесь можно безопасно вызывать suspend-функции для очистки
        closeConnection()
        saveState()
    }
}
```

### Реальные Примеры (RU)

#### Пример 1: Обработка Изображений

```kotlin
class ImageProcessor {
    suspend fun processImages(images: List<Image>): List<ProcessedImage> {
        val results = mutableListOf<ProcessedImage>()

        for ((index, image) in images.withIndex()) {
            ensureActive() // Проверка отмены

            if (index % 10 == 0) {
                yield() // Дать другим корутинам поработать
                println("Обработано $index/${images.size}")
            }

            val processed = processImage(image)
            results.add(processed)
        }

        return results
    }

    private suspend fun processImage(image: Image): ProcessedImage {
        // CPU-интенсивная работа с кооперативной отменой
        repeat(1000) {
            yield()
            // ... тяжёлые вычисления ...
        }
        return ProcessedImage(image)
    }
}
```

#### Пример 2: Сетевой Запрос С Таймаутом И Очисткой

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
            println("Запрос превысил таймаут")
            throw e
        } catch (e: CancellationException) {
            println("Запрос отменён")
            throw e
        } catch (e: Exception) {
            println("Ошибка запроса: ${e.message}")
            throw e
        } finally {
            withContext(NonCancellable) {
                connection.close()
                activeConnections--
                println("Соединение закрыто, активных: $activeConnections")
            }
        }
    }
}
```

#### Пример 3: Миграция Базы Данных

```kotlin
class DatabaseMigrator {
    suspend fun migrateData(
        records: List<Record>,
        onProgress: (Int, Int) -> Unit
    ) {
        var migratedCount = 0
        val errors = mutableListOf<MigrationError>()

        for (record in records) {
            if (!isActive) {
                println("Миграция отменена на записи $migratedCount")
                rollback(migratedCount)
                return
            }

            try {
                migrateRecord(record)
                migratedCount++

                if (migratedCount % 100 == 0) {
                    onProgress(migratedCount, records.size)
                    yield() // Дать другим задачам выполниться
                }
            } catch (e: Exception) {
                errors.add(MigrationError(record.id, e))
            }
        }

        if (errors.isNotEmpty()) {
            println("Миграция завершена с ${errors.size} ошибками")
        } else {
            println("Миграция успешна: $migratedCount записей")
        }
    }

    private suspend fun rollback(count: Int) {
        withContext(NonCancellable) {
            println("Откат $count записей...")
            // Логика отката
        }
    }
}
```

#### Пример 4: Периодическая Фоновая Синхронизация

```kotlin
class BackgroundSync {
    suspend fun startSync() = coroutineScope {
        while (isActive) {
            try {
                syncData()
                println("Синхронизация завершена")
            } catch (e: CancellationException) {
                println("Синхронизация отменена")
                throw e
            } catch (e: Exception) {
                println("Ошибка синхронизации: ${e.message}")
                // Продолжаем при ошибке
            }

            delay(60_000) // Проверяет отмену
        }
    }

    private suspend fun syncData() {
        val data = fetchRemoteData()

        data.chunked(100).forEach { chunk ->
            ensureActive()
            saveToDatabase(chunk)
        }
    }
}
```

### Лучшие Практики

1. Проверяйте отмену в долгих/бесконечных циклах:
   ```kotlin
   while (isActive) {
       doWork()
   }

   for (item in items) {
       ensureActive()
       process(item)
   }
   ```

2. Используйте `yield()` в CPU-интенсивном коде:
   ```kotlin
   repeat(1_000_000) {
       yield()
       calculate()
   }
   ```

3. При обработке `CancellationException` не ломайте семантику отмены:
   ```kotlin
   catch (e: CancellationException) {
       cleanup()
       throw e // или конвертируйте в осознанный "отменено", но не игнорируйте
   }
   ```

4. Используйте `NonCancellable` для критичной очистки:
   ```kotlin
   finally {
       withContext(NonCancellable) {
           saveState()
       }
   }
   ```

### Распространённые Ошибки

1. Нет проверки отмены:
   ```kotlin
   // Практически неотменяемо
   while (true) { doWork() }

   // Отменяемо
   while (isActive) { doWork() }
   ```

2. Проглатывание `CancellationException`:
   ```kotlin
   // Ломает отмену
   try { doWork() }
   catch (e: Exception) { log(e) } // Тут окажется и CancellationException

   // Корректно
   try { doWork() }
   catch (e: Exception) {
       if (e is CancellationException) throw e
       log(e)
   }
   ```

3. Приостановка в `finally` без `NonCancellable`:
   ```kotlin
   // Приостанавливающие функции здесь тоже будут отменены
   try {
       doWork()
   } finally {
       saveState() // Может бросить CancellationException и не завершиться
   }

   // Используйте NonCancellable
   try {
       doWork()
   } finally {
       withContext(NonCancellable) {
           saveState()
       }
   }
   ```

4. Отсутствие `yield()` в плотных CPU-связанных циклах:
   ```kotlin
   // Мешает другим корутинам выполняться
   repeat(1_000_000) {
       calculate()
   }

   // Кооперативно
   repeat(1_000_000) {
       yield()
       calculate()
   }
   ```

**Краткое содержание**: Отмена корутин кооперативная: корутины должны периодически проверять отмену через `ensureActive()`, `yield()`, `isActive` или точки приостановки. Используйте `ensureActive()` для быстрых проверок, `yield()` — в CPU-интенсивных циклах, `isActive` — в условиях циклов. При обработке `CancellationException` не теряйте семантику отмены. Для критичных операций очистки используйте `NonCancellable`. Проверяйте отмену в долгоиграющих операциях.

---

## Answer (EN)

`Coroutine` cancellation is **cooperative**: coroutines must periodically check for cancellation (`isActive`, `ensureActive()`, `yield()`, suspension points) and complete gracefully.

### Why Cancellation is Cooperative

```kotlin
// Non-cooperative: loop body never observes cancellation
val job = launch {
    var i = 0
    while (i < 1_000_000) {
        i++
        // No isActive / ensureActive() / yield()
    }
}

delay(100)
job.cancel() // Job is marked as cancelled, but the loop doesn't check it
job.join()

// Cooperative: observes cancellation
val job2 = launch {
    var i = 0
    while (i < 1_000_000) {
        ensureActive() // Throws CancellationException if job is cancelled
        i++
    }
}

delay(100)
job2.cancel()
job2.join()
```

### Cancellation Check Methods

(Assumes code runs inside a coroutine / `CoroutineScope` where `isActive`, `ensureActive()` and `yield()` from `kotlinx.coroutines` are available.)

#### 1. ensureActive()

Throws `CancellationException` immediately if the coroutine is cancelled.

```kotlin
suspend fun processData(items: List<Item>) {
    for (item in items) {
        ensureActive() // Throws if cancelled
        processItem(item)
    }
}
```

#### 2. yield()

Suspends, checks cancellation, and gives other coroutines a chance to run.

```kotlin
suspend fun heavyComputation(data: List<Int>): Int {
    var result = 0
    for (value in data) {
        yield() // Cooperative cancellation + fair scheduling
        result += complexCalculation(value)
    }
    return result
}
```

`yield()` vs `ensureActive()`:
- `yield()` — suspends, checks cancellation, and lets other coroutines run.
- `ensureActive()` — only checks cancellation, does not suspend.

```kotlin
// yield() is useful in tight CPU-bound loops
launch {
    repeat(1000) {
        yield()
        cpuIntensiveWork()
    }
}

// ensureActive() is cheaper when you just need a quick check
launch {
    for (item in items) {
        ensureActive()
        quickOperation(item)
    }
}
```

#### 3. isActive Property

`isActive` is a `Boolean` flag available in a coroutine context to check if the coroutine is still active.

```kotlin
suspend fun processLargeFile(file: File) {
    file.forEachLine { line ->
        if (!isActive) {
            println("Processing cancelled")
            return // Exit early when cancelled
        }
        processLine(line)
    }
}

// Or with a loop
launch {
    while (isActive) {
        val data = fetchData()
        processData(data)
        delay(1000) // Also checks cancellation
    }
    println("Stopped gracefully")
}
```

### Handling CancellationException

`CancellationException` is a normal signal of cancellation, not a business error. Typically you should either:
- re-throw it (after local cleanup) so that cancellation propagates; or
- intentionally convert it into a "cancelled" result at a boundary, without continuing normal work as if nothing happened.

```kotlin
// Correct: cleanup and preserve cancellation semantics
suspend fun downloadFile(url: String): File = coroutineScope {
    val tempFile = createTempFile()

    try {
        val data = fetchData(url)
        tempFile.writeBytes(data)
        tempFile
    } catch (e: CancellationException) {
        tempFile.delete()
        println("Download cancelled, cleaned up temp file")
        throw e // Usually must be re-thrown
    } catch (e: Exception) {
        tempFile.delete()
        throw e
    }
}

// Wrong: swallows CancellationException and breaks cancellation
suspend fun broken() {
    try {
        doWork()
    } catch (e: Exception) { // Also catches CancellationException
        println("Error: $e")
        // Not re-thrown: coroutine may continue incorrectly
    }
}
```

### NonCancellable Context

Use `NonCancellable` for critical cleanup that must run even when the coroutine is cancelled and may need to call suspending functions.

```kotlin
suspend fun processWithCleanup() {
    try {
        doWork()
    } finally {
        // In a normal finally, suspending functions would also be cancelled.
        // Wrapping in NonCancellable allows them to complete.
        withContext(NonCancellable) {
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
        // CPU-intensive work with cooperative cancellation
        repeat(1000) {
            yield()
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
            if (!isActive) {
                println("Migration cancelled at record $migratedCount")
                rollback(migratedCount)
                return
            }

            try {
                migrateRecord(record)
                migratedCount++

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

            delay(60_000) // Will throw if cancelled
        }
    }

    private suspend fun syncData() {
        val data = fetchRemoteData()

        data.chunked(100).forEach { chunk ->
            ensureActive()
            saveToDatabase(chunk)
        }
    }
}

val syncJob = launch {
    backgroundSync.startSync()
}

onPause {
    syncJob.cancel()
}
```

### Best Practices

1. Always check cancellation in long-running loops:
   ```kotlin
   while (isActive) {
       doWork()
   }

   for (item in items) {
       ensureActive()
       process(item)
   }
   ```

2. Use `yield()` in CPU-intensive code:
   ```kotlin
   repeat(1_000_000) {
       yield()
       heavyCalculation()
   }
   ```

3. When catching `CancellationException`, preserve cancellation semantics:
   ```kotlin
   try {
       operation()
   } catch (e: CancellationException) {
       cleanup()
       throw e // or map to a clear "cancelled" result at boundaries
   }
   ```

4. Use `NonCancellable` for critical cleanup:
   ```kotlin
   finally {
       withContext(NonCancellable) {
           saveState()
           closeResources()
       }
   }
   ```

5. Check cancellation periodically in long operations:
   ```kotlin
   for ((index, item) in items.withIndex()) {
       if (index % 100 == 0) {
           ensureActive()
       }
       process(item)
   }
   ```

### Common Pitfalls

1. Never checking cancellation:
   ```kotlin
   // Cannot be cooperatively cancelled
   while (true) {
       doWork()
   }

   // Cancellable
   while (isActive) {
       doWork()
   }
   ```

2. Swallowing `CancellationException`:
   ```kotlin
   // Breaks cancellation
   try {
       doWork()
   } catch (e: Exception) {
       log(e) // Also catches CancellationException
   }

   // Preserve cancellation
   try {
       doWork()
   } catch (e: Exception) {
       if (e is CancellationException) throw e
       log(e)
   }
   ```

3. Suspending in finally without `NonCancellable`:
   ```kotlin
   // Suspending functions here will also be cancelled
   try {
       doWork()
   } finally {
       saveState() // May throw CancellationException
   }

   // Use NonCancellable
   try {
       doWork()
   } finally {
       withContext(NonCancellable) {
           saveState()
       }
   }
   ```

4. Not yielding in tight CPU-bound loops:
   ```kotlin
   // Starves other coroutines
   repeat(1_000_000) {
       calculate()
   }

   // Cooperative
   repeat(1_000_000) {
       yield()
       calculate()
   }
   ```

**English Summary**: `Coroutine` cancellation is cooperative: coroutines must periodically check for cancellation using `ensureActive()`, `yield()`, or `isActive`. Use `ensureActive()` for quick checks, `yield()` for CPU-intensive loops, and `isActive` in while conditions. When handling `CancellationException`, do not accidentally swallow cancellation; rethrow it (or map it to a clear "cancelled" outcome) after cleanup. Use `NonCancellable` for critical cleanup operations that must complete. Check for cancellation periodically in long-running operations, especially in loops.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Cancellation and timeouts - Kotlin](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [Cooperative cancellation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/ensure-active.html)
- [[c-kotlin]]
- [[c-coroutines]]

## Related Questions
- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
- [[q-kotlin-coroutines-introduction--kotlin--medium]]
