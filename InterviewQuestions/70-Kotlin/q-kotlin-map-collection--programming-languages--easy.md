---
id: lang-008
title: "Kotlin Map Collection / Map коллекция в Kotlin"
aliases: [Kotlin Map Collection, Map коллекция в Kotlin]
topic: kotlin
subtopics: [collections, types]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-11-09
tags: [collections, difficulty/easy, map, kotlin]
moc: moc-kotlin
related: [c-kotlin, c-collections, q-kotlin-property-delegates--programming-languages--medium]
---
# Вопрос (RU)
> Расскажи про коллекцию `Map`

# Question (EN)
> Tell me about the `Map` collection

## Ответ (RU)

`Map` в Kotlin — это коллекция пар ключ-значение.

Ключевые свойства:
- Каждый ключ уникален.
- Значение может повторяться.
- Доступ к элементу происходит по ключу, а не по индексу.
- Базовые интерфейсы: `Map<K, V>` (неизменяемая view) и `MutableMap<K, V>` (изменяемая).

Чаще всего операции поиска по ключу в стандартных реализациях (`HashMap`, `mutableMapOf`) — амортизированно `O(1)`.

См. также: [[c-kotlin]], [[c-collections]]

### Базовое Использование
```kotlin
val ages: Map<String, Int> = mapOf(
    "Alice" to 25,
    "Bob" to 30
)

val aliceAge = ages["Alice"]      // Int? (nullable)
val bobAge = ages.getValue("Bob")  // Int, бросает исключение если ключа нет
```

### Мутируемый Map
```kotlin
val ages: MutableMap<String, Int> = mutableMapOf()
ages["Alice"] = 25
ages["Bob"] = 30
ages.remove("Bob")
```

### Инициализация и перебор
```kotlin
val map = mapOf(
    "one" to 1,
    "two" to 2
)

for ((key, value) in map) {
    println("$key -> $value")
}
```

### Важные Моменты
- `Map` в Kotlin по умолчанию представляет собой read-only интерфейс: вы не можете модифицировать через `Map`, но конкретная реализация может быть изменяемой.
- `MutableMap` расширяет `Map` и добавляет операции записи (`put`, оператор `[]` для присваивания, `remove`).
- Порядок элементов зависит от реализации: `HashMap` не гарантирует порядок, `LinkedHashMap` сохраняет порядок вставки.

### Функции Расширения Для Map

`map`, `mapKeys`, `mapValues` и другие позволяют трансформировать содержимое `Map` как коллекции:

```kotlin
val users = mapOf(
    1 to "Alice",
    2 to "Bob"
)

val nameLengths = users.mapValues { (_, name) -> name.length }
// {1=5, 2=3}

val idToGreeting = users.map { (id, name) -> "$id: Hello, $name" }
// List<String>: ["1: Hello, Alice", "2: Hello, Bob"]
```

## Answer (EN)

In Kotlin, `Map` is a key-value collection.

Key properties:
- Each key is unique.
- Values may repeat.
- You access elements by key, not by index.
- Core interfaces: `Map<K, V>` (read-only view) and `MutableMap<K, V>` (mutable).

For standard implementations (like `HashMap`, `mutableMapOf`) key lookup is typically amortized `O(1)`.

See also: [[c-kotlin]], [[c-collections]]

### Basic Usage
```kotlin
val ages: Map<String, Int> = mapOf(
    "Alice" to 25,
    "Bob" to 30
)

val aliceAge = ages["Alice"]      // Int? (nullable)
val bobAge = ages.getValue("Bob")  // Int, throws if key is missing
```

### Mutable Map
```kotlin
val ages: MutableMap<String, Int> = mutableMapOf()
ages["Alice"] = 25
ages["Bob"] = 30
ages.remove("Bob")
```

### Initialization and Iteration
```kotlin
val map = mapOf(
    "one" to 1,
    "two" to 2
)

for ((key, value) in map) {
    println("$key -> $value")
}
```

### Important Points
- `Map` in Kotlin is a read-only interface: you cannot modify via `Map`, though the underlying implementation may or may not be mutable.
- `MutableMap` extends `Map` and adds write operations (`put`, `[]` assignment, `remove`).
- Element order depends on implementation: `HashMap` does not guarantee order, `LinkedHashMap` preserves insertion order.

### Map Extension Functions

Functions like `map`, `mapKeys`, `mapValues` help transform map contents as collections:

```kotlin
val users = mapOf(
    1 to "Alice",
    2 to "Bob"
)

val nameLengths = users.mapValues { (_, name) -> name.length }
// {1=5, 2=3}

val idToGreeting = users.map { (id, name) -> "$id: Hello, $name" }
// List<String>: ["1: Hello, Alice", "2: Hello, Bob"]
```

## Дополнительные вопросы (RU)

- Чем отличаются `Map` в Kotlin и `Map` в Java (nullability, read-only интерфейсы, функции-расширения и т.д.)?
- Когда стоит выбирать `Map` вместо `List` или других коллекций?
- Каковы распространённые ошибки при использовании `Map` (например, отсутствие ключей, неверные ожидания по поводу порядка)?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-kotlin-immutable-collections--programming-languages--easy]]
- [[q-kotlin-collections--kotlin--medium]]
- [[q-kotlin-map-flatmap--kotlin--medium]]

## Follow-ups

- How do Kotlin `Map` and Java `Map` differ (nullability, read-only interfaces, extension functions, etc.)?
- When would you choose `Map` vs `List` or other collections?
- What are common pitfalls when using `Map` (e.g., missing keys, assumptions about order)?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-immutable-collections--programming-languages--easy]]
- [[q-kotlin-collections--kotlin--medium]]
- [[q-kotlin-map-flatmap--kotlin--medium]]
