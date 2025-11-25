---
id: lang-034
title: "Kotlin Inline Functions / Kotlin Inline Функции"
aliases: [Kotlin Inline Functions, Kotlin Inline Функции]
topic: kotlin
subtopics: [inline-functions, performance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-kotlin-dsl-creation--kotlin--hard]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, higher-order-functions, inline, inline-functions, lambda-expressions, performance]
date created: Friday, October 31st 2025, 6:29:59 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---

# Вопрос (RU)
> Что такое inline функции?

# Question (EN)
> What are inline functions?

## Ответ (RU)

Inline функции в Kotlin — это функции, помеченные ключевым словом `inline`, для которых компилятор пытается встроить (подставить) тело функции непосредственно в место вызова. Это особенно актуально для функций высшего порядка, принимающих лямбды или другие функции в качестве аргументов.

Ключевые моменты:
- Потенциальное уменьшение накладных расходов на вызов функций. За счёт подстановки тела функции в место вызова может быть уменьшено количество реальных вызовов функций и связанных с ними затрат. Это не является строгой гарантией оптимизации во всех случаях, а именно оптимизацией на уровне байткода.
- Оптимизация работы с лямбда-выражениями. По умолчанию лямбды в Kotlin представляются объектами, что создаёт накладные расходы по памяти и работе GC. При использовании inline функций лямбды-параметры могут быть инлайнинены вместе с функцией, что позволяет избежать создания дополнительных объектов. Параметры, помеченные `noinline`, не инлайнятся.
- Нелокальные `return` и модификаторы `crossinline`. Для лямбд, переданных в inline функции (и не помеченных `noinline`), возможны нелокальные `return` (возврат из внешней функции). Если такое поведение запрещено, используется `crossinline`.
- Reified типовые параметры. Только inline функции могут иметь реифицированные (`reified`) типовые параметры, потому что при инлайнинге конкретные аргументы типов подставляются в места вызова. Это позволяет обойти ограничения, связанные со стиранием типов, и, например, вызывать `foo<T>()` с проверкой `T::class`.
- Баланс между производительностью и размером кода. Чрезмерное использование inline может привести к раздуванию байткода (code bloat), что негативно скажется на размере приложения и, потенциально, производительности. Обычно inline оправдан для небольших функций и особенно для функций высшего порядка.

## Answer (EN)

In Kotlin, inline functions are functions marked with the `inline` keyword for which the compiler tries to inline (substitute) the function body directly at the call site. This is especially relevant for higher-order functions that take lambdas or other functions as parameters.

Key points:
- Potential reduction of call overhead. By substituting the body at the call site, the number of actual function calls and associated stack frame setup can be reduced. This is an optimization at the bytecode level, not an unconditional guarantee that "no call stack" is used in all cases.
- Better performance with lambdas. By default, lambdas in Kotlin are represented as objects, which adds allocation and GC overhead. With inline functions, lambda parameters can be inlined together with the function, avoiding creation of additional lambda objects. Parameters marked with `noinline` are not inlined.
- Non-local returns and `crossinline`. For lambda parameters of inline functions (that are not `noinline`), Kotlin allows non-local `return` (returning from the enclosing function). When such behavior must be disallowed, the parameter is marked with `crossinline`.
- Reified type parameters. Only inline functions can have reified type parameters because, after inlining, the concrete type arguments are available at the call sites. This allows working around type erasure limitations, e.g., using `foo<T>()` and accessing `T::class` or performing type checks with `is T`.
- Trade-off with code size. Excessive inlining can lead to bytecode bloat, which may negatively affect application size and potentially performance. Inline is best used for small functions and especially for higher-order functions.

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия inline функций в Kotlin от аналогичных механизмов в Java?
- Когда на практике стоит использовать inline функции?
- Каковы распространённые ошибки и подводные камни при использовании inline функций?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-kotlin-dsl-creation--kotlin--hard]]

## Related Questions

- [[q-kotlin-dsl-creation--kotlin--hard]]