---
id: android-136
title: Performance Optimization Android / Performance Оптимизация Android
aliases: [Performance Optimization Android, Performance Оптимизация Android]
topic: android
subtopics: [performance-battery, performance-memory, performance-rendering]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-memory-management, c-performance, c-power-profiling, q-android-build-optimization--android--medium, q-baseline-profiles-android--android--medium, q-notification-channels-android--android--medium, q-optimize-memory-usage-android--android--medium, q-parsing-optimization-android--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/performance-battery, android/performance-memory, android/performance-rendering, checklist, difficulty/medium, optimization, performance, performance-memory, performance-rendering]

---
# Вопрос (RU)

> Каков комплексный подход к оптимизации производительности Android-приложения? На какие ключевые области сосредоточиться?

# Question (EN)

> What is a comprehensive approach to optimizing Android app performance? What are the key areas to focus on?

---

## Ответ (RU)

Оптимизация производительности требует системного подхода к нескольким критическим областям. Основные направления: запуск приложения, рендеринг UI, управление памятью, работа с сетью и батареей.

### 1. Оптимизация Запуска Приложения

**Целевые ориентиры (примерные)**: cold start около или менее 1000ms, warm start около или менее 500ms для типичных сценариев на целевых устройствах.

```kotlin
class OptimizedApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // ✅ Критическая инициализация на главном потоке
        initializeCrashReporting()

        // ✅ Отложенная инициализация второстепенных компонентов (НЕ через lifecycleScope в Application)
        CoroutineScope(SupervisorJob() + Dispatchers.Default).launch {
            initializeAnalytics()
            initializeAdSDK()
        }

        // ❌ Блокирующие операции I/O
        // loadConfiguration() // Не делать на главном потоке
    }
}

// ✅ Ленивая инициализация компонентов
val database by lazy { Room.databaseBuilder(/* context = ... */).build() }
val imageLoader by lazy { Coil.imageLoader(context) }
```

**Ключевые техники**:
- App Startup library для управления порядком инициализации
- Baseline Profiles для предкомпиляции критического кода
- Стандартный SplashScreen API (Android 12+) и/или windowBackground для сплэш-экрана (избегать отдельной `Activity`)

### 2. Оптимизация UI И Рендеринга

**Целевой ориентир**: 60 FPS (≈16ms на кадр), минимизация jank.

```xml
<!-- ✅ Плоская иерархия с ConstraintLayout (упрощённый пример) -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>

<!-- ❌ Глубокая вложенность (пример, которого стоит избегать) -->
<!--
<LinearLayout>
    <RelativeLayout>
        <FrameLayout>...</FrameLayout>
    </RelativeLayout>
</LinearLayout>
-->

<!-- ✅ ViewStub для условно отображаемых элементов -->
<ViewStub
    android:id="@+id/stub_rarely_used"
    android:layout="@layout/rarely_used" />
```

**Инструменты диагностики**:
- Profile GPU Rendering: выявление просадок FPS
- Debug GPU Overdraw: стремиться к < 2x overdraw
- Layout Inspector: анализ глубины иерархии и лишних перерисовок

### 3. Оптимизация RecyclerView

```kotlin
class OptimizedAdapter : ListAdapter<Item, ViewHolder>(DIFF_CALLBACK) {

    init {
        setHasStableIds(true) // ✅ Используем стабильные ID для более эффективных обновлений
    }

    override fun getItemId(position: Int): Long = getItem(position).id

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
// ✅ Правильная работа с изображениями (использовать разумные размеры)
Glide.with(imageView.context)
    .load(url)
    .override(200, 200) // Пример: целевой размер вместо использования width/height = 0
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

**Инструменты**: LeakCanary для детектирования утечек, `ViewModel` для сохранения данных при пересоздании `Activity`.

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
- Сжатие (gzip автоматически поддерживается в OkHttp)

### 6. Оптимизация Батареи

```kotlin
// ✅ WorkManager с constraints (15 минут — минимальный интервал для PeriodicWorkRequest)
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

    // ✅ Splits для уменьшения размера APK (при необходимости)
    splits {
        abi {
            isEnabled = true
            include("armeabi-v7a", "arm64-v8a")
        }
    }
}
```

**Цель**: минимизировать размер загружаемого артефакта (использовать Android App `Bundle`, WebP/AVIF для изображений, удалять неиспользуемые зависимости). Конкретные пороги (например, 20MB) зависят от домена и функциональности приложения.

### Инструменты Профилирования

- **Android Profiler**: CPU, Memory, Network, Energy
- **Layout Inspector**: анализ UI иерархии в runtime
- **LeakCanary**: автоматическое обнаружение утечек памяти
- **Firebase Performance Monitoring**: метрики в production
- **Perfetto/Systrace**: детальный анализ производительности системы

### Целевые Метрики (ориентиры)

| Метрика     | Хорошо (примерно) | Приемлемо (примерно) |
|-------------|-------------------|----------------------|
| Cold Start  | ≲ 1000ms          | ≲ 1500ms             |
| Frame Rate  | 60 FPS            | > 45 FPS             |
| Память      | зависит от класса устройства и функциональности |
| APK Size    | минимально возможный при сохранении функционала |

---

## Answer (EN)

Performance optimization requires a systematic approach across several critical areas: app startup, UI rendering, memory management, networking, and battery efficiency.

### 1. App Startup Optimization

**Target metrics (guidelines)**: Cold start around or under 1000ms, warm start around or under 500ms for typical scenarios on target devices.

```kotlin
class OptimizedApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // ✅ Critical initialization on main thread only
        initializeCrashReporting()

        // ✅ Defer non-critical initialization (NOT via lifecycleScope in Application)
        CoroutineScope(SupervisorJob() + Dispatchers.Default).launch {
            initializeAnalytics()
            initializeAdSDK()
        }

        // ❌ Blocking I/O operations
        // loadConfiguration() // Don't do on main thread
    }
}

