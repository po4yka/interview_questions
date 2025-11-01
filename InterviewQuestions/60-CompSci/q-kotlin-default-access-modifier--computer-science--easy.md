---
id: 20251012-12271111120
title: "Kotlin Default Access Modifier / Модификатор доступа по умолчанию в Kotlin"
aliases: []
topic: computer-science
subtopics: [access-modifiers, type-system, class-features]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-dispatcher-performance--kotlin--hard, q-kotlin-generics--kotlin--hard, q-debounce-search-coroutines--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - 
  - difficulty/easy
---
# Какой модификатор доступа по умолчанию используется в Kotlin?

# Question (EN)
> What is the default access modifier in Kotlin?

# Вопрос (RU)
> Какой модификатор доступа по умолчанию используется в Kotlin?

---

## Answer (EN)

The default access modifier in Kotlin is **`public`**. If you don't specify any visibility modifier, the declaration is public.

**Access Modifiers in Kotlin:**

```kotlin
// Public (default) - visible everywhere
class PublicClass  // Same as: public class PublicClass

// Private - visible only in the same file (for top-level) or class
private class PrivateClass

// Internal - visible in the same module
internal class InternalClass

// Protected - visible in class and subclasses (only for class members)
open class Base {
    protected val protectedProperty = 42
}
```

**Comparison with Java:**

| Modifier | Kotlin Default | Java Default |
|----------|----------------|---------------|
| Top-level classes | `public` | package-private |
| Class members | `public` | package-private |

**Example:**
```kotlin
// All public by default:
class User(val name: String)  // public class, public property

fun greet() = "Hello"  // public function

val counter = 0  // public property
```

**Key differences from Java:**
- Kotlin: `public` by default
- Java: package-private (no modifier) by default
- Kotlin has `internal` (module visibility) instead of package-private

---

## Ответ (RU)

Модификатор доступа по умолчанию в Kotlin — это **`public`**. Если не указан модификатор видимости, объявление является публичным.

**Модификаторы доступа в Kotlin:**

```kotlin
// Public (по умолчанию) - виден везде
class PublicClass  // То же что: public class PublicClass

// Private - виден только в том же файле (для top-level) или классе
private class PrivateClass

// Internal - виден в том же модуле
internal class InternalClass

// Protected - виден в классе и подклассах (только для членов класса)
open class Base {
    protected val protectedProperty = 42
}
```

**Сравнение с Java:**

| Модификатор | Kotlin по умолчанию | Java по умолчанию |
|----------|----------------|---------------|
| Top-level классы | `public` | package-private |
| Члены класса | `public` | package-private |

**Пример:**
```kotlin
// Всё public по умолчанию:
class User(val name: String)  // public класс, public свойство

fun greet() = "Hello"  // public функция

val counter = 0  // public свойство
```

**Ключевые отличия от Java:**
- Kotlin: `public` по умолчанию
- Java: package-private (без модификатора) по умолчанию
- В Kotlin есть `internal` (видимость в модуле) вместо package-private

## Related Questions

- [[q-dispatcher-performance--kotlin--hard]]
- [[q-kotlin-generics--kotlin--hard]]
- [[q-debounce-search-coroutines--kotlin--medium]]
