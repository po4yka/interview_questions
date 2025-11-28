---
id: "20251110-193234"
title: "Value Classes / Value Classes"
aliases: ["Value Classes"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-data-classes, c-immutability, c-kotlin-concepts, c-memory-optimization, c-compiler-optimization]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Value classes (also known as value types) are types whose instances are represented and compared by their value rather than by object identity. They are typically immutable, may be allocated on the stack or inlined, and can be optimized away by the compiler, reducing heap allocations and indirection. In languages like Kotlin (value classes), Java (value-based classes / Project Valhalla), C# (struct), and Scala (value classes), they are used to create lightweight domain-specific types without runtime overhead.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Value-классы (value types) — это типы, экземпляры которых определяются своим значением, а не ссылочной идентичностью. Обычно они неизменяемы, могут размещаться на стеке или инлайниться в другие структуры и оптимизируются компилятором, уменьшая количество выделений в куче и косвенных обращений. В таких языках, как Kotlin (value classes), Java (value-based classes / Project Valhalla), C# (struct) и Scala (value classes), они применяются для создания лёгких доменных типов без лишних накладных расходов.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Value semantics: equality and behavior зависят от содержимого полей, а не от адреса в памяти; два значения с одинаковыми полями считаются эквивалентными.
- Performance: могут храниться инлайново (stack / внутри других объектов), что уменьшает GC pressure и улучшает cache locality по сравнению с полными объектами.
- Immutability: обычно проектируются как неизменяемые, что упрощает reasoning о коде, делает их безопасными для многопоточности и уменьшает количество ошибок.
- Domain modeling: позволяют вводить «узкие» типы (например, UserId, Email, Money) вместо примитивов, повышая типобезопасность без существенного runtime-оверхеда.
- Language constraints: в конкретных языках накладываются ограничения (например, запрет на nullable/инторнированные reference-поля, наследование, использование как generic-параметров в некоторых контекстах), которые важно знать на интервью.

## Ключевые Моменты (RU)

- Value-семантика: равенство и поведение определяются значением полей, а не адресом в памяти; два одинаковых по содержимому экземпляра считаются эквивалентными.
- Производительность: могут храниться инлайново (на стеке / внутри других объектов), что снижает нагрузку на GC и улучшает работу с кэшем по сравнению с полноценными объектами.
- Неизменяемость: обычно проектируются как immutable-типы, что упрощает понимание кода, повышает потокобезопасность и сокращает количество скрытых сайд-эффектов.
- Моделирование домена: позволяют вводить «узкие» типы (например, UserId, Email, Money) вместо примитивов, повышая типобезопасность без заметных накладных расходов во время выполнения.
- Ограничения языка: в конкретных языках действуют специальные правила (например, ограничения на поля, наследование, generic-совместимость), которые важно знать на собеседованиях.

## References

- Kotlin value classes: https://kotlinlang.org/docs/inline-classes.html
- C# struct (value types): https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/value-types
- Scala value classes: https://docs.scala-lang.org/overviews/core/value-classes.html
