---
id: "20251111-224811"
title: "Message Queues / Message Queues"
aliases: ["Message Queues"]
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

Message queues are middleware components that enable asynchronous communication between services or processes by storing messages until they are processed. They decouple senders and consumers in time and space, improving scalability, reliability, and fault tolerance of distributed systems. Commonly used in microservices, event-driven architectures, background job processing, and integrating heterogeneous systems.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Очереди сообщений — это компоненты промежуточного ПО, обеспечивающие асинхронное взаимодействие сервисов или процессов за счёт хранения сообщений до момента их обработки. Они развязывают отправителей и потребителей по времени и по местоположению, повышая масштабируемость, надёжность и отказоустойчивость распределённых систем. Часто используются в микросервисах, событийно-ориентированных архитектурах, для фоновых задач и интеграции разнородных систем.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Decoupling: Producers and consumers do not need to be online simultaneously; messages are buffered in the queue until processed.
- Asynchronous processing: Long-running or non-critical tasks (emails, reports, data processing) are offloaded from request-response paths, reducing latency.
- Reliability and durability: Messages can be persisted to ensure delivery even if services fail; supports at-least-once or at-most-once delivery semantics.
- Scalability: Multiple consumers can read from the same queue in parallel, enabling horizontal scaling and load leveling.
- Ordering and semantics: Some systems preserve message order (FIFO), and support features like dead-letter queues, retries, and visibility timeouts.

## Ключевые Моменты (RU)

- Развязка компонентов: Продюсер и потребитель не обязаны работать одновременно; сообщения буферизуются в очереди до обработки.
- Асинхронная обработка: Длительные или некритичные задачи (email, отчёты, обработка данных) выносятся из синхронного запроса, снижая задержки.
- Надёжность и устойчивость: Сообщения могут сохраняться на диск, обеспечивая доставку даже при сбоях; поддерживаются гарантии at-least-once и at-most-once.
- Масштабируемость: Несколько потребителей могут параллельно читать из одной очереди, обеспечивая горизонтальное масштабирование и выравнивание нагрузки.
- Порядок и дополнительные механизмы: Некоторые системы сохраняют порядок (FIFO) и предоставляют dead-letter очереди, ретраи, таймаут видимости и другие механизмы обработки ошибок.

## References

- RabbitMQ documentation: https://www.rabbitmq.com/documentation.html
- Apache Kafka documentation (as a distributed log often used for queue-like messaging patterns): https://kafka.apache.org/documentation/
- AWS SQS Developer Guide: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html
