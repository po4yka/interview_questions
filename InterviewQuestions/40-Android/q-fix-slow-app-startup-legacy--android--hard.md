---
id: android-271
title: Fix Slow App Startup Legacy / Исправление медленного запуска приложения
aliases:
- Fix Slow App Startup in Legacy Project
- Исправление медленного запуска приложения в легаси-проекте
topic: android
subtopics:
- architecture-modularization
- monitoring-slo
- performance-startup
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-app-startup
- q-android-performance-measurement-tools--android--medium
- q-app-startup-library--android--medium
- q-app-startup-optimization--android--medium
- q-macrobenchmark-startup--android--medium
- q-what-are-services-used-for--android--medium
sources:
- https://developer.android.com/topic/performance/baselineprofiles/overview
- https://developer.android.com/topic/performance/vitals/launch-time
anki_cards:
- slug: android-271-0-en
  language: en
  anki_id: 1768367158606
  synced_at: '2026-01-14T09:17:53.383541'
- slug: android-271-0-ru
  language: ru
  anki_id: 1768367158630
  synced_at: '2026-01-14T09:17:53.385554'
created: 2025-10-15
updated: 2025-11-11
tags:
- android/architecture-modularization
- android/monitoring-slo
- android/performance-startup
- app-startup
- difficulty/hard
- lazy-init
- legacy-code
- optimization
---
# Вопрос (RU)

> Что делать, если нужно исправить медленный запуск приложения в legacy-проекте?

# Question (EN)

> How would you approach fixing slow app startup in a legacy Android project?

## Ответ (RU)

**Подход:** Систематическая оптимизация с измеримыми результатами через профилирование, отложенную инициализацию и архитектурные улучшения.

## Answer (EN)

**Approach:** Systematic optimization with measurable results through profiling, deferred initialization, and architectural improvements.

## Follow-ups

- How would you profile startup on devices without developer options enabled?
- What trade-offs exist between App Startup library and manual initialization?
- How do you measure startup performance in CI/CD pipeline?
- What's the impact of ProGuard/R8 optimization on startup time?
- How would you prioritize initialization for 20+ SDKs in `Application.onCreate()`?

## References

- Android Baseline Profiles documentation
- Macrobenchmark library guide
- "https://developer.android.com/topic/performance/vitals/launch-time"
- "https://developer.android.com/topic/performance/baselineprofiles/overview"

## Related Questions

### Prerequisites / Concepts

- [[c-app-startup]]
- [[q-android-performance-measurement-tools--android--medium]]

### Prerequisites

- [[q-what-are-services-used-for--android--medium]] - Understanding Android components

### Related

- [[q-android-performance-measurement-tools--android--medium]] - Profiling and measurement tools

