---
id: 20251016-173030
title: "Builder Pattern / Builder Паттерн"
topic: computer-science
difficulty: medium
status: draft
moc: moc-compSci
related: [q-proxy-pattern--design-patterns--medium, q-garbage-collector-definition--programming-languages--easy, q-extensions-concept--programming-languages--easy]
created: 2025-10-15
tags:
  - design-patterns
  - creational-patterns
  - builder
  - gof-patterns
  - kotlin
---
# Builder Pattern

# Question (EN)
> What is the Builder pattern? When should it be used and how does it solve the telescoping constructor problem?

# Вопрос (RU)
> Что такое паттерн Builder? Когда его использовать и как он решает проблему телескопических конструкторов?

---

## Answer (EN)


**Builder (Строитель)** - это порождающий паттерн проектирования, который позволяет конструировать сложные объекты шаг за шагом. Паттерн позволяет создавать различные типы и представления объекта используя один и тот же код конструирования.

### Definition


Builder is a creational design pattern that lets you construct complex objects step by step. The pattern allows you to produce different types and representations of an object using the same construction code.

### Problems it Solves


The builder design pattern solves problems like:

1. **How can a class (the same construction process) create different representations of a complex object?**
2. **How can a class that includes creating a complex object be simplified?**

Creating and assembling the parts of a complex object directly within a class is inflexible. It commits the class to creating a particular representation of the complex object and makes it impossible to change the representation later independently from (without having to change) the class.

### Solution


The builder design pattern describes how to solve such problems:

1. **Encapsulate creating and assembling** the parts of a complex object in a separate `Builder` object
2. **A class delegates object creation** to a `Builder` object instead of creating the objects directly

A class (the same construction process) can delegate to different `Builder` objects to create different representations of a complex object.

## Telescoping Constructor Problem

Also builder solves problem of **telescoping constructors**, when many variants of constructor are created with increasing number of arguments:

```kotlin
// - Telescoping Constructor Anti-Pattern
constructor(firstName: String): this(firstName, "", 0)
constructor(firstName: String, lastName: String): this(firstName, lastName, 0)
constructor(firstName: String, lastName: String, age: Int)
```

Technically they allow you to use the constructor with just enough arguments you want to set, but in practice **adding a new field to the class forces you to modify each constructor**.

### Example: Kotlin-style Builder

```kotlin
class FoodOrder private constructor(
    val bread: String = "Flat bread",
    val condiments: String?,
    val meat: String?,
    val fish: String?
) {

    data class Builder(
        var bread: String? = null,
        var condiments: String? = null,
        var meat: String? = null,
        var fish: String? = null
    ) {

        fun bread(bread: String) = apply { this.bread = bread }
        fun condiments(condiments: String) = apply { this.condiments = condiments }
        fun meat(meat: String) = apply { this.meat = meat }
        fun fish(fish: String) = apply { this.fish = fish }

        fun build() = FoodOrder(
            bread ?: "Flat bread",
            condiments,
            meat,
            fish
        )

        fun randomBuild() = bread(bread ?: "dry")
            .condiments(condiments ?: "pepper")
            .meat(meat ?: "beef")
            .fish(fish ?: "Tilapia")
            .build()
    }
}

// Usage
val foodOrder = FoodOrder.Builder()
    .bread("white bread")
    .meat("bacon")
    .condiments("olive oil")
    .build()
```

## Android Example: NotificationBuilder

### NotificationBuilder

Most traditional usage of the Builder Pattern. Builder's Constructor takes 2 arguments necessary for proper object creation, other fields are getting values through setter methods called on the Builder instance. Finally the `build()` method is called that returns desired notification object.

```kotlin
val notificationBuilder = Notification.Builder(this, "channelId")
notificationBuilder.setContentTitle("Title")
notificationBuilder.setContentText("Content")
notificationBuilder.setSmallIcon(R.mipmap.ic_launcher)
val notification = notificationBuilder.build()
```

### AlertDialogBuilder

Very Kotlin style with utilizing the `apply`. Interestingly enough there is no `build()` method but `show()` that is not only returning dialog object but also displays it. Sounds like a bad idea for a method to do more than one thing, but in this case I believe it was done on purpose to avoid a common mistake of creating a dialog but forgetting to display it with a separate method.

```kotlin
val dialog = AlertDialog.Builder(this)
    .apply {
        setTitle("Title")
        setIcon(R.mipmap.ic_launcher)
    }.show()
```

## Kotlin Named Parameters Alternative

Kotlin comes with **named and default parameters** that help to minimize the number of overloads and improve the readability of the function invocation.

