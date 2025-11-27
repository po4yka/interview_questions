---
id: kotlin-137
title: Array vs List in Kotlin / Разница между Array и List в Kotlin
topic: kotlin
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-11-09
aliases: [Array vs List in Kotlin, Разница между Array и List в Kotlin]
tags: [collections, data-structures, difficulty/easy, kotlin]
moc: moc-kotlin
question_kind: theory
related:
  - c-collections
  - c-kotlin
  - q-kotlin-collections--kotlin--easy
  - q-kotlin-map-collection--programming-languages--easy
  - q-list-set-map-differences--kotlin--easy
  - q-list-vs-sequence--kotlin--medium
subtopics:
  - array
  - collections
  - list
date created: Saturday, November 1st 2025, 12:09:57 pm
date modified: Tuesday, November 25th 2025, 8:53:53 pm
---
# Вопрос (RU)
> В чём разница между `Array` и `List` в Kotlin?

# Question (EN)
> What is the Difference between `Array` and `List` in Kotlin?

## Ответ (RU)
Массивы и списки в Kotlin — это структуры данных для хранения наборов элементов.

В Kotlin важно различать:
- `Array` и типы коллекций (`List`, `MutableList` и др.)
- интерфейсы только для чтения (`List`) и изменяемые (`MutableList`).

### Основные Различия

#### 1. Размер И Изменяемость

**Array**: Имеет фиксированный размер после создания; можно изменять элементы, но не длину.

```kotlin
val array = arrayOf(1, 2, 3, 4, 5)
// array.size == 5, изменить длину нельзя
array[0] = 10 // OK: массивы по умолчанию изменяемые
```

**List**: Интерфейс `List` сам по себе только для чтения (нет add/remove). Для динамического изменения размера используется `MutableList` (например, через `mutableListOf`). На JVM `MutableList` обычно основан на `ArrayList`, который автоматически расширяется.

```kotlin
val list: List<Int> = listOf(1, 2, 3)
// list.add(4) // ОШИБКА: List только для чтения

val mutableList = mutableListOf(1, 2, 3)
mutableList.add(4)        // Размер стал 4
mutableList.removeAt(0)   // Размер стал 3
```

#### 2. Типизация И Представление

**Array**: `Array<T>` хранит ссылки на элементы типа `T`. Для примитивов есть специализированные массивы (`IntArray`, `LongArray` и т.п.), чтобы избежать упаковки (boxing) и лишних накладных расходов (на JVM отображаются в `int[]` и т.п.).

```kotlin
val intArray: IntArray = intArrayOf(1, 2, 3)        // Специализированный массив примитивов
val objectArray: Array<Int> = arrayOf(1, 2, 3)      // Массив упакованных `Int`
```

**List**: Обобщённый тип, концептуально хранит элементы типа `T`. Отдельных примитивных `List`-типов (вроде `IntList`) в стандартной библиотеке нет; `List<Int>` использует упакованные значения там, где это релевантно для целевой платформы.

```kotlin
val list: List<Int> = listOf(1, 2, 3)
```

#### 3. Функциональность

**Array**: Поддерживает индексированный доступ, изменение элементов, итерацию и ряд функций-расширений, но API обычно уже, чем у коллекций.

```kotlin
val array = arrayOf(1, 2, 3)
array[0] = 10
val size = array.size
```

**List / MutableList**: `List` предоставляет богатый набор операций только для чтения (map, filter и др.) как функции-расширения. `MutableList` добавляет операции изменения.

```kotlin
val list = listOf(1, 2, 3, 4, 5)
val filtered = list.filter { it > 2 }  // [3, 4, 5]
val mapped = list.map { it * 2 }       // [2, 4, 6, 8, 10]
val sum = list.sum()                   // 15
val contains = list.contains(3)        // true

val mutableList = mutableListOf(1, 2, 3)
mutableList.add(4)
mutableList[0] = 10
```

#### 4. Производительность

И массивы, и списки на базе массивов обеспечивают O(1) доступ по индексу.

**Array**:
- Фиксированный размер.
- Специализированные массивы примитивов (`IntArray` и др.) более эффективны по памяти и часто быстрее за счёт отсутствия boxing.

```kotlin
val array = IntArray(1_000_000)
array[500_000] = 42  // O(1)
```

**MutableList (на базе `ArrayList`)**:
- Амортизированная O(1) вставка в конец, при расширении возможно перевыделение памяти.
- Для примитивов (`MutableList<Int>`) используются упакованные значения на JVM.

```kotlin
val list = MutableList(1_000_000) { 0 }
list.add(42)  // Амортизированная O(1), иногда с перевыделением
```

Массивы часто выбирают для:
- производительно критичного, индексного доступа и фиксированного размера,
- работы с примитивами.

`MutableList` — для:
- частых структурных изменений,
- использования идиоматичного API коллекций.

#### 5. Примеры Использования

```kotlin
// Array — фиксированный набор известной длины
val daysOfWeek = arrayOf("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")

// MutableList — динамический размер
val shoppingList = mutableListOf("Хлеб", "Молоко")
shoppingList.add("Яйца")
shoppingList.remove("Молоко")
```

### Когда Использовать

**Array**:
- Известный фиксированный размер
- Высокая производительность индексного доступа
- Работа с примитивами (`IntArray`, `ByteArray` и т.д.)
- Interop с Java API, ожидающими массивы

**List / MutableList**:
- Нужен богатый, идиоматичный API коллекций
- Нужен интерфейс только для чтения (`List`)
- Нужен динамически изменяемый размер и операции модификации (`MutableList`)
- Предпочитается читаемость и гибкость

