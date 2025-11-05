---
id: lang-053
title: "Launch Vs Async Await / Launch против Async Await"
aliases: [Launch Vs Async Await, Launch против Async Await]
topic: programming-languages
subtopics: [async-programming, concurrency, coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-hot-vs-cold-flows--programming-languages--medium, q-iterator-concept--programming-languages--easy, q-visitor-pattern--design-patterns--hard]
created: 2025-10-15
updated: 2025-10-31
tags: [async, await, coroutines, difficulty/medium, kotlin, launch, programming-languages]
date created: Friday, October 3rd 2025, 5:21:02 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---
# Чем Launch Отличается От async/await ?

# Вопрос (RU)
> Чем launch отличается от async/await ?

---

# Question (EN)
> What is the difference between launch and async/await?

## Ответ (RU)

Launch используется для запуска корутин без блокировки текущего потока и без получения результата выполнения. Он возвращает объект Job для управления корутиной. Async/await запускает корутину и возвращает результат через Deferred с помощью await. Основные отличия: launch не возвращает результат и используется для асинхронных задач без необходимости результата, async/await нужен когда требуется результат. Выбор зависит от необходимости получения результата асинхронной операции.

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

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-visitor-pattern--design-patterns--hard]]
- [[q-iterator-concept--programming-languages--easy]]
- [[q-hot-vs-cold-flows--programming-languages--medium]]
