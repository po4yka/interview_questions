---
id: 20251006-000006
title: "How to reduce APK size? / Как уменьшить размер APK?"
aliases: []

# Classification
topic: android
subtopics: [build-optimization, apk-size, performance, resources]
question_kind: practical
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru, android/build-optimization, android/apk-size, android/performance, android/resources, difficulty/medium]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: [proguard-r8, build-optimization, app-bundles]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [en, ru, android/build-optimization, android/apk-size, android/performance, android/resources, difficulty/medium]
---

# Question (EN)

> What techniques can be used to reduce Android APK size?

# Вопрос (RU)

> Какие техники можно использовать для уменьшения размера Android APK?

---

## Answer (EN)

Reducing APK size is crucial for improving download conversion rates, reducing storage requirements, and enhancing user experience. Here are comprehensive techniques:

### 1. Enable Code Shrinking with R8/ProGuard

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'),
                         'proguard-rules.pro'
        }
    }
}
```

**What it does:**

-   Removes unused code (dead code elimination)
-   Removes unused resources
-   Obfuscates code (shorter class/method names)
-   Optimizes bytecode

**Impact:** 20-40% size reduction

### 2. Use Android App Bundle (AAB)

```gradle
android {
    bundle {
        language {
            enableSplit = true
        }
        density {
            enableSplit = true
        }
        abi {
            enableSplit = true
        }
    }
}
```

**What it does:**

-   Google Play generates optimized APKs for each device configuration
-   Users only download resources for their device
-   Dynamic feature modules (on-demand delivery)

**Impact:** 15-35% size reduction compared to universal APK

### 3. Optimize Images and Resources

**Use WebP format:**

```kotlin
// WebP provides better compression than PNG/JPEG
// drawable/image.webp (instead of .png or .jpg)
```

**Vector Drawables:**

```xml
<!-- Use VectorDrawable instead of multiple PNG densities -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#000000"
        android:pathData="M12,2C6.48,2 2,6.48 2,12s4.48,10 10,10..." />
</vector>
```

**Remove unused alternative resources:**

```gradle
android {
    defaultConfig {
        // Keep only specific densities
        resConfigs "en", "ru"  // Languages
        resConfigs "xxhdpi", "xxxhdpi"  // Densities
    }
}
```

**Impact:** 10-30% size reduction

### 4. Reduce Native Libraries

```gradle
android {
    defaultConfig {
        ndk {
            // Include only required ABIs
            abiFilters 'arm64-v8a', 'armeabi-v7a'
        }
    }

    // Or use splits
    splits {
        abi {
            enable true
            reset()
            include 'arm64-v8a', 'armeabi-v7a', 'x86', 'x86_64'
            universalApk false
        }
    }
}
```

**Impact:** Can reduce size by 50% if you're including all ABIs

### 5. Remove Unused Dependencies

```kotlin
// Analyze dependencies
// ./gradlew :app:dependencies

// Use specific modules instead of entire libraries
implementation 'com.google.android.gms:play-services-maps:18.0.0'
// Instead of:
// implementation 'com.google.android.gms:play-services:12.0.0'
```

**Check dependency size:**

```bash
./gradlew :app:analyzeReleaseBundle
```

### 6. Use Lint to Find Unused Resources

```bash
./gradlew lint
```

Check `build/reports/lint-results.html` for unused resources.

### 7. Compress Native Libraries

```gradle
android {
    packagingOptions {
        // Compress native libraries
        jniLibs {
            useLegacyPackaging = false
        }
    }
}
```

### 8. Remove Duplicate Resources

```gradle
android {
    packagingOptions {
        resources {
            // Exclude duplicate files
            excludes += '/META-INF/{AL2.0,LGPL2.1}'
            excludes += '/META-INF/DEPENDENCIES'
        }
    }
}
```

### 9. Use Dynamic Feature Modules

```kotlin
// Install on-demand
val request = SplitInstallRequest.newBuilder()
    .addModule("dynamic_feature")
    .build()

splitInstallManager.startInstall(request)
```

### 10. Optimize Build Configuration

```gradle
android {
    buildTypes {
        release {
            // Optimize for size
            minifyEnabled true
            shrinkResources true

            // Use optimized ProGuard rules
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt')
        }
    }

    compileOptions {
        // Enable Java 8 desugaring (smaller than library alternatives)
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
        coreLibraryDesugaringEnabled true
    }
}
```

### 11. Analyze APK Size

**Using Android Studio:**

-   Build → Analyze APK
-   Shows breakdown of APK contents

**Using command line:**

```bash
# Generate size report
./gradlew :app:analyzeReleaseBundle

