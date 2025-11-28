---
id: "20251110-002819"
title: "Inheritance / Inheritance"
aliases: ["Inheritance"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-oop-concepts, c-polymorphism, c-composition, c-interfaces, c-abstract-classes]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 7:48:48 am
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Inheritance is an object-oriented programming mechanism that allows a class (subclass/child) to reuse, extend, or modify the behavior and data of another class (superclass/parent). It enables hierarchical modeling of domains, promotes code reuse, and supports polymorphism through substitutability (using a child wherever a parent is expected). In practice, inheritance should model "is-a" relationships (e.g., Square is-a Shape) and be used judiciously to avoid tight coupling.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Наследование — это механизм объектно-ориентированного программирования, позволяющий классу (подклассу/потомку) переиспользовать, расширять или изменять данные и поведение другого класса (суперкласса/родителя. Оно используется для иерархического моделирования предметной области, повышения повторного использования кода и поддержки полиморфизма за счёт подстановки потомка везде, где ожидается родитель. Наследование должно отражать отношения типа "является" (например, Square является Shape) и применяться осторожно, чтобы избегать сильного зацепления.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- "Is-a" relationship: Use inheritance when the subclass is a specialized form of the superclass (e.g., `Cat` extends `Animal`), not just to share code.
- Code reuse and extension: Child classes inherit fields and methods and can add new members or override existing ones to customize behavior.
- Polymorphism: References of a base type can point to objects of derived types, enabling dynamic dispatch (calling overridden methods at runtime).
- Access control: Visibility modifiers (e.g., `public`, `protected`) determine which superclass members are available to subclasses.
- Design trade-offs: Overuse or incorrect hierarchies lead to brittle, tightly coupled designs; prefer composition over inheritance when the relationship is "has-a" or behavior must vary independently.

## Ключевые Моменты (RU)

- Отношение «является»: Наследование применяют, когда подкласс является специализированным вариантом суперкласса (например, `Cat` расширяет `Animal`), а не только ради общего кода.
- Повторное использование и расширение: Потомок наследует поля и методы, может добавлять новые элементы и переопределять существующие для изменения поведения.
- Полиморфизм: Переменные базового типа могут ссылаться на объекты производных классов, что позволяет динамически вызывать переопределённые методы во время выполнения.
- Управление доступом: Модификаторы видимости (например, `public`, `protected`) определяют, какие члены суперкласса доступны в подклассах.
- Компромиссы в дизайне: Чрезмерное или неверное использование иерархий делает код хрупким и тесно связанным; в случаях отношений «имеет» или независимой вариации поведения часто предпочтительна композиция вместо наследования.

## References

- https://en.wikipedia.org/wiki/Inheritance_(object-oriented_programming)
- Documentation for specific languages on inheritance (e.g., "Classes and Inheritance" in official Java, C#, Kotlin, or C++ docs)
