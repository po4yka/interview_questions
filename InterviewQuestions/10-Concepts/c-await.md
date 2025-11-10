---
id: "20251109-230632"
title: "Await / Await"
aliases: ["Await"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: []
created: "2025-11-09"
updated: "2025-11-09"
tags: ["programming-languages", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

"await" is an operator/keyword used in asynchronous programming to suspend execution of the current function until an awaited asynchronous operation (promise/future/deferred) completes, without blocking the underlying thread. It simplifies callback-based code into a sequential style, improving readability and error handling. Commonly used in languages like JavaScript (async/await), C#, and Kotlin coroutines.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

"await" — это оператор/ключевое слово для асинхронного программирования, которое приостанавливает выполнение текущей функции до завершения ожидаемой асинхронной операции (promise/future/deferred), не блокируя поток. Оно упрощает код с колбэками до последовательного стиля, повышая читаемость и упрощая обработку ошибок. Широко используется в языках JavaScript (async/await), C# и корутинах Kotlin.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Requires an async context: "await" can only be used inside functions or blocks marked for async/coroutine execution (e.g., async function, suspend function).
- Non-blocking semantics: Suspends the current coroutine/task while allowing the underlying thread or event loop to process other work.
- Error propagation: Exceptions from the awaited operation are rethrown at the await site, making error handling similar to synchronous code (try/catch around await).
- Sequential style over callbacks: Allows writing asynchronous steps in order (top-to-bottom) instead of nesting callbacks or using explicit continuations.
- Awaiting multiple tasks: Often combined with constructs like Promise.all / Task.WhenAll / async combinators to run operations concurrently while awaiting their results.

## Ключевые Моменты (RU)

- Требует асинхронного контекста: "await" может использоваться только внутри функций или блоков, объявленных как async/корутины (например, async-функция, suspend-функция).
- Неблокирующая семантика: Приостанавливает текущую корутину/задачу, позволяя потоку или цикл обработки событий выполнять другую работу.
- Проброс ошибок: Исключения из ожидаемой операции пробрасываются в точке await, что позволяет обрабатывать их как в синхронном коде (try/catch вокруг await).
- Последовательный стиль вместо колбэков: Позволяет писать асинхронные шаги линейно (сверху вниз), избегая вложенных колбэков и явных продолжений.
- Ожидание нескольких задач: Часто используется вместе с конструкциями вроде Promise.all / Task.WhenAll / асинхронными комбинаторами для параллельного запуска операций и ожидания их результатов.

## References

- MDN Web Docs: JavaScript async/await
- Microsoft Docs: Asynchronous programming with async and await in C#
- Kotlin Documentation: Coroutines and suspend functions
