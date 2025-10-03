---
id: 20251003140805
title: Coroutine dispatchers / Диспетчеры корутин
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, coroutines, threading]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/214
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-coroutines
  - c-threading

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, coroutines, dispatchers, threading, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What do you know about dispatchers

# Вопрос (RU)
> Что знаешь о диспатчерах

---

## Answer (EN)

The term "dispatcher" is usually related to thread and task management mechanisms, such as **CoroutineDispatcher**.

**Main dispatcher types:**

1. **Dispatchers.Main** - used for executing coroutines on the main UI thread

2. **Dispatchers.IO** - optimized for I/O operations, such as reading and writing files, network operations, etc.

3. **Dispatchers.Default** - optimized for computational tasks requiring significant CPU resources

4. **Dispatchers.Unconfined** - a coroutine launched with this dispatcher starts execution in the current thread but only until the first suspension point; after resuming it may continue execution in another thread

Dispatchers determine which threads coroutines execute on, helping efficiently distribute tasks depending on their nature and resource requirements. Using the right dispatcher can significantly improve application performance and responsiveness.

## Ответ (RU)

Термин "диспатчер" обычно связан с механизмами управления потоками и задачами, такими как CoroutineDispatcher. Основные типы диспатчеров: Dispatchers.Main используется для выполнения корутин на главном потоке пользовательского интерфейса. Dispatchers.IO оптимизирован для работы с вводом-выводом, например чтения и записи файлов, работы с сетью и т.д. Dispatchers.Default оптимизирован для выполнения вычислительных задач, которые требуют значительных ресурсов CPU. Dispatchers.Unconfined - корутина запущенная с этим диспатчером начинает выполнение в текущем потоке но только до первой точки приостановки после возобновления она может продолжить выполнение в другом потоке. Диспатчеры определяют на каких потоках выполняются корутины помогая эффективно распределять задачи в зависимости от их характера и требований к ресурсам. Использование правильного диспатчера может значительно повысить производительность и отзывчивость приложений.

---

## Follow-ups
- How to create custom dispatchers?
- What's the difference between Dispatchers.IO and Dispatchers.Default?
- When should you use Dispatchers.Unconfined?

## References
- [[c-kotlin-coroutines]]
- [[c-threading]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-coroutines-overview--programming-languages--medium]]
- [[q-coroutine-context-essence--programming-languages--medium]]
