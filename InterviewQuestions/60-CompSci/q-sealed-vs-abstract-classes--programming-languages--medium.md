---
id: 20251003140308
title: What is the difference between sealed and abstract classes / В чем отличие sealed классов от абстрактных
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, sealed-classes, abstract]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/461
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-features
  - c-kotlin-advanced

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, sealed-classes, abstract-classes, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the difference between sealed and abstract classes

# Вопрос (RU)
> В чем отличие sealed классов от абстрактных

---

## Answer (EN)

Abstract classes cannot be instantiated directly and may contain abstract methods that must be implemented in subclasses. Sealed classes limit the number of subclasses that can inherit from them - all possible subclasses must be declared in the same file as the sealed class. Key differences: abstract classes can be inherited by any number of subclasses in different files and modules; sealed classes limit subclasses which must all be declared in one file. Abstract classes are used for base classes with common functionality to be implemented in subclasses; sealed classes are used for restricted class hierarchies when all possible variants are known and must be exhaustively handled. Sealed classes provide stricter compile-time type checking, making them convenient for when expressions without needing an else branch.

## Ответ (RU)

Абстрактные классы не могут быть инстанцированы напрямую и могут содержать абстрактные методы которые должны быть реализованы в подклассах. Sealed классы ограничивают количество подклассов которые могут их наследовать Все возможные подклассы должны быть объявлены в том же файле что и sealed класс. Ключевые отличия: абстрактный класс может наследоваться любым количеством подклассов которые могут находиться в разных файлах и модулях sealed класс ограничивает количество подклассов которые могут его наследовать Все подклассы должны быть объявлены в одном файле. Абстрактный класс используется для создания базовых классов с общей функциональностью которая должна быть реализована в подклассах sealed класс используется для создания ограниченных иерархий классов когда все возможные варианты известны и должны быть исчерпывающе обработаны. Sealed класс предоставляет более строгую проверку типов на этапе компиляции что делает его удобным для использования в when-выражениях без необходимости добавления ветки else

---

## Follow-ups
- How does this compare to other approaches?
- What are the performance implications?
- When should you use this feature?

## References
- [[c-kotlin-features]]
- [[c-kotlin-advanced]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-inline-functions--programming-languages--medium]]
