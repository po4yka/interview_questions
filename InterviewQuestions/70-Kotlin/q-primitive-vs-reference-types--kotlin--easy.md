---
'---id': lang-004
title: Primitive Vs Reference Types / Примитивные типы против ссылочных типов
aliases:
- Primitive Vs Reference Types
- Примитивные типы против ссылочных типов
topic: kotlin
subtopics:
- memory
- primitive-types
- reference-types
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-aggregation
- c-algorithms
- c-app-signing
- c-backend
- c-binary-search
- c-binary-search-tree
- c-binder
- c-biometric-authentication
- c-bm25-ranking
- c-by-type
- c-cap-theorem
- c-ci-cd
- c-ci-cd-pipelines
- c-clean-code
- c-compiler-optimization
- c-compose-modifiers
- c-compose-phases
- c-compose-semantics
- c-computer-science
- c-concurrency
- c-cross-platform-development
- c-cross-platform-mobile
- c-cs
- c-data-classes
- c-data-loading
- c-debugging
- c-declarative-programming
- c-deep-linking
- c-density-independent-pixels
- c-dimension-units
- c-dp-sp-units
- c-dsl-builders
- c-dynamic-programming
- c-espresso-testing
- c-event-handling
- c-folder
- c-functional-programming
- c-gdpr-compliance
- c-gesture-detection
- c-gradle-build-cache
- c-gradle-build-system
- c-https-tls
- c-image-formats
- c-inheritance
- c-jit-aot-compilation
- c-kmm
- c-kotlin
- c-lambda-expressions
- c-lazy-grid
- c-lazy-initialization
- c-level
- c-load-balancing
- c-manifest
- c-memory-optimization
- c-memory-profiler
- c-microservices
- c-multipart-form-data
- c-multithreading
- c-mutablestate
- c-networking
- c-offline-first-architecture
- c-oop
- c-oop-concepts
- c-oop-fundamentals
- c-oop-principles
- c-play-console
- c-play-feature-delivery
- c-programming-languages
- c-properties
- c-real-time-communication
- c-references
- c-scaling-strategies
- c-scoped-storage
- c-security
- c-serialization
- c-server-sent-events
- c-shader-programming
- c-snapshot-system
- c-specific
- c-strictmode
- c-system-ui
- c-test-doubles
- c-test-sharding
- c-testing-pyramid
- c-testing-strategies
- c-theming
- c-to-folder
- c-token-management
- c-touch-input
- c-turbine-testing
- c-two-pointers
- c-ui-testing
- c-ui-ux-accessibility
- c-value-classes
- c-variable
- c-weak-references
- c-windowinsets
- c-xml
created: 2025-10-13
updated: 2025-11-11
tags:
- difficulty/easy
- java
- kotlin
- memory
- primitive-types
- programming-languages
- reference-types
anki_cards:
- slug: q-primitive-vs-reference-types--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-primitive-vs-reference-types--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Вопрос (RU)
> В чем разница примитивного и ссылочного типов?

---

# Question (EN)
> What is the difference between primitive and reference types?

## Ответ (RU)

[[c-kotlin]]

### Примитивные Типы

**Хранят значения напрямую** (в Java-примитивах), не могут быть null, и не имеют собственных методов (у самих примитивов в Java):

**Java примитивы:**
```java
// Примитивные типы (8 в Java)
int x = 10;           // Хранит значение 10 напрямую
double y = 3.14;      // Хранит значение 3.14 напрямую
boolean flag = true;  // Хранит true/false напрямую
char c = 'A';         // Хранит символ напрямую

// Не могут быть null
int value = null;  // Ошибка компиляции!

// Нет методов у самого типа
// x.toString();   // Ошибка! У примитивов нет методов как у объектов
```

**Характеристики (Java, концептуально, упрощённо):**
- Переменная примитивного типа хранит само значение, а не ссылку на объект
- Размещение (стек/heap/inline в объекте) определяется JVM и оптимизациями; важна именно модель "значение, а не ссылка"
- Фиксированный размер: `int` = 4 байта, `double` = 8 байт
- Быстрый доступ
- Значения по умолчанию для полей/элементов массивов: `0`, `false`, `\0`
- Не могут быть null
- Не имеют собственных методов (операции реализованы на уровне языка/байткода)

### Ссылочные Типы

**Хранят ссылки (указатели)** на объекты в памяти, могут быть null:

