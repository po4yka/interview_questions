---
id: "20251110-172129"
title: "Service Locator Pattern / Service Locator Pattern"
aliases: ["Service Locator Pattern"]
summary: "Foundational concept for interview preparation"
topic: "architecture-patterns"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-system-design"
related: []
created: "2025-11-10"
updated: "2025-11-10"
tags: ["architecture-patterns", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Service Locator Pattern is a creational/structural design pattern where a central registry (the "service locator") is responsible for providing instances of services to clients on demand. It abstracts how and where dependencies are obtained, often wrapping configuration or DI containers, and is sometimes used in legacy or highly pluggable systems. While it can simplify wiring in the short term, it hides dependencies, which makes testing, reasoning about code, and enforcing architecture boundaries harder compared to explicit Dependency Injection.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Service Locator Pattern — это порождающий/структурный шаблон проектирования, в котором центральный реестр ("локатор сервисов") отвечает за предоставление экземпляров сервисов по запросу клиентов. Он инкапсулирует детали получения зависимостей (конфигурация, DI-контейнеры и т.п.) и иногда используется в легаси-системах или сильно расширяемых платформах. Однако такой подход скрывает зависимости, усложняя тестирование, понимание кода и контроль архитектурных границ по сравнению с явной Dependency Injection.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Centralized registry: A Service Locator holds mappings from service identifiers or interfaces to concrete implementations and returns them on request.
- Inversion of control: Clients delegate responsibility for obtaining dependencies to the locator, but their dependencies become implicit (pulled, not injected).
- Flexibility and configurability: Implementations can be swapped or configured in one place, which may be convenient in plugin architectures or frameworks.
- Testability trade-offs: Hidden dependencies make unit tests and static analysis harder; often considered an anti-pattern in modern DI-driven architectures.
- Comparison to DI: Unlike constructor or method injection, Service Locator couples code to the locator API and obscures required dependencies, which can hurt maintainability at scale.

## Ключевые Моменты (RU)

- Централизованный реестр: Service Locator хранит соответствия между идентификаторами или интерфейсами сервисов и их реализациями и выдаёт нужный сервис по запросу.
- Инверсия управления: Клиенты перекладывают получение зависимостей на локатор, но зависимости становятся неявными (запрашиваются изнутри, а не передаются снаружи).
- Гибкость и конфигурация: Реализации можно менять и настраивать в одном месте, что может быть удобно для плагинных систем и фреймворков.
- Компромиссы тестируемости: Скрытые зависимости усложняют модульное тестирование и статический анализ; в современных архитектурах на базе DI часто рассматривается как антипаттерн.
- Сравнение с DI: В отличие от конструкторной/методной инъекции, Service Locator жёстко связывает код с API локатора и скрывает список зависимостей, что ухудшает поддерживаемость на больших системах.

## References

- https://martinfowler.com/articles/injection.html (section on Service Locator vs. Dependency Injection)
- https://martinfowler.com/articles/injection.html#UsingAServiceLocator
