---
id: 20251005-235010
title: "Suspending vs Blocking / Приостанавливающие vs блокирующие функции"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, suspend, blocking, concurrency, threads]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository - Kotlin Batch 2

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-coroutines-introduction--kotlin--medium, q-suspend-functions-deep-dive--kotlin--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, coroutines, suspend, blocking, concurrency, difficulty/medium]
---
## Question (EN)
> What is the difference between suspending and blocking in Kotlin?
## Вопрос (RU)
> В чем разница между приостанавливающими (suspending) и блокирующими (blocking) функциями в Kotlin?

---

## Answer (EN)

### Blocking

Function A must complete before Function B continues. **Thread is locked** for Function A to complete its execution.

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
        Thread.sleep(delay)  // Thread BLOCKED
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

**Problem**: Main thread does nothing, just waiting. It occupies CPU with unnecessary waiting. **In Android app this would freeze the UI** as main thread is blocked.

### Suspending

Function A can be suspended while Function B executes. Function A can be resumed later. **Thread is NOT locked** by Function A.

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
    delay(delay)  // Coroutine SUSPENDED (not blocked)
    println("Function ${counter} is finished on ${Thread.currentThread().name}")
}

// Output:
// Main execution started
// Coroutine 1 has started work on main
// Coroutine 2 has started work on main
// Other task is working on main
// Coroutine 1 is finished on main
// Coroutine 2 is finished on main
// Main execution stopped
```

**Advantage**: While coroutines are suspended, main thread can execute other tasks. **Main method is NOT blocked** so it can execute other work.

### Key Differences

| Aspect | Blocking | Suspending |
|--------|----------|------------|
| **Thread** | Locked/Blocked | Free to do other work |
| **Execution** | Sequential (must wait) | Concurrent (can interleave) |
| **Resource usage** | Wastes thread time | Efficient thread usage |
| **Android UI** | Freezes UI | Keeps UI responsive |
| **Cost** | Expensive (more threads) | Cheap (fewer threads) |
| **Function type** | Regular function | `suspend` function |
| **Can call from** | Anywhere | Only from coroutine or suspend function |

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
// ❌ Blocking - freezes UI
fun loadData() {
    val data = networkCall()  // UI thread BLOCKED
    updateUI(data)
}

// ✅ Suspending - UI stays responsive
suspend fun loadData() {
    val data = networkCall()  // Coroutine SUSPENDED, UI thread FREE
    updateUI(data)
}

// In ViewModel
fun loadDataSafely() {
    viewModelScope.launch {
        loadData()  // UI never blocked
    }
}
```

**English Summary**: Blocking locks the thread until completion, wasting resources and freezing UI in Android. Suspending releases the thread when waiting, allowing other work, keeping UI responsive. Blocking uses Thread.sleep(), suspending uses delay(). Suspending is cooperative multitasking (coroutines), blocking is thread-based. In Android, always use suspend functions for I/O and long operations to avoid ANR.

## Ответ (RU)

### Блокирующие (Blocking)

Функция A должна завершиться перед тем как продолжится функция B. **Поток заблокирован** для выполнения функции A.

**Проблема**: Главный поток ничего не делает, просто ждет. Занимает CPU ненужным ожиданием. **В Android приложении это заморозит UI**, так как главный поток заблокирован.

### Приостанавливающие (Suspending)

Функция A может быть приостановлена пока выполняется функция B. Функция A может быть возобновлена позже. **Поток НЕ заблокирован** функцией A.

**Преимущество**: Пока корутины приостановлены, главный поток может выполнять другие задачи. **Главный поток НЕ заблокирован**.

### Ключевые отличия

| Аспект | Blocking | Suspending |
|--------|----------|------------|
| **Поток** | Заблокирован | Свободен для другой работы |
| **Выполнение** | Последовательное | Параллельное |
| **Использование ресурсов** | Тратит время потока | Эффективное использование |
| **Android UI** | Замораживает UI | Сохраняет отзывчивость |
| **Тип функции** | Обычная функция | `suspend` функция |

**Краткое содержание**: Блокирующие функции блокируют поток до завершения, тратят ресурсы и замораживают UI в Android. Приостанавливающие функции освобождают поток при ожидании, позволяя другой работе, сохраняя отзывчивость UI. Блокирующие используют Thread.sleep(), приостанавливающие используют delay(). В Android всегда используйте suspend функции для I/O и длительных операций чтобы избежать ANR.

---

## References
- [Coroutines Basics - Kotlin](https://kotlinlang.org/docs/coroutines-basics.html)

## Related Questions
- [[q-kotlin-coroutines-introduction--kotlin--medium]]
- [[q-suspend-functions-deep-dive--kotlin--medium]]
- [[q-launch-vs-async-vs-runblocking--kotlin--medium]]
