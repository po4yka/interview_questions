---
topic: android
tags:
  - android
  - async
  - asynctask
  - coroutines
  - executorservice
  - handler
  - rxjava
  - threading
difficulty: easy
status: draft
---

# Какие асинхронные примитивы используют для обработки данных?

**English**: What async primitives are used for data processing?

## Answer

Async primitives in Android are used to perform background tasks without blocking the main UI thread and ensuring smooth app operation.

**Main async primitives include:**

1. **AsyncTask** (deprecated) - Simple API for short background operations with UI updates

2. **Handler and Looper** - Low-level messaging mechanism for thread communication

3. **ExecutorService and Future** - Java concurrency framework for managing thread pools

4. **RxJava** - Reactive programming library for composing asynchronous and event-based programs

5. **Coroutines** (recommended) - Kotlin's lightweight threads for writing async code that looks synchronous

**Modern recommendation**: Use Kotlin Coroutines for most async operations in Android.

## Ответ

Асинхронные примитивы в Android используются для выполнения задач в фоновом режиме, чтобы не блокировать основной поток пользовательского интерфейса (UI) и обеспечивать плавную работу приложений. Основные асинхронные примитивы включают: AsyncTask, Handler и Looper, ExecutorService и Future, RxJava и Coroutines.

