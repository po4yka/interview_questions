---
'---id': kotlin-151
title: Data Class Variables / Переменные data class
aliases:
- Data Class Variables
- Переменные data class
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
- q-stateflow-sharedflow-differences--kotlin--medium
- q-suspend-functions-basics--kotlin--easy
created: 2025-10-15
updated: 2025-11-09
tags:
- data-classes
- difficulty/medium
- programming-languages
anki_cards:
- slug: q-data-class-variables--kotlin--medium-0-en
  language: en
  anki_id: 1768326280905
  synced_at: '2026-01-23T17:03:50.597745'
- slug: q-data-class-variables--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326280930
  synced_at: '2026-01-23T17:03:50.599472'
---
# Вопрос (RU)
> Какие переменные можно использовать в data class в Kotlin?

---

# Question (EN)
> What variables can be used in a data class in Kotlin?

## Ответ (RU)

В `data class` учитываются только свойства, объявленные в первичном конструкторе с `val` или `var`. Эти свойства автоматически участвуют в `equals()`, `hashCode()`, `toString()`, `copy()` и `componentN()`. Свойства, объявленные в теле класса, не считаются частью "данных" класса и не включаются в автогенерируемые методы.

**Ключевые правила:**
- Параметры первичного конструктора должны быть помечены `val` или `var`.
- Только свойства первичного конструктора используются в автогенерируемых методах.
- Свойства в теле класса исключаются из `equals()`, `hashCode()`, `toString()`, `copy()`.
- Требуется хотя бы один параметр в первичном конструкторе.

### Примеры Кода

**Базовый data class:**

```kotlin
data class User(
    val id: Int,           // Включается во все методы
    val name: String,      // Включается во все методы
    var email: String,     // Включается во все методы (var допускается)
    val age: Int = 0       // Включается (допустимы значения по умолчанию)
)

fun main() {
    val user = User(1, "Alice", "alice@example.com", 30)

    // toString включает все свойства из первичного конструктора
    println(user)
    // User(id=1, name=Alice, email=alice@example.com, age=30)

    // Деструктуризация использует componentN() для свойств конструктора
    val (id, name, email, age) = user
    println("$name ($id): $email, age $age")

    // copy() работает только с этими свойствами
    val updated = user.copy(email = "newemail@example.com")
    println(updated)
}
```

**Свойства в теле класса (ИСКЛЮЧЕНЫ из data-методов):**

```kotlin
data class Product(
    val id: Int,
    val name: String,
    val price: Double
) {
    // Свойства тела класса не включаются в equals, hashCode, toString, copy
    var discount: Double = 0.0
    var quantity: Int = 0
    var lastUpdated: Long = System.currentTimeMillis()

    // Вычисляемое свойство также не включается
    val finalPrice: Double
        get() = price - discount
}

fun main() {
    val product1 = Product(1, "Laptop", 999.99)
    product1.discount = 100.0
    product1.quantity = 5

    val product2 = Product(1, "Laptop", 999.99)
    product2.discount = 50.0  // Другая скидка
    product2.quantity = 3     // Другое количество

    // equals() сравнивает только свойства первичного конструктора
    println("product1 == product2: ${product1 == product2}")  // true!

    // toString() показывает только свойства конструктора
    println(product1)
    // Product(id=1, name=Laptop, price=999.99)

    // copy() копирует только свойства конструктора
    val copy = product1.copy()
    println("Copy discount: ${copy.discount}")   // 0.0 (не скопировано)
    println("Copy quantity: ${copy.quantity}")   // 0 (не скопировано)

    // componentN() только для свойств конструктора
    val (id, name, price) = product1
    println("Destructured: id=$id, name=$name, price=$price")
}
```

**`val` vs `var` в data class:**

```kotlin
data class Person(
    val id: Int,          // Неизменяемое поле
    var name: String,     // Изменяемое поле
    var age: Int          // Изменяемое поле
)

fun main() {
    val person = Person(1, "Alice", 30)

    person.name = "Alice Smith"  // OK
    person.age = 31               // OK

    // person.id = 2  // ОШИБКА: val нельзя переназначить

    println(person)
}
```

**Демонстрация поведения `equals()` и коллекций:**

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
    book2.pages = 500
    book2.publisher = "Другой издатель"

    // Равенство основано только на isbn и title
    println("Books equal: ${book1 == book2}")  // true

    val set = setOf(book1, book2)
    println("Set size: ${set.size}")           // 1

    val map = mapOf(book1 to "First edition")
    println("Find with book2: ${map[book2]}")  // "First edition"
}
```

**Почему это важно — пример с версионированием:**

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
```

**Корректный подход — все значимые данные в конструкторе:**

```kotlin
data class BetterProduct(
    val id: Int,
    val name: String,
    val price: Double,
    val discount: Double = 0.0,    // В конструкторе
    val quantity: Int = 0,         // В конструкторе
    val lastUpdated: Long = System.currentTimeMillis()
) {
    val finalPrice: Double
        get() = price - discount
}
```

**Смешанный подход — метаданные в теле:**

```kotlin
data class CachedData(
    val key: String,
    val value: String
) {
    // Метаданные, не влияющие на идентичность данных
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
```

