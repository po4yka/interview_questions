---
id: android-189
title: Play Feature Delivery / Play Feature Delivery
aliases: [App Bundle, Dynamic Feature Modules, Play Feature Delivery, Динамические модули]
topic: android
subtopics: [app-bundle, build-variants, gradle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-build-optimization--android--hard, q-modularization-strategies--android--hard, q-what-is-app-bundle--android--easy]
created: 2025-10-15
updated: 2025-10-30
tags: [android, android/app-bundle, android/build-variants, android/gradle, app-bundle, difficulty/medium, dynamic-modules]
sources: []
date created: Saturday, November 1st 2025, 1:03:33 pm
date modified: Saturday, November 1st 2025, 5:43:33 pm
---

# Вопрос (RU)

Что вы знаете о Play Feature Delivery?

# Question (EN)

What do you know about Play Feature Delivery?

---

## Ответ (RU)

**Play Feature Delivery** — технология Android App Bundles для условной доставки или загрузки функций по требованию. Позволяет уменьшить размер первоначальной установки и доставлять функциональность только когда она необходима пользователю.

Google Play генерирует оптимизированные APK для конкретной конфигурации устройства из App Bundle, поэтому пользователи загружают только нужный код и ресурсы.

### Типы Доставки Модулей

**1. Install-time** — модуль устанавливается автоматически вместе с приложением:

```xml
<!-- AndroidManifest.xml в feature-модуле -->
<dist:module dist:title="@string/feature_title">
    <dist:delivery>
        <dist:install-time />
    </dist:delivery>
</dist:module>
```

**2. On-demand** — модуль загружается после установки, когда пользователю нужна функция:

```kotlin
val request = SplitInstallRequest.newBuilder()
    .addModule("dynamic_feature")
    .build()

splitInstallManager.startInstall(request)
    .addOnSuccessListener { sessionId ->
        // ✅ Модуль загружается
    }
    .addOnFailureListener { exception ->
        // ❌ Обработка ошибки
    }
```

**3. Conditional** — модуль доставляется только на устройства с определёнными возможностями (AR, API level, регион):

```xml
<dist:module dist:title="@string/ar_feature">
    <dist:delivery>
        <dist:install-time>
            <dist:conditions>
                <dist:device-feature dist:name="android.hardware.camera.ar" />
            </dist:conditions>
        </dist:install-time>
    </dist:delivery>
</dist:module>
```

### Конфигурация Feature-модуля

```gradle
// Feature-модуль
plugins {
    id 'com.android.dynamic-feature'
}

dependencies {
    implementation project(':app')  // ✅ Зависимость от базового модуля
}
```

```gradle
// Базовый модуль app/build.gradle
android {
    dynamicFeatures = [":feature_camera", ":feature_payment"]
}
```

**Что НЕ включать в feature-модуль:**
- Конфигурации подписи (используется из базового модуля)
- `minifyEnabled` (настраивается только в базовом модуле)
- `versionCode`, `versionName` (берутся из базового модуля)

### Мониторинг Загрузки

```kotlin
private val listener = SplitInstallStateUpdatedListener { state ->
    when (state.status()) {
        SplitInstallSessionStatus.DOWNLOADING -> {
            val progress = state.bytesDownloaded() * 100 /
                          state.totalBytesToDownload()
            updateProgress(progress.toInt())
        }
        SplitInstallSessionStatus.INSTALLED -> {
            // ✅ Модуль установлен, может потребоваться recreate()
            if (state.moduleNames().contains("feature_x")) {
                recreate()
            }
        }
        SplitInstallSessionStatus.FAILED -> {
            // ❌ Ошибка установки
            handleError(state.errorCode())
        }
    }
}
```

### SplitCompat — Доступ К Загруженным Модулям

```kotlin
// Вариант 1: Наследование от SplitCompatApplication
class MyApplication : SplitCompatApplication()

// Вариант 2: Ручная установка
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        SplitCompat.install(this)
    }
}
```

### Проверка Установки Модуля

```kotlin
fun isModuleInstalled(moduleName: String): Boolean {
    return splitInstallManager.installedModules.contains(moduleName)
}

// ✅ Всегда проверяйте перед использованием
if (isModuleInstalled("ar_preview")) {
    launchARFeature()
} else {
    requestModuleInstall("ar_preview")
}
```

### Ограничения

1. **Лимит модулей**: 50+ feature-модулей → проблемы производительности
2. **Removable install-time**: максимум 10 модулей
3. **Минимальная версия**: Android 5.0+ для on-demand доставки
4. **SplitCompat**: обязателен для доступа к модулям
5. **Exported activities**: feature-модули не должны экспортировать активности (модуль может быть не загружен)

### Преимущества

- Уменьшение размера первоначальной установки на 30-60%
- Модульная архитектура и лучшая организация кода
- Целевая доставка по конфигурации устройства
- Возможность удаления неиспользуемых модулей
- Быстрые обновления отдельных модулей

### Примеры Использования

