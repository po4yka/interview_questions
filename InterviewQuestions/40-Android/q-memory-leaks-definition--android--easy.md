---
id: android-086
title: Memory Leaks Definition / Определение утечек памяти
aliases:
- Memory Leaks Definition
- Определение утечек памяти
topic: android
subtopics:
- lifecycle
- performance-memory
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
created: 2025-10-13
updated: 2025-11-10
sources: []
tags:
- android/lifecycle
- android/performance-memory
- difficulty/easy
- memory-leaks
- performance
moc: moc-android
related:
- c-android
- c-activity-lifecycle
- q-coroutine-memory-leak-detection--kotlin--hard
- q-coroutine-memory-leaks--kotlin--hard

---

# Вопрос (RU)

> Что такое утечки памяти в Android и как они возникают?

# Question (EN)

> What are memory leaks in Android and how do they occur?

---

## Ответ (RU)

**Утечка памяти** в Android возникает, когда объект больше не нужен для корректной работы приложения, но остаётся достижимым (есть ссылки), из-за чего сборщик мусора не может его освободить.

**Основные причины:**

**1. Статические ссылки на `Activity`:**

```kotlin
// ❌ Утечка памяти
class MyActivity : AppCompatActivity() {
    companion object {
        var instance: Activity? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instance = this  // Пока есть ссылка, Activity не может быть собрана
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
            updateUI()  // Лямбда удерживает ссылку на Activity, пока задача не выполнена
        }, 60000)
    }
}

// ✅ Правильно: очищаем отложенные задачи при уничтожении Activity
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
        // Нет unregister в onDestroy: внешняя сущность продолжает удерживать Activity
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
- Лишний расход батареи

**Обнаружение:**

```kotlin
// LeakCanary автоматически отслеживает удерживаемые (подозрительные) объекты
debugImplementation("com.squareup.leakcanary:leakcanary-android")

// Показывает:
// - Утёкший/удерживаемый объект
// - Цепочку удержания (leak trace)
```

---

## Follow-ups (RU)

- Как обнаруживать утечки памяти с помощью Android Profiler?
- В чем разница между утечкой памяти и избыточным потреблением памяти (memory bloat)?
- Как слабые ссылки (`WeakReference`) помогают предотвращать утечки памяти?
- Какие распространенные утечки памяти возникают в `ViewModel` и `LiveData`?
- Как корутины могут как предотвращать, так и вызывать утечки памяти?

## Ссылки (RU)

- Документация Android Memory Profiler
- Официальное руководство LeakCanary
- "Android Performance: Memory" на developer.android.com

## Связанные вопросы (RU)

### Предпосылки / Концепции (RU)

- [[c-android]]
- [[c-activity-lifecycle]]

### Предпосылки (RU)

- [[q-primitive-vs-reference-types--programming-languages--easy]] - Понимание ссылочных типов
- [[q-reference-types-criteria--programming-languages--medium]] - Детали ссылочных типов

### Похожие (RU)

- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Обнаружение утечек в корутинах
- Жизненный цикл `Activity` и корректная очистка ресурсов
- Паттерны эффективного использования памяти в RecyclerView

### Продвинутые (RU)

- [[q-coroutine-memory-leaks--kotlin--hard]] - Утечки памяти, связанные с `Coroutine`
- [[q-find-object-without-references--programming-languages--medium]] - Продвинутое поведение GC

---

## Answer (EN)

A **memory leak** in Android occurs when an object is no longer needed for the correct functioning of the app but remains reachable (strongly referenced), so the garbage collector cannot reclaim it.

**Common causes:**

**1. Static references to `Activity`:**

```kotlin
// ❌ Memory leak
class MyActivity : AppCompatActivity() {
    companion object {
        var instance: Activity? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instance = this  // As long as this reference exists, Activity can't be collected
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
            updateUI()  // Lambda captures Activity reference until executed
        }, 60000)
    }
}

// ✅ Correct: clear pending tasks when Activity is destroyed
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
        // Missing unregister in onDestroy: external component keeps holding Activity
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
- OutOfMemoryError
- App performance degradation
- Unnecessary battery drain

**Detection:**

```kotlin
// LeakCanary automatically tracks retained (suspicious) objects
debugImplementation("com.squareup.leakcanary:leakcanary-android")

// Shows:
// - Leaked/retained object
// - Retention path (leak trace)
```

---

## Follow-ups

- How do you detect memory leaks using Android Profiler?
- What is the difference between a memory leak and a memory bloat?
- How can weak references help prevent memory leaks?
- What are common memory leaks in `ViewModel` and `LiveData`?
- How do coroutines prevent or cause memory leaks?

## References

- Android Memory Profiler documentation
- LeakCanary official guide
- [Android Performance: Memory](https://developer.android.com/topic/performance/memory)

## Related Questions

### Prerequisites / Concepts

- [[c-android]]
- [[c-activity-lifecycle]]

### Prerequisites

- [[q-primitive-vs-reference-types--programming-languages--easy]] - Understanding references
- [[q-reference-types-criteria--programming-languages--medium]] - Reference types in depth

### Related

- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Detecting coroutine leaks
- `Activity` lifecycle and proper cleanup
- RecyclerView memory efficiency patterns

### Advanced

- [[q-coroutine-memory-leaks--kotlin--hard]] - `Coroutine`-specific memory leaks
- [[q-find-object-without-references--programming-languages--medium]] - Advanced GC behavior
