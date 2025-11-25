---
id: cs-027
title: "Zip Operator Parallel Requests / Оператор zip для параллельных запросов"
aliases: ["Zip Operator", "Оператор zip"]
topic: concurrency
subtopics: [parallel-processing]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-concurrency, q-hot-vs-cold-flows--programming-languages--medium, q-launch-vs-async-await--programming-languages--medium, q-what-is-flow--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [concurrency, coroutines, difficulty/medium, flow, kotlin, parallel-requests, zip-operator]
sources: ["https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/zip.html"]

date created: Saturday, October 4th 2025, 10:39:32 am
date modified: Tuesday, November 25th 2025, 8:53:53 pm
---

# Вопрос (RU)
> Как использовать оператор zip для параллельных запросов?

# Question (EN)
> How do you use the zip operator for parallel requests?

---

## Ответ (RU)

**Теория Zip Operator:**
Оператор `zip` комбинирует элементы из нескольких потоков данных в один поток, попарно по индексу. Он сам по себе НЕ запускает источники параллельно и не гарантирует параллельное выполнение — параллелизм обеспечивается тем, как и где исполняются исходные операции (потоки, корутины, шедулеры). `zip` доступен в RxJava и Kotlin `Flow`. Он полезен, когда нужно объединить результаты нескольких независимых асинхронных источников, которые уже могут работать конкурентно.

Для параллельных запросов в Kotlin обычно:
- используем `async`/`await` для конкурентного выполнения нескольких `suspend`-функций;
- используем `Flow` + `zip`, когда есть несколько потоков (flows), которые уже эмитят данные (возможно, конкурентно), и нужно объединять их по позициям.

**1. async/await для параллельного выполнения:**
*Теория:* Запускаем несколько операций через `async`, затем дожидаемся результатов через `await`. Это даёт конкурентное выполнение: все запросы стартуют почти одновременно в рамках доступных потоков/диспетчера, итоговое время ≈ максимум из времен отдельных операций (например, вместо 150ms + 180ms делаем около 180ms).

```kotlin
// ✅ Параллельное (конкурентное) выполнение с async/await
suspend fun fetchAllUserData(userId: Int): CombinedData = coroutineScope {
    val profileDeferred = async { fetchUserProfile(userId) }
    val postsDeferred = async { fetchUserPosts(userId) }
    val settingsDeferred = async { fetchUserSettings(userId) }

    CombinedData(
        profile = profileDeferred.await(),
        posts = postsDeferred.await(),
        settings = settingsDeferred.await()
    )
}
```

**2. `Flow`.zip для потоковых данных и объединения результатов:**
*Теория:* Оператор `zip` для `Flow` берёт по одному элементу из каждого исходного `Flow` и эмитит пары/кортежи. Он:
- ждёт значения от всех источников для каждой позиции;
- останавливается, когда завершится самый короткий `Flow`;
- не делает вычисления автоматически параллельными: источники могут работать последовательно или конкурентно, в зависимости от их реализации (например, запуска в разных корутинах/диспетчерах).

```kotlin
// ✅ Flow.zip объединяет элементы по индексу
getProfileFlow()
    .zip(getPostsFlow()) { profile, posts ->
        profile to posts
    }
    .zip(getSettingsFlow()) { (profile, posts), settings ->
        Triple(profile, posts, settings)
    }
    .collect { (profile, posts, settings) ->
        // Обработка комбинированных данных
    }
```

**Практика: zip и параллельные запросы:**
Если нужно выполнить несколько независимых запросов параллельно и объединить их результат:
- выполняем запросы конкурентно (например, через `async` или отдельные Flows/корутины);
- затем объединяем их результат:
  - либо после `await` (как в примере выше);
  - либо через `zip`, если каждый запрос представлен как `Flow`.

**3. combine vs zip:**
*Теория:*
- `zip` — попарно по индексу: для каждого эмитта ждёт элементы от всех источников; количество результатов ограничено самым коротким `Flow`.
- `combine` — "latest values": начинает эмитить после того, как каждый источник выдал хотя бы одно значение, далее эмитит при ЛЮБОМ новом значении из любого источника, используя последние значения всех.

```kotlin
// ✅ zip: пары по индексу
flowOf(1, 2, 3).zip(flowOf("A", "B")) { num, letter ->
    "$num$letter"
} // Эмитит: 1A, 2B

// ✅ combine: последние значения
flowOf(1, 2, 3).combine(flowOf("A", "B")) { num, letter ->
    "$num$letter"
} // Эмитит несколько комбинаций с использованием последних значений
```

**Когда использовать:**
- Фиксированное число параллельных запросов к API → `async`/`await` для конкурентного выполнения и последующего объединения результатов.
- Потоковые данные из нескольких источников, которые уже работают (в т.ч. параллельно) → `Flow.zip` для один-к-одному по индексу.
- Реальное время и реакция на любые изменения, когда важно всегда иметь комбинированное "последнее состояние" → `combine`.
- Объединение независимых операций с учётом их природы (одноразовые запросы vs непрерывные потоки).

## Answer (EN)

