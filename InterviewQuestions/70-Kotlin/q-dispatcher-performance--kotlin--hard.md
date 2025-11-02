---
id: kotlin-112
title: "Dispatcher Performance and Selection / Производительность и выбор диспетчеров"
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
source_note: Comprehensive Kotlin Coroutines Guide - Question 140022

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-crossinline-keyword--kotlin--medium, q-kotlin-singleton-creation--programming-languages--easy, q-serialization-basics--programming-languages--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [coroutines, difficulty/hard, difficulty/medium, kotlin]
date created: Sunday, October 12th 2025, 3:39:12 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# Question (EN)
> Kotlin Coroutines advanced topic 140022

# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140022

---

## Answer (EN)


Dispatcher performance involves choosing the right dispatcher for the task and configuring thread pools appropriately.

### Dispatcher Types

**Dispatchers.Default**
- CPU-intensive work
- Thread pool size = CPU cores
```kotlin
withContext(Dispatchers.Default) {
    computeIntensiveOperation()
}
```

**Dispatchers.IO**
- I/O operations (network, files)
- Thread pool: 64 threads (configurable)
```kotlin
withContext(Dispatchers.IO) {
    downloadFile()
}
```

**Dispatchers.Main**
- UI updates
- Single thread
```kotlin
withContext(Dispatchers.Main) {
    updateUI()
}
```

### Performance Patterns

**1. Limited Parallelism**
```kotlin
val limited = Dispatchers.IO.limitedParallelism(4)
```

**2. Custom Dispatchers**
```kotlin
val custom = Executors.newFixedThreadPool(8)
    .asCoroutineDispatcher()
```

**3. Avoid Excessive Switching**
```kotlin
// Bad
withContext(Dispatchers.IO) { op1() }
withContext(Dispatchers.IO) { op2() }

// Good
withContext(Dispatchers.IO) {
    op1()
    op2()
}
```

---
---

## Ответ (RU)


Производительность Dispatcher включает выбор правильного dispatcher для задачи и соответствующую настройку пулов потоков.

### Типы Dispatcher

**Dispatchers.Default**
- CPU-интенсивная работа
- Размер пула потоков = ядра CPU
```kotlin
withContext(Dispatchers.Default) {
    computeIntensiveOperation()
}
```

**Dispatchers.IO**
- I/O операции (сеть, файлы)
- Пул потоков: 64 потока (настраиваемо)
```kotlin
withContext(Dispatchers.IO) {
    downloadFile()
}
```

**Dispatchers.Main**
- Обновления UI
- Один поток
```kotlin
withContext(Dispatchers.Main) {
    updateUI()
}
```

### Паттерны Производительности

**1. Ограниченный параллелизм**
```kotlin
val limited = Dispatchers.IO.limitedParallelism(4)
```

**2. Кастомные Dispatchers**
```kotlin
val custom = Executors.newFixedThreadPool(8)
    .asCoroutineDispatcher()
```

**3. Избегать чрезмерного переключения**
```kotlin
// Плохо
withContext(Dispatchers.IO) { op1() }
withContext(Dispatchers.IO) { op2() }

// Хорошо
withContext(Dispatchers.IO) {
    op1()
    op2()
}
```

---
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
- [[q-coroutine-performance-optimization--kotlin--hard]] - Coroutines
- [[q-flow-performance--kotlin--hard]] - Coroutines
- [[q-select-expression-channels--kotlin--hard]] - Coroutines
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines

### Prerequisites (Easier)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines
