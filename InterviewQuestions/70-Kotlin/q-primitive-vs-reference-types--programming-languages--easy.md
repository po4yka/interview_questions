---
id: lang-004
title: "Primitive Vs Reference Types / Примитивные типы против ссылочных типов"
aliases: [Primitive Vs Reference Types, Примитивные типы против ссылочных типов]
topic: programming-languages
subtopics: [jvm, memory-model, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-adapter-pattern--design-patterns--medium, q-os-fundamentals-concepts--computer-science--hard, q-what-is-job-object--programming-languages--medium]
created: 2025-10-13
updated: 2025-10-31
tags: [difficulty/easy, java, kotlin, memory, primitive-types, programming-languages, reference-types]
date created: Friday, October 3rd 2025, 7:03:57 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---

# В Чем Разница Примитивного И Ссылочного Типов

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

### Примитивные Типы

**Хранят значения напрямую**, не могут быть null, и не имеют методов (в Java):

**Java примитивы:**
```java
// Примитивные типы (8 в Java)
int x = 10;           // Хранит значение 10 напрямую
double y = 3.14;      // Хранит значение 3.14 напрямую
boolean flag = true;  // Хранит true/false напрямую
char c = 'A';         // Хранит символ напрямую

// Не могут быть null
int value = null;  // Ошибка компиляции!

// Нет методов
// x.toString();   // Ошибка! У примитивов нет методов
```

**Характеристики:**
- Хранятся в **стеке** (или inline в объектах)
- Фиксированный размер: `int` = 4 байта, `double` = 8 байт
- Быстрый доступ
- Значения по умолчанию: `0`, `false`, `\0`
- Не могут быть null
- Нет методов

### Ссылочные Типы

**Хранят ссылки (указатели)** на объекты в памяти, могут быть null:

**Java ссылочные типы:**
```java
// Ссылочные типы
String text = "Hello";        // Хранит ссылку на объект String
Integer num = 10;             // Wrapper класс (ссылочный тип)
int[] array = {1, 2, 3};      // Массив (ссылочный тип)
MyClass obj = new MyClass();  // Пользовательский класс (ссылочный тип)

// Могут быть null
String nullText = null;  // OK
Integer nullNum = null;  // OK

// Имеют методы
text.length();           // OK
text.toUpperCase();      // OK
```

**Характеристики:**
- Хранятся в **heap** (ссылка в стеке)
- Переменный размер
- Медленнее доступ (косвенность)
- Значение по умолчанию: `null`
- Могут быть null
- Имеют методы

### Представление В Памяти

**Примитивный тип:**
```
Стек:

 x: 10   (значение хранится напрямую)
```

**Ссылочный тип:**
```
Стек:              Heap:

 ref: →  "Hello"       (реальный объект)
```

### Контекст Kotlin

**Kotlin не раскрывает примитивные типы** программисту, но использует их под капотом:

```kotlin
// Все выглядят как объекты в Kotlin
val x: Int = 10           // Компилируется в int (примитив)
val y: Int? = 10          // Компилируется в Integer (ссылочный)

val text: String = "Hi"   // String (ссылочный тип)

// Все имеют методы в Kotlin
val hex = x.toString(16)  // "a"
val abs = (-5).absoluteValue  // 5

// Nullable типы всегда ссылочные типы
val nullable: Int? = null  // Integer (ссылочный)
val notNull: Int = 10      // int (примитив в байткоде)
```

### Таблица Сравнения

| Аспект | Примитивные Типы | Ссылочные Типы |
|--------|----------------|-----------------|
| **Хранение** | Стек (прямое значение) | Heap (через ссылку) |
| **Память** | Фиксированный размер | Переменный размер |
| **По умолчанию** | 0, false, \0 | null |
| **Nullable** | Нет (Java) | Да |
| **Методы** | Нет (Java) | Да |
| **Скорость** | Быстрее | Медленнее (косвенность) |
| **Примеры (Java)** | int, double, boolean | String, Integer, массивы, объекты |
| **Примеры (Kotlin)** | Не раскрыты | Все типы (Int, String, классы) |

### Boxing И Unboxing (Java)

**Конвертация между примитивными и ссылочными:**

```java
// Boxing: примитив → wrapper
int primitive = 10;
Integer wrapped = Integer.valueOf(primitive);  // Ручной boxing
Integer autoBoxed = primitive;                 // Auto-boxing

// Unboxing: wrapper → примитив
Integer wrapped = 10;
int primitive = wrapped.intValue();  // Ручной unboxing
int autoUnboxed = wrapped;           // Auto-unboxing

// Влияние на производительность
Integer sum = 0;
for (int i = 0; i < 1000; i++) {
    sum += i;  // Auto-boxing/unboxing в каждой итерации! Медленно!
}

// Лучше: использовать примитив
int sum = 0;
for (int i = 0; i < 1000; i++) {
    sum += i;  // Без boxing, быстрее
}
```

### Практические Примеры

**1. Коллекции (Java):**
```java
// Нужно использовать wrapper типы в коллекциях
List<Integer> numbers = new ArrayList<>();  // Integer, не int
numbers.add(10);  // Auto-boxing

// Kotlin
val numbers = listOf(1, 2, 3)  // List<Int> (использует Integer внутренне)
```

**2. Обработка null:**
```java
// Java примитив - не может быть null
int age = getAge();  // Что если возраст неизвестен? Нельзя использовать null!

// Решение: использовать wrapper
Integer age = getAge();  // Может вернуть null
if (age != null) {
    // Использовать age
}

// Kotlin - явные nullable типы
val age: Int? = getAge()  // Может быть null
if (age != null) {
    // Использовать age
}
```

**3. Эффективность памяти:**
```java
// Массив примитивов - эффективность памяти
int[] primitives = new int[1000];  // 4000 байт

// Массив ссылок - больше памяти
Integer[] wrapped = new Integer[1000];  // 4000 байт + 1000 объектов overhead

// Kotlin - специализированные массивы
val primitives = IntArray(1000)  // int[] (эффективно)
val wrapped = Array<Int>(1000) { 0 }  // Integer[] (менее эффективно)
```

### Когда Использовать Каждый

**Используйте примитивные типы (или Int, Double и т.д. Kotlin):**
- Производительно-критичный код
- Большие массивы/коллекции
- Когда null не нужен
- Много математических вычислений

**Используйте ссылочные типы (или nullable типы Kotlin):**
- Нужны null значения
- Коллекции/generics
- Когда нужны методы (в Java)
- Сложные объекты

### Резюме

| Особенность | Примитивный | Ссылочный |
|---------|-----------|-----------|
| **Хранение значения** | Прямое | Через ссылку |
| **Может быть null** | Нет (Java) | Да |
| **Имеет методы** | Нет (Java) | Да |
| **Память** | Эффективно | Больше overhead |
| **Скорость** | Быстро | Медленнее |
| **Видимость в Kotlin** | Скрыто (компилируется из Int) | Все типы |

В **Java**: примитивы и ссылочные типы чётко разделены.
В **Kotlin**: всё выглядит как объекты, но примитивы используются внутренне когда возможно.


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
- [[q-optimize-memory-usage-android--android--medium]] - Memory Management
- [[q-stack-heap-memory-multiple-threads--android--medium]] - Memory Management
- [[q-tasks-back-stack--android--medium]] - Memory Management
- [[q-memory-leak-vs-oom-android--android--medium]] - Memory Management
