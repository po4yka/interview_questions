---id: cs-019
title: "Data Class Special Features / Специальные возможности Data Class"
aliases: ["Data Class Special Features", "Специальные возможности Data Class"]
topic: kotlin
subtopics: [functions, types]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml, q-abstract-class-purpose--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [copy, data-classes, difficulty/easy, equals, hashcode, kotlin, programming-languages, tostring]
sources: ["https://kotlinlang.org/docs/data-classes.html"]
---
# Вопрос (RU)
> Какие особенности имеет Data Class по сравнению с обычными Kotlin классами? Какие методы генерируются автоматически?

# Question (EN)
> What special features does Data Class have compared to regular Kotlin classes? What methods are generated automatically?

---

## Ответ (RU)

**Теория Data Classes:**
Data classes — специальные классы в Kotlin для хранения данных. Компилятор автоматически генерирует 5 основных методов: `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN()`. Эти методы основаны на `properties` в primary constructor. Data classes упрощают работу с immutable data и value objects.

**Автоматически генерируемые методы:**

**1. equals() - Сравнение по содержимому:**

*Теория:* `equals()` сравнивает structural equality (содержимое properties), не referential equality (ссылки). Для data classes два объекта равны, если все properties в primary constructor равны. Для обычных классов, если `equals()` не переопределён, `==` (operator) по умолчанию использует реализацию `equals()` из `Any`, которая сравнивает ссылки (referential equality).

```kotlin
// Data class - сравнение по содержимому
data class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = User("Alice", 30)
val user3 = User("Bob", 25)

println(user1 == user2)  // true - одинаковое содержимое
println(user1 == user3)  // false - разное содержимое
println(user1 === user2) // false - разные объекты в памяти

// Regular class без переопределения equals - сравнение по ссылкам
class Person(val name: String, val age: Int)

val p1 = Person("Alice", 30)
val p2 = Person("Alice", 30)
println(p1 == p2)  // false - разные ссылки!
```

**2. hashCode() - Генерация хеша:**

*Теория:* `hashCode()` генерирует hash code на основе properties в primary constructor. Соблюдается контракт: если `equals()` возвращает `true`, то `hashCode()` одинаковый. Важно для корректной работы в hash-based коллекциях (`HashSet`, `HashMap`).

```kotlin
// Data class - корректный hashCode
data class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = User("Alice", 30)

println(user1.hashCode() == user2.hashCode())  // true

// Работает в HashSet/HashMap
val set = hashSetOf(user1)
println(set.contains(user2))  // true - находит по содержимому

val map = hashMapOf(user1 to "data")
println(map[user2])  // "data" - находит по содержимому
```

**3. toString() - Читаемое представление:**

*Теория:* `toString()` генерирует human-readable строку в формате `ClassName(property1=value1, property2=value2)`. Включает все properties из primary constructor. Полезно для debugging и logging. Для обычных классов по умолчанию возвращается `ClassName@hashCode`.

```kotlin
// Data class - читаемый toString
data class User(val name: String, val age: Int, val email: String)

val user = User("Alice", 30, "alice@example.com")
println(user)  // User(name=Alice, age=30, email=alice@example.com)

// Regular class - нечитаемый toString по умолчанию
class Person(val name: String, val age: Int)
val person = Person("Alice", 30)
println(person)  // Person@7a81197d - бесполезно для debugging!
```

**4. copy() - Создание модифицированной копии:**

*Теория:* `copy()` создаёт shallow copy объекта с возможностью изменить некоторые properties. Поддерживает immutability pattern — вместо изменения объекта создаём новый. Принимает named parameters для properties, которые нужно изменить. Properties, не указанные в `copy()`, копируются из оригинала.

```kotlin
// copy() для immutability
data class User(val name: String, val age: Int, val email: String)

val user = User("Alice", 30, "alice@example.com")

// Изменить один property
val olderUser = user.copy(age = 31)
println(olderUser)  // User(name=Alice, age=31, email=alice@example.com)

// Изменить несколько properties
val updated = user.copy(name = "Alicia", email = "alicia@example.com")
println(updated)  // User(name=Alicia, age=30, email=alicia@example.com)

// Полная копия
val duplicate = user.copy()
println(duplicate == user)  // true - одинаковое содержимое
println(duplicate === user) // false - разные объекты
```

