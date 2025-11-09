---
id: "20251109-142225"
title: "Kotlin Coroutines Basics / Kotlin Coroutines Basics"
aliases: ["Kotlin Coroutines Basics"]
summary: "Foundational concept for interview preparation"
topic: "kotlin"
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
tags: ["kotlin", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Kotlin coroutines are a lightweight concurrency framework that simplifies writing asynchronous, non-blocking code using sequential syntax. They are built on top of suspendable functions and structured concurrency, making it easier to manage background work, cancellations, and error handling compared to callbacks or raw threads. Coroutines are widely used in Android development, backend services with Ktor/Spring, and any Kotlin code that deals with I/O or parallel tasks.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Корутины в Kotlin — это легковесный механизм конкурентности, упрощающий написание асинхронного и неблокирующего кода в последовательном стиле. Они основаны на приостановимых (suspend) функциях и концепции структурированной конкурентности, что облегчает управление фоновыми задачами, отменой и обработкой ошибок по сравнению с колбэками или потоками. Корутины широко используются в Android-разработке, бэкендах на Ktor/Spring и в любом Kotlin-коде, работающем с вводом-выводом или параллельными операциями.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Lightweight vs Threads: Coroutines are much cheaper than OS threads; thousands can run in a single thread, scheduled by the coroutine dispatcher.
- Suspend functions: `suspend` functions can pause without blocking a thread, allowing asynchronous operations (e.g., network, disk) to look like normal sequential code.
- Structured concurrency: Builders like `launch`, `async`, and scopes (`CoroutineScope`, `viewModelScope`, `lifecycleScope`) ensure coroutines are tied to a lifecycle, simplifying cancellation and avoiding leaks.
- Dispatchers: `Dispatchers.Main`, `IO`, `Default`, etc. control which thread(s) coroutines run on, enabling easy switching between UI, CPU-bound, and I/O-bound work.
- Error handling: Exceptions propagate through coroutine scopes; `try/catch`, `supervisorScope`, and `CoroutineExceptionHandler` are used to handle failures predictably.

## Ключевые Моменты (RU)

- Легче потоков: Корутины гораздо дешевле системных потоков; тысячи корутин могут выполняться в одном потоке под управлением диспетчера.
- Приостановимые функции: Функции с модификатором `suspend` могут приостанавливаться без блокировки потока, позволяя писать асинхронные операции (сеть, диск) в привычном последовательном стиле.
- Структурированная конкурентность: Конструкции `launch`, `async` и скоупы (`CoroutineScope`, `viewModelScope`, `lifecycleScope`) привязывают корутины к жизненному циклу, упрощая отмену и предотвращая утечки.
- Диспетчеры: `Dispatchers.Main`, `IO`, `Default` и другие определяют, в каком потоке выполняется корутина, что упрощает переключение между UI, CPU- и I/O-нагруженными задачами.
- Обработка ошибок: Исключения распространяются по иерархии корутин; для предсказуемой обработки используются `try/catch`, `supervisorScope` и `CoroutineExceptionHandler`.

## References

- Kotlin Coroutines official guide: https://kotlinlang.org/docs/coroutines-overview.html
- kotlinx.coroutines GitHub repository: https://github.com/Kotlin/kotlinx.coroutines
