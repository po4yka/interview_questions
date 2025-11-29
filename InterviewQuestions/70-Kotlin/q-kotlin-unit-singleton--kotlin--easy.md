---
id: kotlin-183
title: "Kotlin Unit Singleton / Unit как синглтон в Kotlin"
aliases: [Kotlin Unit, Unit, Unit Singleton, Unit Объект]
topic: kotlin
subtopics: [type-system, unit]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-channel-buffer-strategies-comparison--kotlin--hard, q-suspend-functions-basics--kotlin--easy]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/easy, kotlin, singleton, type-system, unit, void]

date created: Friday, October 31st 2025, 6:28:54 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Вопрос (RU)
> Сколько инстансов `Unit` существует в одном приложении?

# Question (EN)
> How many `Unit` instances exist per application?

## Ответ (RU)

**Unit в Kotlin имеет единственное допустимое значение** (синглтон-значение), то есть существует **одна каноническая "instance" `Unit`** как значение, которое используют все функции с возвращаемым типом `Unit`.

На практике при обычном использовании вы можете считать, что для `Unit` есть один общий экземпляр-значение, а не множество отдельных объектов.

**Ключевые характеристики:**

- **Синглтон-значение**: Только одно допустимое значение `Unit` (объект `Unit`), используемое везде
- **Встроенный тип**: Часть стандартной библиотеки Kotlin
- **Обозначает отсутствие**: Используется для указания отсутствия значимого возвращаемого значения
- **Отличается от void**: В отличие от `void` в Java, `Unit` — это настоящий тип с единственным значением

**Почему синглтон-значение?**

Поскольку `Unit` представляет "отсутствие значимого значения", нет необходимости в нескольких разных значениях. Все функции, возвращающие `Unit`, логически возвращают одно и то же значение `Unit`.

**Пример:**
```kotlin
fun printHello(): Unit {
    println("Hello")
}  // Неявно возвращает значение Unit

fun doSomething() {  // Тип возврата Unit выводится автоматически
    println("Doing something")
}

// Обе функции логически возвращают одно и то же значение Unit
val u1 = printHello()
val u2 = doSomething()
println(u1 === u2)  // true - одно и то же значение Unit
```

**Сравнение с Java:**
```java
// Java
public void method() { }  // Ничего не возвращает (void), это не объект и не значение

// Kotlin
fun method(): Unit { }    // Возвращает значение типа Unit
fun method2() { }         // То же самое (Unit выводится автоматически)
```

**Эффективность памяти**: В типичной реализации `Unit` представляется как одно значение без создания новых объектов при каждом вызове функции. Компилятор и рантайм могут оптимизировать это так, что дополнительных аллокаций практически нет.

---

## Answer (EN)

**In Kotlin, `Unit` has a single allowed value** (a singleton value), meaning there is **one canonical `Unit` "instance" value** that all `Unit`-returning functions conceptually use.

In practice, you can think of `Unit` as having one shared value rather than many separate objects.

**Key characteristics:**

- **Singleton value**: Only one valid value of type `Unit` (the `Unit` object) is used everywhere
- **Built-in type**: Part of the Kotlin standard library
- **Denotes absence**: Used to indicate absence of a meaningful return value
- **Different from void**: Unlike `void` in Java, `Unit` is a real type with a single value

**Why singleton value?**

Since `Unit` represents "no meaningful value", there's no need for multiple distinct values. All functions returning `Unit` conceptually return the same `Unit` value.

**Example:**
```kotlin
fun printHello(): Unit {
    println("Hello")
}  // Implicitly returns Unit value

fun doSomething() {  // Unit return type inferred
    println("Doing something")
}

// Both logically return the same Unit value
val u1 = printHello()
val u2 = doSomething()
println(u1 === u2)  // true - same Unit value
```

**Comparison with Java:**
```java
// Java
public void method() { }  // Returns nothing (void); void is not an object/value instance

// Kotlin
fun method(): Unit { }    // Returns a value of type Unit
fun method2() { }         // Same as above (Unit inferred)
```

**Memory efficiency**: In typical implementations, `Unit` is represented as a single value and does not require creating new objects per call. The compiler/runtime can optimize it so there's effectively no per-call allocation overhead.

---

## Follow-ups

- What are the key differences between `Unit` and Java's `void`?
- When would you use `Unit` in practice (including explicit return type declarations)?
- What are common misconceptions or pitfalls when using `Unit`?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
## Related Questions

- [[q-channel-buffer-strategies-comparison--kotlin--hard]]
- [[q-suspend-functions-basics--kotlin--easy]]
- [[q-kotlin-generic-function-syntax--kotlin--easy]]

## Дополнительные Вопросы (RU)
- Каковы основные различия между `Unit` и `void` в Java?
- Когда вы бы использовали `Unit` на практике (включая явное указание типа)?
- Какие распространенные заблуждения или ошибки связаны с использованием `Unit`?
## Ссылки (RU)
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)