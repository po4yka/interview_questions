---
---
---id: kotlin-203
title: "Interface Properties / Свойства интерфейсов"
aliases: ["Interface Properties", "Свойства интерфейсов"]
topic: kotlin
subtopics: [null-safety, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features, c-properties, q-inline-functions--kotlin--medium, q-kotlin-delegation-detailed--kotlin--medium, q-statein-sharein-flow--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium]
---
# Вопрос (RU)
> Как работать со свойствами в интерфейсах в Kotlin?

---

# Question (EN)
> How to operate with properties in interfaces in Kotlin?

## Ответ (RU)

В интерфейсе можно объявить свойства `val` или `var` без инициализации. Интерфейсы не имеют собственного состояния и не могут использовать backing fields (`field`), поэтому:
- свойство без тела (без реализации аксессоров) является абстрактным, и его реализация (backing field, делегат или вычисление) должна быть предоставлена в реализующем классе;
- свойство с реализованным геттером/сеттером в интерфейсе должно быть реализуемым без обращения к `field` (например, вычисляться на основе других свойств или методов);
- инициализаторы свойств в интерфейсе недопустимы.

Ключевые правила:
- Свойства интерфейса не могут иметь backing fields.
- Можно объявлять кастомные геттеры (и сеттеры для `var`) прямо в интерфейсе, если реализация не требует `field`.
- Свойства `var` могут объявлять сеттеры; если аксессоры абстрактны (без тела), реализацию нужно дать в классе.
- Свойства могут быть абстрактными или иметь реализацию по умолчанию (вычисляемые свойства) в интерфейсе.
- Свойства можно переопределять в реализующих классах.
- Допустимо комбинировать несколько интерфейсов с пересекающимися или вычисляемыми свойствами.
- Допустимо использовать делегирование (`by`) и ленивую инициализацию (`by lazy`) в реализующих классах для свойств, объявленных в интерфейсе.

### Примеры Кода (RU)

Базовые свойства интерфейса:

```kotlin
interface User {
    // Абстрактное свойство — реализация обязательна в классе
    val name: String

    val email: String

    // Свойство с кастомным геттером — есть реализация по умолчанию
    val displayName: String
        get() = "User: $name"

    // Вычисляемое свойство на основе других свойств
    val isValid: Boolean
        get() = name.isNotEmpty() && email.contains("@")
}

class BasicUser(
    override val name: String,
    override val email: String
) : User
```

`val` vs `var` в интерфейсах:

```kotlin
interface Config {
    // val с геттером по умолчанию
    val apiUrl: String
        get() = "https://api.example.com"

    // var — абстрактное изменяемое свойство, реализация в классе
    var timeout: Int

    // var с кастомным геттером, но абстрактным сеттером
    var debugMode: Boolean
        get() = false
}

class AppConfig : Config {
    override val apiUrl: String = "https://api.production.com"
    override var timeout: Int = 30
    override var debugMode: Boolean = false
}
```

Кастомные геттеры и вычисляемые свойства:

```kotlin
interface Shape {
    val width: Double
    val height: Double

    val area: Double
        get() = width * height

    val perimeter: Double
        get() = 2 * (width + height)

    val diagonal: Double
        get() = Math.sqrt(width * width + height * height)
}

class Rectangle(
    override val width: Double,
    override val height: Double
) : Shape
```

Свойства с сеттером и валидацией в классе:

```kotlin
interface Nameable {
    var name: String

    val upperCaseName: String
        get() = name.uppercase()
}

class Person(override var name: String) : Nameable

class Product : Nameable {
    private var _name: String = ""

    override var name: String
        get() = _name
        set(value) {
            require(value.isNotBlank()) { "Name cannot be blank" }
            _name = value.trim()
        }
}
```

Несколько интерфейсов и переопределение свойств:

```kotlin
interface Identifiable {
    val id: String
}

interface Timestamped {
    val createdAt: Long
    val updatedAt: Long

    val age: Long
        get() = System.currentTimeMillis() - createdAt
}

interface NameHolder {
    val name: String
    val displayName: String
        get() = name
}

data class Article(
    override val id: String,
    override val name: String,
    override val createdAt: Long,
    override val updatedAt: Long
) : Identifiable, Timestamped, NameHolder {
    override val displayName: String
        get() = "Article: $name"
}
```

Делегирование и `by lazy` в реализации:

```kotlin
interface DataProvider {
    val data: List<String>
    val size: Int
        get() = data.size

    val isEmpty: Boolean
        get() = data.isEmpty()

    val firstOrNull: String?
        get() = data.firstOrNull()
}

class StringListProvider(override val data: List<String>) : DataProvider

class LazyDataProvider : DataProvider {
    override val data: List<String> by lazy {
        println("Loading data...")
        listOf("Item 1", "Item 2", "Item 3")
    }
}
```

`const` в companion object интерфейса и отсутствие backing fields:

```kotlin
interface Constants {
    companion object {
        const val MAX_SIZE = 100
        const val DEFAULT_TIMEOUT = 30
        const val API_VERSION = "v1"
    }

    val maxRetries: Int
        get() = 3
}

interface Counter {
    // Нельзя иметь инициализатор или использовать field в интерфейсе

    var currentValue: Int
        get() = getCurrentCount()
        set(value) = setCurrentCount(value)

    fun getCurrentCount(): Int
    fun setCurrentCount(value: Int)
}
```

