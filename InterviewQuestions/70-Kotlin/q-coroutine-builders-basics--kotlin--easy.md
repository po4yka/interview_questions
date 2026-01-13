---
anki_cards:
- slug: q-coroutine-builders-basics--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-coroutine-builders-basics--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: kotlin-102
title: "Coroutine Builders: launch, async, runBlocking / Билдеры корутин: launch, async, runBlocking"
aliases: ["Coroutine Builders: launch, async, runBlocking", "Билдеры корутин: launch, async, runBlocking"]

# Classification
topic: kotlin
subtopics: [coroutines, patterns]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140029

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin-coroutines-basics, q-data-class-detailed--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [coroutines, difficulty/easy, kotlin]
---\
# Вопрос (RU)
> Базовая тема корутин Kotlin 140029 (билдеры `launch`, `async`, `runBlocking`)

---

# Question (EN)
> Kotlin Coroutines basic topic 140029 (builders `launch`, `async`, `runBlocking`)

## Ответ (RU)

`Coroutine` builders - это функции, создающие и запускающие корутины в заданном `CoroutineScope`. Основные builders: `launch`, `async` и `runBlocking`.

### Launch
Запускает новую корутину и возвращает `Job`. Предназначен для задач с побочными эффектами, когда результат не требуется напрямую.
```kotlin
fun main() = runBlocking {
    val job = launch {
        delay(1000)
        println("World!")
    }
    println("Hello,")
    job.join() // Ждем завершения при необходимости
}
// Hello,
// (задержка ~1 секунда)
// World!
```

### Async
Запускает корутину, возвращающую результат через `Deferred<T>`. Используется для конкурентного вычисления значений.
```kotlin
fun main() = runBlocking {
    val deferred = async {
        delay(1000)
        "Result"
    }
    println(deferred.await())  // Ждем результат
}
```

### runBlocking
Создает корутину и блокирует текущий поток до завершения переданного блока, возвращая результат этого блока. Обычно используется только на границах (например, в main или тестах).
```kotlin
fun main() {
    val result = runBlocking {
        delay(1000)
        println("Done")
        "Result"
    }
    // Блокируется на ~1 секунду, затем выводит Done и сохраняет "Result" в result
}
```

### Ключевые Отличия
| Builder | Возвращает          | Блокирует поток | Применение                                  |
|---------|---------------------|-----------------|----------------------------------------------|
| launch  | `Job`               | Нет             | "Запустить и забыть", побочные эффекты      |
| async   | `Deferred<T>`       | Нет             | Нужен результат, конкурентные вычисления     |
| runBlocking | Результат блока `T` | Да         | Граница с блокирующим кодом: main(), тесты |

### Практические Примеры
```kotlin
// Внутри CoroutineScope или runBlocking
fun main() = runBlocking {
    // Запустить несколько операций параллельно
    val job1 = launch { operation1() }
    val job2 = launch { operation2() }
    job1.join()
    job2.join()

    // Получить результаты из async параллельно
    val result1 = async { fetchData1() }
    val result2 = async { fetchData2() }
    process(result1.await(), result2.await())
}

// Мост к корутинам в main
fun main() = runBlocking {
    launch { /* корутина */ }
}
```

См. также: [[c-kotlin-coroutines-basics]]

---

## Answer (EN)

`Coroutine` builders are functions that create and start coroutines within a given `CoroutineScope`. The main builders are `launch`, `async`, and `runBlocking`.

### Launch
Starts a new coroutine and returns a `Job`. Intended for tasks with side effects where you don't need a direct result.
```kotlin
fun main() = runBlocking {
    val job = launch {
        delay(1000)
        println("World!")
    }
    println("Hello,")
    job.join() // Wait for completion if needed
}
// Hello,
// (about 1 second delay)
// World!
```

### Async
Starts a coroutine that returns a result via `Deferred<T>`. Used for concurrent computations that produce values.
```kotlin
fun main() = runBlocking {
    val deferred = async {
        delay(1000)
        "Result"
    }
    println(deferred.await())  // Wait for result
}
```

### runBlocking
Creates a coroutine and blocks the current thread until the given block completes, returning that block's result. Typically used only at boundaries (e.g., in main or tests).
```kotlin
fun main() {
    val result = runBlocking {
        delay(1000)
        println("Done")
        "Result"
    }
    // Blocks for about 1 second, then prints Done and stores "Result" in result
}
```

### Key Differences
| Builder    | Returns            | Blocks `Thread` | Use Case                                      |
|------------|--------------------|---------------|-----------------------------------------------|
| launch     | `Job`              | No            | Fire and forget, side effects                 |
| async      | `Deferred<T>`      | No            | Need a result, concurrent computations        |
| runBlocking| Block result `T`   | Yes           | Boundary with blocking code: main(), tests    |

