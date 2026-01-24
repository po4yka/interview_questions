---
anki_cards:
- slug: q-suspending-vs-blocking--kotlin--medium-0-en
  language: en
  anki_id: 1768326287355
  synced_at: '2026-01-23T17:03:51.184616'
- slug: q-suspending-vs-blocking--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326287382
  synced_at: '2026-01-23T17:03:51.186347'
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
| **`Thread`** | Locked/blocked for the duration of the call | Can be free to do other work while coroutine is suspended (with non-blocking suspend operations) |
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
