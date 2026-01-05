---
id: kotlin-161
title: "Equals Hashcode Contracts / Контракты equals и hashCode"
aliases: [Equals Hashcode Contracts, Контракты equals hashCode]
topic: kotlin
subtopics: [language-features]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-equality, c-hash-map, c-kotlin]
created: 2025-10-09
updated: 2025-11-09
tags: [contracts, difficulty/hard, equals, hashcode, programming-languages]
---
# Вопрос (RU)
> Расскажите о контрактах equals() и hashCode() в Kotlin. Каковы их требования и как они работают вместе?

# Question (EN)
> Tell about equals() and hashCode() contracts in Kotlin. What are their requirements and how do they work together?

## Ответ (RU)

Методы `equals()` и `hashCode()` используются для сравнения объектов и их корректной работы в коллекциях (`Set`, `Map`). В Kotlin оператор `==` вызывает `equals()` (безопасно для null), а оператор `===` проверяет ссылочное равенство.

**Контракт equals():**
1. **Рефлексивность**: `a.equals(a)` → true (объект равен самому себе)
2. **Симметричность**: `a.equals(b)` и `b.equals(a)` всегда дают одинаковый результат
3. **Транзитивность**: если `a == b` и `b == c`, то `a == c`
4. **Согласованность**: повторные вызовы `a.equals(b)` возвращают один и тот же результат, пока значения, участвующие в сравнении, не изменились
5. **Сравнение с null**: `a.equals(null) == false`

**Контракт hashCode():**
1. **Согласованность с equals()**: если `a == b`, то `a.hashCode() == b.hashCode()`
2. **Обратное не требуется**: два разных объекта (и/или не равных по equals) могут иметь одинаковый `hashCode()` (коллизия)
3. **Согласованность**: хеш-код не должен меняться, если значения, участвующие в equals/hashCode, не изменились

**В Kotlin можно использовать `data class` для автоматической генерации `equals()`, `hashCode()`, а также `copy()` и `toString()`. См. также [[c-kotlin]] и [[c-equality]].**

### Примеры Кода

**Нарушения контракта equals() и исправления:**

```kotlin
// ПЛОХО: Нарушает симметричность
class BadPerson(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (other is BadPerson) {
            return name == other.name
        }
        // Нарушает симметричность со String!
        if (other is String) {
            return name == other
        }
        return false
    }

    override fun hashCode() = name.hashCode()
}

// ХОРОШО: Правильная реализация equals/hashCode
class GoodPerson(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true  // Рефлексивность (и быстрая проверка ссылок)
        if (other !is GoodPerson) return false  // Проверка типа
        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }
}

fun main() {
    // Плохой пример
    val bad1 = BadPerson("Alice", 30)
    val bad2 = "Alice"

    // Нарушение симметричности
    // println(bad1 == bad2)  // true
    // println(bad2 == bad1)  // false (симметричность нарушена!)

    // Хороший пример
    val good1 = GoodPerson("Alice", 30)
    val good2 = GoodPerson("Alice", 30)
    val good3 = GoodPerson("Alice", 31)

    println(good1 == good2)  // true
    println(good2 == good1)  // true (симметричность)
    println(good1 == good3)  // false (разный возраст)
}
```

**Контракт hashCode():**

```kotlin
class Person(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Person) return false
        return name == other.name && age == other.age
    }

    // ПРАВИЛЬНО: hashCode согласован с equals
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

    // ПРОБЛЕМА: hashCode не использует все поля, участвующие в equals
    // Это не нарушает формальный контракт напрямую (равные объекты все ещё имеют одинаковый hashCode),
    // но ухудшает распределение в хеш-структурах и может приводить к деградации производительности.
    override fun hashCode(): Int {
        return name.hashCode()  // Не включает age
    }
}

fun main() {
    // Правильная реализация
    val p1 = Person("Alice", 30)
    val p2 = Person("Alice", 30)

    println("equals: ${p1 == p2}")  // true
    println("hashCode равны: ${p1.hashCode() == p2.hashCode()}")  // true

    val set = hashSetOf(p1, p2)
    println("Размер Set (правильно): ${set.size}")  // 1 (работает корректно)

    // Реализация с плохим hashCode (но без нарушения формального контракта)
    val b1 = BrokenPerson("Alice", 30)
    val b2 = BrokenPerson("Alice", 31)

    println("\nequals: ${b1 == b2}")  // false
    println("hashCode равны: ${b1.hashCode() == b2.hashCode()}")  // true (коллизия, допустимо)

    val brokenSet = hashSetOf(b1)
    println("Содержит b1: ${brokenSet.contains(b1)}")  // true
    println("Содержит b2: ${brokenSet.contains(b2)}")  // false (ожидаемо: объекты не равны)
}
```

