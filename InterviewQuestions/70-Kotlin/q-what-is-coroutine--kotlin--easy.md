---
anki_cards:
- slug: q-what-is-coroutine--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-what-is-coroutine--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
## Answer (EN)

A **coroutine** is an instance of a **suspendable computation**. It is conceptually similar to a thread in that it runs a block of code that can execute concurrently (more precisely, asynchronously/concurrently) with the rest of the program. However, a coroutine is not bound to any particular thread. It may suspend its execution in one thread and resume in another.

See also: [[c-kotlin]], [[c-coroutines]].

### Key Concepts

1.  **Suspendable**: A coroutine can be suspended (paused) at certain points without blocking the underlying thread. This is the core feature that makes them efficient.
2.  **Lightweight**: You can run thousands or even millions of coroutines on top of a small pool of threads, whereas threads are expensive to create and maintain.
3.  **Structured Concurrency**: Coroutines are launched within a `CoroutineScope`, which allows for proper management of their lifecycle, cancellation, and error propagation.

### Coroutine vs. Thread

| Feature | `Coroutine` | `Thread` |
| :--- | :--- | :--- |
| **Resource Cost** | Very cheap (lightweight) | Expensive (heavyweight) |
| **Blocking** | Non-blocking style (uses suspension instead of blocking for async APIs/operations) | Often blocking (operations block the thread) |
| **Management** | Scheduled and managed by the coroutine dispatcher/runtime on top of OS threads | Managed by the Operating System |
| **Creation** | Fast | Slow |
| **`Context` Switching**| Fast (between coroutines in-process) | Slow (OS-level) |

### Example

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking { // Creates a CoroutineScope and blocks the current thread until all coroutines inside complete
    println("Main program starts: ${Thread.currentThread().name}")

    launch { // Launches a new coroutine in the same scope
        println("Fake work starts: ${Thread.currentThread().name}")
        delay(1000) // Suspends this coroutine for 1 second without blocking the thread
        println("Fake work finished: ${Thread.currentThread().name}")
    }

    println("Main program continues: ${Thread.currentThread().name}")
    delay(2000) // Suspends the main coroutine for 2 seconds, giving time for the child coroutine to complete
    println("Main program ends: ${Thread.currentThread().name}")
}
```

**Output:**
```text
Main program starts: main
Main program continues: main
Fake work starts: main
Fake work finished: main
Main program ends: main
```

In this example, `delay()` is a `suspend` function. When the coroutine calls `delay()`, it is suspended, but the `main` thread is not blocked by that coroutine and can be used to run other coroutines or work.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия корутин от потоков в Java?
- Когда на практике вы бы использовали корутины?
- Какие распространенные ошибки при работе с корутинами следует избегать?

## Ссылки (RU)

- [Документация по Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html)

## Связанные Вопросы (RU)

- [[q-suspend-functions-basics--kotlin--easy]]
- [[q-coroutine-scope-basics--kotlin--easy]]

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

## Related Questions

- [[q-suspend-functions-basics--kotlin--easy]]
- [[q-coroutine-scope-basics--kotlin--easy]]
