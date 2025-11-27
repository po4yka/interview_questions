---
id: kotlin-209
title: "Sealed vs Abstract Classes / Sealed против абстрактных классов"
aliases: [Abstract Classes, Class Hierarchies, Sealed Classes, Sealed vs Abstract]
topic: kotlin
subtopics: [classes, sealed-classes]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-sealed-classes, q-flow-operators-map-filter--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [abstract-classes, classes, difficulty/medium, kotlin, polymorphism, sealed-classes]
date created: Friday, October 31st 2025, 6:30:53 pm
date modified: Tuesday, November 25th 2025, 8:53:49 pm
---
# Вопрос (RU)

> В чем отличие sealed классов от абстрактных классов?

# Question (EN)

> What is the difference between sealed and abstract classes?

## Ответ (RU)

Абстрактные классы не могут быть инстанцированы напрямую и могут содержать абстрактные члены, которые должны быть реализованы в подклассах. Они задают общий базовый класс с общей реализацией и/или контрактами, но не ограничивают, где и в каком количестве могут существовать подклассы (кроме обычных правил видимости и модификаторов наследования).

Sealed-классы также не могут быть инстанцированы напрямую и по сути являются абстрактными, но их ключевая цель — ограничить иерархию: набор прямых подклассов контролируется владельцем sealed-типa и должен быть известен компилятору на этапе компиляции. Для sealed-классов и sealed-интерфейсов в актуальных версиях Kotlin (Kotlin/JVM 1.5+ и соответствующие реализации для других таргетов) прямые наследники должны находиться в том же пакете и модуле, что и sealed-тип; в более ранних версиях Kotlin требовалось объявлять их в том же файле. Это ограничение позволяет компилятору выполнять исчерпывающие проверки when-выражений над такой иерархией при условии, что `when` выражение исходит из sealed-типа и явно обрабатывает все его известные варианты, что часто позволяет обойтись без ветки `else`.

Ключевые отличия:
- Абстрактные классы:
  - Ориентированы на разделение общей реализации/контрактов.
  - Могут иметь подклассы в любых файлах и модулях (с учётом видимости и модификаторов наследования).
  - Сами по себе не обеспечивают исчерпывающие проверки в `when`.
- Sealed-классы и sealed-интерфейсы:
  - Ориентированы на моделирование закрытого набора вариантов.
  - Ограничивают места определения прямых наследников (один пакет и модуль; исторически — один файл), чтобы все варианты были известны компилятору.
  - Интегрируются с `when` для исчерпывающего сопоставления: при обработке всех прямых наследников можно не добавлять ветку `else`.

## Answer (EN)

Abstract classes cannot be instantiated directly and may contain abstract members that must be implemented in subclasses. They define a common base with shared implementation and/or contracts, but do not restrict where or how many subclasses can exist (beyond normal visibility/modifier rules).

Sealed classes are also not instantiable directly and are implicitly abstract, but their key purpose is to restrict the hierarchy: the set of direct subclasses is controlled by the sealed type owner and must be known at compile time. For sealed classes and sealed interfaces in current Kotlin versions (Kotlin/JVM 1.5+ and corresponding multiplatform targets), direct subclasses must be declared in the same package and module as the sealed type; earlier Kotlin versions required them to be in the same file. This restriction allows the compiler to perform exhaustive `when` checks over such hierarchies when the `when` is on the sealed type and all known direct subclasses/objects are handled, often making an `else` branch unnecessary.

Key differences:
- Abstract classes:
  - Focus on sharing implementation and defining contracts.
  - Can have subclasses in arbitrary files/modules (subject to visibility and inheritance modifiers).
  - Do not by themselves enable exhaustive `when` checks.
- Sealed classes and sealed interfaces:
  - Focus on modeling a closed set of variants.
  - Restrict where direct subclasses may be defined (same package and module; historically same file), so all variants are known to the compiler.
  - Integrate with `when` for exhaustive pattern matching: if all direct subclasses are covered, no `else` branch is required.

## Дополнительные Вопросы (RU)

- В чем ключевые отличия по сравнению с Java?
- Когда вы бы использовали это на практике?
- Какие распространенные ошибки стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-sealed-classes]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [[c-sealed-classes]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-kotlin-native--kotlin--hard]]
- [[q-flow-operators-map-filter--kotlin--medium]]
- [[q-select-expression-channels--kotlin--hard]]

## Related Questions

- [[q-kotlin-native--kotlin--hard]]
- [[q-flow-operators-map-filter--kotlin--medium]]
- [[q-select-expression-channels--kotlin--hard]]
