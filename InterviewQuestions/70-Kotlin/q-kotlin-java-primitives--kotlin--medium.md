---
id: lang-094
title: Kotlin Java Primitives / Примитивы Kotlin и Java
aliases:
- Kotlin Java Primitives
- Примитивы Kotlin и Java
topic: kotlin
subtopics:
- type-system
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-flowon-operator-context-switching--kotlin--hard
created: 2025-10-15
updated: 2025-11-10
tags:
- difficulty/medium
- java
- primitives
- types
- wrappers
anki_cards:
- slug: lang-094-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
  - type-system
- slug: lang-094-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
  - type-system
---
# Вопрос (RU)
> Какие примитивы есть в Kotlin, а какие в Java?

# Question (EN)
> What primitives exist in Kotlin and Java?

## Ответ (RU)

Kotlin и Java используют разные подходы к примитивным типам данных. Java имеет явные примитивы и отдельные классы-обертки, а Kotlin предоставляет унифицированную (с точки зрения синтаксиса) систему типов поверх JVM, где компилятор по возможности использует примитивы.

### Java Примитивы

Java содержит **8 примитивных типов** и соответствующие классы-обертки:

| Тип | Размер (логический) | Диапазон | Класс-обертка |
|------|---------------------|----------|---------------|
| `byte` | 8 бит | -128 до 127 | `Byte` |
| `short` | 16 бит | -32,768 до 32,767 | `Short` |
| `int` | 32 бит | -2³¹ до 2³¹-1 | `Integer` |
| `long` | 64 бит | -2⁶³ до 2⁶³-1 | `Long` |
| `float` | 32 бит | IEEE 754 | `Float` |
| `double` | 64 бит | IEEE 754 | `Double` |
| `char` | 16 бит | UTF-16 кодовое значение | `Character` |
| `boolean` | не определен в битах спецификацией | `true` / `false` | `Boolean` |

**Код на Java:**
```java
// Примитивы - значимые типы без методов
int x = 10;
double y = 3.14;
boolean flag = true;

// Классы-обертки - ссылочные типы, имеют методы
Integer boxed = 10;   // Autoboxing (автоупаковка)
int unboxed = boxed;  // Unboxing (распаковка)

// Примитивы не могут быть null
// int value = null;  // Ошибка компиляции
Integer nullable = null;  // OK - класс-обертка

// Проблема autoboxing
Integer a = 1000;
Integer b = 1000;
System.out.println(a == b);      // false (сравнение ссылок)
System.out.println(a.equals(b)); // true (сравнение значений)

// Кэширование Integer (-128 до 127)
Integer c = 100;
Integer d = 100;
System.out.println(c == d);  // true (кэшированные объекты)
```

### Kotlin "примитивы"

Kotlin **не объявляет отдельный синтаксис для примитивных типов**: разработчик работает с типами `Int`, `Double`, `Boolean` и т.п. как с классами. Однако компилятор Kotlin на JVM:
- использует **JVM-примитивы** для non-nullable значений, когда это возможно;
- использует **классы-обертки** (`java.lang.Integer` и др.) для nullable типов, обобщений, `Array<T>` и других случаев.

| Тип Kotlin | JVM примитив (когда возможно) | JVM обертка (когда нужно) |
|-------------|-------------------------------|---------------------------|
| `Byte` | `byte` | `java.lang.Byte` |
| `Short` | `short` | `java.lang.Short` |
| `Int` | `int` | `java.lang.Integer` |
| `Long` | `long` | `java.lang.Long` |
| `Float` | `float` | `java.lang.Float` |
| `Double` | `double` | `java.lang.Double` |
| `Char` | `char` | `java.lang.Character` |
| `Boolean` | `boolean` | `java.lang.Boolean` |