```
:app (базовый модуль — списки товаров, навигация)
:feature:auth (install-time — логин/регистрация)
:feature:seller (on-demand — функции для продавцов)
:feature:ar_preview (conditional — 3D-превью для AR-устройств)
:feature:analytics (deferred — фоновая загрузка аналитики)
```

---

## Answer (EN)

**Play Feature Delivery** is an Android App Bundles technology for conditional or on-demand feature delivery. It reduces initial download size by delivering functionality only when users need it.

Google Play generates optimized APKs for specific device configurations from App Bundles, so users download only the code and resources they need.

### Module Delivery Types

**1. Install-time** — module installed automatically with the app:

```xml
<!-- AndroidManifest.xml in feature module -->
<dist:module dist:title="@string/feature_title">
    <dist:delivery>
        <dist:install-time />
    </dist:delivery>
</dist:module>
```

**2. On-demand** — module downloaded after installation when user needs the feature:

```kotlin
val request = SplitInstallRequest.newBuilder()
    .addModule("dynamic_feature")
    .build()

splitInstallManager.startInstall(request)
    .addOnSuccessListener { sessionId ->
        // ✅ Module is being downloaded
    }
    .addOnFailureListener { exception ->
        // ❌ Handle failure
    }
```

**3. Conditional** — module delivered only to devices with specific capabilities (AR, API level, region):

```xml
<dist:module dist:title="@string/ar_feature">
    <dist:delivery>
        <dist:install-time>
            <dist:conditions>
                <dist:device-feature dist:name="android.hardware.camera.ar" />
            </dist:conditions>
        </dist:install-time>
    </dist:delivery>
</dist:module>
```

### Feature Module Configuration

```gradle
// Feature module
plugins {
    id 'com.android.dynamic-feature'
}

dependencies {
    implementation project(':app')  // ✅ Dependency on base module
}
```

```gradle
// Base module app/build.gradle
android {
    dynamicFeatures = [":feature_camera", ":feature_payment"]
}
```

**What NOT to include in feature module:**
- Signing configurations (inherited from base module)
- `minifyEnabled` (configured only in base module)
- `versionCode`, `versionName` (taken from base module)

### Download Monitoring

```kotlin
private val listener = SplitInstallStateUpdatedListener { state ->
    when (state.status()) {
        SplitInstallSessionStatus.DOWNLOADING -> {
            val progress = state.bytesDownloaded() * 100 /
                          state.totalBytesToDownload()
            updateProgress(progress.toInt())
        }
        SplitInstallSessionStatus.INSTALLED -> {
            // ✅ Module installed, may need recreate()
            if (state.moduleNames().contains("feature_x")) {
                recreate()
            }
        }
        SplitInstallSessionStatus.FAILED -> {
            // ❌ Installation error
            handleError(state.errorCode())
        }
    }
}
```

### SplitCompat — Accessing Downloaded Modules

```kotlin
// Option 1: Extend SplitCompatApplication
class MyApplication : SplitCompatApplication()

// Option 2: Manual installation
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        SplitCompat.install(this)
    }
}
```

### Checking Module Installation

```kotlin
fun isModuleInstalled(moduleName: String): Boolean {
    return splitInstallManager.installedModules.contains(moduleName)
}

// ✅ Always check before using
if (isModuleInstalled("ar_preview")) {
    launchARFeature()
} else {
    requestModuleInstall("ar_preview")
}
```

### Limitations

1. **Module limit**: 50+ feature modules → performance issues
2. **Removable install-time**: max 10 modules
3. **Minimum version**: Android 5.0+ for on-demand delivery
4. **SplitCompat**: required for module access
5. **Exported activities**: feature modules should not export activities (module may not be downloaded)

### Benefits

- 30-60% reduction in initial download size
- Modular architecture and better code organization
- Targeted delivery based on device configuration
- Ability to uninstall unused modules
- Fast updates of individual modules

### Example Use Cases

```
:app (base module — product listings, navigation)
:feature:auth (install-time — login/registration)
:feature:seller (on-demand — seller functionality)
:feature:ar_preview (conditional — 3D preview for AR devices)
:feature:analytics (deferred — background analytics download)
```

---

## Follow-ups

1. How do you handle lifecycle of dynamically loaded activities from feature modules?
2. What happens when a user tries to access a feature module that failed to download?
3. How does ProGuard/R8 work with feature modules and code obfuscation?
4. Can feature modules share resources or code between each other without going through the base module?
5. What are the testing strategies for on-demand modules (local testing, staging, production validation)?

## References

- [[c-app-bundle]]
- [[c-gradle-build-system]]
- https://developer.android.com/guide/playcore/feature-delivery

## Related Questions

### Prerequisites (Easier)

- [[q-what-is-app-bundle--android--easy]]
- [[q-gradle-basics--android--easy]]

### Related (Same Level)

- [[q-anr-application-not-responding--android--medium]]
- [[q-handler-looper-comprehensive--android--medium]]

### Advanced (Harder)

- [[q-modularization-patterns--android--hard]]
- [[q-build-optimization--android--hard]]
