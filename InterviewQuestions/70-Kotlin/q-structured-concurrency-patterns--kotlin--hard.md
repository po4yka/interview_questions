---
id: 20251012-140016
title: "Structured Concurrency Patterns / Паттерны структурированной конкурентности"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, structured-concurrency, coroutinescope, supervision, advanced]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Structured Concurrency Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-coroutinescope-vs-supervisorscope--kotlin--medium, q-coroutine-exception-handling--kotlin--medium, q-advanced-coroutine-patterns--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, coroutines, structured-concurrency, coroutinescope, supervision, advanced, difficulty/hard]
---
# Question (EN)
> What is structured concurrency? Explain coroutineScope vs supervisorScope, parent-child relationships, cancellation propagation, and advanced patterns like withContext, async-await coordination.

# Вопрос (RU)
> Что такое структурированная конкурентность? Объясните coroutineScope vs supervisorScope, отношения родитель-потомок, распространение отмены и продвинутые паттерны.

---

## Answer (EN)

Structured concurrency ensures that all child coroutines complete before their parent, preventing leaks and ensuring proper cleanup.

### Core Principles

```kotlin
// Structured concurrency ensures:
// 1. Parent waits for all children
// 2. Parent cancellation cancels children
// 3. Child failure cancels parent (unless supervised)

suspend fun structuredExample() = coroutineScope {
    launch {
        delay(100)
        println("Child 1 done")
    }
    
    launch {
        delay(200)
        println("Child 2 done")
    }
    
    println("Parent waiting...")
} // Suspends until all children complete

// Output:
// Parent waiting...
// Child 1 done
// Child 2 done
// (then function returns)
```

### coroutineScope vs supervisorScope

```kotlin
// coroutineScope: One child fails → all fail
suspend fun coroutineScopeExample() {
    try {
        coroutineScope {
            launch {
                delay(100)
                throw Exception("Child 1 failed")
            }
            
            launch {
                delay(1000)
                println("Child 2 completes") // Never prints
            }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}") // Caught: Child 1 failed
    }
}

// supervisorScope: One child fails → others continue
suspend fun supervisorScopeExample() {
    supervisorScope {
        launch {
            delay(100)
            throw Exception("Child 1 failed") // Crashes this child only
        }
        
        launch {
            delay(200)
            println("Child 2 completes") // Still prints!
        }
    }
    println("SupervisorScope completed")
}
```

### Advanced Patterns

```kotlin
// Pattern 1: Parallel decomposition with async
suspend fun parallelFetch(): UserProfile = coroutineScope {
    val userDeferred = async { fetchUser() }
    val postsDeferred = async { fetchPosts() }
    val friendsDeferred = async { fetchFriends() }
    
    UserProfile(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        friends = friendsDeferred.await()
    )
}

// Pattern 2: Fail-fast with coroutineScope
suspend fun failFast() = coroutineScope {
    val result1 = async { operation1() }
    val result2 = async { operation2() }
    
    // If either fails, both cancel
    Result(result1.await(), result2.await())
}

// Pattern 3: Independent tasks with supervisorScope
suspend fun independentTasks() = supervisorScope {
    launch { task1() } // Can fail independently
    launch { task2() } // Can fail independently
    launch { task3() } // Can fail independently
}

data class UserProfile(val user: String, val posts: List<String>, val friends: List<String>)
data class Result(val r1: String, val r2: String)
private suspend fun fetchUser() = "user"
private suspend fun fetchPosts() = listOf("post")
private suspend fun fetchFriends() = listOf("friend")
private suspend fun operation1() = "op1"
private suspend fun operation2() = "op2"
private suspend fun task1() {}
private suspend fun task2() {}
private suspend fun task3() {}
```

---

## Ответ (RU)

Структурированная конкурентность гарантирует, что родительская корутина ждет завершения всех дочерних.

### Принципы

1. Родитель ждет всех детей
2. Отмена родителя отменяет детей
3. Ошибка ребенка отменяет родителя (кроме supervisor)

### coroutineScope vs supervisorScope

- **coroutineScope**: Ошибка одного → отмена всех
- **supervisorScope**: Ошибка одного → остальные продолжают

---

## Follow-up Questions

1. **How does cancellation propagate in structured concurrency?**
2. **When to use supervisorScope vs coroutineScope?**
3. **How to handle partial failures?**

---

## References

- [Structured Concurrency](https://kotlinlang.org/docs/composing-suspending-functions.html#structured-concurrency-with-async)

---

## Related Questions

- [[q-coroutinescope-vs-supervisorscope--kotlin--medium]]
- [[q-coroutine-exception-handling--kotlin--medium]]
