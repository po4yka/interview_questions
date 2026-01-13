---
anki_cards:
- slug: q-data-class-purpose--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-data-class-purpose--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: kotlin-228
title: "Data Class Purpose / Назначение data class"
aliases: [Data Class Purpose, Назначение data class]
topic: kotlin
subtopics: [data-classes]
question_kind: theory
difficulty: easy
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features]
created: 2025-10-15
updated: 2025-11-10
tags: [code-generation, data-classes, difficulty/easy, kotlin]
---\
# Вопрос (RU)
> Что такое data class в Kotlin и для чего он нужен?

---

# Question (EN)
> What is a data class in Kotlin and what is it used for?

## Ответ (RU)

Классы данных предназначены для хранения данных. Основная их задача — упростить создание классов, которые будут использоваться преимущественно для хранения данных, не добавляя при этом лишнего шаблонного кода.

Чтобы определить класс данных, достаточно добавить ключевое слово `data` перед объявлением класса:

```kotlin
data class User(val name: String, val age: Int)
```

### Особенности И Преимущества

**Автоматическая генерация функций (по свойствам первичного конструктора):**
- `equals()` — сравнение объектов по содержимому (используются только свойства из первичного конструктора)
- `hashCode()` — хеш-код для использования в коллекциях (основан на свойствах первичного конструктора)
- `toString()` — строковое представление объекта
- `componentN()` — деструктуризация объектов
- `copy()` — создание копии с изменением отдельных полей (учитываются параметры первичного конструктора)

```kotlin
val user1 = User("Alice", 30)
val user2 = user1.copy(age = 31)  // Создаём копию с другим возрастом

// Деструктуризация
val (name, age) = user1
println("$name is $age years old")
```

### Ограничения Data Class

- Должен иметь как минимум один параметр в первичном конструкторе.
- Все параметры, которые должны участвовать в `equals`/`hashCode`/`copy`/`componentN`, должны быть объявлены как `val` или `var` в первичном конструкторе.
- Не может быть `abstract`, `open`, `sealed`, `inner`, `enum` или `annotation` классом.
- Может реализовывать интерфейсы и наследовать от других (обычных) классов, но сам по себе не предназначен для сложной иерархии наследования.

### Использование

- Сокращает количество шаблонного кода.
- Упрощает создание моделей данных и DTO.
- Повышает читабельность кода.
- Обеспечивает предсказуемое поведение при использовании в коллекциях и структурах данных, зависящих от `equals()`/`hashCode()` (например, `Set`, `Map`).

## Answer (EN)

Data classes in Kotlin are designed for holding data. Their main purpose is to simplify creating classes primarily used to store data without extra boilerplate code.

To declare a data class, add the `data` keyword before the class declaration:

```kotlin
data class User(val name: String, val age: Int)
```

### Features and Benefits

**Automatically generated functions (based on primary constructor properties):**
- `equals()` — compares objects by content (only properties from the primary constructor are used)
- `hashCode()` — hash for use in collections (based on primary constructor properties)
- `toString()` — string representation of the object
- `componentN()` — enables destructuring declarations
- `copy()` — creates a copy with modified properties (from the primary constructor)

```kotlin
val user1 = User("Alice", 30)
val user2 = user1.copy(age = 31)  // Create a copy with different age

// Destructuring
val (name, age) = user1
println("$name is $age years old")
```

### Data Class Constraints

- Must have at least one parameter in the primary constructor.
- All parameters that should participate in `equals`/`hashCode`/`copy`/`componentN` must be declared as `val` or `var` in the primary constructor.
- Cannot be `abstract`, `open`, `sealed`, `inner`, `enum`, or `annotation` classes.
- Can implement interfaces and extend other (non-final) classes, but it is primarily intended for simple data holders rather than complex inheritance hierarchies.

### Usage

- Reduces boilerplate code.
- Simplifies creating data models and DTOs.
- Improves code readability.
- `Provides` predictable behavior when used in collections and data structures that rely on `equals()`/`hashCode()` (e.g., `Set`, `Map`).

## Дополнительные Вопросы

- В чем ключевые отличия от Java-классов с ручной реализацией методов?
- Когда вы бы использовали `data class` на практике?
- Какие распространенные ошибки и подводные камни следует избегать (например, свойства вне первичного конструктора, влияние на equals/hashCode)?

## Follow-ups

- What are the key differences between this and Java classes with manually implemented methods?
- When would you use this in practice?
- What are common pitfalls to avoid (e.g., properties declared outside the primary constructor not taking part in equals/hashCode)?

## Ссылки

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-structured-concurrency-kotlin--kotlin--medium]]
- [[q-kotlin-lateinit--kotlin--medium]]

## Related Questions

- [[q-structured-concurrency-kotlin--kotlin--medium]]
- [[q-kotlin-lateinit--kotlin--medium]]
