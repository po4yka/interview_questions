---
id: kotlin-171
title: "Kotlin Vs Java Class Creation / Создание классов Kotlin vs Java"
aliases: [Class Creation, Data Classes, Kotlin Classes, Создание классов]
topic: kotlin
subtopics: [classes, data-classes, syntax]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-inline-function-limitations--kotlin--medium, q-kotlin-lambda-expressions--kotlin--medium, q-mutex-synchronized-coroutines--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [classes, data-classes, difficulty/medium, java, kotlin, syntax]
date created: Friday, October 31st 2025, 6:28:54 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# Что При Создании Классов В Kotlin Изменились По Сравнению С Java?

# Question (EN)
> What changed when creating classes in Kotlin compared to Java?

# Вопрос (RU)
> Что при создании классов в Kotlin изменились по сравнению с Java?

---

## Answer (EN)

Kotlin introduced several significant changes and simplifications when creating classes compared to Java. Here are the main differences:

**1. Class Declaration and Constructors**

**Java:**
```java
public class Person {
    private String name;
    private int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() { return name; }
    public int getAge() { return age; }
}
```

**Kotlin:**
```kotlin
class Person(val name: String, val age: Int)
```

**2. Static Members**

**Java:**
```java
public class MyClass {
    public static final String CONSTANT = "constant";

    public static void staticMethod() {
        // code
    }
}
```

**Kotlin:**
```kotlin
class MyClass {
    companion object {
        const val CONSTANT = "constant"

        @JvmStatic
        fun staticMethod() {
            // code
        }
    }
}
```

**3. Data Classes**

**Java:**
```java
public class User {
    private String name;
    private int age;

    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public boolean equals(Object o) {
        // Implementation
    }

    @Override
    public int hashCode() {
        // Implementation
    }

    @Override
    public String toString() {
        // Implementation
    }
}
```

**Kotlin:**
```kotlin
data class User(val name: String, val age: Int)
// Auto-generates: equals(), hashCode(), toString(), copy(), componentN()
```

**4. Properties and Accessors**

**Java:**
```java
public class Rectangle {
    private int width;
    private int height;

    public int getWidth() { return width; }
    public void setWidth(int width) { this.width = width; }

    public int getHeight() { return height; }
    public void setHeight(int height) { this.height = height; }
}
```

**Kotlin:**
```kotlin
class Rectangle(var width: Int, var height: Int)
// Getters and setters generated automatically
```

**5. Inheritance**

**Java (open by default):**
```java
public class Base {}  // Can be inherited
public final class Final {}  // Cannot be inherited
```

**Kotlin (final by default):**
```kotlin
class Base  // Cannot be inherited (final by default)
open class Open  // Can be inherited
```

**6. Visibility Modifiers**

| Modifier | Java Default | Kotlin Default |
|----------|--------------|----------------|
| Top-level | package-private | `public` |
| Class members | package-private | `public` |
| Kotlin `internal` | No equivalent | Module-visible |

**7. No `new` Keyword**

**Java:**
```java
Person person = new Person("Alice", 30);
```

**Kotlin:**
```kotlin
val person = Person("Alice", 30)
```

**8. Single-Expression Classes**

**Kotlin:**
```kotlin
class Calculator {
    fun add(a: Int, b: Int) = a + b  // Single expression
}
```

**9. Sealed Classes (No Java Equivalent)**

**Kotlin:**
```kotlin
sealed class Result
class Success(val data: String) : Result()
class Error(val message: String) : Result()
```

**Summary of Key Changes:**

| Feature | Java | Kotlin |
|---------|------|--------|
| **Boilerplate** | Verbose | Concise |
| **Properties** | Manual getters/setters | Auto-generated |
| **Data classes** | Manual equals/hashCode/toString | `data class` |
| **Static members** | `static` keyword | `companion object` |
| **Inheritance** | Open by default | Final by default (`open` required) |
| **Visibility** | package-private default | `public` default |
| **Constructors** | Separate from class | Primary in header |
| **Object creation** | `new` keyword | No `new` |

Kotlin's design emphasizes **conciseness**, **safety**, and **expressiveness**, reducing boilerplate while maintaining readability.

---

## Ответ (RU)

При создании классов по сравнению с Java произошли несколько значительных изменений и упрощений. Kotlin предлагает более лаконичный и выразительный синтаксис, что делает код более читаемым и удобным. Объявление классов и конструкторов в Kotlin упрощено, например: class Person(val name: String, val age: Int). Для статических членов используется companion object вместо static. Kotlin предоставляет data классы, которые автоматически генерируют методы equals(), hashCode(), toString(), copy(), и componentN(). Свойства объявляются напрямую, и методы доступа генерируются автоматически.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-inline-function-limitations--kotlin--medium]]
- [[q-kotlin-lambda-expressions--kotlin--medium]]
- [[q-mutex-synchronized-coroutines--kotlin--medium]]
