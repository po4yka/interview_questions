---\
id: "20251110-160936"
title: "Usecase Pattern / Usecase Pattern"
aliases: ["Usecase Pattern"]
summary: "Foundational concept for interview preparation"
topic: "architecture-patterns"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-architecture-patterns"
related: ["c-clean-architecture", "c-architecture-patterns", "c-mvp-pattern", "c-design-patterns", "c-software-design"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [architecture-patterns, concept, difficulty/medium]
---\

# Summary (EN)

Usecase Pattern (a.k.a. Use Case Interactor or `Application` `Service` pattern) structures business logic around explicit use cases, each represented by a dedicated class or function. It separates application-specific operations ("what the system should do") from delivery mechanisms (web, mobile, CLI) and infrastructure (DB, messaging), improving clarity, testability, and maintainability. Commonly used in Clean/Hexagonal Architecture, it helps align code with business language and requirements.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Usecase Pattern (паттерн юз-кейсов, или интеракторов) организует бизнес-логику вокруг явных пользовательских сценариев, каждый из которых оформлен отдельным классом или функцией. Он отделяет прикладные операции ("что система должна делать") от слоев доставки (web, mobile, CLI) и инфраструктуры (БД, очереди), повышая понятность, тестируемость и поддерживаемость. Часто применяется в Clean/Hexagonal Architecture и помогает связать код с языком бизнеса.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Explicit use cases: Each business operation (e.g., CreateOrder, TransferMoney) is modeled as a dedicated use case/interactor, making system behavior readable and aligned with requirements.
- Layered separation: Use cases depend on domain interfaces, not frameworks or controllers, fitting well into layered/clean/hexagonal architectures and reducing coupling to infrastructure.
- Testability: Use cases can be unit-tested in isolation using in-memory adapters or mocks, enabling fast, reliable tests without hitting network or database.
- Single responsibility: Each use case encapsulates one coherent workflow (validation, domain calls, persistence orchestration), reducing God-services and controller bloat.
- Adaptability: The same use case can be reused by multiple interfaces (REST, gRPC, UI, batch jobs), supporting evolution of the system without duplicating core logic.

## Ключевые Моменты (RU)

- Явные юз-кейсы: Каждый бизнес-операция (например, CreateOrder, TransferMoney) оформляется в отдельный use case/интерактор, делая поведение системы прозрачным и согласованным с требованиями.
- Слоевое разделение: Use case-слой зависит от доменных интерфейсов, а не от фреймворков или контроллеров, органично вписывается в layered/clean/hexagonal архитектуры и уменьшает связность с инфраструктурой.
- Тестируемость: Use case-объекты легко тестировать изолированно с помощью in-memory адаптеров или моков, без реальных БД и сетей, что ускоряет и упрощает автоматические тесты.
- Принцип единственной ответственности: Каждый use case инкапсулирует одну согласованную бизнес-процедуру (валидация, вызов домена, оркестрация сохранения), предотвращая разрастание «God-service» и перегруженных контроллеров.
- Адаптируемость: Один и тот же use case может переиспользоваться разными интерфейсами (REST, gRPC, UI, batch-задачи), упрощая развитие системы без дублирования логики.

## References

- Clean Architecture and Use Case Interactors (Robert C. Martin / Uncle Bob)
- Hexagonal Architecture (Ports and Adapters) by Alistair Cockburn
