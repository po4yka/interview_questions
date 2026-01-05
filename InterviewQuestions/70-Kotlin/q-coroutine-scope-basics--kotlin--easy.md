---
id: kotlin-116
title: "CoroutineScope Basics and Usage / Основы CoroutineScope и использование"
aliases: ["CoroutineScope Basics and Usage", "Основы CoroutineScope и использование"]

# Classification
topic: kotlin
subtopics: [coroutines, patterns]
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
related: [c-kotlin-coroutines-basics, q-coroutinescope-vs-supervisorscope--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [coroutines, difficulty/easy, kotlin]
---
# Вопрос (RU)
> Базовый вопрос по `CoroutineScope` в Kotlin (на основе темы 140030)

---

# Question (EN)
> Basic question about `CoroutineScope` in Kotlin (based on topic 140030)

## Ответ (RU)

`CoroutineScope` определяет жизненный цикл и контекст для корутин. Каждая корутина выполняется внутри `CoroutineScope`.

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
4. Используйте `supervisorScope`, когда дочерние корутины должны быть независимы

---

## Answer (EN)

`CoroutineScope` defines the lifecycle and context for coroutines. Every coroutine runs within a `CoroutineScope`.

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
4. Use `supervisorScope` when child coroutines should be independent

---

## Дополнительные Вопросы (RU)

1. Объясните разницу между `CoroutineScope` и `coroutineScope` и приведите пример, когда использовать каждый из них в реальном коде.
2. Какие проблемы могут возникнуть при использовании `GlobalScope`, и почему его следует избегать в продакшене?
3. Как правильно привязать `CoroutineScope` к жизненному циклу `Activity` или `ViewModel` в Android, чтобы избежать утечек памяти?
4. В каких случаях стоит использовать `supervisorScope` вместо обычного `CoroutineScope`, и как это влияет на обработку ошибок?
5. Как организовать обработку ошибок внутри `CoroutineScope`, чтобы не нарушать структурированную конкурентность и не прерывать независимые задачи?

---

## Follow-ups

1. Explain the difference between `CoroutineScope` and `coroutineScope` and provide a concrete example of when to use each in real-world code.
2. What issues can arise from using `GlobalScope`, and why should it be avoided in production code?
3. How do you properly tie a `CoroutineScope` to an `Activity` or `ViewModel` lifecycle on Android to prevent memory leaks?
4. In which scenarios should you use `supervisorScope` instead of a regular `CoroutineScope`, and how does it affect error handling?
5. How can you organize error handling within a `CoroutineScope` to preserve structured concurrency while isolating failures?

---

## Ссылки (RU)

- [[c-kotlin-coroutines-basics]]
- [Документация Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html)

---

## References

- [[c-kotlin-coroutines-basics]]
- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

---

## Связанные Вопросы (RU)

### Похожие (Easy)
- [[q-coroutine-builders-basics--kotlin--easy]] - Основы корутин
- [[q-what-is-coroutine--kotlin--easy]] - Что такое корутина
- [[q-suspend-functions-basics--kotlin--easy]] - Базовые `suspend` функции
- [[q-launch-vs-async--kotlin--easy]] - `launch` vs `async`

### Того Же Уровня (Easy)
- [[q-what-is-coroutine--kotlin--easy]] - Базовые концепции корутин
- [[q-coroutine-builders-basics--kotlin--easy]] - `launch`, `async`, `runBlocking`
- [[q-coroutine-delay-vs-thread-sleep--kotlin--easy]] - `delay()` vs `Thread.sleep()`
- [[q-coroutines-threads-android-differences--kotlin--easy]] - Coroutines vs Threads на Android

### Следующие Шаги (Medium)
- [[q-suspend-functions-basics--kotlin--easy]] - Понимание `suspend` функций
- [[q-coroutine-dispatchers--kotlin--medium]] - Обзор диспетчеров корутин
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Сравнение Scope и Context

### Продвинутые (Harder)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Работа с `Flow`
- [[q-coroutine-profiling--kotlin--hard]] - Профилирование корутин
- [[q-coroutine-performance-optimization--kotlin--hard]] - Оптимизация производительности корутин

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Обзор корутин в Kotlin

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
