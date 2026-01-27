---
id: android-747
title: Baseline Profiles and Macrobenchmark / Baseline Profiles и Macrobenchmark
aliases:
- Baseline Profiles
- Macrobenchmark Library
- Baseline Profiles и Macrobenchmark
topic: android
subtopics:
- performance
- startup
- aot-compilation
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-app-startup-optimization--performance--hard
- q-profiler-tools--performance--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/performance
- android/startup
- difficulty/hard
- baseline-profiles
- macrobenchmark
anki_cards:
- slug: android-747-0-en
  language: en
- slug: android-747-0-ru
  language: ru
---
# Вопрос (RU)

> Что такое Baseline Profiles и Macrobenchmark? Как они улучшают производительность приложения?

# Question (EN)

> What are Baseline Profiles and Macrobenchmark library? How do they improve app performance?

---

## Ответ (RU)

**Baseline Profiles** -- это правила компиляции AOT (Ahead-of-Time), которые сообщают Android, какие методы и классы следует прекомпилировать при установке приложения. Это значительно ускоряет первый запуск и критические пути пользователя.

### Краткий Ответ

- **Baseline Profiles** -- списки критических методов для AOT-компиляции при установке.
- **Macrobenchmark** -- библиотека для измерения реальной производительности (startup, scrolling, анимации).
- Вместе они позволяют как оптимизировать, так и проверять улучшения.

### Подробный Ответ

### Проблема Без Baseline Profiles

Android использует JIT (Just-in-Time) компиляцию по умолчанию. При первом запуске:
1. Код интерпретируется (медленно)
2. JIT постепенно компилирует горячие методы
3. Profile data копится со временем

**Результат**: первые запуски медленные, пользователь видит лаги.

### Как Работают Baseline Profiles

```
Установка APK --> Чтение Baseline Profile --> AOT компиляция
                                                    |
                                                    v
                                           Быстрый первый запуск
```

Profile содержит правила вида:
```
HSPLcom/example/MyActivity;->onCreate(Landroid/os/Bundle;)V
PLcom/example/Repository;->fetchData()Ljava/util/List;
```

- **H** -- Hot method (часто вызывается)
- **S** -- Startup method (вызывается при запуске)
- **P** -- Post-startup method

### Настройка Macrobenchmark Модуля

```kotlin
// build.gradle.kts (macrobenchmark module)
plugins {
    id("com.android.test")
    id("androidx.baselineprofile")
}

android {
    namespace = "com.example.benchmark"
    compileSdk = 35

    defaultConfig {
        minSdk = 24
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    targetProjectPath = ":app"
    experimentalProperties["android.experimental.self-instrumenting"] = true
}

dependencies {
    implementation("androidx.benchmark:benchmark-macro-junit4:1.3.3")
    implementation("androidx.test.ext:junit:1.2.1")
    implementation("androidx.test.uiautomator:uiautomator:2.3.0")
}
```

### Генерация Baseline Profile

```kotlin
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {

    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generateProfile() {
        rule.collect(
            packageName = "com.example.app",
            includeInStartupProfile = true,
            profileBlock = {
                // Запуск приложения
                pressHome()
                startActivityAndWait()

                // Критические пути пользователя
                device.findObject(By.text("Login")).click()
                device.waitForIdle()

                device.findObject(By.res("feed_list")).scroll(Direction.DOWN, 2f)
                device.waitForIdle()
            }
        )
    }
}
```

### Macrobenchmark для Измерения Startup

```kotlin
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {

    @get:Rule
    val rule = MacrobenchmarkRule()

    @Test
    fun startupCompilationNone() = startup(CompilationMode.None())

    @Test
    fun startupCompilationPartial() = startup(
        CompilationMode.Partial(
            baselineProfileMode = BaselineProfileMode.Require
        )
    )

    @Test
    fun startupCompilationFull() = startup(CompilationMode.Full())

    private fun startup(compilationMode: CompilationMode) {
        rule.measureRepeated(
            packageName = "com.example.app",
            metrics = listOf(StartupTimingMetric()),
            compilationMode = compilationMode,
            startupMode = StartupMode.COLD,
            iterations = 10
        ) {
            pressHome()
            startActivityAndWait()
        }
    }
}
```

