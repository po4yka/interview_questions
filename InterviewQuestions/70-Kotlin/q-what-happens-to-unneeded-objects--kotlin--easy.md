---\
id: lang-050
title: "What Happens To Unneeded Objects / Что происходит с ненужными объектами"
aliases: [What Happens To Unneeded Objects, Что происходит с ненужными объектами]
topic: kotlin
subtopics: [jvm, memory-management]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-garbage-collection, c-kotlin]
created: 2025-10-15
updated: 2025-11-09
tags: [automatic-memory, difficulty/easy, garbage-collection, jvm, kotlin, memory-management]

---\
# Вопрос (RU)

> Что происходит с объектами, которые больше не нужны?

# Question (EN)

> What happens to objects that are no longer needed?

## Ответ (RU)

Объекты, к которым больше нет достижимых (strong) ссылок из «живых» корней (стек потока, статические поля, ссылки из работающих потоков и т.п.), считаются мусором (кандидатами на сборку). Они становятся доступными для сборщика мусора JVM, который в некоторый момент времени освобождает занимаемую ими память и делает её доступной для последующих выделений. Этот процесс:

1. Происходит автоматически под управлением JVM (автоматическое управление памятью, см. [[c-garbage-collection]] и [[c-memory-management]]).
2. Не требует и не допускает явного `delete` со стороны разработчика.
3. Носит недетерминированный характер: нельзя гарантировать точный момент сборки.

Упрощённо это выглядит так:

1. Объект становится недостижимым (нет сильных ссылок от GC roots).
2. Сборщик мусора помечает его как мусор.
3. Позже GC освобождает память.
4. Освобождённая память используется для новых выделений.

### Пример (Kotlin)

```kotlin
fun example() {
    val user = User("John")  // Объект создан и доступен через 'user'

    println(user.name)

    // Функция завершается → 'user' выходит из области видимости.
    // Если больше нет других ссылок на этот экземпляр User,
    // он становится кандидатом на сборку мусора.
    // Фактический запуск GC может произойти позже и не гарантирован здесь.
}
```

### Автоматическое Управление Памятью

```kotlin
fun createManyObjects() {
    repeat(1000) {
        val temp = Data()
        // После каждой итерации, если 'temp' нигде не сохраняется,
        // соответствующий объект Data становится недостижимым и пригодным для GC.
    }
    // Нет необходимости и возможности явно удалять эти объекты.
}
```

### Сравнение С C/C++

- В Java/Kotlin на JVM память недостижимых объектов освобождается автоматически сборщиком мусора.
- В C/C++ динамически выделенную память обычно нужно освобождать вручную.

```cpp
Data* data = new Data();
// ... используем data

delete data;  // Требуется явное освобождение, иначе возможна утечка памяти.
```

```kotlin
val data = Data()
// Когда 'data' и другие ссылки исчезают,
// объект становится кандидатом на сборку мусора;
// JVM сама решает, когда фактически освободить память.
```

### Когда Объект Становится Кандидатом На Сборку

```kotlin
class Example {
    fun demo() {
        var obj: Data? = Data()  // Объект создан

        // 'obj' достижим → не собирается

        obj = null  // Если больше нет других ссылок...

        // ...объект становится кандидатом на сборку мусора.
        // GC может освободить память позже; немедленного сбора не гарантируется.
    }
}
```

### Фоновая Работа GC (упрощённо)

```kotlin
// Код разработчика:
fun processData() {
    val temp = LargeData()
    // Используем temp
}  // temp выходит из области видимости

// Концептуально:
// 1. GC периодически или при нехватке памяти запускается.
// 2. Находит объекты, недостижимые из GC roots.
// 3. Освобождает память.
// 4. Делает её доступной для новых выделений.
// Всё это происходит автоматически; разработчик не управляет точным моментом.
```

### Плюсы И Особенности

- Нет ручных `malloc/free` или `new/delete`.
- Меньше типичных ошибок ручного управления памятью (double free, use-after-free).
- Утечки памяти всё ещё возможны, если «держать» ненужные ссылки (GC собирает только недостижимые объекты).
- Разработчик концентрируется на логике, а не на низкоуровневом управлении памятью.

### Как Это Работает На Высоком Уровне

1. Приложение создаёт объекты.
2. GC отслеживает достижимость объектов.
3. Когда GC решает запуститься (по эвристикам, порогам поколений, давлению по памяти):
   - Может происходить краткая остановка приложения (Stop-The-World) в зависимости от алгоритма GC.
   - Определяются недостижимые объекты.
   - Их память освобождается.
4. Приложение продолжает выполнение.

### Пример С System.gc()

```kotlin
fun main() {
    println("Creating objects...")

    repeat(1_000_000) {
        val data = ByteArray(1024)  // 1KB; после итерации пригоден для GC, если не сохранён
    }

    println("Objects created")
    println("Requesting GC...")

    // Это лишь подсказка JVM; GC может запуститься, а может и нет немедленно.
    System.gc()

    println("GC requested (фактический сбор — на усмотрение JVM)")
}
```

