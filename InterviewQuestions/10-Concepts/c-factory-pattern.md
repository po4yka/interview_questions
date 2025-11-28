---
id: "20251110-171655"
title: "Factory Pattern / Factory Pattern"
aliases: ["Factory Pattern"]
summary: "Foundational concept for interview preparation"
topic: "architecture-patterns"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-system-design"
related: [c-builder-pattern, c-singleton-pattern, c-design-patterns, c-dependency-injection, c-abstract-factory]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["architecture-patterns", "auto-generated", "concept", "difficulty/medium"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Factory Pattern is a creational design pattern that encapsulates object creation logic behind a dedicated method or class instead of calling constructors directly. It helps decouple client code from concrete implementations, making it easier to switch, extend, or configure products without changing callers. Commonly used when you have multiple implementations of an interface, conditional creation logic, or need to centralize instantiation policy.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Паттерн Фабрика (Factory Pattern) — это порождающий шаблон проектирования, выносящий логику создания объектов в отдельный метод или класс вместо прямого вызова конструкторов. Он ослабляет связность между клиентским кодом и конкретными реализациями, упрощая замену, расширение и конфигурирование создаваемых объектов без изменений в вызывающем коде. Чаще всего используется при наличии нескольких реализаций интерфейса, сложных или условных правил создания и необходимости централизовать политику инстанцирования.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Encapsulates creation: Moves object construction into a factory method/class, hiding concrete types and constructor details from the client.
- Promotes loose coupling: Clients depend on abstractions (interfaces/base classes) instead of specific implementations, improving testability and flexibility.
- Centralized decision logic: Factory can select implementation based on input parameters, configuration, environment, or runtime conditions.
- Supports extensibility: New product types can often be introduced with minimal changes to existing client code (open/closed principle).
- Common variants: Includes simple factory, Factory Method, and Abstract Factory, each addressing different levels of flexibility and complexity.

## Ключевые Моменты (RU)

- Инкапсулирует создание: Переносит создание объектов в фабричный метод/класс, скрывая конкретные типы и детали конструкторов от клиента.
- Ослабляет связность: Клиент опирается на абстракции (интерфейсы/базовые классы), а не на конкретные реализации, что улучшает тестируемость и гибкость.
- Централизует выбор реализации: Фабрика выбирает нужную реализацию по параметрам, конфигурации, окружению или условиям во время выполнения.
- Облегчает расширение: Новые типы продуктов можно добавить с минимальными изменениями клиентского кода (принцип открытости/закрытости).
- Распространённые варианты: Простой фабричный метод, Factory Method и Abstract Factory, применяемые для разных уровней гибкости и сложности.

## References

- "Design Patterns: Elements of Reusable Object-Oriented Software" by Gamma, Helm, Johnson, Vlissides (Factory Method / Abstract Factory chapters)
- https://refactoring.guru/design-patterns/factory-method
- https://refactoring.guru/design-patterns/abstract-factory
