---
id: "20251110-181434"
title: "Adapter Pattern / Adapter Pattern"
aliases: ["Adapter Pattern"]
summary: "Foundational concept for interview preparation"
topic: "architecture-patterns"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-system-design"
related: [c-design-patterns, c-facade-pattern, c-decorator-pattern, c-composite-pattern, c-architecture-patterns]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["architecture-patterns", "auto-generated", "concept", "difficulty/medium"]
date created: Monday, November 10th 2025, 8:37:43 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Summary (EN)

Adapter Pattern is a structural design pattern that allows incompatible interfaces to work together by introducing an intermediate adapter that translates one interface into another. It helps integrate legacy systems, third-party libraries, or differently designed modules without modifying their existing code. Commonly used in large systems, API integrations, and library/framework boundaries to improve reuse and decouple clients from concrete implementations.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Паттерн Адаптер (Adapter Pattern) — это структурный шаблон проектирования, который позволяет несовместимым интерфейсам работать вместе за счёт промежуточного адаптера, преобразующего один интерфейс в другой. Он помогает интегрировать легаси-системы, сторонние библиотеки или модули с разными интерфейсами без изменения их исходного кода. Широко используется в крупных системах, интеграции API и на границах библиотек/фреймворков для повышения переиспользуемости и ослабления связности.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Defines a wrapper (adapter) that implements the target interface and delegates calls to an existing (adaptee) implementation, translating method signatures or data formats.
- Supports two common forms: Object Adapter (composition-based, preferred) and Class Adapter (inheritance-based, limited in languages without multiple inheritance).
- Enables integration with legacy code or third-party components without modifying their source, aligning with the Open/Closed Principle.
- Localizes conversion logic (protocols, DTOs, formats), simplifying clients and improving maintainability.
- Frequently appears in real-world APIs (e.g., bridging between different logging, persistence, or messaging abstractions) and is a typical interview example for structural patterns.

## Ключевые Моменты (RU)

- Определяет обёртку (адаптер), которая реализует целевой интерфейс и делегирует вызовы существующему объекту (адаптируемому), преобразуя сигнатуры методов или форматы данных.
- Поддерживает две распространённые формы: объектный адаптер (через композицию, предпочтительный) и класс-адаптер (через наследование, ограничен в языках без множественного наследования).
- Позволяет интегрировать легаси-код или сторонние компоненты без изменения их исходников, соответствует принципу открытости/закрытости.
- Локализует логику преобразования (протоколы, DTO, форматы), упрощая код клиентов и повышая сопровождаемость.
- Часто используется в реальных API (например, для стыковки разных логгеров, систем хранения или брокеров сообщений) и является типичным примером структурного шаблона на собеседованиях.

## References

- "Design Patterns: Elements of Reusable Object-Oriented Software" by Gamma, Helm, Johnson, Vlissides (GoF)
- https://refactoring.guru/design-patterns/adapter
