---
id: cs-020
title: "Coroutine Dispatchers / Диспетчеры корутин"
aliases: ["Coroutine Dispatchers", "Диспетчеры корутин"]
topic: cs
subtopics: [coroutines, kotlin, programming-languages, threading]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-coroutine-context]
created: 2025-10-15
updated: 2025-01-25
tags: [coroutines, difficulty/medium, dispatchers, kotlin, programming-languages, threading]
sources: [https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html]
date created: Friday, October 3rd 2025, 5:21:02 pm
date modified: Saturday, November 1st 2025, 5:43:28 pm
---

# Вопрос (RU)
> Что такое диспетчеры корутин? Какие типы диспетчеров существуют и когда их использовать?

# Question (EN)
> What are coroutine dispatchers? What types of dispatchers exist and when to use them?

---

## Ответ (RU)

**Теория Dispatcher:**
CoroutineDispatcher - элемент CoroutineContext, определяющий, на каком потоке (или thread pool) выполняется корутина. Dispatchers управляют thread allocation для корутин, обеспечивая эффективное использование ресурсов. Dispatchers - ключевой механизм для переключения контекста выполнения.

**Основные типы Dispatchers:**

**1. Dispatchers.Main:**

*Теория:* Dispatchers.Main - выполняет корутины на main (UI) thread. Доступен только в UI-приложениях (Android, Swing, JavaFX). Используется для UI updates. Блокирующие операции на Main thread вызывают ANR (Application Not Responding).

```kotlin
// ✅ Dispatchers.Main для UI updates
launch(Dispatchers.Main) {
    // Выполняется на main thread
    textView.text = "Loading..."

    val data = withContext(Dispatchers.IO) {
        // Переключение на IO thread
        fetchData()
    }

    // Автоматическое возвращение на Main thread
    textView.text = data
}
```

**2. Dispatchers.IO:**

*Теория:* Dispatchers.IO - оптимизирован для I/O операций (network, database, file I/O). Использует shared thread pool (по умолчанию 64 потока или количество CPU cores, что больше). Threads могут блокироваться без потери производительности. Не использовать для CPU-intensive задач.

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

*Теория:* Dispatchers.Default - оптимизирован для CPU-intensive задач (вычисления, сортировка, парсинг). Использует shared thread pool размером равным количеству CPU cores (минимум 2). Threads не должны блокироваться. Подходит для background computations.

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

*Теория:* Dispatchers.Unconfined - не confined к конкретному потоку. Корутина начинает выполнение в caller thread до первой suspension point. После resume продолжает в том потоке, где была resumed (зависит от suspend function). Не рекомендуется для production кода. Полезен для unit tests.

```kotlin
// ✅ Dispatchers.Unconfined (для тестов)
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

*Теория:* Custom dispatchers создаются для специфичных задач: ограничение thread pool size, single-threaded execution, priority-based scheduling. `newSingleThreadContext()` создаёт single-threaded dispatcher. `newFixedThreadPoolContext(n)` создаёт fixed-size thread pool. `asCoroutineDispatcher()` конвертирует ExecutorService в dispatcher.

```kotlin
// ✅ Custom single-threaded dispatcher
val singleThreadDispatcher = newSingleThreadContext("MyThread")

launch(singleThreadDispatcher) {
    // Всегда выполняется на одном потоке
    println("Thread: ${Thread.currentThread().name}")
}

// ✅ Custom fixed thread pool
val customDispatcher = Executors.newFixedThreadPool(4).asCoroutineDispatcher()

launch(customDispatcher) {
    // Выполняется на одном из 4 потоков
}

// Важно: закрывать custom dispatchers
singleThreadDispatcher.close()
customDispatcher.close()
```

**Переключение между Dispatchers:**

*Теория:* `withContext(dispatcher)` переключает dispatcher для блока кода. Корутина suspend на время переключения. После завершения блока возвращается к предыдущему dispatcher. `withContext` - structured concurrency safe.

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

**Dispatcher Limitations:**

*Теория:* `limitedParallelism(n)` создаёт view на dispatcher с ограниченным parallelism. Полезно для ограничения concurrent requests к ресурсу. Не создаёт новые threads, использует parent dispatcher pool.

```kotlin
// ✅ Ограничение parallelism
val limitedDispatcher = Dispatchers.IO.limitedParallelism(3)

