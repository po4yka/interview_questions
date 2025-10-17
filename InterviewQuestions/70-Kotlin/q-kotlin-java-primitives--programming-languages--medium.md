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

Kotlin и Java используют разные подходы к примитивным типам данных. Java имеет явные примитивы, а Kotlin предоставляет унифицированную систему типов.

### Java примитивы

Java содержит **8 примитивных типов** и соответствующие классы-обертки:

| Тип | Размер | Диапазон | Класс-обертка |
|------|------|-------|---------------|
| `byte` | 8 бит | -128 до 127 | `Byte` |
| `short` | 16 бит | -32,768 до 32,767 | `Short` |
| `int` | 32 бит | -2³¹ до 2³¹-1 | `Integer` |
| `long` | 64 бит | -2⁶³ до 2⁶³-1 | `Long` |
| `float` | 32 бит | IEEE 754 | `Float` |
| `double` | 64 бит | IEEE 754 | `Double` |
| `char` | 16 бит | Unicode символ | `Character` |
| `boolean` | 1 бит | `true` / `false` | `Boolean` |

**Код на Java:**
```java
// Примитивы - хранятся на стеке, нет методов
int x = 10;
double y = 3.14;
boolean flag = true;

// Классы-обертки - хранятся на куче, есть методы
Integer boxed = 10;  // Autoboxing (автоупаковка)
int unboxed = boxed;  // Unboxing (распаковка)

// Примитивы не могут быть null
int value = null;  // Ошибка компиляции!
Integer nullable = null;  // OK - класс-обертка

// Проблема autoboxing
Integer a = 1000;
Integer b = 1000;
System.out.println(a == b);      // false! (сравнение ссылок)
System.out.println(a.equals(b)); // true (сравнение значений)

// Кэширование Integer (-128 до 127)
Integer c = 100;
Integer d = 100;
System.out.println(c == d);  // true (кэшированные объекты)
```

### Kotlin "примитивы"

Kotlin **не имеет примитивных типов** с точки зрения разработчика. Вместо этого используются **классы**, которые компилятор оптимизирует в JVM примитивы когда возможно:

| Тип Kotlin | JVM примитив | JVM обертка |
|-------------|---------------|-------------|
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
// Выглядят как объекты, но компилируются в примитивы когда возможно
val x: Int = 10          // Компилируется в: int x = 10
val y: Double = 3.14     // Компилируется в: double y = 3.14
val flag: Boolean = true // Компилируется в: boolean flag = true

// Можно вызывать методы (это объекты в Kotlin)
val hex = 255.toString(16)  // "ff"
val abs = (-10).absoluteValue  // 10
val pi = 3.14159.roundToInt()  // 3

// Nullable типы компилируются в классы-обертки
val nullable: Int? = null    // Компилируется в: Integer nullable = null
val notNull: Int = 10        // Компилируется в: int notNull = 10

// Нет проблем с autoboxing
val a: Int = 1000
val b: Int = 1000
println(a == b)   // true (всегда сравнение значений!)
println(a === b)  // зависит от оптимизации (сравнение ссылок)
```

### Ключевые различия

#### 1. Унифицированная система типов

**Kotlin:**
```kotlin
// В Kotlin все типы - объекты
fun <T> identity(value: T): T = value

val x = identity(42)        // Работает! Int это объект
val s = identity("hello")   // Тоже работает!
val list = identity(listOf(1, 2, 3))  // И это работает

// Обобщенные функции работают с любыми типами
fun <T> printValue(value: T) {
    println(value)
}

printValue(10)      // Int
printValue(3.14)    // Double
printValue("text")  // String
```

**Java:**
```java
// В Java примитивы не объекты
public <T> T identity(T value) {
    return value;
}

// identity(42);  // Ошибка! int не T
Integer result = identity(42);  // Нужен autoboxing

// Нужны отдельные методы для примитивов
public int identityInt(int value) { return value; }
public double identityDouble(double value) { return value; }

// Или использовать обертки везде (потеря производительности)
```

#### 2. Nullable типы

**Kotlin:**
```kotlin
// Явное различие nullable vs non-nullable
val notNull: Int = 10           // Не может быть null
// notNull = null  // Ошибка компиляции!

val nullable: Int? = null       // Может быть null
val result = nullable?.plus(5)  // Safe call

