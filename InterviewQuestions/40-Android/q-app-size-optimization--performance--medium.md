---
id: 20251011-220007
title: App Size Optimization / Оптимизация размера приложения
aliases: [App Size Optimization, Оптимизация размера приложения]
topic: android
subtopics: [performance, app-size, optimization]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
related: [q-android-build-optimization--android--medium, q-android-performance-measurement-tools--android--medium, q-android-app-bundles--android--easy]
created: 2025-10-11
updated: 2025-10-15
tags: [android/performance, android/app-size, android/optimization, performance, app-size, optimization, proguard, r8, app-bundle, splits, difficulty/medium]
---
# Question (EN)
> How do you comprehensively reduce APK/AAB size? What strategies and tools do you use for app size optimization?

# Вопрос (RU)
> Как комплексно уменьшить размер APK/AAB? Какие стратегии и инструменты использовать для оптимизации размера приложения?

---

## Answer (EN)

**App Size Optimization** reduces APK/AAB size through resource shrinking, code minification, native library filtering, and Android App Bundle configuration. Smaller apps improve download conversion rates and user experience.

**Size Optimization Theory:**
App size directly impacts user acquisition - download conversion rates drop 1% per 6MB. Optimization strategies include removing unused code/resources, compressing assets, filtering languages/architectures, and using dynamic delivery to reduce initial install size.

**1. R8 Code Minification:**

**Code Shrinking Configuration:**
R8 removes unused code, obfuscates class/method names, and optimizes bytecode. Enables aggressive optimization while preserving necessary classes for reflection and native methods.

```kotlin
// build.gradle (app)
android {
    buildTypes {
        release {
            // Enable code shrinking and obfuscation
            isMinifyEnabled = true
            // Enable resource shrinking
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

**ProGuard Rules:**
```proguard
# Remove logging in release builds
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}

# Keep data classes for serialization
-keep class com.example.model.** { *; }

# Keep Parcelable implementations
-keep class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}

# Keep native methods
-keepclasseswithmembernames class * {
    native <methods>;
}
```

**2. Resource Shrinking:**

**Automatic Resource Removal:**
Removes unused resources automatically when minification is enabled. Can specify resources to keep or discard explicitly.

```kotlin
android {
    buildTypes {
        release {
            isShrinkResources = true
            isMinifyEnabled = true
        }
    }

    // Keep specific resources
    resourceConfigurations += listOf("en", "ru")
}
```

**Resource Keep Configuration:**
```xml
<!-- res/raw/keep.xml -->
<resources xmlns:tools="http://schemas.android.com/tools"
    tools:keep="@layout/used_by_reflection,@drawable/used_in_code"
    tools:discard="@layout/unused*,@drawable/unused*" />
```

**3. Language and Density Filtering:**

**Resource Configuration:**
Filters out unsupported languages and densities to reduce resource size. Only includes necessary translations and screen densities.

```kotlin
android {
    defaultConfig {
        // Only include supported languages
        resourceConfigurations += listOf("en", "ru", "es")

        // Support common densities only
        resourceConfigurations += listOf(
            "mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"
        )
    }
}
```

**4. Image Optimization:**

**WebP Conversion:**
Converts PNG images to WebP format for 70-80% size reduction while maintaining quality. WebP provides better compression than PNG.

```kotlin
// Convert PNG to WebP
// Before: icon_large.png (2.4MB)
// After: icon_large.webp (0.6MB) - 75% reduction
```

**Vector Drawables:**
Uses vector drawables for simple icons and graphics, providing 90%+ size reduction compared to PNG bitmaps.

```xml
<!-- res/drawable/icon.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FF000000"
        android:pathData="M12,2l3.09,6.26L22,9.27l-5,4.87L18.18,22L12,18.77L5.82,22L7,14.14L2,9.27l6.91,-1.01L12,2z"/>
