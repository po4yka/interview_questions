---
id: 20251011-220007
title: App Size Optimization / Оптимизация размера приложения
aliases: ["App Size Optimization", "Оптимизация размера приложения"]
topic: android
subtopics: [gradle, performance-memory]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-bundles--android--easy, q-android-build-optimization--android--medium, q-android-performance-measurement-tools--android--medium]
sources: []
created: 2025-10-11
updated: 2025-10-28
tags: [android/gradle, android/performance-memory, difficulty/medium]
---

# Question (EN)
> What is App Size Optimization and what techniques are used to reduce Android app size?

---

# Вопрос (RU)
> Что такое оптимизация размера приложения и какие техники используются для уменьшения размера Android-приложения?

---

## Answer (EN)

**App Size Optimization** reduces APK/AAB size through code shrinking, resource optimization, and smart distribution. Download conversion rates drop ~1% per 6MB, making size optimization critical for user acquisition.

### Core Techniques

**1. R8 Code Shrinking & Obfuscation**
R8 removes unused code, shortens class/method names, and optimizes bytecode at build time.

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true        // ✅ Enables R8
            isShrinkResources = true       // ✅ Removes unused resources
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

**2. Resource Optimization**
Combine automatic shrinking with manual configuration filtering:

```kotlin
android {
    defaultConfig {
        // ✅ Only ship supported languages
        resourceConfigurations += listOf("en", "ru")

        // ✅ Target common densities only
        resourceConfigurations += listOf("xxhdpi", "xxxhdpi")
    }
}
```

**3. Image Compression**
- Convert PNG/JPG → WebP (70-80% smaller)
- Use vector drawables for icons (90%+ reduction)
- Avoid shipping unused drawable densities

**4. Android App Bundle (AAB)**
Google Play generates device-specific APKs, reducing download size by 40-60%:

```kotlin
android {
    bundle {
        language.enableSplit = true  // ✅ Language splits
        density.enableSplit = true   // ✅ Density splits
        abi.enableSplit = true       // ✅ ABI splits
    }
}
```

**5. Dependency Management**
```kotlin
// ❌ Avoid: Includes entire library
implementation("com.google.android.gms:play-services")

// ✅ Better: Cherry-pick modules
implementation("com.google.android.gms:play-services-maps")
```

---

## Ответ (RU)

**Оптимизация размера приложения** уменьшает размер APK/AAB через сжатие кода, оптимизацию ресурсов и умную дистрибуцию. Конверсия загрузок падает ~1% на каждые 6МБ, что делает оптимизацию критичной для привлечения пользователей.

### Основные техники

**1. Сжатие и обфускация кода с R8**
R8 удаляет неиспользуемый код, сокращает имена классов/методов и оптимизирует байткод на этапе сборки.

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true        // ✅ Включает R8
            isShrinkResources = true       // ✅ Удаляет неиспользуемые ресурсы
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

**2. Оптимизация ресурсов**
Комбинируйте автоматическое сжатие с ручной фильтрацией конфигураций:

```kotlin
android {
    defaultConfig {
        // ✅ Поставляйте только поддерживаемые языки
        resourceConfigurations += listOf("en", "ru")

        // ✅ Только распространённые плотности экрана
        resourceConfigurations += listOf("xxhdpi", "xxxhdpi")
    }
}
```

**3. Сжатие изображений**
- Конвертируйте PNG/JPG → WebP (на 70-80% меньше)
- Используйте vector drawables для иконок (уменьшение на 90%+)
- Не включайте неиспользуемые плотности drawable

**4. Android App Bundle (AAB)**
Google Play генерирует APK под конкретные устройства, уменьшая размер загрузки на 40-60%:

```kotlin
android {
    bundle {
        language.enableSplit = true  // ✅ Разделение по языкам
        density.enableSplit = true   // ✅ Разделение по плотности
        abi.enableSplit = true       // ✅ Разделение по ABI
    }
}
```

**5. Управление зависимостями**
```kotlin
// ❌ Избегайте: включает всю библиотеку
implementation("com.google.android.gms:play-services")

// ✅ Лучше: выбирайте конкретные модули
implementation("com.google.android.gms:play-services-maps")
```

---

## Follow-ups

- How do you measure the impact of app size on conversion rates?
- When should you use dynamic feature modules vs. instant apps?
- How does R8 differ from ProGuard in terms of optimization capabilities?
- What are the trade-offs between AAB splits and maintaining a universal APK?
- How do you prevent R8 from removing code used via reflection?

## References

- [Shrink Your App (Official Docs)](https://developer.android.com/studio/build/shrink-code)
- [Android App Bundle Guide](https://developer.android.com/guide/app-bundle)
- [R8 Optimization](https://developer.android.com/studio/build/r8)

## Related Questions

### Prerequisites
- [[q-android-app-bundles--android--easy]] - Understanding AAB format and benefits
- [[q-gradle-build-basics--android--easy]] - Gradle configuration fundamentals

### Related
- [[q-android-build-optimization--android--medium]] - Build performance and optimization
- [[q-android-performance-measurement-tools--android--medium]] - Profiling and analysis tools
- [[q-proguard-r8-configuration--android--medium]] - Advanced R8/ProGuard rules

### Advanced
- [[q-dynamic-feature-modules--android--hard]] - On-demand feature delivery
- [[q-android-security-obfuscation--android--hard]] - Code protection and reverse engineering