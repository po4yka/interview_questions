---
id: android-007
title: Play Feature Delivery and Dynamic Modules / Play Feature Delivery и динамические
  модули
aliases:
- Play Feature Delivery and Dynamic Modules
- Play Feature Delivery и динамические модули
topic: android
subtopics:
- app-bundle
- architecture-modularization
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-play-feature-delivery
- q-app-bundle-basics--android--medium
created: 2025-10-05
updated: 2025-01-25
tags:
- android/app-bundle
- android/architecture-modularization
- app-bundle
- difficulty/medium
- dynamic-modules
- modularization
- play-feature-delivery
sources:
- https://developer.android.com/guide/app-bundle/dynamic-delivery
date created: Sunday, October 12th 2025, 12:27:50 pm
date modified: Saturday, November 1st 2025, 5:43:33 pm
---

# Вопрос (RU)
> Что такое Play Feature Delivery и динамические модули?

# Question (EN)
> What is Play Feature Delivery and dynamic modules?

---

## Ответ (RU)

**Теория Play Feature Delivery:**
Play Feature Delivery использует возможности Android App Bundles для условной доставки функций приложения. Позволяет загружать функции по требованию или только на устройства с определенными возможностями, уменьшая размер начальной загрузки.

**Основные преимущества:**
- Уменьшение размера начальной загрузки
- Условная доставка функций
- Загрузка по требованию
- Оптимизация для разных устройств

**Создание динамического модуля:**
```groovy
// build.gradle динамического модуля
plugins {
    id 'com.android.dynamic-feature'
}

android {
    compileSdk 34

    defaultConfig {
        minSdk 21
        targetSdk 34
    }
}

dependencies {
    implementation project(':app')
}
```

**Связь с базовым модулем:**
```groovy
// build.gradle базового модуля
android {
    dynamicFeatures = [":dynamic_feature", ":dynamic_feature2"]
}
```

**Типы доставки:**
- Install-time - функции включаются при установке
- On-demand - функции загружаются по требованию
- Conditional - функции загружаются при определенных условиях

**Проверка доступности модуля:**
```kotlin
// Проверка доступности динамического модуля
val splitInstallManager = SplitInstallManagerFactory.create(context)
val request = SplitInstallRequest.newBuilder()
    .addModule("dynamic_feature")
    .build()

splitInstallManager.startInstall(request)
    .addOnSuccessListener { sessionId ->
        // Модуль успешно загружен
    }
    .addOnFailureListener { exception ->
        // Ошибка загрузки
    }
```

**Ограничения:**
- Максимум 50 модулей на устройство
- Максимум 10 удаляемых модулей
- Требует Android 5.0+ (API 21+)
- Необходимо включить SplitCompat

## Answer (EN)

**Play Feature Delivery Theory:**
Play Feature Delivery uses Android App Bundles capabilities for conditional feature delivery. Allows loading features on-demand or only on devices with specific capabilities, reducing initial download size.

**Main advantages:**
- Reduced initial download size
- Conditional feature delivery
- On-demand loading
- Device-specific optimization

**Creating dynamic module:**
```groovy
// build.gradle of dynamic module
plugins {
    id 'com.android.dynamic-feature'
}

android {
    compileSdk 34

    defaultConfig {
        minSdk 21
        targetSdk 34
    }
}

dependencies {
    implementation project(':app')
}
```

**Base module relationship:**
```groovy
// build.gradle of base module
android {
    dynamicFeatures = [":dynamic_feature", ":dynamic_feature2"]
}
```

**Delivery types:**
- Install-time - features included at installation
- On-demand - features loaded on demand
- Conditional - features loaded under specific conditions

**Module availability check:**
```kotlin
// Check dynamic module availability
val splitInstallManager = SplitInstallManagerFactory.create(context)
val request = SplitInstallRequest.newBuilder()
    .addModule("dynamic_feature")
    .build()

splitInstallManager.startInstall(request)
    .addOnSuccessListener { sessionId ->
        // Module successfully loaded
    }
    .addOnFailureListener { exception ->
        // Loading error
    }
```

**Limitations:**
- Maximum 50 modules per device
- Maximum 10 removable modules
- Requires Android 5.0+ (API 21+)
- Must enable SplitCompat

---

## Follow-ups

- How do you handle feature module dependencies?
- What are the performance implications of dynamic modules?
- How do you test dynamic feature delivery?


## References

- [Android App Bundle](https://developer.android.com/guide/app-bundle)


## Related Questions

### Prerequisites / Concepts

- [[c-play-feature-delivery]]


### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-gradle-basics--android--easy]] - Gradle basics

### Related (Same Level)
- [[q-app-bundle-basics--android--medium]] - App Bundle basics
- [[q-android-modularization--android--medium]] - Modularization
- [[q-play-console--android--medium]] - Play Console

### Advanced (Harder)
- [[q-app-bundle-advanced--android--hard]] - App Bundle advanced
- [[q-android-runtime-internals--android--hard]] - Runtime internals
