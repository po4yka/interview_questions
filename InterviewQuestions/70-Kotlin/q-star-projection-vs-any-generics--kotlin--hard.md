---
id: kotlin-027
title: "Star Projection (*) vs Any in Generics / Звездная проекция vs Any в обобщениях"
aliases: ["Star Projection (*) vs Any in Generics", "Звездная проекция vs Any в обобщениях"]
topic: kotlin
subtopics: [generics, star-projection, type-safety]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2
status: draft
moc: moc-kotlin
related: [c-kotlin, q-kotlin-generics--kotlin--hard, q-kotlin-type-system--kotlin--medium]
created: 2025-10-05
updated: 2025-11-09
tags: [difficulty/hard, generics, kotlin, star-projection, type-safety, variance]

---
# Вопрос (RU)
> В чем разница между `*` (звездная проекция) и `Any` в обобщениях Kotlin?

---

# Question (EN)
> What is the difference between `*` (star projection) and `Any` in Kotlin generics?

---

## Ответ (RU)

### Краткое Изложение

`MutableList<*>` представляет список **чего-то неизвестного** — вы не знаете конкретный тип аргумента, нельзя безопасно добавлять элементы (кроме `null`), но можно читать значения как `Any?`.

`MutableList<Any>` представляет список, который явно параметризован типом `Any` и может содержать **произвольные типы вместе** — можно добавлять любой объект и читать как `Any`.

### Звездная Проекция (`*`)

Тип `MutableList<*>` представляет список с некоторым неизвестным, но фиксированным типом `T` (например, фактически это может быть `MutableList<String>` или `MutableList<Int>` и т.п.). Поскольку конкретный `T` неизвестен потребителю:
- **Нельзя добавлять** значения типа `T` (кроме `null`) — компилятор не может проверить типобезопасность.
- **Можно читать** элементы только как `Any?` — безопасный общий супертип, учитывающий возможность `null`.

Важно: `List<*>` не означает «свободно смешанный список любых типов», а «список некоторого одного неизвестного типа»; конкретный тип был зафиксирован при создании списка (например, `List<String>`), но при использовании через `*` вы его теряете.

### Any В Обобщениях

`List<Any>` означает, что тип-параметр явно равен `Any`. Такой список:
- Может содержать **разные типы вместе** — `String`, `Int` и т.д. в одной коллекции.
- Гарантированно не хранит `null` (если не используется `Any?`), поэтому чтение даёт `Any`.

### Детальный Пример С Crate

```kotlin
class Crate<T> {
    private val items = mutableListOf<T>()
    fun produce(): T = items.last()
    fun consume(item: T) = items.add(item)
    fun size(): Int = items.size
}
```

#### Звездная Проекция: Ни Производитель, Ни Потребитель

```kotlin
fun useAsStar(star: Crate<*>) {
    // T неизвестен, возвращаемый тип воспринимается как Any?
    val anyNullable = star.produce()  // Тип Any?

    // Нельзя вызывать consume с конкретным типом - тип T неизвестен
    // star.consume(Fruit())  // - Ошибка

    // Можно использовать только T-независимые функции
    star.size()  // - OK
}
```

#### Any: Может Производить И Потреблять

```kotlin
fun useAsAny(any: Crate<Any>) {
    // T известен как Any - можно читать
    val anyNonNull = any.produce()  // - Тип Any

    // T известен как Any - можно безопасно добавлять любые значения (подтипы Any)
    any.consume(Fruit())  // - OK
    any.consume("String")  // - OK
    any.consume(42)  // - OK

    any.size()  // - OK
}
```

### Таблица Ключевых Отличий

| Аспект        | `List<*>`                                             | `List<Any>`                                     |
|--------------|--------------------------------------------------------|-------------------------------------------------|
| Тип          | Неизвестный проецированный тип                         | Известный аргумент типа `Any`                   |
| Чтение       | Как `Any?`                                            | Как `Any` (не `null`)                           |
| Запись       | Нельзя добавлять (кроме `null`)                        | Можно добавлять любой `Any` (любой не-null тип) |
| Содержимое   | Концептуально однородное (один фиксированный тип `T`) | Гетерогенное (смешанные типы)                  |
| Use case     | Тип неизвестен/не важен, сохранение типобезопасности   | По-настоящему смешанные коллекции              |

