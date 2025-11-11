---
id: cs-008
title: "Iterator Pattern / Паттерн Итератор"
aliases: ["Iterator Pattern", "Паттерн Итератор"]
topic: cs
subtopics: [behavioral]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, c-collections]
created: 2025-10-15
updated: 2025-11-11
tags: [behavioral-patterns, collection-traversal, design-patterns, difficulty/medium, iterator]
sources: ["https://refactoring.guru/design-patterns/iterator"]
---

# Вопрос (RU)
> Что такое паттерн Итератор? Когда его использовать и как он работает?

# Question (EN)
> What is the Iterator pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория Iterator Pattern:**
Iterator — поведенческий (behavioral) шаблон проектирования для последовательного доступа к элементам агрегата без раскрытия его внутреннего представления. Решает проблему: элементы агрегата должны быть доступны и обходиться без раскрытия представления и без жёсткой привязки клиентов к конкретной структуре коллекции. Решение: определить отдельный объект-итератор, инкапсулирующий доступ и обход. Клиенты используют итератор для доступа к агрегату, не зная его структуры.

**Определение:**

*Теория:* Iterator pattern предоставляет способ последовательного доступа к элементам агрегата без раскрытия его внутреннего представления. Определяет отдельный объект (итератор), который инкапсулирует детали обхода элементов агрегата. Это позволяет агрегату изменять внутреннюю структуру без влияния на способ доступа к элементам и отделяет алгоритмы обхода от конкретных коллекций через единый интерфейс итерации.

Важно: в классическом варианте метод `next()` возвращает следующий элемент и считается ошибкой вызывать его без предварительной проверки `hasNext()` (часто это приводит к исключению при отсутствии элементов).

**Проблемы, которые решает:**

*Теория:* Основные проблемы:
- Элементы агрегата должны быть доступны без раскрытия внутреннего представления.
- Нужно определять новые варианты обхода (прямой, обратный, фильтрованный и т.п.) без изменения интерфейса агрегата.
- Когда операции доступа определены прямо в интерфейсе агрегата, это делает дизайн негибким и жёстко связывает агрегат с конкретными сценариями обхода.

Iterator позволяет:
- иметь несколько независимых обходов для одного агрегата;
- добавлять новые варианты обхода без изменения кода коллекции (через новые итераторы);
- использовать единый интерфейс обхода для разных коллекций.

```kotlin
// ✅ Базовый пример с собственным итератором (НЕ переопределяем kotlin.collections.Iterator)

class BookShelfIterator(private val bookShelf: BookShelf) : Iterator<Book> {
    private var index = 0

    override fun hasNext(): Boolean = index < bookShelf.getLength()

    override fun next(): Book {
        if (!hasNext()) throw NoSuchElementException()
        return bookShelf.getBookAt(index++)
    }
}

class BookShelf : Iterable<Book> {
    private val books = mutableListOf<Book>()

    fun addBook(book: Book) = books.add(book)
    fun getLength() = books.size
    fun getBookAt(index: Int) = books[index]

    override fun iterator(): Iterator<Book> = BookShelfIterator(this)
}

data class Book(val name: String)

// Использование
fun main() {
    val bookShelf = BookShelf().apply {
        addBook(Book("Design Patterns"))
        addBook(Book("Effective Java"))
        addBook(Book("Clean Code"))
    }

    for (book in bookShelf) {  // ✅ Итерация через for-in
        println(book.name)
    }
}
```

**Kotlin встроенная поддержка:**

*Теория:* В Kotlin есть встроенная поддержка итераторов через интерфейсы `Iterable<T>` и `Iterator<T>` из стандартной библиотеки. Стандартные коллекции реализуют эти интерфейсы. Циклы `for-in` используют итераторы под капотом. Можно создавать свои коллекции, реализуя `Iterable<T>`, и предоставлять собственные `Iterator<T>`. Функциональные операторы (`map`, `filter`, `forEach` и др.) доступны для стандартных коллекций и для типов, для которых определены соответствующие extension-функции.

