---
id: kotlin-023
title: "Kotlin Visibility Modifiers / Модификаторы видимости в Kotlin"
aliases: ["Kotlin Visibility Modifiers, Модификаторы видимости в Kotlin"]

# Classification
topic: kotlin
subtopics: [access-control, encapsulation, modifiers]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-array-vs-list-kotlin--kotlin--easy, q-coroutine-memory-leaks--kotlin--hard, q-java-kotlin-abstract-classes-difference--programming-languages--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [access-control, difficulty/easy, encapsulation, kotlin, modifiers, visibility]
date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---
# Вопрос (RU)
> Что такое модификаторы видимости в Kotlin?

---

# Question (EN)
> What are visibility modifiers in Kotlin?
## Ответ (RU)

Kotlin позволяет контролировать видимость символов с помощью *модификаторов видимости*, которые могут быть размещены в объявлениях символов.

В Kotlin существует четыре модификатора видимости: **private**, **protected**, **internal** и **public**.

- **public**: объявления видны везде.
- **private**: означает видимый только внутри этого класса (включая все его члены)
- **protected**: означает видимый внутри этого класса (включая все его члены) + видимый в подклассах тоже
- **internal**: модификатор видим везде в том же модуле.

Если вы не указываете модификатор видимости, вы получаете уровень видимости по умолчанию, которым является **public**.

### Java Vs Kotlin

- В Java модификатор по умолчанию — **package private**, в Kotlin — **public**.
- **package private** в Java не имеет эквивалента в Kotlin, ближайшим является **internal**.
- Внешний класс не видит **private** члены своего внутреннего класса в Kotlin.
- Если вы переопределяете **protected** член и не указываете видимость явно, переопределяющий член также будет иметь видимость **protected**. В Java видимость согласно модификатору, и по умолчанию все еще **public**.

---

## Answer (EN)

Kotlin allows you to enforce symbol visibility via *visibility modifiers*, which can be placed on symbol declarations.

There are four visibility modifiers in Kotlin: **private**, **protected**, **internal** and **public**.

- **public**: declarations are visible everywhere.
- **private**: means visible inside this class only (including all its members)
- **protected**: means visible inside this class (including all its members) + visible in subclasses too
- **internal**: modifier are visible everywhere in the same module.

If you don't supply a visibility modifier, you get the default visibility level, which is **public**.

### Java Vs Kotlin

- In Java, the default modifier is **package private**, in Kotlin is **public**.
- Java's **package private** doesn't have an equivalent in Kotlin, the closest is **internal**.
- An Outer class does not see **private** members of its inner class in Kotlin.
- If you override a **protected** member and do not specify the visibility explicitly, the overriding member will also have **protected** visibility. In Java the visibility is according to the modifier and the default is still **public**.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Visibility modifiers](https://kotlinlang.org/docs/tutorials/kotlin-for-py/visibility-modifiers.html)
- [Visibility modifiers reference](https://kotlinlang.org/docs/reference/visibility-modifiers.html)
- [Kotlin for Android Developers: Visibility Modifiers](https://medium.com/mindorks/kotlin-for-android-developers-visibility-modifiers-8d8a3b84d298)
- [Kotlin Basics: Visibility Modifiers](https://medium.com/@HugoMatilla/kotlin-basics-visibility-modifiers-public-internal-protected-and-private-c3bf972aee11)

## Related Questions

### Advanced (Harder)
-  - Access Modifiers
- [[q-visibility-modifiers-kotlin--kotlin--medium]] - Classes
