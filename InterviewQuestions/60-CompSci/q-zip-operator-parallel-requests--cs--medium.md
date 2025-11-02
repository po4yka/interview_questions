---
id: cs-027
title: "Zip Operator Parallel Requests / Оператор zip для параллельных запросов"
aliases: ["Zip Operator", "Оператор zip"]
topic: cs
subtopics: [coroutines, flow, parallel-processing]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-hot-vs-cold-flows--programming-languages--medium, q-launch-vs-async-await--programming-languages--medium, q-what-is-flow--programming-languages--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [coroutines, difficulty/medium, flow, kotlin, parallel-requests, zip-operator]
sources: [https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/zip.html]
date created: Saturday, October 4th 2025, 10:39:32 am
date modified: Saturday, November 1st 2025, 5:43:28 pm
---

# Вопрос (RU)
> Как использовать оператор zip для параллельных запросов?

# Question (EN)
> How do you use the zip operator for parallel requests?

---

## Ответ (RU)

**Теория Zip Operator:**
Zip operator - combines multiple data streams в single stream, executes them parallelly. Available в RxJava, Kotlin Flow, и coroutines. Essential когда need combine results от multiple independent async operations. Key concept: pairing elements by index, waiting для all sources. In Kotlin: `async`/`await` для parallel execution или Flow's `zip` для streaming data.

**1. async/await для параллельного выполнения:**
*Теория:* Launch multiple `async` operations, then `await` results. Executes truly parallel - все requests start simultaneously, wait для all complete. Total time = longest operation (e.g., 150ms vs 330ms sequential).

```kotlin
// ✅ Parallel execution with async/await
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

**2. Flow.zip для streaming data:**
*Теория:* Flow's `zip` operator - pairs elements by index from multiple flows, waits для all sources. Первый emission из flows paired together, второй paired together, etc. Stops когда shortest flow completes.

```kotlin
// ✅ Flow.zip pairs elements by index
getProfileFlow()
    .zip(getPostsFlow()) { profile, posts ->
        Pair(profile, posts)
    }
    .zip(getSettingsFlow()) { (profile, posts), settings ->
        Triple(profile, posts, settings)
    }
    .collect { (profile, posts, settings) ->
        // Handle combined data
    }
```

**3. combine vs zip:**
*Теория:* `zip` - pairs elements by index, waits для all sources emit. `combine` - emits when ANY source emits, uses latest value from each. `zip` - one-to-one pairing. `combine` - latest values combination.

```kotlin
// ✅ zip: pairs by index
flowOf(1, 2, 3).zip(flowOf("A", "B")) { num, letter ->
    "$num$letter"
}  // Emits: 1A, 2B (when both emit)

// ✅ combine: latest values
flowOf(1, 2, 3).combine(flowOf("A", "B")) { num, letter ->
    "$num$letter"
}  // Emits multiple times with latest
```

**When to use:**
- Fixed number of parallel requests (async/await)
- Streaming data from multiple sources (Flow.zip)
- Real-time synchronization (combine)
- Combining independent operations

## Answer (EN)

**Zip Operator Theory:**
Zip operator combines multiple data streams into single stream, executes them parallelly. Available in RxJava, Kotlin Flow, and coroutines. Essential when need to combine results from multiple independent async operations. Key concept: pairing elements by index, waiting for all sources. In Kotlin: `async`/`await` for parallel execution or Flow's `zip` for streaming data.

**1. async/await for parallel execution:**
*Theory:* Launch multiple `async` operations, then `await` results. Executes truly parallel - all requests start simultaneously, wait for all complete. Total time = longest operation (e.g., 150ms vs 330ms sequential).

```kotlin
// ✅ Parallel execution with async/await
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

**2. Flow.zip for streaming data:**
*Theory:* Flow's `zip` operator - pairs elements by index from multiple flows, waits for all sources. First emission from flows paired together, second paired together, etc. Stops when shortest flow completes.

```kotlin
// ✅ Flow.zip pairs elements by index
getProfileFlow()
    .zip(getPostsFlow()) { profile, posts ->
        Pair(profile, posts)
    }
    .zip(getSettingsFlow()) { (profile, posts), settings ->
        Triple(profile, posts, settings)
    }
    .collect { (profile, posts, settings) ->
        // Handle combined data
    }
```

**3. combine vs zip:**
*Theory:* `zip` - pairs elements by index, waits for all sources emit. `combine` - emits when ANY source emits, uses latest value from each. `zip` - one-to-one pairing. `combine` - latest values combination.

```kotlin
// ✅ zip: pairs by index
flowOf(1, 2, 3).zip(flowOf("A", "B")) { num, letter ->
    "$num$letter"
}  // Emits: 1A, 2B (when both emit)

// ✅ combine: latest values
flowOf(1, 2, 3).combine(flowOf("A", "B")) { num, letter ->
    "$num$letter"
}  // Emits multiple times with latest
```

**When to use:**
- Fixed number of parallel requests (async/await)
- Streaming data from multiple sources (Flow.zip)
- Real-time synchronization (combine)
- Combining independent operations

---

## Follow-ups

- What is the difference between zip and combine operators?
- When should you use async/await vs Flow.zip?
- How to handle errors with parallel requests?

## Related Questions

### Prerequisites (Easier)
- Basic coroutines and Flow concepts
- Understanding of async operations

### Related (Same Level)
- [[q-what-is-flow--programming-languages--medium]] - What is Flow
- [[q-launch-vs-async-await--programming-languages--medium]] - launch vs async
- [[q-hot-vs-cold-flows--programming-languages--medium]] - hot vs cold flows

### Advanced (Harder)
- Advanced Flow operators
- Complex parallel processing patterns
- Backpressure handling
