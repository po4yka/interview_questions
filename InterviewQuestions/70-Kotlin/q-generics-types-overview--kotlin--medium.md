---
id: kotlin-174
title: "Generics Types Overview / Обзор обобщенных типов"
aliases: ["Generics Types Overview", "Обзор обобщенных типов", "Kotlin generics types overview", "Обзор дженериков Kotlin"]
topic: kotlin
subtopics: [functions, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features, q-coroutine-parent-child-relationship--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium]
---

# Вопрос (RU)
> Какие виды дженериков существуют в Kotlin и Java?

---

# Question (EN)
> What types of generics exist in Kotlin and Java?

## Ответ (RU)

Дженерики существуют в нескольких формах. Они являются частью системы типов языка [[c-kotlin]] и его особенностей ([[c-kotlin-features]]):

### 1. Обобщённые Классы (Generic Classes)
Классы с параметрами типа:
```kotlin
class Box<T>(val value: T)

val intBox = Box<Int>(42)
val stringBox = Box("Hello")
```

### 2. Обобщённые методы/функции (Generic Methods/Functions)
Методы с собственными параметрами типа:
```kotlin
fun <T> identity(value: T): T {
    return value
}

fun <T> List<T>.second(): T {
    return this[1]
}
```

### 3. Ограничения Типов (Type Bounds/Constraints)

**Верхние границы** (`extends` в Java, `:` в Kotlin):
```kotlin
// Kotlin
fun <T : Number> sum(a: T, b: T): Double {
    return a.toDouble() + b.toDouble()
}

// Java
public static <T extends Number> double sum(T a, T b) {
    return a.doubleValue() + b.doubleValue();
}
```

**Множественные границы:**
```kotlin
fun <T> process(value: T)
    where T : Comparable<T>,
          T : Serializable {
    // T должен реализовывать оба интерфейса
}
```

### 4. Аннотации Вариантности (Variance Annotations)

**Ковариантность** (`out` в Kotlin, `extends`-ограничения и `? extends` wildcard в Java):
```kotlin
interface Producer<out T> {  // Может только производить T
    fun produce(): T
}
```

**Контравариантность** (`in` в Kotlin, `? super` wildcard в Java):
```kotlin
interface Consumer<in T> {   // Может только потреблять T
    fun consume(item: T)
}
```

### 5. Звездочная Проекция и Сырые Типы

```kotlin
List<*>  // Kotlin — звездочная проекция (неизвестный тип)
```
```java
List<?>  // Java — wildcard с неизвестным типом
List     // Java — сырой тип (устаревший, использовать не рекомендуется)
```

**Резюме:**

| Тип                     | Назначение                          | Пример                    |
|-------------------------|-------------------------------------|---------------------------|
| Обобщённый класс        | Параметризованный класс            | `Box<T>`                  |
| Обобщённый метод        | Параметризованный метод/функция    | `<T> T identity(T)`       |
| Верхняя граница         | Ограничение подтипом               | `<T : Number>`, `<T extends Number>` |
| Нижняя граница (Java)   | Ограничение супертипом через wildcard | `List<? super Integer>` |
| Ковариантность          | Производитель                      | `out T`, `? extends T`    |
| Контравариантность      | Потребитель                        | `in T`, `? super T`       |
| Звездочная проекция     | Неизвестный тип в Kotlin           | `List<*>`                 |
| Сырой тип (Java)        | Тип без параметров (устаревший)    | `List`                    |

## Answer (EN)

Generics come in several forms. They are part of the [[c-kotlin]] type system and its language features ([[c-kotlin-features]]):

### 1. Generic Classes
Classes with type parameters:
```kotlin
class Box<T>(val value: T)

val intBox = Box<Int>(42)
val stringBox = Box("Hello")
```

### 2. Generic Methods/Functions
Methods with their own type parameters:
```kotlin
fun <T> identity(value: T): T {
    return value
}

fun <T> List<T>.second(): T {
    return this[1]
}
```

### 3. Type Bounds (Constraints)

**Upper bounds** (`extends` in Java, `:` in Kotlin):
```kotlin
// Kotlin
fun <T : Number> sum(a: T, b: T): Double {
    return a.toDouble() + b.toDouble()
}

// Java
public static <T extends Number> double sum(T a, T b) {
    return a.doubleValue() + b.doubleValue();
}
```

**Multiple bounds:**
```kotlin
fun <T> process(value: T)
    where T : Comparable<T>,
          T : Serializable {
    // T must implement both interfaces
}
```

### 4. Variance Annotations

**Covariance** (`out` in Kotlin, `? extends` wildcard / extends-bounded types in Java):
```kotlin
interface Producer<out T> {  // Can only produce T
    fun produce(): T
}
```

**Contravariance** (`in` in Kotlin, `? super` wildcard in Java):
```kotlin
interface Consumer<in T> {   // Can only consume T
    fun consume(item: T)
}
```

### 5. Star Projections and Raw Types

```kotlin
List<*>  // Kotlin - star projection (unknown type)
```
```java
List<?>  // Java - wildcard with unknown type
List     // Java - raw type (legacy, not recommended)
```

**Summary:**

| Type                 | Purpose                                 | Example                          |
|----------------------|-----------------------------------------|----------------------------------|
| Generic class        | Parameterized class                     | `Box<T>`                         |
| Generic method       | Parameterized method/function           | `<T> T identity(T)`              |
| Upper bound          | Restrict to subtype                     | `<T : Number>`, `<T extends Number>` |
| Lower bound (Java)   | Restrict to supertype via wildcard      | `List<? super Integer>`          |
| Covariance           | Producer                                | `out T`, `? extends T`           |
| Contravariance       | Consumer                                | `in T`, `? super T`              |
| Star projection      | Unknown type in Kotlin                  | `List<*>`                        |
| Raw type (Java)      | Type without parameters (legacy)        | `List`                           |

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation]("https://kotlinlang.org/docs/home.html")

## Related Questions

- [[q-produce-actor-builders--kotlin--medium]]
- [[q-coroutine-parent-child-relationship--kotlin--medium]]
