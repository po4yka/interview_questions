---
id: lang-030
title: "Iterator Concept / Концепция Iterator"
aliases: [Iterator Concept, Концепция Iterator]
topic: kotlin
subtopics: [c-collections, iterators]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-collections, q-iterator-order-guarantee--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [collections, design-patterns, difficulty/easy, iterator, kotlin]
---
# Вопрос (RU)
> Что такое итератор?

# Question (EN)
> What is an iterator?

## Ответ (RU)

Итератор — это объект, позволяющий поэлементно перебирать коллекцию (список, массив, множество и т.п.). Он абстрагирует внутреннюю структуру данных и предоставляет единый способ обхода.

### Интерфейс Iterator

Базовый интерфейс итератора в Kotlin:

```kotlin
interface Iterator<out T> {
    fun hasNext(): Boolean  // Проверяет, есть ли ещё элементы
    fun next(): T           // Возвращает следующий элемент
}
```

### Использование Iterator

- Ручной обход:

```kotlin
val list = listOf("A", "B", "C")
val iterator = list.iterator()

while (iterator.hasNext()) {
    val element = iterator.next()
    println(element)
}
// Вывод: A B C
```

- Цикл for (неявно использует iterator()):

```kotlin
val list = listOf("A", "B", "C")

for (element in list) {  // Под капотом вызывается iterator()
    println(element)
}
```

Итератор, как правило, одноразовый: после полного обхода его нельзя «перемотать назад» или использовать повторно; для нового обхода нужно получить новый итератор.

### MutableIterator

`MutableIterator` позволяет безопасно удалять элементы во время обхода:

```kotlin
interface MutableIterator<out T> : Iterator<T> {
    fun remove()  // Удаляет последний элемент, возвращённый next()
}
```

Пример:

```kotlin
val list = mutableListOf(1, 2, 3, 4, 5)
val iterator = list.iterator()

while (iterator.hasNext()) {
    val element = iterator.next()
    if (element % 2 == 0) {
        iterator.remove()  // Удаляем чётные числа
    }
}

println(list)  // [1, 3, 5]
```

### Пользовательский итератор

Можно реализовать собственный итератор, например, через `Iterable`:

```kotlin
class Range(private val start: Int, private val end: Int) : Iterable<Int> {
    override fun iterator(): Iterator<Int> {
        return object : Iterator<Int> {
            private var current = start

            override fun hasNext(): Boolean = current <= end

            override fun next(): Int {
                if (!hasNext()) throw NoSuchElementException()
                return current++
            }
        }
    }
}

// Использование
val range = Range(1, 5)
for (num in range) {
    println(num)  // 1 2 3 4 5
}
```

### Итераторы и стандартная библиотека Kotlin

Во многих случаях в Kotlin удобнее работать не с `Iterator` напрямую, а с:
- `Iterable` и коллекциями, у которых есть `iterator()`;
- `Sequence` для ленивых операций (`asSequence()` и цепочки `map`/`filter` и т.д.).

Многие функции высшего порядка (`forEach`, `map`, `filter`) определены для `Iterable`, `Sequence` или коллекций, а не для `Iterator`. Обычно вы:
- получаете `Iterator` из `Iterable` через `iterator()`, или
- работаете прямо с коллекцией/`Iterable`/`Sequence`, не опускаясь до «сырого» итератора.

Примеры:

```kotlin
val list = listOf(1, 2, 3, 4, 5)

// forEach для коллекции (Iterable)
list.forEach { println(it) }

// Ленивые операции через Sequence
list.asSequence()
    .filter { it % 2 == 0 }
    .forEach { println(it) }
```

### Преимущества итератора

1. Абстракция: не нужно знать внутреннее устройство коллекции.
2. Унифицированность: единый подход для разных коллекций.
3. Безопасность: снижает риск ошибок работы с индексами.
4. Гибкость: можно задать произвольную логику обхода.
5. Модификация: `MutableIterator` позволяет безопасно удалять элементы при обходе.

### Итератор против индексного цикла

```kotlin
val iterator = list.iterator()
while (iterator.hasNext()) {
    val item = iterator.next()
    println(item)
}
```

```kotlin
for (i in list.indices) {
    val item = list[i]
    println(item)
}
```

Когда предпочтителен итератор:
- работа с абстрактными коллекциями (неизвестно, есть ли быстрый доступ по индексу);
- нужно удалять элементы во время обхода;
- работа с последовательностями или потоками;
- эффективен для структур вроде `LinkedList` и других неиндексируемых структур.

Когда уместен доступ по индексу:
- нужен текущий индекс;
- используется `Array` или `ArrayList` (быстрый случайный доступ);
- нужно легко обращаться к элементам по позициям.

### Распространённая ошибка

`ConcurrentModificationException` при изменении коллекции во время обхода:

```kotlin
val list = mutableListOf(1, 2, 3, 4, 5)

// Неверно: изменение коллекции в for-each
for (element in list) {
    if (element % 2 == 0) {
        list.remove(element)  // ConcurrentModificationException!
    }
}

// Правильно: использовать iterator.remove()
val iterator = list.iterator()
while (iterator.hasNext()) {
    if (iterator.next() % 2 == 0) {
        iterator.remove()  // Безопасно
    }
}

// Альтернатива: создать новую отфильтрованную коллекцию
val filtered = list.filter { it % 2 != 0 }
```

