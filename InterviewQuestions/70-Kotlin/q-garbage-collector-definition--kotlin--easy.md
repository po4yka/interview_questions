---
anki_cards:
- slug: q-garbage-collector-definition--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-garbage-collector-definition--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Question (EN)
> What is a garbage collector?

## Ответ (RU)

**Garbage Collector (GC, Сборщик мусора)** — это **механизм управления памятью**, который **автоматически освобождает память**, выделенную для объектов, которые больше не могут быть использованы программой (то есть стали недостижимыми по ссылкам).

Эта функция присутствует во многих современных языках программирования (Java, Kotlin, C#, Python, JavaScript, Go и др.), где нет необходимости вручную вызывать освобождение памяти для каждого объекта (как в C или C++), хотя неправильная логика всё равно может приводить к утечкам памяти через удержание ненужных ссылок.

## Answer (EN)

**Garbage Collector (GC)** is a **memory management mechanism** that **automatically frees memory** allocated for objects that can no longer be used by the program (i.e., have become unreachable by references).

This feature is present in many modern programming languages (Java, Kotlin, C#, Python, JavaScript, Go, etc.), where you do not manually free each object (unlike in C or C++), although incorrect logic can still cause memory leaks by retaining unnecessary references.

## Как Он Работает

Сборщик мусора обычно работает автоматически и периодически (иногда в отдельных потоках, иногда с паузами), анализируя память программы на предмет объектов, которые больше не доступны для использования.

**Доступность объекта** обычно определяется по наличию **живых ссылок** на него. Если на объект нет активных ссылок из корневого набора (root set), то считается, что он больше не нужен, и память, которую он занимает, может быть освобождена.

### Базовые Принципы

Многие алгоритмы сборки мусора используют следующие базовые принципы:

**1. Пометка (Mark Phase)**

Сканирует объекты, доступные из **корневого набора** (например, ссылки из стека, регистров, статических полей), и помечает все объекты, которые можно достичь напрямую или косвенно, как **живые**.

```kotlin
// Корневые объекты (достижимые из root set)
val user = User("John")         // Локальная переменная, достижима из стека - ROOT
companion object {
    val config = Config()       // Статическое/companion-поле - ROOT
}

// Достижимые объекты
val profile = user.profile      // Достижим из user (ROOT)
val settings = config.settings  // Достижим из config (ROOT)

// Недостижимые объекты (могут быть собраны)
var temp = Data()
temp = null  // Оригинальный Data() теперь недостижим → GC-eligible
```

**2. Очистка (Sweep Phase)**

Затем сборщик проходит по всей heap-памяти и освобождает память, занимаемую объектами, которые не были помечены как живые.

```text
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

```text
До уплотнения:
[Object1] [      ] [Object2] [      ] [Object3]
  (живой) (освобождён) (живой) (освобождён) (живой)

После уплотнения:
[Object1] [Object2] [Object3] [                ]
  compact    compact   compact     свободное место
```

## How It Works (EN)

A garbage collector typically runs automatically and periodically (sometimes in separate threads, sometimes with pauses), scanning the program's memory to find objects that are no longer available for use.

**Object reachability** is usually defined by the presence of **live references** to it. If an object has no active references from the root set, it is considered no longer needed, and the memory it occupies can be reclaimed.

### Basic Principles

Many GC algorithms follow these basic steps:

**1. Mark Phase**

The GC scans objects reachable from the **root set** (e.g., stack, registers, static/companion fields) and marks all objects that are directly or indirectly reachable as **live**.

```kotlin
// Root objects (reachable from root set)
val user = User("John")         // Local variable, reachable from stack - ROOT
companion object {
    val config = Config()       // Static/companion field - ROOT
}

// Reachable objects
val profile = user.profile      // Reachable from user (ROOT)
val settings = config.settings  // Reachable from config (ROOT)

// Unreachable objects (can be collected)
var temp = Data()
temp = null  // Original Data() is now unreachable → GC-eligible
```

**2. Sweep Phase**

The GC then traverses the heap and frees memory occupied by objects that were not marked as live.

```text
Heap Memory:

Before GC:
[User] ← live (marked)
[Profile] ← live (marked, referenced by User)
[TempData] ← dead (unmarked, no references)
[Config] ← live (marked)

After GC:
[User] ← kept
[Profile] ← kept
[        ] ← freed (was TempData)
[Config] ← kept
```

**3. Compacting (optional)**

Some GC algorithms also compact memory by moving live objects together to reduce fragmentation.

```text
Before compaction:
[Object1] [      ] [Object2] [      ] [Object3]
  (live)  (free)   (live)    (free)   (live)

After compaction:
[Object1] [Object2] [Object3] [                ]
  compact   compact   compact      free space
```

---

## Алгоритмы GC

### Generational GC (Наиболее распространённый)

Объекты разделяются на поколения в зависимости от их времени жизни:

- **Young Generation** - только что созданные объекты
- **Old Generation** - долгоживущие объекты
- **Minor GC** - собирает молодое поколение (быстро, часто)
- **Major/Full GC** - собирает весь heap (медленнее, реже)

```kotlin
// Молодое поколение (короткоживущие)
fun processRequest() {
    val request = Request()  // Создан
    val response = handle(request)
    return response
    // request становится eligible для GC после выхода из функции,
    // если не сохранён где-то ещё
}

// Старое поколение (долгоживущие)
object Cache {
    val data = mutableMapOf<String, Any>()  // Может жить всё время работы приложения
}
```

### Mark and Sweep

Классический алгоритм, который помечает живые объекты, затем очищает мёртвые (непомеченные).

### Copying GC

Разделяет heap на два пространства, копирует живые объекты в одно пространство, затем меняет их местами.

### Reference Counting (не В JVM)

Считает ссылки на каждый объект, освобождает, когда счётчик достигает нуля. В чистом виде не используется в JVM; в CPython применяется reference counting в комбинации с отдельным сборщиком циклических ссылок, в Swift — ARC (автоматическое управление счётчиками ссылок).

## GC Algorithms (EN)

### Generational GC (Most common)

Objects are split into generations based on their lifetime:

- **Young Generation** – newly created objects
- **Old Generation** – long-lived objects
- **Minor GC** – collects the young generation (fast, frequent)
- **Major/Full GC** – collects the whole heap (slower, rarer)

```kotlin
// Young generation (short-lived)
fun processRequest() {
    val request = Request()  // Created
    val response = handle(request)
    return response
    // request becomes eligible for GC after the function returns,
    // unless stored somewhere else
}

// Old generation (long-lived)
object Cache {
    val data = mutableMapOf<String, Any>()  // May live for the entire app lifetime
}
```

### Mark and Sweep

A classic algorithm: mark live objects, then sweep and free dead (unmarked) ones.

### Copying GC

Splits the heap into two spaces, copies live objects into the to-space, then swaps spaces.

### Reference Counting (not on the JVM)

Counts references to each object and frees it when the counter reaches zero. Not used in pure form on the JVM; CPython uses reference counting plus a cycle collector, Swift uses ARC (Automatic Reference Counting).

---

## Преимущества

### 1. Уменьшение Ошибок Управления Памятью

Автоматическое управление памятью значительно снижает риски ошибок низкоуровневого управления памятью, таких как:

**Утечки памяти из-за неосвобождённой памяти** — память выделяется вручную, но забывается освободить (типично для C/C++).

```kotlin
// ХОРОШО - Не нужно ручное освобождение памяти
class UserCache {
    private val cache = mutableListOf<User>()

    fun addUser(user: User) {
        cache.add(user)
        // Не нужно вручную освобождать память объекта user
    }
}

// GC освободит память, когда cache и/или содержащиеся в нём объекты
// станут недостижимыми. Логические "утечки" возможны, если хранить ссылки
// дольше, чем нужно.
```

Для иллюстрации ошибок ручного управления памятью (классические double free/use-after-free) можно привести пример на C:

```c
// Double free — повторное освобождение одной и той же памяти
free(ptr);
free(ptr);  // Ошибка: double free — может привести к крэшу
```

```c
// Use-after-free — обращение к уже освобождённой памяти
free(ptr);
*ptr = 10;  // Ошибка: use-after-free — неопределённое поведение
```

В языках с GC программист обычно не вызывает `free` напрямую, поэтому такого класса ошибок, связанных с ручным освобождением памяти, удаётся избежать (остаются только логические утечки из-за удержания ненужных ссылок).

### 2. Простота Разработки

Нет необходимости тратить время на явное освобождение памяти, что упрощает процесс разработки и делает код безопаснее.

```kotlin
// Kotlin - проще и безопаснее
fun createUsers(): List<User> {
    return listOf(
        User("Alice"),
        User("Bob")
    )
}  // Объекты живут столько, сколько на них есть ссылки; затем GC собирает их.

// C - Ручное управление памятью
// User* create_users(int* count) {
//     User* users = (User*)malloc(2 * sizeof(User));
//     // ... инициализация users
//     *count = 2;
//     return users;
// }
// // Вызывающий должен помнить о free(users)!
```

## Advantages (EN)

### 1. Fewer Memory Management Errors

Automatic memory management significantly reduces low-level memory bugs such as:

- Memory leaks from forgotten `free`/`delete` calls (common in C/C++)
- `Double` free (freeing the same memory twice)
- Use-after-free (accessing memory after it has been freed)

In GC-based languages, you do not manually free objects, so classical double-free/use-after-free errors from manual deallocation are avoided. Logical leaks are still possible if you keep unnecessary references.

```kotlin
class UserCache {
    private val cache = mutableListOf<User>()

    fun addUser(user: User) {
        cache.add(user)
        // No manual memory free needed
    }
}

// GC will reclaim memory when cache and/or its contents become unreachable.
```

For comparison with manual memory management pitfalls, here is an example in C:

```c
// Double free — freeing the same memory twice
free(ptr);
free(ptr);  // Error: double free — may lead to crash
```

```c
// Use-after-free — accessing freed memory
free(ptr);
*ptr = 10;  // Error: use-after-free — undefined behavior
```

GC-based environments avoid these specific classes of errors because developers do not call `free` directly.

### 2. Simpler Development

Developers do not need to manage deallocation explicitly, which simplifies code and improves safety.

```kotlin
fun createUsers(): List<User> {
    return listOf(
        User("Alice"),
        User("Bob")
    )
}  // Objects live while referenced; GC collects them afterwards.

// In C, the caller would have to remember to free allocated memory explicitly.
```

---

## Недостатки

### 1. Непредсказуемость

Сборка мусора может быть запущена **в непредсказуемый момент** (с точки зрения прикладного кода), что может привести к **кратковременным задержкам** в выполнении программы, особенно если GC-паузы достаточно длительные.

```kotlin
// GC может приостановить приложение в чувствительные моменты
fun processFrame() {
    // Рендеринг кадра
    drawUI()  // Занимает ~5ms

    // В этот момент может произойти GC-пауза
    // Это вызовет пропуск кадров и дрожание UI

    updateAnimations()
}

// Результат: Непостоянное время кадров
// Кадр 1: 16ms — ок
// Кадр 2: 45ms — пауза GC
// Кадр 3: 16ms — ок
```

**Stop-the-World (STW) Паузы:**

Во время некоторых фаз GC все или часть потоков приложения может быть приостановлена:

```text
Приложение работает → Пауза GC (STW) → Приложение возобновляется
     ||||||||||||       [pause]          ||||||||||||
     Нормальное          Потоки          Нормальное
     выполнение          остановлены      выполнение
```

### 2. Накладные Расходы

Сборка мусора потребляет **системные ресурсы**, такие как время CPU и память, что может снизить общую производительность приложения.

```kotlin
// Накладные расходы GC:
// 1. Время CPU для сканирования и пометки объектов
// 2. Дополнительная память для метаданных и структур GC
// 3. Потенциальные паузы во время циклов сборки

// Пример: Сервер, обрабатывающий запросы
fun handleRequest(request: Request): Response {
    // Создание временных объектов
    val data = parseRequest(request)      // Выделяет память
    val result = processData(data)        // Дополнительные выделения
    return createResponse(result)         // Дополнительные выделения
}

// При большом количестве запросов:
// - Создаётся много временных объектов ("мусора")
// - GC вынужден запускаться чаще
// - Часть CPU уходит на работу GC вместо обработки запросов
```

**Накладные расходы памяти:**

GC нужны дополнительные структуры данных для отслеживания объектов:

```text
Приложению нужно: 100 MB
Накладные расходы GC и служебные структуры: +20 MB (условный пример)
Всего:            120 MB
```

## Disadvantages (EN)

### 1. Unpredictability

Garbage collection can occur at **unpredictable times** from the application's point of view, causing **short pauses** that may impact responsiveness (e.g., frame drops in UI, latency spikes on servers).

During certain phases, many collectors perform a **Stop-the-World (STW) pause**, where application threads are temporarily halted:

```text
Application running → GC pause (STW) → Application resumes
     ||||||||||||      [pause]           ||||||||||||
     Normal exec        Threads          Normal exec
                         stopped
```

This variability can be problematic for real-time or latency-sensitive systems.

### 2. Overhead

GC introduces **CPU and memory overhead** for scanning, marking, and maintaining metadata, which can affect performance, especially under high load or in near real-time systems.

For example, in a high-throughput server creating many short-lived objects, frequent collections consume CPU time that could otherwise serve requests.

There is also some memory overhead for GC bookkeeping structures (e.g., card tables, mark bits), so total memory used by a GC-based runtime is typically higher than the theoretical minimum required by the live objects.

---

## Резюме

**Garbage Collector:**
- Механизм автоматического управления памятью
- Освобождает память недостижимых (неиспользуемых) объектов
- Работает автоматически, отслеживая достижимость объектов
- Часто использует алгоритмы mark-and-sweep и их вариации (включая поколенческие и копирующие)

**Преимущества:**
- Снижает риск утечек памяти из-за забытого free
- Предотвращает ошибки double-free и use-after-free, связанные с ручным освобождением
- Упрощает разработку

**Недостатки:**
- Непредсказуемые паузы (Stop-the-World) и вариативность задержек
- Накладные расходы CPU и памяти
- Может влиять на производительность, особенно в системах реального времени или при высоких нагрузках

**Лучшие практики:**
- Минимизировать избыточные выделения объектов
- Переиспользовать объекты, когда это оправдано
- Использовать пулы объектов для очень частых выделений, если профилирование это оправдывает
- Мониторить поведение GC и использование памяти в продакшене

## Summary (EN)

**Garbage Collector:**
- An automatic memory management mechanism.
- Reclaims memory from unreachable / unused objects.
- Relies on reachability analysis and algorithms like mark-and-sweep (and generational / copying variants).

**Pros:**
- Reduces memory leaks from forgotten manual deallocation.
- Avoids classic double-free and use-after-free errors from manual `free`/`delete`.
- Simplifies development by removing explicit deallocation.

**Cons:**
- Unpredictable pauses (including Stop-the-World phases) and latency variability.
- CPU and memory overhead for tracking objects and running the collector.
- Potential impact on performance in real-time / high-load systems.

**Best Practices:**
- Minimize excessive object allocations.
- Reuse objects where appropriate.
- Use object pools only when profiling shows real benefit.
- Monitor GC behavior and memory usage in production.

---

## Дополнительные Вопросы (RU)

- Как отличаются реализации сборки мусора между JVM (Java/Kotlin) и другими рантаймами (например, Kotlin/Native)?
- Как вы бы анализировали и настраивали поведение GC в реальных приложениях?
- Какие распространённые проблемы, связанные с GC (например, retention leaks), следует избегать?

## Follow-ups

- How does garbage collection differ between platforms like Java (JVM) and Kotlin/Native or other runtimes?
- How would you reason about GC behavior and tuning in real-world applications?
- What are common GC-related pitfalls (e.g., retention leaks) to avoid?

## Ссылки (RU)

- [[c-garbage-collection]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-garbage-collector-basics--kotlin--medium]]
- [[q-garbage-collector-roots--kotlin--medium]]

## Related Questions

- [[q-garbage-collector-basics--kotlin--medium]]
- [[q-garbage-collector-roots--kotlin--medium]]