### Practical Examples
```kotlin
// Inside a CoroutineScope or runBlocking
fun main() = runBlocking {
    // Launch multiple operations in parallel
    val job1 = launch { operation1() }
    val job2 = launch { operation2() }
    job1.join()
    job2.join()

    // Get results from async concurrently
    val result1 = async { fetchData1() }
    val result2 = async { fetchData2() }
    process(result1.await(), result2.await())
}

// Bridge to coroutines in main
fun main() = runBlocking {
    launch { /* coroutine */ }
}
```

---

## Дополнительные Вопросы (RU)

1. Объясните, когда вы выберете `launch` вместо `async` и почему (учитывая тип возвращаемого значения и характер задачи).
2. Почему `runBlocking` не рекомендуется использовать в продакшн-коде Android или серверных приложений (обсудите блокировку потоков и влияние на масштабируемость)?
3. Как связаны `CoroutineScope`, `CoroutineContext` и выбор билдера (`launch`/`async`) при проектировании структурированной конкуррентности?
4. Что произойдет, если внутри `runBlocking` запустить несколько `launch`/`async`, и как это влияет на время выполнения?
5. Как бы вы организовали параллельную загрузку данных с помощью нескольких `async` и последующей агрегацией результатов?

---

## Follow-ups

1. When would you choose `launch` over `async`, and why (considering return type and nature of the task)?
2. Why is `runBlocking` generally discouraged in production Android or server code (discuss thread blocking and scalability impact)?
3. How do `CoroutineScope`, `CoroutineContext`, and the choice of builder (`launch`/`async`) relate when designing structured concurrency?
4. What happens if you start multiple `launch`/`async` calls inside a single `runBlocking`, and how does this affect execution time?
5. How would you organize parallel data loading using multiple `async` calls and then aggregate the results?

---

## Ссылки (RU)

- [Документация по Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html)
- [[c-kotlin-coroutines-basics]]

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)
- [[c-kotlin-coroutines-basics]]

---

## Связанные Вопросы (RU)

### Похожие (Easy)
- [[q-coroutine-scope-basics--kotlin--easy]] - Основы CoroutineScope
- [[q-what-is-coroutine--kotlin--easy]] - Что такое корутина
- [[q-suspend-functions-basics--kotlin--easy]] - Основы suspend-функций
- [[q-launch-vs-async--kotlin--easy]] - Разница между launch и async

### Того Же Уровня (Easy)
- [[q-what-is-coroutine--kotlin--easy]] - Базовые концепции корутин
- [[q-coroutine-scope-basics--kotlin--easy]] - Основы CoroutineScope
- [[q-coroutine-delay-vs-thread-sleep--kotlin--easy]] - `delay()` vs `Thread.sleep()`
- [[q-coroutines-threads-android-differences--kotlin--easy]] - Coroutines vs Threads в Android

### Следующие Шаги (Medium)
- [[q-suspend-functions-basics--kotlin--easy]] - Понимание suspend-функций
- [[q-coroutine-dispatchers--kotlin--medium]] - Обзор диспетчеров корутин
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Сравнение Scope и `CoroutineContext`

### Продвинутое (Harder)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Работа с `Flow` и комбинацией потоков
- [[q-coroutine-profiling--kotlin--hard]] - Профилирование корутин
- [[q-coroutine-performance-optimization--kotlin--hard]] - Оптимизация производительности корутин

### Хабы
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Обзор и введение в корутины Kotlin

---

## Related Questions

### Related (Easy)
- [[q-coroutine-scope-basics--kotlin--easy]] - Coroutines
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines
- [[q-suspend-functions-basics--kotlin--easy]] - Coroutines
- [[q-launch-vs-async--kotlin--easy]] - Coroutines

### Same Level (Easy)
- [[q-what-is-coroutine--kotlin--easy]] - Basic coroutine concepts
- [[q-coroutine-scope-basics--kotlin--easy]] - CoroutineScope fundamentals
- [[q-coroutine-delay-vs-thread-sleep--kotlin--easy]] - `delay()` vs `Thread.sleep()`
- [[q-coroutines-threads-android-differences--kotlin--easy]] - Coroutines vs Threads on Android

### Next Steps (Medium)
- [[q-suspend-functions-basics--kotlin--easy]] - Understanding suspend functions
- [[q-coroutine-dispatchers--kotlin--medium]] - `Coroutine` dispatchers overview
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs `CoroutineContext`

### Advanced (Harder)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines
- [[q-coroutine-performance-optimization--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction
