---
id: lang-095
title: "Kotlin Override Keyword / Ключевое слово override в Kotlin"
aliases: [Kotlin Override Keyword, Ключевое слово override в Kotlin]
topic: kotlin
subtopics: [inheritance, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-coroutine-job-lifecycle--kotlin--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [abstract, difficulty/easy, inheritance, keywords, open, override, polymorphism, kotlin]
---

# Вопрос (RU)
> Какое ключевое слово используется для определения метода, который должен быть переопределен в подклассе?

# Question (EN)
> Which keyword is used to define a method that must be overridden in a subclass?

## Ответ (RU)

В Kotlin ключевое слово **`override`** используется для переопределения метода из родительского класса. Однако, чтобы метод можно было переопределить, метод родительского класса должен быть помечен как **`open`** или быть **`abstract`**.

**Для абстрактных методов (обязательно должны быть переопределены):**
```kotlin
abstract class Animal {
    abstract fun makeSound()  // Должен быть переопределён
}

class Dog : Animal() {
    override fun makeSound() {
        println("Woof!")
    }
}
```

**Для открытых методов (могут быть переопределены):**
```kotlin
open class Vehicle {
    open fun start() {  // Может быть переопределён (но не обязательно)
        println("Vehicle starting")
    }
}

class Car : Vehicle() {
    override fun start() {  // требуется ключевое слово override
        println("Car starting")
    }
}
```

**Ключевые моменты:**
- Используйте `abstract` для объявления метода, который **обязательно** должен быть переопределён
- Используйте `open` для объявления метода, который **может** быть переопределён
- Используйте `override` в подклассе для переопределения метода
- В отличие от Java, Kotlin требует явного ключевого слова `override` (предотвращает случайные переопределения)
- Родительский член должен быть объявлен как `open` или `abstract`, чтобы его можно было переопределить

**Предотвращение дальнейших переопределений:**
```kotlin
open class Base {
    open fun foo() {}
}

class Derived : Base() {
    final override fun foo() {}  // Нельзя переопределить дальше
}
```

**Сравнение с Java:**
- Java: `@Override` необязателен (аннотация)
- Kotlin: `override` обязателен (ключевое слово)
- Kotlin требует, чтобы родительские методы были `open` или `abstract` для переопределения

## Answer (EN)

In Kotlin, the **`override` keyword** is used to override a method from a parent class. However, to make a method overridable, the parent class member must be marked as **`open`** or be **`abstract`**.

**For abstract methods (must be overridden):**
```kotlin
abstract class Animal {
    abstract fun makeSound()  // Must be overridden
}

class Dog : Animal() {
    override fun makeSound() {
        println("Woof!")
    }
}
```

**For open methods (can be overridden):**
```kotlin
open class Vehicle {
    open fun start() {  // Can be overridden (but not required)
        println("Vehicle starting")
    }
}

class Car : Vehicle() {
    override fun start() {  // override keyword required
        println("Car starting")
    }
}
```

**Key points:**
- Use `abstract` to declare a method that **must** be overridden
- Use `open` to declare a method that **can** be overridden
- Use `override` in the subclass to override the method
- Unlike Java, Kotlin requires the explicit `override` keyword (prevents accidental overrides)
- The parent member must be declared `open` or `abstract` to be overridden

**Preventing further overrides:**
```kotlin
open class Base {
    open fun foo() {}
}

class Derived : Base() {
    final override fun foo() {}  // Cannot be overridden further
}
```

**Comparison with Java:**
- Java: `@Override` is optional (annotation)
- Kotlin: `override` is mandatory (keyword)
- Kotlin requires parent methods to be `open` or `abstract` for overriding

## Дополнительные вопросы (RU)

- В чем ключевые отличия этого подхода от Java?
- Когда вы бы использовали это на практике?
- Какие распространенные ошибки стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-kotlin-contracts-smart-casts--kotlin--hard]]
- [[q-equality-operators-kotlin--kotlin--easy]]
- [[q-coroutine-job-lifecycle--kotlin--medium]]

## Related Questions

- [[q-kotlin-contracts-smart-casts--kotlin--hard]]
- [[q-equality-operators-kotlin--kotlin--easy]]
- [[q-coroutine-job-lifecycle--kotlin--medium]]
