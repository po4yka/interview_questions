---
id: cs-020
title: "Coroutine Dispatchers / Диспетчеры корутин"
aliases: ["Coroutine Dispatchers", "Диспетчеры корутин"]
topic: cs
subtopics: [coroutines, kotlin, threading]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-coroutines, q-abstract-class-purpose--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [coroutines, difficulty/medium, dispatchers, kotlin, programming-languages, threading]
sources: ["https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html"]

---

# Вопрос (RU)
> Что такое диспетчеры корутин? Какие типы диспетчеров существуют и когда их использовать?

# Question (EN)
> What are coroutine dispatchers? What types of dispatchers exist and when to use them?

---

## Ответ (RU)

**Теория Dispatcher:**
CoroutineDispatcher — элемент CoroutineContext, определяющий, на каком потоке (или пуле потоков) выполняется корутина или её части. Dispatchers управляют выделением потоков для корутин, обеспечивая эффективное использование ресурсов. Диспетчер — ключевой механизм для выбора/переключения контекста выполнения.

**Основные типы Dispatchers:**

**1. Dispatchers.Main:**

*Теория:* Dispatchers.Main выполняет корутины на главном (UI) потоке. Доступен в средах с "главным" потоком (Android, JavaFX, Swing и др.) при наличии соответствующих зависимостей (например, kotlinx-coroutines-android). Используется для обновления UI и взаимодействия с main loop. Блокирующие операции на главном потоке приводят к фризам UI и на Android могут вызвать ANR (`Application` Not Responding).

```kotlin
// ✅ Dispatchers.Main для UI updates
launch(Dispatchers.Main) {
    // Выполняется на main thread
    textView.text = "Loading..."

    val data = withContext(Dispatchers.IO) {
        // Переключение на IO dispatcher
        fetchData()
    }

    // Автоматическое возвращение на Main dispatcher
    textView.text = data
}
```

**2. Dispatchers.IO:**

*Теория:* Dispatchers.IO оптимизирован для I/O-операций (network, database, file I/O). Использует общий пул потоков, который может расширяться до 64 потоков или до количества ядер (берётся максимум из этих величин). Допускает выполнение блокирующих I/O-операций, не перегружая основной пул CPU-bound задач, но блокировка потоков остаётся затратной и её следует минимизировать. Не использовать для преимущественно CPU-intensive задач.

```kotlin
// ✅ Dispatchers.IO для I/O операций
launch(Dispatchers.IO) {
    // Network request
    val response = apiService.fetchData()

    // Database query
    val users = database.userDao().getAll()

    // File I/O
    val content = File("data.txt").readText()
}
```

**3. Dispatchers.Default:**

*Теория:* Dispatchers.Default оптимизирован для CPU-intensive задач (вычисления, сортировка, парсинг и т.п.). Использует общий пул потоков, размер которого обычно равен количеству CPU-ядер (минимум 2). Потоки не должны длительно блокироваться. Подходит для фоновых вычислений и parallel work.

```kotlin
// ✅ Dispatchers.Default для CPU-intensive задач
launch(Dispatchers.Default) {
    // Сортировка большого списка
    val sorted = largeList.sortedBy { it.value }

    // Парсинг JSON
    val parsed = Json.decodeFromString<Data>(jsonString)

    // Математические вычисления
    val result = complexCalculation(data)
}
```

**4. Dispatchers.Unconfined:**

*Теория:* Dispatchers.Unconfined не привязан к конкретному потоку. Корутина начинает выполнение в вызывающем потоке до первой точки приостановки. После возобновления продолжает на том потоке, который используется реализацией соответствующей suspend-функции. Это делает поведение потоков непредсказуемым; не рекомендуется для production-кода. Может быть полезен для упрощения некоторых тестов или примеров, но в реальных тестах обычно предпочтительнее TestDispatcher из kotlinx-coroutines-test.

