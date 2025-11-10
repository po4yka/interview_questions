---
id: "20251110-202702"
title: "Task Affinity / Task Affinity"
aliases: ["Task Affinity"]
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
created: "2025-11-10"
updated: "2025-11-10"
tags: ["programming-languages", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Task affinity defines the association between a task (or logical unit of work) and the specific execution context (thread, core, process, or event loop) on which it must run. It matters for correctness (e.g., UI updates restricted to a UI thread), performance (cache locality, reduced context switches), and concurrency control (avoiding data races and inconsistent state). Task affinity is commonly used in UI frameworks, coroutine libraries, asynchronous runtimes, and systems programming where tasks must consistently execute on a designated scheduler or thread.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Task affinity (аффинность задач) определяет привязку задачи (или логической единицы работы) к конкретному контексту выполнения — потоку, ядру, процессу или event loop, на котором она должна выполняться. Это важно для корректности (например, обновление UI только из UI-потока), производительности (лучшее использование кэша, меньше переключений контекста) и управления конкурентностью (избежание гонок данных и неконсистентного состояния). Task affinity широко используется в UI-фреймворках, корутинах, асинхронных рантаймах и системном программировании, где задачи должны стабильно выполняться на заданном планировщике или потоке.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Consistent execution context: A task always runs on a specific thread or scheduler (e.g., Android UI thread, main event loop), which simplifies reasoning about shared state.
- Concurrency safety: Enforcing task affinity helps prevent race conditions by ensuring that certain mutable objects are only accessed from one designated context.
- Performance and locality: Keeping a task on the same core or thread can improve cache locality and reduce overhead from context switching or migration.
- Asynchronous programming: Many coroutine/async frameworks (e.g., Kotlin coroutines dispatchers, Java Executors, event loops) expose APIs to control or preserve task affinity across suspensions.
- Design trade-offs: Strong affinity simplifies correctness but may reduce flexibility or fairness; changing or breaking affinity can introduce subtle bugs.

## Ключевые Моменты (RU)

- Стабильный контекст выполнения: Задача последовательно выполняется на определённом потоке или планировщике (например, UI-поток Android, главный event loop), что упрощает работу с общим состоянием.
- Безопасность конкурентности: Жёсткая аффинность задач помогает избегать гонок данных, гарантируя доступ к определённым изменяемым объектам только из одного контекста.
- Производительность и локальность: Сохранение задачи на том же ядре или потоке улучшает кэш-локальность и снижает накладные расходы на переключения контекста.
- Асинхронное программирование: Многие фреймворки для корутин/async (например, диспетчеры корутин Kotlin, Java Executors, event loop) предоставляют средства управления или сохранения аффинности задач при остановках и возобновлениях.
- Компромиссы в дизайне: Сильная аффинность упрощает корректность, но может снижать гибкость и равномерность распределения нагрузки; неправильное изменение аффинности приводит к трудноуловимым багам.

## References

- Android Developers: "Tasks and Back Stack" and documentation on taskAffinity attribute
- Kotlin Coroutines documentation: Dispatchers and confined execution contexts