**Код на Kotlin:**
```kotlin
// Выглядят как объекты, но компилируются в примитивы, когда возможно
val x: Int = 10          // Компилируется в байткод с использованием int
val y: Double = 3.14     // Используется double
val flag: Boolean = true // Используется boolean

// Можно вызывать функции и свойства (часть стандартной библиотеки)
val hex = 255.toString(16)       // "ff"
val abs = (-10).absoluteValue    // 10

// Nullable типы обычно компилируются в классы-обертки
val nullable: Int? = null        // Используется java.lang.Integer
val notNull: Int = 10            // Используется примитив int, когда возможно

// Сравнение
val a: Int = 1000
val b: Int = 1000
println(a == b)   // true (сравнение значений)
println(a === b)  // сравнение ссылок, результат зависит от представления (примитив/обертка)
```

### Ключевые Различия

#### 1. Унифицированная Система Типов

С точки зрения языка Kotlin все эти числовые и логические типы ведут себя как обычные классы и могут использоваться в обобщениях, иметь функции-расширения и т.д. При этом на уровне JVM компилятор старается использовать примитивы для эффективности.

**Kotlin:**
```kotlin
fun <T> identity(value: T): T = value

val x = identity(42)          // Работает, T выводится как Int (будет boxed в контексте обобщения)
val s = identity("hello")   // Работает
val list = identity(listOf(1, 2, 3))
```

**Java:**
```java
public static <T> T identity(T value) {
    return value;
}

// Работает: int 42 автоупакуется в Integer
Integer i = identity(42);       // autoboxing до Integer
String s = identity("hello");

// Для избежания boxing для примитивов приходится писать перегрузки:
public static int identityInt(int value) { return value; }
public static double identityDouble(double value) { return value; }
```

Ключевое отличие: в Kotlin один и тот же синтаксис типов (`Int`, `Double`) используется независимо от того, будут ли значения представлены как примитивы или обертки на JVM, тогда как в Java существуют отдельные типы для примитивов и оберток.

#### 2. Nullable Типы

**Kotlin:**
```kotlin
// Явное различие nullable vs non-nullable
val notNull: Int = 10           // Не может быть null
// notNull = null  // Ошибка компиляции

val nullable: Int? = null       // Может быть null
val result = nullable?.plus(5)  // Safe call

// Типичное представление:
val primitive: Int = 42         // → примитив int в байткоде, где возможно
val boxed: Int? = 42            // → Integer (обертка JVM)

fun processNumber(n: Int?) {
    if (n != null) {
        println(n * 2)  // Smart cast к Int (non-null)
    }
}
```

**Java:**
```java
// Примитивы не могут быть null
int primitive = 10;
// primitive = null;  // Ошибка компиляции

// Обертки могут быть null
Integer wrapper = null;  // OK
// int result = wrapper + 5;  // Возможен NullPointerException при распаковке

if (wrapper != null) {
    int result = wrapper + 5;
}
// Нет встроенной null-safety в системе типов
```

#### 3. Методы На "примитивах"

**Kotlin:**
```kotlin
val number = 42
println(number.toString())         // "42"
println(number.toDouble())         // 42.0
println(number.coerceIn(0, 100))   // 42

val binary = 10.toString(2)        // "1010"
val max = 5.coerceAtLeast(10)      // 10

// Методы расширения
fun Int.isEven() = this % 2 == 0
println(42.isEven())  // true

// Операторы как функции
val sum = 10.plus(5)       // 15 (то же что 10 + 5)
val product = 3.times(4)   // 12 (то же что 3 * 4)
```

**Java:**
```java
// Примитивы не имеют методов
int number = 42;
// number.toString();  // Ошибка: нужен Integer.toString(number)

// Нужны обертки или статические методы
String str = Integer.toString(number);
double d = Integer.valueOf(number).doubleValue();

// Обертки имеют методы
Integer boxed = 42;
String text = boxed.toString();

// Статические методы утилит
int max = Math.max(5, 10);
int abs = Math.abs(-5);
```

#### 4. Когда Kotlin Использует Примитивы Vs Обертки