**Zip Operator Theory:**
The `zip` operator combines elements from multiple data streams into a single stream by pairing items by index. It does NOT by itself start sources in parallel or guarantee parallel execution — parallelism is determined by how the upstream operations are executed (threads, dispatchers, schedulers). `zip` exists in RxJava and Kotlin `Flow` and is useful when you need to join results from multiple independent async sources that may already be running concurrently.

For parallel requests in Kotlin you typically:
- use `async`/`await` to run multiple suspend functions concurrently;
- use `Flow` + `zip` when you have multiple flows that are (possibly concurrently) emitting and you want to combine their emissions by position.

**1. async/await for parallel execution:**
*Theory:* Launch multiple operations with `async`, then wait for results with `await`. This gives concurrent execution: all requests start nearly at the same time (subject to dispatcher/threads), and total time ≈ the max of individual durations (e.g., instead of 150ms + 180ms you get around 180ms).

```kotlin
// ✅ Parallel (concurrent) execution with async/await
suspend fun fetchAllUserData(userId: Int): CombinedData = coroutineScope {
    val profileDeferred = async { fetchUserProfile(userId) }
    val postsDeferred = async { fetchUserPosts(userId) }
    val settingsDeferred = async { fetchUserSettings(userId) }

    CombinedData(
        profile = profileDeferred.await(),
        posts = postsDeferred.await(),
        settings = settingsDeferred.await()
    )
}
```

**2. `Flow`.zip for streaming data and result merging:**
*Theory:* `Flow`'s `zip` operator takes one element from each upstream `Flow` and emits a combined value. It:
- waits for a value from all sources for each position;
- stops when the shortest `Flow` completes;
- does not automatically make upstream computations parallel; they may run sequentially or concurrently depending on how those flows are implemented (e.g., launched in separate coroutines/dispatchers).

```kotlin
// ✅ Flow.zip pairs elements by index
getProfileFlow()
    .zip(getPostsFlow()) { profile, posts ->
        profile to posts
    }
    .zip(getSettingsFlow()) { (profile, posts), settings ->
        Triple(profile, posts, settings)
    }
    .collect { (profile, posts, settings) ->
        // Handle combined data
    }
```

**Practical: zip and parallel requests:**
If you need to run several independent requests in parallel and combine their results:
- run them concurrently (e.g., using `async` or separate flows/coroutines);
- then merge results:
  - either after `await` (as in the example above);
  - or via `zip` if each request is represented as a `Flow`.

**3. combine vs zip:**
*Theory:*
- `zip`: index-based one-to-one pairing — for each emission it waits for values from all sources; number of outputs is limited by the shortest flow.
- `combine`: "latest values" — after each source has emitted at least once, it emits on ANY new emission from any source, using the latest values from all.

```kotlin
// ✅ zip: pairs by index
flowOf(1, 2, 3).zip(flowOf("A", "B")) { num, letter ->
    "$num$letter"
} // Emits: 1A, 2B

// ✅ combine: latest values
flowOf(1, 2, 3).combine(flowOf("A", "B")) { num, letter ->
    "$num$letter"
} // Emits multiple combinations using the latest values
```

**When to use:**
- Fixed set of parallel API calls → `async/await` for concurrent execution, then combine results.
- Streaming data from multiple sources that are already emitting (possibly concurrently) → `Flow.zip` for one-to-one, index-based pairing.
- Real-time synchronization / reactive UIs where you always need the combined latest state → `combine`.
- Combining independent operations according to their nature (one-shot vs continuous streams).

---

## Дополнительные Вопросы (RU)

- В чем разница между операторами `zip` и `combine`?
- Когда стоит использовать `async`/`await` вместо `Flow`.zip?
- Как обрабатывать ошибки при параллельных запросах?

## Follow-ups

- What is the difference between zip and combine operators?
- When should you use async/await vs `Flow`.zip?
- How to handle errors with parallel requests?

## Связанные Вопросы (RU)

### Предпосылки (Проще)
- Базовые понятия корутин и `Flow`
- Понимание асинхронных операций

### Связанные (Тот Же уровень)
- [[q-what-is-flow--programming-languages--medium]] — Что такое `Flow`
- [[q-launch-vs-async-await--programming-languages--medium]] — launch vs async
- [[q-hot-vs-cold-flows--programming-languages--medium]] — hot vs cold flows

### Продвинутое (Сложнее)
- Продвинутые операторы `Flow`
- Сложные паттерны параллельной обработки
- Управление backpressure

## Related Questions

### Prerequisites (Easier)
- Basic coroutines and `Flow` concepts
- Understanding of async operations

### Related (Same Level)
- [[q-what-is-flow--programming-languages--medium]] - What is `Flow`
- [[q-launch-vs-async-await--programming-languages--medium]] - launch vs async
- [[q-hot-vs-cold-flows--programming-languages--medium]] - hot vs cold flows

### Advanced (Harder)
- Advanced `Flow` operators
- Complex parallel processing patterns
- Backpressure handling

## References

- Kotlinx Coroutines `Flow` zip docs: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/zip.html
- [[c-concurrency]]
