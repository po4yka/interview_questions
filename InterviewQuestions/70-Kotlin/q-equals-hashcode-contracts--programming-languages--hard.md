---
tags:
  - programming-languages
difficulty: hard
status: reviewed
---

# Tell about equals and hashCode contracts

**English**: Tell about equals and hashCode contracts in Kotlin.

## Answer

The `equals()` and `hashCode()` methods are used for object comparison and their correct operation in collections (Set, Map).

**equals() contract:**
1. **Reflexive**: `a.equals(a)` → true (object equals itself)
2. **Symmetric**: `a.equals(b) == b.equals(a)`
3. **Transitive**: if `a == b` and `b == c`, then `a == c`
4. **Consistent**: if `a == b`, then `a.equals(b)` always returns the same result as long as the object doesn't change
5. **Comparison with null**: `a.equals(null) == false`

**hashCode() contract:**
1. **Consistency with equals()**: if `a == b`, then `a.hashCode() == b.hashCode()`
2. **Reverse not required**: Two different objects can have the same hashCode() (hash collision)
3. **Consistency**: Hash code should not change if the object hasn't changed

**In Kotlin, you can use `data class` for automatic generation of `equals()`, `hashCode()`, as well as `copy()` and `toString()`.**

### Code Examples

**equals() contract violations and fixes:**

```kotlin
// BAD: Violates symmetry
class BadPerson(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (other is BadPerson) {
            return name == other.name
        }
        // Violates symmetry with String!
        if (other is String) {
            return name == other
        }
        return false
    }

    override fun hashCode() = name.hashCode()
}

// GOOD: Proper equals implementation
class GoodPerson(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true  // Reflexive
        if (other !is GoodPerson) return false  // Type check
        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }
}

fun main() {
    // Bad example
    val bad1 = BadPerson("Alice", 30)
    val bad2 = "Alice"

    // Symmetric violation
    // println(bad1 == bad2)  // true
    // println(bad2 == bad1)  // false (symmetry violated!)

    // Good example
    val good1 = GoodPerson("Alice", 30)
    val good2 = GoodPerson("Alice", 30)
    val good3 = GoodPerson("Alice", 31)

    println(good1 == good2)  // true
    println(good2 == good1)  // true (symmetric)
    println(good1 == good3)  // false (different age)
}
```

**hashCode() contract:**

```kotlin
class Person(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Person) return false
        return name == other.name && age == other.age
    }

    // CORRECT: hashCode consistent with equals
    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }
}

class BrokenPerson(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is BrokenPerson) return false
        return name == other.name && age == other.age
    }

    // WRONG: hashCode NOT consistent with equals
    override fun hashCode(): Int {
        return name.hashCode()  // Doesn't include age!
    }
}

fun main() {
    // Correct implementation
    val p1 = Person("Alice", 30)
    val p2 = Person("Alice", 30)

    println("equals: ${p1 == p2}")  // true
    println("hashCode equal: ${p1.hashCode() == p2.hashCode()}")  // true

    val set = hashSetOf(p1, p2)
    println("Set size (correct): ${set.size}")  // 1 (works correctly)

    // Broken implementation
    val b1 = BrokenPerson("Alice", 30)
    val b2 = BrokenPerson("Alice", 31)

    println("\nequals: ${b1 == b2}")  // false
    println("hashCode equal: ${b1.hashCode() == b2.hashCode()}")  // true (PROBLEM!)

    // HashSet may malfunction
    val brokenSet = hashSetOf(b1)
    println("Contains b1: ${brokenSet.contains(b1)}")  // true
    println("Contains b2: ${brokenSet.contains(b2)}")  // May be true or false!
}
```

**All equals() properties:**

```kotlin
data class Point(val x: Int, val y: Int)

fun main() {
    val a = Point(1, 2)
    val b = Point(1, 2)
    val c = Point(1, 2)

    // 1. Reflexive
    println("Reflexive: ${a == a}")  // true

    // 2. Symmetric
    println("Symmetric: a == b: ${a == b}, b == a: ${b == a}")  // both true

    // 3. Transitive
    println("Transitive: a == b: ${a == b}, b == c: ${b == c}, a == c: ${a == c}")
    // all true

    // 4. Consistent
    repeat(5) {
        println("Consistent check $it: ${a == b}")  // always true
    }

    // 5. Null comparison
    println("Null comparison: ${a == null}")  // false
}
```

**Using in hash-based collections:**

```kotlin
data class Student(val id: Int, val name: String, val grade: Double)

fun main() {
    val student1 = Student(1, "Alice", 95.5)
    val student2 = Student(1, "Alice", 95.5)
    val student3 = Student(2, "Bob", 87.0)

    // HashSet - removes duplicates based on equals/hashCode
    val set = hashSetOf(student1, student2, student3)
    println("Set size: ${set.size}")  // 2 (student1 and student2 are equal)

    // HashMap - uses hashCode for buckets, equals for comparison
    val map = hashMapOf(
        student1 to "Grade A",
        student3 to "Grade B"
    )

    println("Grade for student2: ${map[student2]}")  // "Grade A" (found via equals)

    // Contains check
    println("Set contains student2: ${set.contains(student2)}")  // true
}
```

