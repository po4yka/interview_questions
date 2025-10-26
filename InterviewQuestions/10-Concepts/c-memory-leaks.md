---
id: "20251025-120400"
title: "Memory Leaks / Утечки памяти"
aliases: ["Memory Leaks", "Memory Leak", "Android Memory Leaks", "Утечки памяти", "Утечка памяти"]
summary: "Situations where objects remain in memory longer than necessary due to unintended references, preventing garbage collection and causing performance issues"
topic: "android"
subtopics: ["memory-leaks", "performance", "memory-management", "debugging", "profiling"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-25"
updated: "2025-10-25"
tags: ["concept", "android", "memory-leaks", "performance", "memory-management", "debugging", "profiling"]
---

# Memory Leaks / Утечки памяти

## Summary (EN)

A memory leak occurs when an object that is no longer needed remains in memory because it is still being referenced, preventing the garbage collector from reclaiming that memory. In Android, memory leaks commonly happen when long-lived objects hold references to short-lived objects like Activities, Fragments, or Views. This leads to increased memory consumption, performance degradation, and potentially OutOfMemoryError crashes. Understanding common leak patterns and detection techniques is essential for building stable Android applications.

## Краткое описание (RU)

Утечка памяти происходит, когда объект, который больше не нужен, остается в памяти, потому что на него все еще есть ссылки, что не позволяет сборщику мусора освободить эту память. В Android утечки памяти обычно происходят, когда долгоживущие объекты содержат ссылки на короткоживущие объекты, такие как Activity, Fragment или View. Это приводит к увеличению потребления памяти, снижению производительности и потенциально к сбоям OutOfMemoryError. Понимание распространенных паттернов утечек и методов обнаружения необходимо для создания стабильных Android приложений.

## Key Points (EN)

- Memory leaks prevent garbage collector from freeing unused memory
- Common causes: static references, inner classes, listeners, handlers, threads
- Context leaks are the most common type in Android applications
- Tools like LeakCanary, Android Profiler help detect and diagnose leaks
- ViewModels should never hold references to Views, Activities, or Fragments
- Always unregister listeners, callbacks, and observers in lifecycle methods
- Handlers and AsyncTasks can cause leaks if not handled properly

## Ключевые моменты (RU)

- Утечки памяти не позволяют сборщику мусора освобождать неиспользуемую память
- Частые причины: статические ссылки, внутренние классы, слушатели, handlers, потоки
- Утечки Context - самый распространенный тип в Android приложениях
- Инструменты, такие как LeakCanary, Android Profiler, помогают обнаруживать утечки
- ViewModel никогда не должны содержать ссылки на View, Activity или Fragment
- Всегда отписывайтесь от listeners, callbacks и observers в методах жизненного цикла
- Handlers и AsyncTasks могут вызывать утечки, если не обрабатывать их правильно

## Common Memory Leak Patterns

### 1. Static References to Activity/Context

**Problem**:
```kotlin
// WRONG - Memory leak!
class MyActivity : AppCompatActivity() {
    companion object {
        private var activity: Activity? = null // Static reference
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        activity = this // Leaks the Activity
    }
}
```

**Solution**:
```kotlin
// CORRECT - Use Application Context for static references
class MyManager {
    companion object {
        private var appContext: Context? = null

        fun init(context: Context) {
            appContext = context.applicationContext // Safe
        }
    }
}
```

### 2. Non-Static Inner Classes

**Problem**:
```kotlin
// WRONG - Inner class holds implicit reference to outer Activity
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // This thread will leak the Activity
        MyThread().start()
    }

    inner class MyThread : Thread() {
        override fun run() {
            // Long-running operation
            Thread.sleep(10000)
            // Implicitly holds reference to MyActivity
        }
    }
}
```

**Solution**:
```kotlin
// CORRECT - Use static inner class or separate class
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        MyThread().start()
    }

    class MyThread : Thread() {
        override fun run() {
            Thread.sleep(10000)
            // No reference to Activity
        }
    }
}

// Or use WeakReference if you need the Activity
class MyThread(activity: MyActivity) : Thread() {
    private val activityRef = WeakReference(activity)

    override fun run() {
        Thread.sleep(10000)
        activityRef.get()?.runOnUiThread {
            // Update UI if Activity still exists
        }
    }
}
```

### 3. Listeners and Callbacks

**Problem**:
```kotlin
// WRONG - Listener not unregistered
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        SomeManager.addListener(object : SomeListener {
            override fun onEvent() {
                // This holds reference to Activity
                updateUI()
            }
        })
        // Forgot to remove listener!
    }

    private fun updateUI() { /* ... */ }
}
```

**Solution**:
```kotlin
// CORRECT - Always unregister listeners
class MyActivity : AppCompatActivity() {
    private val listener = object : SomeListener {
        override fun onEvent() {
            updateUI()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        SomeManager.addListener(listener)
    }

    override fun onDestroy() {
        super.onDestroy()
        SomeManager.removeListener(listener)
    }

    private fun updateUI() { /* ... */ }
}
```

### 4. Handler Leaks

**Problem**:
```kotlin
// WRONG - Handler holds implicit reference to Activity
class MyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper()) {
        // Long-delayed message
        true
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.sendEmptyMessageDelayed(0, 60000) // 1 minute delay
        // If Activity is destroyed, handler still holds reference
    }
}
```

**Solution**:
```kotlin
// CORRECT - Use static Handler with WeakReference
class MyActivity : AppCompatActivity() {
    private val handler = MyHandler(this)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.sendEmptyMessageDelayed(0, 60000)
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null) // Clear all messages
    }

    class MyHandler(activity: MyActivity) : Handler(Looper.getMainLooper()) {
        private val activityRef = WeakReference(activity)

        override fun handleMessage(msg: Message) {
            activityRef.get()?.let { activity ->
                // Handle message if Activity still exists
            }
        }
    }
}

// Or better, use coroutines with lifecycle scope
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            delay(60000)
            // Automatically cancelled when Activity is destroyed
            updateUI()
        }
    }
}
```

### 5. Anonymous Classes in Async Operations

**Problem**:
```kotlin
// WRONG - AsyncTask holds reference to Activity
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        object : AsyncTask<Void, Void, String>() {
            override fun doInBackground(vararg params: Void?): String {
                Thread.sleep(10000)
                return "Result"
            }

            override fun onPostExecute(result: String) {
                // Holds reference to Activity
                textView.text = result
            }
        }.execute()
    }
}
```

**Solution**:
```kotlin
// CORRECT - Use coroutines with lifecycle scope
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val result = withContext(Dispatchers.IO) {
                delay(10000)
                "Result"
            }
            // Automatically cancelled if Activity is destroyed
            textView.text = result
        }
    }
}

// Or use ViewModel
class MyViewModel : ViewModel() {
    private val _result = MutableLiveData<String>()
    val result: LiveData<String> = _result

    fun loadData() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                delay(10000)
                "Result"
            }
            _result.value = data
        }
    }
}
```

### 6. LiveData/Flow Observers

**Problem**:
```kotlin
// WRONG - Observing with wrong lifecycle owner
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Using 'this' instead of viewLifecycleOwner
        viewModel.data.observe(this) { data ->
            updateView(data) // May access destroyed view
        }
    }
}
```

**Solution**:
```kotlin
// CORRECT - Use viewLifecycleOwner in Fragments
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.data.observe(viewLifecycleOwner) { data ->
            updateView(data) // Safe
        }
    }
}
```

### 7. Singleton Holding Context

**Problem**:
```kotlin
// WRONG - Singleton holds Activity context
class DatabaseManager private constructor(private val context: Context) {
    companion object {
        @Volatile
        private var instance: DatabaseManager? = null

        fun getInstance(context: Context): DatabaseManager {
            return instance ?: synchronized(this) {
                instance ?: DatabaseManager(context).also { instance = it }
            }
        }
    }
}

// Usage in Activity
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        DatabaseManager.getInstance(this) // Leaks Activity!
    }
}
```

**Solution**:
```kotlin
// CORRECT - Use Application context in Singleton
class DatabaseManager private constructor(context: Context) {
    private val appContext = context.applicationContext

    companion object {
        @Volatile
        private var instance: DatabaseManager? = null

        fun getInstance(context: Context): DatabaseManager {
            return instance ?: synchronized(this) {
                instance ?: DatabaseManager(
                    context.applicationContext // Use Application context
                ).also { instance = it }
            }
        }
    }
}
```

## Detection Tools

### LeakCanary

```kotlin
// build.gradle
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
}

// Automatically detects leaks in debug builds
// Shows notification when leak is detected
```

### Android Profiler

1. Open Android Studio Profiler
2. Select Memory profiler
3. Perform actions that might leak memory
4. Trigger garbage collection
5. Dump heap and analyze objects
6. Look for unexpected instances of Activities/Fragments

### Manual Detection with StrictMode

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            StrictMode.setVmPolicy(
                StrictMode.VmPolicy.Builder()
                    .detectLeakedClosableObjects()
                    .detectLeakedRegistrationObjects()
                    .penaltyLog()
                    .build()
            )
        }
    }
}
```

## Use Cases

### When to Watch Out

- **Long-lived objects**: Singletons, application-level managers
- **Background operations**: Threads, coroutines, AsyncTask
- **Event listeners**: Click listeners, broadcast receivers, observers
- **Static references**: Static collections, static variables
- **Inner classes**: Non-static inner classes holding outer class reference
- **Handlers and Runnables**: Delayed or long-running messages
- **Third-party libraries**: Libraries that register callbacks

### Common Scenarios

- Rotating device (configuration change)
- Navigating away from Activity/Fragment
- Background data loading
- Event bus subscriptions
- Sensor listeners
- Location updates
- Network callbacks

## Trade-offs

**Pros of Proper Memory Management**:
- Improved app performance and responsiveness
- Reduced memory consumption
- Fewer crashes due to OutOfMemoryError
- Better user experience
- Longer battery life
- Ability to handle more concurrent operations

**Cons of Ignoring Memory Leaks**:
- Gradual performance degradation over time
- Increased memory pressure on device
- Potential crashes (OutOfMemoryError)
- Wasted resources (battery, CPU)
- Poor app ratings and user complaints
- Difficult to debug in production

## Best Practices

- Use Application Context for long-lived objects (Singletons)
- Always unregister listeners, receivers, and observers
- Prefer static inner classes or separate classes
- Use WeakReference for Activity/View references in background tasks
- Use lifecycle-aware components (ViewModel, LiveData, lifecycleScope)
- Clear Handler messages in onDestroy()
- Use viewLifecycleOwner in Fragments for observers
- Avoid storing Activity/Fragment references in static fields
- Test for leaks during development with LeakCanary
- Profile memory usage regularly with Android Profiler
- Use coroutines with proper scopes instead of AsyncTask
- Be cautious with third-party libraries that require registration

## Prevention Checklist

- [ ] No static references to Activity, Fragment, or View
- [ ] All listeners/callbacks unregistered in onDestroy()
- [ ] Observers use correct lifecycle owner (viewLifecycleOwner in Fragments)
- [ ] Inner classes are static or use WeakReference
- [ ] Handler messages cleared in onDestroy()
- [ ] ViewModel doesn't reference UI components
- [ ] Singletons use Application Context
- [ ] Coroutines use proper lifecycle scopes
- [ ] Background threads don't hold Activity references
- [ ] LeakCanary integrated in debug builds

## Related Concepts

- [[c-lifecycle]]
- [[c-garbage-collection]]
- [[c-weak-reference]]
- [[c-viewmodel]]
- [[c-lifecycle-aware-components]]
- [[c-profiling]]
- [[c-leakcanary]]
- [[c-context]]

## References

- [Android Developer Guide: Memory Management](https://developer.android.com/topic/performance/memory)
- [Avoiding Memory Leaks](https://developer.android.com/topic/performance/memory-overview)
- [LeakCanary Documentation](https://square.github.io/leakcanary/)
- [Android Profiler Guide](https://developer.android.com/studio/profile/memory-profiler)
- [Common Memory Leak Patterns](https://medium.com/androiddevelopers/nine-ways-to-avoid-memory-leaks-in-android-b6d81648e35e)
