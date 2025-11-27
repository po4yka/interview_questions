---
id: kotlin-015
title: "Suspending vs Blocking / Приостанавливающие vs блокирующие функции"
aliases: ["Suspending vs Blocking", "Приостанавливающие vs блокирующие функции"]

# Classification
topic: kotlin
subtopics: [coroutines]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-kotlin-coroutines-introduction--kotlin--medium, q-suspend-functions-deep-dive--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [blocking, concurrency, coroutines, difficulty/medium, kotlin, suspend]
date created: Friday, October 17th 2025, 9:47:58 pm
date modified: Tuesday, November 25th 2025, 8:53:48 pm
---
# Вопрос (RU)
> В чем разница между приостанавливающими (suspending) и блокирующими (blocking) функциями в Kotlin?

# Question (EN)
> What is the difference between suspending and blocking in Kotlin?

## Ответ (RU)

### Блокирующие (Blocking)

Блокирующая операция удерживает поток занятым до её завершения: пока функция выполняется или "ждёт" (например, через `Thread.sleep()` или синхронный I/O), поток не может выполнять другую работу.

```kotlin
fun main(args: Array<String>) {
    println("Начало выполнения Main")
    threadFunction(1, 200)
    threadFunction(2, 500)
    Thread.sleep(1000)  // Main поток ЗАБЛОКИРОВАН, он просто ждёт
    println("Завершение выполнения Main")
}

fun threadFunction(counter: Int, delay: Long) {
    thread {
        println("Функция ${counter} началась в ${Thread.currentThread().name}")
        Thread.sleep(delay)  // Поток ЭТОЙ нити ЗАБЛОКИРОВАН на время ожидания
        println("Функция ${counter} завершилась в ${Thread.currentThread().name}")
    }
}

// Возможный вывод (порядок строк из разных потоков не гарантирован):
// Начало выполнения Main
// Функция 1 началась в Thread-0
// Функция 2 началась в Thread-1
// Функция 1 завершилась в Thread-0
// Функция 2 завершилась в Thread-1
// Завершение выполнения Main
```

**Проблема**: Главный поток (в примере — `main`) во время `Thread.sleep` ничего не делает, просто ждёт, удерживая за собой поток как ресурс. В Android-приложении такой блокирующий вызов на UI-потоке **заморозит интерфейс**, так как главный поток заблокирован и не может обрабатывать события.

### Приостанавливающие (Suspending)

Приостанавливающая (`suspend`) функция может временно прекратить выполнение корутины ("приостановиться") и возобновиться позже без блокировки потока, если внутри неё используются **неблокирующие приостанавливающие операции** (например, `delay` из `kotlinx.coroutines`). При приостановке корутины поток освобождается и может быть использован другими корутинами.

```kotlin
fun main(args: Array<String>) = runBlocking {
    println("Начало выполнения Main")
    joinAll(
        async { suspendFunction(1, 200) },
        async { suspendFunction(2, 500) },
        async {
            println("Другая задача работает в ${Thread.currentThread().name}")
            delay(100)
        }
    )
    println("Завершение выполнения Main")
}

suspend fun suspendFunction(counter: Int, delay: Long) {
    println("Корутина ${counter} начала работу в ${Thread.currentThread().name}")
    delay(delay)  // Корутина ПРИОСТАНОВЛЕНА (поток может выполнять другие корутины)
    println("Функция ${counter} завершилась в ${Thread.currentThread().name}")
}

// Возможный вывод (для JVM main с runBlocking; диспетчер по умолчанию может отличаться):
// Начало выполнения Main
// Корутина 1 начала работу в main
// Корутина 2 начала работу в main
// Другая задача работает в main
// Корутина 1 завершилась в main
// Корутина 2 завершилась в main
// Завершение выполнения Main
```

Здесь `runBlocking` блокирует вызывающий поток до завершения всех корутин и используется только для примера в обычном `main`. Внутри `runBlocking` такие операции как `delay` не блокируют поток: во время ожидания корутин поток может выполнять другие корутины в рамках того же контекста.

Важно: сам по себе модификатор `suspend` не гарантирует "неблокирующее" поведение и не переключает поток автоматически. Если внутри `suspend`-функции вызвать блокирующий код (например, `Thread.sleep`), поток всё равно будет заблокирован.

**Преимущество**: При использовании корректных `suspend`-API длительные операции могут приостанавливаться без блокировки потока, улучшая масштабируемость и отзывчивость. На Android при правильном использовании (например, `withContext(Dispatchers.IO)` для блокирующего I/O) UI-поток остаётся свободным.