**Java ссылочные типы:**
```java
// Ссылочные типы
String text = "Hello";        // Хранит ссылку на объект String
Integer num = 10;              // Wrapper класс (ссылочный тип)
int[] array = {1, 2, 3};       // Массив (ссылочный тип)
MyClass obj = new MyClass();   // Пользовательский класс (ссылочный тип)

// Могут быть null
String nullText = null;  // OK
Integer nullNum = null;  // OK

// Имеют методы
text.length();           // OK
text.toUpperCase();      // OK
```

**Характеристики (Java, концептуально):**
- Объекты размещаются в heap; переменные содержат ссылку (сама ссылка обычно хранится в стеке или в поле объекта, но точное размещение зависит от JVM)
- Переменный размер объектов
- Доступ к данным через косвенность (по ссылке)
- Значение по умолчанию для полей/элементов массивов ссылочного типа: `null`
- Могут быть null
- Имеют методы/поведение

### Представление В Памяти

(Упрощённая схема, для интуитивного понимания модели, не буквальное расположение байтов)

**Примитивный тип:**
```text
Стек:

 x: 10   (значение хранится напрямую)
```

**Ссылочный тип:**
```text
Стек:              Heap:

 ref: e  "Hello"       (реальный объект)
```

### Контекст Kotlin

**Kotlin не вводит отдельный синтаксис для примитивов** (как `int`/`Integer`), но на JVM использует примитивные типы под капотом, когда это возможно:

```kotlin
// Выглядят как объекты в Kotlin, но отображаются в байткоде эффективно
val x: Int = 10           // Обычно компилируется в int (примитив), если не используется в контексте, требующем ссылку
val y: Int? = 10          // Компилируется в Integer (ссылочный)

val text: String = "Hi"   // `String` (ссылочный тип)

// Можно вызывать функции/свойства
val hex = x.toString(16)       // "a" (будет скомпилировано эффективно)
val abs = (-5).absoluteValue   // 5

// Nullable-типы для чисел всегда представляются ссылочными типами (wrapper)
val nullable: Int? = null  // Integer (ссылочный)
val notNull: Int = 10      // int (примитив в байткоде при стандартных условиях, если не попадает в generic/Any и т.п.)
```

### Таблица Сравнения

| Аспект | Примитивные Типы (Java) | Ссылочные Типы (Java) |
|--------|------------------------|------------------------|
| **Хранение** | Значение в переменной (модель "значение напрямую") | В переменной хранится ссылка на объект в heap |
| **Память** | Фиксированный размер | Переменный размер объектов |
| **По умолчанию** | 0, false, \0 (для полей/массивов) | null |
| **Nullable** | Нет | Да |
| **Методы** | Нет (у самих примитивов) | Да |
| **Скорость** | Обычно быстрее | Обычно медленнее (косвенность, GC) |
| **Примеры (Java)** | `int`, `double`, `boolean` | `String`, `Integer`, массивы, объекты |
| **Примеры (Kotlin/JVM)** | `Int`, `Long` и др. компилируются в примитивы, если non-null и не используются в generic/Any и т.п. | Nullable числовые типы и объекты (`String`, классы) как ссылочные |

### Boxing И Unboxing (Java)

**Конвертация между примитивными и ссылочными:**

```java
// Boxing: примитив e wrapper
int primitive = 10;
Integer wrapped = Integer.valueOf(primitive);  // Ручной boxing
Integer autoBoxed = primitive;                 // Auto-boxing

// Unboxing: wrapper e примитив
Integer wrapped2 = 10;
int primitive2 = wrapped2.intValue();  // Ручной unboxing
int autoUnboxed = wrapped2;            // Auto-unboxing

// Влияние на производительность
Integer sum = 0;
for (int i = 0; i < 1000; i++) {
    sum += i;  // В каждой итерации создаются новые Integer из-за неизменяемости; boxing/unboxing даёт накладные расходы
}

// Лучше: использовать примитив
int sum2 = 0;
for (int i = 0; i < 1000; i++) {
    sum2 += i;  // Без boxing, эффективнее
}
```

### Практические Примеры

**1. Коллекции (Java):**
```java
// Нужно использовать wrapper типы в коллекциях
List<Integer> numbers = new ArrayList<>();  // Integer, не int
numbers.add(10);  // Auto-boxing

// Kotlin (на JVM)
val numbers = listOf(1, 2, 3)  // List<Int> (использует Integer под капотом на JVM)
```

**2. Обработка null:**
```java
// Java примитив - не может быть null
int age = getAge();  // Если возраст может отсутствовать, null использовать нельзя

// Решение: использовать wrapper
Integer ageBoxed = getAge();  // Может вернуть null
if (ageBoxed != null) {
    // Использовать ageBoxed
}

// Kotlin - явные nullable типы
val ageK: Int? = getAge()  // Может быть null
if (ageK != null) {
    // Использовать ageK
}
```