## Answer (EN)

**Iterator** is an object that allows **element-by-element traversal** of a collection (list, array, set, etc.). It abstracts the underlying structure and provides a uniform way to iterate.

### Iterator Interface

**Core methods:**
```kotlin
interface Iterator<out T> {
    fun hasNext(): Boolean  // Check if more elements exist
    fun next(): T           // Get next element
}
```

### Using Iterator

**Manual iteration:**
```kotlin
val list = listOf("A", "B", "C")
val iterator = list.iterator()

while (iterator.hasNext()) {
    val element = iterator.next()
    println(element)
}
// Output: A B C
```

**For loop (uses iterator internally):**
```kotlin
val list = listOf("A", "B", "C")

for (element in list) {  // Calls iterator() behind the scenes
    println(element)
}
```

Remember that an `Iterator` is typically one-shot: once fully consumed, it cannot be rewound or reused; you create a new iterator for another traversal.

### MutableIterator

**Allows removal during iteration:**
```kotlin
interface MutableIterator<out T> : Iterator<T> {
    fun remove()  // Remove last element returned by next()
}
```

**Example:**
```kotlin
val list = mutableListOf(1, 2, 3, 4, 5)
val iterator = list.iterator()

while (iterator.hasNext()) {
    val element = iterator.next()
    if (element % 2 == 0) {
        iterator.remove()  // Remove even numbers
    }
}

println(list)  // [1, 3, 5]
```

### Custom Iterator

**Creating your own iterator:**
```kotlin
class Range(private val start: Int, private val end: Int) : Iterable<Int> {
    override fun iterator(): Iterator<Int> {
        return object : Iterator<Int> {
            private var current = start

            override fun hasNext(): Boolean = current <= end

            override fun next(): Int {
                if (!hasNext()) throw NoSuchElementException()
                return current++
            }
        }
    }
}

// Usage
val range = Range(1, 5)
for (num in range) {
    println(num)  // 1 2 3 4 5
}
```

### Iterator Methods in Kotlin

Be careful: in Kotlin, most higher-order functions like `forEach` and transformations like `map`, `filter`, `asSequence` are defined for `Iterable`, `Sequence`, or collections, not directly for `Iterator`. You typically:
- get an `Iterator` from an `Iterable` via `iterator()`, or
- work with the original `Iterable`/collection or `Sequence` instead of the raw `Iterator`.

Correct examples:

```kotlin
val list = listOf(1, 2, 3, 4, 5)

// forEach on the collection (Iterable)
list.forEach { println(it) }

// Use sequence for lazy operations
list.asSequence()
    .filter { it % 2 == 0 }
    .forEach { println(it) }
```

### Benefits of Iterator

1. **Abstraction**: Don't need to know internal structure.
2. **Uniformity**: Same interface for all collections.
3. **Safety**: Prevents index out of bounds errors.
4. **Flexibility**: Can implement custom iteration logic.
5. **Modification**: `MutableIterator` allows safe removal during iteration.

### Iterator Vs Index-Based Loop

**Iterator approach:**
```kotlin
val iterator = list.iterator()
while (iterator.hasNext()) {
    val item = iterator.next()
    println(item)
}
```

**Index-based approach:**
```kotlin
for (i in list.indices) {
    val item = list[i]
    println(item)
}
```

**When to use iterator:**
- Working with abstract collections (don't know if it's indexed).
- Need to remove elements during iteration.
- Working with sequences or streams.
- `LinkedList` or other non-indexed structures.

**When to use indices:**
- Need current index value.
- `ArrayList` or array (fast random access).
- Need to access multiple elements at once.

### Common Pitfall

**ConcurrentModificationException:**
```kotlin
val list = mutableListOf(1, 2, 3, 4, 5)

// - Wrong: Modifying collection while iterating
for (element in list) {
    if (element % 2 == 0) {
        list.remove(element)  // ConcurrentModificationException!
    }
}

// - Correct: Use iterator.remove()
val iterator = list.iterator()
while (iterator.hasNext()) {
    if (iterator.next() % 2 == 0) {
        iterator.remove()  // Safe
    }
}

// - Alternative: Filter to new list
val filtered = list.filter { it % 2 != 0 }
```

---

## Дополнительные вопросы (RU)

- В чём ключевые отличия реализации итераторов в Kotlin и Java?
- В каких практических случаях особенно полезно явно использовать итератор?
- Какие типичные ошибки при работе с итераторами стоит избегать?

## Follow-ups

- What are the key differences between iterators in Kotlin and Java?
- In which practical scenarios is it especially useful to use an iterator explicitly?
- What common mistakes when working with iterators should be avoided?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-collections]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-what-happens-to-unneeded-objects--programming-languages--easy]]
- [[q-interface-vs-abstract-class--programming-languages--medium]]

## Related Questions

- [[q-what-happens-to-unneeded-objects--programming-languages--easy]]
- [[q-interface-vs-abstract-class--programming-languages--medium]]
