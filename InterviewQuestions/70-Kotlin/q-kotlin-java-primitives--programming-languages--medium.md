---
id: "20251015082237236"
title: "Kotlin Java Primitives / Примитивы Kotlin и Java"
topic: computer-science
difficulty: medium
status: draft
created: 2025-10-15
tags: - java
  - kotlin
  - primitives
  - programming-languages
  - types
  - wrappers
---
# Какие примитивы есть в Kotlin, а какие в Java?

# Question (EN)
> What primitives exist in Kotlin and Java?

# Вопрос (RU)
> Какие примитивы есть в Kotlin, а какие в Java?

---

## Answer (EN)

### Java Primitives

Java has **8 primitive types**:

| Type | Size | Range | Wrapper Class |
|------|------|-------|---------------|
| `byte` | 8 bit | -128 to 127 | `Byte` |
| `short` | 16 bit | -32,768 to 32,767 | `Short` |
| `int` | 32 bit | -2³¹ to 2³¹-1 | `Integer` |
| `long` | 64 bit | -2⁶³ to 2⁶³-1 | `Long` |
| `float` | 32 bit | IEEE 754 | `Float` |
| `double` | 64 bit | IEEE 754 | `Double` |
| `char` | 16 bit | Unicode character | `Character` |
| `boolean` | 1 bit | `true` / `false` | `Boolean` |

**Java code:**
```java
// Primitives - stored on stack, no methods
int x = 10;
double y = 3.14;
boolean flag = true;

// Wrapper classes - stored on heap, have methods
Integer boxed = 10;  // Autoboxing
int unboxed = boxed;  // Unboxing

// Cannot be null
int value = null;  // Compilation error
Integer nullable = null;  // OK - wrapper class
```

### Kotlin "Primitives"

Kotlin **has no primitive types** from user perspective. Instead, it uses **wrapper classes** that compile to JVM primitives when possible:

| Kotlin Type | JVM Primitive | JVM Wrapper |
|-------------|---------------|-------------|
| `Byte` | `byte` | `java.lang.Byte` |
| `Short` | `short` | `java.lang.Short` |
| `Int` | `int` | `java.lang.Integer` |
| `Long` | `long` | `java.lang.Long` |
| `Float` | `float` | `java.lang.Float` |
| `Double` | `double` | `java.lang.Double` |
| `Char` | `char` | `java.lang.Character` |
| `Boolean` | `boolean` | `java.lang.Boolean` |

**Kotlin code:**
```kotlin
// All look like objects, but compile to primitives when possible
val x: Int = 10          // Compiles to: int x = 10
val y: Double = 3.14     // Compiles to: double y = 3.14
val flag: Boolean = true // Compiles to: boolean flag = true

// Can call methods (they're objects in Kotlin)
val hex = 255.toString(16)  // "ff"
val abs = (-10).absoluteValue  // 10

// Nullable types compile to wrapper classes
val nullable: Int? = null    // Compiles to: Integer nullable = null
val notNull: Int = 10        // Compiles to: int notNull = 10
```

### Key Differences

**1. Unified Type System:**
```kotlin
// Kotlin: Everything is an object
fun <T> identity(value: T): T = value

val x = identity(42)  // Works! Int is an object
val s = identity("hello")  // Also works!

// Java: Primitives are not objects
// Need separate methods or autoboxing
```

**2. Nullability:**
```kotlin
// Kotlin: Explicit nullable vs non-nullable
val notNull: Int = 10      // Cannot be null
val nullable: Int? = null  // Can be null

// Java: Primitives cannot be null, wrappers can
int primitive = 10;        // Cannot be null
Integer wrapper = null;    // Can be null
```

**3. No Autoboxing Issues:**
```kotlin
// Kotlin: No surprises
val a: Int = 1000
val b: Int = 1000
println(a == b)        // true (value equality)
println(a === b)       // depends on compilation (referential)

// Java: Autoboxing can cause surprises
Integer a = 1000;
Integer b = 1000;
System.out.println(a == b);  // false! (reference equality)
System.out.println(a.equals(b));  // true (value equality)
```

**4. Smart Compilation:**
```kotlin
fun add(a: Int, b: Int): Int = a + b
// Compiles to efficient primitive arithmetic

fun addNullable(a: Int?, b: Int?): Int? {
    if (a == null || b == null) return null
    return a + b
}
// Uses wrapper classes internally
```

### When Kotlin Uses Primitives vs Wrappers

**Compiles to JVM primitives:**
- Non-nullable types in local variables
- Non-nullable types in parameters/return types
- Non-nullable array elements: `IntArray`, `DoubleArray`

**Compiles to wrapper classes:**
- Nullable types: `Int?`, `Boolean?`
- Generic type parameters: `List<Int>`
- Platform types from Java
- When stored in `Array<Int>`

```kotlin
val primitive: Int = 10           // int (primitive)
val nullable: Int? = 10           // Integer (wrapper)
val list: List<Int> = listOf(1)   // List<Integer> (wrapper)
val array: IntArray = intArrayOf(1)  // int[] (primitive array)
val boxedArray: Array<Int> = arrayOf(1)  // Integer[] (wrapper array)
```

### Summary

| Aspect | Java | Kotlin |
|--------|------|--------|
| **Primitives** | Yes (8 types) | No (unified type system) |
| **Wrappers** | Separate classes | Used automatically |
| **Methods on primitives** | No | Yes |
| **Nullability** | Wrappers only | Explicit `?` suffix |
| **Compilation** | Primitives vs objects | Optimized to primitives when possible |

---

## Ответ (RU)

Java использует примитивные типы: byte, short, int, long, float, double, char, boolean. Kotlin использует обёртки (Int, Double, Boolean и др.), которые компилируются в примитивы при необходимости.

