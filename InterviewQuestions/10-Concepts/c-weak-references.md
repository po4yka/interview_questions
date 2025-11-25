---
id: "20251110-175512"
title: "Weak References / Weak References"
aliases: ["Weak References"]
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
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Summary (EN)

Weak references are object references that do not prevent their referents from being reclaimed by the garbage collector. They are used to hold non-essential or cache-like data so that memory can be freed when needed, helping avoid memory leaks caused by unintended strong references. Common in garbage-collected languages (e.g., Java, Kotlin, .NET), weak references provide a controlled way to reference objects without extending their lifetime.

*This concept file was auto-generated. Content enriched for clarity and interview preparation.*

# Краткое Описание (RU)

Слабые ссылки (weak references) — это ссылки на объекты, которые не препятствуют сборщику мусора освобождать эти объекты. Они используются для хранения не критичных или кэшируемых данных так, чтобы их можно было автоматически освободить при нехватке памяти, предотвращая утечки памяти из-за непреднамеренных сильных ссылок. Широко применяются в языках со сборкой мусора (например, Java, Kotlin, .NET) для контроля времени жизни объектов без его искусственного продления.

*Этот файл концепции был создан автоматически. Содержимое уточнено для целей подготовки к интервью.*

## Key Points (EN)

- Weak vs strong references: A weak reference does not keep the object alive; if only weak references remain, the garbage collector is free to reclaim the object.
- Access semantics: Accessing a weak reference may return null if the referent was collected; code must always check for null (or equivalent) before use.
- Typical uses: Implementing caches, canonicalization maps, listeners/observers, and avoiding memory leaks in long-lived components (e.g., Android contexts, GUI frameworks).
- Variants: Many runtimes also provide soft/phantom references; weak references are more aggressively collected than soft references and are visible to user code (unlike phantom references, which are for post-mortem cleanup).
- Trade-offs: Weak references improve memory usage flexibility but make object availability non-deterministic; they should not be used for critical data or logic that assumes the object always exists.

## Ключевые Моменты (RU)

- Слабые vs сильные ссылки: Слабая ссылка не удерживает объект в памяти; если на объект указывают только слабые ссылки, сборщик мусора может его освободить.
- Семантика доступа: Обращение к слабой ссылке может вернуть null, если объект уже собран; код обязан проверять на null (или эквивалент) перед использованием.
- Типичные сценарии: Реализация кэшей, структур для интернизации/канонизации значений, хранение слушателей/обработчиков событий и предотвращение утечек памяти в долгоживущих компонентах (например, контексты Android, GUI).
- Варианты: Во многих платформах есть также soft и phantom references; слабые ссылки собираются агрессивнее soft-ссылок и доступны в прикладном коде (в отличие от phantom, которые применяются для посмертной очистки).
- Компромиссы: Слабые ссылки повышают гибкость управления памятью, но делают наличие объекта недетерминированным; их нельзя использовать для критичных данных или логики, где объект должен всегда существовать.

## References

- Java Platform: java.lang.ref.WeakReference
- .NET: System.WeakReference, System.WeakReference<T>
- Official language/runtime docs for weak/soft/phantom references (Java, Kotlin/JVM, .NET)