**Компилируется преимущественно в JVM-примитивы:**
```kotlin
// Non-nullable локальные переменные и поля
val x: Int = 10

// Non-nullable параметры и возвращаемые типы
fun add(a: Int, b: Int): Int = a + b

// Примитивные массивы
val intArray: IntArray = intArrayOf(1, 2, 3)        // int[]
val doubleArray: DoubleArray = doubleArrayOf(1.0)   // double[]
val boolArray: BooleanArray = booleanArrayOf(true)  // boolean[]
```

**Компилируется в обертки (boxing):**
```kotlin
// Nullable типы
val nullable: Int? = 10              // Integer

// Параметры обобщенных типов
val list: List<Int> = listOf(1, 2)   // List<Integer> в байткоде (type erasure)
val map: Map<String, Int> = mapOf()  // Map<String, Integer]

// Platform types из Java (Int!) могут быть как int, так и Integer

// Массивы объектов
val boxedArray: Array<Int> = arrayOf(1, 2, 3)  // Integer[]
```

**Пример компиляции (упрощенно):**
```kotlin
fun calculate(a: Int, b: Int?): Int? {
    val local: Int = 10
    val nullable: Int? = null
    return if (b != null) a + b else null
}

// Псевдокод байткода/Java-представления:
// public static Integer calculate(int a, Integer b) {
//     int local = 10;           // примитив
//     Integer nullable = null;  // обертка
//     return (b != null) ? a + b : null;
// }
```

### Массивы - Особый Случай

**Kotlin:**
```kotlin
// Примитивные массивы - производительные
val intArray = IntArray(5)           // int[]
val doubleArray = DoubleArray(5)     // double[]
val byteArray = ByteArray(5)         // byte[]

intArray[0] = 42
println(intArray.size)  // 5

// Создание с инициализацией
val numbers = intArrayOf(1, 2, 3, 4, 5)
val doubles = doubleArrayOf(1.0, 2.0, 3.0)

// Массивы объектов
val boxedArray = Array<Int>(5) { 0 }  // Integer[]
val stringArray = arrayOf("a", "b")   // String[]

// Преобразование
val primitiveToBoxed = intArray.toTypedArray()  // IntArray → Array<Int> → Integer[]
val boxedToPrimitive = boxedArray.toIntArray()  // Array<Int> → IntArray → int[]
```

**Java:**
```java
// Примитивные массивы
int[] intArray = new int[5];
double[] doubleArray = new double[5];

intArray[0] = 42;

// Массивы объектов
Integer[] boxedArray = new Integer[5];
String[] stringArray = {"a", "b"};

// Прямое приведение между int[] и Integer[] невозможно
// Integer[] boxed = (Integer[]) intArray;  // Ошибка

// Нужна поэлементная конвертация, например через цикл или стримы
Integer[] boxed = Arrays.stream(intArray)
                        .boxed()
                        .toArray(Integer[]::new);
```

### Производительность

**Kotlin оптимизации:**
```kotlin
class Counter {
    var count: Int = 0  // Обычно компилируется как поле с примитивным int

    fun increment() {
        count++  // Эффективная операция на примитиве
    }
}

// Коллекции стандартной библиотеки используют обертки для чисел
val list = listOf(1, 2, 3)  // List<Int> → List<Integer> на JVM

// Для больших объемов данных используйте примитивные массивы
val bigArray = IntArray(1_000_000) { it }
```

**Сравнение производительности (идея):**
```kotlin
// Быстро - примитивный массив
val primitiveArray = IntArray(1_000_000)
for (i in primitiveArray.indices) {
    primitiveArray[i] = i * 2
}

// Медленнее - Array<Int> (обертки)
val boxedArray = Array(1_000_000) { 0 }
for (i in boxedArray.indices) {
    boxedArray[i] = i * 2  // boxing/unboxing
}

// Еще медленнее - List<Int> (немутируемая коллекция, обертки)
val list = List(1_000_000) { it }
```

### Unsigned Типы (Kotlin 1.3+)

Kotlin добавляет беззнаковые типы (в Java их нет как отдельных примитивов):

