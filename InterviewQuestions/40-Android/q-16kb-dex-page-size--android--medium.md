---
id: 20251012-122750
title: 16kb Dex Page Size / Размер страницы DEX 16KB
aliases: [16KB DEX Page Size, 16 КБ страница DEX]
topic: android
subtopics: [build-optimization, performance]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-background-tasks-decision-guide--android--medium
  - q-why-fragment-needs-separate-callback-for-ui-creation--android--hard
  - q-what-are-fragments-and-why-are-they-more-convenient-to-use-instead-of-multiple-activities--android--hard
created: 2025-10-15
updated: 2025-10-15
tags:
  - android/build-optimization
  - android/performance
  - dex
  - build-optimization
  - apk-size
  - performance
  - r8
  - proguard
  - difficulty/medium
---
# 16 KB DEX Page Size Issue in Android

# Question (EN)
> What is the 16 KB DEX page size issue in Android? How does it affect app performance and what can developers do about it?

# Вопрос (RU)
> Что такое проблема 16 КБ страниц DEX в Android? Как это влияет на производительность приложения и что могут сделать разработчики?

---

## Answer (EN)

The 16 KB DEX page size issue is a memory alignment problem affecting Android 6.0+ that causes significant app bloat when apps are optimized with R8/ProGuard.

#### Problem

Android uses 16 KB pages for DEX files. Method IDs must be page-aligned, creating wasted padding space.

```
Without alignment: [Header][Strings][Methods][Code]
With alignment:    [Header][Strings][Padding][Methods][Code]
                                    ^^^^^^^^ Wasted space
```

Impact:
- Small apps (< 5 MB): 20-40% size increase
- Large apps (> 50 MB): 5-15% size increase
- Multi-DEX apps: Multiplied impact

#### Detection

APK Analyzer:
- Tools → APK Analyzer → Select APK
- Check classes.dex size
- Look for unusual growth in optimized builds

Command line:
```bash
unzip app-release.apk
ls -lh *.dex
dexdump -f classes.dex > dex_dump.txt
```

#### Solutions

Upgrade to latest AGP:
```kotlin
plugins {
    id("com.android.application") apply false
}
```

Manual R8 configuration (older AGP):
```properties
android.enableR8.fullMode=true
```

Use App Bundle for automatic optimization.

#### Best Practices

Enable R8 optimization:
```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
        }
    }
}
```

Monitor APK size in CI/CD. Use App Bundle instead of APK.

---

## Ответ (RU)

Проблема размера страницы DEX в 16 КБ — это проблема выравнивания памяти, влияющая на Android 6.0+, которая вызывает значительное раздувание приложения при оптимизации с помощью R8/ProGuard.

#### Проблема

Android использует 16 КБ страницы для DEX файлов. Method IDs должны быть выровнены по границе страницы, создавая потраченное место для отступов.

```
Без выравнивания: [Header][Strings][Methods][Code]
С выравниванием:  [Header][Strings][Padding][Methods][Code]
                                    ^^^^^^^^ Потеря места!
```

Влияние:
- Маленькие приложения (< 5 MB): увеличение на 20-40%
- Большие приложения (> 50 MB): увеличение на 5-15%
- Multi-DEX приложения: умноженный эффект

#### Решения

Обновите до последней версии AGP:
```kotlin
plugins {
    id("com.android.application")
}
```

Настройте R8 (старые версии AGP):
```properties
android.enableR8.fullMode=true
```

Используйте App Bundle для автоматической оптимизации.

#### Лучшие практики

Включите R8 оптимизацию:
```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
        }
    }
}
```

Мониторьте размер APK в CI/CD. Используйте App Bundle вместо APK.

---

## Follow-ups

- What happens if you use AGP versions older than 8.2?
- How does this issue affect Instant Apps?
- What's the difference between R8 and ProGuard in handling this issue?
- How do App Bundles mitigate the 16KB page size problem?
- What tools can help detect alignment issues in CI/CD?

## References

- [Android Developer Guide: Configure your build](https://developer.android.com/studio/build)
- [R8 Optimization Guide](https://developer.android.com/studio/build/shrink-code)
- [Android App Bundle](https://developer.android.com/guide/app-bundle)
- [APK Analyzer Documentation](https://developer.android.com/studio/build/analyze-apk)

## Related Questions

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]] - Build

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - Build
- [[q-android-build-optimization--android--medium]] - Build
- [[q-proguard-r8--android--medium]] - Build
- [[q-build-optimization-gradle--gradle--medium]] - Build
- [[q-kapt-ksp-migration--gradle--medium]] - Build

### Advanced (Harder)
- [[q-kotlin-dsl-builders--kotlin--hard]] - Build
