---
id: "20251111-081037"
title: "Composition / Composition"
aliases: ["Composition"]
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
created: "2025-11-11"
updated: "2025-11-11"
tags: ["programming-languages", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Composition is a design principle where complex behavior or structures are built by combining simpler, reusable components or objects, instead of relying on large monolithic types or deep inheritance hierarchies. It promotes flexibility, testability, and loose coupling by delegating work to contained objects through well-defined interfaces. Commonly used in object-oriented and functional programming (e.g., object composition, function composition), it underpins patterns like "composition over inheritance" and modular system design.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Композиция — это принцип проектирования, при котором сложное поведение или структуры строятся путём объединения более простых, переиспользуемых компонентов или объектов, вместо использования громоздких монолитных типов или глубокой иерархии наследования. Она повышает гибкость, тестируемость и слабую связанность, передавая выполнение задач вложенным объектам через чётко определённые интерфейсы. Широко применяется в объектно-ориентированном и функциональном программировании (например, объектная композиция, композиция функций) и лежит в основе подхода «композиция важнее наследования» и модульного проектирования.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Composition over inheritance: Prefer combining small, focused components to achieve behavior instead of extending large base classes, reducing tight coupling and fragile hierarchies.
- Object composition: One object holds references to other objects (has-a relationship) and delegates work to them, enabling easy replacement, testing, and runtime configuration.
- Function composition: Building complex operations by chaining simpler pure functions, improving readability, reuse, and reasoning about data flow.
- Encapsulation and flexibility: Implementation details remain hidden behind interfaces, allowing behavior changes without breaking callers.
- Use in design patterns: Core to patterns like Strategy, Decorator, Adapter, and Builder, which assemble behavior through composed objects.

## Ключевые Моменты (RU)

- «Композиция важнее наследования»: Предпочтительно объединять небольшие специализированные компоненты для реализации поведения, а не расширять громоздкие базовые классы, снижая жёсткую связанность и хрупкость иерархий.
- Объектная композиция: Объект содержит ссылки на другие объекты (отношение has-a) и делегирует им работу, что упрощает подмену, тестирование и конфигурацию во время выполнения.
- Композиция функций: Построение сложных операций путём последовательного применения простых чистых функций, улучшая читаемость, переиспользование и понимание потока данных.
- Инкапсуляция и гибкость: Детали реализации скрыты за интерфейсами, поэтому поведение можно менять без нарушения кода, который использует компонент.
- Использование в шаблонах проектирования: Лежит в основе паттернов Strategy, Decorator, Adapter и Builder, которые формируют поведение через композицию объектов.

## References

- "Design Patterns: Elements of Reusable Object-Oriented Software" by Gamma et al.
- "Effective Java" by Joshua Bloch (items promoting composition over inheritance)
- "Clean Code" by Robert C. Martin (principles of modular and composable design)
