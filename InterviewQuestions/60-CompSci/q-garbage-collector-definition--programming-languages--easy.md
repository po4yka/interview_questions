---
id: 20251012-1227111141
title: "Garbage Collector Definition / Определение Garbage Collector"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - automatic-memory
  - garbage-collection
  - gc
  - java
  - jvm
  - kotlin
  - memory-management
  - programming-languages
---
# Что такое сборщик мусора?

# Question (EN)
> What is a garbage collector?

# Вопрос (RU)
> Что такое сборщик мусора?

---

## Answer (EN)

**Garbage Collector (GC)** is a **memory management mechanism** that **automatically frees memory** allocated for objects that are no longer used in the program.

This feature is present in many modern programming languages (Java, Kotlin, C#, Python, JavaScript, Go) where manual memory management (like in C or C++) is not required.

## How It Works

The garbage collector operates in **background mode**, periodically scanning program memory for objects that are no longer accessible for use.

**Object accessibility** is usually determined by the presence of **live references** to it. If there are no active references to an object, it's considered no longer needed and the memory it occupies can be freed.

### Basic Principles

Many garbage collection algorithms use the following core principles:

**1. Marking (Mark Phase)**

Scans objects accessible from the **root set** (e.g., stack variables, static variables) and marks all objects that can be reached directly or indirectly as **live**.

```kotlin
// Root objects (reachable)
val user = User("John")         // Stack variable - ROOT
companion object {
    val config = Config()       // Static variable - ROOT
}

// Reachable objects
val profile = user.profile      // Reachable from user ROOT
val settings = config.settings  // Reachable from config ROOT

// Unreachable objects (can be collected)
var temp = Data()
temp = null  // Original Data() now unreachable → GC eligible
```

**2. Sweeping (Sweep Phase)**

The collector then goes through all heap memory and frees memory occupied by objects that were not marked as live.

```
Heap Memory:

Before GC:
[User] ← live (marked)
[Profile] ← live (marked, referenced by User)
[TempData] ← dead (not marked, no references)
[Config] ← live (marked)

After GC:
[User] ← kept
[Profile] ← kept
[        ] ← freed (was TempData)
[Config] ← kept
```

**3. Compacting (optional)**

Some GC algorithms also compact memory by moving live objects together to reduce fragmentation.

```
Before Compaction:
[Object1] [      ] [Object2] [      ] [Object3]
  (live)  (freed)   (live)  (freed)   (live)

After Compaction:
[Object1] [Object2] [Object3] [                ]
  compact    compact   compact     free space
```

---

## GC Algorithms

### Generational GC (Most Common)

Objects are divided into generations based on their lifetime:

- **Young Generation** - newly created objects
- **Old Generation** - long-lived objects
- **Minor GC** - collects young generation (fast, frequent)
- **Major/Full GC** - collects entire heap (slow, rare)

```kotlin
// Young generation (short-lived)
fun processRequest() {
    val request = Request()  // Created
    val response = handle(request)
    return response
    // request becomes eligible for GC immediately after function exits
}

// Old generation (long-lived)
object Cache {
    val data = mutableMapOf<String, Any>()  // Lives for app lifetime
}
```

### Mark and Sweep

Classic algorithm that marks live objects, then sweeps dead ones.

### Copying GC

Divides heap into two spaces, copies live objects to one space, then swaps.

### Reference Counting (not in JVM)

Counts references to each object, frees when count reaches zero (used in Python, Swift).

---

## Advantages

### 1. Reduced Memory Management Errors

Automatic memory management significantly reduces risks of errors such as:

**Memory leaks** - memory is allocated but not freed:

```kotlin
// - GOOD - No manual memory management needed
class UserCache {
    private val cache = mutableListOf<User>()

    fun addUser(user: User) {
        cache.add(user)
        // No need to manually free memory
    }
}

// GC automatically frees when cache or users are no longer referenced
```

**Double free** - memory is freed more than once:

```c
// - C/C++ problem (doesn't exist in GC languages)
free(ptr);
free(ptr);  // Double free - crash!
```

**Use after free** - accessing freed memory:

```c
// - C/C++ problem (doesn't exist in GC languages)
free(ptr);
*ptr = 10;  // Use after free - undefined behavior!
```

### 2. Development Simplicity

No need to spend time on explicit memory management, which simplifies the development process.

```kotlin
// - Kotlin - Simple, safe
fun createUsers(): List<User> {
    return listOf(
        User("Alice"),
        User("Bob")
    )
}  // Objects live as long as needed, then GC collects them

// - C - Manual memory management
// User* create_users(int* count) {
//     User* users = (User*)malloc(2 * sizeof(User));
//     // ... initialize users
//     *count = 2;
//     return users;
// }
// // Caller must remember to free(users)!
```

---

## Disadvantages

### 1. Unpredictability

Garbage collection can occur **at any time**, which can lead to **short-term delays** in program execution, especially if GC takes a long time.

```kotlin
// GC can pause application at unpredictable times
fun processFrame() {
    // Rendering frame
    drawUI()  // Takes 5ms

    // GC might pause here for 10-50ms!
    // This causes frame drops and UI jank

    updateAnimations()
}

// Result: Inconsistent frame times
// Frame 1: 16ms GOOD
// Frame 2: 45ms - (GC pause)
// Frame 3: 16ms GOOD
```

**Stop-the-World (STW) Pauses:**

During some GC phases, all application threads are paused:

```
Application Running → GC Pause (STW) → Application Resumes
     ||||||||||||       [pause]          ||||||||||||
     Normal execution   All threads      Normal execution
                        stopped!
```

### 2. Overhead

Garbage collection consumes **system resources** such as CPU time and memory, which can reduce overall application performance.

```kotlin
// GC overhead
// 1. CPU time for scanning and marking objects
// 2. Memory overhead for tracking object metadata
// 3. Pause times during collection cycles

// Example: Server handling requests
fun handleRequest(request: Request): Response {
    // Create temporary objects
    val data = parseRequest(request)      // Allocates memory
    val result = processData(data)        // More allocations
    return createResponse(result)         // More allocations
}

// After many requests:
// - Lots of garbage created
// - GC must run frequently
// - CPU time spent on GC instead of serving requests
```

**Memory Overhead:**

GC needs extra memory to track objects:

```
Application needs: 100 MB
GC overhead:       +20 MB (for metadata, tracking)
Total:             120 MB
```

---

## GC in Different Languages

### Kotlin/Java (JVM)

```kotlin
// Generational GC
val obj = MyObject()  // Allocated in young generation

// Explicit GC hint (not recommended)
System.gc()  // Just a hint, not guaranteed to run

// Monitor GC
// Enable GC logs: -XX:+PrintGCDetails
```

**JVM GC Options:**
- Serial GC - single-threaded
- Parallel GC - multi-threaded (default)
- CMS (Concurrent Mark Sweep) - low pause times
- G1 GC - balanced (Java 9+ default)
- ZGC, Shenandoah - ultra-low latency

### JavaScript

```javascript
// Automatic GC, no control
let obj = { data: "large data" };
obj = null;  // Now eligible for GC
```

### Python

```python

# Reference counting + cycle detection
import gc

# Disable automatic GC
gc.disable()

# Run GC manually
gc.collect()
```

### Go

```go
// Concurrent GC
var data = make([]byte, 1000000)
data = nil  // Eligible for GC

// Trigger GC
runtime.GC()
```

---

## Avoiding GC Problems

### 1. Object Pooling

Reuse objects instead of creating new ones:

```kotlin
// - BAD - Creates garbage
fun processItems(items: List<Item>) {
    for (item in items) {
        val result = Result()  // New object each iteration
        process(item, result)
    }
}

// - GOOD - Reuse object
fun processItems(items: List<Item>) {
    val result = Result()  // Created once
    for (item in items) {
        result.reset()
        process(item, result)
    }
}
```

### 2. Avoid Unnecessary Allocations

```kotlin
// - BAD - Creates string garbage
fun buildMessage(count: Int): String {
    var msg = ""
    for (i in 0 until count) {
        msg += "Item $i, "  // Creates new string each time!
    }
    return msg
}

// - GOOD - Single allocation
fun buildMessage(count: Int): String {
    return buildString {
        for (i in 0 until count) {
            append("Item $i, ")
        }
    }
}
```

### 3. Use Sequences for Large Collections

```kotlin
// - BAD - Creates intermediate collections
val result = list
    .filter { it > 10 }      // Intermediate list
    .map { it * 2 }          // Another intermediate list
    .take(5)                 // Another intermediate list

// - GOOD - Lazy evaluation, no intermediate collections
val result = list.asSequence()
    .filter { it > 10 }
    .map { it * 2 }
    .take(5)
    .toList()
```

---

## Summary

**Garbage Collector:**
- Automatic memory management mechanism
- Frees memory of unused objects
- Works in background by scanning for unreachable objects
- Uses mark-and-sweep (and variations) algorithms

**Advantages:**
- - Eliminates memory leaks
- - Prevents double-free errors
- - Simplifies development

**Disadvantages:**
- - Unpredictable pauses (Stop-the-World)
- - CPU and memory overhead
- - Can impact performance

**Best practices:**
- Minimize object allocations
- Reuse objects when possible
- Use object pools for frequent allocations
- Monitor GC behavior in production

---

## Ответ (RU)

**Garbage Collector (GC, Сборщик мусора)** — это **механизм управления памятью**, который **автоматически освобождает память**, выделенную для объектов, которые больше не используются в программе.

Эта функция присутствует во многих современных языках программирования (Java, Kotlin, C#, Python, JavaScript, Go), где не требуется ручное управление памятью (как в C или C++).

## Как он работает

Сборщик мусора работает в **фоновом режиме**, периодически сканируя память программы на предмет объектов, которые больше не доступны для использования.

**Доступность объекта** обычно определяется по наличию **живых ссылок** на него. Если на объект нет активных ссылок, то считается, что он больше не нужен и память, которую он занимает, может быть освобождена.

### Базовые Принципы

Многие алгоритмы сборки мусора используют следующие базовые принципы:

**1. Пометка (Mark Phase)**

Сканирует объекты, доступные из **корневого набора** (например, переменные стека, статические переменные) и помечает все объекты, которые можно достичь напрямую или косвенно, как **живые**.

```kotlin
// Корневые объекты (достижимые)
val user = User("John")         // Переменная стека - ROOT
companion object {
    val config = Config()       // Статическая переменная - ROOT
}

// Достижимые объекты
val profile = user.profile      // Достижим из user ROOT
val settings = config.settings  // Достижим из config ROOT

// Недостижимые объекты (могут быть собраны)
var temp = Data()
temp = null  // Оригинальный Data() теперь недостижим → GC eligible
```

**2. Очистка (Sweep Phase)**

Затем сборщик проходит по всей heap памяти и освобождает память, занимаемую объектами, которые не были помечены как живые.

```
Heap Memory:

До GC:
[User] ← живой (помечен)
[Profile] ← живой (помечен, ссылается User)
[TempData] ← мёртвый (не помечен, нет ссылок)
[Config] ← живой (помечен)

После GC:
[User] ← оставлен
[Profile] ← оставлен
[        ] ← освобождён (был TempData)
[Config] ← оставлен
```

**3. Уплотнение (Compacting, опционально)**

Некоторые алгоритмы GC также уплотняют память, перемещая живые объекты вместе для уменьшения фрагментации.

```
До уплотнения:
[Object1] [      ] [Object2] [      ] [Object3]
  (живой) (освобождён) (живой) (освобождён) (живой)

После уплотнения:
[Object1] [Object2] [Object3] [                ]
  compact    compact   compact     свободное место
```

---

## Алгоритмы GC

### Generational GC (Наиболее распространённый)

Объекты разделяются на поколения в зависимости от их времени жизни:

- **Young Generation** - только что созданные объекты
- **Old Generation** - долгоживущие объекты
- **Minor GC** - собирает молодое поколение (быстро, часто)
- **Major/Full GC** - собирает весь heap (медленно, редко)

```kotlin
// Молодое поколение (короткоживущие)
fun processRequest() {
    val request = Request()  // Создан
    val response = handle(request)
    return response
    // request становится eligible для GC сразу после выхода из функции
}

// Старое поколение (долгоживущие)
object Cache {
    val data = mutableMapOf<String, Any>()  // Живёт всё время работы приложения
}
```

### Mark and Sweep

Классический алгоритм, который помечает живые объекты, затем очищает мёртвые.

### Copying GC

Разделяет heap на два пространства, копирует живые объекты в одно пространство, затем меняет их местами.

### Reference Counting (не в JVM)

Считает ссылки на каждый объект, освобождает когда счётчик достигает нуля (используется в Python, Swift).

---

## Преимущества

### 1. Уменьшение ошибок управления памятью

Автоматическое управление памятью значительно снижает риски ошибок, таких как:

**Утечки памяти** - память выделяется, но не освобождается:

```kotlin
// ХОРОШО - Не нужно ручное управление памятью
class UserCache {
    private val cache = mutableListOf<User>()

    fun addUser(user: User) {
        cache.add(user)
        // Не нужно вручную освобождать память
    }
}

// GC автоматически освобождает когда cache или users больше не используются
```

**Double free** - память освобождается более одного раза:

```c
// Проблема C/C++ (не существует в GC языках)
free(ptr);
free(ptr);  // Double free - crash!
```

**Use after free** - доступ к освобождённой памяти:

```c
// Проблема C/C++ (не существует в GC языках)
free(ptr);
*ptr = 10;  // Use after free - undefined behavior!
```

### 2. Простота разработки

Нет необходимости тратить время на явное управление памятью, что упрощает процесс разработки.

```kotlin
// Kotlin - Просто, безопасно
fun createUsers(): List<User> {
    return listOf(
        User("Alice"),
        User("Bob")
    )
}  // Объекты живут столько, сколько нужно, затем GC собирает их

// C - Ручное управление памятью
// User* create_users(int* count) {
//     User* users = (User*)malloc(2 * sizeof(User));
//     // ... инициализация users
//     *count = 2;
//     return users;
// }
// // Вызывающий должен помнить о free(users)!
```

---

## Недостатки

### 1. Непредсказуемость

Сборка мусора может произойти **в любой момент**, что может привести к **кратковременным задержкам** в выполнении программы, особенно если GC занимает много времени.

```kotlin
// GC может приостановить приложение в непредсказуемые моменты
fun processFrame() {
    // Рендеринг кадра
    drawUI()  // Занимает 5ms

    // GC может сделать паузу здесь на 10-50ms!
    // Это вызывает пропуск кадров и дрожание UI

    updateAnimations()
}

// Результат: Непостоянное время кадров
// Кадр 1: 16ms ХОРОШО
// Кадр 2: 45ms - (пауза GC)
// Кадр 3: 16ms ХОРОШО
```

**Stop-the-World (STW) Паузы:**

Во время некоторых фаз GC все потоки приложения приостанавливаются:

```
Приложение работает → Пауза GC (STW) → Приложение возобновляется
     ||||||||||||       [pause]          ||||||||||||
     Нормальное          Все потоки       Нормальное
     выполнение          остановлены!     выполнение
```

### 2. Накладные расходы

Сборка мусора потребляет **системные ресурсы**, такие как время CPU и память, что может снизить общую производительность приложения.

```kotlin
// Накладные расходы GC
// 1. Время CPU для сканирования и пометки объектов
// 2. Накладные расходы памяти для отслеживания метаданных объектов
// 3. Паузы во время циклов сборки

// Пример: Сервер обрабатывающий запросы
fun handleRequest(request: Request): Response {
    // Создание временных объектов
    val data = parseRequest(request)      // Выделяет память
    val result = processData(data)        // Больше выделений
    return createResponse(result)         // Больше выделений
}

// После многих запросов:
// - Создаётся много мусора
// - GC должен запускаться часто
// - Время CPU тратится на GC вместо обслуживания запросов
```

**Накладные расходы памяти:**

GC нужна дополнительная память для отслеживания объектов:

```
Приложению нужно: 100 MB
Накладные расходы GC: +20 MB (для метаданных, отслеживания)
Всего:            120 MB
```

---

## Резюме

**Garbage Collector:**
- Механизм автоматического управления памятью
- Освобождает память неиспользуемых объектов
- Работает в фоновом режиме, сканируя недостижимые объекты
- Использует алгоритмы mark-and-sweep (и вариации)

**Преимущества:**
- Устраняет утечки памяти
- Предотвращает ошибки double-free
- Упрощает разработку

**Недостатки:**
- Непредсказуемые паузы (Stop-the-World)
- Накладные расходы CPU и памяти
- Может влиять на производительность

**Лучшие практики:**
- Минимизировать выделение объектов
- Переиспользовать объекты когда возможно
- Использовать пулы объектов для частых выделений
- Мониторить поведение GC в продакшене

