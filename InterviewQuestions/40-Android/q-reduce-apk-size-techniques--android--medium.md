---
id: android-017
title: "How to reduce APK size? / Как уменьшить размер APK?"
aliases: ["How to reduce APK size", "Как уменьшить размер APK"]

# Classification
topic: android
subtopics: [app-bundle, gradle, performance-memory]
question_kind: android
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: [https://github.com/amitshekhariitbhu/android-interview-questions]

# Workflow & relations
status: draft
moc: moc-android
related: [c-app-bundle, q-macrobenchmark-startup--android--medium]

# Timestamps
created: 2025-10-06
updated: 2025-01-27

tags: [android/app-bundle, android/gradle, android/performance-memory, difficulty/medium]
---

# Вопрос (RU)

> Какие техники можно использовать для уменьшения размера Android APK?

# Question (EN)

> What techniques can be used to reduce Android APK size?

---

## Ответ (RU)

Уменьшение размера APK критически важно для улучшения конверсии загрузок и пользовательского опыта. Основные подходы включают сжатие кода, оптимизацию ресурсов и использование [[c-app-bundle|Android App Bundle]].

### 1. R8/ProGuard - Сжатие Кода

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true           // ✅ Удаление неиспользуемого кода
            shrinkResources true         // ✅ Удаление неиспользуемых ресурсов
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'),
                         'proguard-rules.pro'
        }
    }
}
```

**Эффект**: удаление мертвого кода, обфускация имен, оптимизация байткода. Уменьшение 20-40%.

### 2. Android App Bundle

```gradle
android {
    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}
```

**Эффект**: Google Play генерирует оптимизированные APK для каждой конфигурации устройства. Пользователи загружают только нужные ресурсы. Уменьшение 15-35%.

### 3. Оптимизация Ресурсов

```gradle
android {
    defaultConfig {
        resConfigs "en", "ru"              // ✅ Только нужные языки
        resConfigs "xxhdpi", "xxxhdpi"     // ✅ Только нужные плотности
    }
}
```

- **WebP**: лучшее сжатие чем PNG/JPEG (25-35%)
- **VectorDrawable**: вместо множества PNG (50-80%)
- **Lint**: автоматический поиск неиспользуемых ресурсов

### 4. Нативные Библиотеки

```gradle
android {
    defaultConfig {
        ndk {
            abiFilters 'arm64-v8a', 'armeabi-v7a'  // ✅ Только нужные ABI
        }
    }
}
```

**Эффект**: уменьшение до 50% при исключении x86/x86_64.

### 5. Зависимости

```kotlin
// ✅ Конкретные модули
implementation 'com.google.android.gms:play-services-maps:...'

// ❌ Вся библиотека
// implementation 'com.google.android.gms:play-services:...'
```

Анализ размера: `./gradlew :app:analyzeReleaseBundle`

### Ожидаемые Результаты

| Техника | Уменьшение |
|---------|-----------|
| R8/ProGuard + Resource Shrinking | 20-40% |
| Android App Bundle | 15-35% |
| WebP + VectorDrawable | 25-50% |
| ABI фильтры | 30-50% |
| **Комбинированно** | **40-70%** |

### Лучшие Практики

1. Мониторинг размера APK в CI/CD
2. Использование [[c-app-bundle|App Bundle]] вместо APK
3. Регулярный анализ через APK Analyzer
4. Dynamic Feature Modules для опциональных компонентов

## Answer (EN)

Reducing APK size is crucial for improving download conversion rates and user experience. Main approaches include code shrinking, resource optimization, and using [[c-app-bundle|Android App Bundle]].

### 1. R8/ProGuard - Code Shrinking

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true           // ✅ Remove unused code
            shrinkResources true         // ✅ Remove unused resources
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'),
                         'proguard-rules.pro'
        }
    }
}
```

**Effect**: dead code elimination, name obfuscation, bytecode optimization. Reduces by 20-40%.

### 2. Android App Bundle

```gradle
android {
    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}
```

**Effect**: Google Play generates optimized APKs for each device configuration. Users download only required resources. Reduces by 15-35%.

### 3. Resource Optimization

```gradle
android {
    defaultConfig {
        resConfigs "en", "ru"              // ✅ Only required languages
        resConfigs "xxhdpi", "xxxhdpi"     // ✅ Only required densities
    }
}
```

- **WebP**: better compression than PNG/JPEG (25-35%)
- **VectorDrawable**: instead of multiple PNGs (50-80%)
- **Lint**: automatic unused resource detection

### 4. Native Libraries

```gradle
android {
    defaultConfig {
        ndk {
            abiFilters 'arm64-v8a', 'armeabi-v7a'  // ✅ Only required ABIs
        }
    }
}
```

**Effect**: reduces by up to 50% when excluding x86/x86_64.

### 5. Dependencies

```kotlin
// ✅ Specific modules
implementation 'com.google.android.gms:play-services-maps:...'

// ❌ Entire library
// implementation 'com.google.android.gms:play-services:...'
```

Size analysis: `./gradlew :app:analyzeReleaseBundle`

### Expected Results

| Technique | Reduction |
|-----------|-----------|
| R8/ProGuard + Resource Shrinking | 20-40% |
| Android App Bundle | 15-35% |
| WebP + VectorDrawable | 25-50% |
| ABI filters | 30-50% |
| **Combined** | **40-70%** |

### Best Practices

1. Monitor APK size in CI/CD
2. Use [[c-app-bundle|App Bundle]] instead of APK
3. Regular analysis via APK Analyzer
4. Dynamic Feature Modules for optional components

---

## Follow-ups

- How does R8 differ from ProGuard in optimization capabilities?
- What are the trade-offs of Dynamic Feature Modules for app startup performance?
- How to set up APK size regression testing in CI/CD?
- What techniques can reduce APK download size vs install size?

## References

- [[c-app-bundle]] - Android App Bundle architecture
- https://developer.android.com/topic/performance/reduce-apk-size
- https://developer.android.com/studio/build/shrink-code

## Related Questions

### Prerequisites

- Understanding Gradle build system and build types
- ProGuard/R8 basics

### Related (Medium)

- [[q-macrobenchmark-startup--android--medium]] - Startup performance
- AAB vs APK comparison
- Resource optimization strategies

### Advanced (Harder)

- Dynamic Feature Modules implementation
- APK size monitoring in CI/CD pipelines
