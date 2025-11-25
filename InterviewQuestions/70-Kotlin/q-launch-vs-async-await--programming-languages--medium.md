---
id: lang-053
title: "Launch Vs Async Await / Launch против Async Await"
aliases: [Launch Vs Async Await, Launch против Async Await]
topic: kotlin
subtopics: [c-coroutines, c-kotlin-coroutines-basics, coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-hot-vs-cold-flows--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [async, await, coroutines, difficulty/medium, kotlin, launch, programming-languages]
date created: Friday, October 31st 2025, 6:29:07 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---

# Вопрос (RU)
> Чем launch отличается от async/await?

# Question (EN)
> What is the difference between launch and async/await?

## Ответ (RU)

`launch` используется для запуска корутин без блокировки текущего потока, когда не требуется вернуть результат вызывающему коду. Он возвращает объект `Job` для управления корутиной (отмена, ожидание завершения через `join` и т.п.); сама корутина обычно имеет тип результата `Unit`.

`async` используется для запуска корутины, которая должна вернуть результат. Он сразу возвращает объект `Deferred<T>` (наследник `Job`), который представляет отложенный результат; сам результат получается через приостановку с помощью `await()` (или через `getCompleted()` после завершения).

Ключевые отличия:
- `launch` возвращает `Job` и обычно применяется для fire-and-forget задач (например, побочные эффекты). Неперехваченные исключения обрабатываются немедленно через `CoroutineExceptionHandler` контекста или приводят к завершению scope в соответствии с правилами структурированной конкурентности.
- `async` возвращает `Deferred<T>` и используется для конкурентного выполнения вычислений с последующим получением результата через `await()`. Исключения сохраняются внутри `Deferred` и пробрасываются при вызове `await()`/`getCompleted()`.

Оба варианта не блокируют поток и являются extension-функциями `CoroutineScope` (или могут вызываться через `GlobalScope`, что в продакшене обычно не рекомендуется). Выбор зависит от того, нужен ли результат асинхронной операции и как вы планируете обрабатывать ошибки и управлять временем жизни корутин.

Пример:
```kotlin
// launch - результат не нужен вызывающему коду
scope.launch {
    updateUI()
}

// async - результат нужен
val deferred = scope.async {
    fetchDataFromNetwork()
}
val result = deferred.await()
```

---

## Answer (EN)

`launch` is used to start a coroutine without blocking the current thread when the caller does not need a return value. It returns a `Job` used to manage the coroutine (cancellation, waiting for completion via `join`, etc.); the coroutine body itself typically has a `Unit` return type.

`async` is used to start a coroutine that is expected to produce a result. It immediately returns a `Deferred<T>` (a `Job` with a result), which represents the deferred value; you obtain the value by suspending with `await()` (or by calling `getCompleted()` after completion).

Main differences:
- `launch`: Returns a `Job` and is typically used for fire-and-forget tasks (e.g., side effects). Uncaught exceptions are handled immediately via the `CoroutineExceptionHandler` of its context or cause the parent scope to fail according to structured concurrency rules.
- `async`: Returns a `Deferred<T>` and is used for concurrent computations where you need a result via `await()`. Exceptions are captured in the `Deferred` and rethrown when `await()`/`getCompleted()` is called.

Both builders are non-blocking and are extension functions on `CoroutineScope` (or can be used with `GlobalScope`, which is generally discouraged in production). The choice depends on whether you need a result from the asynchronous operation and how you plan to handle errors and manage coroutine lifetime.

Example:
```kotlin
// launch - no result needed by the caller
scope.launch {
    updateUI()
}

// async - result needed
val deferred = scope.async {
    fetchDataFromNetwork()
}
val result = deferred.await()
```

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия этого подхода от Java?
- Когда вы бы использовали это на практике?
- Какие распространённые ошибки следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-coroutines]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [[c-coroutines]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-hot-vs-cold-flows--programming-languages--medium]]

## Related Questions

- [[q-hot-vs-cold-flows--programming-languages--medium]]
