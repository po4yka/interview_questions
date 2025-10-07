---
title: Iterator Pattern
topic: design-patterns
subtopics:
  - behavioral-patterns
  - collection-traversal
difficulty: medium
related:
  - composite-pattern
  - visitor-pattern
status: draft
---

# Iterator Pattern / Паттерн Итератор

## English

### Definition
The Iterator design pattern is a behavioral design pattern that provides a way to access the elements of an aggregate object (like a list) sequentially without exposing its underlying representation. It defines a separate object, called an iterator, which encapsulates the details of traversing the elements of the aggregate, allowing the aggregate to change its internal structure without affecting the way its elements are accessed.

### Problems It Solves
What problems can the Iterator design pattern solve?
- The elements of an aggregate object should be accessed and traversed without exposing its representation (data structures)
- New traversal operations should be defined for an aggregate object without changing its interface

Defining access and traversal operations in the aggregate interface is inflexible because it commits the aggregate to particular access and traversal operations and makes it impossible to add new operations later without having to change the aggregate interface.

### Solution
What solution does the Iterator design pattern describe?
- Define a separate (iterator) object that encapsulates accessing and traversing an aggregate object
- Clients use an iterator to access and traverse an aggregate without knowing its representation (data structures)

Different iterators can be used to access and traverse an aggregate in different ways. New access and traversal operations can be defined independently by defining new iterators.

### When to Use
The Iterator design pattern is particularly useful in scenarios where:
- **Collections need to be traversed in a controlled manner**. When iterating over a collection's elements in a specific order or with predefined conditions, the iterator pattern provides a structured and consistent way to manage the traversal
- **Collection's implementation details are hidden**. When the internal representation of a collection is complex or may change, the iterator pattern abstracts away the implementation details and provides a uniform interface for iteration
- **Different collections need to be traversed similarly**. When dealing with various types of collections, the iterator pattern allows for consistent iteration across different implementations, promoting code reuse and maintainability

### Implementation Steps
1. Create an `Iterator` interface that defines methods like `hasNext()` and `next()`
2. Create a concrete iterator for each collection class
3. The collection class should have a method to return its iterator

### Example in Kotlin

```kotlin
// Step 1: Define the Iterator interface
interface Iterator<T> {
    fun hasNext(): Boolean
    fun next(): T?
}

// Step 2: Concrete Iterator
class BookShelfIterator(private val bookShelf: BookShelf) : Iterator<Book> {
    private var index = 0

    override fun hasNext(): Boolean {
        return index < bookShelf.getLength()
    }

    override fun next(): Book? {
        return bookShelf.getBookAt(index++)
    }
}

// Aggregate class
class BookShelf : Iterable<Book> {
    private val books = mutableListOf<Book>()

    fun addBook(book: Book) {
        books.add(book)
    }

    fun getLength() = books.size

    fun getBookAt(index: Int) = books[index]

    override fun iterator(): Iterator<Book> = BookShelfIterator(this)
}

data class Book(val name: String)

// Client Code
fun main() {
    val bookShelf = BookShelf()
    bookShelf.addBook(Book("Design Patterns"))
    bookShelf.addBook(Book("Effective Java"))
    bookShelf.addBook(Book("Clean Code"))

    val iterator = bookShelf.iterator()
    while (iterator.hasNext()) {
        val book = iterator.next()
        println(book?.name)
    }
}
```

**Output:**
```
Design Patterns
Effective Java
Clean Code
```

**Explanation:**
- We defined an `Iterator` interface with essential methods: `hasNext()` and `next()`
- `BookShelfIterator` is a concrete implementation of this interface, tailored to work with the `BookShelf` class
- The `BookShelf` class, representing our collection, implements the `Iterable` interface and returns its custom iterator
- The client code demonstrates how to iterate over the `BookShelf` collection using the `BookShelfIterator`

### Advantages
- **Simplifies Collection Traversal**. It provides a standard way to iterate through different types of collections
- **Decouples Algorithms from Collections**. You can use the same iteration logic with different types of collections
- **Supports Multiple Traversals**. You can have multiple iterators on the same collection simultaneously
- **Promotes Single Responsibility**. The iteration logic is separated from the collection, adhering to the Single Responsibility Principle

### Disadvantages
- **Increased Complexity**. For simple collections, using an iterator might be overkill
- **Performance Overhead**. In some cases, using an iterator might be less efficient than accessing elements directly

---

## Русский

### Определение
Паттерн проектирования Итератор - это поведенческий паттерн проектирования, который предоставляет способ последовательного доступа к элементам агрегатного объекта (например, списка) без раскрытия его внутреннего представления. Он определяет отдельный объект, называемый итератором, который инкапсулирует детали обхода элементов агрегата, позволяя агрегату изменять свою внутреннюю структуру, не влияя на способ доступа к его элементам.

### Решаемые Проблемы
Какие проблемы решает паттерн Итератор?
- К элементам агрегатного объекта должен быть обеспечен доступ и обход без раскрытия его представления (структур данных)
- Новые операции обхода должны быть определены для агрегатного объекта без изменения его интерфейса

Определение операций доступа и обхода в интерфейсе агрегата негибко, потому что это привязывает агрегат к конкретным операциям доступа и обхода и делает невозможным добавление новых операций позже без необходимости изменения интерфейса агрегата.

