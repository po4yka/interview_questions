---
id: 20251003140807
title: Android async primitives / Асинхронные примитивы в Android
aliases: []

# Classification
topic: android
subtopics: [async, threading]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/290
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-threading
  - c-async-programming

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [android, async, threading, asynctask, handler, executorservice, rxjava, coroutines, android/async, android/threading, difficulty/easy, easy_kotlin, lang/ru, platform/android]
---

# Question (EN)
> What async primitives are used for data processing

# Вопрос (RU)
> Какие асинхронные примитивы используют для обработки данных

---

## Answer (EN)

Async primitives in Android are used to perform background tasks without blocking the main UI thread and ensuring smooth app operation.

**Main async primitives include:**

1. **AsyncTask** (deprecated) - Simple API for short background operations with UI updates

2. **Handler and Looper** - Low-level messaging mechanism for thread communication

3. **ExecutorService and Future** - Java concurrency framework for managing thread pools

4. **RxJava** - Reactive programming library for composing asynchronous and event-based programs

5. **Coroutines** (recommended) - Kotlin's lightweight threads for writing async code that looks synchronous

**Modern recommendation**: Use Kotlin Coroutines for most async operations in Android.

## Ответ (RU)

Асинхронные примитивы в Android используются для выполнения задач в фоновом режиме, чтобы не блокировать основной поток пользовательского интерфейса (UI) и обеспечивать плавную работу приложений. Основные асинхронные примитивы включают: AsyncTask, Handler и Looper, ExecutorService и Future, RxJava и Coroutines.

---

## Follow-ups
- Why is AsyncTask deprecated?
- When should you use WorkManager instead?
- What are the best practices for Android background processing?

## References
- [[c-android-threading]]
- [[c-async-programming]]
- [[moc-android]]

## Related Questions
- [[q-kotlin-coroutines-overview--programming-languages--medium]]
