---
id: kotlin-010
title: Kotlin Enum Classes / Перечисления (Enum) в Kotlin
aliases:
- Kotlin Enum Classes
- Перечисления (Enum) в Kotlin
topic: kotlin
subtopics:
- enums
- types
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-kotlin-features
- q-kotlin-lateinit--kotlin--medium
created: 2025-10-05
updated: 2025-11-09
tags:
- classes
- difficulty/easy
- enums
- kotlin
- types
---
# Вопрос (RU)
> Что такое Enum в Kotlin?

# Question (EN)
> What is an Enum in Kotlin?

## Ответ (RU)

`Enum` в Kotlin — это специальный тип, который представляет группу связанных констант. Он позволяет определить фиксированный набор значений для переменной. Константы enum обычно используются для представления закрытого набора опций или выборов.

Чтобы определить `enum` в Kotlin, вы используете ключевые слова `enum class`, за которыми следует имя перечисления и список значений констант в фигурных скобках. Например:

```kotlin
enum class Color {
    RED, GREEN, BLUE
}
```

В приведенном выше примере перечисление `Color` имеет три константы: `RED`, `GREEN` и `BLUE`.

Перечисления в Kotlin также могут иметь свойства и методы, подобно классам. Каждая константа enum может иметь свои собственные значения для этих свойств. Например:

```kotlin
enum class Color(val rgb: Int) {
    RED(0xFF0000),
    GREEN(0x00FF00),
    BLUE(0x0000FF);

    fun description(): String {
        return when (this) {
            RED -> "Red color"
            GREEN -> "Green color"
            BLUE -> "Blue color"
        }
    }
}
```

В приведенном выше примере перечисление `Color` имеет дополнительное свойство `rgb`, связанное с каждой константой. Оно также имеет метод `description()`, который предоставляет текстовое описание каждого цвета.

Чтобы получить доступ к свойствам и методам константы enum, вы просто используете точечную нотацию. Например:

```kotlin
val redColor = Color.RED
println(redColor.rgb)           // Вывод: 16711680
println(redColor.description()) // Вывод: Red color
```

Перечисления в Kotlin могут быть полезны в различных сценариях, таких как представление дней недели, опций меню, кодов состояния и многого другого. Они обеспечивают типобезопасный и лаконичный способ определения фиксированного набора значений.

См. также: [[c-kotlin]], [[c-kotlin-features]]

## Дополнительные Вопросы (RU)

- В чем ключевые отличия между этим и Java?
- Когда вы бы использовали это на практике?
- Какие распространенные подводные камни нужно избегать?

## Ссылки (RU)

- [Kotlin Enum Classes](https://kotlinlang.org/docs/enum-classes.html)
- [Enums in Kotlin](https://www.baeldung.com/kotlin/enum)

## Связанные Вопросы (RU)

### Продвинутое (сложнее)
- [[q-value-classes-inline-classes--kotlin--medium]] - Классы
- [[q-inner-nested-classes--kotlin--medium]] - Классы
- [[q-enum-class-advanced--kotlin--medium]] - Классы

---

## Answer (EN)

An `enum` in Kotlin is a special type that represents a group of related constants. It allows you to define a fixed set of values for a variable. Enum constants are typically used to represent a closed set of options or choices.

To define an `enum` in Kotlin, you use the `enum class` keyword, followed by the name of the enum and the list of constant values inside curly braces. For example:

```kotlin
enum class Color {
    RED, GREEN, BLUE
}
```

In the above example, the `Color` enum has three constants: `RED`, `GREEN`, and `BLUE`.

Enums in Kotlin can also have properties and methods, similar to classes. Each enum constant can have its own values for these properties. For example:

```kotlin
enum class Color(val rgb: Int) {
    RED(0xFF0000),
    GREEN(0x00FF00),
    BLUE(0x0000FF);

    fun description(): String {
        return when (this) {
            RED -> "Red color"
            GREEN -> "Green color"
            BLUE -> "Blue color"
        }
    }
}
```

In the above example, the `Color` enum has an additional property `rgb` associated with each constant. It also has a method `description()` that provides a textual description of each color.

To access the properties and methods of an enum constant, you simply use dot notation. For example:

```kotlin
val redColor = Color.RED
println(redColor.rgb)           // Output: 16711680
println(redColor.description()) // Output: Red color
```

Enums in Kotlin can be useful in various scenarios, such as representing days of the week, menu options, status codes, and more. They provide a type-safe and concise way to define a fixed set of values.

See also: [[c-kotlin]], [[c-kotlin-features]]

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Kotlin Enum Classes](https://kotlinlang.org/docs/enum-classes.html)
- [Enums in Kotlin](https://www.baeldung.com/kotlin/enum)

## Related Questions

### Advanced (Harder)
- [[q-value-classes-inline-classes--kotlin--medium]] - Classes
- [[q-inner-nested-classes--kotlin--medium]] - Classes
- [[q-enum-class-advanced--kotlin--medium]] - Classes
