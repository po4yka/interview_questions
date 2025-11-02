---
id: kotlin-090
title: "Coroutine Memory Leaks and Prevention / Утечки памяти в корутинах и их предотвращение"
aliases: []

# Classification
topic: kotlin
subtopics: [advanced, coroutines, patterns]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140024

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-default-inheritance-type--programming-languages--easy, q-kotlin-sam-interfaces--kotlin--medium, q-visibility-modifiers-kotlin--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [coroutines, difficulty/hard, difficulty/medium, kotlin]
date created: Sunday, October 12th 2025, 3:39:12 pm
date modified: Saturday, November 1st 2025, 5:43:27 pm
---

# Question (EN)
> Kotlin Coroutines advanced topic 140024

# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140024

---

## Answer (EN)


Memory leaks in coroutines typically occur when coroutines are not properly cancelled, leading to retained references and wasted resources.

### Common Leak Causes

**1. Not Cancelling Scopes**
```kotlin
class ViewModel {
    private val scope = CoroutineScope(Dispatchers.Main)
    
    fun loadData() {
        scope.launch { /* work */ }
    }
    
    // Memory leak if not called!
    fun onCleared() {
        scope.cancel()
    }
}
```

**2. Using GlobalScope**
```kotlin
// Leak: Lives forever
GlobalScope.launch {
    // This runs even after Activity destroyed
}

// Fix: Use lifecycleScope
lifecycleScope.launch {
    // Automatically cancelled
}
```

**3. Capturing Activity/Fragment References**
```kotlin
// Leak
class MyActivity : Activity() {
    fun startWork() {
        GlobalScope.launch {
            updateUI()  // Captures this@MyActivity
        }
    }
}
```

### Detection Tools
- LeakCanary for Android
- Memory Profiler in Android Studio
- Heap dumps analysis

### Prevention
1. Always use structured concurrency
2. Cancel scopes in lifecycle methods
3. Use viewModelScope, lifecycleScope
4. Avoid GlobalScope except for app-level operations

---
---

## Ответ (RU)


Утечки памяти в корутинах обычно происходят когда корутины не отменяются должным образом, приводя к удержанию ссылок и расходу ресурсов.

### Распространенные Причины Утечек

**1. Не отменяются Scopes**
```kotlin
class ViewModel {
    private val scope = CoroutineScope(Dispatchers.Main)
    
    fun loadData() {
        scope.launch { /* work */ }
    }
    
    // Утечка памяти если не вызван!
    fun onCleared() {
        scope.cancel()
    }
}
```

**2. Использование GlobalScope**
```kotlin
// Утечка: Живет вечно
GlobalScope.launch {
    // Это выполняется даже после уничтожения Activity
}

// Исправление: Использовать lifecycleScope
lifecycleScope.launch {
    // Автоматически отменяется
}
```

**3. Захват ссылок на Activity/Fragment**
```kotlin
// Утечка
class MyActivity : Activity() {
    fun startWork() {
        GlobalScope.launch {
            updateUI()  // Захватывает this@MyActivity
        }
    }
}
```

### Инструменты Обнаружения
- LeakCanary для Android
- Memory Profiler в Android Studio
- Анализ heap dumps

### Предотвращение
1. Всегда используйте структурированную конкурентность
2. Отменяйте scopes в методах жизненного цикла
3. Используйте viewModelScope, lifecycleScope
4. Избегайте GlobalScope кроме операций уровня приложения

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

### Related (Hard)
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines
- [[q-coroutine-performance-optimization--kotlin--hard]] - Coroutines
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Coroutines
- [[q-select-expression-channels--kotlin--hard]] - Coroutines

### Prerequisites (Easier)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines
