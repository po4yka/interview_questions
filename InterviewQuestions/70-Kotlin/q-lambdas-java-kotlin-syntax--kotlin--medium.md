---
id: kotlin-139
title: "Lambdas Java Kotlin Syntax / Синтаксис лямбд Java и Kotlin"
aliases: [Functional Programming, Lambda Syntax, Lambdas, Лямбды]
topic: kotlin
subtopics: [functional-programming, lambdas, syntax]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-advanced-coroutine-patterns--kotlin--hard, q-kotlin-immutable-collections--programming-languages--easy, q-kotlin-safe-cast--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium, functional-programming, java, kotlin, lambdas, syntax]
---
# Что Такое Лямбды С Точки Зрения Синтаксиса В Java И Kotlin?

# Вопрос (RU)
> Что такое лямбды с точки зрения синтаксиса в Java и Kotlin?

---

# Question (EN)
> What are lambdas from syntax perspective in Java and Kotlin?

## Ответ (RU)

В Java лямбды — это упрощённый синтаксис для анонимных классов, реализующих функциональный интерфейс. Синтаксис: (параметры) -> { тело }. В Kotlin лямбды представляют собой выражения, передаваемые как функции, с синтаксисом { параметры -> тело }. Kotlin более лаконичен, позволяя опускать параметры, если их можно вывести из контекста.

## Answer (EN)

### Java Lambdas

Lambdas are simplified syntax for anonymous classes implementing **functional interfaces** (interfaces with single abstract method):

**Syntax:** `(parameters) -> { body }`

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

Lambdas are expressions passed as functions, **not limited to single-method interfaces**:

**Syntax:** `{ parameters -> body }`

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

**Key differences:**

| Aspect | Java | Kotlin |
|--------|------|--------|
| Syntax | `(a, b) -> expr` | `{ a, b -> expr }` |
| Requirement | Functional interface | Any function type |
| Single parameter | Must specify | Can use `it` |
| Type inference | Limited | Extensive |
| Trailing lambda | No | Yes (outside parens) |

**Kotlin is more concise** and allows omitting parameters if they can be inferred from context.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-kotlin-immutable-collections--programming-languages--easy]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-kotlin-safe-cast--programming-languages--easy]]
