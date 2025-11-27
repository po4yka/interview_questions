---
id: db-001
title: Virtual tables disadvantages / Недостатки виртуальных таблиц
aliases: []

# Classification
topic: databases
subtopics: [performance]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-backend
related: [
  c-database-performance,
  c-views
]

# Timestamps
created: 2025-10-03
updated: 2025-11-11

# Tags
tags: [database, virtual-tables, views, performance, difficulty/medium, easy_kotlin, lang/ru, topic/databases]
---
# Вопрос (RU)
> Какой минус есть у виртуальных таблиц

# Question (EN)
> What are the disadvantages of virtual tables

---

## Ответ (RU)

В контексте реляционных СУБД под «виртуальными таблицами» обычно имеют в виду нематериализованные представления (логические таблицы, определённые запросом и не хранящие собственные данные). Их основные недостатки:

1. Особенности и ограничения зависят от конкретной СУБД
   - Представление / виртуальная таблица (если это не материализованное представление) не хранит свои данные, а читает их из базовых таблиц.
   - В зависимости от СУБД накладываются ограничения на работу через представление:
     - Не все представления обновляемы (INSERT/UPDATE/DELETE могут быть запрещены или ограничены).
     - В некоторых системах ограничения и триггеры на представления поддерживаются ограниченно; целостность обычно обеспечивается на базовых таблицах.
     - Специализированные механизмы «виртуальных таблиц» (например, основанные на расширениях или модулях полнотекстового поиска) могут иметь дополнительные функциональные ограничения.

2. Особенности производительности и скрытая стоимость
   - Нематериализованное представление разворачивается в определяющий его запрос при выполнении, поэтому сложные представления (особенно с множеством JOIN и агрегатами) могут:
     - Ухудшать производительность при неаккуратном использовании или глубокой вложенности.
     - Скрывать реальную «дороговизну» запроса, создавая иллюзию простой выборки.
   - Производительность зависит от оптимизатора и индексов на базовых таблицах; неверная индексация или чрезмерно сложное определение может привести к замедлению запросов.

3. Связанность с базовой схемой
   - Представления / виртуальные таблицы жёстко зависят от структуры базовых таблиц.
   - Изменения схемы (переименование столбцов, смена типов, удаление таблиц/столбцов) могут «сломать» представления или изменить их поведение.
   - Поддержка большого числа представлений усложняет эволюцию схемы, тестирование и отладку.

Итого: виртуальные таблицы (нематериализованные представления) полезны для абстракции, инкапсуляции и безопасности, но могут приводить к скрытым проблемам с производительностью, усложнять сопровождение и накладывать ограничения на модификацию данных. Их следует использовать с учётом особенностей конкретной СУБД.

## Answer (EN)

In the context of relational databases, "virtual tables" usually refer to non-materialized views (logical tables defined by a query, without their own stored data). Their main disadvantages are:

1. Discrepancies and limitations depending on DBMS implementation
   - A view/virtual table does not store its own data (unless it is a materialized view), it only reads from underlying tables.
   - Depending on the DBMS, there may be restrictions on what can be done through a view:
     - Not all views are updatable (INSERT/UPDATE/DELETE may be disallowed or limited).
     - Some systems restrict triggers or constraints defined directly on views; integrity is usually enforced on base tables.
     - Specialized "virtual table" mechanisms (e.g., extension-based or FTS modules) may have additional functional limitations.

2. Performance characteristics and hidden costs
   - Since a non-materialized view is expanded into its defining query at runtime, complex views (especially with joins and aggregations) can:
     - Degrade performance if used naïvely or nested deeply.
     - Hide the true cost of queries from developers, encouraging seemingly simple `SELECT` statements that are actually heavy.
   - Performance still depends on the optimizer and indexes on underlying tables; misconfigured indexes or overly complex definitions can make queries slower.

3. Coupling to underlying schema
   - Views/virtual tables are tightly coupled to the structure of base tables.
   - Schema changes (renaming columns, changing types, dropping tables/columns) can break views or change their semantics.
   - Maintaining a large set of views increases complexity for schema evolution, testing, and debugging.

Summary: virtual tables (non-materialized views) are useful for abstraction, encapsulation, and security, but they can introduce performance pitfalls, maintenance overhead, and limitations on data modification. They should be used with awareness of DBMS-specific behavior.

---

## Дополнительные вопросы (RU)
- В чём разница между представлениями и материализованными представлениями?
- Когда стоит использовать виртуальные таблицы вместо обычных таблиц?
- Как оптимизировать производительность виртуальных таблиц?

## Follow-ups
- What's the difference between views and materialized views?
- When should you use virtual tables vs regular tables?
- How to optimize virtual table performance?

## Ссылки (RU)
- [[c-database-performance]]
- [[c-views]]
- [[moc-backend]]

## References
- [[c-database-performance]]
- [[c-views]]
- [[moc-backend]]

## Related Questions
-