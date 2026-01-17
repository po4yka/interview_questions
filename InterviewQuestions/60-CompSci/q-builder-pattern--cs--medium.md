---
id: cs-015
title: Builder Pattern / Builder Паттерн
aliases:
- Builder Pattern
- Паттерн Builder
topic: cs
subtopics:
- builder
- creational-patterns
- design-patterns
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-cs
related:
- c-builder-pattern
- c-dao-pattern
- q-factory-method-pattern--cs--medium
created: 2025-10-15
updated: 2025-11-11
tags:
- builder
- creational-patterns
- design-patterns
- difficulty/medium
- gof-patterns
sources:
- https://refactoring.guru/design-patterns/builder
anki_cards:
- slug: cs-015-0-en
  language: en
  anki_id: 1768454033488
  synced_at: '2026-01-15T09:41:02.822862'
- slug: cs-015-0-ru
  language: ru
  anki_id: 1768454033513
  synced_at: '2026-01-15T09:41:02.825447'
---
# Вопрос (RU)
> Что такое паттерн Builder? Когда его использовать и как он решает проблему телескопических конструкторов?

# Question (EN)
> What is the Builder pattern? When should it be used and how does it solve the telescoping constructor problem?

---

## Ответ (RU)

**Теория Builder:**
Builder — порождающий паттерн, который позволяет конструировать сложные объекты пошагово (step-by-step). Он отделяет процесс построения объекта от его конечного представления, что позволяет использовать один и тот же код конструирования для создания разных вариантов (представлений) объекта. В прикладном коде (как в примере ниже) часто используется упрощённый "fluent builder" для решения проблемы телескопических конструкторов.

**Проблема телескопических конструкторов:**
Создание множества перегруженных конструкторов с увеличивающимся числом аргументов. Добавление нового поля требует модификации каждого конструктора. Сложно читать, легко ошибиться, трудно поддерживать.

**Решение:**
Инкапсулировать создание и сборку частей сложного объекта в отдельном объекте Builder. Клиентский код вызывает цепочку методов Builder вместо множества конструкторов. Возможны разные реализации Builder для формирования различных представлений одного и того же объекта.

**Применение (флюент-Builder для неизменяемого объекта):**
```kotlin
// ✅ Builder Pattern (fluent builder для решения телескопических конструкторов)
class FoodOrder private constructor(
    val bread: String,
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

        fun build(): FoodOrder {
            // Здесь можно добавить валидацию и значения по умолчанию
            return FoodOrder(
                bread = bread ?: "Flat bread",
                condiments = condiments,
                meat = meat,
                fish = fish
            )
        }
    }
}

// ✅ Использование
val order = FoodOrder.Builder()
    .bread("white bread")
    .meat("bacon")
    .condiments("olive oil")
    .build()
```

**Android применение:**
```kotlin
// ✅ Notification Builder (классический пример Builder-подхода)
// На практике чаще используется NotificationCompat.Builder из AndroidX
val notification = NotificationCompat.Builder(context, "channelId")
    .setContentTitle("Title")
    .setContentText("Content")
    .setSmallIcon(R.drawable.icon)
    .build()
```

**Альтернатива в Kotlin — именованные параметры и значения по умолчанию:**
```kotlin
// ✅ Для простых случаев это часто предпочтительнее, чем вручную писать Builder
data class User(
    val firstName: String,
    val lastName: String = "",
    val age: Int = 0,
    val email: String? = null
)

val user = User(
    firstName = "John",
    email = "john@example.com"
)
```
Именованные аргументы и значения по умолчанию хорошо решают проблему читаемости и множества необязательных параметров, но не заменяют Builder там, где нужна сложная пошаговая сборка, валидация или несколько вариантов представления.

**Преимущества:**
- Избегает телескопических конструкторов
- Инкапсулирует логику конструирования (включая валидацию и значения по умолчанию)
- Fluent-интерфейс улучшает читаемость
- Даёт контроль над шагами конструирования
- Позволяет иметь разные реализации Builder для разных представлений объекта