## Краткая Версия
Оптимизируйте запуск legacy Android приложения: профилируйте bottleneck'ы, перенесите тяжелую инициализацию в фон, используйте lazy loading и Baseline Profiles для ощутимого (типично 15–30%+) улучшения производительности холодного старта на целевых устройствах.
## Подробная Версия
Систематически оптимизируйте медленный запуск legacy Android приложения:
**Профилирование:**
- Используйте Android Studio Profiler и системную трассировку (Perfetto / System Tracing) для выявления узких мест
- Измерьте холодный/тёплый/горячий старт; ориентиры (а не жёсткие требования): холодный <2с, тёплый <1с, горячий <500мс (на целевых устройствах и для вашего кейса)
**Оптимизация инициализации:**
- Перенесите тяжёлые операции из `Application.onCreate()` в фоновые потоки или отложенный запуск
- Используйте Jetpack App Startup для декларативной инициализации компонентов и управления зависимостями
- Примените отложенную инициализацию (lazy initialization) через dependency injection и ленивый доступ, следя за тем, чтобы тяжёлые операции не выполнялись синхронно на UI-потоке
**Архитектурные улучшения:**
- Разбейте монолитную инициализацию на независимые модули с явными зависимостями
- Используйте Baseline Profiles для AOT-компиляции критических путей запуска
- Реализуйте постепенный rollout оптимизаций с измерением метрик
### Требования
**Функциональные:**
- Приложение должно отображать первый интерактивный экран без ошибок и неполадок инициализации.
- Критические сервисы (логирование, краш-репортинг, безопасность) должны быть корректно инициализированы.
**Нефункциональные:**
- Сократить время холодного старта до приемлемых значений для целевых устройств и продуктовых требований.
- Обеспечить стабильность и предсказуемость старта (без ANR, без долгих «белых экранов»).
- Гарантировать возможность измерения и мониторинга метрик старта в dev/prod.
### Архитектура
- Вынесение тяжёлой инициализации из `Application.onCreate()` и экранов первого показа в отдельные компоненты и фоновые задачи.
- Использование Jetpack App Startup для декларативного описания зависимостей и порядка инициализации.
- Применение DI для ленивой загрузки зависимостей и разделения зон ответственности, с контролем того, где именно происходит тяжёлая работа.
- Интеграция Baseline Profiles и macrobenchmark-тестов как части сборочного конвейера.
### Теоретические Основы
**Типы запуска приложения:**
- **Холодный старт** — приложение запускается с нуля: процесс отсутствует, происходит полная инициализация.
- **Тёплый старт** — приложение уже было запущено; возможны варианты (процесс ещё жив или был пересоздан), часть ресурсов/данных уже прогружена или кеширована, и требуется меньше работы, чем при холодном старте.
- **Горячий старт** — активность возвращается на экран из background при живом процессе, как правило без значительной реконструкции состояния и без пересоздания процесса.
**Критические факторы производительности:**
- **`Application.onCreate()`** — выполняется в UI-потоке; должен содержать только критические инициализации, минимальные по времени.
- **Lazy initialization** — отложенная загрузка компонентов при первом реальном обращении вместо запуска "всё сразу"; при этом нужно избегать запуска тяжёлых операций синхронно на главном потоке.
- **Baseline Profiles** — профили для предкомпиляции критических путей, способные дать значимое улучшение холодного старта.
- **App Startup library** — декларативное управление порядком инициализации компонентов и их зависимостей.
**1. Профилирование и анализ**
Используйте Android Studio Profiler и системную трассировку (Perfetto / System Tracing) для выявления узких мест; при необходимости можно анализировать трассы уровня платформы.
```kotlin
// ✅ Трассировка критических участков (для debug/benchmark сборок с включёнными trace tag'ами)
Trace.beginSection("DatabaseInit")
initDatabase()
Trace.endSection()
// ✅ Macrobenchmark для точных измерений (MacrobenchmarkRule / JUnit Rule)
@Test
fun startupBenchmark() = benchmarkRule.measureRepeated(
    packageName = "com.example.app",
    metrics = listOf(StartupTimingMetric()),
    iterations = 5
) {
    pressHome()
    startActivityAndWait()
}
```
Анализируйте метрики: холодный, тёплый, горячий старт на разных девайсах и сборках. Целевые значения задавайте под свои UX-требования и класс устройств (часто: холодный < 2 сек, тёплый < 1 сек).
**2. Оптимизация `Application.onCreate()`**
Критично: синхронно инициализируются только crash reporting / logging, критические security-настройки и минимальный набор необходимых зависимостей для первого экрана.
```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // ✅ Только критическое
        FirebaseCrashlytics.getInstance().setCrashlyticsCollectionEnabled(true)
        // ❌ Плохо: блокирует UI-поток при старте
        // initDatabase()
        // initNetworking()
        // ✅ Декларативная инициализация через App Startup (пример)
        // Остальные Initializer'ы регистрируются в манифесте и будут выполнены фреймворком
    }
}
```
**3. Jetpack App Startup + Lazy Init**
Используйте App Startup для управления порядком инициализации компонентов и явного описания зависимостей. Не инициируйте компоненты вручную, если за вас это делает библиотека (например, `WorkManager`).
```kotlin
class NetworkInitializer : Initializer<ApiClient> {
    override fun create(context: Context): ApiClient {
        return ApiClient.Builder()
            .baseUrl(BuildConfig.API_URL)
            .build()
    }
    override fun dependencies() = emptyList<Class<Initializer<*>>>()
}
// ✅ Ленивая инициализация через DI (например, Hilt)
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideDatabase(app: Application): AppDatabase =
        Room.databaseBuilder(app, AppDatabase::class.java, "db")
            .build() // Экземпляр создаётся при первом запросе зависимости; убедитесь, что тяжёлая работа не выполняется синхронно на UI-потоке.
}
```
**4. Оптимизация запуска `Activity`**
Перенесите тяжёлую работу из `Activity.onCreate()` в `ViewModel` / фоновый поток, не блокируя построение первого кадра UI.
```kotlin
// ❌ Плохо: блокирует onCreate
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        loadUserData() // Синхронная тяжёлая операция!
    }
}
// ✅ Хорошо: асинхронно во ViewModel
class MainViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {
    val userData = repository.getUserDataFlow()
        .stateIn(viewModelScope, SharingStarted.Lazily, null)
}
```
**5. Baseline Profiles**
Используйте Baseline Profiles для предкомпиляции критических путей (например, запуск, первый экран). В современных проектах это настраивается через отдельный baseline profile модуль / Gradle-плагин; профили генерируются Macrobenchmark-тестами или пишутся вручную.
Пример фрагмента профиля (упрощённый, только для иллюстрации формата, не реальный код Kotlin):
```text
# baseline-prof.txt (упрощённый пример записи методов, синтаксис может отличаться в зависимости от формата/proguard mapping)
HSPLcom/example/app/MainActivity;-><init>()V
HSPLcom/example/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
```
Эффект: ускорение холодного старта за счёт предкомпиляции часто используемых путей (типично двузначный прирост, но зависит от приложения и устройств).
### Лучшие Практики
- **Измеряйте до и после** — устанавливайте baseline-метрики перед оптимизациями.
- **Постепенные изменения** — внедряйте оптимизации поэтапно для изоляции эффектов.
- **Профилируйте на целевых устройствах** — учитывайте реальные девайсы и версии Android; Baseline Profiles применяются движком ART на поддерживаемых версиях.
- **Мониторьте в production** — отслеживайте startup-метрики после релиза.
- **Используйте App Startup** — чтобы явно управлять зависимостями инициализации компонентов вместо хаотичного кода в `Application.onCreate()`.
### Типичные Ошибки
- **Блокировка UI-потока в onCreate()** — приводит к ANR и плохому UX.
- **Инициализация всего сразу** — монолитная загрузка всех компонентов при старте.
- **Отсутствие baseline-измерений** — невозможно оценить эффективность оптимизаций.
- **Игнорирование warm/hot стартов** — фокус только на cold start.
- **Ручная инициализация без явных зависимостей** — race conditions и неправильный порядок инициализации.
## Short Version
Optimize legacy Android app startup: profile bottlenecks, move heavy initialization to background or defer it, use lazy loading and Baseline Profiles for a noticeable (typically 15–30%+) cold-start performance improvement on your target devices.
## Detailed Version
Systematically optimize slow startup in a legacy Android application:
**Profiling:**
- Use Android Studio Profiler and system tracing (Perfetto / System Tracing) to identify bottlenecks
- Measure cold/warm/hot start; treat targets (cold <2s, warm <1s, hot <500ms) as guidelines rather than hard rules, based on your target devices and UX
**Initialization Optimization:**
- Move heavy operations from `Application.onCreate()` to background threads or deferred execution
- Use Jetpack App Startup for declarative component initialization and dependency management
- Apply lazy initialization through dependency injection and on-demand access, ensuring heavy work is not done synchronously on the main thread
**Architectural Improvements:**
- Break monolithic initialization into independent modules with explicit dependencies
- Use Baseline Profiles for AOT compilation of critical startup paths
- Implement gradual rollout of optimizations with metrics measurement
### Requirements
**Functional:**
- App must show the first interactive screen reliably without initialization failures.
- Critical services (logging, crash reporting, security) must be properly initialized.
**Non-functional:**
- Reduce cold start time to acceptable values for target devices and product requirements.
- Ensure stable and predictable startup (no ANRs, no long blank screens).
- Ensure startup performance metrics can be measured and monitored in dev/prod.
### Architecture
- Move heavy initialization out of `Application.onCreate()` and first-screen code into dedicated components and background tasks.
- Use Jetpack App Startup to declaratively describe dependencies and initialization order.
- Use DI for lazy-loaded dependencies and clear separation of concerns, while controlling where heavy work runs.
- Integrate Baseline Profiles and macrobenchmark tests into the build pipeline.
### Theoretical Foundations
**App startup types:**
- **Cold start** — app launches from scratch with no existing process; full initialization is required.
- **Warm start** — app was previously launched; some state/resources are retained (process may be kept or recreated), so less work is needed compared to a cold start.
- **Hot start** — activity comes back to foreground from background with an alive process, typically without significant reconstruction and without process recreation.
**Critical performance factors:**
- **`Application.onCreate()`** — runs on the UI thread and should contain only minimal critical initializations.
- **Lazy initialization** — defer component initialization until first real use instead of doing everything at startup; avoid triggering heavy work synchronously on the main thread when the dependency is first requested.
- **Baseline Profiles** — profiles for precompilation of critical paths that can significantly improve cold start.
- **App Startup library** — declarative management of component initialization order and dependencies.
**1. Profiling and Analysis**
Use Android Studio Profiler and system tracing (Perfetto / System Tracing) to identify bottlenecks; inspect traces when startup time is unclear.
```kotlin
// ✅ Trace critical sections (for debug/benchmark builds with appropriate trace tags enabled)
Trace.beginSection("DatabaseInit")
initDatabase()
Trace.endSection()
// ✅ Macrobenchmark for precise measurements (MacrobenchmarkRule / JUnit Rule)
@Test
fun startupBenchmark() = benchmarkRule.measureRepeated(
    packageName = "com.example.app",
    metrics = listOf(StartupTimingMetric()),
    iterations = 5
) {
    pressHome()
    startActivityAndWait()
}
```
Analyze metrics for cold, warm, and hot starts across devices and builds. `Set` targets based on UX expectations and device class (commonly: cold < 2s, warm < 1s).
**2. Optimize `Application.onCreate()`**
Key rule: initialize synchronously only crash reporting/logging, critical security configuration, and the minimal dependencies required to show the first screen.
```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // ✅ Critical only
        FirebaseCrashlytics.getInstance().setCrashlyticsCollectionEnabled(true)
        // ❌ Bad: blocks UI thread on startup
        // initDatabase()
        // initNetworking()
        // ✅ Use App Startup for declarative initialization (example)
        // Other Initializers are registered in the manifest and executed by the framework.
    }
}
```
**3. Jetpack App Startup + Lazy Init**
Use App Startup to manage component initialization order and define dependencies explicitly. Avoid manual explicit initialization when the library already integrates via its own Initializer (e.g., `WorkManager`).
```kotlin
class NetworkInitializer : Initializer<ApiClient> {
    override fun create(context: Context): ApiClient {
        return ApiClient.Builder()
            .baseUrl(BuildConfig.API_URL)
            .build()
    }
    override fun dependencies() = emptyList<Class<Initializer<*>>>()
}
// ✅ Lazy init via DI (e.g., Hilt)
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideDatabase(app: Application): AppDatabase =
        Room.databaseBuilder(app, AppDatabase::class.java, "db")
            .build() // Instance is created on first actual request; ensure heavy work is not done synchronously on the UI thread when this happens.
}
```
**4. Optimize `Activity` Startup**
Move heavy work out of `Activity.onCreate()` into `ViewModel` / background work so the first frame is rendered quickly.
```kotlin
// ❌ Bad: blocks onCreate
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        loadUserData() // Heavy synchronous operation!
    }
}
// ✅ Good: async in ViewModel
class MainViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {
    val userData = repository.getUserDataFlow()
        .stateIn(viewModelScope, SharingStarted.Lazily, null)
}
```
**5. Baseline Profiles**
Use Baseline Profiles to precompile critical startup paths (e.g., app launch, first screen). In modern setups this is configured via a dedicated baseline profile module / Gradle plugin, with profiles generated by Macrobenchmark tests or authored manually.
Illustrative snippet of a profile entry (simplified, not Kotlin code):
```text
# baseline-prof.txt (simplified example; actual syntax depends on the profile format)
HSPLcom/example/app/MainActivity;-><init>()V
HSPLcom/example/app/MainActivity;->onCreate(Landroid/os/Bundle;)V
```
Effect: improved cold start via precompilation of hot code paths (often double-digit percentage gains, device/app dependent).
### Best Practices
- **Measure before and after** — establish baseline metrics before applying optimizations.
- **Incremental changes** — introduce optimizations gradually to isolate their impact.
- **Profile on target devices** — reflect real devices and Android versions; Baseline Profiles are consumed by ART where supported.
- **Monitor in production** — track startup metrics after release.
- **Use App Startup** — to explicitly manage initialization dependencies instead of uncontrolled logic in `Application.onCreate()`.
### Common Pitfalls
- **Blocking UI thread in onCreate()** — leads to ANRs and poor UX.
- **Initializing everything at once** — monolithic loading of all components at startup.
- **No baseline measurements** — impossible to evaluate effectiveness of optimizations.
- **Ignoring warm/hot starts** — focusing only on cold start.
- **Manual initialization without explicit dependencies** — race conditions and incorrect initialization order.
---