```kotlin
val uByte: UByte = 200u           // 0 до 255
val uShort: UShort = 50000u       // 0 до 65_535
val uInt: UInt = 4_000_000_000u   // 0 до 2³²-1
val uLong: ULong = 10_000_000_000uL  // 0 до 2⁶⁴-1

// Unsigned массивы
val uIntArray = UIntArray(5)
val uBytes = ubyteArrayOf(200u, 255u)

// Операции
val sum = 100u + 50u              // UInt
val overflow = UByte.MAX_VALUE + 1u  // Переполнение по модулю диапазона

println(UByte.MAX_VALUE)  // 255
println(UInt.MAX_VALUE)   // 4294967295u
```

### Взаимодействие С Java

**Из Kotlin вызов Java:**
```kotlin
// Java: public int calculate(int a, Integer b)
val result = javaObject.calculate(10, 20)  // Авто-преобразование Int → int/Integer

// Java метод возвращает Integer (nullable)
val nullable: Int? = javaObject.getNullableInt()  // Безопасно
// val notNull: Int = javaObject.getNullableInt()  // Опасно: возможен NPE в рантайме
```

**Из Java вызов Kotlin:**
```java
// Kotlin: fun process(value: Int): Int
int r1 = kotlinObject.process(42);  // OK, используется int

// Kotlin: fun process(value: Int?): Int?
Integer r2 = kotlinObject.process(null);  // OK, как Integer

// Kotlin: val numbers: IntArray
int[] array = kotlinObject.getNumbers();  // int[]

// Kotlin: val boxed: Array<Int>
Integer[] boxedArray = kotlinObject.getBoxed();  // Integer[]
```

### Сравнительная Таблица

| Аспект | Java | Kotlin |
|--------|------|--------|
| **Примитивы** | Да (8 типов) | Нет отдельного синтаксиса, используются классы (`Int` и т.п.) |
| **Обертки** | Отдельные классы | Используются автоматически при необходимости |
| **Методы на примитивах** | Нет (через обертки/утилиты) | Да (функции/расширения для числовых типов) |
| **Nullable** | Только обертки | Явный синтаксис `?` + проверка компилятором |
| **Autoboxing** | Есть, с подводными камнями (`==`, кэширование) | Boxing есть, но скрыт за единой моделью типов; `==` всегда по значению |
| **Производительность** | Большая разница prim vs wrapper | Компилятор старается использовать примитивы; обертки для nullable/обобщений |
| **Обобщения** | Только ссылочные типы (boxing для примитивов) | Унифицированный синтаксис, но под капотом также boxing для обобщений |
| **Unsigned типы** | Нет | Да (`UByte`, `UShort`, `UInt`, `ULong` и массивы) |

### Резюме

**Java:**
- 8 явных примитивных типов.
- Отдельные классы-обертки для каждого примитива.
- Примитивы не имеют методов; используются утилиты и обертки.
- Autoboxing может приводить к неожиданному поведению (`==`, кэширование, NPE).
- Нужно явно различать примитивы и обертки.

**Kotlin:**
- Единый синтаксис типов (`Int`, `Double` и др.), без отдельных ключевых слов для примитивов.
- Компилятор автоматически выбирает примитивы JVM или обертки в зависимости от контекста.
- Методы и функции-расширения доступны для числовых типов.
- Явное различие nullable vs non-nullable и встроенная null-safety.
- Дополнительные unsigned типы.

**Лучшие практики Kotlin:**

```kotlin
// ✅ Используйте non-nullable типы, когда возможно
val count: Int = 0  // Обычно компилируется в примитив

// ✅ Nullable только при необходимости
val optional: Int? = null

// ✅ Примитивные массивы для больших данных
val bigData = IntArray(1_000_000)

// ✅ Коллекции (List/Set/Map) для удобства, понимая, что там обертки
val smallList = listOf(1, 2, 3)

// ❌ Избегайте ненужных nullable
val unnecessary: Int? = 42  // Лучше Int

// ❌ Не используйте Array<Int> для очень больших числовых данных
val inefficient = Array(1_000_000) { 0 }  // Лучше IntArray
```

