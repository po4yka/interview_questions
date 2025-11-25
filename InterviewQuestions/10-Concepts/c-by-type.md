---
id: "20251110-011818"
title: "By Type / By Type"
aliases: ["By Type"]
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
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 7:48:48 am
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Summary (EN)

"By type" usually refers to organizing, selecting, or resolving program elements based on their static or runtime type. It appears in contexts such as dependency injection (resolving a bean/service by its type), reflection and introspection, overloading/overriding resolution, and collection filtering by element type. Understanding "by type" behavior is important for reasoning about how a language or framework finds the correct implementation, dependency, or object without relying on string identifiers or manual wiring.

*This concept file was auto-generated and has been enriched with concise technical context for interview preparation.*

# Краткое Описание (RU)

Термин «по типу» (by type) обычно означает организацию, выбор или разрешение элементов программы на основе их статического или динамического типа. Он используется в контекстах, таких как dependency injection (поиск/регистрация бина или сервиса по типу), рефлексия и интроспекция, разрешение перегрузок/переопределений и фильтрация коллекций по типу элементов. Понимание поведения «по типу» важно для объяснения, как язык или фреймворк находит нужную реализацию или зависимость без строковых идентификаторов и ручного связывания.

*Этот файл концепции был создан автоматически и дополнен кратким техническим контекстом для подготовки к собеседованиям.*

## Key Points (EN)

- Type-based resolution: Frameworks (e.g., DI containers) can locate dependencies by their class/interface type instead of explicit names, improving safety and reducing configuration errors.
- Overload/override selection: Many languages choose which method/function to call based on the compile-time (and sometimes runtime) type of arguments or receivers.
- Reflection and querying by type: APIs often allow discovering fields, methods, or annotations by type, enabling generic utilities and frameworks.
- Collections and filtering by type: Code may filter heterogeneous collections by element type (e.g., selecting only instances of a given interface or subclass).
- Trade-offs: Pure "by type" lookup can become ambiguous with multiple implementations of the same interface, requiring qualifiers or additional metadata.

## Ключевые Моменты (RU)

- Разрешение по типу: Фреймворки (например, DI-контейнеры) ищут зависимости по типу класса/интерфейса вместо явных имён, что повышает безопасность и снижает риск ошибок конфигурации.
- Выбор перегруженных/переопределённых методов: Во многих языках выбор вызываемого метода зависит от типов аргументов или получателя (compile-time и иногда runtime).
- Рефлексия и поиск по типу: API позволяют находить поля, методы или аннотации по типу, что упрощает создание универсальных утилит и фреймворков.
- Коллекции и фильтрация по типу: Код может фильтровать неоднородные коллекции по типу элементов (например, выбирать только экземпляры нужного интерфейса или подкласса).
- Компромиссы: Чистый поиск «по типу» может стать неоднозначным при нескольких реализациях одного интерфейса, поэтому требуются квалификаторы или дополнительная метаинформация.

## References

- Spring Framework Reference Documentation – Dependency Injection and Bean Resolution (for examples of resolving beans by type)
- Language specifications and docs for method overloading/overriding and type resolution (e.g., Java Language Specification, Kotlin Language Documentation)
