---
id: "20251015082236027"
title: "Generics Types Overview / Обзор обобщенных типов"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags: - bounds
  - generics
  - java
  - kotlin
  - programming-languages
  - type-parameters
  - variance
---
# Какие виды дженериков есть?

# Question (EN)
> What types of generics exist in Kotlin and Java?

# Вопрос (RU)
> Какие виды дженериков существуют в Kotlin и Java?

---

## Answer (EN)

Generics come in several forms:

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
<T extends Number> double sum(T a, T b)
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

**Covariance** (`out` in Kotlin, `extends` in Java):
```kotlin
interface Producer<out T> {  // Can only produce T
    fun produce(): T
}
```

**Contravariance** (`in` in Kotlin, `super` in Java):
```kotlin
interface Consumer<in T> {   // Can only consume T
    fun consume(item: T)
}
```

### 5. Star Projection (Raw Types)
```kotlin
List<*>  // Kotlin - star projection
List     // Java - raw type (deprecated)
```

**Summary:**

| Type | Purpose | Example |
|------|---------|---------|
| Generic class | Parameterized class | `Box<T>` |
| Generic method | Parameterized method | `<T> T identity(T)` |
| Upper bound | Restrict to subtype | `<T : Number>` |
| Lower bound | Java only | `<T super Integer>` |
| Covariance | Producer | `out T` |
| Contravariance | Consumer | `in T` |
| Star projection | Unknown type | `List<*>` |

---

## Ответ (RU)

Дженерики существуют в нескольких формах:

### 1. Обобщённые классы (Generic Classes)
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

### 3. Ограничения типов (Type Bounds/Constraints)

**Верхние границы** (`extends` в Java, `:` в Kotlin):
```kotlin
// Kotlin
fun <T : Number> sum(a: T, b: T): Double {
    return a.toDouble() + b.toDouble()
}

// Java
<T extends Number> double sum(T a, T b)
```

**Множественные границы:**
```kotlin
fun <T> process(value: T)
    where T : Comparable<T>,
          T : Serializable {
    // T должен реализовывать оба интерфейса
}
```

### 4. Аннотации вариантности (Variance Annotations)

**Ковариантность** (`out` в Kotlin, `extends` в Java):
```kotlin
interface Producer<out T> {  // Может только производить T
    fun produce(): T
}
```

**Контравариантность** (`in` в Kotlin, `super` в Java):
```kotlin
interface Consumer<in T> {   // Может только потреблять T
    fun consume(item: T)
}
```

### 5. Звездочная проекция (Star Projection) / Сырые типы (Raw Types)
```kotlin
List<*>  // Kotlin - звездочная проекция
List     // Java - сырой тип (deprecated)
```

**Резюме:**

| Тип | Назначение | Пример |
|------|---------|---------|
| Обобщённый класс | Параметризованный класс | `Box<T>` |
| Обобщённый метод | Параметризованный метод | `<T> T identity(T)` |
| Верхняя граница | Ограничение подтипом | `<T : Number>` |
| Нижняя граница | Только в Java | `<T super Integer>` |
| Ковариантность | Производитель | `out T` |
| Контравариантность | Потребитель | `in T` |
| Звездочная проекция | Неизвестный тип | `List<*>` |

