---
id: kotlin-102
title: "Coroutine Builders: launch, async, runBlocking / Билдеры корутин: launch, async, runBlocking"
aliases: ["Coroutine Builders: launch, async, runBlocking, Билдеры корутин: launch, async, runBlocking"]

# Classification
topic: kotlin
subtopics: [advanced, coroutines, patterns]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140029

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-data-class-detailed--kotlin--medium, q-data-sealed-usage--programming-languages--medium, q-kotlin-null-safety--programming-languages--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [coroutines, difficulty/easy, difficulty/medium, kotlin]
---
# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140029

---

# Question (EN)
> Kotlin Coroutines advanced topic 140029

## Ответ (RU)


Coroutine builders - это функции создающие и запускающие корутины. Основные builders: `launch`, `async` и `runBlocking`.

### Launch
Запускает новую корутину и возвращает Job:
```kotlin
val job = GlobalScope.launch {
    delay(1000)
    println("World!")
}
println("Hello,")
// Hello,
// (задержка 1 секунда)
// World!
```

### Async
Запускает корутину возвращающую результат через Deferred:
```kotlin
val deferred = GlobalScope.async {
    delay(1000)
    "Result"
}
println(deferred.await())  // Ждем результат
```

### runBlocking
Блокирует текущий поток до завершения:
```kotlin
runBlocking {
    delay(1000)
    println("Done")
}
// Блокируется на 1 секунду, затем выводит Done
```

### Ключевые Отличия
| Builder | Возвращает | Блокирует поток | Применение |
|---------|------------|-----------------|------------|
| launch | Job | Нет | Запустить и забыть |
| async | Deferred<T> | Нет | Нужен результат |
| runBlocking | T | Да | main(), тесты |

### Практические Примеры
```kotlin
// Запустить несколько операций
launch { operation1() }
launch { operation2() }

// Получить результаты из async
val result1 = async { fetchData1() }
val result2 = async { fetchData2() }
process(result1.await(), result2.await())

// Мост к корутинам в main
fun main() = runBlocking {
    launch { /* корутина */ }
}
```

---
---

## Answer (EN)


Coroutine builders are functions that create and start coroutines. The main builders are `launch`, `async`, and `runBlocking`.

### Launch
Starts a new coroutine and returns a Job:
```kotlin
val job = GlobalScope.launch {
    delay(1000)
    println("World!")
}
println("Hello,")
// Hello,
// (1 second delay)
// World!
```

### Async
Starts a coroutine that returns a result via Deferred:
```kotlin
val deferred = GlobalScope.async {
    delay(1000)
    "Result"
}
println(deferred.await())  // Wait for result
```

### runBlocking
Blocks the current thread until completion:
```kotlin
runBlocking {
    delay(1000)
    println("Done")
}
// Blocks for 1 second, then prints Done
```

### Key Differences
| Builder | Returns | Blocks Thread | Use Case |
|---------|---------|---------------|----------|
| launch | Job | No | Fire and forget |
| async | Deferred<T> | No | Needs result |
| runBlocking | T | Yes | main(), tests |

### Practical Examples
```kotlin
// Launch multiple operations
launch { operation1() }
launch { operation2() }

// Get results from async
val result1 = async { fetchData1() }
val result2 = async { fetchData2() }
process(result1.await(), result2.await())

// Bridge to coroutines in main
fun main() = runBlocking {
    launch { /* coroutine */ }
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

### Related (Easy)
- [[q-coroutine-scope-basics--kotlin--easy]] - Coroutines
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines
- [[q-suspend-functions-basics--kotlin--easy]] - Coroutines
- [[q-launch-vs-async--kotlin--easy]] - Coroutines

### Same Level (Easy)
- [[q-what-is-coroutine--kotlin--easy]] - Basic coroutine concepts
- [[q-coroutine-scope-basics--kotlin--easy]] - CoroutineScope fundamentals
- [[q-coroutine-delay-vs-thread-sleep--kotlin--easy]] - delay() vs Thread.sleep()
- [[q-coroutines-threads-android-differences--kotlin--easy]] - Coroutines vs Threads on Android

### Next Steps (Medium)
- [[q-suspend-functions-basics--kotlin--easy]] - Understanding suspend functions
- [[q-coroutine-dispatchers--kotlin--medium]] - Coroutine dispatchers overview
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs Context

### Advanced (Harder)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines
- [[q-coroutine-performance-optimization--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

