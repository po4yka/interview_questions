---
id: kotlin-003
title: Kotlin fold and reduce / fold и reduce в Kotlin
aliases:
- fold и reduce в Kotlin
- Kotlin fold and reduce
topic: kotlin
subtopics:
- collections
- fold
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository
status: draft
moc: moc-kotlin
related:
- c-collections
- c-kotlin
created: 2025-10-05
updated: 2025-11-09
tags:
- collections
- difficulty/medium
- fold
- functional-programming
- kotlin
- reduce
anki_cards:
- slug: kotlin-003-0-en
  language: en
  anki_id: 1768326281707
  synced_at: '2026-01-23T17:03:50.655805'
- slug: kotlin-003-0-ru
  language: ru
  anki_id: 1768326281730
  synced_at: '2026-01-23T17:03:50.657396'
---
# Вопрос (RU)
> Какая разница между fold и reduce в Kotlin?

---

# Question (EN)
> What is the difference between fold and reduce in Kotlin?

## Ответ (RU)

### Reduce

- Функция `reduce` преобразует коллекцию в единый результат. Она принимает лямбда-операцию для объединения текущего накопленного значения с очередным элементом.
- `reduce` проходит по коллекции слева направо; в качестве начального значения используется первый элемент коллекции.

```kotlin
val numbers: List<Int> = listOf(1, 2, 3)
val sum = numbers.reduce { acc, next -> acc + next } // 1 + 2 + 3 = 6
```

- Функция `reduce` выбросит `IllegalStateException`, если вызывается для пустой коллекции, так как ей нечего использовать в качестве начального значения.

- Сигнатура функции `reduce` для `Iterable`:

```kotlin
inline fun <S, T : S> Iterable<T>.reduce(operation: (acc: S, T) -> S): S
```

В стандартной библиотеке Kotlin для обычных коллекций используется конкретная форма с одним типовым параметром:

```kotlin
inline fun <S> Iterable<S>.reduce(operation: (acc: S, S) -> S): S
```

Концептуально `reduce` возвращает значение того же типа, что и элементы (или их супертипа), и не позволяет свободно выбирать отличный тип результата.

- Ключевые ограничения `reduce`:
  - нельзя задать явное начальное значение;
  - небезопасно для пустых коллекций (если только вы не используете `reduceOrNull()`);
  - не подходит, когда нужен аккумулятор другого типа (например, `Long` для суммы `Int`).

Для пустых коллекций используйте `reduceOrNull()`, если нужно получить `null` вместо исключения.

### Fold

Чтобы решить эти ограничения `reduce`, можно использовать `fold`:

```kotlin
val numbers: List<Int> = listOf(1, 2, 3)
val sum = numbers.fold(0) { acc, next -> acc + next } // 0 + 1 + 2 + 3 = 6
```

Здесь первый аргумент — начальное значение. Если список пуст, возвращается именно это начальное значение.

Сигнатура:

```kotlin
inline fun <T, R> Iterable<T>.fold(initial: R, operation: (acc: R, T) -> R): R
```

В отличие от `reduce()`, `fold()`:
- позволяет задать начальное значение;
- использует два обобщённых типа `T` (тип элементов) и `R` (тип аккумулятора/результата), поэтому тип результата может отличаться от типа элементов.

Например, можно безопасно накапливать сумму `Int` в `Long`:

```kotlin
val numbers: List<Int> = listOf(1, 2, 3)
val sum: Long = numbers.fold(0L) { acc, next -> acc + next } // R = Long, T = Int
```

Таким образом, `fold`:
- предоставляет явный контроль над начальным значением;
- позволяет менять тип результата независимо от типа элементов коллекции.

## Дополнительные Вопросы (RU)

- Каковы ключевые отличия от подхода в Java?
- Когда вы бы использовали это на практике?
- Каковы распространенные ошибки, которых следует избегать?

## Ссылки (RU)

- [[c-kotlin]]
- "https://kotlinlang.org/docs/collections-overview.html"

## Связанные Вопросы (RU)

- [[q-kotlin-collections--kotlin--easy]]
- [[q-kotlin-scope-functions--kotlin--medium]]

---

## Answer (EN)

### Reduce

- The `reduce` function transforms a collection into a single result. It takes a lambda operation that combines the current accumulated value with the next element.
- `reduce` iterates from left to right; it uses the first element of the collection as the initial accumulator value.

```kotlin
val numbers: List<Int> = listOf(1, 2, 3)
val sum = numbers.reduce { acc, next -> acc + next } // 1 + 2 + 3 = 6
```

- The `reduce` function throws an `IllegalStateException` when called on an empty collection because there is no element to use as the initial value.

- Signature for `reduce` on `Iterable`:

```kotlin
inline fun <S, T : S> Iterable<T>.reduce(operation: (acc: S, T) -> S): S
```

In the Kotlin standard library for regular collections the concrete form is:

```kotlin
inline fun <S> Iterable<S>.reduce(operation: (acc: S, S) -> S): S
```

Conceptually, `reduce` returns a value of (essentially) the same type as the elements and does not let you freely choose a different result type.

- Key limitations of `reduce`:
  - you cannot specify an explicit initial value;
  - it is unsafe on empty collections unless you use `reduceOrNull()`;
  - it is not suitable when you need an accumulator of a different type (e.g. `Long` for summing `Int`).

For empty collections, prefer `reduceOrNull()` if you want `null` instead of an exception.

### Fold

To address these limitations of `reduce`, you can use `fold`:

```kotlin
val numbers: List<Int> = listOf(1, 2, 3)
val sum = numbers.fold(0) { acc, next -> acc + next } // 0 + 1 + 2 + 3 = 6
```

Here, the first argument is the initial value. If the list is empty, this initial value is returned.

Signature:
```kotlin
inline fun <T, R> Iterable<T>.fold(initial: R, operation: (acc: R, T) -> R): R
```

In contrast to `reduce()`, `fold()`:
- lets you specify an explicit initial value;
- has separate generic types `T` (element type) and `R` (accumulator/result type), so the result type can differ from the element type.

- For example, you can safely accumulate an `Int` list into a `Long`:

```kotlin
val numbers: List<Int> = listOf(1, 2, 3)
val sum: Long = numbers.fold(0L) { acc, next -> acc + next } // R = Long, T = Int
```

- Thus, `fold`:
  - provides explicit control over the initial value;
  - allows changing the result type independently of the element type.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- "https://kotlinlang.org/docs/collections-overview.html"

## Related Questions
- [[q-kotlin-collections--kotlin--easy]]
- [[q-kotlin-scope-functions--kotlin--medium]]
