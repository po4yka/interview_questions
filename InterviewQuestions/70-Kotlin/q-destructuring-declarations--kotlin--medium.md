---
id: 20251005-235004
title: "Destructuring Declarations / Деструктурирующие объявления"
aliases: []

# Classification
topic: kotlin
subtopics: [destructuring, data-classes, componentN, syntax]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-data-class-purpose--kotlin--easy]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, destructuring, data-classes, componentN, difficulty/medium]
---
# Question (EN)
> What are destructuring declarations in Kotlin?
# Вопрос (RU)
> Что такое деструктурирующие объявления в Kotlin?

---

## Answer (EN)

Destructuring declarations is a technique for unpacking a class instance into separate variables. You can take an object and create standalone variables from its class variables with just a single line of code.

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

### Traversing a Map

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
// For Pair
map.mapValues { entry -> "${entry.value}!" }
map.mapValues { (key, value) -> "$value!" }  // Destructured

// Difference between parameters
{ a -> ... }           // one parameter
{ a, b -> ... }        // two parameters
{ (a, b) -> ... }      // a destructured pair
{ (a, b), c -> ... }   // a destructured pair and another parameter

// With underscore
map.mapValues { (_, value) -> "$value!" }

// With types
map.mapValues { (_, value): Map.Entry<Int, String> -> "$value!" }
map.mapValues { (_, value: String) -> "$value!" }
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

Data classes automatically generate `component1()`, `component2()`, etc. for all properties.

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
5. **Pattern matching with when expressions**

**English Summary**: Destructuring declarations allow unpacking objects into separate variables in one line. Works with data classes, Pair/Triple, and any class with componentN() operator functions. Can be used in variable declarations, for loops, and lambda parameters. Use underscore to skip unwanted components.

## Ответ (RU)

Деструктурирующие объявления — это техника распаковки экземпляра класса в отдельные переменные. Можно взять объект и создать отдельные переменные из его свойств одной строкой кода.

### Базовый пример

```kotlin
data class Book(val author: String, val title: String, val year: Int)

val book = Book("Roberto Bolano", "2666", 2004)
val (author, title, year) = book  // Деструктуризация

if (year > 2016) {
    println("$title by $author")
}
```

### Возврат нескольких значений

```kotlin
data class Result(val result: Int, val status: Status)

fun function(...): Result {
    return Result(result, status)
}

val (result, status) = function(...)
```

### Обход Map

```kotlin
for ((key, value) in map) {
   // действия с ключом и значением
}
```

### Подчеркивание для неиспользуемых переменных

```kotlin
val (_, status) = getResult()  // Игнорируем первый компонент
```

### Как это работает: функции componentN

```kotlin
data class Person(val name: String, val age: Int)

val (name, age) = Person("Alice", 25)

// Компилируется в:
val name = person.component1()
val age = person.component2()
```

Data классы автоматически генерируют `component1()`, `component2()` и т.д. для всех свойств.

### Случаи использования

1. **Возврат нескольких значений из функций**
2. **Итерация по коллекциям со структурированными данными**
3. **Работа с Pair и Triple**
4. **Извлечение значений из data классов**

**Краткое содержание**: Деструктурирующие объявления позволяют распаковывать объекты в отдельные переменные одной строкой. Работает с data классами, Pair/Triple и любым классом с операторными функциями componentN(). Можно использовать в объявлениях переменных, циклах for и параметрах лямбд. Используйте подчеркивание для пропуска ненужных компонентов.

---

## References
- [Destructuring Declarations - Kotlin Documentation](https://kotlinlang.org/docs/reference/multi-declarations.html)
- [Kotlin Destructuring Declarations](https://www.kotlindevelopment.com/destructuring-declarations/)

## Related Questions
- [[q-data-class-purpose--kotlin--easy]]