</vector>
```

**5. Native Library Filtering:**

**ABI Splits:**
Creates separate APKs for different CPU architectures instead of including all architectures in one APK.

```kotlin
android {
    splits {
        abi {
            isEnable = true
            reset()
            include("armeabi-v7a", "arm64-v8a", "x86", "x86_64")
            isUniversalApk = false
        }
    }
}
```

**6. Android App Bundle:**

**Dynamic Delivery:**
Uses Android App Bundle for automatic optimization. Google Play generates optimized APKs for each device configuration.

```kotlin
android {
    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }

    defaultConfig {
        ndk {
            abiFilters += listOf("armeabi-v7a", "arm64-v8a")
        }
    }
}
```

**7. Dynamic Feature Modules:**

**On-Demand Loading:**
Loads features dynamically to reduce initial app size. Features are downloaded only when needed.

```kotlin
// Add dynamic feature module
implementation project(':feature_module')

// Request dynamic feature
val request = SplitInstallRequest.newBuilder()
    .addModule("feature_module")
    .build()

splitInstallManager.startInstall(request)
```

**8. Dependency Optimization:**

**Library Analysis:**
Excludes unused modules from large libraries and uses lightweight alternatives where possible.

```kotlin
// Exclude unused modules
implementation("com.squareup.retrofit2:retrofit") {
    exclude(group = "com.squareup.okhttp3", module = "okhttp")
}

