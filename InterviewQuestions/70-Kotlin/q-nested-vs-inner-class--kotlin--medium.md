---
id: 20251005-235009
title: "Nested Class vs Inner Class / Вложенный vs внутренний класс"
aliases: []

# Classification
topic: kotlin
subtopics: [nested-class, inner-class, classes, oop]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: reviewed
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, nested-class, inner-class, classes, oop, difficulty/medium]
---
## Question (EN)
> What is the difference between nested class and inner class in Kotlin?
## Вопрос (RU)
> В чем разница между вложенным (nested) и внутренним (inner) классом в Kotlin?

---

## Answer (EN)

### Nested Class

A class declared inside another class. **Cannot access outer class members** (including private). Don't need outer instance to create.

```kotlin
class Outer {
    private val bar: Int = 1

    class Nested {
        fun foo() = 2
    }
}

val demo = Outer.Nested().foo() // == 2
// No outer instance needed!
```

### Inner Class

A nested class marked with `inner` keyword. **Can access all members** of outer class (including private). Requires outer instance to create.

```kotlin
class Outer {
    private val bar: Int = 1

    inner class Inner {
        fun foo() = bar  // - Can access outer's private members
    }
}

val demo = Outer().Inner().foo() // == 1
// Needs Outer() instance!
```

### Key Differences

| Feature | Nested Class | Inner Class |
|---------|--------------|-------------|
| **Keyword** | None (default) | `inner` |
| **Outer class access** | - No | - Yes |
| **Instantiation** | `Outer.Nested()` | `outerInstance.Inner()` |
| **Java equivalent** | Static nested class | Non-static nested class |
| **Memory** | No reference to outer | Holds reference to outer |
| **Use case** | Utility classes, logical grouping | Callbacks, tightly coupled logic |

### Kotlin vs Java Comparison

| Kotlin | Java |
|--------|------|
| Nested class (default) | Static nested class |
| Inner class (`inner` keyword) | Non-static nested class |

### Best Practices

**Use Nested Class when**:
- Inner class doesn't need outer class interaction
- Want to avoid memory leaks (no outer reference)
- Logical grouping only

**Use Inner Class when**:
- Need access to outer class members
- Encapsulating logic tightly coupled with outer
- Implementing callbacks that need outer context

### Example: Memory Implications

```kotlin
class Activity {
    // - BAD - holds reference to Activity (memory leak risk)
    inner class BackgroundTask {
        fun doWork() {
            // Can access Activity members
        }
    }

    // - GOOD - no reference to Activity
    class StaticHelper {
        fun processData(data: Data) {
            // Independent processing
        }
    }
}
```

**English Summary**: Nested classes (default in Kotlin) are like Java static nested classes - no access to outer class, no outer instance needed. Inner classes (with `inner` keyword) are like Java non-static nested - can access outer members, need outer instance. Use nested for independence, inner for tight coupling. Nested classes avoid memory leaks from holding outer references.

## Ответ (RU)

### Вложенный класс (Nested)

Класс, объявленный внутри другого класса. **Не может получить доступ к членам внешнего класса**. Не требует экземпляра внешнего класса.

```kotlin
class Outer {
    private val bar: Int = 1

    class Nested {
        fun foo() = 2
    }
}

val demo = Outer.Nested().foo()  // Не нужен экземпляр Outer!
```

### Внутренний класс (Inner)

Вложенный класс с ключевым словом `inner`. **Может получить доступ ко всем членам** внешнего класса. Требует экземпляр внешнего класса.

```kotlin
class Outer {
    private val bar: Int = 1

    inner class Inner {
        fun foo() = bar  // - Доступ к private членам
    }
}

val demo = Outer().Inner().foo()  // Нужен экземпляр Outer!
```

### Ключевые отличия

| Функция | Nested | Inner |
|---------|--------|-------|
| **Ключевое слово** | Нет (по умолчанию) | `inner` |
| **Доступ к внешнему** | - Нет | - Да |
| **Создание** | `Outer.Nested()` | `outerInstance.Inner()` |
| **Java эквивалент** | Static nested class | Non-static nested |

**Краткое содержание**: Вложенные классы (по умолчанию в Kotlin) как Java static nested - нет доступа к внешнему, не нужен экземпляр внешнего. Внутренние классы (с `inner`) как Java non-static nested - могут обращаться к членам внешнего, нужен экземпляр. Используйте вложенные для независимости, внутренние для тесной связи.

---

## References
- [Nested and Inner Classes - Kotlin](https://kotlinlang.org/docs/nested-classes.html)
- [Understanding Nested and Inner Classes in Kotlin](https://medium.com/@sandeepkella23/understanding-nested-and-inner-classes-in-kotlin-ae1c4d699053)

## Related Questions
- [[q-object-companion-object--kotlin--medium]]