```kotlin
// ✅ Dispatchers.Unconfined (ограниченно, например, в демонстрационных тестах)
launch(Dispatchers.Unconfined) {
    println("Thread 1: ${Thread.currentThread().name}")  // Caller thread

    delay(100)  // Suspension point

    println("Thread 2: ${Thread.currentThread().name}")  // Может быть другой thread
}

// ❌ Не использовать в production коде
launch(Dispatchers.Unconfined) {
    // Непредсказуемое поведение потоков
}
```

**Custom Dispatchers:**

*Теория:* Custom dispatchers создаются для специфичных задач: ограничение размера пула потоков, однопоточное выполнение, кастомный Executor и т.п. `newSingleThreadContext()` создаёт single-threaded dispatcher. `newFixedThreadPoolContext(n)` (устаревший, deprecated) создавал dispatcher с фиксированным пулом потоков; вместо него рекомендуется использовать собственный ExecutorService + `asCoroutineDispatcher()`. `asCoroutineDispatcher()` конвертирует ExecutorService в dispatcher. Важно освобождать ресурсы таких диспетчеров.

```kotlin
// ✅ Custom single-threaded dispatcher
val singleThreadDispatcher = newSingleThreadContext("MyThread")

launch(singleThreadDispatcher) {
    // Всегда выполняется на одном потоке
    println("Thread: ${Thread.currentThread().name}")
}

// ✅ Custom fixed thread pool (рекомендуемый способ через Executor)
val customDispatcher = Executors.newFixedThreadPool(4).asCoroutineDispatcher()

launch(customDispatcher) {
    // Выполняется на одном из 4 потоков
}

// Важно: закрывать custom dispatchers / executor-based dispatchers
singleThreadDispatcher.close()
customDispatcher.close()
```

**Переключение между Dispatchers:**

*Теория:* `withContext(dispatcher)` выполняет блок кода в указанном dispatcher. Вызов `withContext` является suspend-функцией: корутина приостанавливается, планировщик переключает контекст (при необходимости), затем блок выполняется в новом диспетчере. После завершения блока корутина продолжает выполнение в исходном dispatcher (если job ещё активен). `withContext` соответствует принципам structured concurrency.

```kotlin
// ✅ Переключение dispatchers
launch(Dispatchers.Main) {
    showLoading()

    val data = withContext(Dispatchers.IO) {
        // Переключение на IO
        fetchData()
    }
    // Автоматически вернулись на Main

    val processed = withContext(Dispatchers.Default) {
        // Переключение на Default
        processData(data)
    }
    // Автоматически вернулись на Main

    showResult(processed)
}
```

**Dispatcher Limitations / Ограничение параллелизма:**

*Теория:* `limitedParallelism(n)` создаёт "view" на существующий dispatcher с ограниченным уровнем параллелизма. Полезно для ограничения количества одновременных запросов к ресурсу. Не создаёт новые потоки, использует пул исходного dispatcher.

```kotlin
// ✅ Ограничение parallelism
val limitedDispatcher = Dispatchers.IO.limitedParallelism(3)

repeat(10) {
    launch(limitedDispatcher) {
        // Максимум 3 корутины выполняются одновременно в рамках этого dispatcher view
        performDatabaseQuery()
    }
}
```

**Выбор правильного Dispatcher:**

| Задача | Dispatcher | Причина |
|--------|-----------|---------|
| UI updates | Main | Только Main thread может обновлять UI |
| Network requests | IO | Блокирующие/потенциально блокирующие I/O операции |
| Database queries | IO | Блокирующие/потенциально блокирующие I/O операции |
| File I/O | IO | Блокирующие/потенциально блокирующие I/O операции |
| JSON parsing | Default | CPU-intensive вычисления |
| Sorting/filtering | Default | CPU-intensive вычисления |
| Image processing | Default | CPU-intensive вычисления |
| Unit tests | Test dispatcher / Main dispatcher override | Предсказуемое управление временем и потоками в тестах |

**Ключевые концепции:**

1. **Thread Pool Management** — Dispatchers эффективно управляют пулами потоков.
2. **`Context` Switching** — `withContext` для безопасного переключения контекста внутри structured concurrency.
3. **Blocking vs Non-blocking** — IO для I/O, Default для CPU-intensive; избегать блокирующего кода на Main и Default.
4. **Structured Concurrency** — Dispatchers интегрированы с иерархией корутин и scope-ами.
5. **Resource Efficiency** — Правильный выбор dispatcher = эффективное использование потоков и предотвращение contention.

