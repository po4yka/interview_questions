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
updated: 2025-11-11

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
  - Является значением по умолчанию для большинства объявлений на уровне файла и членов классов (если не ограничено контекстом, например `private` классом или файлом).
  - Объявления видны везде, где виден сам контейнер (класс, файл, пакет, модуль).
- **private**:
  - Для членов класса/интерфейса: видно только внутри этого класса/интерфейса.
  - Для top-level объявлений (в файле): видно только внутри этого файла.
- **protected**:
  - Применимо только к членам классов/интерфейсов.
  - Видно внутри этого класса и его подклассов.
- **internal**:
  - Видно везде внутри одного и того же модуля.

Если вы не указываете модификатор видимости, вы получаете уровень видимости по умолчанию: для top-level объявлений и членов классов он **public** (если не ограничен областью видимости контейнера), а для локальных объявлений (внутри функций) модификаторы видимости вообще не применяются.

### Java Vs Kotlin

- В Java для классов и членов без явного модификатора, объявленных в пакете, используется уровень доступа по умолчанию (часто называемый **package-private**): он основан на пакете. В Kotlin по умолчанию для таких объявлений используется **public**, и доступ не привязан к пакету.
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
  - Is the default for most top-level declarations and class members (unless restricted by the containing scope).
  - Declarations are visible everywhere the containing declaration (class/file/module) is visible.
- **private**:
  - For class/interface members: visible only inside that class/interface.
  - For top-level declarations (in a file): visible only inside that file.
- **protected**:
  - Applicable only to class/interface members.
  - Visible inside that class and its subclasses.
- **internal**:
  - Visible everywhere within the same module.

If you don't specify a visibility modifier, you get the default visibility: for top-level declarations and class members, it is **public** (subject to the containing scope), and visibility modifiers are not applicable to local declarations inside functions.

### Java Vs Kotlin

- In Java, classes and members declared without an explicit modifier in a package use the default ("package-private") visibility, which is package-based. In Kotlin, such declarations are **public** by default, and visibility is not based on packages.
- Java's **package-private** has no direct equivalent in Kotlin; the closest conceptually (but module-based, not package-based) is **internal**.
- In Kotlin, an outer class does not see **private** members of another class, including its `inner`/`nested` classes; `private` visibility is always limited to the body of the declaring type or file.
- If you override a **protected** member and do not specify visibility explicitly, the overriding member in Kotlin cannot be less visible and remains **protected** by default (you may widen it, e.g., to `public`). In Java, similarly, an overriding method cannot reduce the visibility of the overridden method.

See also [[c-kotlin]].

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия модификаторов видимости Kotlin от Java?
- Когда на практике использовать каждый модификатор видимости?
- Каковы типичные ошибки и подводные камни при работе с модификаторами видимости?

## Follow-ups (EN)

- What are the key differences between Kotlin visibility modifiers and Java visibility modifiers?
- When would you use each visibility modifier in practice?
- What are common mistakes and pitfalls to avoid when working with visibility modifiers?

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

## Связанные Вопросы (RU)

### Продвинутые (сложнее)
- [[q-visibility-modifiers-kotlin--kotlin--medium]] — более детальное рассмотрение модификаторов видимости в контексте классов.

## Related Questions

### Advanced (Harder)
- [[q-visibility-modifiers-kotlin--kotlin--medium]] — more detailed consideration of visibility modifiers in the context of classes.