**5. componentN() - Destructuring:**

*Теория:* Функции `componentN()` (`component1()`, `component2()`, и т.д.) генерируются для каждого property в primary constructor. Позволяют destructuring declarations — извлечение properties в отдельные переменные. Порядок определяется порядком в primary constructor.

```kotlin
// Destructuring с data class
data class User(val name: String, val age: Int, val email: String)

val user = User("Alice", 30, "alice@example.com")

// Destructuring
val (name, age, email) = user
println("$name, $age, $email")  // Alice, 30, alice@example.com

// Пропуск properties с underscore
val (userName, _) = user  // age и email игнорируются
val (_, userAge, _) = user  // только age

// В циклах
val users = listOf(
    User("Alice", 30, "alice@example.com"),
    User("Bob", 25, "bob@example.com")
)

for ((name, age) in users) {
    println("$name: $age")
}
```

**Требования к Data Classes:**

*Теория:* Data class должен иметь primary constructor с хотя бы одним параметром. Параметры в primary constructor могут быть обычными параметрами или помечены как `val` / `var`. Только параметры, объявленные как `val` или `var`, становятся свойствами класса и участвуют в генерации `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN()`. Data class не может быть `abstract`, `open` или `inner`. (Начиная с Kotlin 1.1 data class может быть `sealed`.)

```kotlin
// Валидные data classes
data class User(val name: String, val age: Int)
data class MutableUser(var name: String, var age: Int)

// Параметр без val/var не становится property
data class UserWithParam(val name: String, age: Int)

// Невалидные data classes
// data class Empty()  // Error: нет параметров
// open data class OpenUser(val name: String)  // Error: data class не может быть open
// abstract data class AbstractUser(val name: String)  // Error: data class не может быть abstract
// inner data class InnerUser(val name: String)  // Error: data class не может быть inner
```

**Генерация только для Primary Constructor:**

*Теория:* Автоматически генерируемые методы используют только properties из primary constructor. Properties в body класса игнорируются в `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN()`. Это может привести к неожиданному поведению.

```kotlin
// Properties в body игнорируются
data class User(val name: String, val age: Int) {
    var address: String = ""  // НЕ в primary constructor
}

val user1 = User("Alice", 30).apply { address = "NYC" }
val user2 = User("Alice", 30).apply { address = "LA" }

// equals() игнорирует address
println(user1 == user2)  // true - address не учитывается

// copy() не копирует address
val copy = user1.copy()
println(copy.address)  // "" - пустая строка, не "NYC"

// toString() не включает address
println(user1)  // User(name=Alice, age=30) - без address
```

**Сравнение: Data Class vs Regular Class:**

```kotlin
// Regular class - всё вручную
class Person(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Person) return false
        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }

    override fun toString() = "Person(name=$name, age=$age)"

    // copy() недоступен по умолчанию
    // componentN() недоступны по умолчанию
}

// Data class - всё автоматически!
data class Person(val name: String, val age: Int)
```

**Use Cases для Data Classes:**

*Теория:* Data classes идеальны для value objects, DTOs, API responses, database entities, configuration, immutable state. Как правило, не рекомендуются для типов с сложной бизнес-логикой или активным mutable state management — их основная цель хранить данные.

```kotlin
// API response
data class UserResponse(
    val id: Int,
    val name: String,
    val email: String
)

// Database entity
data class TodoItem(
    val id: Long,
    val title: String,
    val completed: Boolean
)

// UI state
data class UiState(
    val isLoading: Boolean,
    val data: List<Item>?,
    val error: String?
)
```

**Ключевые концепции:**

1. **Auto-generation** — 5 основных методов генерируются автоматически
2. **Structural Equality** — сравнение по содержимому, не по ссылкам (по умолчанию)
3. **Immutability Pattern** — `copy()` для создания изменённых копий
4. **Primary Constructor Only** — генерация только для primary constructor properties
5. **Value Objects** — идеальны для хранения данных без сложной бизнес-логики