// Use lightweight alternatives
implementation("com.squareup.okhttp3:okhttp") // Instead of full OkHttp
```

**Size Optimization Checklist:**
- Enable R8 full mode for maximum code optimization
- Use Android App Bundle for 40-60% size reduction
- Convert PNG images to WebP format
- Use vector drawables for simple graphics
- Filter languages to supported ones only
- Split APKs by CPU architecture
- Remove unused resources automatically
- Use dynamic feature modules for optional features
- Exclude unused library modules
- Regular APK analysis with APK Analyzer tool

## Ответ (RU)

**Оптимизация размера приложения** уменьшает размер APK/AAB через сжатие ресурсов, минификацию кода, фильтрацию нативных библиотек и конфигурацию Android App Bundle. Меньшие приложения улучшают конверсию загрузок и пользовательский опыт.

**Теория оптимизации размера:**
Размер приложения напрямую влияет на привлечение пользователей - конверсия загрузок падает на 1% за каждые 6МБ. Стратегии оптимизации включают удаление неиспользуемого кода/ресурсов, сжатие ресурсов, фильтрацию языков/архитектур и использование динамической доставки для уменьшения начального размера установки.

**1. Минификация кода R8:**

**Конфигурация сжатия кода:**
R8 удаляет неиспользуемый код, обфусцирует имена классов/методов и оптимизирует байт-код. Включает агрессивную оптимизацию при сохранении необходимых классов для рефлексии и нативных методов.

```kotlin
// build.gradle (app)
android {
    buildTypes {
        release {
            // Включить сжатие кода и обфускацию
            isMinifyEnabled = true
            // Включить сжатие ресурсов
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

**Правила ProGuard:**
```proguard
# Удалить логирование в релизных сборках
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}

# Сохранить классы данных для сериализации
-keep class com.example.model.** { *; }

# Сохранить реализации Parcelable
-keep class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}

# Сохранить нативные методы
-keepclasseswithmembernames class * {
    native <methods>;
}
```

**2. Сжатие ресурсов:**

**Автоматическое удаление ресурсов:**
Удаляет неиспользуемые ресурсы автоматически при включенной минификации. Можно указать ресурсы для сохранения или удаления явно.

```kotlin
android {
    buildTypes {
        release {
            isShrinkResources = true
            isMinifyEnabled = true
        }
    }

    // Сохранить конкретные ресурсы
    resourceConfigurations += listOf("en", "ru")
}
```

**Конфигурация сохранения ресурсов:**
```xml
<!-- res/raw/keep.xml -->
<resources xmlns:tools="http://schemas.android.com/tools"
    tools:keep="@layout/used_by_reflection,@drawable/used_in_code"
    tools:discard="@layout/unused*,@drawable/unused*" />
```

**3. Фильтрация языков и плотности:**

**Конфигурация ресурсов:**
Фильтрует неподдерживаемые языки и плотности для уменьшения размера ресурсов. Включает только необходимые переводы и плотности экранов.

```kotlin
android {
    defaultConfig {
        // Включить только поддерживаемые языки
        resourceConfigurations += listOf("en", "ru", "es")

        // Поддерживать только распространенные плотности
        resourceConfigurations += listOf(
            "mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"
        )
    }
}
```

**4. Оптимизация изображений:**

**Конвертация в WebP:**
Конвертирует PNG изображения в формат WebP для уменьшения размера на 70-80% при сохранении качества. WebP обеспечивает лучшее сжатие чем PNG.

```kotlin
// Конвертировать PNG в WebP
// До: icon_large.png (2.4MB)
// После: icon_large.webp (0.6MB) - сокращение на 75%
```

**Векторные изображения:**
Использует векторные изображения для простых иконок и графики, обеспечивая сокращение размера на 90%+ по сравнению с PNG битмапами.

```xml
<!-- res/drawable/icon.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FF000000"
        android:pathData="M12,2l3.09,6.26L22,9.27l-5,4.87L18.18,22L12,18.77L5.82,22L7,14.14L2,9.27l6.91,-1.01L12,2z"/>
</vector>
```

**5. Фильтрация нативных библиотек:**

**Разделение по ABI:**
Создает отдельные APK для разных CPU архитектур вместо включения всех архитектур в один APK.

```kotlin
android {
    splits {
        abi {
            isEnable = true
            reset()
            include("armeabi-v7a", "arm64-v8a", "x86", "x86_64")
            isUniversalApk = false
        }
    }
}
```

**6. Android App Bundle:**

**Динамическая доставка:**
Использует Android App Bundle для автоматической оптимизации. Google Play генерирует оптимизированные APK для каждой конфигурации устройства.

```kotlin
android {
    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }

    defaultConfig {
        ndk {
            abiFilters += listOf("armeabi-v7a", "arm64-v8a")
        }
    }
}
```

**7. Динамические модули функций:**

**Загрузка по требованию:**
Загружает функции динамически для уменьшения начального размера приложения. Функции загружаются только при необходимости.

```kotlin
// Добавить динамический модуль функции
implementation project(':feature_module')

// Запросить динамическую функцию
val request = SplitInstallRequest.newBuilder()
    .addModule("feature_module")
    .build()

splitInstallManager.startInstall(request)
```

**8. Оптимизация зависимостей:**

**Анализ библиотек:**
Исключает неиспользуемые модули из больших библиотек и использует легковесные альтернативы где возможно.

```kotlin
// Исключить неиспользуемые модули
implementation("com.squareup.retrofit2:retrofit") {
    exclude(group = "com.squareup.okhttp3", module = "okhttp")
}

// Использовать легковесные альтернативы
implementation("com.squareup.okhttp3:okhttp") // Вместо полного OkHttp
```

**Чеклист оптимизации размера:**
- Включить R8 полный режим для максимальной оптимизации кода
- Использовать Android App Bundle для сокращения размера на 40-60%
- Конвертировать PNG изображения в формат WebP
- Использовать векторные изображения для простой графики
- Фильтровать языки только на поддерживаемые
- Разделять APK по CPU архитектуре
- Удалять неиспользуемые ресурсы автоматически
- Использовать динамические модули функций для опциональных функций
- Исключать неиспользуемые модули библиотек
- Регулярный анализ APK с инструментом APK Analyzer

---

## Follow-ups

- How do you measure app size impact on user acquisition?
- What's the difference between R8 and ProGuard?
- How do you handle app size optimization for different device types?
- What are the trade-offs of dynamic feature modules?

## References

- [Shrink Your App](https://developer.android.com/studio/build/shrink-code)
- [Android App Bundle](https://developer.android.com/guide/app-bundle)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-android-build-optimization--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-android-app-bundles--android--easy]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
