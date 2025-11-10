---
id: kotlin-083
title: "Coroutine Performance Optimization / Оптимизация производительности корутин"
aliases: ["Coroutine Performance Optimization", "Оптимизация производительности корутин"]

# Classification
topic: kotlin
subtopics: [coroutines, patterns, advanced]
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
related: [c-kotlin, c-coroutines, q-delegates-compilation--kotlin--hard, q-lifecyclescope-viewmodelscope--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [coroutines, difficulty/hard, kotlin]
---
# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140021

---

# Question (EN)
> Kotlin Coroutines advanced topic 140021

## Ответ (RU)

Оптимизация производительности корутин включает понимание выбора диспетчеров, минимизацию переключения контекста, эффективное использование ресурсов и избежание распространенных проблем производительности. См. также [[c-kotlin]] и [[c-coroutines]].

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
// Плохо: множественные последовательные переключения контекста с одинаковым dispatcher
suspend fun inefficient() {
    withContext(Dispatchers.IO) { operation1() }
    withContext(Dispatchers.IO) { operation2() }
    withContext(Dispatchers.IO) { operation3() }
}

// Лучше: одно переключение контекста для последовательных операций
suspend fun efficient() {
    withContext(Dispatchers.IO) {
        operation1()
        operation2()
        operation3()
    }
}
```

**3. Использование параллельного выполнения (для независимых операций)**
```kotlin
suspend fun loadDataParallel() = coroutineScope {
    val user = async { fetchUser() }
    val settings = async { fetchSettings() }
    val preferences = async { fetchPreferences() }

    UserData(user.await(), settings.await(), preferences.await())
}
```

**4. Избегайте бессмысленного создания огромного числа корутин**
```kotlin
// Потенциально неэффективно: создаёт 1 миллион корутин.
// Коррутины лёгкие, но если внутри тяжёлая или блокирующая работа,
// это приведёт к избыточным накладным расходам и потреблению памяти.
launch {
    (1..1_000_000).forEach {
        launch { process(it) }
    }
}

// Лучше: батчируйте задачи или ограничивайте параллелизм
launch {
    (1..1_000_000).chunked(1000).forEach { chunk ->
        launch {
            chunk.forEach { process(it) }
        }
    }
}
```

**5. Конфигурация параллелизма Dispatcher**
```kotlin
// Кастомный dispatcher с ограниченным параллелизмом на базе Dispatchers.IO
val customDispatcher = Dispatchers.IO.limitedParallelism(4)

launch(customDispatcher) {
    // Не более 4 одновременных корутин на этом dispatcher для данного ограничителя
}
```

**6. Используйте `Flow` для потоковых данных (и правильные dispatcher)**
```kotlin
flow {
    repeat(1_000_000) {
        emit(it)
    }
}
    .map { value ->
        // При тяжёлой работе явно выбирайте dispatcher, например:
        // withContext(Dispatchers.Default) { process(value) }
        process(value)
    }
    .collect { save(it) }
```

### Мониторинг Производительности

```kotlin
suspend fun measurePerformance() {
    val duration = measureTimeMillis {
        coroutineScope {
            repeat(10_000) {
                launch { /* неблокирующая работа */ }
            }
        }
    }
    println("Completed in ${duration}ms")
}
```

### Лучшие Практики

1. **Переиспользуйте `CoroutineScope`** вместо создания новых при каждой операции
2. **Используйте структурированную конкурентность**, избегайте `GlobalScope` для долгоживущих задач
3. **Профилируйте перед оптимизацией** — измеряйте реальные узкие места
4. **Используйте подходящие размеры буферов** в каналах и потоках
5. **Рассматривайте `Sequence`** для CPU-bound трансформаций в одном потоке
6. **Избегайте блокирующих операций** в корутинах; оборачивайте их в соответствующий dispatcher или заменяйте неблокирующими API

---

## Answer (EN)

Coroutine performance optimization involves understanding dispatcher selection, minimizing context switching, efficient resource usage, and avoiding common performance pitfalls. See also [[c-kotlin]] and [[c-coroutines]].

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

**2. Minimize context switching**
```kotlin
// Bad: multiple sequential context switches to the same dispatcher
suspend fun inefficient() {
    withContext(Dispatchers.IO) { operation1() }
    withContext(Dispatchers.IO) { operation2() }
    withContext(Dispatchers.IO) { operation3() }
}

// Better: a single context switch for sequential work
suspend fun efficient() {
    withContext(Dispatchers.IO) {
        operation1()
        operation2()
        operation3()
    }
}
```

**3. Use parallel execution (for independent operations)**
```kotlin
suspend fun loadDataParallel() = coroutineScope {
    val user = async { fetchUser() }
    val settings = async { fetchSettings() }
    val preferences = async { fetchPreferences() }

    UserData(user.await(), settings.await(), preferences.await())
}
```

**4. Avoid pointless creation of huge numbers of coroutines**
```kotlin
// Potentially inefficient: creates 1 million coroutines.
// Coroutines are lightweight, but if each does heavy or blocking work,
// you get significant scheduling and memory overhead.
launch {
    (1..1_000_000).forEach {
        launch { process(it) }
    }
}

// Better: batch work or limit parallelism
launch {
    (1..1_000_000).chunked(1000).forEach { chunk ->
        launch {
            chunk.forEach { process(it) }
        }
    }
}
```

**5. Configure dispatcher parallelism**
```kotlin
// Custom dispatcher with limited parallelism based on Dispatchers.IO
val customDispatcher = Dispatchers.IO.limitedParallelism(4)

launch(customDispatcher) {
    // At most 4 concurrent coroutines on this limited view
}
```

**6. Use `Flow` for streaming data (with appropriate dispatchers)**
```kotlin
flow {
    repeat(1_000_000) {
        emit(it)
    }
}
    .map { value ->
        // For heavy CPU work, explicitly choose dispatcher, e.g.:
        // withContext(Dispatchers.Default) { process(value) }
        process(value)
    }
    .collect { save(it) }
```

### Performance Monitoring

```kotlin
suspend fun measurePerformance() {
    val duration = measureTimeMillis {
        coroutineScope {
            repeat(10_000) {
                launch { /* non-blocking work */ }
            }
        }
    }
    println("Completed in ${duration}ms")
}
```

### Best Practices

1. **Reuse `CoroutineScope`** instead of creating new scopes for every operation
2. **Use structured concurrency** and avoid `GlobalScope` for long-running tasks
3. **Profile before optimizing** – measure real bottlenecks
4. **Use appropriate buffer sizes** in channels and flows
5. **Consider using `Sequence`** for single-threaded CPU-bound transformations
6. **Avoid blocking operations** inside coroutines; wrap them with the proper dispatcher or replace with non-blocking APIs

---

## Дополнительные вопросы (RU)

1. Как вы будете профилировать корутины в крупном приложении и какие инструменты использовать для поиска узких мест?
2. В каких случаях стоит ограничивать параллелизм через `limitedParallelism`, и как выбрать оптимальное значение?
3. Как подойти к оптимизации `Flow`-цепочек с большим количеством операторов и большим объёмом данных?
4. Какие риски возникают при использовании `GlobalScope` с точки зрения производительности и утечек ресурсов?
5. Как вы определите, что стоит перейти от корутин к более низкоуровневым примитивам (например, потокам или нативным API) для критичных путей?

---

## Follow-ups

1. How would you profile coroutines in a large application and which tools would you use to identify bottlenecks?
2. When should you limit parallelism via `limitedParallelism`, and how do you choose an appropriate value?
3. How would you optimize `Flow` pipelines with many operators and high data volume?
4. What are the performance and resource-leak risks of using `GlobalScope`?
5. How do you decide when to replace coroutines with lower-level primitives (threads/native APIs) on critical hot paths?

---

## Ссылки (RU)

- [Документация Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html)

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

---

## Связанные вопросы (RU)

### Сложные (Hard)
- [[q-coroutine-profiling--kotlin--hard]] - Корутины
- [[q-coroutine-memory-leaks--kotlin--hard]] - Корутины
- [[q-flow-performance--kotlin--hard]] - Корутины
- [[q-dispatcher-performance--kotlin--hard]] - Корутины

### Предпосылки (Легче)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Корутины
- [[q-what-is-coroutine--kotlin--easy]] - Корутины

### Хаб
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Введение в корутины

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
