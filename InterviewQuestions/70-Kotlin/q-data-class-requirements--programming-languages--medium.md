---
tags:
  - programming-languages
difficulty: medium
status: reviewed
---

# What are the requirements when creating a data class?

**English**: What are the requirements when creating a data class in Kotlin?

## Answer

**Data class requirements:**

1. **Primary constructor must have at least one parameter**
2. **All primary constructor parameters must be marked as `val` or `var`** to become properties
3. **Cannot be abstract, open, sealed, or inner**
4. **Can inherit from other classes and implement interfaces** (with restrictions)
5. **Kotlin automatically generates**: `equals()`, `hashCode()`, `toString()`, `copy()`, and `componentN()` functions for each property in declaration order

**Additional rules:**
- Only properties declared in the primary constructor participate in auto-generated functions
- Properties declared in the class body are not included in `equals()`, `hashCode()`, `toString()`, or component functions
- Can have secondary constructors, but they must delegate to the primary constructor
- Can override auto-generated functions manually

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
// ❌ ERROR: No parameters in primary constructor
// data class Empty()  // Compilation error

// ❌ ERROR: Parameter not marked as val or var
// data class Invalid(name: String)  // Compilation error

// ❌ ERROR: Cannot be abstract
// abstract data class AbstractData(val value: Int)  // Compilation error

// ❌ ERROR: Cannot be open
// open data class OpenData(val value: Int)  // Compilation error

// ❌ ERROR: Cannot be sealed
// sealed data class SealedData(val value: Int)  // Compilation error

// ❌ ERROR: Cannot be inner
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
data class User(
    val userId: Int,
    val name: String,
    val email: String
) : Entity(userId, System.currentTimeMillis())

// Data class can implement interfaces
interface Identifiable {
    val id: String
}

data class Product(
    override val id: String,
    val name: String,
    val price: Double
) : Identifiable

fun main() {
    val user = User(1, "Alice", "alice@example.com")
    println("User ID: ${user.id}")
    println("Created at: ${user.createdAt}")
    println(user)

    val product = Product("PROD-001", "Laptop", 999.99)
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
    // Book(isbn=978-0-13-468599-1, title=Effective Java, author=Joshua Bloch, pages=416)

    // 2. equals() and hashCode() - content-based equality
    val sameBook = Book("978-0-13-468599-1", "Effective Java", "Joshua Bloch", 416)
    println(book == sameBook)  // true
    println(book.hashCode() == sameBook.hashCode())  // true

    // 3. copy() - create modified copies
    val updatedBook = book.copy(pages = 420)
    println(updatedBook)
    // Book(isbn=978-0-13-468599-1, title=Effective Java, author=Joshua Bloch, pages=420)

    // 4. componentN() - destructuring
    val (isbn, title, author, pages) = book
    println("$title by $author has $pages pages")
    // Effective Java by Joshua Bloch has 416 pages
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

## Ответ

### Вопрос
Какие есть требования при создании data class ?

### Ответ
Data class должен иметь хотя бы один параметр в первичном конструкторе. Параметры первичного конструктора должны быть помечены как val или var чтобы они становились свойствами класса. Kotlin автоматически генерирует equals hashCode toString copy и componentN функции для каждого свойства в порядке их объявления. Data class не может быть abstract open sealed или inner
