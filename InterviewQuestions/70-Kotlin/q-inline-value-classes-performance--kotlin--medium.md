---
tags:
  - kotlin
  - inline-classes
  - value-classes
  - performance
  - optimization
  - zero-cost-abstractions
difficulty: medium
status: draft
---

# Inline Value Classes and Performance

# Question (EN)
> How do inline value classes work? When should you use them for performance? What are the limitations?

# Вопрос (RU)
> Как работают inline value классы? Когда следует использовать их для производительности? Каковы ограничения?

---

## Answer (EN)

**Inline value classes** (formerly inline classes) are zero-cost wrappers that provide type safety without runtime overhead by being inlined at compile time.

---

### Basic Value Class

```kotlin
@JvmInline
value class UserId(val value: Int)

@JvmInline
value class Email(val value: String)

fun sendEmail(userId: UserId, email: Email) {
    // Type-safe!
}

// Compile-time: arguments are just Int and String
// No object allocation!
```

---

### Performance Benefit

**Without value class:**

```kotlin
data class UserId(val value: Int) // Regular class

fun process(id: UserId) {
    println(id.value)
}

// Every call allocates object:
process(UserId(123)) // Heap allocation
```

**With value class:**

```kotlin
@JvmInline
value class UserId(val value: Int)

fun process(id: UserId) {
    println(id.value)
}

// No allocation - inlined to primitive:
process(UserId(123)) // Just passes 123 as Int
```

---

### When to Use

**✅ Type-safe primitives:**

```kotlin
@JvmInline
value class Meters(val value: Double)

@JvmInline
value class Seconds(val value: Double)

fun calculateSpeed(distance: Meters, time: Seconds): Double {
    return distance.value / time.value
}

// Cannot mix up units:
// calculateSpeed(Seconds(10), Meters(100)) // ❌ Compile error!
```

**✅ API keys, IDs:**

```kotlin
@JvmInline
value class ApiKey(val value: String)

@JvmInline
value class SessionToken(val value: String)

fun authenticate(apiKey: ApiKey, token: SessionToken) {
    // Cannot pass token as apiKey
}
```

---

### Limitations

**1. Single property:**

```kotlin
// ✅ Valid
@JvmInline
value class Name(val value: String)

// ❌ Invalid
@JvmInline
value class Person(val name: String, val age: Int) // Multiple properties
```

**2. No identity:**

```kotlin
val id1 = UserId(123)
val id2 = UserId(123)

// No object identity
// id1 === id2 // Cannot compare by reference
id1 == id2 // ✅ Value equality
```

**3. Boxing scenarios:**

```kotlin
@JvmInline
value class UserId(val value: Int)

// Boxed as generic:
val list: List<UserId> = listOf(UserId(1))

// Boxed when null:
val nullable: UserId? = null // Boxed

// Boxed as Any:
val any: Any = UserId(1) // Boxed
```

---

## Ответ (RU)

**Inline value классы** - это обертки без затрат, обеспечивающие безопасность типов без runtime накладных расходов путем инлайнинга во время компиляции.

### Преимущество производительности

Нет аллокации объектов - значение передается как примитив.

### Когда использовать

- Безопасные по типам примитивы (метры, секунды)
- API ключи, ID
- Обертки для улучшения читаемости

### Ограничения

1. Только одно свойство
2. Нет идентичности объекта
3. Boxing в некоторых сценариях (generics, nullable, Any)

Value классы обеспечивают type-safety без performance overhead.
