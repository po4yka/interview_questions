---
id: "20251110-133438"
title: "Architecture Patterns / Architecture Patterns"
aliases: ["Architecture Patterns"]
summary: "Foundational concept for interview preparation"
topic: "architecture-patterns"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-system-design"
related: [c-mvvm, c-mvp-pattern, c-clean-architecture, c-design-patterns, c-repository-pattern]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["architecture-patterns", "auto-generated", "concept", "difficulty/medium"]
date created: Monday, November 10th 2025, 8:37:43 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Summary (EN)

Architecture patterns are reusable, high-level templates that define the overall structure and interaction style of software systems (e.g., layered, microservices, event-driven). They provide proven ways to organize components, manage dependencies, and address recurring concerns such as scalability, maintainability, and deployment. In interviews, they are used to assess your ability to choose appropriate system structures, reason about trade-offs, and align design with business and non-functional requirements.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Архитектурные паттерны — это многократно используемые высокоуровневые шаблоны, определяющие общую структуру и стиль взаимодействия компонентов системы (например, слоистая архитектура, микросервисы, событийно-ориентированная архитектура). Они предоставляют проверенные подходы к организации модулей, управлению зависимостями и решению типичных задач, таких как масштабируемость, сопровождаемость и развертывание. На собеседованиях их используют, чтобы оценить умение выбирать подходящую архитектуру, понимать компромиссы и увязывать дизайн с бизнес- и нефункциональными требованиями.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Common patterns: layered (n-tier), hexagonal/ports-and-adapters, microservices, modular monolith, event-driven, client-server, SOA.
- Each pattern embodies specific trade-offs across scalability, complexity, deployment, operational overhead, and team structure.
- Choice of architecture pattern should be driven by business domain, change frequency, team skills, operational maturity, and non-functional requirements (latency, availability, throughput, compliance).
- Patterns can be combined (e.g., microservices + event-driven communication + hexagonal boundaries) but over-engineering increases cognitive and operational cost.
- Strong candidates can explain why a simpler pattern (e.g., well-structured monolith) may be preferable to microservices in many cases.

## Ключевые Моменты (RU)

- Распространённые паттерны: слоистая (n-tier), гексагональная/ports-and-adapters, микросервисы, модульный монолит, событийно-ориентированная архитектура, клиент-сервер, SOA.
- Каждый паттерн задаёт свои компромиссы по масштабируемости, сложности, развертыванию, операционным затратам и структуре команд.
- Выбор архитектуры должен определяться бизнес-доменом, частотой изменений, навыками команды и нефункциональными требованиями (задержка, доступность, пропускная способность, регуляторные ограничения).
- Паттерны можно комбинировать (например, микросервисы + событийное взаимодействие + гексагональные границы), но избыточная сложность повышает когнитивную и операционную нагрузку.
- Сильный кандидат может обосновать, почему более простая архитектура (например, структурированный монолит) во многих случаях лучше микросервисов.

## References

- "Patterns of Enterprise Application Architecture" — Martin Fowler
- "Software Architecture Patterns" — Mark Richards (O'Reilly)
- https://martinfowler.com/articles/microservices.html
