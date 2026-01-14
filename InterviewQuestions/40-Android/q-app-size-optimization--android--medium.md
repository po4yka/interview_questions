---
id: android-051
title: App Size Optimization / Оптимизация размера приложения
aliases:
- App Size Optimization
- Оптимизация размера приложения
topic: android
subtopics:
- app-bundle
- obfuscation
- performance-memory
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-app-bundle
- q-android-app-bundles--android--easy
- q-android-build-optimization--android--medium
- q-app-startup-optimization--android--medium
- q-optimize-memory-usage-android--android--medium
- q-reduce-apk-size-techniques--android--medium
sources: []
created: 2025-10-11
updated: 2025-11-10
tags:
- android/app-bundle
- android/obfuscation
- android/performance-memory
- difficulty/medium
anki_cards:
- slug: android-051-0-en
  language: en
  anki_id: 1768364268727
  synced_at: '2026-01-14T09:17:53.718362'
- slug: android-051-0-ru
  language: ru
  anki_id: 1768364268749
  synced_at: '2026-01-14T09:17:53.721327'
---
# Вопрос (RU)
> Какие техники используются для уменьшения размера Android-приложения?

---

# Question (EN)
> What techniques are used to reduce Android app size?

---

## Ответ (RU)

**Оптимизация размера** критична для конверсии: рост APK/AAB обычно ухудшает установки и удержание (по данным исследований Google Play и индустрии). Основные векторы атаки — код, ресурсы, нативные библиотеки.

### Сжатие Кода (R8)

R8 удаляет неиспользуемый код (shrinking), сокращает имена (obfuscation), оптимизирует байткод.

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true          // ✅ Включает R8 (shrinking/obfuscation)
            isShrinkResources = true        // ✅ Удаляет неиспользуемые ресурсы (resource shrinking)
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

Важно: для кода, использующего reflection/JNI/аннотации, нужны корректные правила сохранения (keep rules), иначе возможны runtime-ошибки.

**Результат**: во многих проектах с зависимостями возможно значительное уменьшение размера кода (часто десятки процентов, точное значение зависит от проекта).

### Оптимизация Ресурсов

**Фильтрация конфигураций (избирательно)**:
```kotlin
android {
    defaultConfig {
        resourceConfigurations += listOf("en", "ru")          // ✅ Оставлять только действительно поддерживаемые языки
        // Важно: при использовании App Bundle и управляемых Google Play language splits
        // чрезмерное ограничение языков здесь лишит пользователей возможности загрузить отсутствующие локали.
        // Обычно ужесточают только если заведомо не планируются другие языки.
    }
}
```

Осторожно с фильтрацией по плотностям: для универсальных APK или специфичных каналов дистрибуции можно ограничить плотности, но для AAB Google Play и так делает split по плотностям.

**Сжатие изображений**:
- PNG/JPG → WebP: часто 20-80% экономии в зависимости от контента
- Vector drawables для иконок и простых иллюстраций: существенная экономия по сравнению с набором bitmap-ресурсов под разные плотности
- Удаление неиспользуемых ресурсов (включая лишние density-версии) через resource shrinking (`isShrinkResources = true`) и аудит ресурсов

### Android App `Bundle` (AAB)

Google Play для AAB автоматически генерирует device-specific split APKs (языки, плотности, ABI и др.), уменьшая размер загружаемого пакета без необходимости собирать один универсальный APK.

Для проектов, которые по-прежнему распространяют APK напрямую или используют кастомные каналы, можно явно настраивать split-конфигурации:

```kotlin
android {
    bundle {
        language {
            enableSplit = true    // ✅ Разделение по языкам при генерации сплитов
        }
        density {
            enableSplit = true    // ✅ Разделение по плотности
        }
        abi {
            enableSplit = true    // ✅ Разделение по ABI (arm64, armeabi-v7a, x86 и т.д., по необходимости)
        }
    }
}
```

**Результат**: за счёт split APKs размер загружаемого на устройство пакета заметно меньше универсального APK (экономия может достигать десятков процентов, зависит от набора ресурсов/ABI).

### Управление Зависимостями

```kotlin
// ❌ Избегайте: весь Google Play Services (большой монолитный артефакт)
implementation("com.google.android.gms:play-services")

// ✅ Выбирайте модули: только Maps и другие необходимые компоненты
implementation("com.google.android.gms:play-services-maps")
```

**Аудит**: используйте `./gradlew app:dependencies` для анализа транзитивных зависимостей и удаления избыточных библиотек.

### Нативные Библиотеки

```kotlin
android {
    defaultConfig {
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a") // ✅ Ограничить APK требуемыми ABI (например, ARM для большинства устройств)
            // ❌ Не включайте x86/x86_64 без необходимости (эмуляторы, специфические девайсы)
        }
    }
}
```

Для Android App `Bundle` Google Play сам использует ABI splits; агрессивное ограничение `abiFilters` имеет смысл в первую очередь для прямой поставки APK или когда вы осознанно исключаете часть устройств.

Ограничение списка ABI уменьшает размер пакета, но требует учитывать целевые устройства и каналы дистрибуции.

---

## Answer (EN)

**App Size Optimization** is critical for conversion: larger APK/AAB size generally hurts installs and retention (per Google Play and industry studies). Main optimization vectors: code, resources, native libraries.

### Code Shrinking (R8)

