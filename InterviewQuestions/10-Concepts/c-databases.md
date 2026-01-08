---\
id: "20251111-223432"
title: "Databases / Databases"
aliases: ["Databases"]
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
related: ["c-database-design", "c-relational-databases", "c-room", "c-sqlite"]
created: "2025-11-11"
updated: "2025-11-11"
tags: [concept, difficulty/medium, programming-languages]
---\

# Summary (EN)

A database is an organized collection of structured or semi-structured data that is stored, managed, and accessed electronically, typically through a `Database` Management System (DBMS). Databases enable reliable data persistence, efficient querying, and concurrent access, making them critical for backend systems, mobile/desktop apps, analytics, and distributed services. Common models include relational (SQL) and non-relational (NoSQL) databases, each optimized for different access patterns, scalability needs, and consistency requirements.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

База данных — это организованное хранилище структурированных или частично структурированных данных, к которым осуществляется доступ и управление с помощью системы управления базами данных (СУБД). Базы данных обеспечивают надежное долговременное хранение, эффективные запросы и одновременный доступ к данным, поэтому критически важны для серверных систем, мобильных/десктопных приложений, аналитики и распределённых сервисов. Наиболее распространены реляционные (SQL) и нереляционные (NoSQL) модели, каждая оптимизирована под свои паттерны доступа, масштабирование и требования к согласованности.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Data models:
  - Relational (tables, rows, columns, SQL, strong schemas) vs. NoSQL (documents, key-value, wide-column, graphs) chosen based on data structure and query patterns.
- ACID and transactions:
  - Many databases support ACID properties (Atomicity, Consistency, Isolation, Durability) to guarantee correctness for concurrent operations and critical business logic.
- Query languages and APIs:
  - SQL for relational databases; query-by-API or specialized query languages for NoSQL systems (e.g., document queries, graph traversals).
- Indexing and performance:
  - Indexes (B-tree, hash, etc.) accelerate reads but add write overhead; schema and index design strongly affect latency and scalability.
- Scalability and replication:
  - Vertical scaling vs. horizontal scaling (sharding), replication for high availability, and trade-offs between strong and eventual consistency (CAP theorem).

## Ключевые Моменты (RU)

- Модели данных:
  - Реляционные (таблицы, строки, столбцы, SQL, жёсткая схема) и NoSQL (документы, key-value, wide-column, графы) выбираются исходя из структуры данных и шаблонов запросов.
- ACID и транзакции:
  - Многие СУБД обеспечивают свойства ACID (атомарность, согласованность, изоляция, долговечность), что критично для корректности конкурентных операций и бизнес-логики.
- Языки запросов и API:
  - SQL для реляционных БД; API или специализированные языки запросов для NoSQL-систем (например, документные запросы, графовые обходы).
- Индексы и производительность:
  - Индексы (B-tree, hash и др.) ускоряют чтение, но увеличивают стоимость записи; проектирование схемы и индексов сильно влияет на задержки и масштабируемость.
- Масштабирование и репликация:
  - Вертикальное и горизонтальное масштабирование (шардинг), репликация для высокой доступности и компромиссы между строгой и итоговой согласованностью (CAP-теорема).

## References

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- MySQL Documentation: https://dev.mysql.com/doc/
- MongoDB Manual: https://www.mongodb.com/docs/manual/
- `SQLite` Documentation: https://www.sqlite.org/docs.html
