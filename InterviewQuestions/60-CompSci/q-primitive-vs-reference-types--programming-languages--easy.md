---
topic: programming-languages
tags:
  - java
  - kotlin
  - memory
  - primitive-types
  - programming-languages
  - reference-types
difficulty: easy
status: draft
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-programming-languages
related_questions: []
---

# В чем разница примитивного и ссылочного типов

# Question (EN)
> What is the difference between primitive and reference types?

# Вопрос (RU)
> В чем разница примитивного и ссылочного типов?

---

## Answer (EN)

### Primitive Types

**Store values directly**, cannot be null, and have no methods (in Java):

**Java primitives:**
```java
// Primitive types (8 in Java)
int x = 10;           // Stores value 10 directly
double y = 3.14;      // Stores value 3.14 directly
boolean flag = true;  // Stores true/false directly
char c = 'A';         // Stores character directly

// Cannot be null
int value = null;  // Compilation error!

// No methods
// x.toString();   // Error! Primitives have no methods
```

**Characteristics:**
- Stored on **stack** (or inline in objects)
- Fixed size: `int` = 4 bytes, `double` = 8 bytes
- Fast access
- Default values: `0`, `false`, `\0`
- Cannot be null
- No methods

### Reference Types

**Store references (pointers)** to objects in memory, can be null:

**Java reference types:**
```java
// Reference types
String text = "Hello";        // Stores reference to String object
Integer num = 10;             // Wrapper class (reference type)
int[] array = {1, 2, 3};      // Array (reference type)
MyClass obj = new MyClass();  // Custom class (reference type)

// Can be null
String nullText = null;  // OK
Integer nullNum = null;  // OK

// Have methods
text.length();           // OK
text.toUpperCase();      // OK
```

**Characteristics:**
- Stored on **heap** (reference on stack)
- Variable size
- Slower access (indirection)
- Default value: `null`
- Can be null
- Have methods

### Memory Representation

**Primitive type:**
```
Stack:

 x: 10   (value stored directly)

```

**Reference type:**
```
Stack:              Heap:
        
 ref: →  "Hello"       (actual object)
        
```

### Kotlin Context

**Kotlin doesn't expose primitive types** to the programmer, but uses them under the hood:

```kotlin
// All look like objects in Kotlin
val x: Int = 10           // Compiles to int (primitive)
val y: Int? = 10          // Compiles to Integer (reference)

val text: String = "Hi"   // String (reference type)

// All have methods in Kotlin
val hex = x.toString(16)  // "a"
val abs = (-5).absoluteValue  // 5

// Nullable types are always reference types
val nullable: Int? = null  // Integer (reference)
val notNull: Int = 10      // int (primitive in bytecode)
```

### Comparison Table

| Aspect | Primitive Types | Reference Types |
|--------|----------------|-----------------|
| **Storage** | Stack (direct value) | Heap (via reference) |
| **Memory** | Fixed size | Variable size |
| **Default** | 0, false, \0 | null |
| **Nullable** | No (Java) | Yes |
| **Methods** | No (Java) | Yes |
| **Speed** | Faster | Slower (indirection) |
| **Examples (Java)** | int, double, boolean | String, Integer, arrays, objects |
| **Examples (Kotlin)** | Not exposed | All types (Int, String, classes) |

### Boxing and Unboxing (Java)

**Converting between primitive and reference:**

```java
// Boxing: primitive → wrapper
int primitive = 10;
Integer wrapped = Integer.valueOf(primitive);  // Manual boxing
Integer autoBoxed = primitive;                 // Auto-boxing

// Unboxing: wrapper → primitive
Integer wrapped = 10;
int primitive = wrapped.intValue();  // Manual unboxing
int autoUnboxed = wrapped;           // Auto-unboxing

// Performance impact
Integer sum = 0;
for (int i = 0; i < 1000; i++) {
    sum += i;  // Auto-boxing/unboxing in every iteration! Slow!
}

// Better: use primitive
int sum = 0;
for (int i = 0; i < 1000; i++) {
    sum += i;  // No boxing, faster
}
```

### Practical Examples

**1. Collections (Java):**
```java
// Must use wrapper types in collections
List<Integer> numbers = new ArrayList<>();  // Integer, not int
numbers.add(10);  // Auto-boxing

// Kotlin
val numbers = listOf(1, 2, 3)  // List<Int> (uses Integer internally)
```

**2. Null handling:**
```java
// Java primitive - cannot be null
int age = getAge();  // What if age is unknown? Can't use null!

// Solution: use wrapper
Integer age = getAge();  // Can return null
if (age != null) {
    // Use age
}

// Kotlin - explicit nullable types
val age: Int? = getAge()  // Can be null
if (age != null) {
    // Use age
}
```

**3. Memory efficiency:**
```java
// Array of primitives - memory efficient
int[] primitives = new int[1000];  // 4000 bytes

// Array of references - more memory
Integer[] wrapped = new Integer[1000];  // 4000 bytes + 1000 objects overhead

// Kotlin - specialized arrays
val primitives = IntArray(1000)  // int[] (efficient)
val wrapped = Array<Int>(1000) { 0 }  // Integer[] (less efficient)
```

### When to Use Each

**Use primitive types (or Kotlin's Int, Double, etc.):**
- Performance critical code
- Large arrays/collections
- When null is not needed
- Math-heavy computations

**Use reference types (or Kotlin's nullable types):**
- Need null values
- Collections/generics
- When need methods (in Java)
- Complex objects

### Summary

| Feature | Primitive | Reference |
|---------|-----------|-----------|
| **Value storage** | Direct | Via reference |
| **Can be null** | No (Java) | Yes |
| **Has methods** | No (Java) | Yes |
| **Memory** | Efficient | More overhead |
| **Speed** | Fast | Slower |
| **Kotlin visibility** | Hidden (compiled from Int) | All types |

In **Java**: primitives and reference types are clearly separated.
In **Kotlin**: everything looks like objects, but primitives are used internally when possible.

---

## Ответ (RU)

Примитивные типы хранят значения напрямую, не могут быть null и не имеют методов. Ссылочные типы — это объекты которые хранят ссылки на данные в памяти и могут быть null.


---

## Related Questions

### Android Implementation
- [[q-sharedpreferences-definition--android--easy]] - Memory Management
- [[q-leakcanary-library--android--easy]] - Memory Management
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - Memory Management
- [[q-optimize-memory-usage-android--android--medium]] - Memory Management
- [[q-stack-heap-memory-multiple-threads--android--medium]] - Memory Management
- [[q-tasks-back-stack--android--medium]] - Memory Management
- [[q-memory-leak-vs-oom-android--android--medium]] - Memory Management
