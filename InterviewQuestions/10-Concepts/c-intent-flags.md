---
id: "20251110-153623"
title: "Intent Flags / Intent Flags"
aliases: ["Intent Flags"]
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

Intent flags are configuration constants used with Android Intents to control how activities are launched, reused, or placed in the back stack. They define task and activity behavior (e.g., whether to create a new instance, reuse an existing one, or clear history) and are critical for predictable navigation, deep links, and notification handling. Correct use of intent flags prevents duplicate screens, broken back navigation, and security issues when passing data between components.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Intent flags — это набор констант, используемых с Android Intent для управления тем, как запускаются активности, переиспользуются ли они и как размещаются в back stack. Они определяют поведение задач и активностей (создать новый экземпляр, использовать существующий, очистить историю и т.п.) и критичны для предсказуемой навигации, deep link-ов и обработки уведомлений. Корректное использование intent flags помогает избежать дубликатов экранов, некорректной «Назад» навигации и потенциальных проблем с безопасностью при передаче данных.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- FLAG_ACTIVITY_NEW_TASK / FLAG_ACTIVITY_CLEAR_TASK: Control task creation and clearing; often used for starting a fresh flow (e.g., after login) so users cannot navigate back to previous screens.
- FLAG_ACTIVITY_SINGLE_TOP / FLAG_ACTIVITY_REORDER_TO_FRONT: Reuse an existing activity instance instead of creating a new one when it is already at (or in) the top of the stack, reducing duplicates.
- FLAG_ACTIVITY_CLEAR_TOP: Brings an existing instance to the front and removes all activities above it, useful for "home" or "up" navigation patterns.
- FLAG_ACTIVITY_NO_HISTORY / FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS: Prevent specific activities from being kept in the back stack or shown in recent apps for security or UX reasons.
- Common scenarios: Handling notification clicks, deep links, authentication flows, and "logout"/"start over" actions where stack behavior must be explicitly controlled.

## Ключевые Моменты (RU)

- FLAG_ACTIVITY_NEW_TASK / FLAG_ACTIVITY_CLEAR_TASK: Управляют созданием новой задачи и очисткой текущей; часто применяются для запуска «чистого» потока (например, после логина), чтобы пользователь не мог вернуться на старые экраны.
- FLAG_ACTIVITY_SINGLE_TOP / FLAG_ACTIVITY_REORDER_TO_FRONT: Позволяют переиспользовать уже существующий экземпляр Activity вместо создания нового, если он уже на вершине (или в стеке), уменьшая дублирование экранов.
- FLAG_ACTIVITY_CLEAR_TOP: Поднимает существующую Activity наверх и удаляет все активности над ней — удобно для реализации «домой» или "up" навигации.
- FLAG_ACTIVITY_NO_HISTORY / FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS: Запрещают сохранение активности в back stack или показ в списке недавних приложений, что полезно для безопасности и улучшения UX.
- Типичные сценарии: обработка нажатий по уведомлениям, deep link-ы, аутентификационные потоки, действия "logout"/"начать заново", где важно явно контролировать поведение стека.

## References

- Android Developers: Intents and Intent Filters — https://developer.android.com/guide/components/intents-filters
- Android Developers: Tasks and Back Stack — https://developer.android.com/guide/components/activities/tasks-and-back-stack