# Outputs: build/reports/bundle-size-report.txt
```

**APK Analyzer breakdown:**

-   **DEX files**: Java/Kotlin code
-   **Resources**: Images, layouts, strings
-   **Native libs**: .so files
-   **Assets**: Raw files

### Size Reduction Checklist

```kotlin
class APKSizeOptimization {
    /**
     * Checklist for reducing APK size:
     *
     * Code:
     * [x] Enable R8/ProGuard minification
     * [x] Enable resource shrinking
     * [x] Remove unused dependencies
     * [x] Use specific library modules
     *
     * Resources:
     * [x] Convert PNG/JPEG to WebP
     * [x] Use Vector Drawables
     * [x] Remove unused resources (lint)
     * [x] Keep only required densities
     * [x] Keep only required languages
     *
     * Native Libraries:
     * [x] Remove unused ABIs
     * [x] Compress native libraries
     * [x] Use ABI splits
     *
     * Distribution:
     * [x] Use Android App Bundle
     * [x] Enable language/density/ABI splits
     * [x] Use dynamic feature modules
     *
     * Analysis:
     * [x] Run APK Analyzer
     * [x] Check dependency sizes
     * [x] Monitor APK size in CI/CD
     */
}
```

### Expected Results

| Technique                        | Size Reduction            |
| -------------------------------- | ------------------------- |
| R8/ProGuard + Resource Shrinking | 20-40%                    |
| Android App Bundle               | 15-35%                    |
| WebP Images                      | 25-35% (from PNG)         |
| Vector Drawables                 | 50-80% (vs multiple PNGs) |
| ABI Filters                      | 30-50%                    |
| Remove Unused Dependencies       | 5-20%                     |
| **Combined**                     | **40-70%**                |

### Best Practices

1. **Monitor APK size in CI/CD**: Fail builds if size exceeds threshold
2. **Use APK Analyzer regularly**: Understand where size comes from
3. **Prefer App Bundle over APK**: Let Google Play optimize
4. **Use on-demand delivery**: For optional features
5. **Test on lower-end devices**: Verify performance impact

### Common Pitfalls

1. Not enabling minification in release builds
2. Including all ABIs in single APK
3. Using PNG instead of WebP
4. Including entire Google Play Services
5. Not removing unused resources
6. Ignoring dependency sizes

## Ответ (RU)

Уменьшение размера APK критически важно для улучшения конверсии загрузок, снижения требований к хранилищу и улучшения пользовательского опыта.

### Основные техники:

### 1. Включить сжатие кода с R8/ProGuard

**Эффект:** Удаление неиспользуемого кода, ресурсов, обфускация, оптимизация байткода.
**Уменьшение:** 20-40%

### 2. Использовать Android App Bundle (AAB)

**Эффект:** Google Play генерирует оптимизированные APK для каждой конфигурации устройства.
**Уменьшение:** 15-35% по сравнению с универсальным APK

### 3. Оптимизация изображений

-   **WebP формат**: Лучшее сжатие чем PNG/JPEG
-   **Vector Drawables**: Вместо множества PNG разных разрешений
-   **Удаление неиспользуемых ресурсов**: Через `resConfigs`

**Уменьшение:** 10-30%

### 4. Уменьшение нативных библиотек

Включать только необходимые ABI (arm64-v8a, armeabi-v7a).
**Уменьшение:** До 50% при включении всех ABI

### 5. Удаление неиспользуемых зависимостей

Использовать конкретные модули вместо целых библиотек.

### 6. Использование Lint

Для поиска неиспользуемых ресурсов.

### 7. Сжатие нативных библиотек

Через `useLegacyPackaging = false`

### 8. Динамические Feature модули

Установка компонентов по требованию.

### Ожидаемые результаты:

| Техника            | Уменьшение размера |
| ------------------ | ------------------ |
| R8/ProGuard        | 20-40%             |
| App Bundle         | 15-35%             |
| WebP               | 25-35%             |
| Vector Drawables   | 50-80%             |
| ABI фильтры        | 30-50%             |
| **Комбинированно** | **40-70%**         |

### Лучшие практики:

1. Мониторинг размера APK в CI/CD
2. Регулярное использование APK Analyzer
3. Предпочтение App Bundle вместо APK
4. Использование доставки по требованию
5. Тестирование на слабых устройствах

### Частые ошибки:

1. Не включение minification в release сборках
2. Включение всех ABI в один APK
3. Использование PNG вместо WebP
4. Включение всех Google Play Services
5. Неудаление неиспользуемых ресурсов

---

## References

-   [Reduce APK Size - Android Developers](https://developer.android.com/topic/performance/reduce-apk-size)
-   [Android App Bundle](https://developer.android.com/guide/app-bundle)
-   [R8 Shrinking](https://developer.android.com/studio/build/shrink-code)
-   [WebP Images](https://developer.android.com/studio/write/convert-webp)

---

## Follow-ups

-   How do you measure and track APK size changes across different app versions?
-   What are the trade-offs between using dynamic feature modules vs keeping everything in the base APK?
-   How can you implement APK size budgets in your CI/CD pipeline to prevent size regressions?

## References

-   `https://developer.android.com/topic/performance/reduce-apk-size` — APK size reduction guide
-   `https://developer.android.com/studio/build/shrink-code` — Code shrinking
-   `https://developer.android.com/guide/app-bundle` — Android App Bundle

## Related Questions

### Related (Medium)

-   [[q-reduce-app-size--android--medium]] - Optimization
-   [[q-app-size-optimization--performance--medium]] - Performance
-   [[q-macrobenchmark-startup--performance--medium]] - Performance
-   [[q-recomposition-compose--android--medium]] - Jetpack Compose

### Advanced (Harder)

-   [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