## Answer (EN)

In an interface, you can declare `val` or `var` properties without initialization. For properties, you can provide an implementation of the getter directly in the interface via a custom accessor. Interfaces do not have their own state and cannot use backing fields (`field`), therefore:
- a property without a body (no implemented accessors) is abstract, and its implementation (backing field or delegate/computation) must be provided in the implementing class;
- a property with implemented getter/setter in the interface must be implementable without using `field` (for example, computed from other properties or functions);
- property initializers in interfaces are not allowed.

Key rules:
- Interface properties cannot have backing fields.
- They can have custom getters (and setters for `var`) in the interface if the implementation does not require `field`.
- `var` properties can declare setters; if their accessors are abstract (no body), the implementation must be provided in the class.
- Properties can be abstract (no implementation) or have default implementations in the interface (e.g., computed properties).
- Properties can be overridden in implementing classes.
- You can combine multiple interfaces with overlapping or computed properties.
- Implementing classes can use delegation (`by`) and `by lazy` for properties declared in interfaces.

### Code Examples

Basic interface properties:

```kotlin
interface User {
    // Abstract property - must be implemented
    val name: String

    // Abstract property with type
    val email: String

    // Property with custom getter - has implementation
    val displayName: String
        get() = "User: $name"

    // Property with custom getter using other properties
    val isValid: Boolean
        get() = name.isNotEmpty() && email.contains("@")
}

class BasicUser(
    override val name: String,
    override val email: String
) : User
```

val vs var in interfaces:

```kotlin
interface Config {
    // val - read-only, can have getter
    val apiUrl: String
        get() = "https://api.example.com"  // Default implementation

    // var - abstract read-write property: implementation required in class
    var timeout: Int

    // var with custom getter only - still abstract setter
    var debugMode: Boolean
        get() = false  // Default value (no field)
}

class AppConfig : Config {
    // Can override val with val
    override val apiUrl: String = "https://api.production.com"

    // Must provide backing field or equivalent for abstract var
    override var timeout: Int = 30

    // Provide full implementation including setter
    override var debugMode: Boolean = false
}
```

Custom getters in interface:

```kotlin
interface Shape {
    val width: Double
    val height: Double

    // Computed property with getter
    val area: Double
        get() = width * height

    val perimeter: Double
        get() = 2 * (width + height)

    val diagonal: Double
        get() = Math.sqrt(width * width + height * height)
}

class Rectangle(
    override val width: Double,
    override val height: Double
) : Shape
```

Properties with setter (must be implemented in class if abstract):

```kotlin
interface Nameable {
    var name: String

    // Can have custom getter
    val upperCaseName: String
        get() = name.uppercase()
}

class Person(override var name: String) : Nameable {
    // name has both getter and setter from property
}

class Product : Nameable {
    // Custom implementation with backing field
    private var _name: String = ""

    override var name: String
        get() = _name
        set(value) {
            require(value.isNotBlank()) { "Name cannot be blank" }
            _name = value.trim()
        }
}
```

Multiple interface properties:

```kotlin
interface Identifiable {
    val id: String
}

interface Timestamped {
    val createdAt: Long
    val updatedAt: Long

    val age: Long
        get() = System.currentTimeMillis() - createdAt
}

interface NameHolder {
    val name: String
    val displayName: String
        get() = name
}

data class Article(
    override val id: String,
    override val name: String,
    override val createdAt: Long,
    override val updatedAt: Long
) : Identifiable, Timestamped, NameHolder {
    override val displayName: String
        get() = "Article: $name"
}
```

Properties with delegation:

```kotlin
interface DataProvider {
    val data: List<String>
    val size: Int
        get() = data.size

    val isEmpty: Boolean
        get() = data.isEmpty()

    val firstOrNull: String?
        get() = data.firstOrNull()
}

class StringListProvider(override val data: List<String>) : DataProvider

class LazyDataProvider : DataProvider {
    override val data: List<String> by lazy {
        println("Loading data...")
        listOf("Item 1", "Item 2", "Item 3")
    }
}
```

const in companion object of interface and no backing fields in interface:

```kotlin
interface Constants {
    companion object {
        const val MAX_SIZE = 100
        const val DEFAULT_TIMEOUT = 30
        const val API_VERSION = "v1"
    }

    val maxRetries: Int
        get() = 3
}

interface Counter {
    // This would NOT compile in interface:
    // var count: Int = 0
    // var count: Int
    //     get() = field
    //     set(value) { field = value }

    // This WORKS - no backing field needed in the interface itself:
    var currentValue: Int
        get() = getCurrentCount()
        set(value) = setCurrentCount(value)

    fun getCurrentCount(): Int
    fun setCurrentCount(value: Int)
}
```

---

## Дополнительные Вопросы (RU)

- В чем отличия работы со свойствами интерфейсов в Kotlin и Java?
- Когда на практике полезно использовать вычисляемые свойства в интерфейсе?
- Какие распространенные ошибки при использовании свойств интерфейсов в Kotlin?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-statein-sharein-flow--kotlin--medium]]
- [[q-inline-functions--kotlin--medium]]
- [[q-kotlin-delegation-detailed--kotlin--medium]]