// Компилируется по-разному:
val primitive: Int = 42         // → int (примитив JVM)
val boxed: Int? = 42            // → Integer (обертка JVM)

// Умная обработка null
fun processNumber(n: Int?) {
    if (n != null) {
        println(n * 2)  // Smart cast к Int (non-null)
    }
}
```

**Java:**
```java
// Примитивы не могут быть null, обертки могут
int primitive = 10;
// primitive = null;  // Ошибка!

Integer wrapper = null;  // OK
// int result = wrapper + 5;  // NullPointerException!

// Нужны ручные проверки
if (wrapper != null) {
    int result = wrapper + 5;
}

// Нет различия на уровне типов для null-safety
```

#### 3. Методы на "примитивах"

**Kotlin:**
```kotlin
// Методы доступны напрямую
val number = 42
println(number.toString())      // "42"
println(number.toDouble())      // 42.0
println(number.coerceIn(0, 100))  // 42

val binary = 10.toString(2)     // "1010"
val max = 5.coerceAtLeast(10)   // 10

// Методы расширения
fun Int.isEven() = this % 2 == 0
println(42.isEven())  // true

// Операторы как методы
val sum = 10.plus(5)       // 15 (то же что 10 + 5)
val product = 3.times(4)   // 12 (то же что 3 * 4)
```

**Java:**
```java
// Примитивы не имеют методов
int number = 42;
// number.toString();  // Ошибка!

// Нужны обертки или статические методы
String str = Integer.toString(number);
double d = Integer.valueOf(number).doubleValue();

// Обертки имеют методы
Integer boxed = 42;
String text = boxed.toString();  // OK

// Статические методы утилит
int max = Math.max(5, 10);
int abs = Math.abs(-5);
```

#### 4. Когда Kotlin использует примитивы vs обертки

**Компилируется в JVM примитивы:**
```kotlin
// Non-nullable типы в локальных переменных
val x: Int = 10           // int x = 10

// Non-nullable параметры и возвращаемые типы
fun add(a: Int, b: Int): Int = a + b  // int add(int a, int b)

// Примитивные массивы
val intArray: IntArray = intArrayOf(1, 2, 3)        // int[]
val doubleArray: DoubleArray = doubleArrayOf(1.0)   // double[]
val boolArray: BooleanArray = booleanArrayOf(true)  // boolean[]
```

**Компилируется в обертки:**
```kotlin
// Nullable типы
val nullable: Int? = 10              // Integer nullable = 10

// Параметры обобщенных типов
val list: List<Int> = listOf(1, 2)   // List<Integer>
val map: Map<String, Int> = mapOf()  // Map<String, Integer>

// Platform types из Java
// fun javaMethod(): Int! → может быть int или Integer

// Массивы объектов
val boxedArray: Array<Int> = arrayOf(1, 2, 3)  // Integer[]
```

**Примеры компиляции:**
```kotlin
// Kotlin код
fun calculate(a: Int, b: Int?): Int? {
    val local: Int = 10
    val nullable: Int? = null
    return if (b != null) a + b else null
}

// Скомпилируется примерно в:
// Java байткод
public Integer calculate(int a, Integer b) {
    int local = 10;           // примитив
    Integer nullable = null;  // обертка
    return (b != null) ? a + b : null;
}
```

### Массивы - особый случай

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
val primitiveToBoxed = intArray.toTypedArray()  // Integer[]
val boxedToPrimitive = boxedArray.toIntArray()  // int[]
```

**Java:**
```java
// Примитивные массивы
int[] intArray = new int[5];           // примитивы
double[] doubleArray = new double[5];  // примитивы

intArray[0] = 42;

// Массивы объектов
Integer[] boxedArray = new Integer[5];  // обертки
String[] stringArray = {"a", "b"};

// Нельзя преобразовать напрямую
// Integer[] boxed = (Integer[]) intArray;  // Ошибка!

// Нужна ручная конвертация
Integer[] boxed = Arrays.stream(intArray)
                         .boxed()
                         .toArray(Integer[]::new);
```

### Производительность

**Kotlin оптимизации:**
```kotlin
// Компилятор оптимизирует
class Counter {
    var count: Int = 0  // Примитив int в JVM

    fun increment() {
        count++  // Эффективная операция на примитиве
    }
}

// Коллекции используют обертки
val list = listOf(1, 2, 3)  // List<Integer> - накладные расходы

// Используйте примитивные массивы для производительности
val bigArray = IntArray(1_000_000) { it }  // Эффективно
// val bigList = List(1_000_000) { it }  // Менее эффективно
```

