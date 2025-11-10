---
id: kotlin-190
title: "Kotlin When Expression / Выражение when в Kotlin"
aliases: [Pattern Matching, When Expression, When Statement, When Выражение]
topic: kotlin
subtopics: [control-flow, syntax]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-coroutine-cancellation-mechanisms--kotlin--medium, q-reified-type-parameters--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [control-flow, difficulty/easy, kotlin, pattern-matching, syntax, when]
---
# Вопрос (RU)
> Как использовать `when` в Kotlin вместо `switch`?

---

# Question (EN)
> How to use `when` in Kotlin instead of `switch`?

## Ответ (RU)

`when` в Kotlin заменяет `switch` из Java и является **намного более мощным**.

**Базовый синтаксис:**
```kotlin
fun getDayName(day: Int): String {
    return when (day) {
        1 -> "Понедельник"
        2 -> "Вторник"
        3 -> "Среда"
        4 -> "Четверг"
        5 -> "Пятница"
        6 -> "Суббота"
        7 -> "Воскресенье"
        else -> "Неверный день"
    }
}
```

**Несколько значений на ветку:**
```kotlin
when (x) {
    1, 2 -> println("x это 1 или 2")
    in 3..10 -> println("x между 3 и 10")
    !in 10..20 -> println("x вне диапазона 10-20")
    else -> println("Иначе")
}
```

**Без аргумента (заменяет цепочки if-else):**
```kotlin
when {
    x < 0 -> println("Отрицательное")
    x == 0 -> println("Ноль")
    x > 0 -> println("Положительное")
}
```

**Проверка типа:**
```kotlin
fun describe(obj: Any): String = when (obj) {
    is String -> "String длиной ${obj.length}"
    is Int -> "Int со значением $obj"
    is List<*> -> "List размера ${obj.size}"
    else -> "Неизвестный тип"
}
```

**Sealed классы (исчерпывающая проверка):**
```kotlin
sealed class Result
class Success(val data: String) : Result()
class Error(val message: String) : Result()

fun handle(result: Result) = when (result) {
    is Success -> println(result.data)
    is Error -> println(result.message)
    // 'else' не нужен - компилятор знает все случаи!
}
```

**Как выражение:**
```kotlin
val result = when (val x = getValue()) {
    1 -> "Один"
    2 -> "Два"
    else -> "Другое: $x"
}
```

**Преимущества над switch:**
- Может использоваться как выражение
- Нет fall-through (`break` не нужен)
- Может проверять любое условие, не только константы
- Поддерживает диапазоны и проверки типов
- Исчерпывающая проверка с sealed классами

См. также: [[c-kotlin]]

## Answer (EN)

`when` in Kotlin replaces Java's `switch` statement and is **much more powerful**.

**Basic syntax:**
```kotlin
fun getDayName(day: Int): String {
    return when (day) {
        1 -> "Monday"
        2 -> "Tuesday"
        3 -> "Wednesday"
        4 -> "Thursday"
        5 -> "Friday"
        6 -> "Saturday"
        7 -> "Sunday"
        else -> "Invalid day"
    }
}
```

**Multiple values per branch:**
```kotlin
when (x) {
    1, 2 -> println("x is 1 or 2")
    in 3..10 -> println("x is between 3 and 10")
    !in 10..20 -> println("x is outside 10-20")
    else -> println("Otherwise")
}
```

**Without argument (replaces if-else chains):**
```kotlin
when {
    x < 0 -> println("Negative")
    x == 0 -> println("Zero")
    x > 0 -> println("Positive")
}
```

**Type checking:**
```kotlin
fun describe(obj: Any): String = when (obj) {
    is String -> "String of length ${obj.length}"
    is Int -> "Int with value $obj"
    is List<*> -> "List of size ${obj.size}"
    else -> "Unknown type"
}
```

**Sealed classes (exhaustive):**
```kotlin
sealed class Result
class Success(val data: String) : Result()
class Error(val message: String) : Result()

fun handle(result: Result) = when (result) {
    is Success -> println(result.data)
    is Error -> println(result.message)
    // No 'else' needed - compiler knows all cases!
}
```

**As expression:**
```kotlin
val result = when (val x = getValue()) {
    1 -> "One"
    2 -> "Two"
    else -> "Other: $x"
}
```

**Advantages over switch:**
- Can be used as expression
- No fall-through (no `break` needed)
- Can check any condition, not just constants
- Supports ranges and type checks
- Exhaustive checking with sealed classes

---

## Последующие вопросы (RU)

- В чем ключевые отличия `when` от `switch` в Java?
- В каких практических случаях вы бы использовали `when`?
- Какие типичные ошибки при использовании `when` стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-reified-type-parameters--kotlin--medium]]
- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]

## Related Questions

- [[q-reified-type-parameters--kotlin--medium]]
- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
