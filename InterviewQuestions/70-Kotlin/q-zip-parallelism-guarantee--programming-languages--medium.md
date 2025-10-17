---
id: 20251012-154395
title: "Zip Parallelism Guarantee / Гарантия параллелизма zip"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags: - programming-languages
---
# Will zip guarantee parallel execution of 2 network requests launched for Coroutine

**English**: Will zip guarantee parallel execution of 2 network requests launched for Coroutine?

## Answer (EN)
No, zip itself does not guarantee parallelism. If you just write zip(firstCall(), secondCall()), both calls will start sequentially, and zip will just combine their results. To get parallelism: Launch both calls through async. Then pass their await() to zip.

**Detailed explanation:**

The `zip` operator is just a combining function - it waits for results and combines them. It doesn't control how the operations are executed.

**Wrong approach (sequential):**
```kotlin
// Both requests execute sequentially!
val result = zip(
    { networkCall1() },  // Executes first
    { networkCall2() }   // Executes after first completes
) { result1, result2 ->
    CombinedResult(result1, result2)
}
```

**Correct approach (parallel with async):**
```kotlin
coroutineScope {
    val deferred1 = async { networkCall1() }  // Starts immediately
    val deferred2 = async { networkCall2() }  // Starts immediately in parallel

    val result = CombinedResult(
        deferred1.await(),  // Wait for first
        deferred2.await()   // Wait for second
    )
}
```

**Alternative using structured concurrency:**
```kotlin
suspend fun getCombinedData() = coroutineScope {
    val call1 = async { networkCall1() }
    val call2 = async { networkCall2() }

    // zip-like behavior with parallel execution
    Pair(call1.await(), call2.await())
}
```

**Key point:** In Kotlin coroutines, parallelism is achieved through `async` builder, not through combining operators. The `async` launches coroutines concurrently, and `await()` collects the results.

---

## Ответ (RU)
# Вопрос (RU)
Будет ли zip гарантировать параллельность выполнения 2 запросов в сеть, запущенных для Coroutine?

## Ответ (RU)
Нет, zip сам по себе не гарантирует параллельность. Если ты просто напишешь zip(firstCall(), secondCall()), оба вызова начнутся последовательно, и zip просто объединит их результаты. Чтобы получить параллельность: - Запусти оба вызова через async. - Затем передай их await() в zip.
