---
id: lang-053
title: "Launch Vs Async Await / Launch против Async Await"
aliases: [Launch Vs Async Await, Launch против Async Await]
topic: kotlin
subtopics: [coroutines, c-kotlin-coroutines-basics, c-coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-coroutines, q-hot-vs-cold-flows--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [async, await, coroutines, difficulty/medium, kotlin, launch, programming-languages]
---
# Вопрос (RU)
> Чем launch отличается от async/await?

# Question (EN)
> What is the difference between launch and async/await?

## Ответ (RU)

`launch` используется для запуска корутин без блокировки текущего потока, когда не требуется вернуть результат. Он возвращает объект `Job` для управления корутиной (отмена, ожидание завершения через `join` и т.п.).

`async` используется для запуска корутины, которая должна вернуть результат. Он сразу возвращает объект `Deferred<T>`, из которого результат получается через приостановку с помощью `await()`.

Ключевые отличия:
- `launch` не возвращает результат (`Unit`) и обычно применяется для fire-and-forget задач (например, побочные эффекты), при этом неперехваченные исключения обрабатываются через `CoroutineExceptionHandler` контекста.
- `async` возвращает `Deferred<T>`, используется для конкурентного выполнения вычислений с последующим получением результата через `await()`; исключения пробрасываются при вызове `await()`.

Оба варианта не блокируют поток и должны вызываться из корректного `CoroutineScope`. Выбор зависит от того, нужен ли результат асинхронной операции и как вы планируете обрабатывать ошибки.

Пример:
```kotlin
// launch - результат не нужен
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

`launch` is used to start a coroutine without blocking the current thread when no return value is needed. It returns a `Job` object for managing the coroutine (cancellation, waiting for completion via `join`, etc.).

`async` is used to start a coroutine that is expected to produce a result. It immediately returns a `Deferred<T>`, from which you obtain the result by suspending with `await()`.

Main differences:
- `launch`: Returns `Unit`, no result value; typically used for fire-and-forget tasks (e.g., side effects). Uncaught exceptions are handled via the `CoroutineExceptionHandler` of its context.
- `async`: Returns `Deferred<T>`; used for concurrent computations where you need the result via `await()`. Exceptions are propagated when `await()` is called.

Both do not block the underlying thread and must be called from a proper `CoroutineScope`. The choice depends on whether you need a result from the asynchronous operation and how you want to handle errors.

Example:
```kotlin
// launch - no result needed
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

## Дополнительные вопросы (RU)

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

## Связанные вопросы (RU)

- [[q-hot-vs-cold-flows--programming-languages--medium]]

## Related Questions

- [[q-hot-vs-cold-flows--programming-languages--medium]]
