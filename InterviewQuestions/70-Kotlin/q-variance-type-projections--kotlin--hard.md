---
id: kotlin-201
title: Variance Type Projections / Вариантность и проекции типов
aliases:
- Contravariance
- Covariance
- Type Projections
- Variance
- Variance типов
topic: kotlin
subtopics:
- generics
- type-system
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-equals-hashcode-purpose--kotlin--medium
- q-launch-vs-async--kotlin--easy
created: 2025-10-15
updated: 2025-11-09
tags:
- contravariance
- covariance
- difficulty/hard
- generics
- kotlin
- projections
- type-system
- variance
---
# Вопрос (RU)
> Объясните variance на месте объявления против на месте использования в Kotlin. В чем разница между in, out и star проекциями?

---

# Question (EN)
> Explain declaration-site vs use-site variance in Kotlin. What is the difference between in, out, and star projections?

## Ответ (RU)

**Variance** описывает, как отношения подтипизации между generic-типами соотносятся с подтипизацией их параметров типов.

Kotlin поддерживает **вариантность на месте объявления** (declaration-site variance) с помощью модификаторов `out` и `in` в объявлении класса/интерфейса, а также **вариантность на месте использования** (use-site variance) через проекции типов `out`, `in` и `*` в конкретных местах использования обобщённого типа.

См. также: [[c-kotlin]]

### Ковариантность (`out`)

- Объявление `out T` означает, что тип ковариантен по `T`: `Producer<String>` является подтипом `Producer<Any>`.
- Ограничение: параметр типа `T` можно использовать только в позициях "выхода" (возвращаемое значение, значения, выдаваемые наружу), чтобы сохранить type-safety.
- Тип с `out` можно рассматривать как "поставщика" значений `T`.

Пример (на месте объявления):

```kotlin
interface Producer<out T> {
    fun produce(): T          // можно возвращать T
    // fun consume(item: T)  // нельзя принимать T в параметрах (ошибка компиляции)
}

class StringProducer : Producer<String> {
    override fun produce(): String = "Hello"
}

fun exampleCovariance() {
    val stringProducer: Producer<String> = StringProducer()
    val anyProducer: Producer<Any> = stringProducer // ковариантность
}
```

Из стандартной библиотеки: `List<out T>` ковариантен. Например:

```kotlin
val strings: List<String> = listOf("a", "b")
val anys: List<Any> = strings // OK: List ковариантен по T
```

### Контравариантность (`in`)

- Объявление `in T` означает, что тип контравариантен по `T`: `Consumer<Any>` является подтипом `Consumer<String>`.
- Ограничение: параметр типа `T` можно использовать только во "входных" позициях (параметры методов), а возвращать `T` нельзя.
- Тип с `in` можно рассматривать как "потребителя" значений `T`.

Пример (на месте объявления):

```kotlin
interface Consumer<in T> {
    fun consume(item: T)      // можно принимать T
    // fun produce(): T       // нельзя возвращать T (ошибка компиляции)
}

class AnyConsumer : Consumer<Any> {
    override fun consume(item: Any) {
        println(item)
    }
}

fun exampleContravariance() {
    val anyConsumer: Consumer<Any> = AnyConsumer()
    val stringConsumer: Consumer<String> = anyConsumer // контравариантность
}
```

Из стандартной библиотеки: `Comparable<in T>` контравариантен:

```kotlin
class Person(val name: String) : Comparable<Person> {
    override fun compareTo(other: Person): Int = name.compareTo(other.name)
}

fun useComparable(persons: List<Person>, cmp: Comparable<in Person>) {
    // cmp может быть реализован так, чтобы уметь сравнивать Person с Person или с его супертипами
}
```

### Инвариантность

- Без модификаторов `in`/`out` тип инвариантен: `Box<String>` не является ни подтипом, ни супертипом `Box<Any>`.

```kotlin
interface Box<T> {
    fun get(): T
    fun set(item: T)
}

fun exampleInvariance() {
    val stringBox: Box<String> = object : Box<String> {
        private var value: String = ""
        override fun get(): String = value
        override fun set(item: String) { value = item }
    }
    // val anyBox: Box<Any> = stringBox // ошибка: инвариантность
}
```

### Вариантность На Месте Использования (Use-Site Variance / Type Projections)

Use-site variance позволяет "спроецировать" тип, когда объявление инвариантно, но в конкретном контексте мы используем его только как производителя или только как потребителя.

Корректный пример копирования (аналог `Collections.copy`), показывающий отношения подтипов:

```kotlin
fun <T> copy(from: MutableList<out T>, to: MutableList<in T>) {
    for (item in from) {
        to.add(item)
    }
}
```

- `MutableList<out T>` на месте использования означает: источник предоставляет значения типа `T` (или его подтипов), которые мы можем безопасно читать, но не можем добавлять произвольные значения типа `T`.
- `MutableList<in T>` означает: приёмник принимает значения типа `T` (или его подтипов), которые мы можем безопасно записывать, но при чтении элементы видны как `Any?` или более общий тип.

