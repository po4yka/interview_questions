---
id: "20251110-034627"
title: "Properties / Properties"
aliases: ["Properties"]
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
related: ["c-data-classes", "c-kotlin-concepts", "c-by-type", "c-extensions", "c-lazy-initialization"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---

# Summary (EN)

In programming languages, properties are language-level constructs that expose an object's data through controlled accessors (getters/setters) instead of direct field access. They provide a clean, field-like syntax while allowing validation, lazy computation, encapsulation, and backward-compatible changes to internal representation. Properties are common in languages like C#, Kotlin, Swift, and modern frameworks that emphasize encapsulation and API stability.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

В языках программирования свойства (properties) — это языковые конструкции, которые предоставляют доступ к данным объекта через контролируемые методы доступа (getter/setter), а не прямое обращение к полям. Они сохраняют удобный синтаксис, похожий на работу с полями, при этом позволяют выполнять валидацию, ленивые вычисления, инкапсуляцию и безопасные изменения внутреннего представления. Свойства широко используются в языках C#, Kotlin, Swift и других современных экосистемах, ориентированных на устойчивые публичные API.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Encapsulation: Properties hide internal fields while exposing a stable, readable API, enabling changes to implementation without breaking callers.
- Accessors: Getters and setters (including custom logic) control read/write behavior; many languages support computed, read-only, write-only, or delegated properties.
- Validation and side effects: Setters can validate input, trigger events, update dependent state, or enforce invariants instead of blindly assigning values.
- Syntax sugar: Properties often compile down to methods/fields, providing clean syntax (`obj.size`) with method-like flexibility.
- Immutability and constraints: Properties help express immutability (e.g., `val` in Kotlin, `let` bindings, read-only properties) and restrict how and where values can change.

## Ключевые Моменты (RU)

- Инкапсуляция: Свойства скрывают внутренние поля и предоставляют стабильный, читаемый интерфейс, позволяя менять реализацию без ломки внешнего кода.
- Аксессоры: Геттеры и сеттеры (включая пользовательскую логику) управляют чтением/записью; многие языки поддерживают вычисляемые, только для чтения, только для записи или делегированные свойства.
- Валидация и побочные эффекты: Сеттеры могут проверять входные данные, генерировать события, обновлять зависимые значения и поддерживать инварианты вместо прямого присваивания.
- Синтаксический сахар: Свойства обычно компилируются в методы/поля, сочетая лаконичный синтаксис (`obj.size`) с гибкостью методов.
- Неизменяемость и ограничения: Свойства помогают выражать неизменяемость (например, `val` в Kotlin, read-only properties) и контролировать, как и где изменяются значения.

## References

- C# Properties: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/using-properties
- Kotlin Properties and Fields: https://kotlinlang.org/docs/properties.html
- Swift Properties: https://docs.swift.org/swift-book/documentation/the-swift-programming-language/properties/
