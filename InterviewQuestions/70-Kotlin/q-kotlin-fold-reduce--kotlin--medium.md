---
id: 20251005-222659
title: "Kotlin fold and reduce / fold и reduce в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [collections, functional-programming, fold, reduce]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, collections, functional-programming, fold, reduce, difficulty/medium]
---
# Question (EN)
> What is the difference between fold and reduce in Kotlin?
# Вопрос (RU)
> Какая разница между fold и reduce в Kotlin?

---

## Answer (EN)

### Reduce

- `reduce` method transforms a given collection into a single result. It takes a lambda operator to combine a pair of elements into an accumulated value.
- It then traverses the collection from left to right and stepwise combines the accumulated value with the next element.

```kotlin
val numbers: List<Int> = listOf(1, 2, 3)
val sum = numbers.reduce { acc, next -> next + acc }
```

- `reduce` method will throw `RuntimeException` if its operated on an empty list.

- Signature of `reduce` method:

```kotlin
inline fun <S, T:S> Iterable<T>.reduce(operation: (acc:S, T) -> S): S
```

The function defines a generic type S and subtype T of S, Finally reduce returns one value of type S.

- In the following example the sum would exceed the range of `Int` because of that the data type of result is changed to Long. So it will throw compile error (Type argument is not within its bounds):

```kotlin
val sum: Long = numbers.reduce<Long, Int> { acc, next -> acc.toLong() + next.toLong() }
```

- To fix the compile error we will have to change the `Long` type to `Number` as `Number` is superset of `Int`. So **it doesn't solve the problem of changing the result type**

### Fold

To address the issues created by `reduce` we can use `fold`:

```kotlin
val numbers: List<Int> = listOf(1, 2, 3)
val sum = numbers.fold(0, { acc, next -> next + acc })
```

Here first argument is initial value. If list is empty, the initial value is returned.

Signature:
```kotlin
inline fun <T, R> Iterable<T>.fold(initial:R, (acc:R, T) -> R): R
```

In contrast to `reduce()`, it specifies two arbitrary generic types **T** and **R**.

- We can change the result type to **Long** in the following example:

```kotlin
val sum: Long = numbers.fold(0L, { acc, next -> acc + next.toLong() })
```

- `fold` **provides the ability to change the result type**.

## Ответ (RU)

### Reduce

- Метод `reduce` преобразует данную коллекцию в единый результат. Он принимает лямбда-оператор для объединения пары элементов в накопленное значение.
- Затем он проходит по коллекции слева направо и пошагово объединяет накопленное значение со следующим элементом.

```kotlin
val numbers: List<Int> = listOf(1, 2, 3)
val sum = numbers.reduce { acc, next -> next + acc }
```

- Метод `reduce` выбросит `RuntimeException`, если он работает с пустым списком.

- Сигнатура метода `reduce`:

```kotlin
inline fun <S, T:S> Iterable<T>.reduce(operation: (acc:S, T) -> S): S
```

Функция определяет обобщенный тип S и подтип T типа S, в конечном итоге reduce возвращает одно значение типа S.

- В следующем примере сумма превысит диапазон `Int`, из-за этого тип данных результата изменяется на Long. Поэтому будет выброшена ошибка компиляции (Type argument is not within its bounds):

```kotlin
val sum: Long = numbers.reduce<Long, Int> { acc, next -> acc.toLong() + next.toLong() }
```

- Чтобы исправить ошибку компиляции, нам придется изменить тип `Long` на `Number`, так как `Number` является надмножеством `Int`. Таким образом **это не решает проблему изменения типа результата**

### Fold

Чтобы решить проблемы, созданные `reduce`, мы можем использовать `fold`:

```kotlin
val numbers: List<Int> = listOf(1, 2, 3)
val sum = numbers.fold(0, { acc, next -> next + acc })
```

Здесь первый аргумент — начальное значение. Если список пуст, возвращается начальное значение.

Сигнатура:
```kotlin
inline fun <T, R> Iterable<T>.fold(initial:R, (acc:R, T) -> R): R
```

В отличие от `reduce()`, она указывает два произвольных обобщенных типа **T** и **R**.

- Мы можем изменить тип результата на **Long** в следующем примере:

```kotlin
val sum: Long = numbers.fold(0L, { acc, next -> acc + next.toLong() })
```

- `fold` **предоставляет возможность изменить тип результата**.

---

## References
- [Kotlin Collections Documentation](https://kotlinlang.org/docs/reference/collections-overview.html)

## Related Questions
- [[q-kotlin-collections--kotlin--easy]]
- [[q-kotlin-scope-functions--kotlin--medium]]
