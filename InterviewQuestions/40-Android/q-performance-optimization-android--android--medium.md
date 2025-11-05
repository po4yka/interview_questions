---
id: android-136
title: "Performance Optimization Android / Performance Оптимизация Android"
aliases: ["Performance Optimization Android", "Performance Оптимизация Android"]
topic: android
subtopics: [performance-battery, performance-memory, performance-rendering]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-baseline-profiles-android--android--medium, q-notification-channels-android--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/performance-battery, android/performance-memory, android/performance-rendering, checklist, difficulty/medium, optimization, performance, performance-memory, performance-rendering]
date created: Monday, October 27th 2025, 3:42:23 pm
date modified: Saturday, November 1st 2025, 5:43:33 pm
---

# Вопрос (RU)

> Каков комплексный подход к оптимизации производительности Android-приложения? На какие ключевые области сосредоточиться?

# Question (EN)

> What is a comprehensive approach to optimizing Android app performance? What are the key areas to focus on?

---

## Ответ (RU)

Оптимизация производительности требует системного подхода к нескольким критическим областям. Основные направления: запуск приложения, рендеринг UI, управление памятью, работа с сетью и батареей.

### 1. Оптимизация Запуска Приложения

**Целевые метрики**: Cold start < 1000ms, warm start < 500ms.

```kotlin
class OptimizedApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // ✅ Критическая инициализация на главном потоке
        initializeCrashReporting()

        // ✅ Отложенная инициализация второстепенных компонентов
        lifecycleScope.launch {
            initializeAnalytics()
            initializeAdSDK()
        }

        // ❌ Блокирующие операции I/O
        // loadConfiguration() // Не делать на главном потоке
    }
}

// ✅ Ленивая инициализация компонентов
val database by lazy { Room.databaseBuilder(...).build() }
val imageLoader by lazy { Coil.imageLoader(context) }
```

**Ключевые техники**:
- App Startup library для управления порядком инициализации
- Baseline Profiles для предкомпиляции критического кода
- Splash screen через windowBackground (не отдельная Activity)

### 2. Оптимизация UI И Рендеринга

**Целевая метрика**: 60 FPS (16ms на кадр).

```kotlin
// ✅ Плоская иерархия с ConstraintLayout
<ConstraintLayout>
    <TextView
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent" />
</ConstraintLayout>

// ❌ Глубокая вложенность
// <LinearLayout>
//     <RelativeLayout>
//         <FrameLayout>...</FrameLayout>
//     </RelativeLayout>
// </LinearLayout>

// ✅ ViewStub для условно отображаемых элементов
<ViewStub
    android:id="@+id/stub_rarely_used"
    android:layout="@layout/rarely_used" />
```

**Инструменты диагностики**:
- Profile GPU Rendering: выявление просадок FPS
- Debug GPU Overdraw: цель < 2x overdraw
- Layout Inspector: анализ глубины иерархии (< 10 уровней)

### 3. Оптимизация RecyclerView

```kotlin
class OptimizedAdapter : ListAdapter<Item, ViewHolder>(DIFF_CALLBACK) {

    init {
        setHasStableIds(true) // ✅ Предотвращает лишние пересоздания
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        // ✅ Минимальная работа в onBind
        holder.bind(getItem(position))

        // ❌ Избегать тяжёлых операций
        // holder.loadImageSynchronously() // Блокирует рендер
    }
}

// ✅ Настройка префетча и кэша
recyclerView.apply {
    layoutManager = LinearLayoutManager(context).apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }
    setItemViewCacheSize(20)
}
```

**Для больших списков**: Paging 3 library с инкрементальной загрузкой.

### 4. Управление Памятью

```kotlin
// ✅ Правильная работа с изображениями
Glide.with(imageView.context)
    .load(url)
    .override(imageView.width, imageView.height) // Ресайз под размер View
    .diskCacheStrategy(DiskCacheStrategy.ALL)
    .into(imageView)

// ✅ Bitmap sampling для больших файлов
suspend fun loadLargeBitmap(path: String, reqWidth: Int, reqHeight: Int): Bitmap {
    return withContext(Dispatchers.IO) {
        BitmapFactory.Options().run {
            inJustDecodeBounds = true
            BitmapFactory.decodeFile(path, this)

            inSampleSize = calculateInSampleSize(this, reqWidth, reqHeight)
            inJustDecodeBounds = false

            BitmapFactory.decodeFile(path, this)
        }
    }
}

// ✅ SparseArray для примитивных ключей
val sparse = SparseIntArray() // Вместо HashMap<Int, Int>
```

