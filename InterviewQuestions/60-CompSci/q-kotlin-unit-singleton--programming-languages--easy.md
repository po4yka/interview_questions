---
tags:
  - kotlin
  - programming-languages
  - singleton
  - type-system
  - unit
  - void
difficulty: easy
---

# Сколько инстансов Unit на одно приложение

**English**: How many Unit instances per application?

## Answer

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

## Ответ

Unit является синглтоном в Kotlin, то есть существует только один экземпляр Unit на всё приложение Это встроенный тип, используемый для обозначения отсутствия значимого значения