repeat(10) {
    launch(limitedDispatcher) {
        // Максимум 3 корутины выполняются одновременно
        performDatabaseQuery()
    }
}
```

**Выбор правильного Dispatcher:**

| Задача | Dispatcher | Причина |
|--------|-----------|---------|
| UI updates | Main | Только Main thread может обновлять UI |
| Network requests | IO | Блокирующие I/O операции |
| Database queries | IO | Блокирующие I/O операции |
| File I/O | IO | Блокирующие I/O операции |
| JSON parsing | Default | CPU-intensive вычисления |
| Sorting/filtering | Default | CPU-intensive вычисления |
| Image processing | Default | CPU-intensive вычисления |
| Unit tests | Unconfined | Предсказуемое выполнение в тестах |

**Ключевые концепции:**

1. **Thread Pool Management** - Dispatchers управляют thread pools эффективно
2. **Context Switching** - `withContext` для безопасного переключения
3. **Blocking vs Non-blocking** - IO для блокирующих, Default для CPU-intensive
4. **Structured Concurrency** - Dispatchers интегрированы с structured concurrency
5. **Resource Efficiency** - Правильный dispatcher = эффективное использование ресурсов

## Answer (EN)

**Dispatcher Theory:**
CoroutineDispatcher - element of CoroutineContext, determining which thread (or thread pool) executes coroutine. Dispatchers manage thread allocation for coroutines, ensuring efficient resource usage. Dispatchers - key mechanism for switching execution context.

**Main Dispatcher Types:**

**1. Dispatchers.Main:**

*Theory:* Dispatchers.Main - executes coroutines on main (UI) thread. Available only in UI applications (Android, Swing, JavaFX). Used for UI updates. Blocking operations on Main thread cause ANR (Application Not Responding).

```kotlin
// ✅ Dispatchers.Main for UI updates
launch(Dispatchers.Main) {
    // Executes on main thread
    textView.text = "Loading..."

    val data = withContext(Dispatchers.IO) {
        // Switch to IO thread
        fetchData()
    }

    // Automatically returns to Main thread
    textView.text = data
}
```

**2. Dispatchers.IO:**

*Theory:* Dispatchers.IO - optimized for I/O operations (network, database, file I/O). Uses shared thread pool (default 64 threads or CPU cores count, whichever is greater). Threads can block without performance loss. Don't use for CPU-intensive tasks.

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

*Theory:* Dispatchers.Default - optimized for CPU-intensive tasks (computations, sorting, parsing). Uses shared thread pool sized to CPU cores count (minimum 2). Threads shouldn't block. Suitable for background computations.

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

*Theory:* Dispatchers.Unconfined - not confined to specific thread. Coroutine starts execution in caller thread until first suspension point. After resume continues in thread where it was resumed (depends on suspend function). Not recommended for production code. Useful for unit tests.

```kotlin
// ✅ Dispatchers.Unconfined (for tests)
launch(Dispatchers.Unconfined) {
    println("Thread 1: ${Thread.currentThread().name}")  // Caller thread

    delay(100)  // Suspension point

    println("Thread 2: ${Thread.currentThread().name}")  // May be different thread
}

// ❌ Don't use in production code
launch(Dispatchers.Unconfined) {
    // Unpredictable thread behavior
}
```

**Custom Dispatchers:**

*Theory:* Custom dispatchers created for specific tasks: limiting thread pool size, single-threaded execution, priority-based scheduling. `newSingleThreadContext()` creates single-threaded dispatcher. `newFixedThreadPoolContext(n)` creates fixed-size thread pool. `asCoroutineDispatcher()` converts ExecutorService to dispatcher.

```kotlin
// ✅ Custom single-threaded dispatcher
val singleThreadDispatcher = newSingleThreadContext("MyThread")

launch(singleThreadDispatcher) {
    // Always executes on same thread
    println("Thread: ${Thread.currentThread().name}")
}

// ✅ Custom fixed thread pool
val customDispatcher = Executors.newFixedThreadPool(4).asCoroutineDispatcher()

launch(customDispatcher) {
    // Executes on one of 4 threads
}

// Important: close custom dispatchers
singleThreadDispatcher.close()
customDispatcher.close()
```

**Switching Between Dispatchers:**

*Theory:* `withContext(dispatcher)` switches dispatcher for code block. Coroutine suspends during switch. After block completes returns to previous dispatcher. `withContext` - structured concurrency safe.

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

**Dispatcher Limitations:**

*Theory:* `limitedParallelism(n)` creates view on dispatcher with limited parallelism. Useful for limiting concurrent requests to resource. Doesn't create new threads, uses parent dispatcher pool.

```kotlin
// ✅ Limiting parallelism
val limitedDispatcher = Dispatchers.IO.limitedParallelism(3)

repeat(10) {
    launch(limitedDispatcher) {
        // Maximum 3 coroutines execute simultaneously
        performDatabaseQuery()
    }
}
```

**Choosing Right Dispatcher:**

| Task | Dispatcher | Reason |
|------|-----------|--------|
| UI updates | Main | Only Main thread can update UI |
| Network requests | IO | Blocking I/O operations |
| Database queries | IO | Blocking I/O operations |
| File I/O | IO | Blocking I/O operations |
| JSON parsing | Default | CPU-intensive computations |
| Sorting/filtering | Default | CPU-intensive computations |
| Image processing | Default | CPU-intensive computations |
| Unit tests | Unconfined | Predictable execution in tests |

**Key Concepts:**

1. **Thread Pool Management** - Dispatchers manage thread pools efficiently
2. **Context Switching** - `withContext` for safe switching
3. **Blocking vs Non-blocking** - IO for blocking, Default for CPU-intensive
4. **Structured Concurrency** - Dispatchers integrated with structured concurrency
5. **Resource Efficiency** - Right dispatcher = efficient resource usage

---

## Follow-ups

- How does `limitedParallelism()` work internally?
- What happens if you block Dispatchers.Default thread?
- How to test code with different dispatchers?

## Related Questions

### Prerequisites (Easier)
- CoroutineContext basics

### Advanced (Harder)
- Custom dispatcher implementation
- Dispatcher performance optimization
