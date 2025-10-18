---
id: 20251012-140027
title: "launch vs async: When to Use Each / launch против async: когда использовать"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, advanced, patterns]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140027

# Workflow & relations
status: draft
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, coroutines, difficulty/medium]
---
# Question (EN)
> Kotlin Coroutines advanced topic 140027

# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140027

---

## Answer (EN)


`launch` and `async` are both coroutine builders but differ in how they return results.

### launch
Fire-and-forget style, returns Job:
```kotlin
val job = launch {
    delay(1000)
    println("Task completed")
}
job.join()  // Wait for completion
```

### async
Returns Deferred with result:
```kotlin
val deferred = async {
    delay(1000)
    "Result"
}
val result = deferred.await()  // Get result
println(result)  // "Result"
```

### Key Differences
| Feature | launch | async |
|---------|--------|-------|
| Returns | Job | Deferred<T> |
| Result | Unit | T |
| Usage | Side effects | Compute value |
| Exception | Thrown immediately | On await() |

### Choosing Between Them
```kotlin
// Use launch for side effects
launch {
    saveToDatabase(data)
}

// Use async for results
val result = async {
    fetchFromApi()
}.await()

// Parallel async
val r1 = async { fetch1() }
val r2 = async { fetch2() }
combine(r1.await(), r2.await())
```

---
---

## Ответ (RU)


`launch` и `async` оба являются coroutine builders но различаются способом возврата результатов.

### launch
Стиль запустить-и-забыть, возвращает Job:
```kotlin
val job = launch {
    delay(1000)
    println("Task completed")
}
job.join()  // Ждать завершения
```

### async
Возвращает Deferred с результатом:
```kotlin
val deferred = async {
    delay(1000)
    "Result"
}
val result = deferred.await()  // Получить результат
println(result)  // "Result"
```

### Ключевые отличия
| Функция | launch | async |
|---------|--------|-------|
| Возвращает | Job | Deferred<T> |
| Результат | Unit | T |
| Использование | Побочные эффекты | Вычислить значение |
| Исключение | Выброшено сразу | При await() |

### Выбор между ними
```kotlin
// Используйте launch для побочных эффектов
launch {
    saveToDatabase(data)
}

// Используйте async для результатов
val result = async {
    fetchFromApi()
}.await()

// Параллельный async
val r1 = async { fetch1() }
val r2 = async { fetch2() }
combine(r1.await(), r2.await())
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

### Related (Easy)
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines
- [[q-suspend-functions-basics--kotlin--easy]] - Coroutines
- [[q-coroutine-builders-basics--kotlin--easy]] - Coroutines
- [[q-coroutine-scope-basics--kotlin--easy]] - Coroutines

### Advanced (Harder)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-select-expression-channels--kotlin--hard]] - Coroutines
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines