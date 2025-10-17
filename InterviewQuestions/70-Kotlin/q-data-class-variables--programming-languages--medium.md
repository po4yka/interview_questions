---
id: 20251012-154351
title: "Data Class Variables / Переменные data class"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags: - programming-languages
---
# What variables can be used in data class?

# Question (EN)
> What variables can be used in a data class in Kotlin?

# Вопрос (RU)
> Какие переменные можно использовать в data class в Kotlin?

---

## Answer (EN)

In a data class, you can only use properties declared in the primary constructor with `val` or `var`. These properties automatically participate in `equals()`, `hashCode()`, `toString()`, `copy()`, and `componentN()` functions. Other properties (declared in the class body) are not considered part of the class data.

**Key rules:**
- Primary constructor parameters must be marked as `val` or `var`
- Only primary constructor properties are used in auto-generated methods
- Properties in class body are excluded from `equals()`, `hashCode()`, `toString()`, `copy()`
- At least one primary constructor parameter is required

### Code Examples

**Basic data class:**

```kotlin
data class User(
    val id: Int,           // Included in all methods
    val name: String,      // Included in all methods
    var email: String,     // Included in all methods (var is allowed)
    val age: Int = 0       // Included (default values allowed)
)

fun main() {
    val user = User(1, "Alice", "alice@example.com", 30)

    // toString includes all primary constructor properties
    println(user)
    // User(id=1, name=Alice, email=alice@example.com, age=30)

    // Destructuring uses componentN() for primary constructor properties
    val (id, name, email, age) = user
    println("$name ($id): $email, age $age")

    // copy() works with primary constructor properties
    val updated = user.copy(email = "newemail@example.com")
    println(updated)
}
```

**Properties in class body (excluded from data methods):**

```kotlin
data class Product(
    val id: Int,
    val name: String,
    val price: Double
) {
    // Properties in body - NOT included in equals, hashCode, toString, copy
    var discount: Double = 0.0
    var quantity: Int = 0
    var lastUpdated: Long = System.currentTimeMillis()

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

    // equals() only compares primary constructor properties
    println("product1 == product2: ${product1 == product2}")  // true!

    // toString() only includes primary constructor properties
    println(product1)
    // Product(id=1, name=Laptop, price=999.99)
    // Note: discount, quantity not shown!

    // copy() only copies primary constructor properties
    val copy = product1.copy()
    println("Copy discount: ${copy.discount}")   // 0.0 (not copied!)
    println("Copy quantity: ${copy.quantity}")   // 0 (not copied!)

    // componentN() only for primary constructor
    val (id, name, price) = product1
    // Cannot destructure discount or quantity
    println("Destructured: id=$id, name=$name, price=$price")
}
```

**val vs var in data class:**

```kotlin
data class Person(
    val id: Int,          // Immutable - cannot change
    var name: String,     // Mutable - can change
    var age: Int          // Mutable - can change
)

fun main() {
    val person = Person(1, "Alice", 30)

    // Can modify var properties
    person.name = "Alice Smith"
    person.age = 31

    // Cannot modify val property
    // person.id = 2  // ERROR: Val cannot be reassigned

    println(person)
    // Person(id=1, name=Alice Smith, age=31)
}
```

**Demonstration of equals() behavior:**

```kotlin
data class Book(
    val isbn: String,
    val title: String
) {
    var pages: Int = 0
    var publisher: String = ""
}

fun main() {
    val book1 = Book("978-0-13-468599-1", "Effective Java")
    book1.pages = 416
    book1.publisher = "Addison-Wesley"

    val book2 = Book("978-0-13-468599-1", "Effective Java")
    book2.pages = 500  // Different!
    book2.publisher = "Different Publisher"  // Different!

    // Still equal because only ISBN and title are compared
    println("Books equal: ${book1 == book2}")  // true

    // HashCode also ignores class body properties
    val set = setOf(book1, book2)
    println("Set size: ${set.size}")  // 1 (treated as duplicates)

    // HashMap uses hashCode + equals
    val map = mapOf(book1 to "First edition")
    println("Find with book2: ${map[book2]}")  // "First edition"
}
```