Итого: ненужные объекты (недостижимые) на JVM автоматически собираются сборщиком мусора; их память освобождается и переиспользуется, а время сборки недетерминировано.

## Answer (EN)

Objects that are no longer reachable from any live roots (stack, static fields, etc.) are considered garbage (eligible for collection). The garbage collector (GC) may then reclaim the memory they occupy and make it available for future allocations. This is automatic, managed by the JVM, and does not require explicit deletion by the developer; the exact time of collection is non-deterministic.

**Process (Conceptual):**

1. Object becomes unreachable (no strong references from GC roots).
2. Garbage collector identifies it as garbage (eligible for collection).
3. GC reclaims its memory at some later point.
4. Freed memory is reused for new allocations.
5. No manual `delete`-style intervention is available or required.

**Example:**

```kotlin
fun example() {
    val user = User("John")  // Object created and referenced by 'user'

    println(user.name)

    // Function ends → 'user' goes out of scope.
    // If there are no other references to this User instance,
    // it becomes eligible for garbage collection.
    // Actual GC may happen later and is not guaranteed immediately here.
}
```

**Automatic Memory Management:**

```kotlin
fun createManyObjects() {
    repeat(1000) {
        val temp = Data()
        // After each iteration, if 'temp' is not stored anywhere else,
        // that Data instance becomes unreachable and eligible for GC.
    }
    // No need and no way to manually delete these objects.
}
```

**Kotlin/Java vs C/C++:**

- On the JVM (Java, Kotlin on JVM), memory for unreachable objects is reclaimed automatically by the GC.
- In C/C++, dynamically allocated objects must usually be freed manually.

**C++ (Manual):**
```cpp
Data* data = new Data();
// ... use data

delete data;  // Manual cleanup required; forgetting this → memory leak.
```

**Kotlin on JVM (Automatic GC):**
```kotlin
val data = Data()
// When 'data' and any other references to this instance are gone,
// it becomes eligible for GC; the JVM decides when to actually reclaim it.
```

**When Objects Are Collected (Eligibility):**

```kotlin
class Example {
    fun demo() {
        var obj: Data? = Data()  // Object created

        // 'obj' is reachable → not eligible for GC

        obj = null  // If there are no other references to this instance...

        // ...the object becomes eligible for garbage collection.
        // GC may reclaim it later; this is not immediate or guaranteed here.
    }
}
```

**Background Process (Simplified `View`):**

```kotlin
// Developer code:
fun processData() {
    val temp = LargeData()
    // Use temp
}  // 'temp' goes out of scope

// Conceptually:
// 1. GC runs periodically or under memory pressure (implementation-dependent).
// 2. Finds objects that are no longer reachable from GC roots.
// 3. Reclaims their memory.
// 4. Frees it for future allocations.
// All done automatically; timing is not controlled directly by the developer.
```

**Benefits (and Caveats):**

- No manual `malloc/free` or `new/delete`.
- Fewer typical manual-memory bugs (double free, use-after-free).
- But memory leaks are still possible if you keep references to objects longer than needed
  (GC only collects unreachable objects).
- Developer focuses more on logic than low-level memory management.

**How It Works (High Level):**

```text
1. Application creates objects.
2. GC tracks object reachability (not via explicit monitoring of each object by user code).
3. When GC decides to run (e.g., based on heuristics, generation thresholds, or memory pressure):
   - It may briefly pause application threads (Stop-The-World phases) depending on GC algorithm.
   - Identifies unreachable objects.
   - Reclaims their memory.
4. Application continues execution.
```

**Example with System.gc():**

```kotlin
fun main() {
    println("Creating objects...")

    repeat(1_000_000) {
        val data = ByteArray(1024)  // 1KB each; eligible for GC after each iteration if not retained
    }

    println("Objects created")
    println("Requesting GC...")

    // This is only a hint to the JVM; GC may or may not run immediately.
    System.gc()

    println("GC requested (actual memory reclamation is up to the JVM)")
}
```

**Summary:**

Unneeded objects (no longer reachable) on the JVM:
- Are considered garbage (eligible for collection).
- May have their memory automatically reclaimed by the garbage collector.
- The freed memory is reused for new allocations.
- Manual deletion is not available; only reachability controls lifetime.
- The collection process is automatic and non-deterministic.

This is how automatic memory management works in Kotlin/Java on the JVM.

---

## Дополнительные Вопросы (RU)

- Как могут происходить утечки памяти при наличии сборщика мусора?
- Как достижимость объектов (strong/weak/soft ссылки) влияет на поведение GC?
- Как паузы GC могут влиять на производительность приложения?

## Follow-ups

- How do memory leaks still occur with a garbage collector?
- How does object reachability (strong/weak/soft references) affect GC behavior?
- What impact can GC pauses have on application performance?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-suspend-function-return-type-after-compilation--kotlin--hard]]
## Related Questions

- [[q-suspend-function-return-type-after-compilation--kotlin--hard]]
