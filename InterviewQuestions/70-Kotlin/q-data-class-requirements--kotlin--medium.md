---
'---id': kotlin-214
title: Data Class Requirements / Требования Data Class
aliases:
- Data Class Requirements
- Требования Data Class
topic: kotlin
subtopics:
- data-classes
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-aggregation
- c-app-signing
- c-backend
- c-binary-search
- c-binary-search-tree
- c-binder
- c-biometric-authentication
- c-bm25-ranking
- c-by-type
- c-cap-theorem
- c-ci-cd
- c-ci-cd-pipelines
- c-clean-code
- c-compiler-optimization
- c-compose-modifiers
- c-compose-phases
- c-compose-semantics
- c-computer-science
- c-concurrency
- c-cross-platform-development
- c-cross-platform-mobile
- c-cs
- c-data-classes
- c-data-loading
- c-debugging
- c-declarative-programming
- c-deep-linking
- c-density-independent-pixels
- c-dimension-units
- c-dp-sp-units
- c-dsl-builders
- c-dynamic-programming
- c-espresso-testing
- c-event-handling
- c-folder
- c-functional-programming
- c-gdpr-compliance
- c-gesture-detection
- c-gradle-build-cache
- c-gradle-build-system
- c-https-tls
- c-image-formats
- c-inheritance
- c-jit-aot-compilation
- c-kmm
- c-kotlin
- c-lambda-expressions
- c-lazy-grid
- c-lazy-initialization
- c-level
- c-load-balancing
- c-manifest
- c-memory-optimization
- c-memory-profiler
- c-microservices
- c-multipart-form-data
- c-multithreading
- c-mutablestate
- c-networking
- c-offline-first-architecture
- c-oop
- c-oop-concepts
- c-oop-fundamentals
- c-oop-principles
- c-play-console
- c-play-feature-delivery
- c-programming-languages
- c-properties
- c-real-time-communication
- c-references
- c-scaling-strategies
- c-scoped-storage
- c-security
- c-serialization
- c-server-sent-events
- c-shader-programming
- c-snapshot-system
- c-specific
- c-strictmode
- c-system-ui
- c-test-doubles
- c-test-sharding
- c-testing-pyramid
- c-testing-strategies
- c-theming
- c-to-folder
- c-token-management
- c-touch-input
- c-turbine-testing
- c-two-pointers
- c-ui-testing
- c-ui-ux-accessibility
- c-value-classes
- c-variable
- c-weak-references
- c-windowinsets
- c-xml
- q-abstract-class-vs-interface--kotlin--medium
- q-actor-pattern--kotlin--hard
created: 2025-10-15
updated: 2025-11-09
tags:
- data-classes
- difficulty/medium
- programming-languages
anki_cards:
- slug: q-data-class-requirements--kotlin--medium-0-en
  language: en
  anki_id: 1768326292381
  synced_at: '2026-01-23T17:03:51.552409'
- slug: q-data-class-requirements--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326292405
  synced_at: '2026-01-23T17:03:51.554894'
---
# Вопрос (RU)
> Какие требования при создании data class в Kotlin?

---

# Question (EN)
> What are the requirements when creating a data class in Kotlin?

## Ответ (RU)

**Требования к `data class`:**

1. **Первичный конструктор должен иметь хотя бы один параметр.**
2. **Параметры первичного конструктора, которые должны участвовать в auto-generated функциях и стать свойствами, должны быть помечены как `val` или `var`.** (остальные параметры допустимы, но не становятся свойствами и не попадают в сгенерированные методы)
3. **`data class` не может быть `abstract`, `open`, `sealed` или `inner`.**
4. **Может наследоваться от других классов и реализовывать интерфейсы** (с ограничениями, без нарушения запрета на `abstract/open/sealed/inner` для самого `data class`).
5. **Kotlin автоматически генерирует**: `equals()`, `hashCode()`, `toString()`, `copy()` и `componentN()` функции для каждого свойства в порядке объявления.