### Ключевые Отличия

| Аспект | Blocking | Suspending |
|--------|----------|------------|
| **Поток** | Заблокирован на время операции | Может быть свободен для другой работы во время приостановки (при неблокирующих `suspend`-операциях) |
| **Выполнение** | Последовательное в рамках конкретного потока (должен ждать) | Конкурентное: множество корутин может чередоваться на меньшем числе потоков |
| **Использование ресурсов** | Удерживает поток как ресурс | Эффективное использование потоков за счёт приостановки |
| **Android UI** | Блокировка UI-потока ведёт к фризам и ANR | При правильном использовании сохраняет отзывчивость UI |
| **Стоимость** | Дорого: нужно много потоков для масштабирования | Дёшево: много корутин поверх меньшего числа потоков |
| **Тип функции** | Обычная функция (может блокировать) | `suspend`-функция (может приостанавливать) |
| **Вызов из** | Откуда угодно | Только из корутины или другой `suspend`-функции (или через `runBlocking`) |

### Визуальное Сравнение

**Blocking:**
```text
Поток: [====Функция A====][====Функция B====]
        ^ Заблокирован      ^ Заблокирован
```

**Suspending:**
```text
Поток: [==A=][=Другое=][==A==][==B=][=Другое=][==B==]
        ^приостановка ^    ^возобновление
```

### Практический Пример

```kotlin
// - Blocking - замораживает UI при выполнении на главном потоке
fun loadDataBlocking() {
    val data = networkCallBlocking()  // Синхронный/network I/O: при вызове на UI-потоке UI ЗАБЛОКИРОВАН
    updateUI(data)
}

// - Suspending - при использовании неблокирующих/suspend API не блокирует поток ожиданием
suspend fun loadDataSuspending() {
    val data = networkCallSuspending()  // Неблокирующая реализация: корутина ПРИОСТАНОВЛЕНА, поток свободен
    updateUI(data)
}

// В ViewModel
fun loadDataSafely() {
    viewModelScope.launch {
        loadDataSuspending()  // При корректной реализации suspend-функций UI не блокируется
    }
}
```

**Краткое содержание**: Blocking-блокирует поток до завершения операции, удерживает поток как ресурс и при выполнении на UI-потоке замораживает интерфейс. Suspending позволяет приостанавливать выполнение корутин без блокировки потока (при использовании неблокирующих `suspend`-операций): во время ожидания поток может выполнять другие корутины, что улучшает отзывчивость и масштабируемость. `Thread.sleep()` — блокирующая операция, `delay()` — приостанавливающая неблокирующая операция. Корутинная модель реализует кооперативную конкуррентность поверх потоков ОС; блокирующий код опирается на прямое удержание потоков. На Android для I/O и длительных операций следует использовать `suspend`-функции с подходящими диспетчерами (например, `Dispatchers.IO`) и избегать блокирующих вызовов на UI-потоке, чтобы избежать ANR.

См. также: [[c-kotlin]], [[c-coroutines]].

---

## Answer (EN)

### Blocking

A blocking operation keeps a thread busy until it completes: while the function is executing or "waiting" (e.g., via `Thread.sleep()` or synchronous I/O), that thread cannot do other work.

```kotlin
fun main(args: Array<String>) {
    println("Main execution started")
    threadFunction(1, 200)
    threadFunction(2, 500)
    Thread.sleep(1000)  // Main thread BLOCKED: just waiting
    println("Main execution stopped")
}

fun threadFunction(counter: Int, delay: Long) {
    thread {
        println("Function ${counter} has started on ${Thread.currentThread().name}")
        Thread.sleep(delay)  // This worker thread is BLOCKED while sleeping
        println("Function ${counter} is finished on ${Thread.currentThread().name}")
    }
}

// Possible output (interleaving from multiple threads is not guaranteed):
// Main execution started
// Function 1 has started on Thread-0
// Function 2 has started on Thread-1
// Function 1 is finished on Thread-0
// Function 2 is finished on Thread-1
// Main execution stopped
```

**Problem**: The main thread (here `main`) during `Thread.sleep` just waits and holds a thread resource. In an Android app, doing such blocking work on the main (UI) thread **would freeze the UI**, because the thread cannot process input, layout, or draw while blocked.

### Suspending

A suspending (`suspend`) function can pause a coroutine while waiting (e.g., for I/O or a timer) and resume later without blocking the thread, as long as it uses **non-blocking suspending primitives** (such as `delay` from `kotlinx.coroutines`). When a coroutine is suspended, the underlying thread is free to run other coroutines.

