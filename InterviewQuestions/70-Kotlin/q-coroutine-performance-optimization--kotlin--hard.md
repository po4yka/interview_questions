---
id: kotlin-083
title: "Coroutine Performance Optimization / Оптимизация производительности корутин"
aliases: []

# Classification
topic: kotlin
subtopics: [advanced, coroutines, patterns]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140021

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-delegates-compilation--kotlin--hard, q-lifecyclescope-viewmodelscope--kotlin--medium, q-stateflow-purpose--programming-languages--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [coroutines, difficulty/hard, difficulty/medium, kotlin]
date created: Saturday, October 18th 2025, 12:40:07 pm
date modified: Saturday, November 1st 2025, 5:43:27 pm
---

# Question (EN)
> Kotlin Coroutines advanced topic 140021

# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140021

---

## Answer (EN)

Coroutine performance optimization involves understanding dispatcher selection, minimizing context switching, efficient resource usage, and avoiding common performance pitfalls.

### Key Performance Principles

**1. Choose the Right Dispatcher**
```kotlin
// CPU-intensive work
withContext(Dispatchers.Default) {
    processLargeDataset()
}

// I/O operations
withContext(Dispatchers.IO) {
    downloadFile()
}

// UI updates
withContext(Dispatchers.Main) {
    updateUI()
}
```

**2. Minimize Context Switching**
```kotlin
// Bad: Multiple context switches
suspend fun inefficient() {
    withContext(Dispatchers.IO) { operation1() }
    withContext(Dispatchers.IO) { operation2() }
    withContext(Dispatchers.IO) { operation3() }
}

// Good: Single context switch
suspend fun efficient() {
    withContext(Dispatchers.IO) {
        operation1()
        operation2()
        operation3()
    }
}
```

**3. Use Parallel Execution**
```kotlin
suspend fun loadDataParallel() = coroutineScope {
    val user = async { fetchUser() }
    val settings = async { fetchSettings() }
    val preferences = async { fetchPreferences() }

    UserData(user.await(), settings.await(), preferences.await())
}
```

**4. Avoid Creating Too Many Coroutines**
```kotlin
// Bad: Creates 1 million coroutines
launch {
    (1..1_000_000).forEach {
        launch { process(it) }
    }
}

// Good: Use chunking
launch {
    (1..1_000_000).chunked(1000).forEach { chunk ->
        launch {
            chunk.forEach { process(it) }
        }
    }
}
```

**5. Configure Dispatcher Pool Sizes**
```kotlin
// Custom dispatcher with limited parallelism
val customDispatcher = Dispatchers.IO.limitedParallelism(4)

launch(customDispatcher) {
    // Only 4 concurrent operations
}
```

**6. Use Flow for Streaming Data**
```kotlin
// Better than collecting to list
flow {
    repeat(1_000_000) {
        emit(it)
    }
}.map { process(it) }
 .collect { save(it) }
```

### Performance Monitoring

```kotlin
suspend fun measurePerformance() {
    val duration = measureTimeMillis {
        coroutineScope {
            repeat(10_000) {
                launch { /* work */ }
            }
        }
    }
    println("Completed in ${duration}ms")
}
```

### Best Practices

1. **Reuse CoroutineScope** instead of creating new ones
2. **Use structured concurrency** to avoid leaks
3. **Profile before optimizing** - measure actual bottlenecks
4. **Use appropriate buffer sizes** in channels and flows
5. **Consider using sequences** for CPU-bound transformations
6. **Avoid blocking operations** in coroutines

---

## Ответ (RU)

Оптимизация производительности корутин включает понимание выбора диспетчеров, минимизацию переключения контекста, эффективное использование ресурсов и избежание распространенных проблем производительности.

### Ключевые Принципы Производительности

**1. Выбор правильного Dispatcher**
```kotlin
// CPU-интенсивная работа
withContext(Dispatchers.Default) {
    processLargeDataset()
}

// I/O операции
withContext(Dispatchers.IO) {
    downloadFile()
}

// Обновления UI
withContext(Dispatchers.Main) {
    updateUI()
}
```

**2. Минимизация переключения контекста**
```kotlin
// Плохо: Множественные переключения контекста
suspend fun inefficient() {
    withContext(Dispatchers.IO) { operation1() }
    withContext(Dispatchers.IO) { operation2() }
    withContext(Dispatchers.IO) { operation3() }
}

// Хорошо: Единственное переключение контекста
suspend fun efficient() {
    withContext(Dispatchers.IO) {
        operation1()
        operation2()
        operation3()
    }
}
```

**3. Использование параллельного выполнения**
```kotlin
suspend fun loadDataParallel() = coroutineScope {
    val user = async { fetchUser() }
    val settings = async { fetchSettings() }
    val preferences = async { fetchPreferences() }

    UserData(user.await(), settings.await(), preferences.await())
}
```

**4. Избегайте создания слишком многих корутин**
```kotlin
// Плохо: Создает 1 миллион корутин
launch {
    (1..1_000_000).forEach {
        launch { process(it) }
    }
}

// Хорошо: Используйте разбиение на части
launch {
    (1..1_000_000).chunked(1000).forEach { chunk ->
        launch {
            chunk.forEach { process(it) }
        }
    }
}
```

**5. Конфигурация размеров пулов Dispatcher**
```kotlin
// Кастомный dispatcher с ограниченным параллелизмом
val customDispatcher = Dispatchers.IO.limitedParallelism(4)

launch(customDispatcher) {
    // Только 4 одновременные операции
}
```

**6. Используйте Flow для потоковых данных**
```kotlin
// Лучше чем собирать в список
flow {
    repeat(1_000_000) {
        emit(it)
    }
}.map { process(it) }
 .collect { save(it) }
```

### Мониторинг Производительности

```kotlin
suspend fun measurePerformance() {
    val duration = measureTimeMillis {
        coroutineScope {
            repeat(10_000) {
                launch { /* work */ }
            }
        }
    }
    println("Completed in ${duration}ms")
}
```

### Лучшие Практики

1. **Переиспользуйте CoroutineScope** вместо создания новых
2. **Используйте структурированную конкурентность** чтобы избежать утечек
3. **Профилируйте перед оптимизацией** - измеряйте реальные узкие места
4. **Используйте подходящие размеры буферов** в каналах и потоках
5. **Рассмотрите использование sequences** для CPU-bound трансформаций
6. **Избегайте блокирующих операций** в корутинах

---

## Follow-ups

1. **Follow-up question 1**
2. **Follow-up question 2**

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

---

## Related Questions

### Related (Hard)
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines
- [[q-coroutine-memory-leaks--kotlin--hard]] - Coroutines
- [[q-flow-performance--kotlin--hard]] - Coroutines
- [[q-dispatcher-performance--kotlin--hard]] - Coroutines

### Prerequisites (Easier)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