```kotlin
// ✅ Kotlin Iterator поддержка
class CustomCollection<T> : Iterable<T> {
    private val items = mutableListOf<T>()

    fun add(item: T) = items.add(item)

    override fun iterator(): Iterator<T> = items.iterator()
}

// ✅ Использование с преобразованием в стандартную коллекцию
val collection = CustomCollection<String>().apply {
    add("A")
    add("B")
    add("C")
}

for (item in collection) {
    println(item)
}

// Для использования стандартных функциональных операций преобразуем к List
collection.toList()
    .filter { it.length > 0 }
    .map { it.uppercase() }
    .forEach { println(it) }
```

**Multiple Traversals:**

*Теория:* Iterator позволяет иметь несколько итераторов для одного агрегата одновременно. Каждый итератор хранит независимое состояние обхода. Это позволяет обходить одну и ту же коллекцию разными способами или в разных частях алгоритма параллельно. Полезно для: вложенных циклов, многошаговых алгоритмов, разных порядков обхода.

```kotlin
// ✅ Multiple iterators на одной коллекции
class CustomList<T> : Iterable<T> {
    private val items = mutableListOf<T>()

    fun add(item: T) = items.add(item)
    override fun iterator(): Iterator<T> = items.iterator()
}

fun processPairs(collection: CustomList<Int>) {
    val iterator1 = collection.iterator()

    while (iterator1.hasNext()) {
        val a = iterator1.next()
        val iterator2 = collection.iterator() // независимый итератор для каждого a
        while (iterator2.hasNext()) {
            val b = iterator2.next()
            println("Pair: ($a, $b)")
        }
    }
}
```

**Custom Iterator Implementations:**

*Теория:* Можно создавать custom-итераторы для специальных схем обхода. Примеры: обратный обход, фильтрованный обход, объединённый обход нескольких источников, потенциально бесконечные последовательности. Custom-итераторы инкапсулируют логику обхода и позволяют иметь специализированное поведение под конкретные use-case.

```kotlin
// ✅ Custom reverse iterator
class ReverseIterator<T>(private val list: List<T>) : Iterator<T> {
    private var index = list.size - 1

    override fun hasNext(): Boolean = index >= 0

    override fun next(): T {
        if (!hasNext()) throw NoSuchElementException()
        return list[index--]
    }
}

class ReversibleList<T>(private val items: MutableList<T>) : Iterable<T> {
    fun add(item: T) = items.add(item)
    override fun iterator(): Iterator<T> = items.iterator()
    fun reverseIterator(): Iterator<T> = ReverseIterator(items)
}

// Использование
val list = ReversibleList<Int>(mutableListOf(1, 2, 3, 4, 5))
for (item in list.reverseIterator()) {
    println(item)  // 5, 4, 3, 2, 1
}
```

**Когда использовать:**

*Теория:* Используйте Iterator, когда:
- коллекции нужно обходить контролируемым и единообразным образом;
- детали реализации коллекции должны быть скрыты;
- разные коллекции нужно обходить одинаковым образом через общий интерфейс;
- нужны разные варианты обхода без изменения самих коллекций.

Не обязательно усложнять дизайн Iterатором, когда:
- коллекции простые, а прямой доступ понятен и эффективен;
- накладные расходы на создание и использование итераторов критичны;
- приоритет отдан произвольному доступу по индексу, а не последовательному обходу.

✅ **Use Iterator when:**
- Collections need controlled, uniform traversal
- Implementation details must be hidden
- Different collections should be traversed via common interface
- You need multiple/custom traversal strategies without changing collections

❌ **Don't use Iterator when:**
- A very simple collection can be accessed directly without loss of clarity
- Performance overhead of iterator allocation/indirection is critical
- Random access is more important than sequential traversal

**Преимущества:**

1. **Упрощает обход** — стандартный способ итерироваться по коллекциям.
2. **Развязывает алгоритмы и коллекции** — один и тот же код обхода для разных структур.
3. **Поддерживает несколько обходов** — несколько независимых итераторов на одну коллекцию.
4. **Single Responsibility** — логика обхода отделена от логики хранения.

**Недостатки:**

1. **Усложнение** — для простых структур может быть избыточен.
2. **Накладные расходы** — возможен оверхед по сравнению с прямым доступом.
3. **Состояние итератора** — требуется аккуратно поддерживать корректное состояние.

**Ключевые концепции:**

1. **Инкапсуляция** — итератор инкапсулирует логику обхода.
2. **Абстракция** — скрывает реализацию коллекции.
3. **Полиморфизм** — единый интерфейс работы с разными коллекциями.
4. **Управление состоянием** — итератор хранит прогресс обхода.
5. **Разделение ответственности** — обход отделён от логики хранения.

