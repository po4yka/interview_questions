---
id: lang-074
title: "Kotlin Final Modifier / Модификатор final в Kotlin"
aliases: [Kotlin Final Modifier, Модификатор final в Kotlin]
topic: programming-languages
subtopics: [inheritance, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-flowon-operator-context-switching--kotlin--hard, q-infix-functions--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [class-modifiers, classes, difficulty/easy, final, inheritance, open, programming-languages, syntax]
date created: Friday, October 31st 2025, 6:29:33 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---

# Какой Модификатор В Kotlin Делает Класс Нерасширяемым?

# Question (EN)
> Which modifier makes a class non-extendable in Kotlin?

# Вопрос (RU)
> Какой модификатор в Kotlin делает класс нерасширяемым?

---

## Answer (EN)

In Kotlin, the `final` modifier makes a class non-extendable. However, **all classes in Kotlin are `final` by default**. To make a class extendable, you must explicitly use the `open` keyword.

**Example:**
```kotlin
// Final class (default) - cannot be inherited
class FinalClass {
    // ...
}

// Open class - can be inherited
open class OpenClass {
    // ...
}

// This will compile:
class Derived : OpenClass()

// This will NOT compile:
// class Derived : FinalClass()  // Error: class is final
```

**Key points:**
- Unlike Java where classes are open by default, Kotlin classes are `final` by default
- Use `open` keyword to allow inheritance
- This design encourages composition over inheritance
- Sealed classes are another way to control inheritance hierarchy

---

## Ответ (RU)

В Kotlin модификатор `final` делает класс нерасширяемым. Однако **все классы в Kotlin являются `final` по умолчанию**. Чтобы сделать класс расширяемым, необходимо явно использовать ключевое слово `open`.

**Пример:**
```kotlin
// Final класс (по умолчанию) - не может быть унаследован
class FinalClass {
    // ...
}

// Open класс - может быть унаследован
open class OpenClass {
    // ...
}

// Это скомпилируется:
class Derived : OpenClass()

// Это НЕ скомпилируется:
// class Derived : FinalClass()  // Ошибка: класс final
```

**Ключевые моменты:**
- В отличие от Java, где классы открыты по умолчанию, в Kotlin классы `final` по умолчанию
- Используйте ключевое слово `open` для разрешения наследования
- Этот дизайн поощряет композицию над наследованием
- Sealed классы — это другой способ контроля иерархии наследования

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-infix-functions--kotlin--medium]]
-
- [[q-flowon-operator-context-switching--kotlin--hard]]