### Benchmark Прокрутки

```kotlin
@Test
fun scrollPerformance() {
    rule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(
            FrameTimingMetric(),
            TraceSectionMetric("RV OnBind") // Кастомные трейсы
        ),
        compilationMode = CompilationMode.Partial(
            baselineProfileMode = BaselineProfileMode.Require
        ),
        iterations = 5
    ) {
        pressHome()
        startActivityAndWait()

        // Прокрутка списка
        val list = device.findObject(By.res("com.example.app:id/recycler_view"))
        list.setGestureMargin(device.displayWidth / 5)

        repeat(3) {
            list.scroll(Direction.DOWN, 2f)
            device.waitForIdle()
        }
    }
}
```

### Интеграция в CI/CD

```kotlin
// build.gradle.kts (:app)
plugins {
    id("com.android.application")
    id("androidx.baselineprofile")
}

baselineProfile {
    automaticGenerationDuringBuild = true
    saveInSrc = true

    variants {
        create("release") {
            from(project(":macrobenchmark"))
        }
    }
}

dependencies {
    baselineProfile(project(":macrobenchmark"))
}
```

### Типичные Результаты

| Метрика | Без Profile | С Profile | Улучшение |
|---------|-------------|-----------|-----------|
| Cold Start | 850ms | 450ms | 47% |
| Warm Start | 350ms | 200ms | 43% |
| Frame Drops | 15% | 3% | 80% |

### Лучшие Практики

1. **Покрывать критические пути** -- не все методы, только важные
2. **Обновлять регулярно** -- при изменении кода
3. **Тестировать на реальных устройствах** -- эмуляторы не показывают реалистичные данные
4. **Использовать CI** -- автоматическая генерация при релизах

---

## Answer (EN)

**Baseline Profiles** are AOT (Ahead-of-Time) compilation rules that tell Android which methods and classes to pre-compile during app installation. This significantly speeds up first launch and critical user journeys.

### Short Answer

- **Baseline Profiles** -- lists of critical methods for AOT compilation at install time.
- **Macrobenchmark** -- library for measuring real-world performance (startup, scrolling, animations).
- Together they enable both optimizing and verifying improvements.

### Detailed Answer

### Problem Without Baseline Profiles

Android uses JIT (Just-in-Time) compilation by default. On first launch:
1. Code is interpreted (slow)
2. JIT continuously compiles hot methods
3. Profile data accumulates over time

**Result**: first launches are slow, user experiences jank.

### How Baseline Profiles Work

```
APK Install --> Read Baseline Profile --> AOT Compilation
                                               |
                                               v
                                          Fast First Launch
```

Profile contains rules like:
```
HSPLcom/example/MyActivity;->onCreate(Landroid/os/Bundle;)V
PLcom/example/Repository;->fetchData()Ljava/util/List;
```

- **H** -- Hot method (frequently called)
- **S** -- Startup method (called during startup)
- **P** -- Post-startup method

### Macrobenchmark Module Setup

```kotlin
// build.gradle.kts (macrobenchmark module)
plugins {
    id("com.android.test")
    id("androidx.baselineprofile")
}

android {
    namespace = "com.example.benchmark"
    compileSdk = 35

    defaultConfig {
        minSdk = 24
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    targetProjectPath = ":app"
    experimentalProperties["android.experimental.self-instrumenting"] = true
}

dependencies {
    implementation("androidx.benchmark:benchmark-macro-junit4:1.3.3")
    implementation("androidx.test.ext:junit:1.2.1")
    implementation("androidx.test.uiautomator:uiautomator:2.3.0")
}
```

