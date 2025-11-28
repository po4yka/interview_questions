---
id: "20251111-224851"
title: "Database Sharding / Database Sharding"
aliases: ["Database Sharding"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-databases, c-distributed-systems, c-scaling, c-horizontal-scaling, c-partitioning]
created: "2025-11-11"
updated: "2025-11-11"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Tuesday, November 11th 2025, 10:48:51 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Database sharding is a horizontal partitioning strategy where a large logical database is split into smaller, independent pieces (shards), each stored on a separate database instance. It is used to overcome the limits of a single node by distributing load, storage, and traffic, improving scalability and availability for high-volume applications. Sharding is common in large-scale systems (e.g., social networks, e-commerce, SaaS platforms) that must handle massive datasets and high query throughput.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Database sharding (шардинг базы данных) — это стратегия горизонтального разбиения, при которой одна логическая база данных разделяется на несколько независимых фрагментов (шардов), размещённых на отдельных экземплярах БД. Она используется для преодоления ограничений одного узла за счёт распределения нагрузки, хранения и трафика, повышая масштабируемость и доступность высоконагруженных систем. Шардинг широко применяется в крупных системах (соцсети, e-commerce, SaaS), обрабатывающих большие объёмы данных и запросов.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Horizontal partitioning: Data is split by rows (e.g., by user_id, region, tenant) across shards, while each shard keeps the same schema.
- Scalability: New shards/servers can be added to handle more data and traffic when vertical scaling (bigger single machine) becomes insufficient.
- Routing and shard keys: Application or middleware uses a shard key and routing logic (hashing, range, directory) to determine which shard holds a given record.
- Isolation and fault tolerance: Issues on one shard (overload, failure) can be contained without fully impacting other shards, improving reliability.
- Trade-offs: Increases operational complexity and makes cross-shard queries, joins, and transactions harder; requires careful schema and key design.

## Ключевые Моменты (RU)

- Горизонтальное разбиение: Данные делятся по строкам (например, по user_id, региону, клиенту) между шардами при сохранении общей схемы.
- Масштабируемость: Можно добавлять новые шарды/серверы для обработки большего объёма данных и нагрузки, когда вертикальное масштабирование уже не помогает.
- Маршрутизация и shard key: Приложение или прослойка используют ключ шарда и стратегию (хэширование, диапазоны, каталог) для определения нужного шарда.
- Изоляция и отказоустойчивость: Проблемы на одном шарде (перегрузка, сбой) локализуются и не полностью выводят из строя всю систему.
- Компромиссы: Усложняет эксплуатацию и усложняет кросс-шардовые запросы, JOIN-ы и транзакции; требует тщательного выбора ключа и схемы.

## References

- https://aws.amazon.com/what-is/database-sharding/
- https://cloud.google.com/architecture/sharding-pattern
