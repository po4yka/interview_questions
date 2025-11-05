---
id: lang-014
title: "Kotlin Java Abstract Differences / Различия abstract в Kotlin и Java"
aliases: [Kotlin Java Abstract Differences, Различия abstract в Kotlin и Java]
topic: programming-languages
subtopics: [inheritance, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-structured-concurrency-patterns--kotlin--hard]
created: 2025-10-15
updated: 2025-10-31
tags: [abstract, difficulty/medium, inheritance, java, oop, open, programming-languages]
date created: Friday, October 31st 2025, 6:30:00 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---

# Какое Главное Отличие Между Java И Kotlin Касательно Абстрактных Классов И Методов?

**English**: What is the main difference between Java and Kotlin regarding abstract classes and methods?

## Answer (EN)
The main difference is how **overriding** is handled:

### Java
- **Abstract methods** implicitly allow overriding (no keyword needed)
- **Non-abstract methods** are final by default (cannot override without explicitly making them non-final)
- Must explicitly mark as `abstract` or `final`

```java
abstract class Animal {
    abstract void makeSound();     // Can override (implicit)
    void sleep() { }               // Cannot override (final by default)

    // Must explicitly allow overriding:
    public void eat() { }          // Still final!
}
```

### Kotlin
- **Abstract members** are `open` by default (can be overridden)
- **Non-abstract members** are `final` by default (must use `open` to allow overriding)
- More explicit about inheritance intentions

```kotlin
abstract class Animal {
    abstract fun makeSound()       // Can override (open by default)
    fun sleep() { }                // Cannot override (final by default)

    open fun eat() { }             // Must use 'open' to allow overriding
}
```

**Comparison table:**

| Member type | Java | Kotlin |
|-------------|------|--------|
| Abstract method | Implicitly overridable | `open` by default |
| Regular method | Final unless overridden | `final` unless marked `open` |
| Abstract class | Can be extended | Can be extended |

**Philosophy difference:**
- **Java**: Abstract methods are automatically overridable
- **Kotlin**: Explicit `open` keyword required for non-abstract methods

This makes Kotlin's inheritance model **more explicit and intentional**.

## Ответ (RU)

Главное отличие заключается в том, как обрабатывается **переопределение**:

### Java
- **Абстрактные методы** неявно разрешают переопределение (не нужно ключевое слово)
- **Неабстрактные методы** являются final по умолчанию (нельзя переопределить без явного указания)
- Необходимо явно помечать как `abstract` или `final`

```java
abstract class Animal {
    abstract void makeSound();     // Можно переопределить (неявно)
    void sleep() { }               // Нельзя переопределить (final по умолчанию)

    // Необходимо явно разрешить переопределение:
    public void eat() { }          // Всё ещё final!
}
```

### Kotlin
- **Абстрактные члены** являются `open` по умолчанию (можно переопределить)
- **Неабстрактные члены** являются `final` по умолчанию (необходимо использовать `open` для разрешения переопределения)
- Более явно о намерениях наследования

```kotlin
abstract class Animal {
    abstract fun makeSound()       // Можно переопределить (open по умолчанию)
    fun sleep() { }                // Нельзя переопределить (final по умолчанию)

    open fun eat() { }             // Необходимо использовать 'open' для разрешения переопределения
}
```

**Таблица сравнения:**

| Тип члена | Java | Kotlin |
|-------------|------|--------|
| Абстрактный метод | Неявно переопределяемый | `open` по умолчанию |
| Обычный метод | Final пока не переопределён | `final` пока не помечен `open` |
| Абстрактный класс | Можно расширять | Можно расширять |

**Философское различие:**
- **Java**: Абстрактные методы автоматически переопределяемы
- **Kotlin**: Требуется явное ключевое слово `open` для неабстрактных методов

Это делает модель наследования в Kotlin **более явной и намеренной**.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-structured-concurrency-patterns--kotlin--hard]]
-
-
