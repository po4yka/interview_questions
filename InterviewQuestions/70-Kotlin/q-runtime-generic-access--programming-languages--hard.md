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
related: [c-kotlin, q-what-is-garbage-in-gc--programming-languages--easy]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/hard, generics, kotlin, programming-languages, reified, type-erasure]
---
# Вопрос (RU)
> Можно ли получить в runtime доступ к типу дженерика?

---

# Question (EN)
> Can you access generic type at runtime?

## Ответ (RU)

По умолчанию — нельзя, так как (на JVM) дженерики стираются (type erasure) во время компиляции: в runtime `List<String>` и `List<Int>` выглядят одинаково.

В Kotlin есть исключения и обходные пути:

- В `inline`-функциях можно объявлять `reified` type parameter: `inline fun <reified T> ...`. Для таких параметров компилятор подставляет конкретный тип, и в теле функции можно обращаться к `T::class`, `T::class.java` и вызывать `typeOf<T>()`.
- В объявлениях (например, `class Box<T>(val value: T)` или `val property: List<String>`) информация о типе может быть частично доступна через reflection, но на JVM это не гарантирует сохранение конкретных аргументов типа во всех случаях из-за стирания.
- Можно явно передавать `KClass<*>` или `Class<*>` / `KClass<T>` параметром (например, `fun <T: Any> parse(json: String, type: KClass<T>)`), но это обычно даёт доступ только к самому классу, а не к полным параметрам сложных дженериков.
- Для сложных дженериков (например, `List<T>`, `Map<K, V>`) `typeOf<T>()` в сочетании с `reified` и `inline` позволяет получить `KType` с информацией о параметрах типа на месте вызова.

Ключевая идея: без специальных механизмов (`reified` в `inline`-функциях, reflection над декларациями, явная передача type tokens) тип параметра дженерика `T` недоступен в runtime из-за type erasure. См. также [[c-kotlin]].

## Answer (EN)

By default, no: on the JVM generics use type erasure during compilation, so at runtime `List<String>` and `List<Int>` look the same.

In Kotlin there are exceptions and workarounds:

- In `inline` functions you can declare a `reified` type parameter: `inline fun <reified T> ...`. For such parameters the compiler substitutes the concrete type, so inside the function you can use `T::class`, `T::class.java`, and call `typeOf<T>()`.
- For declarations (e.g., `class Box<T>(val value: T)` or `val property: List<String>`) some generic type information can be obtained via reflection, but on the JVM concrete type arguments are not reliably preserved everywhere because of erasure.
- You can explicitly pass a `KClass<*>` or `KClass<T>` / `Class<*>` argument (e.g., `fun <T: Any> parse(json: String, type: KClass<T>)`), but this usually gives you only the raw class, not full generic arguments of complex types.
- For complex generics (e.g., `List<T>`, `Map<K, V>`) `typeOf<T>()` combined with `reified` and `inline` allows you to obtain a `KType` with type arguments information at the call site.

Key idea: without special mechanisms (reified inline functions, reflection on declarations, or explicitly passing type tokens), a generic type parameter `T` is not available at runtime because of type erasure.

---

## Дополнительные вопросы (RU)

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

## Связанные вопросы (RU)

- [[q-what-is-garbage-in-gc--programming-languages--easy]]

## Related Questions

- [[q-what-is-garbage-in-gc--programming-languages--easy]]
