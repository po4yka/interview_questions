---
id: lang-002
title: "Kotlin Collections Overview / Обзор коллекций Kotlin"
aliases: ["Kotlin Collections Overview", "Обзор коллекций Kotlin"]
topic: kotlin
subtopics: [functions]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-collections, c-concepts--kotlin--medium, q-abstract-class-vs-interface--kotlin--medium]
created: 2025-10-13
updated: 2025-11-11
tags: [difficulty/easy]

date created: Saturday, October 18th 2025, 9:35:30 am
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---
# Вопрос (RU)
> Какие коллекции знаешь?

# Question (EN)
> What collections do you know?

## Ответ (RU)

В Kotlin есть коллекции с **интерфейсами только для чтения (read-only)** и **изменяемые (mutable)** коллекции:

### Коллекции Только Для Чтения (Read-only интерфейсы)
- `List` — упорядоченная коллекция, допускающая дубликаты (интерфейс только для чтения)
- `Set` — коллекция уникальных элементов (интерфейс только для чтения; сама по себе не гарантирует порядок)
- `Map` — пары ключ-значение с уникальными ключами (интерфейс только для чтения)

(Важно: эти интерфейсы не гарантируют структурную неизменяемость данных; они лишь не предоставляют методов изменения.)

### Изменяемые Коллекции
- `MutableList` — можно добавлять/удалять элементы
- `MutableSet` — можно добавлять/удалять уникальные элементы
- `MutableMap` — можно добавлять/удалять пары ключ-значение

### Специализированные Реализации (JVM / Стандартные реализации)
- `ArrayList` — реализация `MutableList` на основе динамического массива (на JVM обычно `java.util.ArrayList`)
- `HashSet` — реализация `MutableSet` на основе хеш-таблицы (на JVM обычно `java.util.HashSet`)
- `HashMap` — реализация `MutableMap` на основе хеш-таблицы (на JVM обычно `java.util.HashMap`)

> `LinkedList` как отдельная коллекция доступна через Java interop (`java.util.LinkedList`) и в Kotlin для нее есть расширения, но она не является отдельным Kotlin-специфичным типом коллекции стандартной библиотеки.

Также стоит учитывать, что:
- Функции `listOf`, `setOf`, `mapOf` по умолчанию возвращают коллекции, которые через полученный read-only интерфейс нельзя модифицировать (попытки обойти это через небезопасные касты не гарантированы и могут привести к ошибкам).
- Например, на JVM `setOf` обычно возвращает `LinkedHashSet`, который сохраняет порядок вставки, хотя сам интерфейс `Set` порядок не обещает.

**Примеры создания:**
```kotlin
// Коллекции только для чтения (read-only интерфейсы)
val list: List<Int> = listOf(1, 2, 3)
val set: Set<String> = setOf("a", "b", "c")
val map: Map<String, String> = mapOf("key" to "value")

// Изменяемые коллекции
val mutableList: MutableList<Int> = mutableListOf(1, 2, 3)
val mutableSet: MutableSet<String> = mutableSetOf("a", "b")
val mutableMap: MutableMap<String, String> = mutableMapOf("key" to "value")
```

**Примечание**: "Только для чтения" в Kotlin означает, что через данный тип (интерфейс) нельзя вызывать методы изменения коллекции. Это не то же самое, что гарантированная неизменяемость данных или "read-only ссылка" — исходная коллекция может изменяться через другие ссылки или API.

См. также: [[c-kotlin]], [[c-collections]]

---

## Answer (EN)

In Kotlin there are collections with **read-only interfaces** and **mutable** collections:

### Read-only Collections (Read-only interfaces)
- `List` - ordered collection allowing duplicates (read-only interface)
- `Set` - collection of unique elements (read-only interface; does not itself guarantee order)
- `Map` - key-value pairs with unique keys (read-only interface)

(Important: these interfaces do not guarantee structural immutability; they only do not expose mutating operations.)

### Mutable Collections
- `MutableList` - can add/remove elements
- `MutableSet` - can add/remove unique elements
- `MutableMap` - can add/remove key-value pairs

### Specialized Implementations (JVM / Standard implementations)
- `ArrayList` - dynamic array implementation of `MutableList` (on JVM typically `java.util.ArrayList`)
- `HashSet` - hash table implementation of `MutableSet` (on JVM typically `java.util.HashSet`)
- `HashMap` - hash table implementation of `MutableMap` (on JVM typically `java.util.HashMap`)

> `LinkedList` is available via Java interop (`java.util.LinkedList`), and Kotlin provides extension functions for it, but it is not a separate Kotlin-specific collection type defined by the standard library.

Also note that:
- `listOf`, `setOf`, `mapOf` return collections that cannot be modified via the returned read-only interface (attempts to bypass this via unsafe casts are unsupported and may fail).
- On JVM, for example, `setOf` usually returns a `LinkedHashSet` that preserves insertion order, even though the `Set` interface itself does not promise ordering.

**Creation examples:**
```kotlin
// Read-only collections (read-only interfaces)
val list: List<Int> = listOf(1, 2, 3)
val set: Set<String> = setOf("a", "b", "c")
val map: Map<String, String> = mapOf("key" to "value")

// Mutable collections
val mutableList: MutableList<Int> = mutableListOf(1, 2, 3)
val mutableSet: MutableSet<String> = mutableSetOf("a", "b")
val mutableMap: MutableMap<String, String> = mutableMapOf("key" to "value")
```

**Note**: In Kotlin, "read-only" means that via the given type (interface) you cannot call mutating operations. It does not guarantee that the underlying data is truly immutable or that the reference is special; the same backing collection may still be modified through other references or APIs.

See also: [[c-kotlin]], [[c-collections]]

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия коллекций Kotlin от коллекций Java?
- Когда бы ты использовал коллекции Kotlin на практике?
- Какие распространенные подводные камни при работе с коллекциями Kotlin стоит учитывать?

## Follow-ups

- What are the key differences between Kotlin collections and Java collections?
- When would you use Kotlin collections in practice?
- What are common pitfalls to avoid when working with Kotlin collections?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-abstract-class-vs-interface--kotlin--medium]]

## Related Questions

- [[q-abstract-class-vs-interface--kotlin--medium]]