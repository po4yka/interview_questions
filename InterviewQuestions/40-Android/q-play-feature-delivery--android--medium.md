---
id: "20251015082237340"
title: "Play Feature Delivery"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [play-feature-delivery, dynamic-modules, app-bundle, difficulty/medium]
---
# Play Feature Delivery / Play Feature Delivery

**English**: What do you know about Play Feature Delivery?

## Answer (EN)
**Play Feature Delivery** uses advanced capabilities of Android App Bundles, allowing certain features of your app to be **delivered conditionally or downloaded on demand**. This enables you to reduce initial download size and deliver features only when needed.

Google Play's app serving model uses Android App Bundles to generate and serve optimized APKs for each user's device configuration, so users download only the code and resources they need to run your app.

To implement Play Feature Delivery, you need to separate features from your base app into **feature modules**.

**Feature Module Build Configuration:**

When you create a new feature module using Android Studio, the IDE applies the following Gradle plugin:

```gradle
// The dynamic-feature plugin is required for feature modules
plugins {
    id 'com.android.dynamic-feature'
}
```

Many of the properties available to the standard application plugin are also available to feature modules.

**What NOT to include in feature module build configuration:**

Because each feature module depends on the base module, it inherits certain configurations. You should omit the following:

1. **Signing configurations**: App bundles are signed using signing configurations from the base module

2. **The `minifyEnabled` property**: Enable code shrinking for your entire app project from only the base module's build configuration. You can specify additional ProGuard rules for each feature module

3. **`versionCode` and `versionName`**: When building your app bundle, Gradle uses app version information that the base module provides

**Establishing relationship to the base module:**

When Android Studio creates your feature module, it makes it visible to the base module:

```gradle
// In the base module's build.gradle file
android {
    ...
    // Specifies feature modules that have a dependency on this base module
    dynamicFeatures = [":dynamic_feature", ":dynamic_feature2"]
}
```

Additionally, the feature module includes the base module as a dependency:

```gradle
// In the feature module's build.gradle file
dependencies {
    ...
    // Declares a dependency on the base module, ':app'
    implementation project(':app')
}
```

**Delivery Options:**

**1. Install-time delivery:**

Features delivered at install time are installed automatically when the app is installed. This is the default delivery option.

```xml
<!-- AndroidManifest.xml in feature module -->
<manifest ...>
    <dist:module
        dist:instant="false"
        dist:title="@string/feature_title">
        <dist:delivery>
            <dist:install-time />
        </dist:delivery>
    </dist:module>
</manifest>
```

**2. On-demand delivery:**

Features delivered on demand can be downloaded and installed after app installation, when the user needs them.

```xml
<manifest ...>
    <dist:module
        dist:instant="false"
        dist:title="@string/feature_title">
        <dist:delivery>
            <dist:on-demand />
        </dist:delivery>
    </dist:module>
</manifest>
```

**Requesting on-demand module:**

```kotlin
// Create a request
val request = SplitInstallRequest.newBuilder()
    .addModule("dynamic_feature")
    .build()

// Start the installation
splitInstallManager.startInstall(request)
    .addOnSuccessListener { sessionId ->
        // Handle successful request
    }
    .addOnFailureListener { exception ->
        // Handle failure
    }
```

**3. Conditional delivery:**

Deliver features based on device capabilities (features, API level, user country, etc.):

```xml
<manifest ...>
    <dist:module
        dist:instant="false"
        dist:title="@string/ar_feature_title">
        <dist:delivery>
            <dist:install-time>
                <dist:conditions>
                    <!-- Only deliver to devices with AR support -->
                    <dist:device-feature dist:name="android.hardware.camera.ar" />
                </dist:conditions>
            </dist:install-time>
        </dist:delivery>
    </dist:module>
</manifest>
```

**Real-World Example:**

Consider an app that allows users to buy and sell goods in an online marketplace. You can modularize features:

```
:app (base module)
 :feature:login (install-time)
 :feature:browse (install-time)
 :feature:sell (on-demand - only for sellers)
 :feature:payment (on-demand - only when needed)
 :feature:ar-preview (conditional - AR-capable devices only)
```

**Monitoring Download Progress:**

