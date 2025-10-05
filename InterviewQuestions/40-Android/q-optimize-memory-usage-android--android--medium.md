---
tags:
  - android
  - memory-optimization
  - performance
  - weakreference
  - lrucache
  - glide
  - easy_kotlin
  - android/memory-management
  - android/performance
  - memory-management
  - optimization
difficulty: medium
---

# Как оптимизировать использование памяти в приложении?

**English**: How to optimize memory usage in an application?

## Answer

**1. Minimize Static Variables**

```kotlin
// ❌ BAD - Static reference leaks
companion object {
    var context: Context? = null
    val userList = mutableListOf<User>()  // Never released
}

// ✅ GOOD - Use application context or avoid statics
companion object {
    lateinit var appContext: Context  // Application context OK
}
```

**2. Avoid Memory Leaks**

Properly manage references to contexts and activities.

```kotlin
// ❌ BAD - Activity leak
class MyTask(private val activity: Activity) : AsyncTask<>() {
    // Holds Activity reference
}

// ✅ GOOD - Use WeakReference
class MyTask(activity: Activity) : AsyncTask<>() {
    private val activityRef = WeakReference(activity)

    override fun doInBackground() {
        activityRef.get()?.let { activity ->
            // Safe access
        }
    }
}
```

**3. Use WeakReference for Large Objects**

```kotlin
class ImageCache {
    private val cache = mutableMapOf<String, WeakReference<Bitmap>>()

    fun put(key: String, bitmap: Bitmap) {
        cache[key] = WeakReference(bitmap)
    }

    fun get(key: String): Bitmap? {
        return cache[key]?.get()
    }
}
```

**4. Avoid Inner Classes in Activity**

Replace with static nested classes.

```kotlin
// ❌ BAD - Implicit Activity reference
class MyActivity : AppCompatActivity() {
    inner class MyRunnable : Runnable {
        override fun run() {
            // Holds MyActivity reference
        }
    }
}

// ✅ GOOD - Static nested class
class MyActivity : AppCompatActivity() {
    class MyRunnable(private val activityRef: WeakReference<MyActivity>) : Runnable {
        override fun run() {
            activityRef.get()?.let {
                // Use activity
            }
        }
    }
}
```

**5. Use LruCache for Memory Caching**

```kotlin
class DataCache {
    // Cache up to 4MB of data
    private val maxMemory = (Runtime.getRuntime().maxMemory() / 1024).toInt()
    private val cacheSize = maxMemory / 8

    private val lruCache = object : LruCache<String, Bitmap>(cacheSize) {
        override fun sizeOf(key: String, bitmap: Bitmap): Int {
            return bitmap.byteCount / 1024  // Size in KB
        }
    }

    fun putBitmap(key: String, bitmap: Bitmap) {
        lruCache.put(key, bitmap)
    }

    fun getBitmap(key: String): Bitmap? {
        return lruCache.get(key)
    }
}
```

**6. Profile with Android Studio Profiler**

```kotlin
// Monitor memory in real-time
// Android Studio → View → Tool Windows → Profiler
// Memory tab → Track allocations
```

**7. Use LeakCanary**

```kotlin
// build.gradle
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
}

// Automatically detects leaks in debug builds
```

**8. Use Glide or Picasso for Images**

```kotlin
// ✅ Glide - automatic memory management
Glide.with(context)
    .load(imageUrl)
    .placeholder(R.drawable.placeholder)
    .into(imageView)

// ✅ Picasso - similar benefits
Picasso.get()
    .load(imageUrl)
    .resize(800, 600)  // Optimize size
    .centerCrop()
    .into(imageView)
```

**9. Manage Large Objects**

```kotlin
// Load images at optimal size
fun decodeSampledBitmapFromResource(
    res: Resources,
    resId: Int,
    reqWidth: Int,
    reqHeight: Int
): Bitmap {
    return BitmapFactory.Options().run {
        inJustDecodeBounds = true
        BitmapFactory.decodeResource(res, resId, this)

        // Calculate inSampleSize
        inSampleSize = calculateInSampleSize(this, reqWidth, reqHeight)

        inJustDecodeBounds = false
        BitmapFactory.decodeResource(res, resId, this)
    }
}

fun calculateInSampleSize(
    options: BitmapFactory.Options,
    reqWidth: Int,
    reqHeight: Int
): Int {
    val (height: Int, width: Int) = options.run { outHeight to outWidth }
    var inSampleSize = 1

    if (height > reqHeight || width > reqWidth) {
        val halfHeight = height / 2
        val halfWidth = width / 2

        while (halfHeight / inSampleSize >= reqHeight &&
            halfWidth / inSampleSize >= reqWidth) {
            inSampleSize *= 2
        }
    }

    return inSampleSize
}
```

**10. Release Resources**

```kotlin
class MyActivity : AppCompatActivity() {
    private var bitmap: Bitmap? = null

    override fun onDestroy() {
        // Release bitmap
        bitmap?.recycle()
        bitmap = null

        super.onDestroy()
    }
}
```

**Memory Optimization Checklist:**

| Practice | Description |
|----------|-------------|
| ✅ Avoid statics | Or use application context only |
| ✅ Fix leaks | Use WeakReference, proper cleanup |
| ✅ Use LruCache | For in-memory caching |
| ✅ Optimize images | Load at required size |
| ✅ Use image libraries | Glide, Picasso, Coil |
| ✅ Profile regularly | Android Profiler, LeakCanary |
| ✅ Release resources | onDestroy, onPause |
| ✅ Avoid inner classes | Use static nested + WeakReference |

**Summary:**

- Minimize static variables
- Avoid memory leaks with proper reference management
- Use WeakReference for large objects
- Replace inner classes with static nested classes
- Use LruCache for caching
- Profile with Android Studio Profiler and LeakCanary
- Use Glide/Picasso for images
- Load images at optimal size

## Ответ

Минимизируйте использование статических переменных. Избегайте утечек памяти, правильно управляя ссылками на контексты и активности. Используйте слабые ссылки (WeakReference) для больших объектов. Избегайте внутренних классов в Activity, заменяя их статическими вложенными классами. Применяйте LruCache для кэширования данных в памяти. Профилируйте приложение с помощью Android Studio Profiler и LeakCanary. Используйте Glide или Picasso для загрузки и кэширования изображений. Управляйте крупными объектами и загружайте изображения оптимального размера.

