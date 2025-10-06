---
tags:
  - collections
  - comparison
  - java
  - kotlin
  - null-safety
  - programming-languages
  - type-inference
  - type-system
  - types
difficulty: medium
---

# Чем типы в Kotlin отличаются от типов в Java

**English**: How do Kotlin types differ from Java types?

## Answer

| Feature | Kotlin | Java |
|---------|--------|------|
| **Null Safety** | Variables cannot be null by default (`String` vs `String?`) | All objects can be null |
| **Collections** | Clear separation: `List` vs `MutableList` | No distinction (all mutable) |
| **Data Classes** | Automatic method generation with `data class` | Manual implementation required |
| **Type Inference** | Extensive: `val x = 10` | Limited (local variables with `var`) |
| **Smart Casts** | Automatic after `is` check | Explicit cast after `instanceof` |
| **Primitive Types** | No primitives (unified type system) | Separate primitives (`int`) and wrappers (`Integer`) |

**Examples:**

```kotlin
// Kotlin
val name: String = "John"        // Cannot be null
val nullable: String? = null     // Explicitly nullable
val list = listOf(1, 2, 3)       // Immutable
val x = 10                       // Type inferred

if (obj is String) {
    println(obj.length)          // Auto-cast
}
```

```java
// Java
String name = "John";             // Can be null
String nullable = null;           // No distinction
List<Integer> list = List.of(1, 2, 3); // Can be modified with reflection
int x = 10;                       // Must specify type

if (obj instanceof String) {
    println(((String) obj).length()); // Explicit cast
}
```

**Key differences:**
1. **Kotlin**: Null safety by default
2. **Kotlin**: Immutable/mutable collections distinction
3. **Kotlin**: Auto-generated methods for data classes
4. **Kotlin**: Better type inference
5. **Kotlin**: Smart casts after type checks

## Ответ

В Kotlin по умолчанию переменные не могут быть null, в отличие от Java где все объекты могут быть null...

