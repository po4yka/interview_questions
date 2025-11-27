---
id: android-017
title: "How to reduce APK size? / Как уменьшить размер APK?"
aliases: ["How to reduce APK size", "Как уменьшить размер APK"]
topic: android
subtopics: [app-bundle, gradle, performance-memory]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
sources: ["https://github.com/amitshekhariitbhu/android-interview-questions"]
status: draft
moc: moc-android
related: [c-app-bundle, q-macrobenchmark-startup--android--medium]
created: 2024-10-06
updated: 2025-11-10
tags: [android/app-bundle, android/gradle, android/performance-memory, difficulty/medium]

date created: Saturday, November 1st 2025, 12:47:02 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---
# Вопрос (RU)

> Какие техники можно использовать для уменьшения размера Android APK?

# Question (EN)

> What techniques can be used to reduce Android APK size?

---

## Ответ (RU)

Уменьшение размера APK критически важно для улучшения конверсии загрузок и пользовательского опыта. Основные подходы включают сжатие кода, оптимизацию ресурсов и использование [[c-app-bundle|Android App `Bundle`]].

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

**Эффект**: удаление мертвого кода, обфускация имен, оптимизация байткода. Типичное уменьшение порядка 20–40% (в зависимости от проекта).

### 2. Android App `Bundle`

```gradle
android {
    // Для Android App Bundle Play сам генерирует сплиты по ABI, density и языкам.
    // Отдельная декларация splits здесь обычно не требуется для AAB.
    // Пример настройки языка при необходимости:
    bundle {
        language {
            // enableSplit = true  // ✅ Разрешить раздельную доставку языковых пакетов
            // enableSplit = false // ✅ Отключить сплиты, если хотим все языки в базовом APK
        }
    }
}
```

**Эффект**: Google Play на основе App `Bundle` генерирует оптимизированные APK/сплиты для каждой конфигурации устройства (ABI, плотность, язык). Пользователи загружают только нужные им части. Типичное уменьшение порядка 15–35% по сравнению с монолитным APK.

### 3. Оптимизация Ресурсов

```gradle
android {
    defaultConfig {
        // ✅ Ограничиваем только нужные языки для ресурсов
        // ВНИМАНИЕ: resConfigs физически удаляет ресурсы из APK/AAB.
        resConfigs "en", "ru"
    }

    // ✅ Для прямых APK-сборок можно включить сплиты по плотности
    splits {
        density {
            enable true
            // при необходимости можно исключить неиспользуемые плотности
            // exclude "ldpi", "mdpi"
        }
    }
}
```

- **WebP**: лучшее сжатие, чем PNG/JPEG, без видимой потери качества для большинства ресурсов (часто экономия 20–35%).
- **VectorDrawable**: используйте для иконок и простых форм; для сложных изображений векторы могут быть больше растров.
- **Lint + shrinkResources**: автоматический поиск и удаление неиспользуемых ресурсов.

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

**Эффект**: заметное уменьшение размера (часто до ~50% от нативной части), если исключить x86/x86_64 и другие неиспользуемые ABI.

### 5. Зависимости

```kotlin
// ✅ Подключаем только необходимые модули
implementation "com.google.android.gms:play-services-maps:..."

// ❌ Не тянем весь пакет целиком
// implementation "com.google.android.gms:play-services:..."
```

Анализ размера: `./gradlew :app:analyzeReleaseBundle` (при поддержке текущей версии AGP) или APK Analyzer в Android Studio.

### Ожидаемые Результаты

| Техника | Уменьшение |
|---------|-----------|
| R8/ProGuard + Resource Shrinking | ~20-40% |
| Android App `Bundle` | ~15-35% |
| WebP + VectorDrawable | ~25-50% |
| ABI фильтры | ~30-50% |
| **Комбинированно** | **до ~40-70%** |

(Фактические значения зависят от структуры конкретного приложения и характера ресурсов.)

### Лучшие Практики

1. Мониторинг размера APK/AAB в CI/CD.
2. Использование [[c-app-bundle|App `Bundle`]] как основного формата доставки (Google Play).
3. Регулярный анализ через APK Analyzer / `analyzeReleaseBundle`.
4. Dynamic Feature Modules для опциональных компонентов, чтобы не загружать их при первой установке.

