---
---
---id: kotlin-110
title: "Structured Concurrency Patterns / Паттерны структурированной конкурентности"
aliases: ["Structured Concurrency Patterns", "Паттерны структурированной конкурентности"]

# Classification
topic: kotlin
subtopics: [coroutines, coroutinescope]
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
related: [c-concurrency, c-coroutines, c-stateflow, c-structured-concurrency, q-advanced-coroutine-patterns--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [advanced, coroutines, coroutinescope, difficulty/hard, kotlin, structured-concurrency, supervision]
---
# Вопрос (RU)
> Что такое структурированная конкурентность? Объясните различия coroutineScope и supervisorScope, отношения родитель-потомок, распространение отмены и продвинутые паттерны, включая withContext и координацию async/await.

---

# Question (EN)
> What is structured concurrency? Explain coroutineScope vs supervisorScope, parent-child relationships, cancellation propagation, and advanced patterns like withContext, async-await coordination.

## Ответ (RU)

Структурированная конкурентность гарантирует, что все дочерние корутины завершаются в рамках своей области, прежде чем завершится родитель, что предотвращает утечки и обеспечивает корректную очистку ресурсов.

### Базовые Принципы

```kotlin
// Структурированная конкурентность гарантирует:
// 1. Родитель ждёт всех дочерних корутин
// 2. Отмена родителя отменяет всех детей
// 3. Ошибка ребёнка отменяет родителя (кроме случаев supervisor)

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
} // Приостанавливается, пока все дети не завершатся

// Вывод:
// Parent waiting...
// Child 1 done
// Child 2 done
// (после этого функция возвращается)
```

### coroutineScope Vs supervisorScope

```kotlin
// coroutineScope: ошибка одной дочерней корутины → отменяются все дети и область
suspend fun coroutineScopeExample() {
    try {
        coroutineScope {
            launch {
                delay(100)
                throw Exception("Child 1 failed")
            }
            
            launch {
                delay(1000)
                println("Child 2 completes") // Никогда не будет выведено
            }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}") // Caught: Child 1 failed
    }
}

// supervisorScope: ошибка одной дочерней корутины не валит остальных
suspend fun supervisorScopeExample() {
    supervisorScope {
        launch {
            delay(100)
            throw Exception("Child 1 failed") // Падает только эта корутина
        }
        
        launch {
            delay(200)
            println("Child 2 completes") // Всё ещё будет выведено
        }
    }
    println("SupervisorScope completed")
}
```

### Продвинутые Паттерны

```kotlin
// Паттерн 1: Параллельная декомпозиция с async
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

// Паттерн 2: Fail-fast с coroutineScope
suspend fun failFast() = coroutineScope {
    val result1 = async { operation1() }
    val result2 = async { operation2() }
    
    // Если любая из них падает, обе отменяются, обеспечивая согласованность
    Result(result1.await(), result2.await())
}

// Паттерн 3: Независимые задачи с supervisorScope
suspend fun independentTasks() = supervisorScope {
    launch { task1() } // Может упасть независимо
    launch { task2() } // Может упасть независимо
    launch { task3() } // Может упасть независимо
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

Также в структурированной конкурентности активно используется `withContext` для переключения контекстов без потери гарантий: все операции внутри `withContext` принадлежат области вызвавшей корутины и корректно отменяются/завершаются вместе с ней.

---

## Answer (EN)

Structured concurrency ensures that all child coroutines complete within a well-defined scope before their parent completes, preventing leaks and ensuring proper cleanup of resources.

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

### coroutineScope Vs supervisorScope

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

You also commonly use `withContext` to switch dispatchers while preserving structured concurrency: all work inside `withContext` is still bound to the parent scope and is cancelled/cleaned up with it.

---

## Дополнительные Вопросы (RU)

1. Как именно распространяется отмена в иерархии корутин при использовании структурированной конкурентности?
2. В каких случаях следует предпочесть `supervisorScope` вместо `coroutineScope`?
3. Как обрабатывать частичные сбои (partial failures) при параллельном выполнении задач с `async`?
4. Как использование `withContext` влияет на структурированную конкурентность и обработку исключений?
5. Как отличить корректное использование структурированной конкурентности от анти-паттерна с глобальными `launch`?

---

## Follow-ups

1. How does cancellation propagate in a coroutine hierarchy under structured concurrency?
2. When should you prefer `supervisorScope` over `coroutineScope`?
3. How do you handle partial failures when running tasks in parallel with `async`?
4. How does using `withContext` affect structured concurrency and exception handling?
5. How do you distinguish correct structured concurrency usage from anti-patterns with global `launch`?

---

## Ссылки (RU)

- [[c-structured-concurrency]]
- [Structured Concurrency (официальная документация)](https://kotlinlang.org/docs/composing-suspending-functions.html#structured-concurrency-with-async)

---

## References

- [[c-structured-concurrency]]
- [Structured Concurrency](https://kotlinlang.org/docs/composing-suspending-functions.html#structured-concurrency-with-async)

---

## Связанные Вопросы (RU)

- [[q-coroutinescope-vs-supervisorscope--kotlin--medium]]
- [[q-coroutine-exception-handling--kotlin--medium]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]

---

## Related Questions

- [[q-coroutinescope-vs-supervisorscope--kotlin--medium]]
- [[q-coroutine-exception-handling--kotlin--medium]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]
