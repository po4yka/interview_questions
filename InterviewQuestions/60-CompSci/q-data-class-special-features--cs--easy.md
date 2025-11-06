---
id: cs-019
title: "Data Class Special Features / Специальные возможности Data Class"
aliases: ["Data Class Special Features", "Специальные возможности Data Class"]
topic: cs
subtopics: [data-classes, kotlin, programming-languages]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-data-classes]
created: 2025-10-15
updated: 2025-01-25
tags: [copy, data-class, difficulty/easy, equals, hashcode, kotlin, programming-languages, tostring]
sources: [https://kotlinlang.org/docs/data-classes.html]
---

# Вопрос (RU)
> Какие особенности имеет Data Class по сравнению с обычными Kotlin классами? Какие методы генерируются автоматически?

# Question (EN)
> What special features does Data Class have compared to regular Kotlin classes? What methods are generated automatically?

---

## Ответ (RU)

**Теория Data Classes:**
Data classes - специальные классы в Kotlin для хранения данных. Компилятор автоматически генерирует 5 методов: `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN()`. Эти методы основаны на properties в primary constructor. Data classes упрощают работу с immutable data и value objects.

**Автоматически генерируемые методы:**

**1. equals() - Сравнение по содержимому:**

*Теория:* `equals()` сравнивает structural equality (содержимое properties), не referential equality (ссылки). Для data classes два объекта равны, если все properties в primary constructor равны. Для обычных классов `==` сравнивает ссылки (referential equality).

```kotlin
// ✅ Data class - сравнение по содержимому
data class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = User("Alice", 30)
val user3 = User("Bob", 25)

println(user1 == user2)  // true - одинаковое содержимое
println(user1 == user3)  // false - разное содержимое
println(user1 === user2) // false - разные объекты в памяти

// ❌ Regular class - сравнение по ссылкам
class Person(val name: String, val age: Int)

val p1 = Person("Alice", 30)
val p2 = Person("Alice", 30)
println(p1 == p2)  // false - разные ссылки!
```

**2. hashCode() - Генерация хеша:**

*Теория:* `hashCode()` генерирует hash code на основе properties в primary constructor. Гарантирует contract: если `equals()` возвращает `true`, то `hashCode()` одинаковый. Необходимо для корректной работы в hash-based коллекциях (HashSet, HashMap).

```kotlin
// ✅ Data class - корректный hashCode
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

*Теория:* `toString()` генерирует human-readable строку в формате `ClassName(property1=value1, property2=value2)`. Включает все properties из primary constructor. Полезно для debugging и logging. Для обычных классов возвращает `ClassName@hashCode`.

```kotlin
// ✅ Data class - читаемый toString
data class User(val name: String, val age: Int, val email: String)

val user = User("Alice", 30, "alice@example.com")
println(user)  // User(name=Alice, age=30, email=alice@example.com)

// ❌ Regular class - нечитаемый toString
class Person(val name: String, val age: Int)
val person = Person("Alice", 30)
println(person)  // Person@7a81197d - бесполезно для debugging!
```

**4. copy() - Создание модифицированной копии:**

*Теория:* `copy()` создаёт shallow copy объекта с возможностью изменить некоторые properties. Поддерживает immutability pattern - вместо изменения объекта создаём новый. Принимает named parameters для properties, которые нужно изменить. Properties не указанные в `copy()` копируются из оригинала.

```kotlin
// ✅ copy() для immutability
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

*Теория:* `componentN()` функции (component1(), component2(), etc.) генерируются для каждого property в primary constructor. Позволяют destructuring declarations - извлечение properties в отдельные переменные. Порядок определяется порядком в primary constructor.

```kotlin
// ✅ Destructuring с data class
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

*Теория:* Data class должен иметь primary constructor с хотя бы одним parameter. Все parameters должны быть `val` или `var`. Не может быть `abstract`, `open`, `sealed`, или `inner`. Эти ограничения обеспечивают корректную генерацию методов.

```kotlin
// ✅ Валидные data classes
data class User(val name: String, val age: Int)
data class MutableUser(var name: String, var age: Int)

// ❌ Невалидные data classes
// data class Empty()  // Error: нет parameters
// open data class OpenUser(val name: String)  // Error: open
// abstract data class AbstractUser(val name: String)  // Error: abstract
```

**Генерация только для Primary Constructor:**

*Теория:* Автоматически генерируемые методы используют только properties из primary constructor. Properties в body класса игнорируются в `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN()`. Это может привести к неожиданному поведению.

```kotlin
// ✅ Properties в body игнорируются
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
// ❌ Regular class - всё вручную
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

    // copy() недоступен
    // componentN() недоступны
}

// ✅ Data class - всё автоматически!
data class Person(val name: String, val age: Int)
```

**Use Cases для Data Classes:**

*Теория:* Data classes идеальны для value objects, DTOs, API responses, database entities, configuration, immutable state. Не использовать для классов с бизнес-логикой или mutable state management.

```kotlin
// ✅ API response
data class UserResponse(
    val id: Int,
    val name: String,
    val email: String
)

// ✅ Database entity
data class TodoItem(
    val id: Long,
    val title: String,
    val completed: Boolean
)