**Why this matters - tracking changes:**

```kotlin
data class Entity(
    val id: Int,
    val data: String
) {
    var version: Int = 0
    var modifiedAt: Long = 0

    fun update(newData: String): Entity {
        val updated = this.copy(data = newData)
        updated.version = this.version + 1
        updated.modifiedAt = System.currentTimeMillis()
        return updated
    }
}

fun main() {
    val entity1 = Entity(1, "Original data")
    entity1.version = 1
    entity1.modifiedAt = System.currentTimeMillis()

    Thread.sleep(100)

    val entity2 = entity1.update("Updated data")

    println("Entity 1: $entity1, version=${entity1.version}")
    println("Entity 2: $entity2, version=${entity2.version}")

    // Different versions but copy() didn't preserve it
    println("entity2 version: ${entity2.version}")  // 2
    println("entity2 modifiedAt: ${entity2.modifiedAt}")  // Updated time
}
```

**Correct approach - all data in constructor:**

```kotlin
data class BetterProduct(
    val id: Int,
    val name: String,
    val price: Double,
    val discount: Double = 0.0,    // In constructor
    val quantity: Int = 0,         // In constructor
    val lastUpdated: Long = System.currentTimeMillis()
) {
    val finalPrice: Double
        get() = price - discount
}

fun main() {
    val product1 = BetterProduct(1, "Laptop", 999.99, 100.0, 5)
    val product2 = BetterProduct(1, "Laptop", 999.99, 50.0, 3)

    // Now equals() compares all properties
    println("product1 == product2: ${product1 == product2}")  // false

    // toString() shows all properties
    println(product1)
    // BetterProduct(id=1, name=Laptop, price=999.99, discount=100.0, quantity=5, lastUpdated=...)

    // copy() preserves all properties
    val copy = product1.copy(quantity = 10)
    println("Copy discount: ${copy.discount}")   // 100.0 (copied!)
    println("Copy quantity: ${copy.quantity}")   // 10 (updated)
}
```

**Mixed approach - when to use body properties:**

```kotlin
data class CachedData(
    val key: String,
    val value: String
) {
    // Metadata - not part of data identity
    @Transient
    var accessCount: Int = 0

    @Transient
    var lastAccessed: Long = 0

    fun access(): String {
        accessCount++
        lastAccessed = System.currentTimeMillis()
        return value
    }
}

fun main() {
    val cache1 = CachedData("user_1", "Alice")
    val cache2 = CachedData("user_1", "Alice")

    cache1.access()
    cache1.access()
    cache2.access()

    // Same data, different metadata
    println("cache1 == cache2: ${cache1 == cache2}")  // true (correct!)
    println("cache1 accesses: ${cache1.accessCount}")  // 2
    println("cache2 accesses: ${cache2.accessCount}")  // 1

    // Both can be keys in map because they're equal
    val map = mutableMapOf<CachedData, String>()
    map[cache1] = "First"
    map[cache2] = "Second"  // Replaces first
    println("Map size: ${map.size}")  // 1
}
```

**Validation with primary constructor properties:**

```kotlin
data class Email(val address: String) {
    init {
        require(address.contains("@")) {
            "Email must contain @"
        }
        require(address.length >= 5) {
            "Email too short"
        }
    }

    // Additional computed property
    val domain: String
        get() = address.substringAfter("@")
}

data class Age(val years: Int) {
    init {
        require(years in 0..150) {
            "Age must be between 0 and 150"
        }
    }

    val isAdult: Boolean
        get() = years >= 18
}

fun main() {
    val email = Email("user@example.com")
    println(email)
    println("Domain: ${email.domain}")

    val age = Age(25)
    println(age)
    println("Is adult: ${age.isAdult}")

    // These would throw exceptions:
    // Email("invalid")  // No @
    // Age(-5)  // Negative
}
```