**3. Эффективность памяти:**
```java
// Массив примитивов - эффективность памяти
int[] primitives = new int[1000];  // ~4000 байт

// Массив ссылок + объектов - больше памяти
Integer[] wrapped = new Integer[1000];  // ~1000 ссылок + до 1000 Integer-объектов (существенный overhead)

// Kotlin - специализированные массивы
val primitivesK = IntArray(1000)              // компилируется в int[] (эффективно)
val wrappedK = Array<Int>(1000) { 0 }        // Integer[] (менее эффективно)
```

### Когда Использовать Каждый

**Используйте примитивные типы (или Kotlin `Int`, `Double` и т.д. в non-null контексте):**
- Производительно-критичный код
- Большие массивы/коллекции
- Когда null не нужен
- Много математических вычислений

**Используйте ссылочные типы (или nullable типы Kotlin / wrapper-типы Java):**
- Нужны null значения
- Коллекции/generics (в Java коллекции работают только с ссылочными типами)
- Для сложных объектов и доменных моделей

### Резюме

| Особенность | Примитивный | Ссылочный |
|---------|-----------|-----------|
| **Хранение значения** | Прямое значение в переменной | Через ссылку на объект |
| **Может быть null** | Нет (Java) | Да |
| **Имеет методы** | Нет (Java-примитивы) | Да |
| **Память** | Эффективно | Больше overhead |
| **Скорость** | Обычно быстрее | Обычно медленнее |
| **Видимость в Kotlin (JVM)** | `Int`/`Long` и др. как value-тип, отображаемый в примитивы, когда это возможно | Nullable/объектные типы и объекты (`String` и др.) как ссылочные |

В **Java**: примитивы и ссылочные типы чётко разделены.
В **Kotlin** (на JVM): синтаксически всё выглядит как обычные типы, но под капотом используются примитивы, когда это возможно для эффективности.

---

## Answer (EN)

[[c-kotlin]]

### Primitive Types

**Store values directly** (for Java primitives), cannot be null, and have no instance methods on the primitive type itself (in Java):

**Java primitives:**
```java
// Primitive types (8 in Java)
int x = 10;           // Stores value 10 directly
double y = 3.14;      // Stores value 3.14 directly
boolean flag = true;  // Stores true/false directly
char c = 'A';         // Stores character directly

// Cannot be null
int value = null;  // Compilation error!

// No methods on the primitive itself
// x.toString();   // Error! Primitives do not have methods like objects
```

**Characteristics (Java, conceptual/simplified model):**
- A primitive-typed variable holds the value itself, not a reference to an object
- Actual placement (stack/heap/inline in an object) is JVM/implementation dependent; conceptually it's "value, not reference"
- Fixed size: `int` = 4 bytes, `double` = 8 bytes
- Fast access
- Default values for fields/array elements: `0`, `false`, `\0`
- Cannot be null
- No instance methods (operations are implemented by the language/bytecode)

### Reference Types

**Store references (pointers)** to objects in memory, can be null:

**Java reference types:**
```java
// Reference types
String text = "Hello";        // Stores reference to String object
Integer num = 10;              // Wrapper class (reference type)
int[] array = {1, 2, 3};       // Array (reference type)
MyClass obj = new MyClass();   // Custom class (reference type)

// Can be null
String nullText = null;  // OK
Integer nullNum = null;  // OK

// Have methods
text.length();           // OK
text.toUpperCase();      // OK
```

**Characteristics (Java, conceptual model):**
- Objects are allocated on the heap; variables hold a reference (the reference itself typically lives on the stack or in an object field, but exact details are JVM-specific)
- Variable-size objects
- Access via indirection through the reference
- Default value for fields/array elements of reference type: `null`
- Can be null
- Have methods/behavior

### Memory Representation

(Simplified diagrams to illustrate the model; not a literal layout guarantee)

**Primitive type:**
```text
Stack:

 x: 10   (value stored directly)
```

**Reference type:**
```text
Stack:              Heap:
        
 ref: e  "Hello"       (actual object)
        
```

### Kotlin Context

**Kotlin does not have separate syntax for primitives vs wrappers** (like `int` vs `Integer`), but on the JVM it uses primitive types under the hood when possible:

```kotlin
// All look like regular types in Kotlin, but compiled efficiently
val x: Int = 10           // Typically compiles to int (primitive) when not used in a context requiring a reference
val y: Int? = 10          // Compiles to Integer (reference)

val text: String = "Hi"   // `String` (reference type)

// Can call functions/properties
val hex = x.toString(16)       // "a" (compiled efficiently)
val abs = (-5).absoluteValue   // 5

// Nullable numeric types are always represented as reference types (wrappers)
val nullable: Int? = null  // Integer (reference)
val notNull: Int = 10      // int (primitive in bytecode under typical conditions, if not forced into a reference context such as generics/Any)
```

