---
id: kotlin-031
title: "Nested Class vs Inner Class / Вложенный vs внутренний класс"
aliases: ["Nested Class vs Inner Class", "Вложенный vs внутренний класс"]

# Classification
topic: kotlin
subtopics: [classes, inner-class, nested-class]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, q-coroutine-memory-leaks--kotlin--hard, q-retry-operators-flow--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-11-10

tags: [classes, difficulty/medium, inner-classes, kotlin, nested-classes, oop]
---
# Вопрос (RU)
> В чем разница между вложенным (nested) и внутренним (inner) классом в Kotlin?

# Question (EN)
> What is the difference between nested class and inner class in Kotlin?

## Ответ (RU)

### Вложенный Класс (Nested Class)

Класс, объявленный внутри другого класса. **Не может получить доступ к членам внешнего класса** (включая `private`). Не требует экземпляра внешнего класса для создания.

```kotlin
class Outer {
    private val bar: Int = 1

    class Nested {
        fun foo() = 2
    }
}

val demo = Outer.Nested().foo()  // Не нужен экземпляр Outer!
```

### Внутренний Класс (Inner Class)

Вложенный класс с ключевым словом `inner`. **Может получить доступ ко всем членам внешнего класса**, включая приватные. Требует экземпляр внешнего класса.

Важно: внутренний класс неявно хранит ссылку на экземпляр внешнего класса.

```kotlin
class Outer {
    private val bar: Int = 1

    inner class Inner {
        fun foo() = bar  // Доступ к private-членам Outer
    }
}

val demo = Outer().Inner().foo()  // Нужен экземпляр Outer!
```

### Ключевые Отличия

| Характеристика | Вложенный класс (Nested) | Внутренний класс (Inner) |
|----------------|--------------------------|--------------------------|
| **Ключевое слово** | Нет (по умолчанию) | `inner` |
| **Доступ к внешнему классу** | Нет доступа | Есть доступ |
| **Создание экземпляра** | `Outer.Nested()` | `outerInstance.Inner()` |
| **Java-эквивалент** | Static nested class | Non-static nested class |
| **Память** | Не содержит ссылки на внешний класс | Хранит ссылку на экземпляр внешнего класса |
| **Типичные случаи использования** | Вспомогательные/utility-классы, логическая группировка | Коллбеки, тесно связанная с внешним классом логика |

### Kotlin Vs Java: Сравнение

| Kotlin | Java |
|--------|------|
| Вложенный класс (по умолчанию) | Static nested class |
| Внутренний класс (`inner`) | Non-static nested class |

### Лучшие Практики

**Используйте вложенный класс (Nested), когда:**
- Внутренний тип не нуждается в доступе к членам внешнего класса.
- Нужна только логическая группировка.
- Важно избежать удержания ссылки на внешний объект и потенциальных утечек памяти.

**Используйте внутренний класс (Inner), когда:**
- Нужен прямой доступ к полям/методам внешнего класса.
- Логика тесно связана с состоянием внешнего класса.
- Реализуете коллбеки/листенеры, которым нужен контекст внешнего класса.

### Пример: Влияние На Память

```kotlin
class Activity {
    // ПЛОХО: inner-класс неявно удерживает ссылку на Activity (риск утечки памяти)
    inner class BackgroundTask {
        fun doWork() {
            // Может обращаться к членам Activity
        }
    }

    // ХОРОШО: вложенный класс не хранит ссылку на Activity
    class StaticHelper {
        fun processData(data: Data) {
            // Независимая обработка данных
        }
    }
}
```

**Краткое резюме (RU)**: Вложенные классы в Kotlin по умолчанию ведут себя как `static` nested классы в Java: не имеют доступа к членам внешнего класса и не требуют экземпляра внешнего класса. Внутренние классы с `inner` аналогичны не-`static` вложенным классам в Java: имеют доступ к членам внешнего класса и хранят ссылку на его экземпляр, что важно учитывать с точки зрения памяти.

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

### Kotlin Vs Java Comparison

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

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)
- [[c-kotlin]]
- [Nested and Inner Classes - Kotlin](https://kotlinlang.org/docs/nested-classes.html)
- [Understanding Nested and Inner Classes in Kotlin](https://medium.com/@sandeepkella23/understanding-nested-and-inner-classes-in-kotlin-ae1c4d699053)

## References
- [[c-kotlin]]
- [Nested and Inner Classes - Kotlin](https://kotlinlang.org/docs/nested-classes.html)
- [Understanding Nested and Inner Classes in Kotlin](https://medium.com/@sandeepkella23/understanding-nested-and-inner-classes-in-kotlin-ae1c4d699053)

## Связанные Вопросы (RU)

### Связанные (Medium)
- [[q-inner-nested-classes--kotlin--medium]] - Классы
- [[q-class-initialization-order--kotlin--medium]] - Классы
- [[q-enum-class-advanced--kotlin--medium]] - Классы
- [[q-value-classes-inline-classes--kotlin--medium]] - Классы

## Related Questions

### Related (Medium)
- [[q-inner-nested-classes--kotlin--medium]] - Classes
- [[q-class-initialization-order--kotlin--medium]] - Classes
- [[q-enum-class-advanced--kotlin--medium]] - Classes
- [[q-value-classes-inline-classes--kotlin--medium]] - Classes