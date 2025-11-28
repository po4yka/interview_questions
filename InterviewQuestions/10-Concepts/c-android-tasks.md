---
id: "20251110-180501"
title: "Android Tasks"
aliases: ["Android Tasks"]
summary: "Foundational concept for interview preparation"
topic: "android"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-android"
related: [c-task-backstack, c-activity-lifecycle, c-intent-flags, c-task-affinity, c-activity]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["android", "auto-generated", "concept", "difficulty/medium"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

In Android, a "task" is a collection of activities that users interact with as a single, coherent unit of work, represented in the recent apps screen as one entry. Tasks define how activities are launched, how they share history (back stack), and how navigation behaves when moving between different parts of an app or across apps. Understanding tasks is essential for implementing predictable navigation, deep links, and multi-window behavior.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

В Android «task» (задача) — это набор Activity, с которыми пользователь взаимодействует как с единой логической последовательностью действий, отображаемой в списке недавних приложений одной карточкой. Tasks определяют, как Activity запускаются, как формируется back stack и как ведёт себя навигация внутри приложения и между приложениями. Понимание задач критично для предсказуемой навигации, deep links и работы в многооконном режиме.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Task = back stack: a task is essentially a stack of activities managed by the system; the top activity is what the user currently sees.
- Launch modes and flags: activity launchMode and Intent flags (e.g., FLAG_ACTIVITY_NEW_TASK, CLEAR_TOP) directly influence task creation, reuse, and back stack behavior.
- Recent apps integration: each task appears as an entry in the Overview/Recents screen, affecting how users switch between workflows.
- Cross-app flows: tasks can contain activities from multiple apps, so incorrect configuration can lead to confusing back navigation or unintended task duplication.
- Modern navigation: when using the Navigation Component or deep links, task and back stack rules must align with the desired UX (up vs back behavior, single-activity vs multi-activity patterns).

## Ключевые Моменты (RU)

- Task как стек: задача по сути является стеком Activity, которым управляет система; верхняя Activity — то, что видит пользователь.
- Режимы запуска и флаги: launchMode Activity и флаги Intent (например, FLAG_ACTIVITY_NEW_TASK, CLEAR_TOP) определяют создание, переиспользование задач и поведение back stack.
- Экран недавних: каждая задача отображается отдельной карточкой в списке недавних приложений, влияя на переключение между сценариями работы.
- Межприложечные сценарии: одна задача может содержать Activity из разных приложений, и некорректная конфигурация может ломать ожидаемое поведение кнопки Back или дублировать задачи.
- Современная навигация: при использовании Navigation Component и deep links правила задач и back stack должны соответствовать ожидаемому UX (Up vs Back, одноактивити-архитектура и др.).

## References

- Android Developers: Activities overview — https://developer.android.com/guide/components/activities/intro-activities
- Android Developers: Tasks and Back Stack — https://developer.android.com/guide/components/activities/tasks-and-back-stack
