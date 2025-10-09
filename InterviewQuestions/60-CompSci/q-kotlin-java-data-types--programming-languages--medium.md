---
tags:
  - data-types
  - java
  - kotlin
  - primitives
  - programming-languages
  - reference-types
  - type-system
  - types
difficulty: medium
status: reviewed
---

# Какие типы данных существуют в Java и Kotlin?

**English**: What data types exist in Java and Kotlin?

## Answer

In both Java and Kotlin, data types are divided into **primitive types** and **reference types**, but with important differences.

### Java Data Types

#### Primitive Types (8 types)
**Stored on stack, no methods:**
```java
byte b = 127;           // 8 bit
short s = 32767;        // 16 bit
int i = 2147483647;     // 32 bit
long l = 9223372036854775807L;  // 64 bit

float f = 3.14f;        // 32 bit floating point
double d = 3.14159;     // 64 bit floating point

char c = 'A';           // 16 bit Unicode character
boolean flag = true;    // true/false
```

#### Reference Types
**Stored on heap, have methods:**
```java
String text = "Hello";              // String
Integer num = 10;                   // Wrapper class
int[] array = {1, 2, 3};           // Array
List<String> list = new ArrayList<>();  // Collection
MyClass obj = new MyClass();        // Custom class
Runnable r = () -> {};             // Interface
```

### Kotlin Data Types

#### All Types are Objects
**No primitive types from user perspective:**
```kotlin
val b: Byte = 127         // Wrapper (compiles to byte when possible)
val s: Short = 32767      // Wrapper (compiles to short)
val i: Int = 2147483647   // Wrapper (compiles to int)
val l: Long = 9223372036854775807L  // Wrapper (compiles to long)

val f: Float = 3.14f      // Wrapper (compiles to float)
val d: Double = 3.14159   // Wrapper (compiles to double)

val c: Char = 'A'         // Wrapper (compiles to char)
val flag: Boolean = true  // Wrapper (compiles to boolean)
```

#### Reference Types
```kotlin
val text: String = "Hello"          // String
val list: List<String> = listOf()   // Collection
val map: Map<String, Int> = mapOf() // Map
val obj: MyClass = MyClass()        // Custom class

// Kotlin adds special types:
fun doNothing(): Unit { }           // Unit - like void but is an object
fun fail(): Nothing = throw Exception()  // Nothing - never returns
```

### Key Differences

#### 1. Type System

| Aspect | Java | Kotlin |
|--------|------|--------|
| **Primitive types** | Yes (8 types) | No (all are objects) |
| **Unified system** | No (primitives separate) | Yes (everything is object) |
| **Methods on numbers** | No (primitives) | Yes (all have methods) |

```java
// Java - primitives have no methods
int x = 10;
// x.toString();  // Error!
Integer y = 10;
y.toString();  // OK

// Kotlin - all have methods
val x: Int = 10
x.toString()  // OK! Int is an object
```

#### 2. Nullability

**Java - all reference types can be null:**
```java
// Primitives cannot be null
int x = null;  // Compilation error

// All reference types can be null
String s = null;        // OK
Integer i = null;       // OK
MyClass obj = null;     // OK
```

**Kotlin - explicit nullable vs non-nullable:**
```kotlin
// Non-nullable by default
val x: Int = 10
// x = null  // Compilation error!

val s: String = "Hello"
// s = null  // Compilation error!

// Nullable types with ?
val y: Int? = null       // OK
val text: String? = null  // OK
val obj: MyClass? = null  // OK
```

#### 3. Special Kotlin Types

**Unit** - equivalent to Java's `void`, but is an object:
```kotlin
fun doSomething(): Unit {
    println("Done")
}  // Returns Unit singleton

// Can be used as type parameter
val list: List<Unit> = listOf(Unit)

// Java equivalent
void doSomething() {
    System.out.println("Done");
}  // Returns nothing
```

**Nothing** - type for functions that never return:
```kotlin
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}

fun infiniteLoop(): Nothing {
    while (true) { }
}

// Used in type inference
val x = null  // Type is Nothing?
```

#### 4. Arrays

**Java - primitive arrays vs object arrays:**
```java
int[] primitives = {1, 2, 3};      // Primitive array
Integer[] objects = {1, 2, 3};     // Object array
String[] strings = {"a", "b"};     // Object array
```

**Kotlin - specialized array types:**
```kotlin
val primitives: IntArray = intArrayOf(1, 2, 3)  // int[] (primitives)
val objects: Array<Int> = arrayOf(1, 2, 3)      // Integer[] (objects)
val strings: Array<String> = arrayOf("a", "b")  // String[]

// Specialized primitive arrays
val bytes: ByteArray = byteArrayOf(1, 2)
val chars: CharArray = charArrayOf('a', 'b')
val doubles: DoubleArray = doubleArrayOf(1.0, 2.0)
```

### Type Hierarchy

**Java:**
```
Object (reference types)
  ├─ String
  ├─ Integer, Double, etc. (wrappers)
  ├─ Arrays
  └─ Custom classes

(primitives are separate, not part of hierarchy)
```

**Kotlin:**
```
Any (all types)
  ├─ Any? (nullable)
  ├─ Number
  │   ├─ Int, Double, Float, Long, Short, Byte
  │   └─ All are objects
  ├─ String
  ├─ Collections
  └─ Custom classes
      └─ Nothing (bottom type)
```

### Summary

| Feature | Java | Kotlin |
|---------|------|--------|
| **Primitives** | 8 primitive types (int, double, etc.) | No primitives (Int, Double wrappers) |
| **Reference types** | String, classes, arrays, interfaces | String, classes, collections |
| **Nullability** | All reference types nullable | Explicit nullable (?) vs non-nullable |
| **Type hierarchy** | Primitives separate from Object | All types inherit from Any |
| **Special types** | void (not a type) | Unit (object), Nothing (never returns) |
| **Methods on numbers** | Only on wrapper classes | All number types have methods |
| **Compilation** | Primitives stay primitives | Kotlin types compile to primitives when possible |

**Kotlin advantages:**
- Unified type system (everything is object)
- Explicit null safety
- No autoboxing confusion
- Methods available on all types

## Ответ

В Java и Kotlin типы данных делятся на примитивные и ссылочные. В Java: int, double и тд как примитивы и String, классы объекты массивы интерфейсы как ссылочные типы. В Kotlin: Int Double и тд как обёртки примитивов JVM, String коллекции классы с nullable и nonnullable типами. Kotlin добавляет Unit эквивалент void но объект, и Nothing для функций которые всегда бросают исключение. Также в Kotlin все данные являются объектами