```kotlin
class MyActivity : AppCompatActivity() {
    private lateinit var splitInstallManager: SplitInstallManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        splitInstallManager = SplitInstallManagerFactory.create(this)

        // Register listener
        splitInstallManager.registerListener(listener)
    }

    private val listener = SplitInstallStateUpdatedListener { state ->
        when (state.status()) {
            SplitInstallSessionStatus.DOWNLOADING -> {
                val progress = (state.bytesDownloaded() * 100 / state.totalBytesToDownload()).toInt()
                updateProgressBar(progress)
            }
            SplitInstallSessionStatus.INSTALLED -> {
                // Module installed successfully
                // Might need to recreate activity
                if (state.moduleNames().contains("dynamic_feature")) {
                    recreate()
                }
            }
            SplitInstallSessionStatus.FAILED -> {
                // Handle installation failure
                showError(state.errorCode())
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        splitInstallManager.unregisterListener(listener)
    }
}
```

**Checking if module is installed:**

```kotlin
fun isModuleInstalled(moduleName: String): Boolean {
    return splitInstallManager.installedModules.contains(moduleName)
}

// Usage
if (isModuleInstalled("ar_preview")) {
    // Launch AR feature
    launchARPreview()
} else {
    // Request module download
    requestModuleInstall("ar_preview")
}
```

**Deferred Installation:**

Request installation but don't wait for it:

```kotlin
val request = SplitInstallRequest.newBuilder()
    .addModule("background_feature")
    .build()

splitInstallManager.deferredInstall(listOf("background_feature"))
    .addOnSuccessListener {
        // Installation will happen in the background
    }
```

**Canceling Installation:**

```kotlin
splitInstallManager.cancelInstall(sessionId)
```

**Uninstalling a module:**

```kotlin
splitInstallManager.deferredUninstall(listOf("feature_to_remove"))
    .addOnSuccessListener {
        // Module will be uninstalled
    }
```

**Considerations and Limitations:**

1. **Module limit**: Installing 50 or more feature modules on a single device might lead to performance issues. Install-time modules configured as removable count separately

2. **Removable install-time modules**: Limit to 10 or fewer, otherwise download/install time increases

3. **Android version**: Only devices running Android 5.0 (API level 21) and higher support on-demand delivery. Enable **Fusing** for earlier versions

4. **SplitCompat**: Enable SplitCompat so your app has access to downloaded feature modules

5. **Exported activities**: Feature modules should not specify activities with `android:exported` set to `true` because there's no guarantee the module is downloaded

6. **Check before access**: Always confirm a feature is downloaded before accessing its code/resources

**Enable SplitCompat:**

```kotlin
// Option 1: In Application class
class MyApplication : SplitCompatApplication() {
    // SplitCompat is automatically installed
}

// Option 2: Manual installation
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        SplitCompat.install(this)
    }
}

// Option 3: Per-activity
class MyActivity : AppCompatActivity() {
    override fun attachBaseContext(newBase: Context) {
        super.attachBaseContext(newBase)
        SplitCompat.install(this)
    }
}
```

**Dependencies:**

```gradle
// app/build.gradle
dependencies {
    implementation "com.google.android.play:core:1.10.3"
    // Or the newer version
    implementation "com.google.android.play:feature-delivery:2.1.0"
}
```

**Benefits:**

-  **Reduced initial download size** — users download only what they need
-  **Modular architecture** — better code organization
-  **Targeted delivery** — features only for specific devices/conditions
-  **Storage savings** — users can uninstall unused features
-  **Faster updates** — update individual modules without updating entire app

**Use Cases:**

- AR features (only for AR-capable devices)
- Advanced camera features (only for devices with certain cameras)
- Regional features (only for specific countries)
- Premium features (download when user subscribes)
- Heavy assets (download when user needs them)
- Educational content (download lessons as needed)

**Summary:**

- **Play Feature Delivery**: Advanced delivery options for app features
- **Delivery types**: Install-time, on-demand, conditional
- **Requirements**: Android 5.0+, SplitCompat, feature modules
- **Benefits**: Reduced download size, modular architecture, targeted delivery
- **Limitations**: Module count limits, version requirements, complexity
- **Use cases**: AR features, regional content, premium features, large assets

