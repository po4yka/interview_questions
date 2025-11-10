---
id: kotlin-023
title: "Kotlin Visibility Modifiers / Модификаторы видимости в Kotlin"
aliases: ["Kotlin Visibility Modifiers", "Модификаторы видимости в Kotlin"]

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
related: [c-kotlin, q-array-vs-list-kotlin--kotlin--easy, q-coroutine-memory-leaks--kotlin--hard]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [access-control, difficulty/easy, encapsulation, kotlin, modifiers, visibility]
---
# Вопрос (RU)
> Что такое модификаторы видимости в Kotlin?

---

# Question (EN)
> What are visibility modifiers in Kotlin?

---

## Ответ (RU)

Kotlin позволяет контролировать видимость объявлений с помощью *модификаторов видимости*, которые указываются в объявлениях классов, функций, свойств и других символов.

В Kotlin существует четыре модификатора видимости: **private**, **protected**, **internal** и **public**.

Общее поведение:

- **public**:
  - По умолчанию для большинства деклараций.
  - Объявления видны везде, где виден сам контейнер (класс, файл, пакет, модуль).
- **private**:
  - Для членoв класса/интерфейса: видно только внутри этого класса/интерфейса.
  - Для top-level объявлений (в файле): видно только внутри этого файла.
- **protected**:
  - Применимо только к членам классов/интерфейсов.
  - Видно внутри этого класса и его подклассов.
- **internal**:
  - Видно везде внутри одного и того же модуля.

Если вы не указываете модификатор видимости, вы получаете уровень видимости по умолчанию: для top-level объявлений и членов классов он **public** (если не ограничен контекстом), а для локальных объявлений (внутри функций) модификаторы видимости вообще не применяются.

### Java vs Kotlin

- В Java модификатор по умолчанию для top-level классов/членов без модификатора — **package-private**; в Kotlin — **public**.
- **package-private** в Java не имеет прямого эквивалента в Kotlin; ближайшая по смыслу (но основанная на модуле, а не пакете) — **internal**.
- В Kotlin внешний класс не видит **private** члены другого класса, включая его `inner`/`nested` классы; `private` всегда ограничивает видимость телом того типа или файла, в котором объявлен член.
- Если вы переопределяете **protected** член и не указываете видимость явно, переопределяющий член в Kotlin не может быть менее видимым и по умолчанию остаётся **protected** (вы можете сделать его более открытым, например `public`). В Java аналогично: переопределяющий метод не может иметь более строгую видимость, чем у базового.

Также см. [[c-kotlin]].

---

## Answer (EN)

Kotlin allows you to control declaration visibility via *visibility modifiers*, specified on classes, functions, properties, and other symbols.

There are four visibility modifiers in Kotlin: **private**, **protected**, **internal**, and **public**.

General behavior:

- **public**:
  - Default for most declarations.
  - Declarations are visible everywhere the containing declaration (class/file/module) is visible.
- **private**:
  - For class/interface members: visible only inside that class/interface.
  - For top-level declarations (in a file): visible only inside that file.
- **protected**:
  - Applicable only to class/interface members.
  - Visible inside that class and its subclasses.
- **internal**:
  - Visible everywhere within the same module.

If you don't specify a visibility modifier, you get the default visibility: for top-level declarations and class members it is **public** (subject to the containing scope), and visibility modifiers are not applicable to local declarations inside functions.

### Java vs Kotlin

- In Java, the default (no modifier) for top-level classes/members is **package-private**; in Kotlin it's **public**.
- Java's **package-private** has no direct equivalent in Kotlin; the closest conceptually (but module-based, not package-based) is **internal**.
- In Kotlin, an outer class does not see **private** members of another class, including its `inner`/`nested` classes; `private` visibility is always limited to the body of the declaring type or file.
- If you override a **protected** member and do not specify visibility explicitly, the overriding member in Kotlin cannot be less visible and remains **protected** by default (you may widen it, e.g., to `public`). In Java, similarly, an overriding method cannot reduce the visibility of the overridden method.

See also [[c-kotlin]].

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия модификаторов видимости Kotlin от Java?
- Когда на практике использовать каждый модификатор видимости?
- Каковы типичные ошибки и подводные камни при работе с модификаторами видимости?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

---

## Ссылки (RU)

- [Visibility modifiers](https://kotlinlang.org/docs/visibility-modifiers.html)
- [Kotlin for Android Developers: Visibility Modifiers](https://medium.com/mindorks/kotlin-for-android-developers-visibility-modifiers-8d8a3b84d298)
- [Kotlin Basics: Visibility Modifiers](https://medium.com/@HugoMatilla/kotlin-basics-visibility-modifiers-public-internal-protected-and-private-c3bf972aee11)

## References

- [Visibility modifiers](https://kotlinlang.org/docs/visibility-modifiers.html)
- [Kotlin for Android Developers: Visibility Modifiers](https://medium.com/mindorks/kotlin-for-android-developers-visibility-modifiers-8d8a3b84d298)
- [Kotlin Basics: Visibility Modifiers](https://medium.com/@HugoMatilla/kotlin-basics-visibility-modifiers-public-internal-protected-and-private-c3bf972aee11)

---

## Связанные вопросы (RU)

### Продвинутые (сложнее)
- [[q-visibility-modifiers-kotlin--kotlin--medium]] — более детальное рассмотрение модификаторов видимости в контексте классов.

## Related Questions

### Advanced (Harder)
- [[q-visibility-modifiers-kotlin--kotlin--medium]] - Classes