**Все свойства equals():**

```kotlin
data class Point(val x: Int, val y: Int)

fun main() {
    val a = Point(1, 2)
    val b = Point(1, 2)
    val c = Point(1, 2)

    // 1. Рефлексивность
    println("Рефлексивность: ${a == a}")  // true

    // 2. Симметричность
    println("Симметричность: a == b: ${a == b}, b == a: ${b == a}")  // оба true

    // 3. Транзитивность
    println("Транзитивность: a == b: ${a == b}, b == c: ${b == c}, a == c: ${a == c}")
    // все true

    // 4. Согласованность
    repeat(5) {
        println("Проверка согласованности $it: ${a == b}")  // всегда true
    }

    // 5. Сравнение с null
    println("Сравнение с null: ${a == null}")  // false
}
```

**Использование в хеш-коллекциях:**

```kotlin
data class Student(val id: Int, val name: String, val grade: Double)

fun main() {
    val student1 = Student(1, "Alice", 95.5)
    val student2 = Student(1, "Alice", 95.5)
    val student3 = Student(2, "Bob", 87.0)

    // HashSet - удаляет дубликаты на основе equals/hashCode
    val set = hashSetOf(student1, student2, student3)
    println("Размер Set: ${set.size}")  // 2 (student1 и student2 равны)

    // HashMap - использует hashCode для корзин, equals для сравнения
    val map = hashMapOf(
        student1 to "Оценка A",
        student3 to "Оценка B"
    )

    println("Оценка для student2: ${map[student2]}")  // "Оценка A" (найдено через equals)

    // Проверка contains
    println("Set содержит student2: ${set.contains(student2)}")  // true
}
```

**Шаблон ручной реализации:**

```kotlin
class Book(
    val isbn: String,
    val title: String,
    val author: String,
    val pages: Int
) {
    override fun equals(other: Any?): Boolean {
        // 1. Проверка равенства ссылок
        if (this === other) return true

        // 2. Проверка типа и smart cast
        if (other !is Book) return false

        // 3. Сравнение свойств
        if (isbn != other.isbn) return false
        if (title != other.title) return false
        if (author != other.author) return false
        if (pages != other.pages) return false

        return true
    }

    override fun hashCode(): Int {
        // Используем все свойства, которые есть в equals()
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

**Автоматическая реализация data class:**

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

    // Автоматически правильные equals/hashCode
    println("p1 == p2: ${p1 == p2}")  // true
    println("p1.hashCode() == p2.hashCode(): ${p1.hashCode() == p2.hashCode()}")  // true

    // Работает в коллекциях
    val products = hashSetOf(p1, p2, p3)
    println("Уникальных продуктов: ${products.size}")  // 2

    val inventory = hashMapOf(
        p1 to 10,
        p3 to 50
    )
    println("Запас ноутбуков: ${inventory[p2]}")  // 10 (найдено через equals)
}
```

**Распространенные ошибки:**

```kotlin
// ОШИБКА 1: Переопределение equals без hashCode
class Mistake1(val value: Int) {
    override fun equals(other: Any?): Boolean {
        if (other !is Mistake1) return false
        return value == other.value
    }
    // Отсутствует hashCode()!
}

// ОШИБКА 2: Использование изменяемых свойств в equals/hashCode
class Mistake2(var value: Int) {
    override fun equals(other: Any?) = (other as? Mistake2)?.value == value
    override fun hashCode() = value
}

// ОШИБКА 3: Несогласованные equals/hashCode
class Mistake3(val a: Int, val b: Int) {
    override fun equals(other: Any?) =
        (other as? Mistake3)?.let { a == it.a && b == it.b } ?: false

    // Нарушение контракта: hashCode не учитывает b, хотя он участвует в equals
    override fun hashCode() = a
}

fun demonstrateMistakes() {
    // Ошибка 1: HashMap не будет работать корректно для поиска по "равному" ключу
    val m1a = Mistake1(5)
    val m1b = Mistake1(5)
    val map1 = hashMapOf(m1a to "value")
    println("Найдено по equals ключу: ${map1[m1b]}")  // null (контракт нарушен)

    // Ошибка 2: Изменение значения нарушает контракт после помещения в Set/Map
    val m2 = Mistake2(10)
    val set2 = hashSetOf(m2)
    m2.value = 20  // Изменено после добавления в set!
    println("Set содержит m2: ${set2.contains(m2)}")  // Может быть false (сломано)

    // Ошибка 3: Равные объекты могут иметь разные hashCode, что нарушает контракт
    val m3a = Mistake3(1, 2)
    val m3b = Mistake3(1, 2)
    println("Равны: ${m3a == m3b}")  // true
    println("Одинаковый хеш: ${m3a.hashCode() == m3b.hashCode()}")  // может быть false (нарушение контракта)
}
```