**Source**: [Overview of Play Feature Delivery](https://developer.android.com/guide/playcore/feature-delivery)

## Ответ (RU)
**Play Feature Delivery** использует расширенные возможности Android App Bundles, позволяя доставлять определённые функции приложения **условно или по требованию**. Это позволяет уменьшить размер первоначальной загрузки и доставлять функции только когда они нужны.

Google Play использует Android App Bundles для генерации и доставки оптимизированных APK для каждой конфигурации устройства пользователя, поэтому пользователи загружают только необходимый код и ресурсы.

Для реализации Play Feature Delivery необходимо отделить функции от базового приложения в **feature модули**.

**Конфигурация feature модуля:**

```gradle
// Плагин dynamic-feature необходим для feature модулей
plugins {
    id 'com.android.dynamic-feature'
}
```

**Что НЕ включать в конфигурацию feature модуля:**

1. **Конфигурации подписи** — App Bundle подписываются конфигурацией из базового модуля
2. **Свойство `minifyEnabled`** — сжатие кода включается только из базового модуля
3. **`versionCode` и `versionName`** — Gradle использует информацию о версии из базового модуля

**Связь с базовым модулем:**

```gradle
// В build.gradle базового модуля
android {
    dynamicFeatures = [":dynamic_feature", ":dynamic_feature2"]
}

// В build.gradle feature модуля
dependencies {
    implementation project(':app')
}
```

**Варианты доставки:**

**1. Install-time delivery (доставка при установке):**

```xml
<dist:module dist:title="@string/feature_title">
    <dist:delivery>
        <dist:install-time />
    </dist:delivery>
</dist:module>
```

**2. On-demand delivery (доставка по требованию):**

```xml
<dist:module dist:title="@string/feature_title">
    <dist:delivery>
        <dist:on-demand />
    </dist:delivery>
</dist:module>
```

**Запрос модуля по требованию:**

```kotlin
val request = SplitInstallRequest.newBuilder()
    .addModule("dynamic_feature")
    .build()

splitInstallManager.startInstall(request)
    .addOnSuccessListener { sessionId ->
        // Обработка успешного запроса
    }
    .addOnFailureListener { exception ->
        // Обработка ошибки
    }
```

**3. Conditional delivery (условная доставка):**

```xml
<dist:module dist:title="@string/ar_feature_title">
    <dist:delivery>
        <dist:install-time>
            <dist:conditions>
                <!-- Только для устройств с поддержкой AR -->
                <dist:device-feature dist:name="android.hardware.camera.ar" />
            </dist:conditions>
        </dist:install-time>
    </dist:delivery>
</dist:module>
```

**Пример реального приложения:**

```
:app (базовый модуль)
 :feature:login (install-time)
 :feature:browse (install-time)
 :feature:sell (on-demand - только для продавцов)
 :feature:payment (on-demand - только при необходимости)
 :feature:ar-preview (conditional - только AR-устройства)
```

**Мониторинг прогресса загрузки:**

```kotlin
private val listener = SplitInstallStateUpdatedListener { state ->
    when (state.status()) {
        SplitInstallSessionStatus.DOWNLOADING -> {
            val progress = (state.bytesDownloaded() * 100 / state.totalBytesToDownload()).toInt()
            updateProgressBar(progress)
        }
        SplitInstallSessionStatus.INSTALLED -> {
            // Модуль успешно установлен
            recreate()
        }
        SplitInstallSessionStatus.FAILED -> {
            showError(state.errorCode())
        }
    }
}
```

**Проверка установки модуля:**

```kotlin
fun isModuleInstalled(moduleName: String): Boolean {
    return splitInstallManager.installedModules.contains(moduleName)
}
```

**Ограничения и соображения:**

1. **Лимит модулей**: Установка 50+ feature модулей может привести к проблемам производительности
2. **Removable install-time модули**: Ограничьте до 10 или меньше
3. **Версия Android**: Только Android 5.0+ поддерживает on-demand доставку
4. **SplitCompat**: Необходимо включить для доступа к загруженным модулям
5. **Exported activities**: Feature модули не должны экспортировать активности
6. **Проверка перед доступом**: Всегда подтверждайте, что feature загружен

**Включение SplitCompat:**

```kotlin
// Вариант 1: В Application классе
class MyApplication : SplitCompatApplication()

// Вариант 2: Ручная установка
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        SplitCompat.install(this)
    }
}
```

**Преимущества:**

- Уменьшенный размер первоначальной загрузки
- Модульная архитектура
- Целевая доставка для определённых устройств
- Экономия хранилища
- Более быстрые обновления

**Случаи использования:**

- AR функции (только для AR-устройств)
- Региональные функции
- Премиум функции (загрузка при подписке)
- Тяжёлые ресурсы
- Образовательный контент

**Резюме:**

Play Feature Delivery предоставляет расширенные опции доставки функций приложения через App Bundles. Поддерживает три типа доставки: при установке, по требованию и условную. Требует Android 5.0+, SplitCompat и feature модули. Основные преимущества: уменьшенный размер загрузки, модульная архитектура, целевая доставка.
