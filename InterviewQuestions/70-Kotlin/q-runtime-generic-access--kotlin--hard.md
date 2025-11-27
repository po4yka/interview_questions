---
id: lang-024
title: "Runtime Generic Access / Доступ к дженерикам во время выполнения"
aliases: [Runtime Generic Access, Доступ к дженерикам во время выполнения]
topic: kotlin
subtopics: [generics, reification, type-system]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-concepts--kotlin--medium, q-what-is-garbage-in-gc--programming-languages--easy]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/hard, generics, kotlin, programming-languages, reified, type-erasure]

date created: Friday, October 31st 2025, 6:30:07 pm
date modified: Tuesday, November 25th 2025, 8:53:49 pm
---
# Вопрос (RU)
> Можно ли получить в runtime доступ к типу дженерика?

---

# Question (EN)
> Can you access generic type at runtime?

## Ответ (RU)

По умолчанию — нельзя (на JVM), так как дженерики стираются (type erasure) во время компиляции: в runtime `List<String>` и `List<Int>` выглядят одинаково как `List`.

В Kotlin (на JVM) есть исключения и обходные пути:

- В `inline`-функциях можно объявлять `reified` type parameter: `inline fun <reified T> ...`. Для таких параметров компилятор подставляет конкретный тип, и в теле функции можно обращаться к `T::class`, `T::class.java` и вызывать `typeOf<T>()`.
- В объявлениях (например, `class Box<T>(val value: T)` или `val property: List<String>`) сигнатуры с дженериками (generic signatures) сохраняются в метаданных байткода, и через reflection можно получить информацию о аргументах типа у свойств, полей, суперклассов и интерфейсов. Но фактический runtime-тип объекта по-прежнему стерт: экземпляр `List<String>` в рантайме имеет raw-тип `List`, а не отдельный `List<String>`.
- Можно явно передавать `KClass<*>` или `Class<*>` / `KClass<T>` параметром (например, `fun <T: Any> parse(json: String, type: KClass<T>)`), но это обычно даёт доступ только к классу, а не к полным параметрам сложных дженериков без дополнительных оберток (type tokens).
- Для сложных дженериков (например, `List<T>`, `Map<K, V>`) `typeOf<T>()` в сочетании с `reified` и `inline` позволяет получить `KType` с информацией о параметрах типа на месте вызова.

Ключевая идея (для JVM): без специальных механизмов (`reified` в `inline`-функциях, reflection над декларациями, явная передача type tokens) тип параметра дженерика `T` недоступен в runtime из-за type erasure. См. также [[c-concepts--kotlin--medium]].

## Answer (EN)

By default (on the JVM), no: generics use type erasure during compilation, so at runtime `List<String>` and `List<Int>` both appear as raw `List`.

In Kotlin (on the JVM) there are exceptions and workarounds:

- In `inline` functions you can declare a `reified` type parameter: `inline fun <reified T> ...`. For such parameters the compiler substitutes the concrete type, so inside the function you can use `T::class`, `T::class.java`, and call `typeOf<T>()`.
- For declarations (e.g., `class Box<T>(val value: T)` or `val property: List<String>`) generic signatures are stored in the bytecode metadata, and via reflection you can inspect type arguments of properties, fields, supertypes, and interfaces. However, the actual runtime type of an instance is still erased: an instance of `List<String>` has the raw runtime type `List`, not a distinct `List<String>`.
- You can explicitly pass a `KClass<*>` or `KClass<T>` / `Class<*>` argument (e.g., `fun <T: Any> parse(json: String, type: KClass<T>)`), but this usually gives you only the class, not full generic arguments of complex types, unless you introduce additional wrappers (type tokens).
- For complex generics (e.g., `List<T>`, `Map<K, V>`) `typeOf<T>()` combined with `reified` and `inline` allows you to obtain a `KType` including type argument information at the call site.

Key idea (for JVM): without special mechanisms (reified inline functions, reflection on declarations, or explicitly passing type tokens), a generic type parameter `T` is not available at runtime because of type erasure.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия от Java?
- Когда это используется на практике?
- Каковы типичные подводные камни?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[c-variable--programming-languages--easy]]

## Related Questions

- [[c-variable--programming-languages--easy]]