## Answer (EN)

**Dispatcher Theory:**
CoroutineDispatcher is an element of CoroutineContext that determines which thread (or thread pool) executes a coroutine or its parts. Dispatchers manage thread allocation for coroutines, ensuring efficient resource usage. A dispatcher is a key mechanism for selecting/switching execution context.

**Main Dispatcher Types:**

**1. Dispatchers.Main:**

*Theory:* Dispatchers.Main runs coroutines on the main (UI) thread. It is available in environments with a main/UI thread (Android, JavaFX, Swing, etc.) when the proper dependencies are added (e.g., kotlinx-coroutines-android). It is used for UI updates and interactions with the main loop. Blocking operations on the main thread cause UI freezes and on Android can lead to ANR (`Application` Not Responding).

```kotlin
// ✅ Dispatchers.Main for UI updates
launch(Dispatchers.Main) {
    // Executes on main thread
    textView.text = "Loading..."

    val data = withContext(Dispatchers.IO) {
        // Switch to IO dispatcher
        fetchData()
    }

    // Automatically returns to Main dispatcher
    textView.text = data
}
```

**2. Dispatchers.IO:**

*Theory:* Dispatchers.IO is optimized for I/O operations (network, database, file I/O). It uses a shared thread pool that can grow up to 64 threads or the number of CPU cores, whichever is greater. It is designed to tolerate blocking I/O without overloading the CPU-bound Default pool, but blocking threads is still a resource cost and should be kept reasonable. Do not use it for primarily CPU-intensive work.

```kotlin
// ✅ Dispatchers.IO for I/O operations
launch(Dispatchers.IO) {
    // Network request
    val response = apiService.fetchData()

    // Database query
    val users = database.userDao().getAll()

    // File I/O
    val content = File("data.txt").readText()
}
```

**3. Dispatchers.Default:**

*Theory:* Dispatchers.Default is optimized for CPU-intensive tasks (computations, sorting, parsing, etc.). It uses a shared thread pool sized to the number of CPU cores (minimum 2). Threads in this pool should not be blocked for long. Suitable for background computations and parallel work.

```kotlin
// ✅ Dispatchers.Default for CPU-intensive tasks
launch(Dispatchers.Default) {
    // Sorting large list
    val sorted = largeList.sortedBy { it.value }

    // JSON parsing
    val parsed = Json.decodeFromString<Data>(jsonString)

    // Mathematical computations
    val result = complexCalculation(data)
}
```

**4. Dispatchers.Unconfined:**

*Theory:* Dispatchers.Unconfined is not confined to any specific thread. A coroutine starts in the caller thread until the first suspension point. After resumption, it continues in the thread chosen by the suspending function's implementation. This leads to unpredictable threading behavior; it is not recommended for production code. It can be useful for certain demos or simple tests, but for real tests prefer TestDispatcher from kotlinx-coroutines-test.

```kotlin
// ✅ Dispatchers.Unconfined (used sparingly, e.g., in demonstration tests)
launch(Dispatchers.Unconfined) {
    println("Thread 1: ${Thread.currentThread().name}")  // Caller thread

    delay(100)  // Suspension point

    println("Thread 2: ${Thread.currentThread().name}")  // May be a different thread
}

// ❌ Don't use in production code
launch(Dispatchers.Unconfined) {
    // Unpredictable thread behavior
}
```

**Custom Dispatchers:**

*Theory:* Custom dispatchers are created for specific needs: limiting thread pool size, single-threaded execution, using a custom Executor, etc. `newSingleThreadContext()` creates a single-threaded dispatcher. `newFixedThreadPoolContext(n)` (deprecated) used to create a fixed-size thread pool dispatcher; instead prefer your own ExecutorService plus `asCoroutineDispatcher()`. `asCoroutineDispatcher()` converts an ExecutorService into a dispatcher. It is important to properly release resources.

