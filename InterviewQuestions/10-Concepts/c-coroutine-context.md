---
id: "20251111-073616"
title: "Coroutine Context / Coroutine Context"
aliases: ["Coroutine Context"]
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
created: "2025-11-11"
updated: "2025-11-11"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Tuesday, November 11th 2025, 7:36:16 am
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Coroutine context is a structured set of elements that defines how a coroutine runs: its dispatcher (threading), job (lifecycle), name, and other metadata. It matters because it controls scheduling, cancellation, propagation of metadata, and resource management across suspended functions. In practice (e.g., Kotlin coroutines), every coroutine has a context, and child coroutines inherit and can override parts of their parent's context.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Контекст корутины — это структурированный набор элементов, определяющих, как выполняется корутина: её диспетчер (потоки), job (жизненный цикл), имя и другие метаданные. Он важен тем, что управляет планированием, отменой, распространением метаданных и управлением ресурсами между приостанавливаемыми функциями. На практике (например, в корутинах Kotlin) у каждой корутины есть контекст, а дочерние корутины наследуют и могут переопределять части контекста родителя.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Composition of elements: A coroutine context is a set of key-value elements (e.g., Job, CoroutineDispatcher, CoroutineName) combined via "+"; each key is unique within a context.
- Dispatcher/threading: The CoroutineDispatcher in the context determines which thread or thread pool executes coroutine code (e.g., Default, IO, Main).
- Job and cancellation: The Job element controls lifecycle, structured concurrency, and cancellation; cancellation propagates through the context hierarchy.
- Inheritance and overriding: Child coroutines inherit their parent context by default, but specific elements (like dispatcher or name) can be overridden when launching.
- Context propagation: Context travels across suspension points, ensuring consistent execution environment and metadata without manually passing parameters.

## Ключевые Моменты (RU)

- Состав из элементов: Контекст корутины — это набор пар ключ-значение (Job, CoroutineDispatcher, CoroutineName и др.), объединяемых через "+"; каждый ключ уникален в пределах контекста.
- Диспетчер и потоки: Элемент CoroutineDispatcher в контексте определяет, на каком потоке или пуле потоков выполняется корутина (например, Default, IO, Main).
- Job и отмена: Элемент Job управляет жизненным циклом, структурированной конкуррентностью и отменой; отмена распространяется по иерархии контекстов.
- Наследование и переопределение: Дочерние корутины по умолчанию наследуют контекст родителя, но отдельные элементы (например, диспетчер или имя) можно переопределить при запуске.
- Пропагация контекста: Контекст переносится через точки приостановки, обеспечивая согласованную среду выполнения и метаданные без явной передачи параметров.

## References

- Kotlin Coroutines Guide: Coroutine context and dispatchers — https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html