**Дополнительные правила:**
- Только свойства, объявленные в первичном конструкторе, участвуют в автоматически генерируемых функциях.
- Свойства, объявленные в теле класса, не включаются в `equals()`, `hashCode()`, `toString()` или компонентные функции.
- Можно иметь вторичные конструкторы, но они должны делегировать к первичному конструктору.
- Можно переопределять автоматически генерируемые функции вручную.

### Примеры Кода

**Валидный `data class`:**

```kotlin
// Минимальный валидный data class
data class Person(val name: String)

// Полный data class с несколькими свойствами
data class User(
    val id: Int,
    val name: String,
    var email: String,  // var разрешен
    val isActive: Boolean = true  // значения по умолчанию разрешены
)

fun main() {
    val user = User(1, "Alice", "alice@example.com")
    println(user)  // User(id=1, name=Alice, email=alice@example.com, isActive=true)

    // copy() работает
    val updated = user.copy(email = "newemail@example.com")
    println(updated)

    // Деструктуризация
    val (id, name, email, isActive) = user
    println("$name имеет ID $id")
}
```

**Невалидные примеры `data class`:**

```kotlin
// ОШИБКА: нет параметров в первичном конструкторе
// data class Empty()  // Ошибка компиляции

// ОШИБКА: параметры ожидаются как свойства, но не помечены val/var
// data class Invalid(name: String)  // Ошибка компиляции

// ОШИБКА: не может быть abstract
// abstract data class AbstractData(val value: Int)  // Ошибка компиляции

// ОШИБКА: не может быть open
// open data class OpenData(val value: Int)  // Ошибка компиляции

// ОШИБКА: не может быть sealed
// sealed data class SealedData(val value: Int)  // Ошибка компиляции

// ОШИБКА: не может быть inner
// class Outer {
//     inner data class InnerData(val value: Int)  // Ошибка компиляции
// }
```

**Свойства в теле vs в конструкторе:**

```kotlin
data class Product(
    val id: Int,
    val name: String,
    val price: Double
) {
    // Свойства в теле: НЕ входят в equals/hashCode/toString/copy/componentN
    var discount: Double = 0.0
    var quantity: Int = 0

    val finalPrice: Double
        get() = price - discount
}

fun main() {
    val product1 = Product(1, "Laptop", 999.99)
    product1.discount = 100.0
    product1.quantity = 5

    val product2 = Product(1, "Laptop", 999.99)
    product2.discount = 50.0
    product2.quantity = 3

    // equals() сравнивает только параметры конструктора
    println(product1 == product2)  // true

    // toString() включает только параметры конструктора
    println(product1)  // Product(id=1, name=Laptop, price=999.99)

    // copy() копирует только параметры конструктора
    val copy = product1.copy()
    println(copy.discount)   // 0.0
    println(copy.quantity)   // 0

    // componentN() только для параметров конструктора
    val (id, name, price) = product1
}
```

### Data Class И Наследование

```kotlin
// Базовый класс (должен быть open)
open class Entity(val id: Int, val createdAt: Long)

// Data class может наследоваться от open-класса
data class UserEntity(
    val userId: Int,
    val name: String,
    val email: String
) : Entity(userId, System.currentTimeMillis())

// Data class может реализовывать интерфейсы
interface Identifiable {
    val id: String
}

data class ProductEntity(
    override val id: String,
    val name: String,
    val price: Double
) : Identifiable

fun main() {
    val user = UserEntity(1, "Alice", "alice@example.com")
    println("User ID: ${user.id}")
    println("Created at: ${user.createdAt}")
    println(user)

    val product = ProductEntity("PROD-001", "Laptop", 999.99)
    println("Product: ${product.name}, ID: ${product.id}")
}
```

### Data Class С Вторичным Конструктором

