---
id: lang-045
title: Kotlin Property Delegates / Делегаты свойств Kotlin
aliases:
- Kotlin Property Delegates
- Делегаты свойств Kotlin
topic: kotlin
subtopics:
- delegation
- type-system
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-coroutine-scope-basics--kotlin--easy
- q-kotlin-channels--kotlin--medium
- q-kotlin-map-flatmap--kotlin--medium
created: 2025-10-15
updated: 2025-11-09
tags:
- delegates
- difficulty/medium
- kotlin
- property-delegates
---
# Вопрос (RU)
> В чем особенность делегатов свойств?

# Question (EN)
> What are the features of property delegates?

## Ответ (RU)

Делегаты свойств в Kotlin — это механизм, позволяющий перенести логику хранения и доступа к значению свойства (get/set) в отдельный объект, используя ключевое слово `by`.

Ключевые особенности:
- Разделение ответственности: свойство описывает интерфейс доступа, делегат инкапсулирует реализацию.
- Повторное использование: один делегат может использоваться многими свойствами и в разных классах.
- Гибкость и расширяемость: можно определять собственные делегаты, реализуя операторы `getValue`/`setValue` (в виде функций-расширений или методов), с сигнатурами, определёнными языком.
- Поддержка `val`/`var`: для `val` требуется только `getValue`, для `var` также `setValue`.
- Применимость к разным видам свойств: можно использовать для свойств класса, top-level свойств, локальных и расширений.
- Стандартные делегаты из стандартной библиотеки: `lazy`, `observable`, `vetoable`, `notNull`, а также делегаты для хранения в `Map`.
- Интеграция с языком: синтаксис делегирования (`by`) и контракт делегата проверяются компилятором, что делает использование безопасным и предсказуемым.

Краткий пример:
```kotlin
class Example {
    val lazyValue: String by lazy { "computed" }
}
```

## Answer (EN)

In Kotlin, property delegates are a language feature that lets you move the logic of storing and accessing a property’s value (get/set) into a separate object using the `by` keyword.

Key features:
- Separation of concerns: the property defines the access interface, while the delegate encapsulates the implementation.
- Reusability: one delegate can be reused by multiple properties and across classes.
- Flexibility and extensibility: you can define custom delegates by implementing `getValue`/`setValue` (as member or extension functions) with language-defined signatures.
- Support for `val`/`var`: `val` requires only `getValue`, `var` also requires `setValue`.
- Works for multiple property kinds: usable with member, top-level, local, and extension properties.
- Standard library delegates: `lazy`, `observable`, `vetoable`, `notNull`, and map-backed delegates.
- Language-level integration: the `by` syntax and delegate contract are enforced by the compiler, making usage safe and predictable.

Simple example:
```kotlin
class Example {
    val lazyValue: String by lazy { "computed" }
}
```

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого механизма от Java?
- Когда целесообразно использовать делегаты свойств на практике?
- Каковы типичные подводные камни при использовании делегатов?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin по делегированным свойствам](https://kotlinlang.org/docs/delegated-properties.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/delegated-properties.html)
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-kotlin-map-flatmap--kotlin--medium]]
- [[q-coroutine-scope-basics--kotlin--easy]]
- [[q-kotlin-channels--kotlin--medium]]

## Related Questions

- [[q-kotlin-map-flatmap--kotlin--medium]]
- [[q-coroutine-scope-basics--kotlin--easy]]
- [[q-kotlin-channels--kotlin--medium]]