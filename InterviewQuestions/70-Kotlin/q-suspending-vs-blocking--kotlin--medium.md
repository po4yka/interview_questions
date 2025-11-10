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
related: [c-kotlin, c-coroutines, q-kotlin-coroutines-introduction--kotlin--medium, q-suspend-functions-deep-dive--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-11-09

tags: [blocking, concurrency, coroutines, difficulty/medium, kotlin, suspend]
---
# Вопрос (RU)
> В чем разница между приостанавливающими (suspending) и блокирующими (blocking) функциями в Kotlin?

# Question (EN)
> What is the difference between suspending and blocking in Kotlin?

## Ответ (RU)

### Блокирующие (Blocking)

Функция A должна завершиться перед тем, как продолжится функция B. **Поток заблокирован** для выполнения функции A.

```kotlin
fun main(args: Array<String>) {
    println("Начало выполнения Main")
    threadFunction(1, 200)
    threadFunction(2, 500)
    Thread.sleep(1000)  // Main поток ЗАБЛОКИРОВАН
    println("Завершение выполнения Main")
}

fun threadFunction(counter: Int, delay: Long) {
    thread {
        println("Функция ${counter} началась в ${Thread.currentThread().name}")
        Thread.sleep(delay)  // Поток ЗАБЛОКИРОВАН
        println("Функция ${counter} завершилась в ${Thread.currentThread().name}")
    }
}

// Вывод:
// Начало выполнения Main
// Функция 1 началась в Thread-0
// Функция 2 началась в Thread-1
// Функция 1 завершилась в Thread-0
// Функция 2 завершилась в Thread-1
// Завершение выполнения Main
```

**Проблема**: Главный поток (в примере) ничего не делает, просто ждёт, удерживая за собой поток как ресурс. В Android-приложении такой блокирующий вызов на UI-потоке **заморозит интерфейс**, так как главный поток заблокирован и не может обрабатывать события.

### Приостанавливающие (Suspending)

Функция A (корутина) может быть приостановлена, пока ожидает результат, и возобновлена позже. При приостановке корутины **поток не блокируется** этой операцией и может быть использован другими корутинами.

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
    delay(delay)  // Корутина ПРИОСТАНОВЛЕНА (поток освобождён для других задач)
    println("Функция ${counter} завершилась в ${Thread.currentThread().name}")
}

// Вывод (с учетом использования runBlocking в JVM main):
// Начало выполнения Main
// Корутина 1 начала работу в main
// Корутина 2 начала работу в main
// Другая задача работает в main
// Корутина 1 завершилась в main
// Корутина 2 завершилась в main
// Завершение выполнения Main
```

Здесь `runBlocking` блокирует вызывающий поток до завершения всех корутин и используется только для примера в обычном `main`. Внутри `runBlocking` функции `delay` и другие приостанавливающие вызовы не блокируют поток: во время ожидания поток может выполнять другие корутины.

**Преимущество**: При использовании `suspend`-функций и корутин длительные операции могут приостанавливаться без блокировки потока, улучшая масштабируемость и отзывчивость. На Android при правильном использовании (например, `withContext(Dispatchers.IO)` для I/O) UI-поток остаётся свободным.

### Ключевые Отличия

| Аспект | Blocking | Suspending |
|--------|----------|------------|
| **Поток** | Заблокирован на время операции | Свободен для другой работы во время приостановки |
| **Выполнение** | Последовательное в рамках конкретного потока (должен ждать) | Конкурентное: корутины могут чередоваться на тех же потоках |
| **Использование ресурсов** | Удерживает поток как ресурс | Эффективное использование потоков за счёт приостановки |
| **Android UI** | Блокировка UI-потока ведёт к фризам и ANR | При правильном использовании сохраняет отзывчивость UI |
| **Стоимость** | Дорого: много потоков для масштабирования | Дёшево: много корутин поверх меньшего числа потоков |
| **Тип функции** | Обычная функция (может блокировать) | `suspend`-функция (может приостанавливать) |
| **Вызов из** | Откуда угодно | Только из корутины или другой `suspend`-функции (или через `runBlocking`) |

### Визуальное Сравнение

**Blocking:**
```
Поток: [====Функция A====][====Функция B====]
        ^ Заблокирован      ^ Заблокирован
```

**Suspending:**
```
Поток: [==A=][=Другое=][==A==][==B=][=Другое=][==B==]
        ^приостановка ^    ^возобновление
```

### Практический Пример

```kotlin
// - Blocking - замораживает UI при выполнении на главном потоке
fun loadData() {
    val data = networkCall()  // Если это блокирующий вызов на UI-потоке, UI поток ЗАБЛОКИРОВАН
    updateUI(data)
}

// - Suspending - позволяет не блокировать UI при использовании подходящих диспетчеров/неблокирующих API
suspend fun loadData() {
    val data = networkCall()  // При использовании неблокирующего/suspend API корутина ПРИОСТАНОВЛЕНА, поток свободен
    updateUI(data)
}

