---
id: 20251005-235007
title: "Functional Interfaces vs Type Aliases / Функциональные интерфейсы vs псевдонимы типов"
aliases: []

# Classification
topic: kotlin
subtopics: [functional-interfaces, type-aliases, sam, comparison]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-sam-interfaces--kotlin--medium, q-type-aliases--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, functional-interfaces, type-aliases, sam, difficulty/medium]
---

# Question (EN)
> What is the difference between functional interfaces and type aliases in Kotlin?

# Вопрос (RU)
> В чем разница между функциональными интерфейсами и псевдонимами типов в Kotlin?

---

## Answer (EN)

### Functional Interface (SAM)

An interface with **only one abstract method**. Declared with `fun` modifier.

```kotlin
fun interface KRunnable {
   fun invoke()
}
```

### Type Alias

Alternative name for an **existing type**. Doesn't create new type.

```kotlin
typealias MyHandler = (Int, String, Any) -> Unit
typealias Predicate<T> = (T) -> Boolean
```

### Key Differences

| Feature | Functional Interface | Type Alias |
|---------|---------------------|------------|
| **Creates new type** | Yes | No |
| **Members** | Multiple non-abstract + one abstract | One member only |
| **Extensions** | Can add interface-specific extensions | Extensions apply to underlying type |
| **Implements/Extends** | Can implement and extend other interfaces | Just a name |
| **Type safety** | Stronger (distinct type) | Weaker (same as underlying) |

### When to Use Each

**Functional Interface** when:
- API needs more than just a function (contracts, operations)
- Need type-specific extensions
- Want distinct type for type safety

**Type Alias** when:
- API accepts simple function with specific signature
- Want shorter name for complex type
- Don't need additional operations

### Example Comparison

```kotlin
// Type alias - simple renaming
typealias ClickHandler = (View) -> Unit

fun setClickListener(handler: ClickHandler) {
    // handler is just (View) -> Unit
}

// Functional interface - new type
fun interface ClickListener {
    fun onClick(view: View)
}

// Can add extensions specific to ClickListener
fun ClickListener.withLogging(): ClickListener = ClickListener { view ->
    println("Clicked: $view")
    onClick(view)
}

// Type alias extensions affect ALL functions of that type
fun ClickHandler.withLogging(): ClickHandler = { view ->
    println("Clicked: $view")
    this(view)  // Affects all (View) -> Unit functions!
}
```

**English Summary**: Functional interfaces create new distinct types, can have multiple non-abstract members, and support interface-specific extensions. Type aliases just rename existing types for readability. Choose functional interfaces for complex contracts; type aliases for simple function type renaming.

## Ответ (RU)

### Функциональный интерфейс (SAM)

Интерфейс с **только одним абстрактным методом**. Объявляется с модификатором `fun`.

```kotlin
fun interface KRunnable {
   fun invoke()
}
```

### Псевдоним типа

Альтернативное имя для **существующего типа**. Не создает новый тип.

```kotlin
typealias MyHandler = (Int, String, Any) -> Unit
```

### Ключевые отличия

| Функция | Функциональный интерфейс | Псевдоним типа |
|---------|--------------------------|----------------|
| **Создает новый тип** | Да | Нет |
| **Члены** | Несколько не-абстрактных + один абстрактный | Только один член |
| **Расширения** | Можно добавить специфичные для интерфейса | Применяются к базовому типу |
| **Типобезопасность** | Сильнее (отдельный тип) | Слабее (тот же что базовый) |

**Краткое содержание**: Функциональные интерфейсы создают новые отдельные типы, могут иметь несколько не-абстрактных членов и поддерживают специфичные для интерфейса расширения. Псевдонимы типов просто переименовывают существующие типы для читаемости.

---

## References
- [Functional (SAM) Interfaces - Kotlin](https://kotlinlang.org/docs/fun-interfaces.html)
- [Type Aliases - Kotlin](https://kotlinlang.org/docs/type-aliases.html)

## Related Questions
- [[q-kotlin-sam-interfaces--kotlin--medium]]
- [[q-type-aliases--kotlin--medium]]