## Answer (EN)

Kotlin and Java use different approaches to primitive types. Java has explicit primitive types and separate wrapper classes, while Kotlin exposes a unified (syntax-level) type system on top of the JVM where the compiler uses primitives when possible and wrappers when needed.

### Java Primitives

Java has **8 primitive types** and corresponding wrapper classes:

| Type | Logical Size | Range | Wrapper Class |
|------|--------------|-------|---------------|
| `byte` | 8 bits | -128 to 127 | `Byte` |
| `short` | 16 bits | -32,768 to 32,767 | `Short` |
| `int` | 32 bits | -2³¹ to 2³¹-1 | `Integer` |
| `long` | 64 bits | -2⁶³ to 2⁶³-1 | `Long` |
| `float` | 32 bits | IEEE 754 | `Float` |
| `double` | 64 bits | IEEE 754 | `Double` |
| `char` | 16 bits | UTF-16 code unit | `Character` |
| `boolean` | size not defined in bits by the spec | `true` / `false` | `Boolean` |

**Java code:**
```java
// Primitives: value types, no instance methods
int x = 10;
double y = 3.14;
boolean flag = true;

// Wrapper classes: reference types, have methods
Integer boxed = 10;   // Autoboxing
int unboxed = boxed;  // Unboxing

// Primitives cannot be null
// int value = null;  // Compile-time error
Integer nullable = null;  // OK - wrapper class

// Autoboxing pitfall
Integer a = 1000;
Integer b = 1000;
System.out.println(a == b);      // false (reference equality)
System.out.println(a.equals(b)); // true (value equality)

// Integer cache (-128 to 127)
Integer c = 100;
Integer d = 100;
System.out.println(c == d);  // true (cached objects)
```

### Kotlin "Primitives"

Kotlin does not have a separate primitive syntax: you use types like `Int`, `Double`, `Boolean` as regular types. On the JVM, the Kotlin compiler:
- uses JVM primitives for non-nullable values where possible;
- uses wrapper classes (`java.lang.Integer`, etc.) for nullable types, generics, `Array<T>`, and similar cases.

| Kotlin Type | JVM Primitive (when possible) | JVM Wrapper (when needed) |
|-------------|-------------------------------|---------------------------|
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
// Look like objects, compiled to primitives when possible
val x: Int = 10          // Uses primitive int in bytecode
val y: Double = 3.14     // Uses double
val flag: Boolean = true // Uses boolean

// Standard library functions and extensions
val hex = 255.toString(16)       // "ff"
val abs = (-10).absoluteValue    // 10

// Nullable types typically use wrappers
val nullable: Int? = null        // Uses java.lang.Integer
val notNull: Int = 10            // Uses primitive int when possible

// Comparison
val a: Int = 1000
val b: Int = 1000
println(a == b)   // true (value equality)
println(a === b)  // reference equality; depends on representation
```

### Key Differences

#### 1. Unified Type System

From Kotlin's point of view, numeric and boolean types behave like regular classes and can be used in generics, have extension functions, etc., while the compiler picks primitives or wrappers underneath.

```kotlin
fun <T> identity(value: T): T = value

val x = identity(42)          // T inferred as Int (boxed in generic context)
val s = identity("hello")
val list = identity(listOf(1, 2, 3))
```

```java
public static <T> T identity(T value) {
    return value;
}

Integer i = identity(42);   // 42 autoboxed to Integer
String s = identity("hello");

// Overloads required to avoid boxing for primitives
public static int identityInt(int value) { return value; }
public static double identityDouble(double value) { return value; }
```

Kotlin uses one syntax (`Int`, `Double`, etc.) regardless of whether values are implemented as primitives or wrappers; Java has distinct primitive and wrapper types.

#### 2. Nullability

```kotlin
val notNull: Int = 10        // Cannot be null
val nullable: Int? = null    // Can be null
val result = nullable?.plus(5)

