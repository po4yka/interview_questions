---
id: lang-049
title: "Equals Hashcode Rules / Правила equals и hashCode"
aliases: [Equals Hashcode Rules, Правила equals и hashCode]
topic: kotlin
subtopics: [collections, equality, object-methods]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-equality, q-equals-hashcode-contracts--programming-languages--medium, q-equals-hashcode-purpose--programming-languages--hard]
created: 2025-10-15
updated: 2025-11-09
tags: [collections, contracts, difficulty/medium, equality, object-methods, kotlin]
---

# Вопрос (RU)
> Какие существуют правила для методов equals и hashcode?

# Question (EN)
> What rules exist for equals and hashCode methods?

## Ответ (RU)

Методы `equals()` и `hashCode()` определяют логику сравнения объектов и корректную работу хеш-коллекций, таких как `HashSet`, `HashMap` и `Hashtable` (см. также [[c-equality]]).

**Контракт equals():**
1. **Рефлексивность**: для любого не-null объекта `x`, `x.equals(x)` должно возвращать `true`.
2. **Симметричность**: если `x.equals(y)` возвращает `true`, то `y.equals(x)` также должно возвращать `true`.
3. **Транзитивность**: если `x.equals(y)` и `y.equals(z)` возвращают `true`, то `x.equals(z)` также должно возвращать `true`.
4. **Согласованность**: повторные вызовы `x.equals(y)` должны давать один и тот же результат, пока значения, участвующие в сравнении, не изменились.
5. **Сравнение с null**: для любого не-null объекта `x`, вызов `x.equals(null)` должен возвращать `false`.

**Контракт hashCode():**
1. **Согласованность во времени**: в течение одного выполнения программы вызов `x.hashCode()` должен возвращать одно и то же значение, пока состояние объекта, используемое в `equals()`/`hashCode()`, не меняется.
2. **Согласованность с equals**:
   - если `x.equals(y)` возвращает `true`, то `x.hashCode() == y.hashCode()` должно быть `true`;
   - если `x.equals(y)` возвращает `false`, то их `hashCode()` может быть как равным, так и разным (коллизии допустимы).
3. **Коллизии допустимы**: разные объекты (в том числе не равные по `equals`) могут иметь одинаковый `hashCode` — это не нарушает контракт, но для эффективности хеш-структур желательно минимизировать коллизии.

**Практическое правило**: когда вы переопределяете `equals()`, вы практически всегда должны переопределить и `hashCode()` таким образом, чтобы оба опирались на один и тот же набор значимых полей.

## Answer (EN)

Methods `equals()` and `hashCode()` define how objects are compared and are critical for correct behavior of hash-based collections such as `HashSet`, `HashMap`, and `Hashtable` (see also [[c-equality]]).

**equals() contract:**
1. **Reflexive**: for any non-null reference `x`, `x.equals(x)` must return `true`.
2. **Symmetric**: if `x.equals(y)` is `true`, then `y.equals(x)` must also be `true`.
3. **Transitive**: if `x.equals(y)` and `y.equals(z)` are `true`, then `x.equals(z)` must also be `true`.
4. **Consistent**: repeated calls to `x.equals(y)` must return the same result as long as the state used in the comparison does not change.
5. **Null comparison**: for any non-null reference `x`, `x.equals(null)` must return `false`.

**hashCode() contract:**
1. **Stable during execution**: during a single execution of the program, `x.hashCode()` must consistently return the same value as long as the object state used in `equals()`/`hashCode()` does not change.
2. **Consistency with equals**:
   - if `x.equals(y)` is `true`, then `x.hashCode() == y.hashCode()` must be `true`;
   - if `x.equals(y)` is `false`, their `hashCode()` values may be either equal or different (collisions are allowed).
3. **Collisions allowed**: different objects (including unequal ones) may have the same `hashCode`; this does not violate the contract, but good implementations minimize collisions for better performance.

**Practical rule**: when you override `equals()`, you should almost always override `hashCode()` as well, and both must be based on the same set of significant fields.

## Дополнительные вопросы (RU)

- В чем ключевые отличия этого контракта от Java?
- Когда это используется на практике?
- Какие распространенные ошибки следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

-
-
-

## Related Questions

-
-
-