---

## Answer (EN)

The `equals()` and `hashCode()` methods are used for object comparison and correct behavior in collections (`Set`, `Map`). In Kotlin, the `==` operator calls `equals()` (null-safe), while `===` checks referential equality.

**equals() contract:**
1. **Reflexive**: `a.equals(a)` → true (object equals itself)
2. **Symmetric**: `a.equals(b)` and `b.equals(a)` must always return the same result
3. **Transitive**: if `a == b` and `b == c`, then `a == c`
4. **Consistent**: repeated calls to `a.equals(b)` must return the same result as long as the values used in comparison do not change
5. **Null comparison**: `a.equals(null) == false`

**hashCode() contract:**
1. **Consistency with equals()**: if `a == b`, then `a.hashCode() == b.hashCode()`
2. **No reverse requirement**: two different / non-equal objects may have the same `hashCode()` (collision)
3. **Consistency**: hash code should not change as long as the values used in equals/hashCode remain unchanged

**In Kotlin, you can use `data class` for automatic generation of `equals()`, `hashCode()`, along with `copy()` and `toString()`. See also [[c-kotlin]] and [[c-equality]].**

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

// GOOD: Proper equals/hashCode implementation
class GoodPerson(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true  // Reflexive / fast path
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

    // PROBLEM: hashCode does not use all properties used in equals.
    // This does not break the formal contract directly (equal objects still share the same hashCode),
    // but leads to poor distribution and potential performance degradation.
    override fun hashCode(): Int {
        return name.hashCode()  // Doesn't include age
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

    // Implementation with poor hashCode (but no formal contract violation)
    val b1 = BrokenPerson("Alice", 30)
    val b2 = BrokenPerson("Alice", 31)

    println("\nequals: ${b1 == b2}")  // false
    println("hashCode equal: ${b1.hashCode() == b2.hashCode()}")  // true (collision, allowed)

    val brokenSet = hashSetOf(b1)
    println("Contains b1: ${brokenSet.contains(b1)}")  // true
    println("Contains b2: ${brokenSet.contains(b2)}")  // false (expected: objects are not equal)
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

// MISTAKE 2: Using mutable properties in equals/hashCode
class Mistake2(var value: Int) {
    override fun equals(other: Any?) = (other as? Mistake2)?.value == value
    override fun hashCode() = value
}

// MISTAKE 3: Inconsistent equals/hashCode
class Mistake3(val a: Int, val b: Int) {
    override fun equals(other: Any?) =
        (other as? Mistake3)?.let { a == it.a && b == it.b } ?: false

    // Violates the contract: hashCode ignores b, which participates in equals
    override fun hashCode() = a
}

fun demonstrateMistakes() {
    // Mistake 1: HashMap lookup by an "equal" key won't work correctly
    val m1a = Mistake1(5)
    val m1b = Mistake1(5)
    val map1 = hashMapOf(m1a to "value")
    println("Found via equals key: ${map1[m1b]}")  // null (contract violated)

    // Mistake 2: Changing value after insertion breaks the contract
    val m2 = Mistake2(10)
    val set2 = hashSetOf(m2)
    m2.value = 20  // Changed after adding to set!
    println("Set contains m2: ${set2.contains(m2)}")  // May be false (broken)

    // Mistake 3: Equal objects may produce different hashCodes, violating the contract
    val m3a = Mistake3(1, 2)
    val m3b = Mistake3(1, 2)
    println("Equal: ${m3a == m3b}")  // true
    println("Same hash: ${m3a.hashCode() == m3b.hashCode()}")  // may be false (violation)
}
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-destructuring-declarations--kotlin--medium]]
- [[q-kotlin-inline-functions--kotlin--medium]]
- [[q-coroutine-exception-handler--kotlin--medium]]
