---
id: lang-014
title: "Kotlin Java Abstract Differences / Различия abstract в Kotlin и Java"
aliases: [Kotlin Java Abstract Differences, Различия abstract в Kotlin и Java]
topic: kotlin
subtopics: [inheritance, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features, q-structured-concurrency-patterns--kotlin--hard]
created: 2025-10-15
updated: 2025-11-09
tags: [abstract, difficulty/medium, inheritance, java, oop, open, programming-languages]
---

# Вопрос (RU)
> Какое главное отличие между Java и Kotlin касательно абстрактных классов и методов?

# Question (EN)
> What is the main difference between Java and Kotlin regarding abstract classes and methods?

## Ответ (RU)

Главное отличие заключается в том, насколько явно выражаются наследование и переопределение.

### Java
- Абстрактные методы неявно разрешают переопределение (не нужно отдельное ключевое слово для `open`).
- Обычные (неабстрактные) нестатические методы (в том числе в абстрактных классах) по умолчанию НЕ являются `final` и могут быть переопределены, пока явно не помечены `final`.
- Необходимо явно помечать методы как `abstract` или `final`, чтобы изменить их поведение.

```java
abstract class Animal {
    abstract void makeSound();     // Должен быть реализован в конкретных подклассах; переопределяем.
    void sleep() { }               // По умолчанию переопределяем (не final).

    public void eat() { }          // Также переопределяем, пока явно не указан final.

    public final void die() { }    // Нельзя переопределить.
}
```

### Kotlin
- Абстрактные члены по определению открыты для переопределения и должны быть реализованы в конкретных классах.
- Неабстрактные члены по умолчанию `final`; чтобы разрешить переопределение, нужно явно использовать `open`.
- Необходимо явно использовать `open`/`final`/`abstract` для выражения намерений наследования.

```kotlin
abstract class Animal {
    abstract fun makeSound()       // Должен быть реализован; по сути открыт для переопределения.
    fun sleep() { }                // final по умолчанию; нельзя переопределить.

    open fun eat() { }             // Явно open; можно переопределить.
}
```

**Таблица сравнения:**

| Тип члена         | Java                                   | Kotlin                                  |
|-------------------|----------------------------------------|-----------------------------------------|
| Абстрактный метод | Всегда переопределяемый                | `abstract` член фактически открыт       |
| Обычный метод     | Переопределяем, пока не указан `final` | `final` по умолчанию; нужен `open`      |
| Абстрактный класс | Можно расширять                        | Можно расширять                         |

**Философское различие:**
- Java: Более разрешающая модель по умолчанию; большинство методов можно переопределить, если не указано `final`.
- Kotlin: Более явная и ограничивающая модель; методы `final` по умолчанию, переопределение требует явного `open`.

Это делает модель наследования в Kotlin более явной и намеренной. См. также [[c-kotlin]].

## Answer (EN)
The main difference is how overriding and inheritance are expressed explicitly.

### Java
- Abstract methods implicitly allow overriding (no keyword needed to make them overridable).
- Instance methods (including methods in abstract classes) are NON-final and overridable by default, unless explicitly marked `final`.
- You must explicitly mark methods as `abstract` or `final` to change their behavior.

```java
abstract class Animal {
    abstract void makeSound();     // Must be implemented in concrete subclasses; overridable.
    void sleep() { }               // Overridable by default (not final).

    public void eat() { }          // Also overridable unless declared final.

    public final void die() { }    // Cannot be overridden.
}
```

### Kotlin
- Abstract members are `open` by definition and must be overridden in concrete subclasses.
- Non-abstract members are `final` by default; use `open` to allow overriding.
- You must explicitly use `open`/`final`/`abstract` to express inheritance and overriding intentions.

```kotlin
abstract class Animal {
    abstract fun makeSound()       // Must be implemented; open by nature.
    fun sleep() { }                // final by default; cannot be overridden.

    open fun eat() { }             // Explicitly open; can be overridden.
}
```

**Comparison table:**

| Member type      | Java                                  | Kotlin                                  |
|------------------|----------------------------------------|-----------------------------------------|
| Abstract method  | Always overridable                     | `abstract` members are effectively open |
| Regular method   | Overridable unless marked `final`      | `final` by default; needs `open`        |
| Abstract class   | Can be extended                        | Can be extended                         |

**Philosophy difference:**
- Java: More permissive by default; most methods are overridable unless made `final`.
- Kotlin: More explicit and restrictive by default; methods are `final` unless explicitly marked `open`.

This makes Kotlin's inheritance model more explicit and intentional. See also [[c-kotlin]].

## Дополнительные вопросы (RU)

- Как эти значения по умолчанию для наследования влияют на проектирование API в Kotlin по сравнению с Java?
- В каких случаях вы намеренно помечаете члены как `final`, `open` или `abstract`?
- Какие типичные подводные камни возникают при переносе кода на Kotlin из Java с активным использованием наследования?

## Follow-ups

- How do these inheritance defaults affect API design in Kotlin vs Java?
- When would you intentionally mark members as `final`, `open`, or `abstract`?
- What common pitfalls arise when porting inheritance-heavy Java code to Kotlin?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-structured-concurrency-patterns--kotlin--hard]]
