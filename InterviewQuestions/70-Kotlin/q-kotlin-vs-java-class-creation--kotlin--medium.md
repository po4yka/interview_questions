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
related: [c-kotlin, q-inline-function-limitations--kotlin--medium, q-kotlin-lambda-expressions--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [classes, data-classes, difficulty/medium, java, kotlin, syntax]
date created: Friday, October 31st 2025, 6:28:54 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Вопрос (RU)
> Что при создании классов в Kotlin изменилось по сравнению с Java?

---

# Question (EN)
> What changed when creating classes in Kotlin compared to Java?

## Ответ (RU)

При создании классов по сравнению с Java в Kotlin появилось несколько значительных изменений и упрощений.

1. Объявление класса и конструкторов

Java:
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

Kotlin:
```kotlin
class Person(val name: String, val age: Int)
// Первичный конструктор объявлен в заголовке класса, параметры с val/var сразу становятся свойствами
```

1. Статические члены (`static`) и `companion object`

Java:
```java
public class MyClass {
    public static final String CONSTANT = "constant";

    public static void staticMethod() {
        // code
    }
}
```

Kotlin:
```kotlin
class MyClass {
    companion object {
        const val CONSTANT = "constant"

        @JvmStatic
        fun staticMethod() {
            // код
        }
    }
}
```

1. `data class`

Java:
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
        // реализация
    }

    @Override
    public int hashCode() {
        // реализация
    }

    @Override
    public String toString() {
        // реализация
    }
}
```

Kotlin:
```kotlin
data class User(val name: String, val age: Int)
// Автоматически генерирует: equals(), hashCode(), toString(), copy(), componentN() для свойств primary-конструктора (объявленных через val/var)
```

1. Свойства и аксессоры

Java:
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

Kotlin:
```kotlin
class Rectangle(var width: Int, var height: Int)
// Геттеры и сеттеры генерируются автоматически
```

1. Наследование

Java (если явно не указан `final`, класс можно наследовать):
```java
public class Base {}  // можно наследовать
public final class Final {}  // нельзя наследовать
```

Kotlin (`final` по умолчанию, нужно явно указать `open` для наследования):
```kotlin
class Base  // нельзя наследовать (final по умолчанию)
open class Open  // можно наследовать
```

1. Модификаторы видимости

| Модификатор              | Java по умолчанию        | Kotlin по умолчанию          |
|--------------------------|--------------------------|------------------------------|
| Верхнеуровневые сущности | package-private          | public                       |
| Члены класса             | package-private          | public                       |
| `internal` Kotlin        | Нет прямого аналога      | Видимость в пределах модуля  |

1. Создание объектов без `new`

Java:
```java
Person person = new Person("Alice", 30);
```

Kotlin:
```kotlin
val person = Person("Alice", 30)
```

1. Однострочные (single-expression) функции

Kotlin позволяет объявлять методы в виде однострочных функций вместо стандартного блочного синтаксиса Java, что делает объявления короче:

```kotlin
class Calculator {
    fun add(a: Int, b: Int) = a + b  // однострочная функция
}
```

1. `sealed`-классы

```kotlin
sealed class Result
class Success(val data: String) : Result()
class Error(val message: String) : Result()
```

Современный Java также поддерживает sealed-классы, но в Kotlin они появились раньше и тесно интегрированы с `when`-выражениями для исчерпывающих проверок.

Итоговые отличия:

| Характеристика     | Java                              | Kotlin                                           |
|--------------------|-----------------------------------|--------------------------------------------------|
| Шаблонный код      | Много бойлерплейта               | Лаконичный синтаксис                            |
| Свойства           | Ручные геттеры/сеттеры           | `val`/`var`, аксессоры генерируются автоматически |
| Data-классы        | Ручная реализация методов         | Ключевое слово `data class`                     |
| Статические члены  | `static`                          | `companion object`, `@JvmStatic`                |
| Наследование       | Не final по умолчанию (если не указан `final`) | `final` по умолчанию, нужен `open`     |
| Видимость          | package-private по умолчанию      | `public` по умолчанию, есть `internal`          |
| Конструкторы       | Отдельно от объявления класса     | Первичный конструктор в заголовке класса        |
| Создание объектов  | Ключевое слово `new`              | Без `new`                                       |

Эти особенности делают Kotlin более лаконичным, безопасным и выразительным при работе с классами по сравнению с Java. См. также [[c-kotlin]] для общей информации о языке.

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
// Primary constructor in the class header; val/var parameters become properties
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
        public fun staticMethod() {
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
// Auto-generates: equals(), hashCode(), toString(), copy(), componentN() for primary-constructor properties declared with val/var
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

**Java (not final by default; can be inherited unless marked final):**
```java
public class Base {}  // Can be inherited
public final class Final {}  // Cannot be inherited
```

**Kotlin (final by default; must be marked open to inherit):**
```kotlin
class Base  // Cannot be inherited (final by default)
open class Open  // Can be inherited
```

**6. Visibility Modifiers**

| Modifier          | Java Default                 | Kotlin Default                          |
|-------------------|-----------------------------|-----------------------------------------|
| Top-level         | package-private              | public                                  |
| Class members     | package-private              | public                                  |
| Kotlin `internal` | No direct equivalent         | Visible within a module                 |

**7. No `new` Keyword**

**Java:**
```java
Person person = new Person("Alice", 30);
```

**Kotlin:**
```kotlin
val person = Person("Alice", 30)
```

**8. Single-Expression Functions**

Kotlin allows methods to be written as single-expression functions instead of Java's typical block-bodied methods, making declarations shorter and more expressive:

```kotlin
class Calculator {
    fun add(a: Int, b: Int) = a + b  // Single-expression function
}
```

**9. Sealed Classes**

**Kotlin:**
```kotlin
sealed class Result
class Success(val data: String) : Result()
class Error(val message: String) : Result()
```

Note: Modern Java (since Java 17) also supports sealed classes, but Kotlin's sealed classes were introduced earlier and integrate closely with `when` expressions for exhaustive checks.

**Summary of Key Changes:**

| Feature          | Java                         | Kotlin                                      |
|------------------|------------------------------|---------------------------------------------|
| Boilerplate      | Verbose                      | Concise                                    |
| Properties       | Manual getters/setters       | Auto-generated (`val`/`var`)               |
| Data classes     | Manual equals/hashCode/toString | `data class` keyword                    |
| Static members   | `static` keyword             | `companion object` (+ `@JvmStatic` for Java interop) |
| Inheritance      | Not final by default         | Final by default (`open` required)         |
| Visibility       | package-private default (no modifier) | `public` default; has `internal` (module scope) |
| Constructors     | Separate from class header   | Primary constructor in class header        |
| Object creation  | `new` keyword                | No `new`                                   |

Kotlin's design emphasizes conciseness, safety, and expressiveness, reducing boilerplate while maintaining readability.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions

- [[q-inline-function-limitations--kotlin--medium]]
- [[q-kotlin-lambda-expressions--kotlin--medium]]
- [[q-mutex-synchronized-coroutines--kotlin--medium]]