## Answer (EN)

**Iterator Pattern Theory:**
Iterator is a behavioral design pattern that provides sequential access to elements of an aggregate object without exposing its internal representation. It solves the problem of making elements of a collection accessible and traversable without tying clients to the concrete data structure. The solution: define a separate iterator object that encapsulates access and traversal. Clients use the iterator to access the aggregate without knowing its internal structure.

**Definition:**

*Theory:* The Iterator pattern provides a way to access elements of an aggregate object sequentially without exposing its underlying representation. It defines a separate object (iterator) that encapsulates the details of traversing the elements of the aggregate. This allows the aggregate to change its internal structure without affecting how clients iterate over it and decouples algorithms from concrete collection types via a unified iteration interface.

Important: in the classic form, `next()` returns the next element and it is an error to call it without checking `hasNext()` first (often resulting in an exception if there are no more elements).

**Problems Solved:**

*Theory:* Main problems:
- Elements of an aggregate must be accessible without exposing the internal structure.
- New traversal strategies (forward, reverse, filtered, etc.) should be addable without changing the aggregate's interface.
- When traversal logic is baked into the aggregate interface, it becomes inflexible and tightly coupled to specific operations.

Iterator allows you to:
- have multiple independent traversals over the same aggregate;
- add new traversal strategies without modifying the collection code (by adding new iterators);
- use a unified traversal interface for different collections.

```kotlin
// ✅ Basic example with a custom iterator (do NOT redefine kotlin.collections.Iterator)

class BookShelfIterator(private val bookShelf: BookShelf) : Iterator<Book> {
    private var index = 0

    override fun hasNext(): Boolean = index < bookShelf.getLength()

    override fun next(): Book {
        if (!hasNext()) throw NoSuchElementException()
        return bookShelf.getBookAt(index++)
    }
}

class BookShelf : Iterable<Book> {
    private val books = mutableListOf<Book>()

    fun addBook(book: Book) = books.add(book)
    fun getLength() = books.size
    fun getBookAt(index: Int) = books[index]

    override fun iterator(): Iterator<Book> = BookShelfIterator(this)
}

data class Book(val name: String)

// Usage
fun main() {
    val bookShelf = BookShelf().apply {
        addBook(Book("Design Patterns"))
        addBook(Book("Effective Java"))
        addBook(Book("Clean Code"))
    }

    for (book in bookShelf) {  // ✅ Iteration via for-in
        println(book.name)
    }
}
```

**Kotlin Built-in Support:**

*Theory:* Kotlin has built-in iterator support via `Iterable<T>` and `Iterator<T>` from the standard library. Standard collections implement these interfaces. `for-in` loops use iterators under the hood. You can create custom collections by implementing `Iterable<T>` and providing your own `Iterator<T>`. Functional operators like `map`, `filter`, and `forEach` are available on standard collection types and on types for which proper extension functions are defined.

```kotlin
// ✅ Kotlin Iterator support
class CustomCollection<T> : Iterable<T> {
    private val items = mutableListOf<T>()

    fun add(item: T) = items.add(item)

    override fun iterator(): Iterator<T> = items.iterator()
}

// Usage
val collection = CustomCollection<String>().apply {
    add("A")
    add("B")
    add("C")
}

for (item in collection) {
    println(item)
}

// To use standard functional operations, convert to a standard collection
collection.toList()
    .filter { it.length > 0 }
    .map { it.uppercase() }
    .forEach { println(it) }
```

**Multiple Traversals:**

*Theory:* Iterator supports having multiple iterators over the same aggregate at the same time. Each iterator maintains its own traversal state. This allows traversing the same collection in different ways or in parallel parts of an algorithm. Useful for: nested loops, multi-pass algorithms, different iteration orders.

```kotlin
// ✅ Multiple iterators on the same collection
class CustomList<T> : Iterable<T> {
    private val items = mutableListOf<T>()

    fun add(item: T) = items.add(item)
    override fun iterator(): Iterator<T> = items.iterator()
}

fun processPairs(collection: CustomList<Int>) {
    val iterator1 = collection.iterator()

    while (iterator1.hasNext()) {
        val a = iterator1.next()
        val iterator2 = collection.iterator() // independent iterator for each outer element
        while (iterator2.hasNext()) {
            val b = iterator2.next()
            println("Pair: ($a, $b)")
        }
    }
}
```