**Краткое содержание**: Массивы имеют фиксированную длину и подходят для низкоуровневых, индексных и примитивных операций. Коллекции Kotlin представлены интерфейсами: `List` — только для чтения, `MutableList` — изменяемый динамический список, обычно на базе массива. Оба варианта дают O(1) доступ по индексу, но специализированные массивы могут быть эффективнее; списки, как правило, выразительнее и удобнее для прикладного кода.

## Answer (EN)

Arrays and lists are data structures for storing collections of elements.

In Kotlin it's also important to distinguish between:
- `Array` vs collection types (`List`, `MutableList`, etc.)
- read-only interfaces (`List`) vs mutable ones (`MutableList`).

### Key Differences

#### 1. Size and Mutability

**Array**: Has a fixed size after creation; you can change elements, but not the length.

```kotlin
val array = arrayOf(1, 2, 3, 4, 5)
// array.size == 5, length cannot be changed
array[0] = 10 // OK: arrays are mutable by default
```

**List**: The `List` interface itself is read-only (no add/remove). To have a resizable collection, use `MutableList` (e.g. via `mutableListOf`). On the JVM, `MutableList` is typically backed by `ArrayList`, which grows dynamically.

```kotlin
val list: List<Int> = listOf(1, 2, 3)
// list.add(4) // ERROR: List is read-only

val mutableList = mutableListOf(1, 2, 3)
mutableList.add(4)      // Size becomes 4
mutableList.removeAt(0) // Size becomes 3
```

#### 2. Typing and Representation

**Array**: A Kotlin `Array<T>` stores references to elements of type `T`. For primitives there are specialized array types (e.g. `IntArray`, `LongArray`) to avoid boxing overhead (on JVM they map to primitive arrays like `int[]`).

```kotlin
val intArray: IntArray = intArrayOf(1, 2, 3)       // Specialized primitive array
val objectArray: Array<Int> = arrayOf(1, 2, 3)     // Array of boxed `Int` values
```

**List**: Is generic and conceptually holds elements of type `T`. Kotlin does not provide primitive-specialized `List` types like `IntList`; `List<Int>` uses boxed values where relevant for the target platform.

```kotlin
val list: List<Int> = listOf(1, 2, 3)
```

#### 3. Functionality

**Array**: Supports indexed access, mutation, iteration, and some extension functions, but has a more limited API compared to Kotlin collection interfaces.

```kotlin
val array = arrayOf(1, 2, 3)
array[0] = 10
val size = array.size
```

**List / MutableList**: `List` provides rich read-only operations (map, filter, etc.) as extension functions. `MutableList` adds modification operations.

```kotlin
val list = listOf(1, 2, 3, 4, 5)
val filtered = list.filter { it > 2 }   // [3, 4, 5]
val mapped = list.map { it * 2 }        // [2, 4, 6, 8, 10]
val sum = list.sum()                    // 15
val contains = list.contains(3)         // true

val mutableList = mutableListOf(1, 2, 3)
mutableList.add(4)
mutableList[0] = 10
```

#### 4. Performance

Both arrays and lists backed by arrays provide O(1) access by index.

**Array**:
- Fixed size.
- Primitive arrays (`IntArray`, etc.) are memory-efficient and can be faster due to no boxing.

```kotlin
val array = IntArray(1_000_000)
array[500_000] = 42  // O(1)
```

**MutableList (ArrayList-backed)**:
- Provides amortized O(1) `add` at the end, but may occasionally reallocate underlying storage.
- Uses boxed types for primitives on JVM (`MutableList<Int>` stores boxed `Int`).

```kotlin
val list = MutableList(1_000_000) { 0 }
list.add(42)  // Amortized O(1), may trigger reallocation
```

Arrays are often preferred for:
- performance-sensitive, index-heavy, fixed-size or primitive-heavy data.

Mutable lists are preferred for:
- frequent structural modifications,
- idiomatic use of Kotlin collection APIs.

#### 5. Use Cases

```kotlin
// Array - fixed size sequence of known length
val daysOfWeek = arrayOf("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

// MutableList - dynamic size
val shoppingList = mutableListOf("Bread", "Milk")
shoppingList.add("Eggs")
shoppingList.remove("Milk")
```

### When to Use

**Array**:
- Known fixed size
- High-performance, index-based access
- Working with primitive types (`IntArray`, `ByteArray`, etc.)
- Interop with Java APIs that require arrays

**List / MutableList**:
- Need a richer, idiomatic collections API
- Need a read-only view over a collection (`List`)
- Need dynamic size and mutation operations (`MutableList`)
- Prefer clarity and flexibility over manual size management

**Summary**: Arrays have fixed length and are good for low-level, index-based and primitive-heavy operations. Kotlin lists are collection interfaces; `List` is read-only, `MutableList` is resizable and mutable, backed typically by an array. Both provide O(1) index access, but arrays (especially primitive arrays) can be more efficient; lists are generally more expressive and convenient for typical application code.

## Дополнительные Вопросы (RU)

- В чём ключевые отличия работы с массивами и списками в Kotlin по сравнению с Java?
- Когда вы бы использовали `Array` или `List`/`MutableList` на практике?
- Какие распространённые ошибки при выборе между `Array` и `List` стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-collections]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-collections]]

## Связанные Вопросы (RU)

- [[q-equals-hashcode-purpose--kotlin--medium]]
- [[q-visibility-modifiers-kotlin--kotlin--medium]]
- [[q-catch-operator-flow--kotlin--medium]]

## Related Questions

- [[q-equals-hashcode-purpose--kotlin--medium]]
- [[q-visibility-modifiers-kotlin--kotlin--medium]]
- [[q-catch-operator-flow--kotlin--medium]]