### Star Projection (`*`)

Star projection используется, когда конкретный параметр типа неизвестен, но нужно безопасно работать с типом.

```kotlin
fun printList(list: List<*>) {
    for (item in list) {
        println(item) // item имеет тип Any?
    }
}
```

`List<*>` означает: "список элементов некоторого неизвестного типа". Мы можем читать элементы только как `Any?`, но не можем добавлять произвольные значения (кроме `null` там, где это допустимо), сохраняя type-safety.

Variance и проекции типов в Kotlin позволяют выразить, какие операции с generic-типами безопасны, и избежать проблем с небезопасной подстановкой типов.

## Answer (EN)

**Variance** describes how subtyping between generic types relates to subtyping of their type parameters.

Kotlin supports:
- **Declaration-site variance** via `out` and `in` in the generic type declaration.
- **Use-site variance** via type projections (`out`, `in`, `*`) at specific usage sites.

See also: [[c-kotlin]]

---

### Covariance (`out`)

- `out T` on a type parameter makes the type covariant in `T`: `Producer<String>` is a subtype of `Producer<Any>`.
- Restriction: `T` can only be used in "output" positions (returned/produced values) in the declaration to preserve type safety.
- Intuition: "producer" of `T`.

Declaration-site example:

```kotlin
interface Producer<out T> {
    fun produce(): T          // Can return T
    // fun consume(item: T)   // Error: cannot use T in in-position
}

class StringProducer : Producer<String> {
    override fun produce(): String = "Hello"
}

fun exampleCovariance() {
    val stringProducer: Producer<String> = StringProducer()
    val anyProducer: Producer<Any> = stringProducer // Covariant
}
```

Standard library: `List<out T>` is covariant:

```kotlin
val strings: List<String> = listOf("a", "b")
val anys: List<Any> = strings // OK
```

---

### Contravariance (`in`)

- `in T` on a type parameter makes the type contravariant in `T`: `Consumer<Any>` is a subtype of `Consumer<String>`.
- Restriction: `T` can only be used in "input" positions (method parameters); it cannot be returned.
- Intuition: "consumer" of `T`.

Declaration-site example:

```kotlin
interface Consumer<in T> {
    fun consume(item: T)      // Can accept T
    // fun produce(): T       // Error: cannot return T
}

class AnyConsumer : Consumer<Any> {
    override fun consume(item: Any) {
        println(item)
    }
}

fun exampleContravariance() {
    val anyConsumer: Consumer<Any> = AnyConsumer()
    val stringConsumer: Consumer<String> = anyConsumer // Contravariant
}
```

Standard library: `Comparable<in T>` is contravariant. Typical usage:

```kotlin
class Person(val name: String) : Comparable<Person> {
    override fun compareTo(other: Person): Int = name.compareTo(other.name)
}

fun useComparable(persons: List<Person>, cmp: Comparable<in Person>) {
    // cmp can compare Person with Person or its supertypes, consistent with contravariant T
}
```

---

### Invariance (no variance)

Without `in`/`out`, a generic type is invariant: you cannot substitute `Generic<A>` where `Generic<B>` is expected, even if `A` is a subtype of `B`.

```kotlin
interface Box<T> {
    fun get(): T
    fun set(item: T)
}

fun exampleInvariance() {
    val stringBox: Box<String> = object : Box<String> {
        private var value: String = ""
        override fun get(): String = value
        override fun set(item: String) { value = item }
    }
    // val anyBox: Box<Any> = stringBox // Error: invariant
}
```

---

### Use-Site Variance (Type Projections)

Use-site variance lets you project variance when using an invariant type.

A correct copy function (similar in spirit to `Collections.copy`) that expresses the relation between source and destination element types:

```kotlin
fun <T> copy(from: MutableList<out T>, to: MutableList<in T>) {
    for (item in from) {
        to.add(item)
    }
}
```

- `MutableList<out T>`: `from` is treated as a producer of `T` (or its subtypes). We cannot safely add arbitrary `T` values to it.
- `MutableList<in T>`: `to` is treated as a consumer of `T`. We can safely add `T` values, but items read from it have type `Any?` or another supertype.

---

### Star Projection (`*`)

Star projection represents an unknown type argument while preserving type safety.

```kotlin
fun printList(list: List<*>) {
    for (item in list) {
        println(item) // item is Any?
    }
}
```

`List<*>` means "a list of elements of some unknown type". You can safely read elements as `Any?`, but in general you cannot add arbitrary elements to it (except `null` where allowed).

---

Variance and type projections in Kotlin help express which operations on generic types are safe and prevent unsafe substitutions.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-equals-hashcode-purpose--kotlin--medium]]
- [[q-launch-vs-async--kotlin--easy]]
