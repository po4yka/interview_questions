---
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
related: [c-kotlin-features, c-kotlin]
created: 2025-10-15
updated: 2025-11-10
tags: [code-generation, data-classes, difficulty/easy, kotlin]
---
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

**Автоматическая генерация функций:**
- `equals()` - сравнение объектов по содержимому
- `hashCode()` - хеш-код для использования в коллекциях
- `toString()` - строковое представление объекта
- `componentN()` - деструктуризация объектов
- `copy()` - создание копии с изменением отдельных полей

```kotlin
val user1 = User("Alice", 30)
val user2 = user1.copy(age = 31)  // Создаём копию с другим возрастом

// Деструктуризация
val (name, age) = user1
println("$name is $age years old")
```

### Использование

- Сокращает количество шаблонного кода
- Упрощает создание моделей данных
- Повышает читабельность кода
- Обеспечивает корректную работу с коллекциями (благодаря `equals()`/`hashCode()`)

## Answer (EN)

Data classes in Kotlin are designed for holding data. Their main purpose is to simplify creating classes primarily used to store data without extra boilerplate code.

To declare a data class, add the `data` keyword before the class declaration:

```kotlin
data class User(val name: String, val age: Int)
```

### Features and Benefits

**Automatically generated functions:**
- `equals()` - compares objects by content
- `hashCode()` - generates hash for use in collections
- `toString()` - string representation of the object
- `componentN()` - enables destructuring declarations
- `copy()` - creates a copy with modified fields

```kotlin
val user1 = User("Alice", 30)
val user2 = user1.copy(age = 31)  // Create a copy with different age

// Destructuring
val (name, age) = user1
println("$name is $age years old")
```

### Usage

- Reduces boilerplate code
- Simplifies creation of data models
- Improves code readability
- Ensures correct behavior in collections (thanks to `equals()`/`hashCode()`)

## Дополнительные вопросы

- В чем ключевые отличия от Java-классов с ручной реализацией методов?
- Когда вы бы использовали `data class` на практике?
- Какие распространенные ошибки и подводные камни следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-structured-concurrency-kotlin--kotlin--medium]]
- [[q-kotlin-lateinit--programming-languages--medium]]

## Related Questions

- [[q-structured-concurrency-kotlin--kotlin--medium]]
- [[q-kotlin-lateinit--programming-languages--medium]]
