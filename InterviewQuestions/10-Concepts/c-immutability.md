---
id: "20251110-165852"
title: "Immutability / Immutability"
aliases: ["Immutability"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-functional-programming, c-data-classes, c-value-classes, c-kotlin-concepts]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Immutability is a property of data or objects whose state cannot be changed after creation. It improves correctness and reasoning about code by eliminating side effects, and is heavily used in functional programming, concurrent systems, and value types in languages like Kotlin, Java, Scala, and Python. Immutability simplifies debugging, enables safe sharing across threads, and supports optimizations such as caching and structural sharing.

*This concept file was auto-generated and enriched for interview preparation.*

# Краткое Описание (RU)

Immutability (иммутабельность) — это свойство данных или объектов, состояние которых не может быть изменено после создания. Оно повышает корректность и предсказуемость кода за счёт отсутствия побочных эффектов и широко используется в функциональном программировании, многопоточных системах и при работе со значимыми типами в языках вроде Kotlin, Java, Scala и Python. Иммутабельность упрощает отладку, позволяет безопасно разделять данные между потоками и даёт возможности для оптимизаций, таких как кэширование и структурное разделение.

*Этот файл концепции был создан автоматически и дополнен для подготовки к собеседованиям.*

## Key Points (EN)

- Immutable vs mutable: Immutable values cannot be modified; updates are modeled by creating new values, while mutable values allow in-place changes.
- Thread-safety: Immutable objects are inherently thread-safe and can be freely shared without synchronization, reducing concurrency bugs.
- Functional style: Immutability is a core principle of functional programming, enabling referential transparency and easier reasoning about functions.
- Performance trade-offs: Creating new objects instead of mutating can be more expensive, but is often mitigated by persistent data structures and structural sharing.
- Practical usage: Prefer immutable data for DTOs, configuration, domain values, and public APIs; use controlled mutability internally where performance or stateful behavior is required.

## Ключевые Моменты (RU)

- Иммутабельные vs мутабельные: Иммутабельные значения не изменяются; «изменения» моделируются созданием новых значений, тогда как мутабельные объекты позволяют менять состояние на месте.
- Потокобезопасность: Иммутабельные объекты по своей природе потокобезопасны и могут свободно разделяться между потоками без дополнительной синхронизации, снижая количество ошибок конкуренции.
- Функциональный стиль: Иммутабельность — базовый принцип функционального программирования, обеспечивающий ссылочную прозрачность и более простое рассуждение о поведении функций.
- Производственные компромиссы: Создание новых объектов вместо изменений «на месте» может быть дороже, но это компенсируется персистентными структурами данных и структурным разделением.
- Практическое применение: Отдавайте приоритет иммутабельным данным для DTO, конфигураций, доменных значений и публичных API; используйте контролируемую мутабельность внутри модулей там, где нужны производительность или состояние.

## References

- https://kotlinlang.org/docs/basic-syntax.html#variables
- https://docs.oracle.com/javase/tutorial/essential/concurrency/immutable.html
- https://en.wikipedia.org/wiki/Immutable_object

