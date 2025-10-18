---
id: 20251012-154392
title: "Variance Type Projections / Вариантность и проекции типов"
topic: kotlin
difficulty: hard
status: draft
moc: moc-kotlin
related: [q-kotlin-constructor-keyword--programming-languages--easy, q-equals-hashcode-purpose--kotlin--medium, q-launch-vs-async--kotlin--easy]
created: 2025-10-15
tags:
  - kotlin
  - generics
  - variance
  - type-system
  - projections
  - covariance
---
# Variance and Type Projections in Kotlin

# Question (EN)
> Explain declaration-site vs use-site variance in Kotlin. What is the difference between in, out, and star projections?

# Вопрос (RU)
> Объясните variance на месте объявления против на месте использования в Kotlin. В чем разница между in, out и star проекциями?

---

## Answer (EN)

**Variance** describes how subtyping between generic types relates to subtyping of their type parameters. Kotlin supports both **declaration-site** and **use-site** variance.

---

### Covariance (out)

Producer - can only produce (return) values:

```kotlin
// Declaration-site covariance
interface Producer<out T> {
    fun produce(): T          //  Can return T
    // fun consume(item: T)   //  Cannot accept T as parameter
}

class StringProducer : Producer<String> {
    override fun produce(): String = "Hello"
}

fun example() {
    val stringProducer: Producer<String> = StringProducer()
    val anyProducer: Producer<Any> = stringProducer //  Covariant
}
```

**Real-world: List<out T>**

```kotlin
val strings: List<String> = listOf("a", "b")
val objects: List<Any> = strings //  List is covariant
```

---

### Contravariance (in)

Consumer - can only consume (accept) values:

```kotlin
// Declaration-site contravariance
interface Consumer<in T> {
    fun consume(item: T)      //  Can accept T
    // fun produce(): T       //  Cannot return T
}

class AnyConsumer : Consumer<Any> {
    override fun consume(item: Any) {
        println(item)
    }
}

fun example() {
    val anyConsumer: Consumer<Any> = AnyConsumer()
    val stringConsumer: Consumer<String> = anyConsumer //  Contravariant
}
```

**Real-world: Comparable<in T>**

```kotlin
class Person(val name: String) : Comparable<Any> {
    override fun compareTo(other: Any): Int = 0
}

val person: Comparable<Person> = Person("John") //  Contravariant
```

---

### Invariance (no variance)

Cannot substitute:

```kotlin
interface Box<T> {
    fun get(): T
    fun set(item: T)
}

fun example() {
    val stringBox: Box<String> = StringBox()
    // val anyBox: Box<Any> = stringBox //  Invariant
}
```

---

### Use-Site Variance (Projections)

Apply variance at use-site:

```kotlin
// Declaration is invariant
class MutableList<T>

fun copy(from: MutableList<out Any>, to: MutableList<in Any>) {
    for (item in from) {
        to.add(item)
    }
}
```

---

### Star Projection (*)

Unknown type:

```kotlin
fun printList(list: List<*>) {
    for (item in list) {
        println(item) // item is Any?
    }
}
```

---

## Ответ (RU)

**Variance** описывает, как подтипизация между generic типами соотносится с подтипизацией их параметров типов.

### Ковариантность (out)

Производитель - может только возвращать значения. List<out T> - пример.

### Контравариантность (in)

Потребитель - может только принимать значения. Comparable<in T> - пример.

### Инвариантность

Нет замены. MutableList<T> инвариантен.

### Use-Site Variance

Применение variance в месте использования: `MutableList<out T>`, `MutableList<in T>`.

### Star Projection

Неизвестный тип: `List<*>` означает список неизвестного типа.

Variance обеспечивает type-safety при работе с generic типами в Kotlin.

## Related Questions

- [[q-kotlin-constructor-keyword--programming-languages--easy]]
- [[q-equals-hashcode-purpose--kotlin--medium]]
- [[q-launch-vs-async--kotlin--easy]]