**Валидация в init-блоке и вычисляемые свойства:**

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
```

**Полный пример:**

```kotlin
data class UserProfile(
    // Основные данные — в первичном конструкторе
    val userId: Int,
    val username: String,
    var email: String,
    var displayName: String
) {
    // Метаданные — в теле класса
    var loginCount: Int = 0
    var lastLoginAt: Long = 0
    var createdAt: Long = System.currentTimeMillis()

    val isNewUser: Boolean
        get() = loginCount < 5

    fun login() {
        loginCount++
        lastLoginAt = System.currentTimeMillis()
    }

    override fun toString(): String {
        return "UserProfile(userId=$userId, username='$username', email='$email', " +
                "displayName='$displayName', loginCount=$loginCount, lastLoginAt=$lastLoginAt)"
    }
}
```

## Answer (EN)

In a `data class`, only properties declared in the primary constructor with `val` or `var` are considered part of the data. These properties automatically participate in `equals()`, `hashCode()`, `toString()`, `copy()`, and `componentN()` functions. Properties declared in the class body are not part of the structural data and are ignored by the generated methods.

**Key rules:**
- Primary constructor parameters must be marked with `val` or `var`.
- Only primary constructor properties are used in the auto-generated methods.
- Properties in the class body are excluded from `equals()`, `hashCode()`, `toString()`, `copy()`.
- At least one primary constructor parameter is required.

### Code Examples

The following Kotlin examples mirror the RU section and illustrate the same rules.

**Basic data class:**

```kotlin
data class User(
    val id: Int,           // Included in all generated methods
    val name: String,      // Included in all generated methods
    var email: String,     // Included in all generated methods (var is allowed)
    val age: Int = 0       // Included; default values are allowed
)

fun main() {
    val user = User(1, "Alice", "alice@example.com", 30)

    // toString includes all primary-constructor properties
    println(user)
    // User(id=1, name=Alice, email=alice@example.com, age=30)

    // Destructuring uses componentN() for primary-constructor properties
    val (id, name, email, age) = user
    println("$name ($id): $email, age $age")

    // copy() works only with these properties
    val updated = user.copy(email = "newemail@example.com")
    println(updated)
}
```

**Properties in the class body (EXCLUDED from data methods):**

```kotlin
data class Product(
    val id: Int,
    val name: String,
    val price: Double
) {
    // Body properties are not included in equals, hashCode, toString, copy
    var discount: Double = 0.0
    var quantity: Int = 0
    var lastUpdated: Long = System.currentTimeMillis()

    // Computed property is also not included
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

    // equals() compares only primary-constructor properties
    println("product1 == product2: ${product1 == product2}")  // true!

    // toString() shows only constructor properties
    println(product1)
    // Product(id=1, name=Laptop, price=999.99)

    // copy() copies only constructor properties
    val copy = product1.copy()
    println("Copy discount: ${copy.discount}")   // 0.0 (not copied)
    println("Copy quantity: ${copy.quantity}")   // 0 (not copied)

    // componentN() exists only for constructor properties
    val (id, name, price) = product1
    println("Destructured: id=$id, name=$name, price=$price")
}
```

**`val` vs `var` in a data class:**

```kotlin
data class Person(
    val id: Int,          // Immutable field
    var name: String,     // Mutable field
    var age: Int          // Mutable field
)

fun main() {
    val person = Person(1, "Alice", 30)

    person.name = "Alice Smith"  // OK
    person.age = 31               // OK

    // person.id = 2  // ERROR: val cannot be reassigned

    println(person)
}
```

**Demonstrating `equals()` behavior and collections:**

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
    book2.pages = 500
    book2.publisher = "Another publisher"

    // Equality is based only on isbn and title
    println("Books equal: ${book1 == book2}")  // true

    val set = setOf(book1, book2)
    println("Set size: ${set.size}")           // 1

    val map = mapOf(book1 to "First edition")
    println("Find with book2: ${map[book2]}")  // "First edition"
}
```

**Why this matters — versioning example:**

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
```

**Correct approach — all significant data in the constructor:**

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
```

**Mixed approach — metadata in the body:**

```kotlin
data class CachedData(
    val key: String,
    val value: String
) {
    // Metadata that does not affect data identity
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
```

**Validation in init block and computed properties:**

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
```

**Full example:**

```kotlin
data class UserProfile(
    // Core data — in the primary constructor
    val userId: Int,
    val username: String,
    var email: String,
    var displayName: String
) {
    // Metadata — in the class body
    var loginCount: Int = 0
    var lastLoginAt: Long = 0
    var createdAt: Long = System.currentTimeMillis()

    val isNewUser: Boolean
        get() = loginCount < 5

    fun login() {
        loginCount++
        lastLoginAt = System.currentTimeMillis()
    }

    override fun toString(): String {
        return "UserProfile(userId=$userId, username='$username', email='$email', " +
                "displayName='$displayName', loginCount=$loginCount, lastLoginAt=$lastLoginAt)"
    }
}
```

## Дополнительные Вопросы (RU)

- В чем ключевые отличия поведения `data class` по сравнению с Java-классами?
- В каких практических сценариях особенно полезны `data class` и их автогенерируемые методы?
- Каковы распространенные ошибки при использовании свойств тела класса в `data class`?

## Follow-ups

- What are the key differences between this and Java classes?
- In which practical scenarios are data classes and their generated methods especially useful?
- What are common pitfalls when using body properties in data classes?

## Ссылки (RU)

- [[c-kotlin]]
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-suspend-functions-basics--kotlin--easy]]

## Related Questions

- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-suspend-functions-basics--kotlin--easy]]
