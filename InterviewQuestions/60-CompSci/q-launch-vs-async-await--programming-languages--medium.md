---
id: 20251003140804
title: Launch vs async/await / Различия между launch и async/await
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, coroutines]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/136
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-coroutines

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, coroutines, launch, async, await, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

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

## Ответ (RU)

Launch используется для запуска корутин без блокировки текущего потока и без получения результата выполнения. Он возвращает объект Job для управления корутиной. Async/await запускает корутину и возвращает результат через Deferred с помощью await. Основные отличия: launch не возвращает результат и используется для асинхронных задач без необходимости результата, async/await нужен когда требуется результат. Выбор зависит от необходимости получения результата асинхронной операции.

---

## Follow-ups
- When should you use withContext instead?
- What happens if you don't call await() on async?
- How to run multiple async operations in parallel?

## References
- [[c-kotlin-coroutines]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-coroutines-overview--programming-languages--medium]]
- [[q-coroutine-dispatchers--programming-languages--medium]]