**Инструменты**: LeakCanary для детектирования утечек, ViewModel для сохранения данных при пересоздании Activity.

### 5. Оптимизация Сети

```kotlin
// ✅ Offline-first архитектура
class Repository(private val api: ApiService, private val dao: ArticleDao) {
    fun getArticles(): Flow<List<Article>> = flow {
        emit(dao.getAllArticles()) // Сначала кэш

        try {
            val fresh = api.getArticles()
            dao.insertAll(fresh)
            emit(dao.getAllArticles())
        } catch (e: Exception) {
            // Продолжаем с кэшированными данными
        }
    }
}

// ✅ Настройка кэша OkHttp
val client = OkHttpClient.Builder()
    .cache(Cache(context.cacheDir, 10L * 1024 * 1024))
    .build()
```

**Ключевые принципы**:
- Кэширование HTTP-ответов
- Пагинация для списков
- Field filtering (запрос только нужных полей)
- Сжатие (gzip автоматически в OkHttp)

### 6. Оптимизация Батареи

```kotlin
// ✅ WorkManager с constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .setConstraints(constraints)
    .build()

// ✅ Оптимизация location updates
fusedLocationClient.requestLocationUpdates(
    LocationRequest.create().apply {
        interval = 60_000 // ✅ 1 минута (не каждую секунду)
        priority = LocationRequest.PRIORITY_BALANCED_POWER_ACCURACY
    },
    locationCallback,
    Looper.getMainLooper()
)
```

### 7. Оптимизация Сборки

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true // ✅ R8 shrinking
            isShrinkResources = true // ✅ Удаление неиспользуемых ресурсов
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    // ✅ Splits для уменьшения размера APK
    splits {
        abi {
            isEnable = true
            include("armeabi-v7a", "arm64-v8a")
        }
    }
}
```

**Цель**: APK < 20MB через Android App Bundle, WebP для изображений, удаление неиспользуемых зависимостей.

### Инструменты Профилирования

- **Android Profiler**: CPU, Memory, Network, Energy
- **Layout Inspector**: анализ UI иерархии в runtime
- **LeakCanary**: автоматическое обнаружение утечек памяти
- **Firebase Performance Monitoring**: метрики в production
- **Perfetto/Systrace**: детальный анализ производительности системы

### Целевые Метрики

| Метрика       | Хорошо   | Приемлемо |
|--------------|----------|-----------|
| Cold Start   | < 1000ms | < 1500ms  |
| Frame Rate   | 60 FPS   | > 45 FPS  |
| Память       | < 100MB  | < 150MB   |
| APK Size     | < 20MB   | < 50MB    |

---

## Answer (EN)

Performance optimization requires a systematic approach across several critical areas: app startup, UI rendering, memory management, networking, and battery efficiency.

### 1. App Startup Optimization

**Target metrics**: Cold start < 1000ms, warm start < 500ms.

```kotlin
class OptimizedApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // ✅ Critical initialization on main thread only
        initializeCrashReporting()

        // ✅ Defer non-critical initialization
        lifecycleScope.launch {
            initializeAnalytics()
            initializeAdSDK()
        }

        // ❌ Blocking I/O operations
        // loadConfiguration() // Don't do on main thread
    }
}

// ✅ Lazy component initialization
val database by lazy { Room.databaseBuilder(...).build() }
val imageLoader by lazy { Coil.imageLoader(context) }
```

**Key techniques**:
- App Startup library for dependency initialization order
- Baseline Profiles for pre-compiling critical code paths
- Splash screen via windowBackground (not a separate Activity)

### 2. UI and Rendering Optimization

**Target metric**: 60 FPS (16ms per frame).

```kotlin
// ✅ Flat hierarchy with ConstraintLayout
<ConstraintLayout>
    <TextView
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent" />
</ConstraintLayout>

// ❌ Deep nesting
// <LinearLayout>
//     <RelativeLayout>
//         <FrameLayout>...</FrameLayout>
//     </RelativeLayout>
// </LinearLayout>

// ✅ ViewStub for conditionally shown views
<ViewStub
    android:id="@+id/stub_rarely_used"
    android:layout="@layout/rarely_used" />
```

**Diagnostic tools**:
- Profile GPU Rendering: identify frame drops
- Debug GPU Overdraw: target < 2x overdraw
- Layout Inspector: analyze hierarchy depth (< 10 levels)

### 3. RecyclerView Optimization

```kotlin
class OptimizedAdapter : ListAdapter<Item, ViewHolder>(DIFF_CALLBACK) {