**Manual implementation template:**

```kotlin
class Book(
    val isbn: String,
    val title: String,
    val author: String,
    val pages: Int
) {
    override fun equals(other: Any?): Boolean {
        // 1. Reference equality
        if (this === other) return true

        // 2. Type check and smart cast
        if (other !is Book) return false

        // 3. Property comparison
        if (isbn != other.isbn) return false
        if (title != other.title) return false
        if (author != other.author) return false
        if (pages != other.pages) return false

        return true
    }

    override fun hashCode(): Int {
        // Use all properties that are in equals()
        var result = isbn.hashCode()
        result = 31 * result + title.hashCode()
        result = 31 * result + author.hashCode()
        result = 31 * result + pages
        return result
    }

    override fun toString(): String {
        return "Book(isbn='$isbn', title='$title', author='$author', pages=$pages)"
    }
}

fun main() {
    val book1 = Book("978-0-13-468599-1", "Effective Java", "Joshua Bloch", 416)
    val book2 = Book("978-0-13-468599-1", "Effective Java", "Joshua Bloch", 416)

    println(book1 == book2)  // true
    println(book1.hashCode() == book2.hashCode())  // true
}
```

**data class automatic implementation:**

```kotlin
data class Product(
    val id: Int,
    val name: String,
    val price: Double
)

fun main() {
    val p1 = Product(1, "Laptop", 999.99)
    val p2 = Product(1, "Laptop", 999.99)
    val p3 = Product(2, "Mouse", 29.99)

    // Automatically correct equals/hashCode
    println("p1 == p2: ${p1 == p2}")  // true
    println("p1.hashCode() == p2.hashCode(): ${p1.hashCode() == p2.hashCode()}")  // true

    // Works in collections
    val products = hashSetOf(p1, p2, p3)
    println("Unique products: ${products.size}")  // 2

    val inventory = hashMapOf(
        p1 to 10,
        p3 to 50
    )
    println("Laptop stock: ${inventory[p2]}")  // 10 (found via equals)
}
```

**Common mistakes:**

```kotlin
// MISTAKE 1: Overriding equals without hashCode
class Mistake1(val value: Int) {
    override fun equals(other: Any?): Boolean {
        if (other !is Mistake1) return false
        return value == other.value
    }
    // Missing hashCode()!
}

// MISTAKE 2: Using mutable properties
class Mistake2(var value: Int) {
    override fun equals(other: Any?) = (other as? Mistake2)?.value == value
    override fun hashCode() = value
}

// MISTAKE 3: Inconsistent equals/hashCode
class Mistake3(val a: Int, val b: Int) {
    override fun equals(other: Any?) =
        (other as? Mistake3)?.let { a == it.a && b == it.b } ?: false

    override fun hashCode() = a  // Only uses 'a', not 'b'!
}

fun demonstrateMistakes() {
    // Mistake 1: HashMap won't work correctly
    val m1a = Mistake1(5)
    val m1b = Mistake1(5)
    val map1 = hashMapOf(m1a to "value")
    println("Found via equals key: ${map1[m1b]}")  // null! (should be "value")

    // Mistake 2: Changing value breaks contract
    val m2 = Mistake2(10)
    val set2 = hashSetOf(m2)
    m2.value = 20  // Changed after adding to set!
    println("Set contains m2: ${set2.contains(m2)}")  // false! (broken)

    // Mistake 3: Equal objects with different hash codes
    val m3a = Mistake3(1, 2)
    val m3b = Mistake3(1, 3)
    println("Equal: ${m3a == m3b}")  // false
    println("Same hash: ${m3a.hashCode() == m3b.hashCode()}")  // true (violation!)
}
```

---

## Ответ

### Вопрос
Расскажи о контрактах equals и hashCode

### Ответ
Методы equals() и hashCode() используются для сравнения объектов и их корректной работы в коллекциях (Set, Map). Контракт `equals()` должен: Рефлексивность: a.equals(a) → true (объект равен самому себе). Симметричность: a.equals(b) == b.equals(a). Транзитивность: если a == b и b == c, то a == c. Согласованность: если a == b, то a.equals(b) всегда возвращает одно и же, пока объект не изменится. Сравнение с null всегда даёт false: a.equals(null) == false.", "Контракт `hashCode()` должен: Согласованность с equals(): если a == b, то a.hashCode() == b.hashCode(). Но обратное не обязательно: два разных объекта могут иметь одинаковый hashCode(). Хеш-код не должен меняться, если объект не изменился. В Kotlin можно использовать data class для автоматической генерации equals(), hashCode(), а также copy() и toString().