```kotlin
data class Rectangle(
    val width: Double,
    val height: Double
) {
    // Вторичный конструктор обязан делегировать к первичному
    constructor(side: Double) : this(side, side)

    val area: Double
        get() = width * height
}

fun main() {
    val rectangle = Rectangle(10.0, 5.0)
    val square = Rectangle(5.0)

    println("Rectangle: ${rectangle.width} x ${rectangle.height}, Area: ${rectangle.area}")
    println("Square: ${square.width} x ${square.height}, Area: ${square.area}")
}
```

### Демонстрация Авто-сгенерированных Функций

```kotlin
data class Book(
    val isbn: String,
    val title: String,
    val author: String,
    val pages: Int
)

fun main() {
    val book = Book(
        isbn = "978-0-13-468599-1",
        title = "Effective Java",
        author = "Joshua Bloch",
        pages = 416
    )

    // 1. toString()
    println(book)

    // 2. equals() и hashCode() — сравнение по содержимому
    val sameBook = Book("978-0-13-468599-1", "Effective Java", "Joshua Bloch", 416)
    println(book == sameBook)
    println(book.hashCode() == sameBook.hashCode())

    // 3. copy() — создание измененных копий
    val updatedBook = book.copy(pages = 420)
    println(updatedBook)

    // 4. componentN() — деструктуризация
    val (isbn, title, author, pages) = book
    println("$title by $author has $pages pages")
}
```

### Переопределение Авто-сгенерированных Функций

```kotlin
data class Point(val x: Int, val y: Int) {
    // Кастомный toString()
    override fun toString(): String {
        return "Point($x, $y)"
    }

    // Кастомный equals() — сравниваем только x
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Point) return false
        return x == other.x
    }

    // При переопределении equals() нужно согласованно переопределить hashCode()
    override fun hashCode(): Int {
        return x
    }
}

fun main() {
    val p1 = Point(1, 2)
    val p2 = Point(1, 5)

    println(p1 == p2)
    println(p1.hashCode() == p2.hashCode())

    val p3 = p1.copy(y = 10)
    val (x, y) = p3
    println("x=$x, y=$y")
}
```

### Data Class В Коллекциях

```kotlin
data class Student(
    val id: Int,
    val name: String,
    val grade: Double
)

fun main() {
    val students = listOf(
        Student(1, "Alice", 95.5),
        Student(2, "Bob", 87.0),
        Student(3, "Charlie", 92.0),
        Student(1, "Alice", 95.5)  // дубликат
    )

    // Использование в Set (дубликаты убираются)
    val uniqueStudents = students.toSet()
    println("Unique students: ${uniqueStudents.size}")

    // Использование как ключи Map
    val studentMap = students.associateBy { it.id }
    println("Student 1: ${studentMap[1]?.name}")

    // Сортировка
    val sortedByGrade = students.sortedBy { it.grade }
    sortedByGrade.forEach { println("${it.name}: ${it.grade}") }
}
```

### Data Class С Валидацией

```kotlin
data class Email(val address: String) {
    init {
        require(address.contains("@")) {
            "Invalid email address: $address"
        }
        require(address.length >= 5) {
            "Email address too short"
        }
    }
}

data class Age(val years: Int) {
    init {
        require(years in 0..150) {
            "Age must be between 0 and 150, got $years"
        }
    }
}

fun main() {
    val email = Email("user@example.com")
    println(email)

    val age = Age(25)
    println(age)

    // Следующие примеры бросят IllegalArgumentException:
    // val badEmail = Email("invalid")
    // val badAge = Age(-5)
}
```

## Answer (EN)

**Data class requirements:**

1. **Primary constructor must have at least one parameter.**
2. **Primary constructor parameters that should become properties and take part in auto-generated methods must be marked with `val` or `var`.** (other parameters are allowed, but they do not become properties and are not included in generated methods)
3. **A `data class` cannot be `abstract`, `open`, `sealed`, or `inner`.**
4. **Can inherit from other classes and implement interfaces** (with restrictions, and without making the `data class` itself abstract/open/sealed/inner).
5. **Kotlin automatically generates**: `equals()`, `hashCode()`, `toString()`, `copy()`, and `componentN()` functions for each property in declaration order.

