---
id: 20251012-1227111159
title: "Launch Vs Async Await"
topic: computer-science
difficulty: medium
status: draft
moc: moc-compSci
related: [q-visitor-pattern--design-patterns--hard, q-iterator-concept--programming-languages--easy, q-hot-vs-cold-flows--programming-languages--medium]
created: 2025-10-15
tags:
  - async
  - await
  - coroutines
  - kotlin
  - launch
  - programming-languages
---
# Чем launch отличается от async/await ?

# Question (EN)
> What is the difference between launch and async/await?

# Вопрос (RU)
> Чем launch отличается от async/await ?

---

## Answer (EN)

**launch** is used to start coroutines without blocking the current thread and without getting execution result. It returns a Job object for coroutine management.

**async/await** starts a coroutine and returns result through Deferred using await.

**Main differences:**
- **launch**: Doesn't return a result, used for fire-and-forget async tasks
- **async/await**: Returns a Deferred result, used when you need the computation result

Choice depends on whether you need the result of async operation.

**Example:**
```kotlin
// launch - no result needed
launch {
    updateUI()
}

// async - result needed
val result = async {
    fetchDataFromNetwork()
}.await()
```

---

## Ответ (RU)

Launch используется для запуска корутин без блокировки текущего потока и без получения результата выполнения. Он возвращает объект Job для управления корутиной. Async/await запускает корутину и возвращает результат через Deferred с помощью await. Основные отличия: launch не возвращает результат и используется для асинхронных задач без необходимости результата, async/await нужен когда требуется результат. Выбор зависит от необходимости получения результата асинхронной операции.

## Related Questions

- [[q-visitor-pattern--design-patterns--hard]]
- [[q-iterator-concept--programming-languages--easy]]
- [[q-hot-vs-cold-flows--programming-languages--medium]]