**Complete example:**

```kotlin
data class UserProfile(
    // Core data - in primary constructor
    val userId: Int,
    val username: String,
    var email: String,
    var displayName: String
) {
    // Metadata - in class body
    var loginCount: Int = 0
    var lastLoginAt: Long = 0
    var createdAt: Long = System.currentTimeMillis()

    // Computed properties
    val isNewUser: Boolean
        get() = loginCount < 5

    fun login() {
        loginCount++
        lastLoginAt = System.currentTimeMillis()
    }

    override fun toString(): String {
        // Custom toString including metadata
        return "UserProfile(userId=$userId, username='$username', email='$email', " +
                "displayName='$displayName', loginCount=$loginCount, lastLoginAt=$lastLoginAt)"
    }
}

fun main() {
    val user1 = UserProfile(1, "alice", "alice@example.com", "Alice")
    val user2 = UserProfile(1, "alice", "alice@example.com", "Alice")

    user1.login()
    user1.login()
    user2.login()

    // Data equality - only primary constructor
    println("Data equal: ${user1 == user2}")  // true

    // But different state
    println("User1 logins: ${user1.loginCount}")  // 2
    println("User2 logins: ${user2.loginCount}")  // 1

    // Custom toString shows everything
    println(user1)

    // copy() only copies primary constructor
    val user3 = user1.copy(displayName = "Alice Smith")
    println("User3 login count: ${user3.loginCount}")  // 0 (not copied)
}
```

---

## Ответ (RU)

В data class можно использовать только свойства, объявленные в первичном конструкторе с `val` или `var`. Эти свойства автоматически участвуют в `equals()`, `hashCode()`, `toString()`, `copy()` и `componentN()`. Другие свойства (объявленные в теле класса) не считаются частью данных класса.

**Ключевые правила:**
- Параметры первичного конструктора должны быть помечены `val` или `var`
- Только свойства первичного конструктора используются в автогенерируемых методах
- Свойства в теле класса исключаются из `equals()`, `hashCode()`, `toString()`, `copy()`
- Требуется хотя бы один параметр в первичном конструкторе

### Пример

**Базовый data class:**
```kotlin
data class User(
    val id: Int,           // Включается во все методы
    val name: String,      // Включается во все методы
    var email: String      // Включается (var разрешен)
)
```

**Свойства в теле класса (НЕ участвуют):**
```kotlin
data class Product(
    val id: Int,
    val name: String
) {
    var discount: Double = 0.0  // НЕ участвует в equals, hashCode, toString, copy
    var quantity: Int = 0       // НЕ участвует
}

val p1 = Product(1, "Laptop")
p1.discount = 100.0

val p2 = Product(1, "Laptop")
p2.discount = 50.0  // Другая скидка

println(p1 == p2)  // true! (discount не сравнивается)
println(p1)        // Product(id=1, name=Laptop) - без discount
val copy = p1.copy()
println(copy.discount)  // 0.0 (не скопирован!)
```

**Правильный подход** - все важные данные в конструкторе:
```kotlin
data class BetterProduct(
    val id: Int,
    val name: String,
    val discount: Double = 0.0,  // В конструкторе
    val quantity: Int = 0         // В конструкторе
)

val p1 = BetterProduct(1, "Laptop", 100.0, 5)
val p2 = BetterProduct(1, "Laptop", 50.0, 3)

println(p1 == p2)  // false (все свойства сравниваются)
println(p1)        // Показывает все свойства
val copy = p1.copy(quantity = 10)
println(copy.discount)  // 100.0 (сохранен!)
```

**Когда использовать свойства в теле:**
- Для метаданных, которые не должны влиять на равенство объектов
- Для временных/вычисляемых значений
- Для кэшей и счетчиков

```kotlin
data class CachedData(
    val key: String,
    val value: String
) {
    var accessCount: Int = 0    // Метаданные
    var lastAccessed: Long = 0  // Не часть данных
}
```
