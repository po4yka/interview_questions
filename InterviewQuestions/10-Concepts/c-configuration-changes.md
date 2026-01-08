---\
id: "20251110-122611"
title: "Configuration Changes / Configuration Changes"
aliases: ["Configuration Changes"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: ["c-android-lifecycle", "c-activity-lifecycle", "c-fragment-lifecycle", "c-savedinstancestate", "c-viewmodel"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---\

# Summary (EN)

In Android and other runtime environments, configuration changes are system-triggered events that occur when device or app configuration (such as screen rotation, locale, UI mode, or multi-window state) changes. They often cause an `Activity` or equivalent UI container to be destroyed and recreated so that resources and layouts can be reloaded for the new configuration. Proper handling of configuration changes is critical to preserve user state, avoid memory leaks, and ensure responsive, adaptive UIs.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

В Android и других средах выполнения configuration changes (изменения конфигурации) — это системные события, возникающие при изменении конфигурации устройства или приложения (например, поворот экрана, смена языка, изменение темы, режим split-screen). Они часто приводят к уничтожению и повторному созданию `Activity` или аналогичного UI-контейнера для переразметки и загрузки ресурсов под новую конфигурацию. Корректная обработка таких изменений критична для сохранения состояния пользователя, избежания утечек памяти и адаптивного интерфейса.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- System-driven lifecycle: Configuration changes are initiated by the system, typically causing Activity/Fragment recreation and a full lifecycle restart unless explicitly handled.
- State preservation: Developers must save and restore UI state (e.g., via onSaveInstanceState, `ViewModel`, or other state holders) to avoid data loss on rotation or other changes.
- Resource qualifiers: Different layouts, drawables, and values (land/port, night/notnight, swXXXdp, locale) are automatically selected based on the current configuration.
- Handling strategies: Options include relying on default recreation, using architecture components (`ViewModel`, LiveData/Flow), or selectively handling changes via configuration flags (e.g., configChanges) when appropriate.
- Common pitfalls: Ignoring configuration changes can lead to crashes, duplicated network calls, memory leaks, or inconsistent UI after rotation or theme/locale changes.

## Ключевые Моменты (RU)

- Управление жизненным циклом: Изменения конфигурации инициируются системой и обычно приводят к пересозданию Activity/Fragment с повторным прохождением жизненного цикла, если их явно не переопределять.
- Сохранение состояния: Разработчик обязан сохранять и восстанавливать состояние UI (например, через onSaveInstanceState, `ViewModel` или другие хранилища состояния), чтобы избежать потери данных при повороте экрана и других изменениях.
- Квалификаторы ресурсов: Разные layout, drawable и values (land/port, night/notnight, swXXXdp, locale) автоматически выбираются в зависимости от текущей конфигурации.
- Стратегии обработки: Можно опираться на стандартное пересоздание, использовать архитектурные компоненты (`ViewModel`, LiveData/Flow) или выборочно обрабатывать изменения через флаги конфигурации (например, configChanges), когда это оправдано.
- Типичные ошибки: Игнорирование configuration changes приводит к падениям, дублирующимся запросам, утечкам памяти и некорректному UI после поворота, смены темы или локали.

## References

- Android Developers: "Handle configuration changes" (developer.android.com)