// ✅ UI state
data class UiState(
    val isLoading: Boolean,
    val data: List<Item>?,
    val error: String?
)
```

**Ключевые концепции:**

1. **Auto-generation** - 5 методов генерируются автоматически
2. **Structural Equality** - сравнение по содержимому, не по ссылкам
3. **Immutability Pattern** - `copy()` для создания изменённых копий
4. **Primary Constructor Only** - генерация только для primary constructor properties
5. **Value Objects** - идеальны для хранения данных без бизнес-логики

## Answer (EN)

**Data Classes Theory:**
Data classes - special classes in Kotlin for storing data. Compiler automatically generates 5 methods: `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN()`. These methods based on properties in primary constructor. Data classes simplify working with immutable data and value objects.

**Automatically Generated Methods:**

**1. equals() - Content Comparison:**

*Theory:* `equals()` compares structural equality (properties content), not referential equality (references). For data classes two objects equal if all properties in primary constructor equal. For regular classes `==` compares references (referential equality).

```kotlin
// ✅ Data class - content comparison
data class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = User("Alice", 30)
val user3 = User("Bob", 25)

println(user1 == user2)  // true - same content
println(user1 == user3)  // false - different content
println(user1 === user2) // false - different objects in memory

// ❌ Regular class - reference comparison
class Person(val name: String, val age: Int)

val p1 = Person("Alice", 30)
val p2 = Person("Alice", 30)
println(p1 == p2)  // false - different references!
```

**2. hashCode() - Hash Generation:**

*Theory:* `hashCode()` generates hash code based on properties in primary constructor. Guarantees contract: if `equals()` returns `true`, then `hashCode()` same. Required for correct work in hash-based collections (HashSet, HashMap).

```kotlin
// ✅ Data class - correct hashCode
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

*Theory:* `toString()` generates human-readable string in format `ClassName(property1=value1, property2=value2)`. Includes all properties from primary constructor. Useful for debugging and logging. For regular classes returns `ClassName@hashCode`.

```kotlin
// ✅ Data class - readable toString
data class User(val name: String, val age: Int, val email: String)

val user = User("Alice", 30, "alice@example.com")
println(user)  // User(name=Alice, age=30, email=alice@example.com)

// ❌ Regular class - unreadable toString
class Person(val name: String, val age: Int)
val person = Person("Alice", 30)
println(person)  // Person@7a81197d - useless for debugging!
```

**4. copy() - Creating Modified Copy:**

*Theory:* `copy()` creates shallow copy of object with ability to change some properties. Supports immutability pattern - instead of changing object create new one. Accepts named parameters for properties to change. Properties not specified in `copy()` copied from original.

```kotlin
// ✅ copy() for immutability
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

*Theory:* `componentN()` functions (component1(), component2(), etc.) generated for each property in primary constructor. Allow destructuring declarations - extracting properties into separate variables. Order determined by primary constructor order.

```kotlin
// ✅ Destructuring with data class
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

*Theory:* Data class must have primary constructor with at least one parameter. All parameters must be `val` or `var`. Cannot be `abstract`, `open`, `sealed`, or `inner`. These restrictions ensure correct method generation.

```kotlin
// ✅ Valid data classes
data class User(val name: String, val age: Int)
data class MutableUser(var name: String, var age: Int)

// ❌ Invalid data classes
// data class Empty()  // Error: no parameters
// open data class OpenUser(val name: String)  // Error: open
// abstract data class AbstractUser(val name: String)  // Error: abstract
```

**Generation Only for Primary Constructor:**

*Theory:* Automatically generated methods use only properties from primary constructor. Properties in class body ignored in `equals()`, `hashCode()`, `toString()`, `copy()`, `componentN()`. This can lead to unexpected behavior.

```kotlin
// ✅ Properties in body ignored
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
// ❌ Regular class - everything manual
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

    // copy() unavailable
    // componentN() unavailable
}

// ✅ Data class - everything automatic!
data class Person(val name: String, val age: Int)
```

**Use Cases for Data Classes:**

*Theory:* Data classes ideal for value objects, DTOs, API responses, database entities, configuration, immutable state. Don't use for classes with business logic or mutable state management.

```kotlin
// ✅ API response
data class UserResponse(
    val id: Int,
    val name: String,
    val email: String
)

// ✅ Database entity
data class TodoItem(
    val id: Long,
    val title: String,
    val completed: Boolean
)

// ✅ UI state
data class UiState(
    val isLoading: Boolean,
    val data: List<Item>?,
    val error: String?
)
```

**Key Concepts:**

1. **Auto-generation** - 5 methods generated automatically
2. **Structural Equality** - comparison by content, not references
3. **Immutability Pattern** - `copy()` for creating modified copies
4. **Primary Constructor Only** - generation only for primary constructor properties
5. **Value Objects** - ideal for storing data without business logic

---

## Follow-ups

- What happens if you override equals() but not hashCode() in data class?
- Can data classes inherit from other classes?
- How does copy() work with nested data classes?

## Related Questions

### Prerequisites (Easier)
- Basic Kotlin classes
- Kotlin properties and constructors

### Related (Same Level)
- [[q-data-class-component-functions--programming-languages--easy]] - Component functions details
- [[q-kotlin-data-classes--kotlin--easy]] - Data classes basics

### Advanced (Harder)
- Deep copy for nested data classes
- Custom equals/hashCode implementation