```kotlin
// Without Builder (using named parameters)
data class User(
    val firstName: String,
    val lastName: String = "",
    val age: Int = 0,
    val email: String? = null,
    val phone: String? = null
)

// Usage
val user = User(
    firstName = "John",
    lastName = "Doe",
    email = "john@example.com"
)
```

This is often preferred in Kotlin for simple cases, but Builder is still useful for:
- Complex validation logic
- Conditional object creation
- Multiple build variants (like `randomBuild()`)
- When you need to reuse builder state

## Преимущества и недостатки

### Advantages (Преимущества)


1. **Allows you to vary a product's internal representation** - Can create different representations using the same build process
2. **Encapsulates code for construction and representation** - Construction code is separated from business logic
3. **Provides control over the steps of the construction process** - Can execute construction steps in a specific order
4. **Avoids telescoping constructors** - No need for multiple constructor overloads
5. **Readable code** - Fluent interface makes code self-documenting

### Disadvantages (Недостатки)


1. **Builder classes must be mutable** - Goes against immutability principles
2. **May hamper/complicate dependency injection** - DI frameworks often work with constructors
3. **More code** - Requires creating builder class and methods
4. **Overkill for simple objects** - Kotlin named parameters are often better

## Complex Builder Example

```kotlin
// Complex builder with validation
class HttpRequest private constructor(
    val url: String,
    val method: String,
    val headers: Map<String, String>,
    val body: String?,
    val timeout: Long
) {

    class Builder(private val url: String) {
        private var method: String = "GET"
        private var headers: MutableMap<String, String> = mutableMapOf()
        private var body: String? = null
        private var timeout: Long = 30_000

        fun method(method: String) = apply {
            require(method in listOf("GET", "POST", "PUT", "DELETE")) {
                "Invalid HTTP method"
            }
            this.method = method
        }

        fun addHeader(key: String, value: String) = apply {
            headers[key] = value
        }

        fun headers(headers: Map<String, String>) = apply {
            this.headers.putAll(headers)
        }

        fun body(body: String) = apply {
            require(method != "GET") {
                "GET requests cannot have a body"
            }
            this.body = body
        }

        fun timeout(milliseconds: Long) = apply {
            require(milliseconds > 0) {
                "Timeout must be positive"
            }
            this.timeout = milliseconds
        }

        fun build(): HttpRequest {
            require(url.isNotBlank()) {
                "URL cannot be blank"
            }

            return HttpRequest(
                url = url,
                method = method,
                headers = headers.toMap(),
                body = body,
                timeout = timeout
            )
        }
    }
}

// Usage
val request = HttpRequest.Builder("https://api.example.com/users")
    .method("POST")
    .addHeader("Content-Type", "application/json")
    .addHeader("Authorization", "Bearer token")
    .body("""{"name": "John"}""")
    .timeout(60_000)
    .build()
```

## Best Practices

```kotlin
// - DO: Use private constructor
class Product private constructor(
    val param1: String,
    val param2: Int
) {
    class Builder { /* ... */ }
}

// - DO: Return builder from setter methods (fluent interface)
fun param1(value: String) = apply { this.param1 = value }

// - DO: Validate in build() method
fun build(): Product {
    require(param1.isNotBlank()) { "param1 is required" }
    return Product(param1, param2)
}

// - DO: Use nested Builder class
class Product {
    class Builder { /* ... */ }
}

// - DON'T: Use builder for simple data classes
// Prefer Kotlin named parameters

// - DON'T: Forget validation
// Build should validate before creating object
```

**English**: **Builder** is a creational design pattern for constructing complex objects step by step using the same construction code. **Problem**: Telescoping constructors (multiple constructor overloads) are inflexible and hard to maintain. Creating complex objects directly is rigid. **Solution**: Separate Builder object encapsulates object construction. **Advantages**: avoids telescoping constructors, encapsulates construction logic, fluent interface improves readability, control over construction steps. **Disadvantages**: mutable builders, more code, may complicate DI. **Android examples**: NotificationBuilder, AlertDialogBuilder. **Kotlin alternative**: named parameters for simple cases. Use Builder for: complex validation, conditional creation, multiple build variants.

## Links