### Дополнительные Вопросы (RU)

- В чем различия между R8 и ProGuard с точки зрения возможностей оптимизации?
- Каковы компромиссы использования Dynamic Feature Modules для времени запуска приложения?
- Как настроить регрессионное тестирование размера APK в CI/CD?
- Какие техники позволяют уменьшить размер загрузки APK по сравнению с размером установки?

### Ссылки (RU)

- [[c-app-bundle]] - Архитектура Android App `Bundle`
- https://developer.android.com/topic/performance/reduce-apk-size
- https://developer.android.com/studio/build/shrink-code

### Связанные Вопросы (RU)

#### Предварительные Знания

- Понимание системы сборки Gradle и типов сборок
- Базовые знания ProGuard/R8

#### Связанные (Средний уровень)

- [[q-macrobenchmark-startup--android--medium]] - Производительность запуска
- Сравнение AAB и APK
- Стратегии оптимизации ресурсов

#### Продвинутые (Сложнее)

- Реализация Dynamic Feature Modules
- Мониторинг размера APK в конвейерах CI/CD

## Answer (EN)

Reducing APK size is crucial for improving download conversion rates and user experience. Main approaches include code shrinking, resource optimization, and using [[c-app-bundle|Android App `Bundle`]].

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

**Effect**: dead code elimination, name obfuscation, bytecode optimization. Typical reduction on the order of 20–40% (project-dependent).

### 2. Android App `Bundle`

```gradle
android {
    // For Android App Bundle, Play generates ABI/density/language splits automatically.
    // Explicit splits configuration is usually not required for AAB itself.
    // Example for language configuration if needed:
    bundle {
        language {
            // enableSplit = true  // ✅ Enable separate language splits
            // enableSplit = false // ✅ Disable language splits to keep all languages together
        }
    }
}
```

**Effect**: Google Play generates optimized APKs/splits per device configuration (ABI, density, language) from the App `Bundle`. Users download only what they need. Typical reduction around 15–35% vs a single universal APK.

### 3. Resource Optimization

```gradle
android {
    defaultConfig {
        // ✅ Limit to required resource languages
        // NOTE: resConfigs physically removes resources from APK/AAB.
        resConfigs "en", "ru"
    }

    // ✅ For direct APK builds you can enable density splits.
    splits {
        density {
            enable true
            // optionally exclude densities you don't support
            // exclude "ldpi", "mdpi"
        }
    }
}
```

- **WebP**: better compression than PNG/JPEG without visible quality loss for most assets (often 20–35% savings).
- **VectorDrawable**: best for icons and simple shapes; for complex images vectors can be larger than bitmaps.
- **Lint + shrinkResources**: automatically detect and remove unused resources.

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

**Effect**: significant reduction in the native portion size (often up to ~50%) when excluding x86/x86_64 and other unused ABIs.

### 5. Dependencies

```kotlin
// ✅ Use only required modules
implementation "com.google.android.gms:play-services-maps:..."

// ❌ Avoid pulling the entire bundle
// implementation "com.google.android.gms:play-services:..."
```

Size analysis: `./gradlew :app:analyzeReleaseBundle` (if supported by your AGP version) or APK Analyzer in Android Studio.

### Expected Results

| Technique | Reduction |
|-----------|-----------|
| R8/ProGuard + Resource Shrinking | ~20-40% |
| Android App `Bundle` | ~15-35% |
| WebP + VectorDrawable | ~25-50% |
| ABI filters | ~30-50% |
| **Combined** | **up to ~40-70%** |

(Actual values depend on the app structure and asset characteristics.)

### Best Practices

1. Monitor APK/AAB size in CI/CD.
2. Use [[c-app-bundle|App `Bundle`]] as the primary distribution format (Google Play).
3. Regularly analyze builds via APK Analyzer / `analyzeReleaseBundle`.
4. Use Dynamic Feature Modules for optional components so they are not downloaded on first install.

---

## Follow-ups

- How does R8 differ from ProGuard in optimization capabilities?
- What are the trade-offs of Dynamic Feature Modules for app startup performance?
- How to set up APK size regression testing in CI/CD?
- What techniques can reduce APK download size vs install size?

## References

- [[c-app-bundle]] - Android App `Bundle` architecture
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
