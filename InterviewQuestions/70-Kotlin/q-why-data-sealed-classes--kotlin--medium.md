---
id: kotlin-226
title: Why Data Sealed Classes / Зачем нужны Data и Sealed классы
aliases:
- Class Design
- Data Classes
- Sealed Classes
- Классы в Kotlin
topic: kotlin
subtopics:
- classes
- data-classes
- sealed-classes
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-fan-in-fan-out--kotlin--hard
- q-kotlin-visibility-modifiers--kotlin--easy
created: 2025-10-15
updated: 2025-11-10
tags:
- classes
- data-classes
- design
- difficulty/medium
- kotlin
- sealed-classes
anki_synced: true
anki_slugs:
- 70-kotlin-q-why-data-sealed-classes-kotlin-medium-p01-ru
anki_last_sync: '2025-11-26T22:32:40.783101'
anki_cards:
- slug: kotlin-226-0-en
  language: en
  anki_id: 1768326295980
  synced_at: '2026-01-23T17:03:51.699105'
- slug: kotlin-226-0-ru
  language: ru
  anki_id: 1768326296006
  synced_at: '2026-01-23T17:03:51.699927'
---
# Вопрос (RU)

> Зачем в Kotlin нужны `data` классы и `sealed` классы?

# Question (EN)

> Why are `data` classes and `sealed` classes needed in Kotlin?

## Ответ (RU)

Data классы и sealed классы служат разным целям в системе типов Kotlin (см. [[c-kotlin]]).

### Data Классы
Автоматически генерируют полезные методы:
```kotlin
data class User(val name: String, val age: Int)
// Авто-генерирует: equals(), hashCode(), toString(), copy(), componentN()

val user = User("Alice", 25)
val older = user.copy(age = 26)
```

**Зачем использовать data классы:**
- Нужно равенство по значению
- Нужна функциональность copy
- Работа с неизменяемыми данными
- Нужна деструктуризация

### Sealed Классы
Ограничивают наследование известными подтипами:
```kotlin
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
}

// Исчерпывающий when
fun handle(result: Result) = when (result) {
    is Result.Success -> show(result.data)
    is Result.Error -> showError(result.message)
    Result.Loading -> showLoading()
    // else не нужен - компилятор знает все случаи
}
```

**Зачем использовать sealed классы:**
- Представить ограниченные иерархии типов
- Исчерпывающие when выражения
- Лучше чем enum, когда состояния имеют данные
- ADTs (Алгебраические типы данных)

## Answer (EN)

Data classes and sealed classes serve different purposes in Kotlin's type system.

### Data Classes
Automatically generate useful methods:
```kotlin
data class User(val name: String, val age: Int)
// Auto-generates: equals(), hashCode(), toString(), copy(), componentN()

val user = User("Alice", 25)
val older = user.copy(age = 26)
```

**Why use data classes:**
- Need value equality
- Need copy functionality
- Working with immutable data
- Need destructuring

### Sealed Classes
Restrict inheritance to known subtypes:
```kotlin
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
}

// Exhaustive when
fun handle(result: Result) = when (result) {
    is Result.Success -> show(result.data)
    is Result.Error -> showError(result.message)
    Result.Loading -> showLoading()
    // No else needed - compiler knows all cases
}
```

**Why use sealed classes:**
- Represent restricted type hierarchies
- Exhaustive when expressions
- Better than enum when states have data
- ADTs (Algebraic Data Types)

## Дополнительные Вопросы (RU)

- Каковы ключевые отличия от Java?
- Когда вы бы использовали это на практике?
- Какие распространенные ошибки стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-kotlin-visibility-modifiers--kotlin--easy]]
- [[q-fan-in-fan-out--kotlin--hard]]

## Related Questions

- [[q-kotlin-visibility-modifiers--kotlin--easy]]
- [[q-fan-in-fan-out--kotlin--hard]]
