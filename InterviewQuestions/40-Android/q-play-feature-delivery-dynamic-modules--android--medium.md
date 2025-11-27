---
id: android-007
title: Play Feature Delivery and Dynamic Modules / Play Feature Delivery и динамические модули
aliases: [Play Feature Delivery and Dynamic Modules, Play Feature Delivery и динамические модули]
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
  - c-app-bundle
  - q-android-app-bundles--android--easy
  - q-play-asset-delivery-strategy--android--hard
  - q-play-billing-v6-architecture--android--hard
  - q-play-feature-delivery--android--medium
created: 2025-10-05
updated: 2025-11-11
tags: [android/app-bundle, android/architecture-modularization, app-bundle, difficulty/medium, dynamic-modules, modularization, play-feature-delivery]
sources:
  - "https://developer.android.com/guide/app-bundle/dynamic-delivery"

date created: Saturday, November 1st 2025, 1:03:33 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---
# Вопрос (RU)
> Что такое Play Feature Delivery и динамические модули?

# Question (EN)
> What is Play Feature Delivery and dynamic modules?

---

## Ответ (RU)

**Теория Play Feature Delivery:**
Play Feature Delivery — механизм Google Play, использующий Android App `Bundle` (AAB) для доставки динамических feature-модулей. Он позволяет:
- включать некоторые модули в установку (install-time),
- загружать функции по требованию (on-demand),
- доставлять их только на устройства с определёнными условиями (conditional delivery),
что уменьшает размер начальной загрузки и оптимизирует доставку функциональности.

Динамические модули — это модули с плагином `com.android.dynamic-feature`, которые зависят от базового модуля и поставляются только через App `Bundle` (не поддерживаются в standalone APK-сборке).

**Основные преимущества:**
- Уменьшение размера начальной установки (base APK меньше)
- Условная доставка функций (по стране, версии SDK, capabilities и т.п.)
- Загрузка по требованию, когда пользователь реально доходит до функциональности
- Оптимизация под разные устройства и сценарии использования

**Создание динамического модуля (упрощённый пример):**
```groovy
// build.gradle динамического модуля (module: dynamic_feature)
plugins {
    id 'com.android.dynamic-feature'
}

android {
    compileSdk 34

    defaultConfig {
        minSdk 21
        targetSdk 34
    }

    // namespace должен отличаться от базового, но быть согласованным
    namespace 'com.example.app.dynamic_feature'
}

dependencies {
    // Динамический модуль зависит от базового приложения
    implementation project(':app')
}
```

**Связь с базовым модулем:**
```groovy
// build.gradle базового модуля (обычно :app)
plugins {
    id 'com.android.application'
}

android {
    // Перечень подключённых dynamic feature модулей
    dynamicFeatures = [":dynamic_feature", ":dynamic_feature2"]
}
```

**Типы доставки (Play Feature Delivery):**
- Install-time — модуль устанавливается вместе с базовым приложением.
- On-demand — модуль загружается по запросу во время работы (через Play Core / Play In-App Updates API).
- Conditional — модуль устанавливается автоматически, если выполняются заданные условия (API level, страна, размер экрана, capabilities и др.).

**Запрос установки динамического модуля:**
```kotlin
// Загрузка dynamic feature модуля по требованию
val splitInstallManager = SplitInstallManagerFactory.create(context)
val request = SplitInstallRequest.newBuilder()
    .addModule("dynamic_feature") // имя модуля из settings.gradle
    .build()

splitInstallManager.startInstall(request)
    .addOnSuccessListener { sessionId ->
        // Запрос установки принят, можно отслеживать прогресс по sessionId
    }
    .addOnFailureListener { exception ->
        // Ошибка при запросе установки модуля
    }
```

Проверить, установлен ли модуль, можно, например, через:
```kotlin
val installedModules = splitInstallManager.installedModules
val isInstalled = "dynamic_feature" in installedModules
```

**Ограничения и особенности:**
- Динамические feature-модули доступны только при распространении через Android App `Bundle` в Google Play.
- Требуется minSdkVersion >= 21.
- На устройствах до Android 10 (API < 29) для доступа к коду/ресурсам динамических модулей из не-базовых контекстов может понадобиться включить SplitCompat.
- На практике существует ограничение на количество динамических модулей/asset packs (например, до 50), а также на число "removable" модулей; конкретные лимиты определяются текущими правилами Play и могут изменяться, их нужно уточнять в актуальной документации.

