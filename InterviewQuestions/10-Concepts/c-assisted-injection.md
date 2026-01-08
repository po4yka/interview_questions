---\
id: "20251110-171042"
title: "Assisted Injection / Assisted Injection"
aliases: ["Assisted Injection"]
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
related: ["c-dagger", "c-hilt", "c-dependency-injection", "c-koin", "c-factory-pattern"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---\

# Summary (EN)

Assisted injection is a dependency injection pattern where most dependencies are provided by the DI container, but selected arguments are supplied manually at creation time (often via a generated factory). It is used when some constructor parameters are only known at runtime (e.g., user input, IDs, configuration values) and cannot be bound statically. Assisted injection helps keep classes injectable and testable while avoiding service locators or manual wiring.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Assisted injection (ассоциированная/частично управляемая контейнером инъекция) — это паттерн внедрения зависимостей, при котором большинство зависимостей предоставляет DI-контейнер, а часть аргументов (известных только во время выполнения) передаётся вручную через фабрику. Он применяется, когда не все параметры конструктора могут быть заранее связаны в контейнере (например, пользовательский ввод, динамические идентификаторы, параметры запроса). Assisted injection позволяет сохранять классы инъецируемыми и тестируемыми без использования service locator или хаотичного ручного связывания.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Separates concerns: the DI container injects stable dependencies, while callers pass dynamic, runtime-specific values.
- Implemented via factories: frameworks like Dagger/Hilt and Guice generate or use annotated factories (e.g., `@AssistedInject`, `@AssistedFactory`) to construct objects with mixed injected and assisted parameters.
- Improves testability: dependencies remain explicit in constructors, avoiding hidden lookups and making objects easy to mock in unit tests.
- Avoids overbinding: no need to create many bindings for every possible runtime argument combination; the same factory method is reused.
- Common in Kotlin/Java backends, Android apps, and other DI-heavy systems that need per-request or per-screen objects with contextual data.

## Ключевые Моменты (RU)

- Разделяет ответственность: DI-контейнер предоставляет стабильные зависимости, а вызывающий код передаёт динамические значения, известные только в runtime.
- Реализуется через фабрики: такие фреймворки, как Dagger/Hilt и Guice, используют или генерируют фабрики (например, `@AssistedInject`, `@AssistedFactory`) для создания объектов с комбинацией инъецируемых и «ассистируемых» параметров.
- Улучшает тестируемость: все зависимости остаются явными в конструкторе, без скрытых lookup-ов, что упрощает подмену в модульных тестах.
- Избегает избыточных binding-ов: не требуется отдельная конфигурация DI под каждую комбинацию аргументов; используется одна фабрика с параметрами.
- Типичный сценарий — объекты уровня запроса, экрана или операции, которым нужны как сервисы из контейнера, так и контекстные данные (ID, конфигурация, ввод пользователя).

## References

- `Dagger` / `Hilt` documentation on `@AssistedInject` and `@AssistedFactory`
- Google Guice documentation on AssistedInject extension
