---
id: cs-001
title: "Java Kotlin Abstract Classes Difference"
aliases: []
topic: computer-science
subtopics: [access-modifiers, class-features, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-inline-function-limitations--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium]
---
# Какое Главное Отличие Между Java И Kotlin Касательно Абстрактных Классов, Методов?

# Вопрос (RU)
> Какое главное отличие между Java и Kotlin касательно абстрактных классов, методов?

---

# Question (EN)
> What are the main differences between Java and Kotlin regarding abstract classes and methods?

## Ответ (RU)

Java и Kotlin оба поддерживают концепции абстрактных классов и методов, но существуют определенные различия в подходах и возможностях, связанных с этими концепциями в каждом из языков. Рассмотрим ключевые отличия: 1. Синтаксис и использование - Java использует ключевое слово abstract для объявления абстрактных классов и методов. Абстрактные методы не могут иметь реализации в абстрактном классе. - Kotlin также использует ключевое слово abstract для объявления абстрактных классов и методов. Основное отличие в том, что Kotlin поддерживает свойства которые могут быть абстрактными. 2. Наследование и реализация - Java не поддерживает множественное наследование классов поэтому классы могут наследовать только один абстрактный класс. - Kotlin вводит понятие интерфейсов которые могут содержать реализацию по умолчанию и класс может реализовывать несколько интерфейсов. Это предоставляет большую гибкость по сравнению с Java. 3. Модификаторы доступа по умолчанию - В Java, если он не указан по умолчанию он имеет уровень доступа package-private. - В Kotlin, если он не указан по умолчанию он является public.

## Answer (EN)

Both **Java** and **Kotlin** support concepts of abstract classes and methods, but there are certain differences in approaches and capabilities related to these concepts in each language.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

-
- [[q-inline-function-limitations--kotlin--medium]]
-
