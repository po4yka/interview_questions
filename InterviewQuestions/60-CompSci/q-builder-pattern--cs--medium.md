---
id: cs-015
title: "Builder Pattern / Builder Паттерн"
aliases: ["Builder Pattern", "Паттерн Builder"]
topic: cs
subtopics: [builder, creational-patterns, design-patterns]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-factory-method-pattern--design-patterns--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [builder, creational-patterns, design-patterns, difficulty/medium, gof-patterns, kotlin]
sources: [https://refactoring.guru/design-patterns/builder]
date created: Saturday, November 1st 2025, 1:24:17 pm
date modified: Saturday, November 1st 2025, 5:43:28 pm
---

# Вопрос (RU)
> Что такое паттерн Builder? Когда его использовать и как он решает проблему телескопических конструкторов?

# Question (EN)
> What is the Builder pattern? When should it be used and how does it solve the telescoping constructor problem?

---

## Ответ (RU)

**Теория Builder:**
Builder - порождающий паттерн, который позволяет конструировать сложные объекты шаг за шагом. Позволяет создавать различные типы и представления объекта, используя один и тот же код конструирования. Решает проблему телескопических конструкторов и делает создание сложных объектов более гибким.

**Проблема телескопических конструкторов:**
Создание множества вариантов конструктора с увеличивающимся числом аргументов. На практике добавление нового поля требует модификации каждого конструктора. Негибко и трудно поддерживать.

**Решение:**
Инкапсулировать создание и сборку частей сложного объекта в отдельном объекте Builder. Класс делегирует создание объекта объекту Builder вместо прямого создания. Класс может делегировать различным Builder объектам создание различных представлений.

**Применение:**
```kotlin
// ✅ Builder Pattern
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

        fun build() = FoodOrder(
            bread ?: "Flat bread",
            condiments, meat, fish
        )
    }
}

// ✅ Usage
val order = FoodOrder.Builder()
    .bread("white bread")
    .meat("bacon")
    .condiments("olive oil")
    .build()
```

**Android применение:**
```kotlin
// ✅ Notification Builder (классический пример)
val notification = Notification.Builder(context, "channelId")
    .setContentTitle("Title")
    .setContentText("Content")
    .setSmallIcon(R.drawable.icon)
    .build()
```

**Альтернатива в Kotlin - именованные параметры:**
```kotlin
// ✅ Для простых случаев предпочтительнее
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

**Преимущества:**
- Избегает телескопических конструкторов
- Инкапсулирует логику конструирования
- Fluent интерфейс улучшает читаемость
- Контроль над шагами конструирования
- Разделяет представления объекта

**Недостатки:**
- Builder классы должны быть изменяемыми
- Больше кода
- Избыточность для простых объектов

**Когда использовать:**
- Много необязательных параметров
- Сложная логика валидации
- Условное создание объектов
- Множественные варианты сборки

**Не использовать когда:**
- Простой объект с малым числом параметров
- Kotlin именованные параметры достаточны

---

## Answer (EN)

**Builder Theory:**
Builder is a creational design pattern that lets you construct complex objects step by step. Allows you to produce different types and representations of an object using the same construction code. Solves telescoping constructor problem and makes creating complex objects more flexible.

**Telescoping Constructor Problem:**
Creating many constructor variants with increasing number of arguments. In practice, adding a new field requires modifying each constructor. Inflexible and hard to maintain.

**Solution:**
Encapsulate creating and assembling parts of a complex object in a separate Builder object. A class delegates object creation to a Builder object instead of creating objects directly. A class can delegate to different Builder objects to create different representations.

**Application:**
```kotlin
// ✅ Builder Pattern
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

        fun build() = FoodOrder(
            bread ?: "Flat bread",
            condiments, meat, fish
        )
    }
}

// ✅ Usage
val order = FoodOrder.Builder()
    .bread("white bread")
    .meat("bacon")
    .condiments("olive oil")
    .build()
```

**Android Application:**
```kotlin
// ✅ Notification Builder (classic example)
val notification = Notification.Builder(context, "channelId")
    .setContentTitle("Title")
    .setContentText("Content")
    .setSmallIcon(R.drawable.icon)
    .build()
```

**Kotlin Alternative - Named Parameters:**
```kotlin
// ✅ For simple cases, prefer this
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

**Advantages:**
- Avoids telescoping constructors
- Encapsulates construction logic
- Fluent interface improves readability
- Control over construction steps
- Separates object representations

**Disadvantages:**
- Builder classes must be mutable
- More code required
- Overkill for simple objects

**When to use:**
- Many optional parameters
- Complex validation logic
- Conditional object creation
- Multiple build variants

**When not to use:**
- Simple object with few parameters
- Kotlin named parameters sufficient

## Follow-ups

- Builder vs Factory Method pattern?
- Kotlin DSL vs Builder pattern?
- Immutable objects with Builder?

## References

- [[c-design-patterns]]
- https://refactoring.guru/design-patterns/builder

## Related Questions

### Related (Medium)
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern
