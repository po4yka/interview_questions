---
anki_cards:
- slug: q-kotlin-reference-equality-operator--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-kotlin-reference-equality-operator--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---id: lang-048
title: "Kotlin Reference Equality Operator / Оператор ссылочного равенства в Kotlin"
aliases: [Kotlin Reference Equality Operator, Оператор ссылочного равенства в Kotlin]
topic: kotlin
subtopics: [operators, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-equality, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml, q-data-class-detailed--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/easy, equality, operators, programming-languages, reference-equality, structural-equality]
---
# Вопрос (RU)
> Какой оператор используется для проверки равенства ссылок в Kotlin?

---

# Question (EN)
> Which operator is used to check reference equality in Kotlin?

## Ответ (RU)

В Kotlin для проверки **ссылочного равенства** используется оператор **`===`** (также называемого референтным равенством). Он проверяет, указывают ли две переменные на один и тот же объект в памяти.

См. также: [[c-kotlin]], [[c-equality]]

**Сравнение: `==` vs `===`**

```kotlin
val a = "Hello"
val b = "Hello"
val c = a

// Структурное равенство (==) - проверяет содержимое (null-safe вызов equals)
a == b   // true (одинаковое содержимое)

// Референтное равенство (===) - проверяет, один ли это объект
// Важно: результат a === b не гарантирован спецификацией Kotlin и зависит от платформы/реализации
a === b  // может быть true или false

a === c  // true (c ссылается на a)

val d = String(charArrayOf('H', 'e', 'l', 'l', 'o'))
a == d   // true (одинаковое содержимое)
a === d  // false (разные объекты в памяти)
```

**С пользовательскими объектами:**
```kotlin
data class User(val name: String)

val user1 = User("John")
val user2 = User("John")
val user3 = user1

user1 == user2   // true (data class equals проверяет содержимое)
user1 === user2  // false (разные объекты)
user1 === user3  // true (одна и та же ссылка)
```

**Ключевые различия:**

| Оператор | Назначение | Null-safe |
|----------|---------|-----------|
| `==` | Структурное равенство (компилируется в null-safe вызов `equals()`) | Да |
| `===` | Референтное равенство (один объект) | Да |
| `!=` | Структурное неравенство | Да |
| `!==` | Референтное неравенство | Да |

**Kotlin vs Java:**
- Kotlin `==` ≈ Java `.equals()` (c null-safe оберткой: `a?.equals(b) ?: (b == null)`)
- Kotlin `===` ≈ Java `==`
- `==` в Kotlin является null-safe, `==` в Java для ссылочных типов проверяет ссылки и не является null-safe в том же смысле (возможен `NullPointerException` при вызове `.equals` напрямую).

## Answer (EN)

In Kotlin, the **`===` operator** is used to check **reference equality** (also called referential equality). It checks whether two variables point to the same object in memory.

See also: [[c-kotlin]], [[c-equality]]

**Comparison: `==` vs `===`**

```kotlin
val a = "Hello"
val b = "Hello"
val c = a

// Structural equality (==) - checks content (null-safe equals)
a == b   // true (same content)

// Referential equality (===) - checks if same object
// Important: the result of a === b is not guaranteed by Kotlin spec and depends on platform/implementation
a === b  // may be true or false

a === c  // true (c references a)

val d = String(charArrayOf('H', 'e', 'l', 'l', 'o'))
a == d   // true (same content)
a === d  // false (different objects in memory)
```

**With custom objects:**
```kotlin
data class User(val name: String)

val user1 = User("John")
val user2 = User("John")
val user3 = user1

user1 == user2   // true (data class equals checks content)
user1 === user2  // false (different objects)
user1 === user3  // true (same reference)
```

**Key Differences:**

| Operator | Purpose | Null-safe |
|----------|---------|-----------|
| `==` | Structural equality (compiled to a null-safe `equals()` call) | Yes |
| `===` | Referential equality (same object) | Yes |
| `!=` | Structural inequality | Yes |
| `!==` | Referential inequality | Yes |

**Kotlin vs Java:**
- Kotlin `==` ≈ Java `.equals()` (with null-safe wrapper: `a?.equals(b) ?: (b == null)`)
- Kotlin `===` ≈ Java `==`
- Kotlin's `==` is null-safe; Java's `==` for reference types checks references and using `.equals` directly can throw `NullPointerException` when the receiver is null.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия оператора `===` от оператора `==` в Java?
- В каких случаях на практике следует использовать `===`?
- Какие распространенные ошибки и подводные камни связаны с использованием `===`?

## Follow-ups

- What are the key differences between the `===` operator and Java's `==` operator?
- When would you use `===` in practice?
- What are common pitfalls to avoid when using `===`?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-data-class-detailed--kotlin--medium]]
- [[q-destructuring-declarations--kotlin--medium]]
- [[q-mutex-synchronized-coroutines--kotlin--medium]]

## Related Questions

- [[q-data-class-detailed--kotlin--medium]]
- [[q-destructuring-declarations--kotlin--medium]]
- [[q-mutex-synchronized-coroutines--kotlin--medium]]