---

## Answer (EN)

**Play Feature Delivery theory:**
Play Feature Delivery is a Google Play mechanism built on top of Android App Bundles (AAB) that delivers dynamic feature modules. It allows you to:
- include some modules at install-time,
- download features on-demand at runtime,
- deliver features only to devices that meet specific conditions (conditional delivery),
which reduces the initial download size and optimizes how functionality is delivered.

Dynamic modules are modules that use the `com.android.dynamic-feature` plugin, depend on the base module, and are delivered only via App Bundles (they are not supported as standalone APK builds).

**Main advantages:**
- Smaller initial install (base APK is lighter)
- Conditional delivery (based on country, SDK version, capabilities, etc.)
- On-demand loading when the user actually reaches the feature
- Better optimization for different devices and usage scenarios

**Creating a dynamic module (simplified example):**
```groovy
// build.gradle of dynamic feature module (module: dynamic_feature)
plugins {
    id 'com.android.dynamic-feature'
}

android {
    compileSdk 34

    defaultConfig {
        minSdk 21
        targetSdk 34
    }

    // namespace should be distinct but consistent with the base module
    namespace 'com.example.app.dynamic_feature'
}

dependencies {
    // Dynamic feature depends on the base app module
    implementation project(':app')
}
```

**Base module relationship:**
```groovy
// build.gradle of base module (usually :app)
plugins {
    id 'com.android.application'
}

android {
    // List of dynamic feature modules attached to the base
    dynamicFeatures = [":dynamic_feature", ":dynamic_feature2"]
}
```

**Delivery types (Play Feature Delivery):**
- Install-time — feature is installed together with the base app.
- On-demand — feature is downloaded on demand at runtime (via Play Core / Play APIs).
- Conditional — feature is automatically installed only if specified conditions are met (API level, country, screen size, capabilities, etc.).

**Requesting a dynamic module installation:**
```kotlin
// Request download/installation of a dynamic feature module on demand
val splitInstallManager = SplitInstallManagerFactory.create(context)
val request = SplitInstallRequest.newBuilder()
    .addModule("dynamic_feature") // module name as in settings.gradle
    .build()

splitInstallManager.startInstall(request)
    .addOnSuccessListener { sessionId ->
        // Install request accepted; you can track progress using sessionId
    }
    .addOnFailureListener { exception ->
        // Error requesting module installation
    }
```

To check whether a module is already installed:
```kotlin
val installedModules = splitInstallManager.installedModules
val isInstalled = "dynamic_feature" in installedModules
```

**Limitations and considerations:**
- Dynamic feature modules are supported when distributing via Android App `Bundle` through Google Play.
- Requires minSdkVersion >= 21.
- On devices before Android 10 (API < 29), SplitCompat may be required to access code/resources from dynamic modules in some contexts.
- There are practical limits on the number of dynamic feature modules/asset packs (e.g., around 50) and removable modules; these are defined by current Play policies and may change, so always consult up-to-date documentation.

---

## Follow-ups (RU)

- Как вы обрабатываете зависимости между feature-модулями?
- Каковы производительные последствия использования динамических модулей?
- Как вы тестируете доставку динамических модулей?

---

## Follow-ups

- How do you handle feature module dependencies?
- What are the performance implications of dynamic modules?
- How do you test dynamic feature delivery?

---

## Ссылки (RU)

- [Android App `Bundle`](https://developer.android.com/guide/app-bundle)

## References

- [Android App `Bundle`](https://developer.android.com/guide/app-bundle)

---

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-app-bundle]]

### Предпосылки (Проще)
- [[q-android-app-components--android--easy]] - Компоненты приложения
- [[q-gradle-basics--android--easy]] - Основы Gradle

### Связанные (Такой Же уровень)
- [[q-android-app-bundles--android--easy]] - Основы App `Bundle`
- [[q-android-modularization--android--medium]] - Модульная архитектура

### Продвинутые (Сложнее)
- [[q-android-runtime-internals--android--hard]] - Внутреннее устройство рантайма

## Related Questions

### Prerequisites / Concepts

- [[c-app-bundle]]

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-gradle-basics--android--easy]] - Gradle basics

### Related (Same Level)
- [[q-android-app-bundles--android--easy]] - App `Bundle` basics
- [[q-android-modularization--android--medium]] - Modularization

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - Runtime internals
