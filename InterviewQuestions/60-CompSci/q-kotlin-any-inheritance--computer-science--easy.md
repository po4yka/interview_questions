---
id: 20251012-12271111111
title: "Kotlin Any Inheritance / Наследование от Any в Kotlin"
aliases: []
topic: computer-science
subtopics: [access-modifiers, type-system, null-safety]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-default-access-modifier--programming-languages--easy, q-channel-buffering-strategies--kotlin--hard, q-partition-function--kotlin--easy]
created: 2025-10-15
updated: 2025-10-31
tags:
  - 
  - difficulty/easy
---
# Все классы Kotlin наследуются от Any

# Question (EN)
> All Kotlin classes inherit from Any

# Вопрос (RU)
> Все классы Kotlin наследуются от Any

---

## Answer (EN)

In Kotlin, **all classes by default inherit from the `Any` class**. This class is the root (base) class for all other classes in Kotlin. It is analogous to the `Object` class in Java.

**Key points:**

- **Any** is the supertype of all non-nullable types
- Analogous to Java's `Object` class
- Every class implicitly extends `Any` (even without explicit declaration)

**Any provides three methods:**
```kotlin
open class Any {
    public open operator fun equals(other: Any?): Boolean
    public open fun hashCode(): Int
    public open fun toString(): String
}
```

**Example:**
```kotlin
class MyClass  // Implicitly extends Any

val obj: Any = MyClass()  // Can assign to Any
obj.toString()            // Methods from Any available
obj.equals(obj)
obj.hashCode()
```

**Type hierarchy:**
```
Any (root)
 String
 Int
 List<T>
 YourCustomClass
```

**Note**: For nullable types, the root is `Any?`

---

## Ответ (RU)

В Kotlin **все классы по умолчанию наследуются от класса `Any`**. Этот класс является корневым (базовым) классом для всех других классов в Kotlin. Он аналогичен классу `Object` в Java.

**Ключевые моменты:**

- **Any** является супертипом всех ненулевых типов
- Аналогичен классу `Object` в Java
- Каждый класс неявно расширяет `Any` (даже без явного объявления)

**Any предоставляет три метода:**
```kotlin
open class Any {
    public open operator fun equals(other: Any?): Boolean
    public open fun hashCode(): Int
    public open fun toString(): String
}
```

**Пример:**
```kotlin
class MyClass  // Неявно расширяет Any

val obj: Any = MyClass()  // Можно присвоить Any
obj.toString()            // Методы из Any доступны
obj.equals(obj)
obj.hashCode()
```

**Иерархия типов:**
```
Any (корень)
 String
 Int
 List<T>
 YourCustomClass
```

**Примечание**: Для nullable типов корнем является `Any?`

## Related Questions

- [[q-kotlin-default-access-modifier--programming-languages--easy]]
- [[q-channel-buffering-strategies--kotlin--hard]]
- [[q-partition-function--kotlin--easy]]