```kotlin
fun main(args: Array<String>) = runBlocking {
    println("Main execution started")
    joinAll(
        async { suspendFunction(1, 200) },
        async { suspendFunction(2, 500) },
        async {
            println("Other task is working on ${Thread.currentThread().name}")
            delay(100)
        }
    )
    println("Main execution stopped")
}

suspend fun suspendFunction(counter: Int, delay: Long) {
    println("Coroutine ${counter} has started work on ${Thread.currentThread().name}")
    delay(delay)  // Coroutine SUSPENDED (thread may run other coroutines)
    println("Function ${counter} is finished on ${Thread.currentThread().name}")
}

// Possible output (for this JVM main + runBlocking; actual dispatcher/thread may vary):
// Main execution started
// Coroutine 1 has started work on main
// Coroutine 2 has started work on main
// Other task is working on main
// Coroutine 1 is finished on main
// Coroutine 2 is finished on main
// Main execution stopped
```

Here `runBlocking` blocks the calling thread until all coroutines complete, and is used only for a simple `main` example. Inside `runBlocking`, suspending calls like `delay` do not block the thread: while one coroutine is suspended, the thread can execute other coroutines in that context.

Important: the `suspend` modifier by itself does not automatically make code non-blocking or move it off the main thread. If a `suspend` function calls blocking code (e.g., `Thread.sleep()`), the thread will still be blocked.

**Advantage**: With properly implemented suspend APIs, long-running work can wait without blocking a thread, improving scalability and responsiveness. On Android, when used correctly (e.g., wrapping blocking I/O in `withContext(Dispatchers.IO)`), the UI thread remains responsive.

### Key Differences

| Aspect | Blocking | Suspending |
|--------|----------|------------|
| **Thread** | Locked/blocked for the duration of the call | Can be free to do other work while coroutine is suspended (with non-blocking suspend operations) |
| **Execution** | Sequential on a given thread (must wait) | Concurrent: many coroutines can interleave on a smaller thread pool |
| **Resource usage** | Holds a thread resource while waiting | Efficient: many coroutines can share fewer threads |
| **Android UI** | Blocking on main thread freezes UI / risks ANR | When used properly, keeps UI responsive |
| **Cost** | Expensive to scale (many threads) | Cheap to scale (many coroutines on few threads) |
| **Function type** | Regular function (may block) | `suspend` function (can suspend) |
| **Can call from** | Anywhere | Only from a coroutine or another `suspend` function (or via `runBlocking`) |

### Visual Comparison

**Blocking**:
```text
Thread: [====Function A====][====Function B====]
        ^ Blocked          ^ Blocked
```

**Suspending**:
```text
Thread: [==A=][=Other=][==A==][==B=][=Other=][==B==]
        ^suspend  ^    ^resume
```

### Practical Example

```kotlin
// - Blocking - freezes UI when executed on the main thread
fun loadDataBlocking() {
    val data = networkCallBlocking()  // Synchronous/blocking I/O: on main thread this BLOCKS the UI
    updateUI(data)
}

// - Suspending - when using proper suspend/non-blocking APIs, avoids blocking the thread while waiting
suspend fun loadDataSuspending() {
    val data = networkCallSuspending()  // Non-blocking suspend implementation: coroutine SUSPENDED, thread free
    updateUI(data)
}

// In ViewModel
fun loadDataSafely() {
    viewModelScope.launch {
        loadDataSuspending()  // With correctly implemented suspend I/O, UI is not blocked
    }
}
```

**English Summary**: Blocking keeps a thread held until the operation completes; if done on the main/UI thread, it freezes the UI and wastes a valuable resource. Suspending (when using non-blocking suspend primitives) lets coroutines pause without blocking the underlying thread, enabling other work to run and improving scalability and responsiveness. `Thread.sleep()` is blocking; `delay()` is a suspending non-blocking operation. Coroutines provide cooperative concurrency built on top of threads; blocking code relies on directly holding threads. On Android, use suspend functions with appropriate dispatchers (e.g., `Dispatchers.IO`) and avoid blocking calls on the main thread to prevent ANR.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Coroutines Basics - Kotlin](https://kotlinlang.org/docs/coroutines-basics.html)

## Related Questions
- [[q-kotlin-coroutines-introduction--kotlin--medium]]
- [[q-suspend-functions-deep-dive--kotlin--medium]]
- [[q-launch-vs-async-vs-runblocking--kotlin--medium]]
