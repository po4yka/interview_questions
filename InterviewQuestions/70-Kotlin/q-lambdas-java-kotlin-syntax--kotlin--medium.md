---
id: kotlin-139
title: "Lambdas Java Kotlin Syntax / Синтаксис лямбд Java и Kotlin"
aliases: [Functional Programming, Lambda Syntax, Lambdas]
topic: kotlin
subtopics: [lambdas, syntax, functions]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: ready
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features, q-advanced-coroutine-patterns--kotlin--hard]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, functional-programming, java, kotlin, lambdas, syntax]
---
# Вопрос (RU)
> Что такое лямбды с точки зрения синтаксиса в Java и Kotlin?

## Ответ (RU)

### Лямбды в Java

В Java лямбды — это синтаксический сахар для реализации функциональных интерфейсов (интерфейсов с одним абстрактным методом, SAM). Записываются как `(параметры) -> выражение` или `(параметры) -> { операторы }`. На уровне спецификации они не объявляют анонимный класс напрямую, а компилируются через `invokedynamic`, но логически заменяют анонимные классы, реализующие функциональный интерфейс. Это также значит, что у лямбд иные семантики идентичности и сериализации по сравнению с анонимными классами.

```java
// Функциональный интерфейс
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
}

// Использование лямбда-выражений
Calculator add = (a, b) -> a + b;
Calculator multiply = (a, b) -> { return a * b; };

// Со stream API
list.stream()
    .filter(x -> x > 0)
    .map(x -> x * 2)
    .collect(Collectors.toList());
```

### Лямбды в Kotlin

В Kotlin лямбды — это функциональные литералы: выражения вида `{ параметры -> тело }`, значения типов функций, которые можно передавать как аргументы, возвращать из функций и сохранять в переменные. Kotlin поддерживает нативные типы функций (без обязательных интерфейсов), мощный вывод типов, trailing-lambda-синтаксис и неявный параметр `it` для лямбд с одним параметром.

```kotlin
// Лямбда как переменная
val add: (Int, Int) -> Int = { a, b -> a + b }
val multiply = { a: Int, b: Int -> a * b }

// Неявный параметр 'it' для одного параметра
val double: (Int) -> Int = { it * 2 }

// Работа с коллекциями
list.filter { it > 0 }
    .map { it * 2 }
```

### Ключевые отличия

- Синтаксис:
  - Java: `(a, b) -> expr` или `(a, b) -> { ... }`.
  - Kotlin: `{ a, b -> expr }` или `{ a, b -> ... }`.
- Требования:
  - Java: только функциональные интерфейсы (SAM).
  - Kotlin: нативные типы функций, SAM не обязателен.
- Один параметр:
  - Java: параметр всегда явно указывается.
  - Kotlin: можно использовать неявный параметр `it`.
- Вывод типов:
  - Java: более ограниченный.
  - Kotlin: более мощный вывод типов.
- Trailing lambda:
  - Java: нет специального синтаксиса.
  - Kotlin: есть специальный синтаксис — лямбда может быть вынесена за скобки.

# Question (EN)
> What are lambdas from syntax perspective in Java and Kotlin?

## Answer (EN)

### Java Lambdas

Lambdas provide a concise syntax for providing implementations of functional interfaces (single abstract method interfaces, SAM). They are written as `(parameters) -> expression` or `(parameters) -> { statements }`.

Conceptually, they replace boilerplate of anonymous classes implementing a functional interface, but under the hood they are implemented via `invokedynamic` and are not simply anonymous inner classes (e.g., different identity/serialization semantics).

```java
// Functional interface
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
}

// Lambda usage
Calculator add = (a, b) -> a + b;
Calculator multiply = (a, b) -> { return a * b; };

// With streams
list.stream()
    .filter(x -> x > 0)
    .map(x -> x * 2)
    .collect(Collectors.toList());
```

### Kotlin Lambdas

Kotlin lambdas are function literals: `{ parameters -> body }` expressions that are values of function types, not limited to single-method interfaces.

```kotlin
// Lambda as variable
val add: (Int, Int) -> Int = { a, b -> a + b }
val multiply = { a: Int, b: Int -> a * b }

// Implicit 'it' for single parameter
val double: (Int) -> Int = { it * 2 }

// With collections
list.filter { it > 0 }
    .map { it * 2 }
```

Key differences:

- Syntax:
  - Java: `(a, b) -> expr` or `(a, b) -> { ... }`.
  - Kotlin: `{ a, b -> expr }` or `{ a, b -> ... }`.
- Requirement:
  - Java: only functional interfaces (SAM).
  - Kotlin: native function types, SAM not required.
- Single parameter:
  - Java: parameter must be declared explicitly.
  - Kotlin: can use implicit `it`.
- Type inference:
  - Java: more limited.
  - Kotlin: more powerful type inference.
- Trailing lambda:
  - Java: no special syntax.
  - Kotlin: has trailing lambda syntax (lambda can be moved outside parentheses).

---

## Дополнительные вопросы (RU)

- Каковы ключевые отличия между синтаксисом и семантикой лямбд в Java и Kotlin?
- Когда на практике использовать лямбды в Kotlin по сравнению с Java?
- Какие распространенные подводные камни при работе с лямбдами (например, захват переменных, различие между SAM и типами функций)?

## Follow-ups

- What are the key differences between Java and Kotlin lambda syntax and semantics?
- When would you use lambdas in practice in Kotlin vs Java?
- What are common pitfalls to avoid (e.g., capturing variables, SAM vs function types)?

## Ссылки (RU)

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-advanced-coroutine-patterns--kotlin--hard]]

## Related Questions

- [[q-advanced-coroutine-patterns--kotlin--hard]]
