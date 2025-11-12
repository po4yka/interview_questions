---
id: db-004
title: Database migration purpose / Цель миграции баз данных
aliases: []

# Classification
topic: databases
subtopics: [migration]
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
  c-database-design,
  c-migrations
]

# Timestamps
created: 2025-10-03
updated: 2025-11-11

# Tags
tags: [database, migration, schema-evolution, difficulty/medium, easy_kotlin, lang/ru, topic/databases]
---

# Вопрос (RU)
> Что такое миграция баз данных и для чего она нужна

# Question (EN)
> What is database migration and what is it used for

---

## Ответ (RU)

Миграция баз данных — это контролируемый, повторяемый процесс изменения структуры или данных базы данных (например, добавление или изменение таблиц, столбцов, индексов, ограничений, трансформация данных) с сохранением целостности данных и корректной работы приложений при переходе между версиями.

Миграции, как правило, версионируются и применяются последовательно, чтобы:
- любое окружение (dev, staging, production) можно было привести к нужной версии схемы,
- изменения были отслеживаемыми, тестируемыми и часто обратимыми.

Зачем нужны миграции:
- Улучшение производительности (например, добавление индексов, оптимизация схемы)
- Масштабирование и повышение надежности (например, шардинг, партиционирование, рефакторинг схемы)
- Обновление систем и схемы (поддержка новых версий СУБД или новых возможностей)
- Интеграция новых функций приложения, требующих изменений схемы или данных
- Соответствие требованиям регуляторов и корпоративным стандартам (добавление обязательных полей и т.п.)

Цели миграций включают:
- Обеспечение безопасной эволюции схемы без потери данных
- Сохранение обратной совместимости при развертывании, когда это необходимо
- Поддержание согласованности и воспроизводимости всех окружений

Миграции обеспечивают плавную и предсказуемую эволюцию схемы и данных при сохранении целостности и функциональности приложений.

## Answer (EN)

Database migration is a controlled, repeatable process of changing the structure or data of a database (for example, adding or modifying tables, columns, indexes, constraints, or transforming data) while preserving data integrity and keeping applications working correctly across versions.

Migrations are usually versioned and applied sequentially so that:
- any environment (dev, staging, production) can be brought to a specific schema version,
- changes are traceable, testable, and often reversible.

Why migrations are needed:
- Performance improvements (e.g., adding indexes, optimizing schemas)
- Scaling and reliability (e.g., sharding, partitioning, refactoring schemas)
- System and schema upgrades (e.g., adapting to new features or database versions)
- Integration of new application features that require schema or data changes
- Compliance and governance (e.g., storing additional fields required by regulations)

Migration goals include:
- Ensuring safe schema evolution without data loss
- Maintaining backward compatibility during deployments when needed
- Keeping all environments consistent and reproducible

Migrations ensure smooth, predictable schema and data evolution while preserving data integrity and application functionality.

---

## Дополнительные вопросы (RU)
- Какие существуют стратегии миграции (big bang vs incremental)?
- Как обрабатывать откаты миграций?
- Какие инструменты доступны для миграций баз данных?

## Follow-ups
- What are migration strategies (big bang vs incremental)?
- How to handle migration rollbacks?
- What tools are available for database migrations?

## Ссылки (RU)
- [[c-database-design]]
- [[c-migrations]]
- [[moc-backend]]

## References
- [[c-database-design]]
- [[c-migrations]]
- [[moc-backend]]

## Related Questions

### Related (Medium)
- [[q-virtual-tables-disadvantages--databases--medium]] - Databases
- [[q-relational-table-unique-data--databases--medium]] - Databases
- [[q-kapt-ksp-migration--android--medium]] - Kapt
- [[q-callback-to-coroutine-conversion--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-sql-join-algorithms-complexity--databases--hard]] - Databases
