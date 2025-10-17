---
id: 20251012-12271111120
title: "Kotlin Default Access Modifier / Модификатор доступа по умолчанию в Kotlin"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - access-modifiers
  - kotlin
  - programming-languages
  - public
  - syntax
  - visibility
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

Модификатор доступа по умолчанию в Kotlin — это `public`. Если не указан модификатор видимости, объявление является публичным.

