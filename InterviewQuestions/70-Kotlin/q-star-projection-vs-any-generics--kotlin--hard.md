---
id: 20251005-235005
title: "Star Projection (*) vs Any in Generics / Звездная проекция vs Any в обобщениях"
aliases: []

# Classification
topic: kotlin
subtopics: [generics, star-projection, variance, type-safety]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-generics--kotlin--hard]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, generics, star-projection, variance, type-safety, difficulty/hard]
---
# Question (EN)
> What is the difference between `*` (star projection) and `Any` in Kotlin generics?
# Вопрос (RU)
> В чем разница между `*` (звездная проекция) и `Any` в обобщениях Kotlin?

---

## Answer (EN)

### Quick Summary

`MutableList<*>` represents a list of **something unknown** - you can't add to it but can read `Any?`.

`MutableList<Any>` represents a list that can contain **any type mixed together** - you can add any object and read `Any`.

### Star Projection (`*`)

The type `MutableList<*>` represents a list of something (you don't know what exactly). Since you don't know the type:
- **Cannot add** anything (except null) - compiler can't verify type safety
- **Can read** but only as `Any?` - all objects inherit from `Any`

`List<*>` can contain objects of **any type, but only that one type** (e.g., only Strings or only Ints).

### Any in Generics

`List<Any>` can contain **different types mixed together** - Strings and Ints and anything else, all in the same list.

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
    // T is unknown, produces default supertype Any?
    val anyNullable = star.produce()  // Type is Any?

    // Cannot access T's properties - don't know the type
    // anyNullable.getColor()  // - Error

    // Cannot consume - don't know the type of Crate
    // star.consume(Fruit())  // - Error

    // Only use T-independent functions
    star.size()  // - OK
}
```

#### Any: Can Produce and Consume

```kotlin
fun useAsAny(any: Crate<Any>) {
    // T is known to be Any - can produce
    val anyNonNull = any.produce()  // - Type is Any

    // T is known to be Any - can consume
    any.consume(Fruit())  // - OK
    any.consume("String")  // - OK
    any.consume(42)  // - OK - all are subtypes of Any

    // Can use T-independent functions too
    any.size()  // - OK
}
```

### Key Differences Table

| Aspect | `List<*>` | `List<Any>` |
|--------|-----------|-------------|
| **Type** | Unknown type (projection) | Known type (Any) |
| **Read** | `Any?` | `Any` (non-null) |
| **Write** | Cannot add (except null) | Can add any object |
| **Contents** | Homogeneous (one type) | Heterogeneous (mixed types) |
| **Use case** | Type unknown/irrelevant | Truly mixed types |

### Practical Examples

#### Reading from Lists

```kotlin
val unknownList: List<*> = listOf("a", "b", "c")  // Actually List<String>
val first: Any? = unknownList.first()  // Must be Any?

val anyList: List<Any> = listOf("a", 2, 3.0)  // Mixed types
val firstAny: Any = anyList.first()  // Can be Any (non-null)
```

#### Writing to MutableLists

```kotlin
val unknownMutable: MutableList<*> = mutableListOf("a", "b")
// unknownMutable.add("c")  // - Cannot add - unknown type

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

// Any - less type safety
fun processAnyList(list: List<Any>) {
    // Can add any type - might not be what you want
    // Loses original type information - RISKY
}
```

### When to Use Each

**Use `List<*>` when**:
- You don't know or care about the exact type
- You only need to call type-independent methods (size, isEmpty, etc.)
- You want to prevent accidental modifications
- You're writing generic algorithms that work with any list

**Use `List<Any>` when**:
- You genuinely need a heterogeneous collection
- You want to store different types together
- You need to consume (add) items

### Variance Connection

```kotlin
// Star projection is like combining in and out
List<*> == List<out Any?>  // Can read Any?, can't write

// Any is invariant
List<Any>  // Can read Any, can write Any
```

**English Summary**: `List<*>` (star projection) represents an unknown but specific type - can read as `Any?` but can't write. `List<Any>` represents a truly mixed collection - can read and write any type. Star projection preserves type safety by preventing writes; Any allows heterogeneous collections but loses type information.

## Ответ (RU)

### Краткое изложение

`MutableList<*>` представляет список **чего-то неизвестного** - нельзя добавлять, но можно читать как `Any?`.

`MutableList<Any>` представляет список, который может содержать **любые типы вместе** - можно добавлять любой объект и читать как `Any`.

### Звездная проекция (`*`)

Тип `MutableList<*>` представляет список чего-то (точно не знаете чего). Поскольку тип неизвестен:
- **Нельзя добавлять** ничего (кроме null) - компилятор не может проверить типобезопасность
- **Можно читать** только как `Any?` - все объекты наследуются от `Any`

`List<*>` может содержать объекты **любого типа, но только этого одного типа**.

### Any в обобщениях

`List<Any>` может содержать **разные типы вместе** - String, Int и что угодно еще, все в одном списке.

### Детальный пример

```kotlin
class Crate<T> {
    private val items = mutableListOf<T>()
    fun produce(): T = items.last()
    fun consume(item: T) = items.add(item)
    fun size(): Int = items.size
}
```

#### Звездная проекция: не производитель, не потребитель

```kotlin
fun useAsStar(star: Crate<*>) {
    // T неизвестен, производит Any?
    val anyNullable = star.produce()  // Тип Any?

    // Нельзя потреблять
    // star.consume(Fruit())  // - Ошибка

    // Только T-независимые функции
    star.size()  // - OK
}
```

#### Any: может производить и потреблять

```kotlin
fun useAsAny(any: Crate<Any>) {
    // T известен как Any - может производить
    val anyNonNull = any.produce()  // - Тип Any

    // T известен как Any - может потреблять
    any.consume(Fruit())  // - OK
    any.consume("String")  // - OK
    any.consume(42)  // - OK

    any.size()  // - OK
}
```

### Когда что использовать

**Используйте `List<*>` когда**:
- Не знаете или не важен точный тип
- Нужны только методы независимые от типа (size, isEmpty и т.д.)
- Хотите предотвратить случайные модификации

**Используйте `List<Any>` когда**:
- Действительно нужна гетерогенная коллекция
- Хотите хранить разные типы вместе

**Краткое содержание**: `List<*>` (звездная проекция) представляет неизвестный но конкретный тип - можно читать как `Any?`, но нельзя писать. `List<Any>` представляет действительно смешанную коллекцию - можно читать и писать любой тип. Звездная проекция сохраняет типобезопасность предотвращая запись; Any позволяет гетерогенные коллекции но теряет информацию о типе.

---

## References
- [Difference between "*" and "Any" in Kotlin generics - StackOverflow](https://stackoverflow.com/questions/40138923/difference-between-and-any-in-kotlin-generics)
- [Generics: in, out, where - Kotlin Documentation](https://kotlinlang.org/docs/generics.html)

## Related Questions
- [[q-kotlin-generics--kotlin--hard]]
