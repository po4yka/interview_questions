---
id: lang-018
title: "Kotlin Java Data Types / Типы данных Kotlin и Java"
aliases: [Kotlin Java Data Types, Типы данных Kotlin и Java]
topic: kotlin
subtopics: [type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-delegates-compilation--kotlin--hard, q-job-state-machine-transitions--kotlin--medium, q-testing-coroutines-runtest--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [data-types, difficulty/medium, java, primitives, reference-types, type-system]
date created: Friday, October 31st 2025, 6:30:00 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Вопрос (RU)
> Какие типы данных существуют в Java и Kotlin?

# Question (EN)
> What data types exist in Java and Kotlin?

## Ответ (RU)

В Java и Kotlin типы данных делятся на примитивоподобные и ссылочные, но модель и поведение существенно различаются.

### Типы Данных Java

#### Примитивные Типы (8 типов)
Языковые примитивы (значения без методов у самих значений):
```java
byte b = 127;                  // 8-bit
short s = 32767;               // 16-bit
int i = 2147483647;            // 32-bit
long l = 9223372036854775807L; // 64-bit

float f = 3.14f;               // 32-bit floating point
double d = 3.14159;            // 64-bit floating point

char c = 'A';                  // 16-bit UTF-16 code unit
boolean flag = true;           // true/false
```

Для работы как с объектами используются классы-обёртки (`Integer`, `Double` и т.д.), которые дают методы и участвуют в иерархии `Object`.

#### Ссылочные Типы

Объекты, доступ к которым осуществляется через ссылки:
```java
String text = "Hello";                     // String
Integer num = 10;                          // Класс-обёртка
int[] array = {1, 2, 3};                   // Массив примитивов
List<String> list = new ArrayList<>();     // Коллекция
MyClass obj = new MyClass();               // Пользовательский класс
Runnable r = () -> {};                     // Интерфейс / лямбда
```

(В большинстве реализаций размещаются в куче, но это деталь реализации, а не часть спецификации языка.)

### Типы Данных Kotlin

#### Значимые Типы, Отображаемые В Примитивы JVM, Когда Это Возможно

С точки зрения Kotlin все типы — полноправные элементы типовой системы с методами; на JVM они компилируются в примитивы Java или обёртки по необходимости.
```kotlin
val b: Byte = 127
val s: Short = 32767
val i: Int = 2147483647
val l: Long = 9223372036854775807L

val f: Float = 3.14f
val d: Double = 3.14159

val c: Char = 'A'
val flag: Boolean = true
```

Компилятор:
- использует примитивы JVM (`int`, `double` и т.п.), когда это безопасно и эффективно;
- использует классы-обёртки (`java.lang.Integer` и т.д.), когда нужны объектные типы (дженерики, nullable-типы и др.).

#### Ссылочные Типы

```kotlin
val text: String = "Hello"             // String
val list: List<String> = listOf()      // Коллекция
val map: Map<String, Int> = mapOf()    // Map
val obj: MyClass = MyClass()           // Пользовательский класс

// Специальные типы Kotlin
fun doNothing(): Unit { }                // Unit — как void, но реальный тип
fun fail(): Nothing = throw Exception()  // Nothing — функция не возвращает нормально
```

### Ключевые Отличия Java И Kotlin

#### 1. Типовая Система

- Java:
  - Есть 8 примитивных типов, синтаксически и концептуально отличных от ссылочных.
  - Примитивы не входят в иерархию `Object`; методы доступны только у обёрток.
- Kotlin:
  - Использует единообразные типы (`Int`, `Double` и т.п.), которые в байткоде сопоставляются с примитивами/обёртками JVM.
  - Более унифицированная модель: числовые и логические типы выглядят как обычные типы с методами, хотя на уровне JVM это могут быть примитивы.

```java
// Java — примитив не имеет методов
int x = 10;
// x.toString();  // Ошибка
Integer y = 10;
y.toString();      // OK
```

```kotlin
// Kotlin — у `Int` есть методы (на уровне языка)
val kx: Int = 10
kx.toString()      // OK
```

#### 2. Null-безопасность

- Java:
  - Примитивы не могут быть `null`.
  - Любой ссылочный тип (включая обёртки) может быть `null` по умолчанию.
```java
int x = 0;
// int y = null;  // Ошибка компиляции

String s = null;      // OK
Integer i = null;     // OK
MyClass obj = null;   // OK
```

- Kotlin:
  - Не-null типы по умолчанию.
  - Явное разделение на `T` и `T?`.
```kotlin
val x: Int = 10
// x = null        // Ошибка компиляции

val s: String = "Hello"
// s = null        // Ошибка компиляции

val y: Int? = null        // Nullable
val text: String? = null  // Nullable
val obj: MyClass? = null  // Nullable
```

#### 3. Специальные Типы Kotlin

- `Unit` — аналог роли `void` в Java, но это реальный тип с единственным значением `Unit`.
```kotlin
fun doSomething(): Unit {
    println("Done")
}

val list: List<Unit> = listOf(Unit)
```

```java
// Эквивалент по роли в Java
void doSomething() {
    System.out.println("Done");
}
```

- `Nothing` — нижний тип, для функций, которые никогда не завершаются нормально (всегда бросают исключение или зациклены):
```kotlin
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}

fun infiniteLoop(): Nothing {
    while (true) { }
}

// Литерал null сам по себе имеет тип Nothing?
val x = null  // Тип выводится как Nothing?
```

#### 4. Массивы

- Java:
```java
int[] primitives = {1, 2, 3};      // Массив примитивов
Integer[] objects = {1, 2, 3};     // Массив обёрток
String[] strings = {"a", "b"};   // Массив ссылочных типов
```

- Kotlin:
```kotlin
val primitives: IntArray = intArrayOf(1, 2, 3)   // Компилируется в int[]
val objects: Array<Int> = arrayOf(1, 2, 3)       // Компилируется в Integer[]
val strings: Array<String> = arrayOf("a", "b")  // Компилируется в String[]

val bytes: ByteArray = byteArrayOf(1, 2)
val chars: CharArray = charArrayOf('a', 'b')
val doubles: DoubleArray = doubleArrayOf(1.0, 2.0)
```

### Иерархия Типов

- Java (упрощённо):
  - `java.lang.Object` — корень иерархии ссылочных типов.
  - `String`, `Number` (`Integer`, `Double` и т.п.), массивы, пользовательские классы — наследуются от `Object`.
  - Примитивы не входят в эту иерархию.

- Kotlin (упрощённо, для JVM):
  - `Any` — корень всех ненулевых ссылочных типов в системе типов Kotlin.
  - `Any?` — верхний тип для всех nullable-типов (включая `null`).
  - Числовые типы (`Int`, `Double`, и т.п.) являются полноправными типами Kotlin; на JVM они отображаются в примитивы или соответствующие wrapper-типы.
  - `Nothing` — нижний тип: подтип всех типов, не имеет значений.

### Итог

Краткое сравнение:

- Примитивы:
  - Java: 8 примитивов, отдельны от `Object`.
  - Kotlin: использует типы вроде `Int` (компилируются в примитивы/обёртки), нет отдельного синтаксиса примитивов.
- Ссылочные типы:
  - Java: `String`, классы, массивы, интерфейсы, обёртки.
  - Kotlin: `String`, классы, коллекции, массивы, и т.п.
- Null-безопасность:
  - Java: ссылочные типы могут быть `null` без явной аннотации.
  - Kotlin: явное `T` vs `T?`.
- Иерархия типов:
  - Java: примитивы вне иерархии `Object`.
  - Kotlin: `Any` / `Any?` задают верхние типы для (не)nullable значений; числовые и другие базовые типы — часть единой системы типов и сопоставляются на JVM с примитивами/обёртками.
- Специальные типы:
  - Java: `void` (не полноценный тип).
  - Kotlin: `Unit` (реальный тип), `Nothing` (нижний тип).
- Методы на числах:
  - Java: только у обёрток.
  - Kotlin: напрямую у `Int`, `Double` и других.

**Преимущества Kotlin в этом контексте:**
- Более единообразная типовая система.
- Встроенная null-безопасность через `T` / `T?`.
- Меньше скрытых проблем, связанных с (auto)boxing.
- Методы и операторы доступны прямо на базовых типах.

## Answer (EN)

In both Java and Kotlin, data types are divided into primitive-like and reference types, but with important differences.

### Java Data Types

#### Primitive Types (8 types)
Language-level primitive values (no methods on the values themselves):
```java
byte b = 127;                  // 8-bit
short s = 32767;               // 16-bit
int i = 2147483647;            // 32-bit
long l = 9223372036854775807L; // 64-bit

float f = 3.14f;               // 32-bit floating point
double d = 3.14159;            // 64-bit floating point

char c = 'A';                  // 16-bit UTF-16 code unit
boolean flag = true;           // true/false
```

(Boxing via wrapper classes like `Integer`, `Double`, etc., provides objects with methods.)

#### Reference Types

Objects accessed via references:
```java
String text = "Hello";                     // String
Integer num = 10;                          // Wrapper class
int[] array = {1, 2, 3};                   // Primitive array
List<String> list = new ArrayList<>();     // Collection
MyClass obj = new MyClass();               // Custom class
Runnable r = () -> {};                     // Interface / lambda
```

(In most implementations they are heap-allocated, but that is an implementation detail, not a language guarantee.)

### Kotlin Data Types

#### Value Types Mapped to JVM Primitives when Possible

From the Kotlin language perspective all types are first-class, have members, and participate in the type system; on the JVM they are compiled to Java primitives or wrappers as needed.
```kotlin
val b: Byte = 127
val s: Short = 32767
val i: Int = 2147483647
val l: Long = 9223372036854775807L

val f: Float = 3.14f
val d: Double = 3.14159

val c: Char = 'A'
val flag: Boolean = true
```

The compiler:
- uses JVM primitive types (`int`, `double`, etc.) where safe and efficient,
- uses wrapper types (e.g. `java.lang.Integer`) when required (generics, nullable types, etc.).

#### Reference Types
```kotlin
val text: String = "Hello"             // String
val list: List<String> = listOf()      // Collection
val map: Map<String, Int> = mapOf()    // Map
val obj: MyClass = MyClass()           // Custom class

// Kotlin adds special types:
fun doNothing(): Unit { }                // Unit - like void but is a real type
fun fail(): Nothing = throw Exception()  // Nothing - function never returns normally
```

### Key Differences

#### 1. Type System

| Aspect | Java | Kotlin |
|--------|------|--------|
| Primitive types | Yes (8 types) | No separate primitive syntax; uses types like `Int` mapped to JVM primitives where possible |
| Unified system | No (primitives vs references) | More unified: numeric/boolean/char types are regular Kotlin types in the language's type system |
| Methods on numbers | Only on wrapper classes | Yes, on `Int`, `Double`, etc. |

```java
// Java - primitives have no methods
int x = 10;
// x.toString();  // Error
Integer y = 10;
y.toString();      // OK
```

```kotlin
// Kotlin - types like `Int` have members at language level
val kx: Int = 10
kx.toString();     // OK
```

#### 2. Nullability

**Java - reference types can be null (by default):**
```java
// Primitives cannot be null
int x = 0;
// int y = null;  // Compilation error

// Reference types can be null
String s = null;      // OK
Integer i = null;     // OK
MyClass obj = null;   // OK
```

**Kotlin - explicit nullable vs non-nullable types:**
```kotlin
// Non-nullable by default
val x: Int = 10
// x = null        // Compilation error

val s: String = "Hello"
// s = null        // Compilation error

// Nullable types with ?
val y: Int? = null        // OK
val text: String? = null  // OK
val obj: MyClass? = null  // OK
```

#### 3. Special Kotlin Types

**Unit** - equivalent in role to Java's `void`, but is a proper type with a single value:
```kotlin
fun doSomething(): Unit {
    println("Done")
}  // Returns Unit singleton

val list: List<Unit> = listOf(Unit)  // Can be used as a type argument
```

```java
// Java equivalent by role
void doSomething() {
    System.out.println("Done");
}
```

**Nothing** - bottom type, for functions that never return normally:
```kotlin
fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}

fun infiniteLoop(): Nothing {
    while (true) { }
}

// A standalone null literal has type Nothing? for type inference
val x = null  // Type is Nothing?
```

#### 4. Arrays

**Java - primitive arrays vs object arrays:**
```java
int[] primitives = {1, 2, 3};      // Primitive array
Integer[] objects = {1, 2, 3};     // Wrapper array
String[] strings = {"a", "b"};   // Reference array
```

**Kotlin - specialized array types:**
```kotlin
val primitives: IntArray = intArrayOf(1, 2, 3)   // Compiles to int[]
val objects: Array<Int> = arrayOf(1, 2, 3)       // Compiles to Integer[]
val strings: Array<String> = arrayOf("a", "b")  // Compiles to String[]

val bytes: ByteArray = byteArrayOf(1, 2)
val chars: CharArray = charArrayOf('a', 'b')
val doubles: DoubleArray = doubleArrayOf(1.0, 2.0)
```

### Type Hierarchy

**Java (simplified):**
```java
java.lang.Object
   ├─ String
   ├─ Number
   │    ├─ Integer, Double, etc. (wrappers)
   ├─ Arrays (as objects)
   ├─ Custom classes

// Primitives are not part of this class hierarchy.
```

**Kotlin (simplified JVM view):**
```kotlin
Any            // root of all non-null reference types in Kotlin's type system
  ├─ Number
  ├─ Other Kotlin types (String, collections, custom classes, etc.)

Any?           // top type for all nullable types (includes Any and null)

Nothing        // bottom type: subtype of all types, no values
```

Numeric types (`Int`, `Double`, etc.) are proper Kotlin types that conceptually fit into this hierarchy at the language level, while on the JVM they are represented as primitives or wrapper classes depending on context.

### Summary

| Feature | Java | Kotlin |
|---------|------|--------|
| Primitives | 8 primitive types, separate from `Object` | Types like `Int`, `Double` compile to primitives when possible; no separate primitive syntax |
| Reference types | `String`, classes, arrays, interfaces, wrappers | `String`, classes, collections, arrays, etc. |
| Nullability | All reference types nullable by default | Explicit `T` vs `T?` |
| Type hierarchy | Primitives outside `Object` hierarchy | `Any` / `Any?` as top types; basic types participate in single type system and map to primitives/wrappers on JVM |
| Special types | `void` (not a real type) | `Unit` (real return type), `Nothing` (bottom type) |
| Methods on numbers | Only on wrapper classes | Available on `Int`, `Double`, etc. |
| Compilation | Primitives remain primitives | Maps to primitives/boxed types as needed |

**Kotlin advantages (in this context):**
- More uniform type system (numeric and other types are regular Kotlin types).
- Built-in null safety via `T` / `T?`.
- Fewer surprises from boxing/unboxing.
- Methods available directly on numeric and other basic types.

## Дополнительные Вопросы (RU)

- Как единая типовая система Kotlin влияет на дизайн API по сравнению с разделением примитивов и ссылочных типов в Java?
- Как null-безопасность Kotlin (`T` vs `T?`) помогает снизить вероятность `NullPointerException` по сравнению с Java?
- Какие подводные камни возникают при интероперабельности Kotlin и Java (примитивы, массивы, nullable-типы)?

## Follow-ups

- How does Kotlin's unified type system differ from Java's primitive/reference split in real-world code?
- How does Kotlin's null-safety (`T` vs `T?`) help prevent `NullPointerException`s compared to Java?
- What are common pitfalls when interoperating Kotlin with Java types (primitives, arrays, nullable types)?

## Ссылки (RU)

- [[c-kotlin]]
- https://kotlinlang.org/docs/home.html

## References

- [[c-kotlin]]
- https://kotlinlang.org/docs/home.html

## Связанные Вопросы (RU)

- [[q-job-state-machine-transitions--kotlin--medium]]
- [[q-delegates-compilation--kotlin--hard]]
- [[q-testing-coroutines-runtest--kotlin--medium]]

## Related Questions

- [[q-job-state-machine-transitions--kotlin--medium]]
- [[q-delegates-compilation--kotlin--hard]]
- [[q-testing-coroutines-runtest--kotlin--medium]]
