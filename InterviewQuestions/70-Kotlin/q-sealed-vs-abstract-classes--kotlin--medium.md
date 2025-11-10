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
---

# Вопрос (RU)

> В чем отличие sealed классов от абстрактных классов?

# Question (EN)

> What is the difference between sealed and abstract classes?

## Ответ (RU)

Абстрактные классы не могут быть инстанцированы напрямую и могут содержать абстрактные члены, которые должны быть реализованы в подклассах. Они задают общий базовый класс с общей реализацией и/или контрактами, но не ограничивают, где и в каком количестве могут существовать подклассы (кроме обычных правил видимости и модификаторов наследования).

Sealed-классы также не могут быть инстанцированы напрямую и по сути являются абстрактными, но их ключевая цель — ограничить иерархию: набор прямых подклассов контролируется владельцем sealed-класса и известен компилятору на этапе компиляции. В Kotlin/JVM (начиная с Kotlin 1.5) прямые подклассы sealed-класса должны находиться в том же пакете и модуле; в более ранних версиях Kotlin требовалось объявлять их в том же файле. Это ограничение позволяет компилятору выполнять исчерпывающие проверки when-выражений над такой иерархией, часто без необходимости добавлять ветку `else`.

Ключевые отличия:
- Абстрактные классы:
  - Ориентированы на разделение общей реализации/контрактов.
  - Могут иметь подклассы в любых файлах и модулях (с учётом видимости и модификаторов наследования).
  - Сами по себе не обеспечивают исчерпывающие проверки в `when`.
- Sealed-классы:
  - Ориентированы на моделирование закрытого набора вариантов.
  - Ограничивают места определения подклассов (один пакет/модуль; исторически — один файл), чтобы все варианты были известны компилятору.
  - Интегрируются с `when` для исчерпывающего сопоставления без ветки `else` при обработке всех подклассов.

## Answer (EN)

Abstract classes cannot be instantiated directly and may contain abstract members that must be implemented in subclasses. They define a common base with shared implementation and/or contracts, but do not restrict where or how many subclasses can exist (beyond normal visibility/modifier rules).

Sealed classes are also not instantiable directly and are implicitly abstract, but their key purpose is to restrict the class hierarchy: the set of direct subclasses is controlled by the sealed class owner and must be known at compile time. In Kotlin/JVM (Kotlin 1.5+), direct subclasses of a sealed class must be located in the same package and module; earlier Kotlin versions required the same file. This restriction enables exhaustive `when` expressions over sealed hierarchies, often without needing an `else` branch.

Key differences:
- Abstract classes:
  - Focus on sharing code/contracts.
  - Can have subclasses defined in arbitrary files/modules (subject to visibility and inheritance modifiers).
  - Do not by themselves enable exhaustiveness checks.
- Sealed classes:
  - Focus on modeling a closed set of variants.
  - Restrict where subclasses may be defined (same package/module; historically same file), so all variants are known to the compiler.
  - Integrate with `when` for exhaustive pattern matching without `else` when all subclasses are covered.

## Дополнительные вопросы (RU)

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

## Связанные вопросы (RU)

- [[q-kotlin-native--kotlin--hard]]
- [[q-flow-operators-map-filter--kotlin--medium]]
- [[q-select-expression-channels--kotlin--hard]]

## Related Questions

- [[q-kotlin-native--kotlin--hard]]
- [[q-flow-operators-map-filter--kotlin--medium]]
- [[q-select-expression-channels--kotlin--hard]]