### Comparison Table

| Aspect | Primitive Types (Java) | Reference Types (Java) |
|--------|------------------------|------------------------|
| **Storage** | Value in the variable ("direct value" model) | Variable holds reference to object on heap |
| **Memory** | Fixed size | Variable-size objects |
| **Default** | 0, false, \0 (for fields/arrays) | null |
| **Nullable** | No | Yes |
| **Methods** | No (on primitive itself) | Yes |
| **Speed** | Usually faster | Usually slower (indirection, GC) |
| **Examples (Java)** | `int`, `double`, `boolean` | `String`, `Integer`, arrays, objects |
| **Examples (Kotlin/JVM)** | `Int`, `Long`, etc. compiled to primitives when non-null and not used in generic/Any contexts | Nullable numeric types and objects (`String`, classes) as references |

### Boxing and Unboxing (Java)

**Converting between primitive and reference:**

```java
// Boxing: primitive e wrapper
int primitive = 10;
Integer wrapped = Integer.valueOf(primitive);  // Manual boxing
Integer autoBoxed = primitive;                 // Auto-boxing

// Unboxing: wrapper e primitive
Integer wrapped2 = 10;
int primitive2 = wrapped2.intValue();  // Manual unboxing
int autoUnboxed = wrapped2;            // Auto-unboxing

// Performance impact
Integer sum = 0;
for (int i = 0; i < 1000; i++) {
    sum += i;  // Causes boxing/unboxing and creation of new Integer instances (wrappers are immutable)
}

// Better: use primitive
int sum2 = 0;
for (int i = 0; i < 1000; i++) {
    sum2 += i;  // No boxing, faster
}
```

### Practical Examples

**1. Collections (Java):**
```java
// Must use wrapper types in collections
List<Integer> numbers = new ArrayList<>();  // Integer, not int
numbers.add(10);  // Auto-boxing

// Kotlin (on JVM)
val numbers = listOf(1, 2, 3)  // List<Int> (uses Integer under the hood on JVM)
```

**2. Null handling:**
```java
// Java primitive - cannot be null
int age = getAge();  // If age may be unknown, null cannot be used here

// Solution: use wrapper
Integer ageBoxed = getAge();  // Can return null
if (ageBoxed != null) {
    // Use ageBoxed
}

// Kotlin - explicit nullable types
val ageK: Int? = getAge()  // Can be null
if (ageK != null) {
    // Use ageK
}
```

**3. Memory efficiency:**
```java
// Array of primitives - memory efficient
int[] primitives = new int[1000];  // ~4000 bytes

// Array of references + objects - more memory
Integer[] wrapped = new Integer[1000];  // ~1000 references + up to 1000 Integer objects (significant overhead)

// Kotlin - specialized arrays
val primitivesK = IntArray(1000)              // compiles to int[] (efficient)
val wrappedK = Array<Int>(1000) { 0 }        // Integer[] (less efficient)
```

### When to Use Each

**Use primitive types (or Kotlin's non-null `Int`, `Double`, etc.):**
- Performance-critical code
- Large arrays/collections
- When null is not needed
- Math-heavy computations

**Use reference types (or Kotlin's nullable types / Java wrapper types):**
- Need null values
- Collections/generics (Java collections work with reference types)
- Complex/domain objects

### Summary

| Feature | Primitive | Reference |
|---------|-----------|-----------|
| **Value storage** | Direct value in variable | Via reference to object |
| **Can be null** | No (Java) | Yes |
| **Has methods** | No (Java primitives) | Yes |
| **Memory** | Efficient | More overhead |
| **Speed** | Usually fast | Usually slower |
| **Kotlin visibility (JVM)** | `Int`/`Long` etc. as value types compiled to primitives when possible | Nullable/object types (`String` etc.) as references |

In **Java**: primitives and reference types are clearly separated.
In **Kotlin** (on JVM): everything looks like regular types, but primitives are used internally when possible for efficiency.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

### Android Implementation
- [[q-sharedpreferences-definition--android--easy]] - Memory Management
- [[q-leakcanary-library--android--easy]] - Memory Management
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - Memory Management
- [[q-stack-heap-memory-multiple-threads--android--medium]] - Memory Management
- [[q-tasks-back-stack--android--medium]] - Memory Management
- [[q-memory-leak-vs-oom-android--android--medium]] - Memory Management
