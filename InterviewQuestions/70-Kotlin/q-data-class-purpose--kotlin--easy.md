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
related: [q-prohibit-object-creation--programming-languages--easy, q-structured-concurrency-kotlin--kotlin--medium, q-kotlin-lateinit--programming-languages--medium, q-data-class-detailed--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - kotlin
  - data-classes
  - code-generation
  - difficulty/easy
---
# Для чего нужен data class?

# Question (EN)
> What is a data class in Kotlin and what is it used for?

# Вопрос (RU)
> Что такое data class в Kotlin и для чего он нужен?

---

## Answer (EN)

Data classes in Kotlin are designed for holding data. They automatically generate boilerplate methods that would otherwise need to be manually written:
- `equals()` - compares objects by content
- `hashCode()` - generates hash for collections
- `toString()` - string representation
- `componentN()` - enables destructuring
- `copy()` - creates copy with modified fields

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = user1.copy(age = 31)  // Copy with different age
val (name, age) = user1  // Destructuring
```

Data classes reduce boilerplate code, simplify model creation, improve readability, and ensure correct collection behavior.

## Ответ (RU)

Классы данных предназначены для хранения данных. Основная их задача — упростить создание классов, которые будут использоваться преимущественно для хранения данных, не добавляя при этом лишнего шаблонного кода.

Чтобы определить класс данных, достаточно добавить ключевое слово `data` перед объявлением класса:

```kotlin
data class User(val name: String, val age: Int)
```

### Особенности и преимущества

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
- Обеспечивает корректную работу с коллекциями (благодаря equals/hashCode)

## Related Questions

- [[q-prohibit-object-creation--programming-languages--easy]]
- [[q-structured-concurrency-kotlin--kotlin--medium]]
- [[q-kotlin-lateinit--programming-languages--medium]]