val primitive: Int = 42      // usually primitive int
val boxed: Int? = 42         // `Integer` under the hood
```

```java
int primitive = 10;          // Cannot be null
Integer wrapper = null;      // Can be null; NPE risk on unboxing
```

Kotlin encodes nullability in the type system and enforces it at compile time; Java relies on conventions and runtime checks.

#### 3. Methods on "Primitives"

```kotlin
val number = 42
println(number.toString())
println(number.toDouble())
println(number.coerceIn(0, 100))

fun Int.isEven() = this % 2 == 0
println(42.isEven())
```

```java
int number = 42;
String str = Integer.toString(number);
Integer boxed = 42;
String text = boxed.toString();
```

Kotlin exposes methods and extensions on these types directly; Java requires wrappers or utility methods for similar behavior.

#### 4. When Kotlin Uses Primitives Vs Wrappers

Kotlin compiles to JVM primitives when:
- Types are non-nullable (`Int`, `Double`, etc.).
- They are used in primitive arrays (`IntArray`, `DoubleArray`, etc.).

It uses wrapper types when:
- Types are nullable (`Int?`, etc.).
- Used as generic type arguments: `List<Int>`, `Map<String, Int>`.
- In `Array<Int>` and other object arrays.
- For platform types from Java when needed.

```kotlin
val primitive: Int = 10                // int
val nullableInt: Int? = 10             // Integer
val list: List<Int> = listOf(1, 2, 3)  // List<Integer>
val intArray: IntArray = intArrayOf(1, 2, 3)   // int[]
val boxedArray: Array<Int> = arrayOf(1, 2, 3)  // Integer[]
```

### Arrays - Special Case

Kotlin distinguishes between primitive arrays and object arrays, mapping closely to Java:

```kotlin
// Primitive arrays (efficient)
val intArray = IntArray(5)         // int[]
val doubleArray = DoubleArray(5)   // double[]
val byteArray = ByteArray(5)       // byte[]

intArray[0] = 42
println(intArray.size)  // 5

// With initialization
val numbers = intArrayOf(1, 2, 3, 4, 5)
val doubles = doubleArrayOf(1.0, 2.0, 3.0)

// Object arrays
val boxedArray = Array<Int>(5) { 0 }  // Integer[]
val stringArray = arrayOf("a", "b")   // String[]

// Conversions (require element-wise transformation under the hood)
val primitiveToBoxed = intArray.toTypedArray()  // IntArray -> Array<Int> -> Integer[]
val boxedToPrimitive = boxedArray.toIntArray()  // Array<Int> -> IntArray -> int[]
```

```java
// Primitive arrays
int[] intArray = new int[5];
double[] doubleArray = new double[5];

intArray[0] = 42;

// Object arrays
Integer[] boxedArray = new Integer[5];
String[] stringArray = {"a", "b"};

// No direct cast between int[] and Integer[]
// Integer[] boxed = (Integer[]) intArray;  // Compile-time error

// Must convert element-wise (loop or streams)
Integer[] boxed = Arrays.stream(intArray)
                        .boxed()
                        .toArray(Integer[]::new);
```

Key points:
- Primitive arrays (`IntArray`, etc. / `int[]`, etc.) are more memory- and CPU-efficient.
- Conversions between primitive arrays and boxed/object arrays always require iteration.

### Performance

Kotlin aims to match Java's performance characteristics for primitives while providing a cleaner type model.

```kotlin
class Counter {
    var count: Int = 0      // Typically compiled as a primitive int field

    fun increment() {
        count++             // Efficient primitive operation
    }
}

// Standard library collections store numbers as boxed types on the JVM
val list = listOf(1, 2, 3)  // List<Int> -> List<Integer>

// Use primitive arrays for large numeric data
val bigArray = IntArray(1_000_000) { it }
```

Illustrative comparison:

```kotlin
// Fast: primitive array (no boxing)
val primitiveArray = IntArray(1_000_000)
for (i in primitiveArray.indices) {
    primitiveArray[i] = i * 2
}