### Практические Примеры

#### Чтение Из Списков

```kotlin
val unknownList: List<*> = listOf("a", "b", "c")  // Фактически List<String>
val first: Any? = unknownList.first()  // Должен быть Any?

val anyList: List<Any> = listOf("a", 2, 3.0)  // Смешанные типы
val firstAny: Any = anyList.first()  // Any (не null)
```

#### Запись В MutableList

```kotlin
val unknownMutable: MutableList<*> = mutableListOf("a", "b")
// unknownMutable.add("c")  // - Ошибка: добавить нельзя, аргумент типа неизвестен

val anyMutable: MutableList<Any> = mutableListOf("a", 2)
anyMutable.add(3.0)  // - OK - Any принимает всё
anyMutable.add("d")  // - OK
```

### Сравнение Типобезопасности

```kotlin
// Звездная проекция - типобезопасность сохраняется
fun processList(list: List<*>) {
    // Нельзя случайно добавить неверный тип - ХОРОШО
    // Можно безопасно читать как Any? - БЕЗОПАСНО
}

// Any - менее строгий относительно исходного типа элементов
fun processAnyList(list: MutableList<Any>) {
    // Можно добавлять любые типы - это может не совпадать с ожиданиями вызывающей стороны
    // Точная информация о типе элементов теряется - риск при неправильном использовании
}
```

### Связь С Вариантом (variance)

Звездная проекция определяется на основе вариативности параметра типа в объявлении класса. Для простой инвариантной декларации `class Box<T>` звездная проекция `Box<*>` с точки зрения потребителя ведёт себя примерно как `Box<out Any?>` (можно читать как `Any?`, но нельзя безопасно записывать значения типа `T`). Для `in`/`out`-вариантных параметров правила проекции соответствующим образом корректируются, чтобы сохранить типобезопасность.

### Когда Что Использовать

**Используйте `List<*>`, когда**:
- Вы не знаете или вам не важен точный аргумент типа.
- Нужны только методы, не зависящие от конкретного типа (`size`, `isEmpty` и т.п.).
- Хотите предотвратить небезопасные модификации коллекции.
- Пишите обобщённые алгоритмы, которые должны работать с любым `List<T>`.

**Используйте `List<Any>`, когда**:
- Действительно нужна гетерогенная коллекция.
- Нужно хранить разные типы вместе.
- Нужно иметь возможность добавлять произвольные значения.

**Русское резюме**: `List<*>` (звездная проекция) представляет неизвестный, но конкретный аргумент типа — элементы можно читать как `Any?`, но нельзя безопасно записывать значения типа `T`. `List<Any>` представляет список с явным типом `Any` — можно читать и добавлять любые не-null значения. Звездная проекция сохраняет типобезопасность, ограничивая запись; `Any` позволяет гетерогенные коллекции ценой потери точной информации о типах элементов.

---

## Answer (EN)

### Quick Summary

`MutableList<*>` represents a list of **something unknown** — the exact type argument is unknown, you cannot safely add elements of that type (except `null`), but you can read values as `Any?`.

`MutableList<Any>` represents a list explicitly parameterized with `Any` and can contain **any types mixed together** — you can add any object and read values as `Any`.

### Star Projection (`*`)

The type `MutableList<*>` represents a list with some unknown but fixed type `T` (for example, it might actually be a `MutableList<String>` or `MutableList<Int>`). Since the concrete `T` is unknown at the use site:
- You **cannot add** values of type `T` (except `null`) — the compiler cannot guarantee type safety.
- You **can read** elements, but only as `Any?`, which is the safe common supertype when the actual type argument (and its nullability) is unknown.

Important: `List<*>` does not mean "freely mixed arbitrary types". It means "a list of some single, specific type" that was fixed when the list was created; you just don't know which one when you see `*`.

### Any in Generics

`List<Any>` means the type parameter is explicitly `Any`. Such a list:
- May contain **different types mixed together** — `String`, `Int`, etc., in the same collection.
- Is known not to contain `null` (unless you use `Any?`), so reading elements gives you `Any`.

### Detailed Example with Crate

```kotlin
class Crate<T> {
    private val items = mutableListOf<T>()
    fun produce(): T = items.last()
    fun consume(item: T) = items.add(item)
    fun size(): Int = items.size
}
```

