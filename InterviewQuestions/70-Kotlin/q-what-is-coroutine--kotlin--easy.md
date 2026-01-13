---
---
---\
id: kotlin-072
title: "What is a Coroutine? Basic Concepts / Что такое корутина? Основные концепции"
aliases: ["What is a Coroutine? Basic Concepts", "Что такое корутина? Основные концепции"]
topic: kotlin
subtopics: [concurrency, coroutines]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-coroutine-scope-basics--kotlin--easy, q-suspend-functions-basics--kotlin--easy]
created: 2025-10-12
updated: 2025-11-11
tags: [async, concurrency, coroutines, difficulty/easy, kotlin]

---\
# Вопрос (RU)
> Что такое корутина в Kotlin? Объясните её основные концепции и чем она отличается от потока.

# Question (EN)
> What is a coroutine in Kotlin? Explain its basic concepts and how it differs from a thread.

## Ответ (RU)

**Корутина** (или сопрограмма) — это экземпляр **приостанавливаемого вычисления**. Концептуально она похожа на поток, так как выполняет блок кода конкурентно (точнее — асинхронно/конкурентно) с остальной частью программы. Однако корутина не привязана к какому-либо конкретному потоку. Она может приостановить свое выполнение в одном потоке и возобновить в другом.

См. также: [[c-kotlin]], [[c-coroutines]].

### Ключевые Концепции

1.  **Приостанавливаемость (Suspendable)**: Корутины можно приостанавливать в определенных точках, не блокируя при этом поток, в котором они выполняются. Это ключевая особенность, делающая их эффективными.
2.  **Легковесность**: Вы можете запустить тысячи или даже миллионы корутин поверх небольшого числа потоков, в то время как потоки дороги в создании и поддержании.
3.  **Структурированная конкуррентность (Structured Concurrency)**: Корутины запускаются в пределах `CoroutineScope`, что позволяет управлять их жизненным циклом, отменой и обработкой ошибок.

### Корутина vs. Поток

| Характеристика | Корутина | Поток |
| :--- | :--- | :--- |
| **Затраты ресурсов**| Очень дешевые (легковесные) | Дорогие (тяжеловесные) |
| **Блокировка** | Неблокирующий стиль (используют приостановку вместо блокировки для асинхронных операций) | Часто блокирующие (операции блокируют поток) |
| **Управление** | Планируются и управляются диспетчером корутин (библиотекой/рантаймом поверх потоков ОС) | Управляются операционной системой |
| **Создание** | Быстрое | Медленное |
| **Переключение контекста**| Быстрое (между корутинами внутри процесса) | Медленное (на уровне ОС) |

### Пример

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking { // Создает CoroutineScope и блокирует текущий поток до завершения всех корутин внутри
    println("Основная программа стартует: ${Thread.currentThread().name}")

    launch { // Запускает новую корутину в том же scope
        println("Фейковая работа стартует: ${Thread.currentThread().name}")
        delay(1000) // Приостанавливает корутину на 1 секунду, не блокируя поток
        println("Фейковая работа завершена: ${Thread.currentThread().name}")
    }

    println("Основная программа продолжается: ${Thread.currentThread().name}")
    delay(2000) // Приостанавливает корутину main на 2 секунды, давая времени дочерней корутине завершиться
    println("Основная программа завершается: ${Thread.currentThread().name}")
}
```

**Вывод:**
```text
Основная программа стартует: main
Основная программа продолжается: main
Фейковая работа стартует: main
Фейковая работа завершена: main
Основная программа завершается: main
```

В этом примере `delay()` — это `suspend`-функция. Когда корутина вызывает `delay()`, она приостанавливается, но поток `main` не блокируется этой корутиной и может быть использован для выполнения других задач или корутин.

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