**Недостатки:**
- Обычно требует дополнительного Builder-класса (больше кода)
- Может быть избыточен для простых объектов
- Часто реализуется через изменяемый Builder (что нормально), хотя возможны и неизменяемые реализации

**Когда использовать:**
- Много необязательных параметров
- Сложная логика валидации и/или зависимые параметры
- Условное создание или пошаговая конфигурация объекта
- Несколько вариантов сборки / представлений одного и того же объекта

**Не использовать когда:**
- Простой объект с малым числом параметров
- Именованные параметры и значения по умолчанию в Kotlin уже достаточно решают задачу

---

## Answer (EN)

**Builder Theory:**
Builder is a creational design pattern that allows constructing complex objects step by step. It separates the construction process from the final representation so that the same construction code can create different representations of an object. In practical Kotlin/OO code (as in the example below), a common variant is the fluent builder used primarily to solve the telescoping constructor problem.

**Telescoping Constructor Problem:**
You end up with many overloaded constructors with an increasing number of arguments. Adding a new field requires updating multiple constructors, the API becomes hard to read, error-prone, and difficult to maintain.

**Solution:**
Encapsulate the creation and assembly of a complex object inside a separate Builder object. Client code calls a chain of builder methods instead of dealing with multiple constructors. Different Builder implementations can be used to produce different representations or configurations of the same product.

**`Application` (fluent Builder for an immutable object):**
```kotlin
// ✅ Builder Pattern (fluent builder addressing telescoping constructors)
class FoodOrder private constructor(
    val bread: String,
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

        fun build(): FoodOrder {
            // Validation and defaults can be applied here
            return FoodOrder(
                bread = bread ?: "Flat bread",
                condiments = condiments,
                meat = meat,
                fish = fish
            )
        }
    }
}

// ✅ Usage
val order = FoodOrder.Builder()
    .bread("white bread")
    .meat("bacon")
    .condiments("olive oil")
    .build()
```

**Android `Application`:**
```kotlin
// ✅ Notification Builder (classic Builder-style API)
// In modern apps, NotificationCompat.Builder from AndroidX is typically preferred for compatibility
val notification = NotificationCompat.Builder(context, "channelId")
    .setContentTitle("Title")
    .setContentText("Content")
    .setSmallIcon(R.drawable.icon)
    .build()
```

**Kotlin Alternative — Named Parameters and Default Values:**
```kotlin
// ✅ For simple cases, this is often preferable to writing a custom Builder
data class User(
    val firstName: String,
    val lastName: String = "",
    val age: Int = 0,
    val email: String? = null
)

val user = User(
    firstName = "John",
    email = "john@example.com"
)
```
Named arguments and default values address readability and optional parameters well, but they do not replace Builder when you need complex stepwise construction, validation, or multiple product variants.

**Advantages:**
- Avoids telescoping constructors
- Encapsulates construction logic (including validation and defaults)
- Fluent interface improves readability
- Gives control over construction steps
- Allows different Builder implementations for different representations/configurations

**Disadvantages:**
- Requires additional Builder classes/logic (more code)
- Can be overkill for simple objects
- Often implemented with a mutable Builder (which is fine), though immutable builder implementations are also possible

**When to use:**
- Many optional parameters
- Complex validation logic and/or interdependent parameters
- Conditional or stepwise object construction
- Multiple build variants/representations of the same product

**When not to use:**
- Simple objects with few parameters
- Kotlin named parameters and default values already solve the problem sufficiently

## Follow-ups

- Builder vs Factory Method pattern?
- Kotlin DSL vs Builder pattern?
- Immutable objects with Builder?

## References

- [[c-design-patterns]]
- https://refactoring.guru/design-patterns/builder

## Related Questions

### Related (Medium)
- [[q-template-method-pattern--cs--medium]] - Factory Method pattern