    init {
        setHasStableIds(true) // ✅ Prevents unnecessary recreations
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        // ✅ Minimal work in onBind
        holder.bind(getItem(position))

        // ❌ Avoid heavy operations
        // holder.loadImageSynchronously() // Blocks rendering
    }
}

// ✅ Configure prefetch and cache
recyclerView.apply {
    layoutManager = LinearLayoutManager(context).apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }
    setItemViewCacheSize(20)
}
```

**For large lists**: Paging 3 library with incremental loading.

### 4. Memory Management

```kotlin
// ✅ Proper image handling
Glide.with(imageView.context)
    .load(url)
    .override(imageView.width, imageView.height) // Resize to View dimensions
    .diskCacheStrategy(DiskCacheStrategy.ALL)
    .into(imageView)

// ✅ Bitmap sampling for large files
suspend fun loadLargeBitmap(path: String, reqWidth: Int, reqHeight: Int): Bitmap {
    return withContext(Dispatchers.IO) {
        BitmapFactory.Options().run {
            inJustDecodeBounds = true
            BitmapFactory.decodeFile(path, this)

            inSampleSize = calculateInSampleSize(this, reqWidth, reqHeight)
            inJustDecodeBounds = false

            BitmapFactory.decodeFile(path, this)
        }
    }
}

// ✅ SparseArray for primitive keys
val sparse = SparseIntArray() // Instead of HashMap<Int, Int>
```

**Tools**: LeakCanary for leak detection, ViewModel for data retention across configuration changes.

### 5. Network Optimization

```kotlin
// ✅ Offline-first architecture
class Repository(private val api: ApiService, private val dao: ArticleDao) {
    fun getArticles(): Flow<List<Article>> = flow {
        emit(dao.getAllArticles()) // Cache first

        try {
            val fresh = api.getArticles()
            dao.insertAll(fresh)
            emit(dao.getAllArticles())
        } catch (e: Exception) {
            // Continue with cached data
        }
    }
}

// ✅ Configure OkHttp cache
val client = OkHttpClient.Builder()
    .cache(Cache(context.cacheDir, 10L * 1024 * 1024))
    .build()
```

**Key principles**:
- HTTP response caching
- Pagination for lists
- Field filtering (request only needed fields)
- Compression (gzip automatic in OkHttp)

### 6. Battery Optimization

```kotlin
// ✅ WorkManager with constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .setConstraints(constraints)
    .build()

// ✅ Optimize location updates
fusedLocationClient.requestLocationUpdates(
    LocationRequest.create().apply {
        interval = 60_000 // ✅ 1 minute (not every second)
        priority = LocationRequest.PRIORITY_BALANCED_POWER_ACCURACY
    },
    locationCallback,
    Looper.getMainLooper()
)
```

### 7. Build Optimization

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true // ✅ R8 shrinking
            isShrinkResources = true // ✅ Remove unused resources
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    // ✅ Splits to reduce APK size
    splits {
        abi {
            isEnable = true
            include("armeabi-v7a", "arm64-v8a")
        }
    }
}
```

**Target**: APK < 20MB via Android App Bundle, WebP for images, remove unused dependencies.

### Profiling Tools

- **Android Profiler**: CPU, Memory, Network, Energy
- **Layout Inspector**: analyze UI hierarchy at runtime
- **LeakCanary**: automatic memory leak detection
- **Firebase Performance Monitoring**: production metrics
- **Perfetto/Systrace**: detailed system performance analysis

### Target Metrics

| Metric       | Good     | Acceptable |
|-------------|----------|------------|
| Cold Start   | < 1000ms | < 1500ms   |
| Frame Rate   | 60 FPS   | > 45 FPS   |
| Memory       | < 100MB  | < 150MB    |
| APK Size     | < 20MB   | < 50MB     |

---

## Follow-ups

- How do Baseline Profiles improve startup performance?
- What are the trade-offs between DiskLruCache and DataStore for caching?
- How does R8 full-mode differ from standard optimization?
- When should you use RecyclerView.RecycledViewPool for nested lists?
- What battery impact metrics should trigger optimization?

## References

- [Performance](https://developer.android.com/topic/performance)
- https://developer.android.com/topic/performance/baselineprofiles
- [Profiling](https://developer.android.com/studio/profile)


## Related Questions

### Prerequisites
- Understanding Activity and Fragment lifecycle is essential for optimization context
- RecyclerView fundamentals are required for list optimization

### Related
- [[q-baseline-profiles-android--android--medium]] - Startup optimization technique
- [[q-notification-channels-android--android--medium]] - Battery-efficient notifications

### Advanced
- Implementing custom Lint rules to enforce performance best practices
- Advanced initialization strategies with App Startup library
