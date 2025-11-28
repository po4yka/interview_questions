---
id: "20251110-165912"
title: "Unidirectional Data Flow / Unidirectional Data Flow"
aliases: ["Unidirectional Data Flow"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-state-management, c-mvp-pattern, c-architecture-patterns, c-livedata, c-mutablestate]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Unidirectional Data Flow (UDF) is an architectural principle where data always moves in a single direction through the system: from a source of truth (state) to the UI and then back via explicit events or actions. It matters because it makes data dependencies easier to track, simplifies debugging, and reduces inconsistent state compared to ad-hoc bidirectional bindings. UDF is widely used in modern UI architectures (React/Redux, MVI, Elm architecture, Flux), reactive systems, and state management libraries.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Unidirectional Data Flow (однонаправленный поток данных) — это архитектурный принцип, при котором данные движутся только в одном направлении: от источника истины (состояния) к UI и обратно через явные события или действия. Он важен тем, что упрощает отслеживание изменений данных, облегчает отладку и снижает риск рассинхронизации состояния по сравнению с произвольными двусторонними привязками. UDF широко применяется в современных UI-архитектурах (React/Redux, MVI, Elm, Flux), реактивных системах и средствах управления состоянием.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Single source of truth: Application state is centralized (or logically centralized), and the UI is a pure projection of this state.
- One-way cycle: UI does not modify state directly; instead, user interactions and events dispatch actions, which are processed (e.g., by reducers/update functions) to produce new state.
- Predictability and debuggability: Since data flows in one direction, it is easier to reason about "what caused what", enabling time-travel debugging, logging, and reliable reproduction of bugs.
- Immutability-friendly: Often combined with immutable state updates, which simplifies change detection and reduces side effects.
- Trade-off: May introduce extra boilerplate or ceremony (actions, reducers, stores), but pays off in larger, complex or reactive applications.

## Ключевые Моменты (RU)

- Единый источник истины: Состояние приложения централизовано (или логически централизовано), а UI является чистой проекцией этого состояния.
- Однонаправленный цикл: UI не изменяет состояние напрямую; пользовательские действия и события отправляют действия (actions), которые обрабатываются (например, редьюсерами/функциями обновления) и формируют новое состояние.
- Предсказуемость и отладка: Однонаправленное движение данных упрощает понимание причинно-следственных связей, поддерживает логирование, time-travel debugging и воспроизводимость ошибок.
- Удобно для неизменяемости: Часто сочетается с неизменяемыми обновлениями состояния, что упрощает отслеживание изменений и уменьшает побочные эффекты.
- Компромисс: Может приводить к дополнительному "бойлерплейту" (actions, reducers, store), но окупается в крупных, сложных или реактивных системах.

## References

- https://redux.js.org/understanding/thinking-in-redux/three-principles
- https://facebook.github.io/flux/docs/in-depth-overview
- https://guide.elm-lang.org/architecture/
