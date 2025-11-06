---
id: android-051
title: App Size Optimization / Оптимизация размера приложения
aliases: [App Size Optimization, Оптимизация размера приложения]
topic: android
subtopics:
  - app-bundle
  - gradle
  - performance-memory
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-android-app-bundles--android--easy
sources: []
created: 2025-10-11
updated: 2025-10-30
tags: [android/app-bundle, android/gradle, android/performance-memory, difficulty/medium]
---

# Вопрос (RU)
> Какие техники используются для уменьшения размера Android-приложения?

---

# Question (EN)
> What techniques are used to reduce Android app size?

---

## Ответ (RU)

**Оптимизация размера** критична для конверсии: каждые 6 МБ снижают установки на ~1%. Основные векторы атаки — код, ресурсы, нативные библиотеки.

### Сжатие Кода (R8)

R8 удаляет неиспользуемый код (shrinking), сокращает имена (obfuscation), оптимизирует байткод.

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true         // ✅ Включает R8
            isShrinkResources = true        // ✅ Удаляет неиспользуемые ресурсы
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

**Результат**: 30-50% уменьшение кода в типичном проекте с зависимостями.

### Оптимизация Ресурсов

**Фильтрация конфигураций**:
```kotlin
android {
    defaultConfig {
        resourceConfigurations += listOf("en", "ru")         // ✅ Только нужные языки
        resourceConfigurations += listOf("xxhdpi", "xxxhdpi") // ✅ Целевые плотности
    }
}
```

**Сжатие изображений**:
- PNG/JPG → WebP: экономия 70-80%
- Vector drawables для иконок: экономия 90%+
- Удаление неиспользуемых densities через R8

### Android App `Bundle` (AAB)

Google Play генерирует APK под конкретное устройство:

```kotlin
android {
    bundle {
        language.enableSplit = true   // ✅ Разделение по языкам
        density.enableSplit = true    // ✅ Разделение по плотности
        abi.enableSplit = true        // ✅ Разделение по ABI (arm64, x86)
    }
}
```

**Результат**: экономия 40-60% размера установки против универсального APK.

### Управление Зависимостями

```kotlin
// ❌ Избегайте: весь Google Play Services (~10 МБ)
implementation("com.google.android.gms:play-services")

// ✅ Выбирайте модули: только Maps (~2 МБ)
implementation("com.google.android.gms:play-services-maps")
```

**Аудит**: используйте `./gradlew app:dependencies` для анализа транзитивных зависимостей.

### Нативные Библиотеки

```kotlin
android {
    defaultConfig {
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a") // ✅ Только ARM (99% устройств)
            // ❌ Не включайте x86/x86_64 без необходимости
        }
    }
}
```

---

## Answer (EN)

**App Size Optimization** is critical for conversion: every 6 MB reduces installs by ~1%. Attack vectors: code, resources, native libraries.

### Code Shrinking (R8)

R8 removes unused code (shrinking), shortens names (obfuscation), optimizes bytecode.

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true         // ✅ Enables R8
            isShrinkResources = true        // ✅ Removes unused resources
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

**Result**: 30-50% code reduction in typical projects with dependencies.

### Resource Optimization

**Configuration Filtering**:
```kotlin
android {
    defaultConfig {
        resourceConfigurations += listOf("en", "ru")         // ✅ Only needed languages
        resourceConfigurations += listOf("xxhdpi", "xxxhdpi") // ✅ Target densities
    }
}
```

**Image Compression**:
- PNG/JPG → WebP: 70-80% savings
- Vector drawables for icons: 90%+ reduction
- Remove unused densities via R8

### Android App `Bundle` (AAB)

Google Play generates device-specific APKs:

```kotlin
android {
    bundle {
        language.enableSplit = true   // ✅ Language splits
        density.enableSplit = true    // ✅ Density splits
        abi.enableSplit = true        // ✅ ABI splits (arm64, x86)
    }
}
```

**Result**: 40-60% install size savings vs. universal APK.

### Dependency Management

```kotlin
// ❌ Avoid: entire Google Play Services (~10 MB)
implementation("com.google.android.gms:play-services")

// ✅ Cherry-pick modules: only Maps (~2 MB)
implementation("com.google.android.gms:play-services-maps")
```

**Audit**: use `./gradlew app:dependencies` to analyze transitive dependencies.

### Native Libraries

```kotlin
android {
    defaultConfig {
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a") // ✅ Only ARM (99% devices)
            // ❌ Don't include x86/x86_64 unless required
        }
    }
}
```

---

## Follow-ups

- How do you measure app size impact on conversion rates in production?
- When should you use dynamic feature modules vs. instant apps?
- What are the trade-offs of aggressive R8 optimization in debugging crashes?
- How do you handle ProGuard rules for libraries using reflection or JNI?
- What metrics indicate over-aggressive resource stripping in production?

## References

- [[c-app-bundle]] - AAB format and split APK generation
- [Shrink Your App (Official Docs)](https://developer.android.com/studio/build/shrink-code)
- [Android App `Bundle` Guide](https://developer.android.com/guide/app-bundle)
- [R8 Optimization](https://developer.android.com/studio/build/r8)

## Related Questions

### Prerequisites
- [[q-android-app-bundles--android--easy]] - Understanding AAB format and benefits
 - Gradle configuration fundamentals

### Related
- [[q-android-build-optimization--android--medium]] - Build performance optimization
 - Advanced R8/ProGuard rules
- [[q-android-performance-measurement-tools--android--medium]] - Profiling and analysis tools

### Advanced
 - On-demand feature delivery
 - Code protection strategies
