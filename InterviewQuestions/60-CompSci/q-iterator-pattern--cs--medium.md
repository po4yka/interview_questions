---
id: cs-008
title: "Iterator Pattern / Паттерн Итератор"
aliases: ["Iterator Pattern", "Паттерн Итератор"]
topic: cs
subtopics: [behavioral-patterns, collection-traversal, design-patterns]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-composite-pattern--design-patterns--medium, q-facade-pattern--design-patterns--medium, q-visitor-pattern--design-patterns--hard]
created: 2025-10-15
updated: 2025-01-25
tags: [behavioral-patterns, collection-traversal, design-patterns, difficulty/medium, iterator, kotlin]
sources: [https://refactoring.guru/design-patterns/iterator]
date created: Monday, October 6th 2025, 7:33:52 am
date modified: Sunday, October 26th 2025, 12:07:59 pm
---

# Вопрос (RU)
> Что такое паттерн Итератор? Когда его использовать и как он работает?

# Question (EN)
> What is the Iterator pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория Iterator Pattern:**
Iterator - behavioral design pattern для sequential доступа к elements aggregate object без exposing его internal representation. Решает проблему: элементы aggregate должны быть accessible и traversed без exposing representation. Решение: define separate iterator object, инкапсулирующий access и traversal. Clients используют iterator для доступа к aggregate, не зная его structure.

**Определение:**

*Теория:* Iterator pattern предоставляет way to access elements aggregate object sequentially без exposing underlying representation. Определяет separate object (iterator), который encapsulates details traversing elements aggregate. Позволяет aggregate изменять internal structure без affecting способ доступа к elements. Decouples algorithms от collections через единый iteration interface.

**Проблемы, которые решает:**

*Теория:* Основные проблемы: элементы aggregate должны быть accessible без exposing representation; новые traversal operations должны быть defined без changing interface aggregate; когда access operations defined в aggregate interface - это inflexible, commits aggregate к particular operations. Iterator позволяет иметь multiple traversals для одного aggregate, add new operations без changing aggregate.

```kotlin
// ✅ Базовый Iterator пример
interface Iterator<T> {
    fun hasNext(): Boolean
    fun next(): T?
}

class BookShelfIterator(private val bookShelf: BookShelf) : Iterator<Book> {
    private var index = 0

    override fun hasNext(): Boolean = index < bookShelf.getLength()

    override fun next(): Book? = bookShelf.getBookAt(index++)
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

*Теория:* Kotlin имеет built-in поддержку Iterator через `Iterable<T>` interface и `Iterator<T>` interface. Collections автоматически implement эти interfaces. For-in loops используют iterators под капотом. Можно создавать custom iterators для custom collections. Можно использовать functional operators (map, filter, forEach).

```kotlin
// ✅ Kotlin Iterator поддержка
class CustomCollection<T> : Iterable<T> {
    private val items = mutableListOf<T>()

    fun add(item: T) = items.add(item)

    override fun iterator(): Iterator<T> = items.iterator()
}

// ✅ Использование
val collection = CustomCollection<String>().apply {
    add("A")
    add("B")
    add("C")
}

// For-in loop
for (item in collection) {
    println(item)
}

// Functional operations
collection
    .filter { it.length > 1 }
    .map { it.uppercase() }
    .forEach { println(it) }
```

**Multiple Traversals:**

*Теория:* Iterator поддерживает multiple iterators на одном aggregate одновременно. Каждый iterator поддерживает independent traversal state. Позволяет traverse same collection разными способами одновременно. Полезно для: nested loops, multi-pass algorithms, different traversal orders.

```kotlin
// ✅ Multiple iterators на одной коллекции
class CustomList<T> : Iterable<T> {
    private val items = mutableListOf<T>()

    fun add(item: T) = items.add(item)
    override fun iterator() = items.iterator()
}

fun processPairs(collection: CustomList<Int>) {
    val iterator1 = collection.iterator()
    val iterator2 = collection.iterator()

    while (iterator1.hasNext()) {
        val a = iterator1.next()
        while (iterator2.hasNext()) {
            val b = iterator2.next()
            println("Pair: ($a, $b)")
        }
    }
}
```

**Custom Iterator Implementations:**

*Теория:* Можно создавать custom iterators для специальных traversal patterns. Примеры: reverse iteration, filtered iteration, zipped iteration, infinite iteration. Custom iterators инкапсулируют логику traversal. Позволяют иметь specialized iteration behavior для конкретных use cases.

```kotlin
// ✅ Custom reverse iterator
class ReverseIterator<T>(private val list: List<T>) : Iterator<T> {
    private var index = list.size - 1

    override fun hasNext() = index >= 0

    override fun next() = list[index--]
}

class ReversibleList<T>(private val items: MutableList<T>) {
    fun add(item: T) = items.add(item)
    fun iterator() = items.iterator()
    fun reverseIterator() = ReverseIterator(items)
}

// Использование
val list = ReversibleList<Int>(mutableListOf(1, 2, 3, 4, 5))
for (item in list.reverseIterator()) {
    println(item)  // 5, 4, 3, 2, 1
}
```

**Когда использовать:**

*Теория:* Используйте Iterator когда: коллекции нужно обходить controlled manner; collection implementation details hidden и complex; разные коллекции нужно обходить similarly; нужна consistency iteration across different implementations. Не используйте для: simple collections где direct access более efficient; когда performance критичен и iterator overhead значим.

✅ **Use Iterator when:**
- Collections нужен controlled traversal
- Implementation details должны быть hidden
- Different collections нужно traverse similarly
- Нужна consistency в iteration

❌ **Don't use Iterator when:**
- Simple collections с direct access более efficient
- Performance критичен и iterator overhead значим
- Random access более important, чем sequential

**Преимущества:**

1. **Simplifies Traversal** - standard way to iterate collections
2. **Decouples Algorithms** - same iteration logic с different collections
3. **Multiple Traversals** - multiple iterators на same collection
4. **Single Responsibility** - iteration logic separated от collection

**Недостатки:**

1. **Increased Complexity** - для simple collections может быть overkill
2. **Performance Overhead** - может быть less efficient чем direct access
3. **Iterator State** - нужно maintain iterator state

**Ключевые концепции:**

1. **Encapsulation** - iterator encapsulates traversal logic
2. **Abstraction** - hides collection implementation
3. **Polymorphism** - iterators работают с different collections
4. **State Management** - iterator maintains traversal state
5. **Separation of Concerns** - iteration отделён от collection logic

## Answer (EN)

**Iterator Pattern Theory:**
Iterator - behavioral design pattern for sequential access to elements of aggregate object without exposing its internal representation. Solves problem: elements of aggregate should be accessible and traversed without exposing representation. Solution: define separate iterator object encapsulating access and traversal. Clients use iterator to access aggregate without knowing its structure.

**Definition:**

*Theory:* Iterator pattern provides way to access elements of aggregate object sequentially without exposing underlying representation. Defines separate object (iterator), which encapsulates details of traversing elements of aggregate. Allows aggregate to change internal structure without affecting way to access elements. Decouples algorithms from collections through unified iteration interface.

**Problems Solved:**

*Theory:* Main problems: elements of aggregate should be accessible without exposing representation; new traversal operations should be defined without changing aggregate interface; when access operations defined in aggregate interface - inflexible, commits aggregate to particular operations. Iterator allows having multiple traversals for single aggregate, add new operations without changing aggregate.

```kotlin
// ✅ Basic Iterator example
interface Iterator<T> {
    fun hasNext(): Boolean
    fun next(): T?
}

class BookShelfIterator(private val bookShelf: BookShelf) : Iterator<Book> {
    private var index = 0

    override fun hasNext(): Boolean = index < bookShelf.getLength()

    override fun next(): Book? = bookShelf.getBookAt(index++)
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

    for (book in bookShelf) {  // ✅ Iteration through for-in
        println(book.name)
    }
}
```

**Kotlin Built-in Support:**

*Theory:* Kotlin has built-in support for Iterator through `Iterable<T>` interface and `Iterator<T>` interface. Collections automatically implement these interfaces. For-in loops use iterators under hood. Can create custom iterators for custom collections. Can use functional operators (map, filter, forEach).

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

// For-in loop
for (item in collection) {
    println(item)
}

// Functional operations
collection
    .filter { it.length > 1 }
    .map { it.uppercase() }
    .forEach { println(it) }
```

**Multiple Traversals:**

*Theory:* Iterator supports multiple iterators on one aggregate simultaneously. Each iterator maintains independent traversal state. Allows traversing same collection in different ways simultaneously. Useful for: nested loops, multi-pass algorithms, different traversal orders.

```kotlin
// ✅ Multiple iterators on same collection
class CustomList<T> : Iterable<T> {
    private val items = mutableListOf<T>()

    fun add(item: T) = items.add(item)
    override fun iterator() = items.iterator()
}

fun processPairs(collection: CustomList<Int>) {
    val iterator1 = collection.iterator()
    val iterator2 = collection.iterator()

    while (iterator1.hasNext()) {
        val a = iterator1.next()
        while (iterator2.hasNext()) {
            val b = iterator2.next()
            println("Pair: ($a, $b)")
        }
    }
}
```

**Custom Iterator Implementations:**

*Theory:* Can create custom iterators for special traversal patterns. Examples: reverse iteration, filtered iteration, zipped iteration, infinite iteration. Custom iterators encapsulate traversal logic. Allow having specialized iteration behavior for specific use cases.

```kotlin
// ✅ Custom reverse iterator
class ReverseIterator<T>(private val list: List<T>) : Iterator<T> {
    private var index = list.size - 1

    override fun hasNext() = index >= 0

    override fun next() = list[index--]
}

class ReversibleList<T>(private val items: MutableList<T>) {
    fun add(item: T) = items.add(item)
    fun iterator() = items.iterator()
    fun reverseIterator() = ReverseIterator(items)
}

// Usage
val list = ReversibleList<Int>(mutableListOf(1, 2, 3, 4, 5))
for (item in list.reverseIterator()) {
    println(item)  // 5, 4, 3, 2, 1
}
```

**When to Use:**

*Theory:* Use Iterator when: collections need controlled traversal; collection implementation details hidden and complex; different collections need traversing similarly; need consistency in iteration across different implementations. Don't use for: simple collections where direct access more efficient; when performance critical and iterator overhead significant.

✅ **Use Iterator when:**
- Collections need controlled traversal
- Implementation details must be hidden
- Different collections need traversing similarly
- Need consistency in iteration

❌ **Don't use Iterator when:**
- Simple collections with direct access more efficient
- Performance critical and iterator overhead significant
- Random access more important than sequential

**Advantages:**

1. **Simplifies Traversal** - standard way to iterate collections
2. **Decouples Algorithms** - same iteration logic with different collections
3. **Multiple Traversals** - multiple iterators on same collection
4. **Single Responsibility** - iteration logic separated from collection

**Disadvantages:**

1. **Increased Complexity** - for simple collections may be overkill
2. **Performance Overhead** - may be less efficient than direct access
3. **Iterator State** - need to maintain iterator state

**Key Concepts:**

1. **Encapsulation** - iterator encapsulates traversal logic
2. **Abstraction** - hides collection implementation
3. **Polymorphism** - iterators work with different collections
4. **State Management** - iterator maintains traversal state
5. **Separation of Concerns** - iteration separated from collection logic

---

## Follow-ups

- How does Iterator pattern relate to Composite pattern?
- What is the difference between Iterator and Visitor pattern?
- How does Kotlin's for-in loop work under the hood?

## Related Questions

### Prerequisites (Easier)
- Basic Kotlin collections
- Understanding of Iterable interface

### Related (Same Level)
- [[q-facade-pattern--design-patterns--medium]] - Facade pattern
- [[q-composite-pattern--design-patterns--medium]] - Composite pattern
- [[q-visitor-pattern--design-patterns--hard]] - Visitor pattern

### Advanced (Harder)
- Custom iterator implementations
- Iteration performance optimization
- Reactive streams vs Iterators
