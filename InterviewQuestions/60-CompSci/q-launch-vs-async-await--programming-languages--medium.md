---
tags:
  - kotlin
  - coroutines
  - launch
  - async
  - await
  - easy_kotlin
  - programming-languages
difficulty: medium
---

# Чем launch отличается от async/await ?

**English**: What is the difference between launch and async/await?

## Answer

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

## Ответ

Launch используется для запуска корутин без блокировки текущего потока и без получения результата выполнения. Он возвращает объект Job для управления корутиной. Async/await запускает корутину и возвращает результат через Deferred с помощью await. Основные отличия: launch не возвращает результат и используется для асинхронных задач без необходимости результата, async/await нужен когда требуется результат. Выбор зависит от необходимости получения результата асинхронной операции.

