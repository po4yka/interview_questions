---
id: 20251016-172614
title: "Kotlin Unit Singleton / Unit как синглтон в Kotlin"
topic: computer-science
difficulty: easy
status: draft
moc: moc-kotlin
related: [q-channel-buffer-strategies-comparison--kotlin--hard, q-suspend-functions-basics--kotlin--easy, q-kotlin-generic-function-syntax--programming-languages--easy]
created: 2025-10-15
tags:
  - kotlin
  - programming-languages
  - singleton
  - type-system
  - unit
  - void
---
# Сколько инстансов Unit на одно приложение

# Question (EN)
> How many Unit instances per application?

# Вопрос (RU)
> Сколько инстансов Unit на одно приложение

---

## Answer (EN)

**Unit is a singleton** in Kotlin, meaning there is **only one Unit instance** per entire application.

**Key characteristics:**

- **Singleton**: Only one instance exists
- **Built-in type**: Part of Kotlin standard library
- **Denotes absence**: Used to indicate absence of meaningful value
- **Similar to void**: But unlike `void`, Unit is an actual object

**Why singleton?**

Since Unit represents "no meaningful value", there's no need for multiple instances. All functions returning Unit return the same singleton instance.

**Example:**
```kotlin
fun printHello(): Unit {
    println("Hello")
}  // Implicitly returns Unit singleton

fun doSomething() {  // Unit return type inferred
    println("Doing something")
}

// Both return the same Unit instance
val u1 = printHello()
val u2 = doSomething()
println(u1 === u2)  // true - same instance!
```

**Comparison with Java:**
```java
// Java
public void method() { }  // Returns nothing (void)

// Kotlin
fun method(): Unit { }    // Returns Unit singleton
fun method2() { }         // Same as above (Unit inferred)
```

**Memory efficiency**: Since it's a singleton, no memory waste from multiple Unit objects.

---

## Ответ (RU)

**Unit является синглтоном** в Kotlin, то есть существует **только один экземпляр Unit** на всё приложение.

**Ключевые характеристики:**

- **Синглтон**: Существует только один экземпляр
- **Встроенный тип**: Часть стандартной библиотеки Kotlin
- **Обозначает отсутствие**: Используется для указания отсутствия значимого значения
- **Похож на void**: Но в отличие от `void`, Unit - это реальный объект

**Почему синглтон?**

Поскольку Unit представляет "отсутствие значимого значения", нет необходимости в нескольких экземплярах. Все функции, возвращающие Unit, возвращают один и тот же экземпляр синглтона.

**Пример:**
```kotlin
fun printHello(): Unit {
    println("Hello")
}  // Неявно возвращает синглтон Unit

fun doSomething() {  // Тип возврата Unit выводится автоматически
    println("Doing something")
}

// Обе функции возвращают один и тот же экземпляр Unit
val u1 = printHello()
val u2 = doSomething()
println(u1 === u2)  // true - один и тот же экземпляр!
```

**Сравнение с Java:**
```java
// Java
public void method() { }  // Ничего не возвращает (void)

// Kotlin
fun method(): Unit { }    // Возвращает синглтон Unit
fun method2() { }         // То же самое (Unit выводится автоматически)
```

**Эффективность памяти**: Поскольку это синглтон, нет потерь памяти от множества объектов Unit.

## Related Questions

- [[q-channel-buffer-strategies-comparison--kotlin--hard]]
- [[q-suspend-functions-basics--kotlin--easy]]
- [[q-kotlin-generic-function-syntax--programming-languages--easy]]
