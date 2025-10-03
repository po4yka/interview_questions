---
id: 20251003141107
title: Unit singleton in Kotlin / Unit как синглтон в Kotlin
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, type-system]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/683
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-type-system

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, unit, singleton, type-system, void, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> How many Unit instances per application

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

## Ответ (RU)

Unit является синглтоном в Kotlin, то есть существует только один экземпляр Unit на всё приложение Это встроенный тип, используемый для обозначения отсутствия значимого значения

---

## Follow-ups
- How does Unit differ from Nothing?
- Can you explicitly return Unit?
- Why is Unit an object and not void?

## References
- [[c-kotlin-type-system]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-any-unit-nothing--programming-languages--medium]]
