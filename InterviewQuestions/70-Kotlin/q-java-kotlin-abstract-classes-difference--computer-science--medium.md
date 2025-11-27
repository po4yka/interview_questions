---
id: kotlin-300
title: "Java Kotlin Abstract Classes Difference / Главное отличие абстрактных классов в Java и Kotlin"
aliases: ["Java Kotlin Abstract Classes Difference"]
topic: kotlin
subtopics: [class-features, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c--kotlin--medium, q-inline-function-limitations--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium]
date created: Tuesday, November 25th 2025, 12:59:08 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---
# Вопрос (RU)
> Какое главное отличие между Java и Kotlin касательно абстрактных классов и методов?

---

# Question (EN)
> What is the main difference between Java and Kotlin regarding abstract classes and methods?

## Ответ (RU)

Java и Kotlin оба поддерживают абстрактные классы и методы, но ключевое отличие в том, как Kotlin сочетает абстрактные классы с моделью "final по умолчанию" и поддержкой абстрактных свойств.

Основные моменты:

1. Абстрактные свойства vs методы-доступа
   - В Java можно объявлять только абстрактные методы, но не абстрактные поля. Фактически, контракт "свойства" задается через абстрактные `get`/`set`-методы.
   - В Kotlin можно объявлять абстрактные свойства (`abstract val/var`) прямо в абстрактном классе. Подклассы обязаны их реализовать, что делает контракт более явным и выразительным по сравнению с Java.

2. Наследование и `final`/`open` по умолчанию
   - В Java классы и методы по умолчанию не `final` (если явно не указано и класс не объявлен `final`), поэтому возможность наследования и переопределения более неявна.
   - В Kotlin классы и методы по умолчанию `final`. Абстрактный класс должен быть помечен `abstract` (что делает его наследуемым), а не-абстрактные члены, которые нужно переопределять, должны быть явно помечены `open`. Это "final по умолчанию" в сочетании с абстрактными свойствами — главное практическое отличие по сравнению с Java.

3. Остальные аспекты (контекст)
   - В обоих языках нет множественного наследования классов.
   - Отличия в модификаторах доступа по умолчанию (package-private в Java vs `public` в Kotlin для верхнего уровня) и в возможностях интерфейсов (реализации по умолчанию) важны как контекст, но не являются главным отличием, о котором обычно спрашивают на собеседовании.

## Answer (EN)

Both Java and Kotlin support abstract classes and abstract methods, but the main difference lies in how Kotlin combines abstract classes with its "final by default" model and support for abstract properties.

Key points:

1. Abstract properties vs accessor methods
   - In Java, you can only declare abstract methods, not abstract fields; property-like contracts are expressed via abstract getter/setter methods.
   - In Kotlin, you can declare abstract properties (`abstract val/var`) directly in abstract classes. Subclasses must implement them, which makes the contract more explicit and expressive than in Java.

2. Inheritance and `final`/`open` defaults
   - In Java, classes and methods are not `final` by default (unless explicitly marked or the class itself is `final`), so inheritance/overriding is more implicitly available.
   - In Kotlin, classes and methods are `final` by default. An abstract class must be marked `abstract` (which makes it inheritable), and non-abstract members intended for overriding must be marked `open`. This "final by default" behavior, combined with abstract properties, is the primary practical difference from Java.

3. Other aspects (context)
   - Both languages disallow multiple inheritance of classes.
   - Differences in default access modifiers (package-private in Java vs `public` for top-level declarations in Kotlin) and richer interfaces with default implementations are important context but not the core interview-level difference.

## Дополнительные Вопросы (RU)

- В чем основное практическое преимущество абстрактных свойств в Kotlin по сравнению с абстрактными методами в Java?
- Как политика `final` по умолчанию в Kotlin влияет на проектирование иерархий абстрактных базовых классов по сравнению с Java?
- Какие распространенные ошибки встречаются при проектировании абстрактных классов в Kotlin (например, забытый `open`, смешение с интерфейсами и т.п.)?

## Follow-ups

- What is the main practical benefit of abstract properties in Kotlin compared to abstract methods in Java?
- How does Kotlin's `final`-by-default policy influence the design of abstract base class hierarchies compared to Java?
- What common mistakes occur when designing abstract classes in Kotlin (e.g., missing `open`, confusion with interfaces, etc.)?

## Ссылки (RU)

- [[c--kotlin--medium]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-inline-function-limitations--kotlin--medium]]

## Related Questions

- [[q-inline-function-limitations--kotlin--medium]]