**Additional rules:**
- Only properties declared in the primary constructor participate in auto-generated functions.
- Properties declared in the class body are not included in `equals()`, `hashCode()`, `toString()`, or component functions.
- You can define secondary constructors, but they must delegate to the primary constructor.
- You can override auto-generated functions manually.

### Code Examples

**Valid data class:**

```kotlin
// Minimum valid data class
data class Person(val name: String)

// Full data class with multiple properties
data class User(
    val id: Int,
    val name: String,
    var email: String,  // var is allowed
    val isActive: Boolean = true  // default values allowed
)

fun main() {
    val user = User(1, "Alice", "alice@example.com")
    println(user)  // User(id=1, name=Alice, email=alice@example.com, isActive=true)

    // copy() works
    val updated = user.copy(email = "newemail@example.com")
    println(updated)

    // Destructuring works
    val (id, name, email, isActive) = user
    println("$name has ID $id")
}
```

**Invalid data class examples:**

```kotlin
// ERROR: No parameters in primary constructor
// data class Empty()  // Compilation error

// ERROR: Parameters that are meant to be properties but are not marked as val or var
// data class Invalid(name: String)  // Compilation error

// ERROR: Cannot be abstract
// abstract data class AbstractData(val value: Int)  // Compilation error

// ERROR: Cannot be open
// open data class OpenData(val value: Int)  // Compilation error

// ERROR: Cannot be sealed
// sealed data class SealedData(val value: Int)  // Compilation error

// ERROR: Cannot be inner
// class Outer {
//     inner data class InnerData(val value: Int)  // Compilation error
// }
```

**Properties in body vs constructor:**

```kotlin
data class Product(
    val id: Int,
    val name: String,
    val price: Double
) {
    // Property in body - NOT included in equals, hashCode, toString, copy, componentN
    var discount: Double = 0.0
    var quantity: Int = 0

    // Computed property - also not included
    val finalPrice: Double
        get() = price - discount
}

fun main() {
    val product1 = Product(1, "Laptop", 999.99)
    product1.discount = 100.0
    product1.quantity = 5

    val product2 = Product(1, "Laptop", 999.99)
    product2.discount = 50.0  // Different discount
    product2.quantity = 3     // Different quantity

    // equals() only compares constructor parameters
    println(product1 == product2)  // true! (discount and quantity not compared)

    // toString() only includes constructor parameters
    println(product1)  // Product(id=1, name=Laptop, price=999.99)

    // copy() only copies constructor parameters
    val copy = product1.copy()
    println(copy.discount)   // 0.0 (not copied)
    println(copy.quantity)   // 0 (not copied)

    // componentN() only for constructor parameters
    val (id, name, price) = product1
    // Cannot destructure discount or quantity
}
```

**Data class with inheritance:**

```kotlin
// Base class (must be open)
open class Entity(val id: Int, val createdAt: Long)

// Data class can inherit from open class
data class UserEntity(
    val userId: Int,
    val name: String,
    val email: String
) : Entity(userId, System.currentTimeMillis())

// Data class can implement interfaces
interface Identifiable {
    val id: String
}

data class ProductEntity(
    override val id: String,
    val name: String,
    val price: Double
) : Identifiable

fun main() {
    val user = UserEntity(1, "Alice", "alice@example.com")
    println("User ID: ${user.id}")
    println("Created at: ${user.createdAt}")
    println(user)

    val product = ProductEntity("PROD-001", "Laptop", 999.99)
    println("Product: ${product.name}, ID: ${product.id}")
}
```

**Data class with secondary constructor:**