#### Star Projection: No Producer, No Consumer

```kotlin
fun useAsStar(star: Crate<*>) {
    // T is unknown, produced type is seen as Any?
    val anyNullable = star.produce()  // Type is Any?

    // Cannot call consume with a specific type - T is unknown
    // star.consume(Fruit())  // - Error

    // Only T-independent functions are allowed
    star.size()  // - OK
}
```

#### Any: Can Produce and Consume

```kotlin
fun useAsAny(any: Crate<Any>) {
    // T is known to be Any - can read
    val anyNonNull = any.produce()  // - Type is Any

    // T is known to be Any - can safely accept any subtype of Any
    any.consume(Fruit())  // - OK
    any.consume("String")  // - OK
    any.consume(42)  // - OK - all are subtypes of Any

    // Can use T-independent functions too
    any.size()  // - OK
}
```

### Key Differences Table

| Aspect        | `List<*>`                                      | `List<Any>`                              |
|--------------|------------------------------------------------|------------------------------------------|
| Type         | Unknown projected type                         | Known type argument `Any`               |
| Read         | As `Any?`                                      | As `Any` (non-null)                     |
| Write        | Cannot add (except `null`)                     | Can add any `Any` (any non-null type)   |
| Contents     | Conceptually homogeneous (one fixed type `T`)  | Heterogeneous (mixed types)             |
| Use case     | Type unknown/irrelevant, preserve safety       | Truly mixed-type collections            |

### Practical Examples

#### Reading from Lists

```kotlin
val unknownList: List<*> = listOf("a", "b", "c")  // Actually List<String>
val first: Any? = unknownList.first()  // Must be Any?

val anyList: List<Any> = listOf("a", 2, 3.0)  // Mixed types
val firstAny: Any = anyList.first()  // Any (non-null)
```

#### Writing to MutableLists

```kotlin
val unknownMutable: MutableList<*> = mutableListOf("a", "b")
// unknownMutable.add("c")  // - Error: cannot add, type argument is unknown

val anyMutable: MutableList<Any> = mutableListOf("a", 2)
anyMutable.add(3.0)  // - OK - Any accepts everything
anyMutable.add("d")  // - OK
```

#### Type Safety Comparison

```kotlin
// Star projection - type safety preserved
fun processList(list: List<*>) {
    // Can't accidentally add wrong types - GOOD
    // Can safely read as Any? - SAFE
}

// Any - less strict w.r.t. original element type
fun processAnyList(list: MutableList<Any>) {
    // Can add any type - may not match original expectations of callers
    // Original precise type information is lost - RISKY if misused
}
```

### When to Use Each

**Use `List<*>` when**:
- You don't know or care about the exact type argument.
- You only need to call type-independent methods (`size`, `isEmpty`, etc.).
- You want to prevent accidental modifications where the type is erased.
- You're writing generic algorithms that should work with any `List<T>`.

**Use `List<Any>` when**:
- You genuinely need a heterogeneous collection.
- You want to store different types together.
- You need to be able to consume (add) arbitrary values.

### Variance Connection

Star projection is defined based on the variance of the type parameter in the class declaration. For a simple invariant declaration like `class Box<T>`, the star projection `Box<*>` is treated similarly to `Box<out Any?>` from the consumer's point of view (you can read as `Any?`, but not write values of `T`). For `in`/`out`-variant parameters, the projection rules adjust accordingly to preserve type safety.

**English Summary**: `List<*>` (star projection) represents an unknown but specific type argument — you can read elements as `Any?` but cannot write elements of type `T`. `List<Any>` represents a list explicitly typed with `Any` — you can read and write any non-null type. Star projection preserves type safety by preventing unsafe writes; `Any` allows heterogeneous collections at the cost of losing precise type information.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Difference between "*" and "Any" in Kotlin generics - StackOverflow](https://stackoverflow.com/questions/40138923/difference-between-and-any-in-kotlin-generics)
- [Generics: in, out, where - Kotlin Documentation](https://kotlinlang.org/docs/generics.html)
- [[c-kotlin]]

## Related Questions

### Related (Hard)
- [[q-kotlin-generics--kotlin--hard]] - Generics
- [[q-kotlin-type-system--kotlin--medium]] - Kotlin type system