### Решение
Какое решение описывает паттерн Итератор?
- Определить отдельный объект (итератор), который инкапсулирует доступ и обход агрегатного объекта
- Клиенты используют итератор для доступа и обхода агрегата, не зная его представления (структур данных)

Различные итераторы могут использоваться для доступа и обхода агрегата различными способами. Новые операции доступа и обхода могут быть определены независимо путем определения новых итераторов.

### Когда Использовать
Паттерн проектирования Итератор особенно полезен в сценариях, где:
- **Коллекции нужно обходить контролируемым образом**. При итерации по элементам коллекции в определенном порядке или с предопределенными условиями паттерн итератор предоставляет структурированный и последовательный способ управления обходом
- **Детали реализации коллекции скрыты**. Когда внутреннее представление коллекции сложное или может измениться, паттерн итератор абстрагирует детали реализации и предоставляет единообразный интерфейс для итерации
- **Различные коллекции нужно обходить одинаково**. При работе с различными типами коллекций паттерн итератор позволяет обеспечить последовательную итерацию по различным реализациям, способствуя повторному использованию кода и поддерживаемости

### Шаги Реализации
1. Создать интерфейс `Iterator`, который определяет методы типа `hasNext()` и `next()`
2. Создать конкретный итератор для каждого класса коллекции
3. Класс коллекции должен иметь метод для возврата своего итератора

### Пример на Kotlin

```kotlin
// Шаг 1: Определить интерфейс Iterator
interface Iterator<T> {
    fun hasNext(): Boolean
    fun next(): T?
}

// Шаг 2: Конкретный итератор
class BookShelfIterator(private val bookShelf: BookShelf) : Iterator<Book> {
    private var index = 0

    override fun hasNext(): Boolean {
        return index < bookShelf.getLength()
    }

    override fun next(): Book? {
        return bookShelf.getBookAt(index++)
    }
}

// Класс агрегата
class BookShelf : Iterable<Book> {
    private val books = mutableListOf<Book>()

    fun addBook(book: Book) {
        books.add(book)
    }

    fun getLength() = books.size

    fun getBookAt(index: Int) = books[index]

    override fun iterator(): Iterator<Book> = BookShelfIterator(this)
}

data class Book(val name: String)

// Клиентский код
fun main() {
    val bookShelf = BookShelf()
    bookShelf.addBook(Book("Design Patterns"))
    bookShelf.addBook(Book("Effective Java"))
    bookShelf.addBook(Book("Clean Code"))

    val iterator = bookShelf.iterator()
    while (iterator.hasNext()) {
        val book = iterator.next()
        println(book?.name)
    }
}
```

**Вывод:**
```
Design Patterns
Effective Java
Clean Code
```

**Объяснение:**
- Мы определили интерфейс `Iterator` с основными методами: `hasNext()` и `next()`
- `BookShelfIterator` - это конкретная реализация этого интерфейса, адаптированная для работы с классом `BookShelf`
- Класс `BookShelf`, представляющий нашу коллекцию, реализует интерфейс `Iterable` и возвращает свой пользовательский итератор
- Клиентский код демонстрирует, как перебирать коллекцию `BookShelf` с использованием `BookShelfIterator`

### Преимущества
- **Упрощает обход коллекций**. Предоставляет стандартный способ перебора различных типов коллекций
- **Отделяет алгоритмы от коллекций**. Можно использовать одну и ту же логику итерации с разными типами коллекций
- **Поддерживает множественные обходы**. Можно иметь несколько итераторов для одной и той же коллекции одновременно
- **Способствует принципу единственной ответственности**. Логика итерации отделена от коллекции, соблюдая принцип единственной ответственности

### Недостатки
- **Увеличенная сложность**. Для простых коллекций использование итератора может быть излишним
- **Накладные расходы производительности**. В некоторых случаях использование итератора может быть менее эффективным, чем прямой доступ к элементам

---

## References
- [Iterator Design Pattern - GeeksforGeeks](https://www.geeksforgeeks.org/iterator-pattern/)
- [Iterator pattern - Wikipedia](https://en.wikipedia.org/wiki/Iterator_pattern)
- [Iterator Design Pattern Use Case - Medium](https://medium.com/@mehar.chand.cloud/iterator-design-pattern-use-case-traverse-different-collections-bca646860c20)
- [Iterator Design Pattern in Kotlin](https://www.javaguides.net/2023/10/iterator-design-pattern-in-kotlin.html)
- [Iterator Design Pattern: A Comprehensive Guide - Medium](https://medium.com/system-design-by-harsh-khandelwal/iterator-design-pattern-a-comprehensive-guide-e8711ff48329)
- [Iterator Design Pattern - SourceMaking](https://sourcemaking.com/design_patterns/memento)
- [Iterator - Refactoring Guru](https://refactoring.guru/design-patterns/iterator)
- [Iterator Software Pattern Kotlin Examples](https://softwarepatterns.com/kotlin/iterator-software-pattern-kotlin-example)
- [The Iterator Design Pattern in Kotlin - Medium](https://medium.com/softaai-blogs/the-iterator-design-pattern-in-kotlin-simplified-and-explained-aac3d174a7aa)

---

**Source:** Kirchhoff-Android-Interview-Questions
**Attribution:** Content adapted from the Kirchhoff repository
