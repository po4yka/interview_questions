---
id: kotlin-116
title: "CoroutineScope Basics and Usage / Основы CoroutineScope и использование"
aliases: ["CoroutineScope Basics and Usage, Основы CoroutineScope и использование"]

# Classification
topic: kotlin
subtopics: [advanced, coroutines, patterns]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140030

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-coroutinescope-vs-supervisorscope--kotlin--medium, q-data-class-variables--programming-languages--medium, q-kotlin-sealed-classes-features--programming-languages--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [coroutines, difficulty/easy, difficulty/medium, kotlin]
---
# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140030

---

# Question (EN)
> Kotlin Coroutines advanced topic 140030

## Ответ (RU)


CoroutineScope определяет жизненный цикл и контекст для корутин. Каждая корутина выполняется внутри scope.

### Создание Scopes
```kotlin
// Кастомный scope
val scope = CoroutineScope(Dispatchers.Main)

// Android lifecycle scopes
lifecycleScope.launch { }
viewModelScope.launch { }

// Временный scope
coroutineScope {
    // Структурированная конкурентность
}
```

### Отмена Scope
```kotlin
val scope = CoroutineScope(Job())
scope.launch { /* работа */ }
scope.cancel()  // Отменяет все дочерние корутины
```

### Структурированная Конкурентность
```kotlin
suspend fun fetchData() = coroutineScope {
    val data1 = async { fetch1() }
    val data2 = async { fetch2() }
    combine(data1.await(), data2.await())
}  // Ждет все дочерние
```

### Лучшие Практики
1. Используйте lifecycle-aware scopes в Android
2. Всегда отменяйте кастомные scopes
3. Предпочитайте `coroutineScope` вместо `GlobalScope`
4. Используйте `supervisorScope` когда дочерние должны быть независимы

---
---

## Answer (EN)


CoroutineScope defines the lifecycle and context for coroutines. Every coroutine runs within a scope.

### Creating Scopes
```kotlin
// Custom scope
val scope = CoroutineScope(Dispatchers.Main)

// Android lifecycle scopes
lifecycleScope.launch { }
viewModelScope.launch { }

// Temporary scope
coroutineScope {
    // Structured concurrency
}
```

### Scope Cancellation
```kotlin
val scope = CoroutineScope(Job())
scope.launch { /* work */ }
scope.cancel()  // Cancels all child coroutines
```

### Structured Concurrency
```kotlin
suspend fun fetchData() = coroutineScope {
    val data1 = async { fetch1() }
    val data2 = async { fetch2() }
    combine(data1.await(), data2.await())
}  // Wait for all children
```

### Best Practices
1. Use lifecycle-aware scopes in Android
2. Always cancel custom scopes
3. Prefer `coroutineScope` over `GlobalScope`
4. Use `supervisorScope` when children should be independent

---
---

## Follow-ups

1. **Follow-up question 1**
2. **Follow-up question 2**

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

---

## Related Questions

### Related (Easy)
- [[q-coroutine-builders-basics--kotlin--easy]] - Coroutines
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines
- [[q-suspend-functions-basics--kotlin--easy]] - Coroutines
- [[q-launch-vs-async--kotlin--easy]] - Coroutines

### Same Level (Easy)
- [[q-what-is-coroutine--kotlin--easy]] - Basic coroutine concepts
- [[q-coroutine-builders-basics--kotlin--easy]] - launch, async, runBlocking
- [[q-coroutine-delay-vs-thread-sleep--kotlin--easy]] - delay() vs Thread.sleep()
- [[q-coroutines-threads-android-differences--kotlin--easy]] - Coroutines vs Threads on Android

### Next Steps (Medium)
- [[q-suspend-functions-basics--kotlin--easy]] - Understanding suspend functions
- [[q-coroutine-dispatchers--kotlin--medium]] - Coroutine dispatchers overview
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs Context

### Advanced (Harder)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines
- [[q-coroutine-performance-optimization--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