R8 removes unused code (shrinking), shortens names (obfuscation), and optimizes bytecode.

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true          // ✅ Enables R8 (shrinking/obfuscation)
            isShrinkResources = true        // ✅ Removes unused resources (resource shrinking)
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

Note: for code using reflection/JNI/annotation processing, proper keep rules are required; otherwise you risk runtime issues in release builds.

**Result**: many projects with multiple dependencies see substantial size reduction (often tens of percent; exact savings are project-specific).

### Resource Optimization

**Configuration Filtering (selective)**:
```kotlin
android {
    defaultConfig {
        resourceConfigurations += listOf("en", "ru")          // ✅ Keep only truly supported languages
        // Important: with App Bundles and Play-managed language splits,
        // over-restricting languages here will prevent users from downloading missing locales.
        // Typically tightened only when other languages are definitively not planned.
    }
}
```

Be careful with density filtering: for universal APKs or specific distribution channels it can be used, but for AAB Google Play already creates density-specific splits, so manual restriction is usually unnecessary.

**Image Compression**:
- PNG/JPG → WebP: often 20-80% savings depending on content
- Vector drawables for icons and simple illustrations: significant savings vs. multiple bitmap density variants
- Remove unused resources (including redundant density variants) via resource shrinking (`isShrinkResources = true`) and resource audits

### Android App `Bundle` (AAB)

For AABs, Google Play automatically generates device-specific split APKs (language, density, ABI, etc.), reducing download/install size without requiring a single universal APK.

For apps still distributing APKs directly or via custom channels, you can explicitly configure splits:

```kotlin
android {
    bundle {
        language {
            enableSplit = true    // ✅ Language splits when generating splits
        }
        density {
            enableSplit = true    // ✅ Density splits
        }
        abi {
            enableSplit = true    // ✅ ABI splits (arm64, armeabi-v7a, x86, etc. as appropriate)
        }
    }
}
```

**Result**: with split APKs, the on-device download size is significantly smaller than a universal APK (savings can reach tens of percent depending on resources/ABIs).

### Dependency Management

```kotlin
// ❌ Avoid: entire Google Play Services (large monolithic artifact)
implementation("com.google.android.gms:play-services")

// ✅ Cherry-pick modules: only Maps and other required components
implementation("com.google.android.gms:play-services-maps")
```

**Audit**: use `./gradlew app:dependencies` to inspect transitive dependencies and drop unnecessary libraries.

### Native Libraries

```kotlin
android {
    defaultConfig {
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a") // ✅ Limit APK to required ABIs (e.g., ARM for the majority of devices)
            // ❌ Don't include x86/x86_64 unless specifically needed (emulators, certain devices)
        }
    }
}
```

For Android App Bundles, Play already applies ABI splits; aggressive `abiFilters` are mainly relevant for direct APK distribution or when you intentionally drop support for certain device classes.

Limiting ABIs reduces package size but must be aligned with your target device set and distribution channels.

---

## Дополнительные Вопросы (RU)

- Как вы измеряете влияние размера приложения на конверсию и удержание в продакшене?
- Когда стоит использовать динамические feature-модули по сравнению с instant apps?
- Каковы компромиссы агрессивной оптимизации R8 при отладке сбоев?
- Как вы настраиваете правила ProGuard/R8 для библиотек, использующих reflection или JNI?
- Какие сигналы показывают, что вы слишком агрессивно удалили ресурсы в продакшене?

## Follow-ups

- How do you measure app size impact on conversion rates in production?
- When should you use dynamic feature modules vs. instant apps?
- What are the trade-offs of aggressive R8 optimization in debugging crashes?
- How do you handle ProGuard rules for libraries using reflection or JNI?
- What metrics indicate over-aggressive resource stripping in production?

---

## Ссылки (RU)

- [[c-app-bundle]] — формат AAB и генерация split APK
- "Shrink Your App" (официальная документация): https://developer.android.com/studio/build/shrink-code
- Руководство по Android App `Bundle`: https://developer.android.com/guide/app-bundle
- Документация по R8: https://developer.android.com/studio/build/r8

## References

- [[c-app-bundle]] - AAB format and split APK generation
- [Shrink Your App (Official Docs)](https://developer.android.com/studio/build/shrink-code)
- [Android App `Bundle` Guide](https://developer.android.com/guide/app-bundle)
- [R8 Optimization](https://developer.android.com/studio/build/r8)

---

## Связанные Вопросы (RU)

### Предварительные Знания
- [[q-android-app-bundles--android--easy]] — понимание формата AAB и его преимуществ
- Базовые основы конфигурации Gradle и сборки Android-проекта

### Связанные
- [[q-android-build-optimization--android--medium]] — оптимизация процесса сборки
- [[q-android-performance-measurement-tools--android--medium]] — инструменты профилирования и анализа производительности

### Продвинутые Темы
- Поставляемые по требованию модули (on-demand feature delivery)
- Стратегии защиты кода и артефактов при минимизации и обфускации

## Related Questions

### Prerequisites
- [[q-android-app-bundles--android--easy]] - Understanding AAB format and benefits
- Gradle configuration fundamentals

### Related
- [[q-android-build-optimization--android--medium]] - Build performance optimization
- [[q-android-performance-measurement-tools--android--medium]] - Profiling and analysis tools

### Advanced
- On-demand feature delivery
- Code protection strategies
