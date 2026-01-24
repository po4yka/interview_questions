---
id: kotlin-034
title: Destructuring Declarations / Деструктурирующие объявления
aliases:
- Destructuring Declarations
- Деструктурирующие объявления
topic: kotlin
subtopics:
- componentN
- data-classes
- destructuring
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-data-class-detailed--kotlin--medium
- q-data-class-purpose--kotlin--easy
created: 2025-10-05
updated: 2025-11-10
tags:
- componentN
- data-classes
- destructuring
- difficulty/medium
- kotlin
anki_cards:
- slug: kotlin-034-0-en
  language: en
  anki_id: 1768326294981
  synced_at: '2026-01-23T17:03:51.658650'
- slug: kotlin-034-0-ru
  language: ru
  anki_id: 1768326295007
  synced_at: '2026-01-23T17:03:51.659475'
---
# Вопрос (RU)
> Что такое деструктурирующие объявления в Kotlin?

---

# Question (EN)
> What are destructuring declarations in Kotlin?

## Ответ (RU)

Деструктурирующие объявления — это техника распаковки экземпляра класса в отдельные переменные. Можно взять объект и создать отдельные переменные из его свойств одной строкой кода.

### Базовый Пример

```kotlin
data class Book(val author: String, val title: String, val year: Int)

val book = Book("Roberto Bolano", "2666", 2004)
val (author, title, year) = book  // Деструктуризация

if (year > 2016) {
    println("$title by $author")
}
```

### Возврат Нескольких Значений

```kotlin
data class Result(val result: Int, val status: Status)

fun function(...): Result {
    return Result(result, status)
}

val (result, status) = function(...)
```

### Обход `Map`

```kotlin
for ((key, value) in map) {
   // действия с ключом и значением
}
```

### Подчеркивание Для Неиспользуемых Переменных

```kotlin
val (_, status) = getResult()  // Игнорируем первый компонент
```

### Деструктуризация В Лямбдах

```kotlin
// Пример с Map.Entry
map.mapValues { (key, value) -> "$value!" }  // key и value получены через деструктуризацию

// С подчёркиванием для пропуска
map.mapValues { (_, value) -> "$value!" }
```

### Как Это Работает: Функции componentN

```kotlin
data class Person(val name: String, val age: Int)

val person = Person("Alice", 25)
val (name, age) = person

// Компилируется в:
val name = person.component1()
val age = person.component2()
```

Data классы автоматически генерируют `component1()`, `component2()` и т.д. для всех свойств.

### Пользовательская Деструктуризация

```kotlin
class MyClass(val a: String, val b: Int) {
    operator fun component1() = a
    operator fun component2() = b
}

val (a, b) = MyClass("test", 42)  // Работает!
```

### Случаи Использования

1. **Возврат нескольких значений из функций**
2. **Итерация по коллекциям со структурированными данными**
3. **Работа с Pair и Triple**
4. **Извлечение значений из data классов**

**Краткое содержание**: Деструктурирующие объявления позволяют распаковывать объекты в отдельные переменные одной строкой. Работает с data классами, Pair/Triple и любым классом с операторными функциями `componentN()`. Можно использовать в объявлениях переменных, циклах `for` и параметрах лямбд. Используйте подчеркивание для пропуска ненужных компонентов.

См. также: [[c-kotlin]].

---

## Answer (EN)

Destructuring declarations are a technique for unpacking a class instance into separate variables. You can take an object and create standalone variables from its properties with just a single line of code.

### Basic Example

```kotlin
data class Book(val author: String, val title: String, val year: Int)

val book = Book("Roberto Bolano", "2666", 2004)
val (author, title, year) = book  // Destructuring

if (year > 2016) {
    println("$title by $author")
}
```

### Returning Multiple Values

```kotlin
data class Result(val result: Int, val status: Status)

fun function(...): Result {
    // computations
    return Result(result, status)
}

// Destructuring the return value
val (result, status) = function(...)
```

### Traversing a `Map`

```kotlin
for ((key, value) in map) {
   // do something with the key and the value
}
```

### Underscore for Unused Variables

```kotlin
val (_, status) = getResult()  // Ignore first component
```

### Destructuring in Lambdas

```kotlin
// Using destructuring with Map.Entry
map.mapValues { (key, value) -> "$value!" }  // key and value destructured from entry

// With underscore to skip unused components
map.mapValues { (_, value) -> "$value!" }
```

### How it Works: componentN Functions

Destructuring works by calling `componentN()` functions:

```kotlin
data class Person(val name: String, val age: Int)

val person = Person("Alice", 25)
val (name, age) = person

// Compiled to:
val name = person.component1()
val age = person.component2()
```

Data classes automatically generate `component1()`, `component2()`, etc. for their properties.

### Custom Destructuring

```kotlin
class MyClass(val a: String, val b: Int) {
    operator fun component1() = a
    operator fun component2() = b
}

val (a, b) = MyClass("test", 42)  // Works!
```

### Use Cases

1. **Returning multiple values from functions**
2. **Iterating over collections with structured data**
3. **Working with Pair and Triple**
4. **Extracting values from data classes**

**English Summary**: Destructuring declarations allow unpacking objects into separate variables in one line. Works with data classes, Pair/Triple, and any class with `componentN()` operator functions. Can be used in variable declarations, for loops, and lambda parameters. Use underscore to skip unwanted components.

See also: [[c-kotlin]].

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого механизма от Java?
- Когда вы бы использовали деструктуризацию на практике?
- Какие распространенные подводные камни стоит учитывать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)
- [Destructuring Declarations - Документация Kotlin](https://kotlinlang.org/docs/destructuring-declarations.html)
- [Kotlin Destructuring Declarations](https://www.kotlindevelopment.com/destructuring-declarations/)

## References
- [Destructuring Declarations - Kotlin Documentation](https://kotlinlang.org/docs/destructuring-declarations.html)
- [Kotlin Destructuring Declarations](https://www.kotlindevelopment.com/destructuring-declarations/)

## Связанные Вопросы (RU)

### Связанные (Medium)
- [[q-infix-functions--kotlin--medium]] - Infix

## Related Questions

### Related (Medium)
- [[q-infix-functions--kotlin--medium]] - Infix
