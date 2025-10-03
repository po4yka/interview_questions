---
id: 20251003141103
title: Lambdas in Java vs Kotlin / Лямбды в Java и Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, java, lambdas]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/605
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-lambdas
  - c-functional-programming

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, java, lambdas, functional-programming, syntax, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What are lambdas from syntax perspective in Java and Kotlin?

# Вопрос (RU)
> Что такое лямбды с точки зрения синтаксиса в Java и Kotlin?

---

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

## Ответ (RU)

В Java лямбды — это упрощённый синтаксис для анонимных классов, реализующих функциональный интерфейс. Синтаксис: (параметры) -> { тело }. В Kotlin лямбды представляют собой выражения, передаваемые как функции, с синтаксисом { параметры -> тело }. Kotlin более лаконичен, позволяя опускать параметры, если их можно вывести из контекста.

---

## Follow-ups
- What are higher-order functions?
- What is SAM conversion in Kotlin?
- How do closures work?

## References
- [[c-lambdas]]
- [[c-functional-programming]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-sam-conversions--programming-languages--medium]]
