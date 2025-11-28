---
id: "20251111-223400"
title: "Cap Theorem / Cap Theorem"
aliases: ["Cap Theorem"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-distributed-systems, c-databases, c-system-design, c-microservices, c-consistency]
created: "2025-11-11"
updated: "2025-11-11"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Tuesday, November 11th 2025, 10:34:00 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Summary (EN)

CAP theorem (Consistency, Availability, Partition Tolerance) is a principle in distributed systems that states: in the presence of a network partition, a system can guarantee either consistency or availability, but not both simultaneously. It helps engineers reason about trade-offs when designing databases and distributed services, especially under failure conditions. Commonly used to compare systems like relational databases, NoSQL stores, and microservice architectures.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Теорема CAP (Consistency, Availability, Partition Tolerance) — это принцип в распределённых системах, утверждающий, что при наличии сетевого разделения система может гарантировать либо согласованность, либо доступность, но не обе одновременно. Она помогает инженерам осознанно выбирать компромиссы при проектировании баз данных и распределённых сервисов, особенно в условиях отказов сети. Часто используется для сравнения реляционных СУБД, NoSQL-систем и архитектур на основе микросервисов.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Consistency (C): All clients see the same data at the same time; reads reflect the most recent successful write.
- Availability (A): Every request receives a non-error response (success or failure) within a reasonable time, even during failures.
- Partition Tolerance (P): The system continues to operate despite arbitrary message loss or network splits between nodes.
- Trade-off under partition: When a partition occurs, a distributed system must choose to favor either consistency (CP systems) or availability (AP systems).
- Practical impact: Real-world systems are always partition-tolerant at scale; CAP guides storage/architecture choices (e.g., CP for strong consistency, AP for high availability and eventual consistency).

## Ключевые Моменты (RU)

- Consistency (C): Все клиенты видят одинаковые данные; чтения отражают последний успешно подтверждённый записью статус.
- Availability (A): Каждый запрос получает ненулевой ответ (успех или контролируемая ошибка) в разумные сроки, даже при частичных отказах.
- Partition Tolerance (P): Система продолжает работать при потере сообщений и сетевых разделениях между узлами.
- Компромисс при разделении: При сетевом разделении распределённая система вынуждена выбирать, что важнее — согласованность (CP-системы) или доступность (AP-системы).
- Практическое значение: В масштабируемых системах разделения неизбежны, поэтому CAP используется для выбора архитектуры и хранилищ (например, CP для строгой согласованности, AP для высокой доступности и «eventual consistency»).

## References

- "Brewer's CAP Theorem" talk and follow-up papers by Eric Brewer.
- "CAP Twelve Years Later: How the "Rules" Have Changed" – Eric Brewer, IEEE Computer, 2012.
- Distributed systems and NoSQL database documentation (e.g., Apache Cassandra, MongoDB, etc.) for practical CAP trade-off examples.