**Custom Iterator Implementations:**

*Theory:* You can create custom iterators for special traversal patterns, such as reverse iteration, filtered iteration, zipping multiple sources, or infinite/lazy sequences. Custom iterators encapsulate traversal logic and provide specialized behavior for specific use cases.

```kotlin
// ✅ Custom reverse iterator
class ReverseIterator<T>(private val list: List<T>) : Iterator<T> {
    private var index = list.size - 1

    override fun hasNext(): Boolean = index >= 0

    override fun next(): T {
        if (!hasNext()) throw NoSuchElementException()
        return list[index--]
    }
}

class ReversibleList<T>(private val items: MutableList<T>) : Iterable<T> {
    fun add(item: T) = items.add(item)
    override fun iterator(): Iterator<T> = items.iterator()
    fun reverseIterator(): Iterator<T> = ReverseIterator(items)
}

// Usage
val list = ReversibleList<Int>(mutableListOf(1, 2, 3, 4, 5))
for (item in list.reverseIterator()) {
    println(item)  // 5, 4, 3, 2, 1
}
```

**When to Use:**

*Theory:* Use Iterator when:
- collections need controlled, uniform traversal;
- collection implementation details should remain hidden;
- different collection types must be traversed in a consistent way via a common API;
- you need multiple/custom traversal strategies without modifying the collections.

You might avoid explicit Iterator pattern when:
- collections are trivial and direct access is clearer and efficient enough;
- iterator overhead is critical in hot paths;
- random access by index is the primary operation, not sequential traversal.

✅ **Use Iterator when:**
- Collections need controlled, uniform traversal
- Implementation details must be hidden
- Different collections should share a common traversal interface
- Multiple/custom traversals are required

❌ **Don't use Iterator when:**
- Very simple collections are easier to access directly
- Performance overhead of iterator usage is critical
- Random access is more important than sequential traversal

**Advantages:**

1. **Simplifies Traversal** — standard way to iterate over collections.
2. **Decouples Algorithms** — same traversal logic works with different collections.
3. **Multiple Traversals** — multiple independent iterators on the same collection.
4. **Single Responsibility** — iteration logic separated from storage logic.

**Disadvantages:**

1. **Increased Complexity** — may be overkill for simple structures.
2. **Performance Overhead** — can be less efficient than direct access.
3. **Iterator State** — requires careful state management.

**Key Concepts:**

1. **Encapsulation** — iterator encapsulates traversal logic.
2. **Abstraction** — hides collection implementation details.
3. **Polymorphism** — unified interface for different collections.
4. **State Management** — iterator maintains traversal state.
5. **Separation of Concerns** — traversal separated from collection logic.

---

## Дополнительные вопросы (RU)

- Как паттерн Итератор соотносится с паттерном Компоновщик (Composite)?
- В чем разница между паттернами Итератор и Посетитель (Visitor)?
- Как работает цикл `for-in` в Kotlin под капотом?

## Follow-ups

- How does Iterator pattern relate to Composite pattern?
- What is the difference between Iterator and Visitor pattern?
- How does Kotlin's for-in loop work under the hood?

## Связанные вопросы (RU)

### Предпосылки (проще)
- Базовые коллекции в Kotlin
- Понимание интерфейса `Iterable`

### Связанные (того же уровня)
- [[q-facade-pattern--design-patterns--medium]] - Паттерн Фасад
- [[q-visitor-pattern--design-patterns--hard]] - Паттерн Посетитель

### Продвинутые (сложнее)
- Кастомные реализации итераторов
- Оптимизация производительности итераций
- Реактивные потоки vs итераторы

## Related Questions

### Prerequisites (Easier)
- Basic Kotlin collections
- Understanding of Iterable interface

### Related (Same Level)
- [[q-facade-pattern--design-patterns--medium]] - Facade pattern
- [[q-visitor-pattern--design-patterns--hard]] - Visitor pattern

### Advanced (Harder)
- Custom iterator implementations
- Iteration performance optimization
- Reactive streams vs Iterators

## References

- [[c-architecture-patterns]]
- [[c-collections]]
- ["https://refactoring.guru/design-patterns/iterator"]