### Generating Baseline Profile

```kotlin
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {

    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generateProfile() {
        rule.collect(
            packageName = "com.example.app",
            includeInStartupProfile = true,
            profileBlock = {
                // Launch app
                pressHome()
                startActivityAndWait()

                // Critical user journeys
                device.findObject(By.text("Login")).click()
                device.waitForIdle()

                device.findObject(By.res("feed_list")).scroll(Direction.DOWN, 2f)
                device.waitForIdle()
            }
        )
    }
}
```

### Macrobenchmark for Startup Measurement

```kotlin
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {

    @get:Rule
    val rule = MacrobenchmarkRule()

    @Test
    fun startupCompilationNone() = startup(CompilationMode.None())

    @Test
    fun startupCompilationPartial() = startup(
        CompilationMode.Partial(
            baselineProfileMode = BaselineProfileMode.Require
        )
    )

    @Test
    fun startupCompilationFull() = startup(CompilationMode.Full())

    private fun startup(compilationMode: CompilationMode) {
        rule.measureRepeated(
            packageName = "com.example.app",
            metrics = listOf(StartupTimingMetric()),
            compilationMode = compilationMode,
            startupMode = StartupMode.COLD,
            iterations = 10
        ) {
            pressHome()
            startActivityAndWait()
        }
    }
}
```

### Scroll Benchmark

```kotlin
@Test
fun scrollPerformance() {
    rule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(
            FrameTimingMetric(),
            TraceSectionMetric("RV OnBind") // Custom traces
        ),
        compilationMode = CompilationMode.Partial(
            baselineProfileMode = BaselineProfileMode.Require
        ),
        iterations = 5
    ) {
        pressHome()
        startActivityAndWait()

        // Scroll the list
        val list = device.findObject(By.res("com.example.app:id/recycler_view"))
        list.setGestureMargin(device.displayWidth / 5)

        repeat(3) {
            list.scroll(Direction.DOWN, 2f)
            device.waitForIdle()
        }
    }
}
```

### CI/CD Integration

```kotlin
// build.gradle.kts (:app)
plugins {
    id("com.android.application")
    id("androidx.baselineprofile")
}

baselineProfile {
    automaticGenerationDuringBuild = true
    saveInSrc = true

    variants {
        create("release") {
            from(project(":macrobenchmark"))
        }
    }
}

dependencies {
    baselineProfile(project(":macrobenchmark"))
}
```

### Typical Results

| Metric | Without Profile | With Profile | Improvement |
|--------|-----------------|--------------|-------------|
| Cold Start | 850ms | 450ms | 47% |
| Warm Start | 350ms | 200ms | 43% |
| Frame Drops | 15% | 3% | 80% |

### Best Practices

1. **Cover critical paths** -- not all methods, only important ones
2. **Update regularly** -- when code changes
3. **Test on real devices** -- emulators don't show realistic data
4. **Use CI** -- automatic generation on releases

---

## Ссылки (RU)

- [Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles)
- [Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview)
- [Jetpack Benchmark](https://developer.android.com/jetpack/androidx/releases/benchmark)

## References (EN)

- [Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles)
- [Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview)
- [Jetpack Benchmark](https://developer.android.com/jetpack/androidx/releases/benchmark)

## Follow-ups (EN)

- How do Startup Profiles differ from Baseline Profiles?
- What is the difference between `CompilationMode.Partial` and `CompilationMode.Full`?
- How to benchmark Jetpack Compose applications?
- What metrics does `FrameTimingMetric` provide?

## Дополнительные Вопросы (RU)

- Чем Startup Profiles отличаются от Baseline Profiles?
- В чём разница между `CompilationMode.Partial` и `CompilationMode.Full`?
- Как бенчмаркить Jetpack Compose приложения?
- Какие метрики предоставляет `FrameTimingMetric`?