```kotlin
// ✅ Custom single-threaded dispatcher
val singleThreadDispatcher = newSingleThreadContext("MyThread")

launch(singleThreadDispatcher) {
    // Always executes on the same thread
    println("Thread: ${Thread.currentThread().name}")
}

// ✅ Custom fixed thread pool (recommended approach via Executor)
val customDispatcher = Executors.newFixedThreadPool(4).asCoroutineDispatcher()

launch(customDispatcher) {
    // Executes on one of 4 threads
}

// Important: close custom dispatchers / executor-based dispatchers
singleThreadDispatcher.close()
customDispatcher.close()
```

**Switching Between Dispatchers:**

*Theory:* `withContext(dispatcher)` runs a given block in the specified dispatcher. The call is a suspend function: the coroutine is suspended, the scheduler may switch the context, then the block runs in the new dispatcher. After the block completes, execution continues in the original dispatcher (if the job is still active). `withContext` adheres to structured concurrency.

```kotlin
// ✅ Switching dispatchers
launch(Dispatchers.Main) {
    showLoading()

    val data = withContext(Dispatchers.IO) {
        // Switch to IO
        fetchData()
    }
    // Automatically returned to Main

    val processed = withContext(Dispatchers.Default) {
        // Switch to Default
        processData(data)
    }
    // Automatically returned to Main

    showResult(processed)
}
```

**Dispatcher Limitations / Limiting Parallelism:**

*Theory:* `limitedParallelism(n)` creates a view of an existing dispatcher with limited parallelism. Useful for limiting the number of concurrent operations accessing a shared resource. It does not create new threads; it uses the parent dispatcher's pool.

```kotlin
// ✅ Limiting parallelism
val limitedDispatcher = Dispatchers.IO.limitedParallelism(3)

repeat(10) {
    launch(limitedDispatcher) {
        // At most 3 coroutines run in parallel within this dispatcher view
        performDatabaseQuery()
    }
}
```

**Choosing the Right Dispatcher:**

| Task | Dispatcher | Reason |
|------|-----------|--------|
| UI updates | Main | Only the main thread can update UI |
| Network requests | IO | Blocking/potentially blocking I/O operations |
| Database queries | IO | Blocking/potentially blocking I/O operations |
| File I/O | IO | Blocking/potentially blocking I/O operations |
| JSON parsing | Default | CPU-intensive computations |
| Sorting/filtering | Default | CPU-intensive computations |
| Image processing | Default | CPU-intensive computations |
| Unit tests | Test dispatcher / Main dispatcher override | Predictable control over time and threads in tests |

**Key Concepts:**

1. **Thread Pool Management** - Dispatchers efficiently manage thread pools.
2. **`Context` Switching** - `withContext` for safe context switching within structured concurrency.
3. **Blocking vs Non-blocking** - IO for I/O, Default for CPU-intensive; avoid blocking on Main and Default.
4. **Structured Concurrency** - Dispatchers integrate with coroutine scopes and job hierarchy.
5. **Resource Efficiency** - Correct dispatcher choice = efficient thread usage and less contention.

---

## Дополнительные вопросы (RU)

- Как `limitedParallelism()` работает внутренне?
- Что произойдет, если заблокировать поток `Dispatchers.Default`?
- Как тестировать код, который использует разные диспетчеры (kotlinx-coroutines-test, TestDispatcher и т.п.)?

## Follow-ups

- How does `limitedParallelism()` work internally?
- What happens if you block a Dispatchers.Default thread?
- How to test code that uses different dispatchers (kotlinx-coroutines-test, TestDispatcher, etc.)?

## Связанные вопросы (RU)

### Предпосылки (проще)
- Основы CoroutineContext

### Продвинутое (сложнее)
- Реализация кастомного диспетчера
- Оптимизация производительности диспетчеров

## Related Questions

### Prerequisites (Easier)
- CoroutineContext basics

### Advanced (Harder)
- Custom dispatcher implementation
- Dispatcher performance optimization

## References

- [[c-coroutines]]
- "https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html"