## Answer (EN)

**Data Classes Theory:**
Data classes are special classes in Kotlin for storing data. The compiler automatically generates 5 primary methods: `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN()`. These methods are based on the properties in the primary constructor. Data classes simplify working with immutable data and value objects.

**Automatically Generated Methods:**

**1. equals() - Content Comparison:**

*Theory:* `equals()` compares structural equality (properties content), not referential equality (references). For data classes two objects are equal if all properties in the primary constructor are equal. For regular classes, if `equals()` is not overridden, `==` uses the implementation from `Any`, which compares references (referential equality).

```kotlin
// Data class - content comparison
data class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = User("Alice", 30)
val user3 = User("Bob", 25)

println(user1 == user2)  // true - same content
println(user1 == user3)  // false - different content
println(user1 === user2) // false - different objects in memory

// Regular class without overridden equals - reference comparison
class Person(val name: String, val age: Int)

val p1 = Person("Alice", 30)
val p2 = Person("Alice", 30)
println(p1 == p2)  // false - different references!
```

**2. hashCode() - Hash Generation:**

*Theory:* `hashCode()` generates a hash code based on properties in the primary constructor. The contract is respected: if `equals()` returns `true`, then `hashCode()` is the same. This is required for correct behavior in hash-based collections (`HashSet`, `HashMap`).

```kotlin
// Data class - correct hashCode
data class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = User("Alice", 30)

println(user1.hashCode() == user2.hashCode())  // true

// Works in HashSet/HashMap
val set = hashSetOf(user1)
println(set.contains(user2))  // true - finds by content

val map = hashMapOf(user1 to "data")
println(map[user2])  // "data" - finds by content
```

**3. toString() - Readable Representation:**

*Theory:* `toString()` generates a human-readable string in format `ClassName(property1=value1, property2=value2)`. It includes all properties from the primary constructor. Useful for debugging and logging. For regular classes, the default implementation returns `ClassName@hashCode`.

```kotlin
// Data class - readable toString
data class User(val name: String, val age: Int, val email: String)

val user = User("Alice", 30, "alice@example.com")
println(user)  // User(name=Alice, age=30, email=alice@example.com)

// Regular class - unreadable default toString
class Person(val name: String, val age: Int)
val person = Person("Alice", 30)
println(person)  // Person@7a81197d - useless for debugging!
```

**4. copy() - Creating Modified Copy:**

*Theory:* `copy()` creates a shallow copy of an object with the ability to change some properties. It supports the immutability pattern — instead of changing an object, create a new one. It accepts named parameters for properties to change. Properties not specified in `copy()` are copied from the original.

```kotlin
// copy() for immutability
data class User(val name: String, val age: Int, val email: String)

val user = User("Alice", 30, "alice@example.com")

// Change one property
val olderUser = user.copy(age = 31)
println(olderUser)  // User(name=Alice, age=31, email=alice@example.com)

// Change multiple properties
val updated = user.copy(name = "Alicia", email = "alicia@example.com")
println(updated)  // User(name=Alicia, age=30, email=alicia@example.com)

// Full copy
val duplicate = user.copy()
println(duplicate == user)  // true - same content
println(duplicate === user) // false - different objects
```

**5. componentN() - Destructuring:**

*Theory:* `componentN()` functions (`component1()`, `component2()`, etc.) are generated for each property in the primary constructor. They allow destructuring declarations — extracting properties into separate variables. The order is determined by the order in the primary constructor.

```kotlin
// Destructuring with data class
data class User(val name: String, val age: Int, val email: String)

val user = User("Alice", 30, "alice@example.com")

// Destructuring
val (name, age, email) = user
println("$name, $age, $email")  // Alice, 30, alice@example.com

// Skip properties with underscore
val (userName, _) = user  // age and email ignored
val (_, userAge, _) = user  // only age

// In loops
val users = listOf(
    User("Alice", 30, "alice@example.com"),
    User("Bob", 25, "bob@example.com")
)

for ((name, age) in users) {
    println("$name: $age")
}
```

**Data Classes Requirements:**

