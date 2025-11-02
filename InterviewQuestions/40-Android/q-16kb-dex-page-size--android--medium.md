---
id: android-483
title: 16kb Dex Page Size / Размер страницы DEX 16KB
aliases: [16KB DEX Page Size, 16 КБ страница DEX]
topic: android
subtopics: [gradle, performance-memory]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-gradle, c-app-bundle, q-proguard-r8--android--medium, q-build-optimization-gradle--android--medium, q-android-app-bundles--android--easy]
created: 2025-10-25
updated: 2025-10-29
sources: []
tags: [android/gradle, android/performance-memory, difficulty/medium]
date created: Wednesday, October 29th 2025, 4:18:15 pm
date modified: Thursday, October 30th 2025, 11:12:44 am
---

# Вопрос (RU)
> Что такое проблема размера страницы DEX 16KB в Android?

---

# Question (EN)
> What is the 16KB DEX page size issue in Android?

---

## Ответ (RU)

Проблема размера страницы DEX 16KB - это проблема выравнивания памяти в Android 6.0+, вызывающая раздувание размера приложения при оптимизации с R8/ProGuard.

**Причина**: Android использует страницы по 16 KB для DEX-файлов. ID методов выравниваются по границам страниц, создавая пустое место:

```
Без выравнивания: [Header][Strings][Methods][Code]
С выравниванием:  [Header][Strings][Padding][Methods][Code]  ✅ Правильно
                                   ^^^^^^^^ Потерянное место   ❌ Неэффективно
```

**Влияние**:
- Малые приложения (< 5 MB): +20-40% размера
- Большие приложения (> 50 MB): +5-15% размера

**Решение**:
```kotlin
// ✅ Обновить AGP до последней версии
plugins {
    id("com.android.application") version "8.2+"  // ✅ Автоматическая оптимизация
}

// ✅ Включить R8
android {
    buildTypes {
        release {
            isMinifyEnabled = true          // ✅ Обязательно
            isShrinkResources = true        // ✅ Рекомендуется
        }
    }
}
```

**Лучшие практики**:
- Использовать App Bundle вместо APK
- Мониторить размер в CI/CD

---

## Answer (EN)

The 16 KB DEX page size issue is a memory alignment problem affecting Android 6.0+ that causes app bloat when optimized with R8/ProGuard.

**Cause**: Android uses 16 KB pages for DEX files. Method IDs align to page boundaries, creating wasted padding:

```
Without alignment: [Header][Strings][Methods][Code]
With alignment:    [Header][Strings][Padding][Methods][Code]  ✅ Correct
                                    ^^^^^^^^ Wasted space      ❌ Inefficient
```

**Impact**:
- Small apps (< 5 MB): +20-40% size increase
- Large apps (> 50 MB): +5-15% size increase

**Solution**:
```kotlin
// ✅ Upgrade to latest AGP
plugins {
    id("com.android.application") version "8.2+"  // ✅ Auto-optimization
}

// ✅ Enable R8
android {
    buildTypes {
        release {
            isMinifyEnabled = true          // ✅ Required
            isShrinkResources = true        // ✅ Recommended
        }
    }
}
```

**Best practices**:
- Use App Bundle instead of APK
- Monitor size in CI/CD

---

## Follow-ups

- How do App Bundles mitigate this issue?
- What's the difference between R8 and ProGuard handling?
- How to detect alignment issues in CI/CD?
- Why does R8 optimization sometimes increase APK size?
- How does dex page alignment affect cold start performance?

## References

- [[c-gradle]] - Build system
- [[c-app-bundle]] - App distribution format
- [R8 Optimization](https://developer.android.com/studio/build/shrink-code)
- [App Bundle Guide](https://developer.android.com/guide/app-bundle)
- [DEX Format Specification](https://source.android.com/docs/core/runtime/dex-format)

## Related Questions

### Prerequisites (Easy)
- [[q-gradle-basics--android--easy]]
- [[q-android-app-bundles--android--easy]]

### Related (Medium)
- [[q-proguard-r8--android--medium]]
- [[q-build-optimization-gradle--android--medium]]
- [[q-gradle-build-system--android--medium]]

### Advanced (Hard)
- APK size analysis and optimization strategies
- Custom R8 rules for extreme size reduction