**Сравнение производительности:**
```kotlin
// Быстро - примитивный массив
val primitiveArray = IntArray(1_000_000)
for (i in primitiveArray.indices) {
    primitiveArray[i] = i * 2  // Примитивные операции
}

// Медленнее - Array<Int> (обертки)
val boxedArray = Array(1_000_000) { 0 }
for (i in boxedArray.indices) {
    boxedArray[i] = i * 2  // Autoboxing/unboxing
}

// Еще медленнее - List<Int> (неизменяемая коллекция)
val list = List(1_000_000) { 0 }
// Нельзя изменить элементы напрямую
```

### Unsigned типы (Kotlin 1.3+)

Kotlin добавляет беззнаковые типы (недоступны в Java):

```kotlin
// Unsigned типы
val uByte: UByte = 200u           // 0 до 255
val uShort: UShort = 50000u       // 0 до 65,535
val uInt: UInt = 4_000_000_000u   // 0 до 2³²-1
val uLong: ULong = 10000000000u   // 0 до 2⁶⁴-1

// Unsigned массивы
val uIntArray = UIntArray(5)
val uBytes = ubyteArrayOf(200u, 255u)

// Операции
val sum = 100u + 50u              // UInt
val overflow = UByte.MAX_VALUE + 1u  // Переполнение до 0

println(UByte.MAX_VALUE)  // 255
println(UInt.MAX_VALUE)   // 4294967295
```

### Взаимодействие с Java

**Из Kotlin вызов Java:**
```kotlin
// Java метод: public int calculate(int a, Integer b)
val result = javaObject.calculate(10, 20)  // Автоматическая конвертация

// Java метод возвращает Integer (nullable!)
val nullable: Int? = javaObject.getNullableInt()  // Правильно
// val notNull: Int = javaObject.getNullableInt()  // Опасно!
```

**Из Java вызов Kotlin:**
```java
// Kotlin: fun process(value: Int): Int
int result = kotlinObject.process(42);  // OK

// Kotlin: fun process(value: Int?): Int?
Integer result = kotlinObject.process(null);  // OK

// Kotlin: val numbers: IntArray
int[] array = kotlinObject.getNumbers();  // Примитивный массив

// Kotlin: val boxed: Array<Int>
Integer[] boxedArray = kotlinObject.getBoxed();  // Массив объектов
```

### Сравнительная таблица

| Аспект | Java | Kotlin |
|--------|------|--------|
| **Примитивы** | Да (8 типов) | Нет (унифицированная система) |
| **Обертки** | Отдельные классы | Используются автоматически |
| **Методы на примитивах** | Нет | Да |
| **Nullable** | Только обертки | Явный синтаксис `?` |
| **Autoboxing** | Автоматический (с подводными камнями) | Автоматический (без проблем) |
| **Производительность** | Примитивы vs обертки | Оптимизируется компилятором |
| **Обобщения** | Только обертки | Работают прозрачно |
| **Unsigned типы** | Нет | Да (UByte, UInt, ULong, UShort) |

### Резюме

**Java:**
- 8 явных примитивных типов
- Отдельные классы-обертки для каждого
- Нет методов на примитивах
- Autoboxing может быть проблемным
- Нужно помнить о различии примитив vs обертка

**Kotlin:**
- Унифицированная система типов (все объекты)
- Автоматическая оптимизация в примитивы JVM
- Методы доступны на всех типах
- Явное различие nullable vs non-nullable
- Безопасная работа с null
- Дополнительные unsigned типы

**Лучшие практики Kotlin:**

```kotlin
// ✅ Используйте non-nullable типы когда возможно
val count: Int = 0  // Компилируется в примитив

// ✅ Используйте nullable только при необходимости
val optional: Int? = null  // Обертка

// ✅ Примитивные массивы для производительности
val bigData = IntArray(1_000_000)

// ✅ Обычные коллекции для удобства
val smallList = listOf(1, 2, 3)

// ❌ Избегайте ненужных nullable
val unnecessary: Int? = 42  // Лучше Int

// ❌ Не используйте Array<Int> для больших данных
val inefficient = Array(1_000_000) { 0 }  // Используйте IntArray
```