*Theory:* A data class must have a primary constructor with at least one parameter. Parameters in the primary constructor may be regular parameters or marked as `val` / `var`. Only parameters declared as `val` or `var` become properties of the class and participate in the generation of `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN()`. A data class cannot be `abstract`, `open`, or `inner`. (Since Kotlin 1.1, a data class is allowed to be `sealed`.)

```kotlin
// Valid data classes
data class User(val name: String, val age: Int)
data class MutableUser(var name: String, var age: Int)

// Parameter without val/var is not a property
data class UserWithParam(val name: String, age: Int)

// Invalid data classes
// data class Empty()  // Error: no parameters
// open data class OpenUser(val name: String)  // Error: data class cannot be open
// abstract data class AbstractUser(val name: String)  // Error: data class cannot be abstract
// inner data class InnerUser(val name: String)  // Error: data class cannot be inner
```

**Generation Only for Primary Constructor:**

*Theory:* Automatically generated methods use only properties from the primary constructor. Properties in the class body are ignored in `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN()`. This can lead to unexpected behavior.

```kotlin
// Properties in body are ignored
data class User(val name: String, val age: Int) {
    var address: String = ""  // NOT in primary constructor
}

val user1 = User("Alice", 30).apply { address = "NYC" }
val user2 = User("Alice", 30).apply { address = "LA" }

// equals() ignores address
println(user1 == user2)  // true - address not considered

// copy() doesn't copy address
val copy = user1.copy()
println(copy.address)  // "" - empty string, not "NYC"

// toString() doesn't include address
println(user1)  // User(name=Alice, age=30) - without address
```

**Comparison: Data Class vs Regular Class:**

```kotlin
// Regular class - everything manual
class Person(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Person) return false
        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }

    override fun toString() = "Person(name=$name, age=$age)"

    // copy() unavailable by default
    // componentN() unavailable by default
}

// Data class - everything automatic!
data class Person(val name: String, val age: Int)
```

**Use Cases for Data Classes:**

*Theory:* Data classes are ideal for value objects, DTOs, API responses, database entities, configuration, immutable state. As a rule of thumb, they are not recommended for types with complex business logic or heavy mutable state management — their primary purpose is to hold data.

```kotlin
// API response
data class UserResponse(
    val id: Int,
    val name: String,
    val email: String
)

// Database entity
data class TodoItem(
    val id: Long,
    val title: String,
    val completed: Boolean
)

// UI state
data class UiState(
    val isLoading: Boolean,
    val data: List<Item>?,
    val error: String?
)
```

**Key Concepts:**

1. **Auto-generation** - 5 primary methods generated automatically
2. **Structural Equality** - comparison by content (by default), not references
3. **Immutability Pattern** - `copy()` for creating modified copies
4. **Primary Constructor Only** - generation only for primary constructor properties
5. **Value Objects** - ideal for storing data without complex business logic

---

## Дополнительные Вопросы (RU)

- Что произойдет, если переопределить `equals()` без переопределения `hashCode()` в data class?
- Могут ли data classes наследоваться от других классов?
- Как работает `copy()` с вложенными data classes?

## Follow-ups

- What happens if you override `equals()` but not `hashCode()` in a data class?
- Can data classes inherit from other classes?
- How does `copy()` work with nested data classes?

## Связанные Вопросы (RU)

### Предпосылки (проще)
- Базовые Kotlin-классы
- Свойства и конструкторы в Kotlin

### Похожие (тот Же уровень)
- Компонентные функции data classes
- Базовые операции с data classes

### Продвинутые (сложнее)
- Глубокое копирование вложенных data classes
- Пользовательская реализация `equals()`/`hashCode()`

## Related Questions

### Prerequisites (Easier)
- Basic Kotlin classes
- Kotlin properties and constructors

### Related (Same Level)
- Data classes component functions
- Data classes basics

### Advanced (Harder)
- Deep copy for nested data classes
- Custom equals/hashCode implementation

## Ссылки (RU)

- [Документация Kotlin: Data classes](https://kotlinlang.org/docs/data-classes.html)

## References

- [Kotlin Documentation: Data classes](https://kotlinlang.org/docs/data-classes.html)