// ✅ Lazy component initialization
val database by lazy { Room.databaseBuilder(/* context = ... */).build() }
val imageLoader by lazy { Coil.imageLoader(context) }
```

**Key techniques**:
- App Startup library for controlling initialization order
- Baseline Profiles for pre-compiling critical code paths
- Standard SplashScreen API (Android 12+) and/or windowBackground for splash (avoid a separate `Activity`)

### 2. UI and Rendering Optimization

**Target guideline**: 60 FPS (≈16ms per frame), minimize jank.

```xml
<!-- ✅ Flat hierarchy with ConstraintLayout (simplified example) -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>

<!-- ❌ Deep nesting (example to avoid) -->
<!--
<LinearLayout>
    <RelativeLayout>
        <FrameLayout>...</FrameLayout>
    </RelativeLayout>
</LinearLayout>
-->

<!-- ✅ ViewStub for conditionally shown views -->
<ViewStub
    android:id="@+id/stub_rarely_used"
    android:layout="@layout/rarely_used" />
```

**Diagnostic tools**:
- Profile GPU Rendering: identify frame drops
- Debug GPU Overdraw: aim for < 2x overdraw
- Layout Inspector: analyze hierarchy depth and unnecessary invalidations

### 3. RecyclerView Optimization

```kotlin
class OptimizedAdapter : ListAdapter<Item, ViewHolder>(DIFF_CALLBACK) {

    init {
        setHasStableIds(true) // ✅ Use stable IDs for more efficient updates
    }

    override fun getItemId(position: Int): Long = getItem(position).id

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
// ✅ Proper image handling (use reasonable target sizes)
Glide.with(imageView.context)
    .load(url)
    .override(200, 200) // Example target size instead of potentially 0 width/height
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

**Tools**: LeakCanary for leak detection, `ViewModel` for retaining data across configuration changes.

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
- Compression (gzip is automatically supported in OkHttp)

### 6. Battery Optimization

```kotlin
// ✅ WorkManager with constraints (15 minutes is the minimum interval for PeriodicWorkRequest)
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

    // ✅ Splits to reduce APK size (if applicable)
    splits {
        abi {
            isEnabled = true
            include("armeabi-v7a", "arm64-v8a")
        }
    }
}
```

**Target**: minimize delivered artifact size (use Android App `Bundle`, WebP/AVIF for images, remove unused dependencies). Exact numbers (e.g., 20MB) depend on app domain and requirements.

### Profiling Tools

- **Android Profiler**: CPU, Memory, Network, Energy
- **Layout Inspector**: analyze UI hierarchy at runtime
- **LeakCanary**: automatic memory leak detection
- **Firebase Performance Monitoring**: production metrics
- **Perfetto/Systrace**: detailed system performance analysis

### Target Metrics (guidelines)

| Metric     | Good (approx.) | Acceptable (approx.) |
|------------|----------------|----------------------|
| Cold Start | ≲ 1000ms       | ≲ 1500ms             |
| Frame Rate | 60 FPS         | > 45 FPS             |
| Memory     | depends on device class and app complexity |
| APK Size   | as small as reasonably possible |

---

## Дополнительные Вопросы (RU)

- Как Baseline Profiles помогают улучшить время запуска?
- Каковы компромиссы между использованием `DiskLruCache` и `DataStore` для кэширования?
- Чем отличается full-mode R8 от стандартной оптимизации?
- Когда стоит использовать `RecyclerView.RecycledViewPool` для вложенных списков?
- Какие метрики влияния на батарею должны стать триггером для оптимизации?

## Follow-ups

- How do Baseline Profiles improve startup performance?
- What are the trade-offs between DiskLruCache and DataStore for caching?
- How does R8 full-mode differ from standard optimization?
- When should you use RecyclerView.RecycledViewPool for nested lists?
- What battery impact metrics should trigger optimization?

## Ссылки (RU)

- [Performance](https://developer.android.com/topic/performance)
- https://developer.android.com/topic/performance/baselineprofiles
- [Profiling](https://developer.android.com/studio/profile)

## References

- [Performance](https://developer.android.com/topic/performance)
- https://developer.android.com/topic/performance/baselineprofiles
- [Profiling](https://developer.android.com/studio/profile)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-memory-management]]
- [[c-power-profiling]]
- [[c-performance]]

### Предпосылки

- Понимание жизненного цикла `Activity` и `Fragment` важно для контекста оптимизации
- Базовые знания `RecyclerView` необходимы для оптимизации списков

### Связанные

- [[q-baseline-profiles-android--android--medium]] — техника оптимизации запуска
- [[q-notification-channels-android--android--medium]] — энергоэффективные уведомления

### Продвинутое

- Реализация пользовательских Lint-правил для контроля практик производительности
- Продвинутые стратегии инициализации с помощью App Startup library

## Related Questions

### Prerequisites / Concepts

- [[c-memory-management]]
- [[c-power-profiling]]
- [[c-performance]]

### Prerequisites

- Understanding `Activity` and `Fragment` lifecycle is essential for optimization context
- RecyclerView fundamentals are required for list optimization

### Related

- [[q-baseline-profiles-android--android--medium]] - Startup optimization technique
- [[q-notification-channels-android--android--medium]] - Battery-efficient notifications

### Advanced

- Implementing custom Lint rules to enforce performance best practices
- Advanced initialization strategies with App Startup library
