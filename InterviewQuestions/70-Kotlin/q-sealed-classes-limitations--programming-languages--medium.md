---
id: lang-025
title: "Sealed Classes Limitations"
aliases: [Sealed Classes Limitations, Ограничения Sealed Классов]
topic: kotlin
subtopics: [sealed-classes, oop, class-hierarchy]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-sealed-classes, q-what-is-flow--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [class-hierarchy, difficulty/medium, kotlin, programming-languages, sealed-classes]
---
# Вопрос (RU)
> Какие есть ограничения у sealed классов?

---

# Question (EN)
> What are the limitations of sealed classes?

## Ответ (RU)

Основные ограничения sealed классов (и интерфейсов) в Kotlin:

- Ограниченный контроль наследования: наследниками sealed класса/интерфейса могут быть только типы, явно объявленные как его подтипы в разрешённых местах (в том же файле — для ранних версий Kotlin; в современных версиях — в том же модуле и в том же пакете, либо в том же файле, в зависимости от синтаксиса объявления).
- Нельзя свободно расширять иерархию извне: вы не можете сделать произвольный наследник sealed типа в другом ("чужом") модуле/пакете/файле, поэтому иерархия жёстко фиксирована.
- Sealed класс сам по себе не может быть final (по смыслу он задаёт закрытую, но расширяемую внутри ограниченной области иерархию) и используется именно для контролируемого полиморфизма.
- Подтипы должны удовлетворять правилам видимости и места объявления для sealed типов; это делает архитектуру более жёсткой и иногда усложняет рефакторинг или разделение по модулям.

Важно:
- Sealed классы по сути абстрактны (нельзя создать экземпляр sealed класса напрямую без конкретного подтипа).
- В Kotlin также существуют sealed интерфейсы; утверждение, что sealed можно использовать только для классов и объектов и не для интерфейсов, неверно.
- Sealed типы не запрещают наследование от других классов или реализацию интерфейсов; ограничение относится к тому, кто может наследовать sealed тип.

(Не путать с преимуществами: исчерпывающие `when`, контроль иерархии, удобное сопоставление с образцом — это плюсы, а не ограничения.)

## Answer (EN)

Key limitations of sealed classes (and interfaces) in Kotlin:

- Restricted inheritance scope: only types explicitly declared as their subtypes in allowed locations may extend/implement a sealed class/interface (in the same file for early Kotlin versions; in modern Kotlin, within the same module and package or same file, depending on declaration syntax).
- You cannot arbitrarily extend a sealed type from another ("foreign") module/package/file, so the hierarchy is tightly controlled and closed to uncontrolled extension.
- A sealed class is inherently non-final in the sense that it is designed to define a closed but controlled hierarchy; it exists specifically for constrained polymorphism, not for free extension everywhere.
- Subtypes must follow visibility and placement rules for sealed types; this can make architecture more rigid and sometimes complicates refactoring or module splitting.

Important clarifications:
- Sealed classes are effectively abstract (you cannot instantiate a sealed class itself directly without a concrete subtype).
- Kotlin also has sealed interfaces; the claim that sealed can be used only for classes/objects and not interfaces is incorrect.
- Sealed types are not forbidden from inheriting from other classes or implementing interfaces; the restriction is on who may inherit from a sealed type, not what a sealed type may inherit from.

(Do not confuse these with advantages: exhaustive `when` expressions, controlled hierarchies, and pattern-matching-like usage are benefits, not limitations.)

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия этого подхода от Java?
- Когда вы бы использовали sealed классы на практике?
- Какие распространенные ошибки следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-sealed-classes]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-sealed-classes]]

## Связанные вопросы (RU)

- [[q-what-is-flow--programming-languages--medium]]

## Related Questions

- [[q-what-is-flow--programming-languages--medium]]