// Slower: Array<Int> (boxing/unboxing on each element)
val boxedArray = Array(1_000_000) { 0 }
for (i in boxedArray.indices) {
    boxedArray[i] = i * 2
}

// Heavier: List<Int> (immutable structure + boxed elements)
val list = List(1_000_000) { it }
```

So, for large numeric datasets, prefer primitive arrays over `Array<Int>` or `List<Int>` when performance matters.

### Unsigned Types (Kotlin 1.3+)

Kotlin adds unsigned numeric types (Java has no dedicated unsigned primitives):

```kotlin
val uByte: UByte = 200u
val uShort: UShort = 50000u
val uInt: UInt = 4_000_000_000u
val uLong: ULong = 10_000_000_000uL

val uIntArray = UIntArray(5)
val uBytes = ubyteArrayOf(200u, 255u)

val sum = 100u + 50u
val overflow = UByte.MAX_VALUE + 1u
```

These are implemented with compiler support and mapped onto existing JVM types but behave as unsigned in Kotlin code.

### Interoperability with Java

When Kotlin calls Java:

```kotlin
// Java: public int calculate(int a, Integer b)
val result = javaObject.calculate(10, 20)

// Java: Integer getNullableInt()
val nullable: Int? = javaObject.getNullableInt()  // Safe
// val notNull: Int = javaObject.getNullableInt() // Unsafe: possible NPE
```

When Java calls Kotlin:

```java
// Kotlin: fun process(value: Int): Int
int r1 = kotlinObject.process(42);   // uses primitive int

// Kotlin: fun process(value: Int?): Int?
Integer r2 = kotlinObject.process(null); // uses Integer

// Kotlin: val numbers: IntArray
int[] array = kotlinObject.getNumbers();

// Kotlin: val boxed: Array<Int>
Integer[] boxedArray = kotlinObject.getBoxed();
```

Understanding when values are primitives vs wrappers at the boundaries is important to avoid accidental boxing or NPEs.

### Comparative Table

| Aspect | Java | Kotlin |
|--------|------|--------|
| Primitives | 8 explicit primitive types | No separate primitive syntax; uses `Int`, etc. |
| Wrappers | Separate wrapper classes | Used automatically when needed |
| Methods on primitives | None (use wrappers/utils) | Available via member/extension functions |
| Nullability | Only via wrappers | Built-in nullability with `?` and checks |
| Autoboxing | Explicit pitfalls (`==`, caching, NPE) | Boxing exists but mostly hidden; `==` is value equality |
| Generics | Work with reference types only | Same syntax; primitives boxed in generic contexts |
| Unsigned types | Not built-in | Built-in (`UByte`, `UShort`, `UInt`, `ULong`) |

### Kotlin Best Practices (Summary)

```kotlin
// Prefer non-nullable types when possible
val count: Int = 0  // Typically compiled to a primitive

// Use nullable only when it reflects real absence of a value
val maybeValue: Int? = null

// Use primitive arrays for large numeric data
val bigData = IntArray(1_000_000)

// Use collections (List/Set/Map) for expressiveness, knowing they store boxed numbers
val smallList = listOf(1, 2, 3)

// Avoid unnecessary nullable wrappers
val bad: Int? = 42     // Prefer non-nullable Int

// Avoid Array<Int> for huge numeric datasets
val inefficient = Array(1_000_000) { 0 }  // Prefer IntArray
```

## Follow-ups

- What are common boxing/autoboxing pitfalls in mixed Kotlin/Java code?
- When would you choose primitive arrays vs collections in Kotlin?
- How does null-safety in Kotlin reduce NPE risks compared to Java's primitive/wrapper model?

## References

- [[c-kotlin]]
- https://kotlinlang.org/docs/home.html

## Related Questions

- [[q-flowon-operator-context-switching--kotlin--hard]]
- [[q-kotlin-reflection--kotlin--medium]]
