---\
id: "20251110-134624"
title: "Context / Context"
aliases: ["Context"]
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
related: ["c-activity", "c-application-class", "c-fragments", "c-memory-leaks", "c-android-basics"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---\

# Summary (EN)

In programming languages, "context" is the surrounding information that gives meaning to code: available variables, scope, types, configuration, execution environment, and user/session data. It is essential for making functions and components behave correctly without hard-coding global state, and is widely used in areas like dependency injection, request handling, coroutines, concurrency, and configuration management.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

В языках программирования «контекст» — это окружающая информация, которая придаёт смысл коду: доступные переменные, области видимости, типы, конфигурация, окружение выполнения, данные пользователя/сессии. Контекст важен для корректного поведения функций и компонентов без жёсткой привязки к глобальному состоянию и широко используется в DI, обработке запросов, корутинах, конкуренции и управлении конфигурацией.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Execution/scope context: Defines which identifiers (variables, functions, types) are visible and how name resolution works (e.g., lexical scope, closures, this/receiver).
- Environmental context: `Provides` runtime data such as configuration, locale, authentication, and request metadata, often passed as context objects instead of globals.
- Concurrency and async context: Propagates cancellation, deadlines, and metadata across threads/coroutines (e.g., Go's context.`Context`, Kotlin CoroutineContext).
- Dependency/context injection: Frameworks supply dependencies and settings through a context (e.g., application/context objects in DI containers and web frameworks).
- Design trade-offs: Good context usage improves modularity and testability; abusing context (overloaded or implicit) reduces clarity and makes code harder to reason about.

## Ключевые Моменты (RU)

- Контекст выполнения/области видимости: Определяет, какие идентификаторы (переменные, функции, типы) видимы и как разрешаются имена (лексическая область, замыкания, this/receiver).
- Контекст окружения: Предоставляет данные рантайма — конфигурацию, локаль, аутентификацию, метаданные запроса — обычно через объекты контекста вместо глобальных переменных.
- Контекст конкуренции и асинхронности: Передаёт отмену, дедлайны и метаданные между потоками/корутинами (например, context.`Context` в Go, CoroutineContext в Kotlin).
- Контекст в DI и фреймворках: Фреймворки предоставляют зависимости и настройки через контекст (application/context-объекты в DI-контейнерах и веб-фреймворках).
- Компромиссы дизайна: Грамотное использование контекста повышает модульность и тестируемость; чрезмерный или неявный контекст ухудшает читаемость и усложняет понимание кода.

## References

- Go context package: https://pkg.go.dev/context
- Kotlin coroutines CoroutineContext: https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html
- Android `Context` overview: https://developer.android.com/reference/android/content/Context
