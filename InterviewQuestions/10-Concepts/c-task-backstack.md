---
id: "20251110-192639"
title: "Task Backstack / Task Backstack"
aliases: ["Task Backstack"]
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
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Task Backstack (often referred to as the task and activity back stack in Android) is the ordered history of activities or screens that belong to a logical task, defining how users navigate backward through an app. It matters because it controls user experience when pressing Back/Home, handling deep links, and switching between apps. Understanding task backstack behavior is essential for designing predictable navigation flows, handling multiple entry points, and avoiding unexpected exits or duplicated screens.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Task Backstack (часто имеющий в виду стек задач и активити в Android) — это упорядоченная история экранов/активити, которая образует логическую задачу и определяет, как пользователь возвращается назад по навигации. Это важно, потому что именно стек управляет поведением кнопки Назад/Домой, обработкой диплинков и переключением между приложениями. Понимание task backstack критично для проектирования предсказуемой навигации, работы с несколькими точками входа и избежания неожиданного выхода из приложения или дублирования экранов.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Logical task: A "task" groups activities/screens that together fulfill a user goal; the backstack preserves their order for Back navigation.
- Activity stack behavior: New activities are pushed on top; Back pops the current activity, revealing the previous one.
- Launch modes and flags: launchMode (standard, singleTop, singleTask, singleInstance) and Intent flags (e.g., FLAG_ACTIVITY_NEW_TASK, CLEAR_TOP) directly influence how tasks and their backstacks are created and reused.
- Multiple tasks: An app can participate in multiple tasks (e.g., via deep links or different entry points), so understanding when a new task is created vs. reusing an existing one is key.
- UX and correctness: Misconfigured backstack leads to broken navigation (loops, unexpected exits, multiple copies of screens), so correct configuration is a common interview topic.

## Ключевые Моменты (RU)

- Логическая задача (task): "Task" объединяет экраны/активити, которые вместе реализуют цель пользователя; backstack сохраняет их порядок для корректной навигации Назад.
- Поведение стека активити: Новые активити добавляются сверху стека; кнопка Назад снимает верхнюю активити, показывая предыдущую.
- Режимы запуска и флаги: launchMode (standard, singleTop, singleTask, singleInstance) и флаги Intent (например, FLAG_ACTIVITY_NEW_TASK, CLEAR_TOP) напрямую влияют на создание, переиспользование задач и формирование backstack.
- Несколько задач: Приложение может участвовать в нескольких задачах (через диплинки, разные точки входа), поэтому важно понимать, когда создаётся новый task, а когда используется существующий.
- UX и корректность: Неверная настройка backstack приводит к сломанной навигации (циклы, неожиданный выход, дубликаты экранов), поэтому тема часто поднимается на собеседованиях.

## References

- Android Developers: Tasks and back stack — https://developer.android.com/guide/components/activities/tasks-and-back-stack

