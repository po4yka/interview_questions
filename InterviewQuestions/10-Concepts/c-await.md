---
id: "20251110-015045"
title: "Await"
aliases: ["Await"]
summary: "Foundational concept for interview preparation"
topic: "kotlin"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-coroutines, c-kotlin-coroutines, c-structured-concurrency, c-coroutine-context, c-flow]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "kotlin"]
date created: Monday, November 10th 2025, 7:48:48 am
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Summary (EN)

In Kotlin coroutines, `await` is a suspending operation (commonly `Deferred.await()` or `Job.join()`) that asynchronously waits for a result or completion without blocking the underlying thread. It allows structured, readable asynchronous code by suspending the coroutine until the awaited computation finishes, then resuming with the result or error. `await` is heavily used when composing multiple concurrent tasks, improving performance while keeping code sequential in style.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

В корутинах Kotlin `await` — это приостанавливающая операция (обычно `Deferred.await()` или `Job.join()`), которая асинхронно ожидает результат или завершение без блокировки потока. Она позволяет писать структурированный и читаемый асинхронный код: корутина приостанавливается до окончания вычисления, затем возобновляется с результатом или ошибкой. `await` часто используется при композиции нескольких параллельных задач, повышая производительность при сохранении последовательного стиля кода.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- `Deferred.await()` suspends the calling coroutine until the asynchronous computation completes and returns its result (or throws the underlying exception).
- `await` is non-blocking: it frees the thread to run other coroutines instead of using traditional blocking calls like `Thread.sleep` or `Future.get`.
- Commonly used with `async`/`await` pattern to start concurrent work (`async`) and later collect results (`await`) in a clear, sequential-looking style.
- Works within structured concurrency: cancellations and exceptions propagate through coroutine scopes, so `await` participates in cooperative cancellation.
- Misuse (e.g., calling `runBlocking` + `await` on main/UI thread incorrectly) can lead to deadlocks or UI freezes; prefer suspending contexts.

## Ключевые Моменты (RU)

- `Deferred.await()` приостанавливает вызывающую корутину до завершения асинхронного вычисления и возвращает результат (или пробрасывает исходное исключение).
- `await` неблокирующий: он освобождает поток для выполнения других корутин, в отличие от классических блокирующих вызовов вроде `Thread.sleep` или `Future.get`.
- Часто используется в паре `async`/`await`: `async` запускает параллельную работу, `await` позднее читает результаты в коде, выглядящем как последовательный.
- Вписывается в структурную конкуррентность: отмена и исключения распространяются по иерархии скоупов, `await` участвует в кооперативной отмене.
- Некорректное использование (например, `runBlocking` + `await` на основном/UI-потоке без необходимости) может привести к взаимоблокировкам или фризам UI; предпочтительны корректные приостанавливающие контексты.

## References

- Kotlin Coroutines Guide – Asynchronous programming with coroutines (kotlinlang.org/docs/coroutines-guide.html)
- Kotlinx Coroutines API Reference – `Deferred` and `await` (kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/)
