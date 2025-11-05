---
id: kotlin-072
title: "What is a Coroutine? Basic Concepts / Что такое корутина? Основные концепции"
aliases: ["What is a Coroutine? Basic Concepts, Что такое корутина? Основные концепции"]

# Classification
topic: kotlin
subtopics: [async, concurrency, coroutines]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-coroutine-scope-basics--kotlin--easy, q-suspend-functions-basics--kotlin--easy]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [async, concurrency, coroutines, difficulty/easy, kotlin]
date created: Saturday, November 1st 2025, 1:01:33 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# Question (EN)
> What is a coroutine in Kotlin? Explain its basic concepts and how it differs from a thread.

# Вопрос (RU)
> Что такое корутина в Kotlin? Объясните её основные концепции и чем она отличается от потока.

---

## Answer (EN)

A **coroutine** is an instance of **suspendable computation**. It is conceptually similar to a thread, in that it takes a block of code to run that works concurrently with the rest of the code. However, a coroutine is not bound to any particular thread. It may suspend its execution in one thread and resume in another one.

### Key Concepts

1.  **Suspendable**: A coroutine can be suspended (paused) at certain points without blocking the underlying thread. This is the core feature that makes them so efficient.
2.  **Lightweight**: You can run thousands or even millions of coroutines on a single thread, whereas threads are expensive to create and maintain.
3.  **Structured Concurrency**: Coroutines are launched within a `CoroutineScope`, which allows for better management of their lifecycle, cancellation, and error handling.

### Coroutine vs. Thread

| Feature | Coroutine | Thread |
| :--- | :--- | :--- |
| **Resource Cost** | Very cheap (lightweight) | Expensive (heavyweight) |
| **Blocking** | Non-blocking (suspends) | Blocking |
| **Management** | Managed by the Kotlin runtime | Managed by the Operating System |
| **Creation** | Fast | Slow |
| **Context Switching**| Fast (in-process) | Slow (OS-level) |

### Example

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking { // Creates a CoroutineScope
    println("Main program starts: ${Thread.currentThread().name}")

    launch { // Launches a new coroutine
        println("Fake work starts: ${Thread.currentThread().name}")
        delay(1000) // Suspends the coroutine for 1 second
        println("Fake work finished: ${Thread.currentThread().name}")
    }

    println("Main program continues: ${Thread.currentThread().name}")
    delay(2000) // Wait for the coroutine to finish
    println("Main program ends: ${Thread.currentThread().name}")
}
```

**Output:**
```
Main program starts: main
Main program continues: main
Fake work starts: main
Fake work finished: main
Main program ends: main
```

In this example, `delay()` is a `suspend` function. When the coroutine calls `delay()`, it is suspended, but the `main` thread is not blocked and can continue its work.

---

## Ответ (RU)

**Корутина** (или сопрограмма) — это экземпляр **приостанавливаемого вычисления**. Концептуально она похожа на поток, так как выполняет блок кода параллельно с остальной частью программы. Однако корутина не привязана к какому-либо конкретному потоку. Она может приостановить свое выполнение в одном потоке и возобновить в другом.

### Ключевые Концепции

1.  **Приостанавливаемость (Suspendable)**: Корутину можно приостановить в определенных точках, не блокируя при этом основной поток. Это ключевая особенность, делающая их такими эффективными.
2.  **Легковесность**: Вы можете запустить тысячи или даже миллионы корутин в одном потоке, в то время как потоки дороги в создании и поддержании.
3.  **Структурированный параллелизм (Structured Concurrency)**: Корутины запускаются в пределах `CoroutineScope`, что позволяет лучше управлять их жизненным циклом, отменой и обработкой ошибок.

### Корутина vs. Поток

| Характеристика | Корутина | Поток |
| :--- | :--- | :--- |
| **Затраты ресурсов**| Очень дешевые (легковесные) | Дорогие (тяжеловесные) |
| **Блокировка** | Неблокирующие (приостанавливаются)| Блокирующие |
| **Управление** | Управляются средой выполнения Kotlin | Управляются операционной системой |
| **Создание** | Быстрое | Медленное |
| **Переключение контекста**| Быстрое (внутри процесса) | Медленное (на уровне ОС) |

### Пример

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking { // Создает CoroutineScope
    println("Основная программа стартует: ${Thread.currentThread().name}")

    launch { // Запускает новую корутину
        println("Фейковая работа стартует: ${Thread.currentThread().name}")
        delay(1000) // Приостанавливает корутину на 1 секунду
        println("Фейковая работа завершена: ${Thread.currentThread().name}")
    }

    println("Основная программа продолжается: ${Thread.currentThread().name}")
    delay(2000) // Ждем завершения корутины
    println("Основная программа завершается: ${Thread.currentThread().name}")
}
```

**Вывод:**
```
Основная программа стартует: main
Основная программа продолжается: main
Фейковая работа стартует: main
Фейковая работа завершена: main
Основная программа завершается: main
```

В этом примере `delay()` — это `suspend` функция. Когда корутина вызывает `delay()`, она приостанавливается, но поток `main` не блокируется и может продолжать свою работу.

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Related Questions

- [[q-suspend-functions-basics--kotlin--easy]]
- [[q-coroutine-scope-basics--kotlin--easy]]
