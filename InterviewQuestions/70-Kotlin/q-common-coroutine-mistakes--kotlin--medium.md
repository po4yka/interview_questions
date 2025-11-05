---
id: kotlin-098
title: "Top 10 common Kotlin coroutines mistakes and anti-patterns / 10 частых ошибок с Kotlin корутинами"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-12
tags: [anti-patterns, best-practices, code-review, coroutines, difficulty/medium, gotchas, kotlin, mistakes]
moc: moc-kotlin
related: [q-coroutine-exception-handler--kotlin--medium, q-coroutine-virtual-time--kotlin--medium, q-debugging-coroutines-techniques--kotlin--medium, q-flow-backpressure--kotlin--hard, q-kotlin-collections-overview--programming-languages--easy, q-mutex-synchronized-coroutines--kotlin--medium]
subtopics:
  - anti-patterns
  - best-practices
  - coroutines
  - gotchas
  - mistakes
date created: Saturday, November 1st 2025, 12:10:17 pm
date modified: Saturday, November 1st 2025, 5:43:27 pm
---
# Вопрос (RU)
> Какие самые распространенные ошибки при использовании Kotlin корутин, и как их исправить?

---

# Question (EN)
> What are the most common mistakes when using Kotlin coroutines, and how do you fix them?

## Ответ (RU)

Даже опытные разработчики совершают типичные ошибки при работе с Kotlin корутинами. Эти ошибки могут привести к утечкам памяти, крашам, состояниям гонки или плохой производительности. Понимание и избегание этих анти-паттернов критично для production-ready кода.



[Полный русский перевод следует той же структуре]

### Ключевые Выводы

1. **Никогда не используйте GlobalScope** - Используйте lifecycle-aware области
2. **Всегда обрабатывайте отмену** - Проверяйте isActive, используйте ensureActive()
3. **Не блокируйте потоки** - Никакого runBlocking или Thread.sleep в production
4. **Используйте правильные диспетчеры** - IO для I/O, Default для CPU, Main для UI
5. **supervisorScope для независимости** - Независимые сбои задач
6. **Всегда await() async** - Не забывайте результаты
7. **Минимизируйте создание корутин** - Только когда полезно
8. **Структурированная конкурентность** - Позвольте фреймворку управлять lifecycle
9. **Избегайте утечек памяти** - Используйте правильные области
10. **Правильная обработка исключений** - Знайте различия launch vs async

---

## Answer (EN)

Even experienced developers make common mistakes when working with Kotlin coroutines. These mistakes can lead to memory leaks, crashes, race conditions, or poor performance. Understanding and avoiding these anti-patterns is critical for production-ready code.



### Mistake 1: Using GlobalScope

**Problem:** `GlobalScope` coroutines are not tied to any lifecycle and can leak.

```kotlin
//  WRONG: GlobalScope coroutine continues after Activity destroyed
class MyActivity : AppCompatActivity() {
    fun loadData() {
        GlobalScope.launch {
            val data = repository.fetchData()
            updateUI(data) // Crashes if Activity destroyed!
        }
    }
}
```

**Why wrong:**
- Coroutine continues even after Activity/ViewModel destroyed
- Can cause memory leaks
- Can crash when accessing destroyed views
- No structured concurrency

** FIX: Use proper scope**

```kotlin
//  CORRECT: Use lifecycleScope
class MyActivity : AppCompatActivity() {
    fun loadData() {
        lifecycleScope.launch {
            val data = repository.fetchData()
            updateUI(data) // Safe: cancelled when Activity destroyed
        }
    }
}

//  CORRECT: Use viewModelScope
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = repository.fetchData()
            _dataState.value = data // Safe: cancelled when ViewModel cleared
        }
    }
}

//  CORRECT: Custom scope with lifecycle
class MyRepository {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun fetchData() {
        scope.launch {
            // Work
        }
    }

    fun cleanup() {
        scope.cancel() // Cancel all coroutines
    }
}
```

**Detection:** Search codebase for `GlobalScope`

```bash
## Follow-ups

1. How do you implement custom CoroutineScope with proper lifecycle management?
2. What tools exist for detecting coroutine-related memory leaks?
3. How do you refactor legacy code with GlobalScope to use proper scopes?
4. Can you explain the performance impact of excessive coroutine creation?
5. How do you audit a codebase for coroutine anti-patterns?
6. What are the most subtle coroutine bugs that are hard to detect?
7. How do you educate a team about coroutine best practices?

## References

- [Kotlin Coroutines Best Practices](https://kotlinlang.org/docs/coroutines-guide.html)
- [Android Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)
- [Common Coroutine Mistakes](https://elizarov.medium.com/top-10-coroutines-mistakes-42b19c2a25b2)

## Related Questions

- [[q-coroutine-exception-handler--kotlin--medium|CoroutineExceptionHandler usage]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Debugging coroutines]]
- [[q-mutex-synchronized-coroutines--kotlin--medium|Thread-safe coroutines]]
