---
topic: android
tags:
  - android
  - android/memory-management
  - debugging
  - leakcanary
  - memory-leaks
  - memory-management
  - weakreference
difficulty: medium
status: draft
---

# Как LeakCanary понимает что произошла утечка памяти?

**English**: How does LeakCanary understand that a memory leak occurred?

## Answer

LeakCanary detects memory leaks through the following process:

**1. Integration with Component Lifecycle**

The tool tracks destruction of Activity and Fragment through observers.

```kotlin
// LeakCanary registers lifecycle observers
class LeakCanaryLifecycleObserver : LifecycleObserver {
    @OnLifecycleEvent(Lifecycle.Event.ON_DESTROY)
    fun onDestroy(owner: LifecycleOwner) {
        // Track destroyed component
        watchObject(owner)
    }
}
```

**2. Create Weak References**

Creates weak references to objects after their destruction.

```kotlin
// Simplified LeakCanary logic
fun watchObject(watchedObject: Any) {
    val key = UUID.randomUUID().toString()
    val watchUptimeMillis = clock.uptimeMillis()

    // Create weak reference
    val reference = KeyedWeakReference(
        watchedObject,
        key,
        queue
    )

    // Store for tracking
    watchedObjects[key] = watchUptimeMillis
}
```

**3. Trigger Garbage Collection and Wait**

```kotlin
// Request GC
private fun gcTrigger() {
    // Suggest garbage collection
    Runtime.getRuntime().gc()

    // Give GC time to run
    Thread.sleep(100)

    // Finalization
    System.runFinalization()
}
```

**4. Check if Weak Reference Was Cleared**

If weak reference is not null after GC, this indicates a memory leak.

```kotlin
// Check if object was collected
fun checkForLeaks() {
    // Trigger GC
    gcTrigger()

    // Remove references that were cleared
    var ref = queue.poll()
    while (ref != null) {
        watchedObjects.remove(ref.key)
        ref = queue.poll()
    }

    // Remaining objects are leaked
    val leakedObjects = watchedObjects.filter { (key, time) ->
        // Object should have been collected by now
        clock.uptimeMillis() - time >= retainedDelayMillis
    }

    if (leakedObjects.isNotEmpty()) {
        // Heap dump for analysis
        dumpHeap()
    }
}
```

**Complete Flow:**

```
1. Activity.onDestroy() called
         ↓
2. LeakCanary creates WeakReference to Activity
         ↓
3. Wait 5 seconds
         ↓
4. Trigger System.gc()
         ↓
5. Check if WeakReference.get() == null
         ↓
    ┌─────┴─────┐
    │           │
   YES         NO
    │           │
    │           ↓
    │      Leak detected!
    │           ↓
    │      Create heap dump
    │           ↓
    │      Analyze with Shark
    ↓
No leak, continue monitoring
```

**Example Detection:**

```kotlin
class MyActivity : AppCompatActivity() {
    companion object {
        // ❌ Static reference causes leak
        var leakedActivity: Activity? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        leakedActivity = this  // Leak!
    }
}

// LeakCanary detection:
// 1. Activity destroyed
// 2. WeakReference created
// 3. GC triggered
// 4. WeakReference.get() != null (Activity not collected)
// 5. Leak detected!
```

**Weak Reference Behavior:**

```kotlin
// Normal case (no leak)
val activity = MyActivity()
val weakRef = WeakReference(activity)

activity = null  // Remove strong reference
System.gc()

weakRef.get()  // null - object was collected ✅

// Leak case
companion object {
    var staticRef: Activity? = null
}

val activity = MyActivity()
staticRef = activity  // Strong reference
val weakRef = WeakReference(activity)

activity = null  // Local reference removed
System.gc()

weakRef.get()  // NOT null - static ref holds it ❌
```

**LeakCanary Setup:**

```kotlin
// build.gradle
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
}

// Automatically initialized in debug builds
// No code needed!
```

**Custom Watching:**

```kotlin
// Watch custom objects
class MyViewModel : ViewModel() {
    init {
        AppWatcher.objectWatcher.watch(
            this,
            "MyViewModel instance"
        )
    }
}
```

**Summary:**

1. **Lifecycle Integration** - Observes Activity/Fragment destruction
2. **Weak References** - Creates WeakReference after destruction
3. **GC Trigger** - Calls System.gc() to attempt collection
4. **Leak Detection** - If WeakReference.get() != null → leak!
5. **Heap Dump** - Creates dump for detailed analysis

## Ответ

LeakCanary понимает, что произошла утечка памяти следующим образом:

1. **Интеграция с жизненным циклом компонентов** - инструмент отслеживает уничтожение Activity и Fragment через наблюдателей
2. **Создание слабых ссылок** на объекты после их уничтожения
3. **Вызов сборки мусора** и ожидание
4. **Проверка** была ли слабая ссылка освобождена сборщиком мусора

Если слабая ссылка не равна null после GC, это указывает на утечку памяти.

