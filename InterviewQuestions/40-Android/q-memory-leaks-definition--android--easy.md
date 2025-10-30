---
id: 20251012-122711
title: "Memory Leaks Definition / Определение утечек памяти"
aliases: ["Memory Leaks Definition", "Определение утечек памяти"]
topic: android
subtopics: [performance-memory, lifecycle]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-10-28
sources: []
tags: [android/performance-memory, android/lifecycle, memory-leaks, performance, difficulty/easy]
moc: moc-android
related: [q-coroutine-memory-leaks--kotlin--hard, q-coroutine-memory-leak-detection--kotlin--hard]
date created: Tuesday, October 28th 2025, 9:36:26 pm
date modified: Thursday, October 30th 2025, 3:13:19 pm
---

# Вопрос (RU)

> Что такое утечки памяти в Android и как они возникают?

# Question (EN)

> What are memory leaks in Android and how do they occur?

---

## Ответ (RU)

**Утечка памяти** возникает, когда объект больше не используется приложением, но остаётся недоступным для сборщика мусора из-за сохранившихся ссылок на него.

**Основные причины:**

**1. Статические ссылки на Activity:**

```kotlin
// ❌ Утечка памяти
class MyActivity : AppCompatActivity() {
    companion object {
        var instance: Activity? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instance = this  // Activity никогда не освободится
    }
}
```

**2. Обработчики и отложенные задачи:**

```kotlin
// ❌ Утечка памяти
class MyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        handler.postDelayed({
            updateUI()  // Удерживает Activity
        }, 60000)
    }
}

// ✅ Правильно
class MyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.postDelayed({ updateUI() }, 60000)
    }

    override fun onDestroy() {
        handler.removeCallbacksAndMessages(null)
        super.onDestroy()
    }
}
```

**3. Забытые слушатели:**

```kotlin
// ❌ Утечка памяти
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        eventBus.register(this)
        // Отсутствует unregister в onDestroy
    }
}

// ✅ Правильно
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        eventBus.register(this)
    }

    override fun onDestroy() {
        eventBus.unregister(this)
        super.onDestroy()
    }
}
```

**Последствия:**

- Рост потребления памяти
- OutOfMemoryError
- Замедление приложения
- Расход батареи

**Обнаружение:**

```kotlin
// LeakCanary автоматически обнаруживает утечки
debugImplementation("com.squareup.leakcanary:leakcanary-android")

// Показывает:
// - Утёкший объект
// - Цепочку удержания
// - Размер удержанной памяти
```

## Answer (EN)

A **memory leak** occurs when an object is no longer used by the application but remains inaccessible to the garbage collector due to existing references.

**Common causes:**

**1. Static references to Activity:**

```kotlin
// ❌ Memory leak
class MyActivity : AppCompatActivity() {
    companion object {
        var instance: Activity? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instance = this  // Activity never released
    }
}
```

**2. Handlers and delayed tasks:**

```kotlin
// ❌ Memory leak
class MyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        handler.postDelayed({
            updateUI()  // Holds Activity reference
        }, 60000)
    }
}

// ✅ Correct
class MyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.postDelayed({ updateUI() }, 60000)
    }

    override fun onDestroy() {
        handler.removeCallbacksAndMessages(null)
        super.onDestroy()
    }
}
```

**3. Forgotten listeners:**

```kotlin
// ❌ Memory leak
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        eventBus.register(this)
        // Missing unregister in onDestroy
    }
}

// ✅ Correct
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        eventBus.register(this)
    }

    override fun onDestroy() {
        eventBus.unregister(this)
        super.onDestroy()
    }
}
```

**Effects:**

- Memory usage grows over time
- OutOfMemoryError crashes
- App performance degradation
- Battery drain

**Detection:**

```kotlin
// LeakCanary automatically detects leaks
debugImplementation("com.squareup.leakcanary:leakcanary-android")

// Shows:
// - Leaked object
// - Retention chain
// - Retained memory size
```

---

## Follow-ups

- How do you detect memory leaks using Android Profiler?
- What is the difference between a memory leak and a memory bloat?
- How can weak references help prevent memory leaks?
- What are common memory leaks in ViewModel and LiveData?
- How do coroutines prevent or cause memory leaks?

## References

- Android Memory Profiler documentation
- LeakCanary official guide
- [Android Performance: Memory](https://developer.android.com/topic/performance/memory)

## Related Questions

### Prerequisites
- [[q-primitive-vs-reference-types--programming-languages--easy]] - Understanding references
- [[q-reference-types-criteria--programming-languages--medium]] - Reference types in depth

### Related
- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Detecting coroutine leaks
- Activity lifecycle and proper cleanup
- RecyclerView memory efficiency patterns

### Advanced
- [[q-coroutine-memory-leaks--kotlin--hard]] - Coroutine-specific memory leaks
- [[q-find-object-without-references--programming-languages--medium]] - Advanced GC behavior