- [Builder](https://refactoring.guru/design-patterns/builder)
- [Builder pattern](https://en.wikipedia.org/wiki/Builder_pattern)
- [Kotlin Builder Pattern](https://swiderski.tech/kotlin-builder-pattern/)
- [Builder Design Pattern in Kotlin](https://www.baeldung.com/kotlin/builder-pattern)

## Further Reading

- [Builder Design Pattern in Kotlin](https://medium.com/@ssvaghasiya61/builder-design-pattern-in-kotlin-50d6c669675c)

---
*Source: Kirchhoff Android Interview Questions*


## Ответ (RU)

### Определение

Builder (Строитель) - это порождающий паттерн проектирования, который позволяет конструировать сложные объекты шаг за шагом. Паттерн позволяет создавать различные типы и представления объекта, используя один и тот же код конструирования.

### Проблемы, которые решает

Паттерн Builder решает следующие проблемы:

1. **Как класс может создавать различные представления сложного объекта используя один и тот же процесс конструирования?**
2. **Как упростить класс, который включает создание сложного объекта?**

Создание и сборка частей сложного объекта напрямую внутри класса негибка. Это привязывает класс к созданию конкретного представления сложного объекта и делает невозможным изменение представления позже независимо от класса (без необходимости изменения класса).

### Решение

Паттерн Builder описывает, как решить такие проблемы:

1. **Инкапсулировать создание и сборку** частей сложного объекта в отдельном объекте `Builder`
2. **Класс делегирует создание объекта** объекту `Builder` вместо прямого создания объектов

Класс (один и тот же процесс конструирования) может делегировать различным объектам `Builder` создание различных представлений сложного объекта.

### Проблема телескопических конструкторов

Builder также решает проблему **телескопических конструкторов**, когда создается множество вариантов конструктора с увеличивающимся числом аргументов:

```kotlin
// Анти-паттерн телескопических конструкторов
constructor(firstName: String): this(firstName, "", 0)
constructor(firstName: String, lastName: String): this(firstName, lastName, 0)
constructor(firstName: String, lastName: String, age: Int)
```

Технически они позволяют использовать конструктор с необходимым количеством аргументов, но на практике **добавление нового поля в класс заставляет модифицировать каждый конструктор**.

### Пример: Kotlin-style Builder

```kotlin
class FoodOrder private constructor(
    val bread: String = "Flat bread",
    val condiments: String?,
    val meat: String?,
    val fish: String?
) {

    data class Builder(
        var bread: String? = null,
        var condiments: String? = null,
        var meat: String? = null,
        var fish: String? = null
    ) {

        fun bread(bread: String) = apply { this.bread = bread }
        fun condiments(condiments: String) = apply { this.condiments = condiments }
        fun meat(meat: String) = apply { this.meat = meat }
        fun fish(fish: String) = apply { this.fish = fish }

        fun build() = FoodOrder(
            bread ?: "Flat bread",
            condiments,
            meat,
            fish
        )

        fun randomBuild() = bread(bread ?: "dry")
            .condiments(condiments ?: "pepper")
            .meat(meat ?: "beef")
            .fish(fish ?: "Tilapia")
            .build()
    }
}

// Использование
val foodOrder = FoodOrder.Builder()
    .bread("white bread")
    .meat("bacon")
    .condiments("olive oil")
    .build()
```

### Примеры в Android

#### NotificationBuilder

Наиболее традиционное использование паттерна Builder. Конструктор Builder принимает 2 аргумента, необходимых для корректного создания объекта, остальные поля получают значения через setter методы, вызываемые на экземпляре Builder. В конце вызывается метод `build()`, который возвращает желаемый объект уведомления.

```kotlin
val notificationBuilder = Notification.Builder(this, "channelId")
notificationBuilder.setContentTitle("Title")
notificationBuilder.setContentText("Content")
notificationBuilder.setSmallIcon(R.mipmap.ic_launcher)
val notification = notificationBuilder.build()
```

#### AlertDialogBuilder

Очень Kotlin-стиль с использованием `apply`. Интересно, что здесь нет метода `build()`, а есть `show()`, который не только возвращает объект диалога, но и отображает его. Звучит как плохая идея для метода делать больше одной вещи, но в данном случае это сделано специально, чтобы избежать распространенной ошибки создания диалога без его отображения отдельным методом.

```kotlin
val dialog = AlertDialog.Builder(this)
    .apply {
        setTitle("Title")
        setIcon(R.mipmap.ic_launcher)
    }.show()
```

### Альтернатива в Kotlin: именованные параметры

Kotlin предоставляет **именованные параметры и параметры по умолчанию**, которые помогают минимизировать количество перегрузок и улучшить читаемость вызова функции.

```kotlin
// Без Builder (используя именованные параметры)
data class User(
    val firstName: String,
    val lastName: String = "",
    val age: Int = 0,
    val email: String? = null,
    val phone: String? = null
)

// Использование
val user = User(
    firstName = "John",
    lastName = "Doe",
    email = "john@example.com"
)
```

Это часто предпочтительнее в Kotlin для простых случаев, но Builder все еще полезен для:
- Сложной логики валидации
- Условного создания объектов
- Множественных вариантов сборки (как `randomBuild()`)
- Когда нужно переиспользовать состояние builder'а

### Преимущества

1. **Позволяет варьировать внутреннее представление продукта** - Можно создавать различные представления используя один и тот же процесс сборки
2. **Инкапсулирует код для конструирования и представления** - Код конструирования отделен от бизнес-логики
3. **Обеспечивает контроль над шагами процесса конструирования** - Можно выполнять шаги конструирования в определенном порядке
4. **Избегает телескопических конструкторов** - Нет необходимости в множественных перегрузках конструктора
5. **Читаемый код** - Fluent интерфейс делает код самодокументируемым

### Недостатки

1. **Классы Builder должны быть изменяемыми** - Идет вразрез с принципами неизменяемости
2. **Может затруднять внедрение зависимостей** - DI фреймворки часто работают с конструкторами
3. **Больше кода** - Требуется создание класса builder и методов
4. **Избыточность для простых объектов** - Именованные параметры Kotlin часто лучше

### Сложный пример Builder

```kotlin
// Сложный builder с валидацией
class HttpRequest private constructor(
    val url: String,
    val method: String,
    val headers: Map<String, String>,
    val body: String?,
    val timeout: Long
) {

    class Builder(private val url: String) {
        private var method: String = "GET"
        private var headers: MutableMap<String, String> = mutableMapOf()
        private var body: String? = null
        private var timeout: Long = 30_000

        fun method(method: String) = apply {
            require(method in listOf("GET", "POST", "PUT", "DELETE")) {
                "Неверный HTTP метод"
            }
            this.method = method
        }

        fun addHeader(key: String, value: String) = apply {
            headers[key] = value
        }

        fun headers(headers: Map<String, String>) = apply {
            this.headers.putAll(headers)
        }

        fun body(body: String) = apply {
            require(method != "GET") {
                "GET запросы не могут иметь body"
            }
            this.body = body
        }

        fun timeout(milliseconds: Long) = apply {
            require(milliseconds > 0) {
                "Timeout должен быть положительным"
            }
            this.timeout = milliseconds
        }

        fun build(): HttpRequest {
            require(url.isNotBlank()) {
                "URL не может быть пустым"
            }

            return HttpRequest(
                url = url,
                method = method,
                headers = headers.toMap(),
                body = body,
                timeout = timeout
            )
        }
    }
}

// Использование
val request = HttpRequest.Builder("https://api.example.com/users")
    .method("POST")
    .addHeader("Content-Type", "application/json")
    .addHeader("Authorization", "Bearer token")
    .body("""{"name": "John"}""")
    .timeout(60_000)
    .build()
```

### Лучшие практики

```kotlin
// DO: Используйте приватный конструктор
class Product private constructor(
    val param1: String,
    val param2: Int
) {
    class Builder { /* ... */ }
}

// DO: Возвращайте builder из setter методов (fluent интерфейс)
fun param1(value: String) = apply { this.param1 = value }

// DO: Валидируйте в методе build()
fun build(): Product {
    require(param1.isNotBlank()) { "param1 обязателен" }
    return Product(param1, param2)
}

// DO: Используйте вложенный класс Builder
class Product {
    class Builder { /* ... */ }
}

// DON'T: Не используйте builder для простых data классов
// Предпочитайте именованные параметры Kotlin

// DON'T: Не забывайте валидацию
// Build должен валидировать перед созданием объекта
```

### Когда использовать Builder

**Используйте Builder когда:**
- Объект имеет много необязательных параметров
- Нужна сложная логика валидации
- Требуется условное создание объектов
- Нужны множественные варианты сборки
- Порядок установки параметров важен

**Не используйте Builder когда:**
- Объект прост и имеет мало параметров
- Kotlin именованные параметры достаточны
- Нет необходимости в валидации или условной логике


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Creational Patterns
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern
- [[q-abstract-factory-pattern--design-patterns--medium]] - Abstract Factory pattern
- [[q-prototype-pattern--design-patterns--medium]] - Prototype pattern

### Structural Patterns
- [[q-adapter-pattern--design-patterns--medium]] - Adapter pattern

### Behavioral Patterns
- [[q-strategy-pattern--design-patterns--medium]] - Strategy pattern