// В ViewModel
fun loadDataSafely() {
    viewModelScope.launch {
        loadData()  // При корректной реализации suspend-функций UI не блокируется
    }
}
```

**Краткое содержание**: Blocking блокирует поток до завершения операции, удерживает поток как ресурс и при выполнении на UI-потоке замораживает интерфейс. Suspending позволяет приостанавливать выполнение без блокировки потока: во время ожидания поток может выполнять другие корутины, что улучшает отзывчивость и масштабируемость. `Thread.sleep()` — блокирующая операция, `delay()` — приостанавливающая. Корутинная модель реализует кооперативную конкуррентность поверх потоков ОС; блокирующий код опирается на прямое удержание потоков. На Android для I/O и длительных операций следует использовать `suspend`-функции и подходящие диспетчеры (например, `Dispatchers.IO`), чтобы избежать ANR.

См. также: [[c-kotlin]], [[c-coroutines]].

---

## Answer (EN)

### Blocking

Function A must complete before Function B continues on the same thread. **The thread is blocked** while Function A executes.

```kotlin
fun main(args: Array<String>) {
    println("Main execution started")
    threadFunction(1, 200)
    threadFunction(2, 500)
    Thread.sleep(1000)  // Main thread BLOCKED
    println("Main execution stopped")
}

fun threadFunction(counter: Int, delay: Long) {
    thread {
        println("Function ${counter} has started on ${Thread.currentThread().name}")
        Thread.sleep(delay)  // This thread is BLOCKED
        println("Function ${counter} is finished on ${Thread.currentThread().name}")
    }
}

// Output:
// Main execution started
// Function 1 has started on Thread-0
// Function 2 has started on Thread-1
// Function 1 is finished on Thread-0
// Function 2 is finished on Thread-1
// Main execution stopped
```

**Problem**: The main thread (in this example) just waits and holds on to a thread resource. In an Android app, doing such blocking work on the main (UI) thread **would freeze the UI**, because the thread cannot process input, layout, or draw while blocked.

### Suspending

Function A (a coroutine) can be suspended while waiting (e.g., for I/O or a timer) and resumed later. When a coroutine is suspended, **the underlying thread is not blocked by that operation** and can run other coroutines instead.

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
    delay(delay)  // Coroutine SUSPENDED (thread released for other work)
    println("Function ${counter} is finished on ${Thread.currentThread().name}")
}

// Output (for this JVM main + runBlocking example):
// Main execution started
// Coroutine 1 has started work on main
// Coroutine 2 has started work on main
// Other task is working on main
// Coroutine 1 is finished on main
// Coroutine 2 is finished on main
// Main execution stopped
```

Here `runBlocking` blocks the calling thread until all coroutines complete, and is used only for simple `main` examples. Inside `runBlocking`, suspending calls like `delay` do not block the thread: while one coroutine is suspended, the thread can execute other coroutines.

**Advantage**: With suspend functions and coroutines, long-running work can wait without blocking a thread, improving scalability and responsiveness. On Android, when used correctly (e.g., with `Dispatchers.IO` for blocking I/O), the UI thread remains responsive.

### Key Differences

| Aspect | Blocking | Suspending |
|--------|----------|------------|
| **Thread** | Locked/blocked for the duration of the call | Free to do other work while coroutine is suspended |
| **Execution** | Sequential on a given thread (must wait) | Concurrent: coroutines can interleave on the same pool of threads |
| **Resource usage** | Holds a thread resource while waiting | Efficient: many coroutines can share fewer threads |
| **Android UI** | Blocking on main thread freezes UI / risks ANR | When used properly, keeps UI responsive |
| **Cost** | Expensive to scale (many threads) | Cheap to scale (many coroutines on few threads) |
| **Function type** | Regular function (may block) | `suspend` function (can suspend) |
| **Can call from** | Anywhere | Only from a coroutine or another `suspend` function (or via `runBlocking`) |

### Visual Comparison

**Blocking**:
```
Thread: [====Function A====][====Function B====]
        ^ Blocked          ^ Blocked
```

**Suspending**:
```
Thread: [==A=][=Other=][==A==][==B=][=Other=][==B==]
        ^suspend  ^    ^resume
```

### Practical Example

```kotlin
// - Blocking - freezes UI when executed on the main thread
fun loadData() {
    val data = networkCall()  // If this is blocking I/O on the main thread, UI thread is BLOCKED
    updateUI(data)
}

// - Suspending - allows avoiding UI blocking when using proper dispatchers/non-blocking APIs
suspend fun loadData() {
    val data = networkCall()  // With a proper suspend/non-blocking implementation, coroutine is SUSPENDED, thread is free
    updateUI(data)
}

// In ViewModel
fun loadDataSafely() {
    viewModelScope.launch {
        loadData()  // With correctly implemented suspend I/O, UI is never blocked
    }
}
```

**English Summary**: Blocking keeps the thread busy (held) until the operation completes; if done on the main/UI thread, it freezes the UI and wastes a valuable thread resource. Suspending lets coroutines pause without blocking the underlying thread, enabling other work to run and improving scalability and responsiveness. `Thread.sleep()` is blocking; `delay()` is suspending. Coroutines provide cooperative concurrency built on top of threads; blocking code relies on directly holding threads. On Android, use suspend functions with appropriate dispatchers (e.g., `Dispatchers.IO`) for I/O and long operations to avoid ANR.

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
