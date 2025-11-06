---
id: android-095
title: "LeakCanary Detection Mechanism / Механизм обнаружения LeakCanary"
aliases: ["How LeakCanary Detects Memory Leaks", "LeakCanary Detection Mechanism", "Как LeakCanary обнаруживает утечки памяти", "Механизм обнаружения LeakCanary"]
topic: android
subtopics: [performance-memory, profiling]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-10-31
tags: [android/performance-memory, android/profiling, difficulty/medium, leakcanary, memory-leaks, weakreference]
moc: moc-android
related: [c-memory-leaks, c-memory-management, c-garbage-collection]
sources: []
---

# Вопрос (RU)

> Как LeakCanary обнаруживает утечки памяти?

# Question (EN)

> How does LeakCanary detect memory leaks?

---

## Ответ (RU)

LeakCanary обнаруживает утечки памяти через механизм слабых ссылок (WeakReference) и мониторинг жизненного цикла компонентов.

**Процесс обнаружения:**

**1. Интеграция с жизненным циклом**

LeakCanary автоматически отслеживает уничтожение `Activity` и `Fragment` через lifecycle observers:

```kotlin
class LeakCanaryLifecycleObserver : LifecycleObserver {
 @OnLifecycleEvent(Lifecycle.Event.ON_DESTROY)
 fun onDestroy(owner: LifecycleOwner) {
 AppWatcher.objectWatcher.watch(owner)
 }
}
```

**2. Создание слабой ссылки**

После вызова `onDestroy()` создается WeakReference на объект:

```kotlin
fun watch(watchedObject: Any) {
 val key = UUID.randomUUID().toString()
 val reference = KeyedWeakReference(
 watchedObject,
 key,
 referenceQueue
 )
 watchedObjects[key] = clock.uptimeMillis()
}
```

**3. Проверка после GC**

LeakCanary ждет 5 секунд, запускает сборщик мусора и проверяет, была ли очищена слабая ссылка:

```kotlin
fun checkForLeaks() {
 gcTrigger() // Runtime.getRuntime().gc()

 // Удаляем очищенные ссылки из очереди
 removeWeaklyReachableObjects()

 // Оставшиеся объекты = утечки
 val leakedRefs = watchedObjects.filter { (_, time) ->
 clock.uptimeMillis() - time >= retainedDelayMillis
 }

 if (leakedRefs.isNotEmpty()) {
 dumpHeap() // ✅ Создаем heap dump для анализа
 }
}
```

**Принцип работы WeakReference:**

```kotlin
// ✅ Нормальный случай (нет утечки)
val activity = MyActivity()
val weakRef = WeakReference(activity)
activity = null
System.gc()
weakRef.get() // null - объект собран GC

// ❌ Утечка памяти
companion object {
 var staticRef: Activity? = null // Сильная ссылка!
}
val activity = MyActivity()
staticRef = activity
val weakRef = WeakReference(activity)
activity = null
System.gc()
weakRef.get() // NOT null - staticRef удерживает объект
```

**Архитектура LeakCanary:**

1. **ObjectWatcher** - отслеживает объекты через WeakReference
2. **ReferenceQueue** - получает уведомления об очищенных ссылках
3. **HeapDumper** - создает heap dump при обнаружении утечки
4. **Shark** - анализирует heap dump и строит граф ссылок

**Кастомный мониторинг:**

```kotlin
class MyViewModel : ViewModel() {
 init {
 AppWatcher.objectWatcher.watch(
 this,
 "MyViewModel should be cleared"
 )
 }
}
```

## Answer (EN)

LeakCanary detects memory leaks through weak references (WeakReference) and lifecycle monitoring.

**Detection Process:**

**1. `Lifecycle` Integration**

LeakCanary automatically tracks `Activity` and `Fragment` destruction via lifecycle observers:

```kotlin
class LeakCanaryLifecycleObserver : LifecycleObserver {
 @OnLifecycleEvent(Lifecycle.Event.ON_DESTROY)
 fun onDestroy(owner: LifecycleOwner) {
 AppWatcher.objectWatcher.watch(owner)
 }
}
```

**2. Weak Reference Creation**

After `onDestroy()` is called, a WeakReference is created for the object:

```kotlin
fun watch(watchedObject: Any) {
 val key = UUID.randomUUID().toString()
 val reference = KeyedWeakReference(
 watchedObject,
 key,
 referenceQueue
 )
 watchedObjects[key] = clock.uptimeMillis()
}
```

**3. Post-GC Verification**

LeakCanary waits 5 seconds, triggers garbage collection, and checks if the weak reference was cleared:

```kotlin
fun checkForLeaks() {
 gcTrigger() // Runtime.getRuntime().gc()

 // Remove cleared references from queue
 removeWeaklyReachableObjects()

 // Remaining objects = leaks
 val leakedRefs = watchedObjects.filter { (_, time) ->
 clock.uptimeMillis() - time >= retainedDelayMillis
 }

 if (leakedRefs.isNotEmpty()) {
 dumpHeap() // ✅ Create heap dump for analysis
 }
}
```

**WeakReference Behavior:**

```kotlin
// ✅ Normal case (no leak)
val activity = MyActivity()
val weakRef = WeakReference(activity)
activity = null
System.gc()
weakRef.get() // null - object was collected

// ❌ Memory leak
companion object {
 var staticRef: Activity? = null // Strong reference!
}
val activity = MyActivity()
staticRef = activity
val weakRef = WeakReference(activity)
activity = null
System.gc()
weakRef.get() // NOT null - staticRef holds the object
```

**LeakCanary Architecture:**

1. **ObjectWatcher** - tracks objects via WeakReference
2. **ReferenceQueue** - receives notifications about cleared references
3. **HeapDumper** - creates heap dump when leak is detected
4. **Shark** - analyzes heap dump and builds reference graph

**Custom Monitoring:**

```kotlin
class MyViewModel : ViewModel() {
 init {
 AppWatcher.objectWatcher.watch(
 this,
 "MyViewModel should be cleared"
 )
 }
}
```

---

## Follow-ups

1. What happens if garbage collection doesn't run when `System.gc()` is called?
2. How does LeakCanary distinguish between legitimate retained objects and actual leaks?
3. What is the performance impact of LeakCanary in debug builds?
4. How does the Shark library analyze heap dumps to identify leak causes?
5. Can LeakCanary detect leaks in custom objects beyond `Activity` and `Fragment`?

## References

- [[c-memory-management]] - Memory management fundamentals
- [[c-garbage-collection]] - Garbage collection concepts
- - Weak reference patterns
- https://square.github.io/leakcanary/ - Official LeakCanary documentation

## Related Questions

### Prerequisites (Easier)
- [[q-leakcanary-library--android--easy]] - LeakCanary library introduction
- [[q-memory-leaks-definition--android--easy]] - Memory leak fundamentals
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Threading basics

### Related (Same Level)
- [[q-leakcanary-heap-dump-analysis--android--medium]] - Analyzing heap dumps
- [[q-memory-leak-detection--android--medium]] - Leak detection strategies
- [[q-android-performance-measurement-tools--android--medium]] - Profiling tools
- [[q-memory-leak-vs-oom-android--android--medium]] - Memory issues comparison

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - Runtime memory management
- [[q-fix-slow-app-startup-legacy--android--hard]] - App performance tuning
- [[q-observability-sdk--android--hard]] - Production monitoring
