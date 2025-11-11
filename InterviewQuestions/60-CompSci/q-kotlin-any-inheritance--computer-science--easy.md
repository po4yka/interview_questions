---
id: cs-015
title: "Kotlin Any Inheritance / Наследование от Any в Kotlin"
aliases: []
topic: kotlin
subtopics: [type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-concepts--kotlin--medium, q-abstract-class-vs-interface--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [kotlin/type-system, difficulty/easy]
---

# Вопрос (RU)
> Все классы Kotlin наследуются от `Any`

# Question (EN)
> All Kotlin classes inherit from `Any`

---

## Ответ (RU)

В Kotlin пользовательские классы (и большинство встроенных типов-классов) по умолчанию наследуются от класса `Any`. Этот класс является корневым (базовым) классом для всех других ненулевых типов в Kotlin. Он аналогичен классу `Object` в Java.

Важно: под "наследуются от `Any`" здесь понимаются именно классы; интерфейсы не имеют `Any` своим суперклассом, но `Any` является общим супертипом в системе типов.

**Ключевые моменты:**

- `Any` является супертипом всех ненулевых типов (включая такие языковые типы, как `Int`, `Boolean` и др.)
- Аналогичен классу `Object` в Java
- Каждый класс неявно имеет базовый класс `Any`, если явно не указан другой суперкласс

**`Any` предоставляет три базовых метода (концептуальная сигнатура):**
```kotlin
open class Any {
    public open operator fun equals(other: Any?): Boolean
    public open fun hashCode(): Int
    public open fun toString(): String
}
```

**Пример:**
```kotlin
class MyClass  // Неявно наследуется от Any

val obj: Any = MyClass()  // Можно присвоить переменной типа Any
obj.toString()            // Методы из Any доступны
obj.equals(obj)
obj.hashCode()
```

**Иерархия типов (упрощённо):**
```
Any (корень)
 String
 Int
 List<T>
 YourCustomClass
```

**Примечание**: Для nullable типов соответствующим корневым супертипом является `Any?`.

## Answer (EN)

In Kotlin, user-defined classes (and most built-in class types) by default inherit from the `Any` class. This class is the root (base) class for all other non-nullable types in Kotlin. It is analogous to the `Object` class in Java.

Note: "inherit from `Any`" here refers to class types; interfaces do not extend `Any` as a superclass, but `Any` is a common supertype in the type system.

**Key points:**

- `Any` is the supertype of all non-nullable types (including Kotlin primitive types like `Int`, `Boolean`, etc., at the language level)
- Analogous to Java's `Object` class
- Every class implicitly has `Any` as its base class if no other superclass is specified

**Any provides three core methods (conceptual signature):**
```kotlin
open class Any {
    public open operator fun equals(other: Any?): Boolean
    public open fun hashCode(): Int
    public open fun toString(): String
}
```

**Example:**
```kotlin
class MyClass  // Implicitly inherits from Any

val obj: Any = MyClass()  // Can assign to Any
obj.toString()            // Methods from Any available
obj.equals(obj)
obj.hashCode()
```

**Type hierarchy (simplified):**
```
Any (root)
 String
 Int
 List<T>
 YourCustomClass
```

**Note**: For nullable types, the corresponding root supertype is `Any?`.

## Дополнительные вопросы (RU)

- [[q-abstract-class-vs-interface--kotlin--medium]]
- Объясните отличие `Any` от `Any?` в контексте иерархии типов.
- Как соотносится `Any` в Kotlin с `Object` в Java при интеропе?
- Почему интерфейсы в Kotlin не наследуются от `Any` как класса, но тем не менее совместимы с ним как с супертипом?

## Follow-ups

- [[q-abstract-class-vs-interface--kotlin--medium]]
- Explain the difference between `Any` and `Any?` in the type hierarchy.
- How does Kotlin's `Any` relate to Java's `Object` in Kotlin/JVM interop?
- Why don't interfaces in Kotlin extend `Any` as a class but are still compatible with it as a common supertype?

## Ссылки (RU)

- [[c-concepts--kotlin--medium]]

## References (EN)

- [[c-concepts--kotlin--medium]]

## Related Questions

- [[q-abstract-class-vs-interface--kotlin--medium]]