```kotlin
data class Rectangle(
    val width: Double,
    val height: Double
) {
    // Secondary constructor - must delegate to primary
    constructor(side: Double) : this(side, side)

    val area: Double
        get() = width * height
}

fun main() {
    val rectangle = Rectangle(10.0, 5.0)
    val square = Rectangle(5.0)  // Uses secondary constructor

    println("Rectangle: ${rectangle.width} x ${rectangle.height}, Area: ${rectangle.area}")
    println("Square: ${square.width} x ${square.height}, Area: ${square.area}")
}
```

**Auto-generated functions demonstration:**

```kotlin
data class Book(
    val isbn: String,
    val title: String,
    val author: String,
    val pages: Int
)

fun main() {
    val book = Book(
        isbn = "978-0-13-468599-1",
        title = "Effective Java",
        author = "Joshua Bloch",
        pages = 416
    )

    // 1. toString() - automatically generated
    println(book)

    // 2. equals() and hashCode() - content-based equality
    val sameBook = Book("978-0-13-468599-1", "Effective Java", "Joshua Bloch", 416)
    println(book == sameBook)  // true
    println(book.hashCode() == sameBook.hashCode())  // true

    // 3. copy() - create modified copies
    val updatedBook = book.copy(pages = 420)
    println(updatedBook)

    // 4. componentN() - destructuring
    val (isbn, title, author, pages) = book
    println("$title by $author has $pages pages")
}
```

**Overriding auto-generated functions:**

```kotlin
data class Point(val x: Int, val y: Int) {
    // Custom toString()
    override fun toString(): String {
        return "Point($x, $y)"
    }

    // Custom equals() - only compare x
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Point) return false
        return x == other.x
    }

    // Must override hashCode() when overriding equals()
    override fun hashCode(): Int {
        return x
    }
}

fun main() {
    val p1 = Point(1, 2)
    val p2 = Point(1, 5)  // Different y

    println(p1 == p2)  // true (only x is compared)
    println(p1.hashCode() == p2.hashCode())  // true

    // copy() and componentN() still work
    val p3 = p1.copy(y = 10)
    val (x, y) = p3
    println("x=$x, y=$y")
}
```

**Data class in collections:**

```kotlin
data class Student(
    val id: Int,
    val name: String,
    val grade: Double
)

fun main() {
    val students = listOf(
        Student(1, "Alice", 95.5),
        Student(2, "Bob", 87.0),
        Student(3, "Charlie", 92.0),
        Student(1, "Alice", 95.5)  // Duplicate
    )

    // Works in Set (duplicates removed)
    val uniqueStudents = students.toSet()
    println("Unique students: ${uniqueStudents.size}")  // 3

    // Works as Map keys
    val studentMap = students.associateBy { it.id }
    println("Student 1: ${studentMap[1]?.name}")  // Alice

    // Sorting works with data classes
    val sortedByGrade = students.sortedBy { it.grade }
    sortedByGrade.forEach { println("${it.name}: ${it.grade}") }
}
```

**Data class with validation:**

```kotlin
data class Email(val address: String) {
    init {
        require(address.contains("@")) {
            "Invalid email address: $address"
        }
        require(address.length >= 5) {
            "Email address too short"
        }
    }
}

data class Age(val years: Int) {
    init {
        require(years in 0..150) {
            "Age must be between 0 and 150, got $years"
        }
    }
}

fun main() {
    val email = Email("user@example.com")
    println(email)

    val age = Age(25)
    println(age)

    // These would throw exceptions:
    // val badEmail = Email("invalid")  // IllegalArgumentException
    // val badAge = Age(-5)  // IllegalArgumentException
}
```

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия `data class` в Kotlin от аналогичных возможностей в Java?
- Когда на практике стоит использовать `data class`?
- Какие распространенные ошибки и подводные камни при использовании `data class`?

## Follow-ups

- What are the key differences between Kotlin `data class` and Java approaches?
- When would you use a `data class` in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-actor-pattern--kotlin--hard]]
- [[q-abstract-class-vs-interface--kotlin--medium]]

## Related Questions

- [[q-actor-pattern--kotlin--hard]]
- [[q-abstract-class-vs-interface--kotlin--medium]]
