---
id: lang-066
title: "Kotlin Sealed Classes Features / Особенности sealed классов в Kotlin"
aliases: [Kotlin Sealed Classes Features, Особенности sealed классов в Kotlin]
topic: kotlin
subtopics: [sealed-classes, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-sealed-classes, q-kotlin-lambda-expressions--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, programming-languages, sealed-classes]
---
# Вопрос (RU)
> В чем особенность sealed классов?

---

# Question (EN)
> What are the features of sealed classes?

---

## Ответ (RU)

Главная особенность sealed-классов (и sealed-интерфейсов) — ограничение иерархии наследования и, как следствие, полный контроль над набором допустимых подтипов.

Ключевые моменты:
- Набор прямых наследников sealed-типа должен быть фиксирован и известен компилятору. В современных версиях Kotlin прямые наследники могут быть объявлены:
  - в том же файле, что и sealed-класс/интерфейс (изначальное правило), или
  - в том же модуле и пакете (для расширенной формы, поддерживаемой платформами, на которых реализована данная возможность),
  что в итоге формирует "закрытую" иерархию для компилятора.
- Компилятор знает обо всех прямых наследниках sealed-типа, поэтому `when` по sealed-типу может быть проверен на полноту (exhaustive), и `else` можно не писать, если обработаны все варианты.
- Sealed-классы и sealed-интерфейсы удобно использовать для моделирования:
  - состояний (UI state, загрузка/успех/ошибка),
  - результатов операций (Success / Error / Loading и т.п.),
  - замкнутых доменных иерархий.
- Наследники могут быть `class`, `data class` или `object`, что позволяет удобно инкапсулировать данные для каждого варианта.
- Для лучшего понимания см. [[c-kotlin]] и [[c-sealed-classes]].

## Answer (EN)

The main feature of sealed classes (and sealed interfaces) is that they restrict the inheritance hierarchy, giving you full control over the set of allowed subtypes.

Key points:
- The set of direct subclasses of a sealed type must be fixed and known to the compiler. In modern Kotlin, direct subclasses can be declared:
  - in the same file as the sealed class/interface (the original rule), or
  - in the same module and package (for the extended form, on platforms where this is supported),
  which effectively creates a "closed" hierarchy from the compiler's perspective.
- Because the compiler knows all direct subclasses of a sealed type, `when` expressions on that type can be checked for exhaustiveness, and you can omit `else` when all variants are covered.
- Sealed classes and sealed interfaces are ideal for modeling:
  - states (e.g., UI state, loading/success/error),
  - operation results (e.g., Success / Error / Loading),
  - closed domain hierarchies.
- Subclasses can be `class`, `data class`, or `object`, allowing you to encapsulate specific data for each variant.
- For more details see [[c-kotlin]] and [[c-sealed-classes]].

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия sealed-классов от возможностей Java?
- В каких практических сценариях вы бы использовали sealed-классы?
- Какие распространенные ошибки и подводные камни при использовании sealed-классов?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin]("https://kotlinlang.org/docs/home.html")

## References

- [Kotlin Documentation]("https://kotlinlang.org/docs/home.html")

## Смежные вопросы (RU)

- [[q-retrofit-coroutines-best-practices--kotlin--medium]]
- [[q-testing-stateflow-sharedflow--kotlin--medium]]
- [[q-kotlin-lambda-expressions--kotlin--medium]]

## Related Questions

- [[q-retrofit-coroutines-best-practices--kotlin--medium]]
- [[q-testing-stateflow-sharedflow--kotlin--medium]]
- [[q-kotlin-lambda-expressions--kotlin--medium]]
