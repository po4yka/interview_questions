---
id: 20251012-122769
title: Android Project Parts / Части Android проекта
aliases: [Android Project Parts, Части Android проекта]
topic: android
subtopics: [project-structure, gradle, resources]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
created: 2025-10-15
updated: 2025-10-15
tags: [android/project-structure, android/gradle, android/resources, assets, gradle, manifest, project-structure, resources, difficulty/easy]
related: [q-android-manifest-file--android--easy, q-gradle-build-system--android--medium, q-android-modularization--android--medium]
---
# Question (EN)
> What parts make up an Android project and what is each part responsible for?

# Вопрос (RU)
> Из каких частей состоит Android-проект и какая часть за что отвечает?

---

## Answer (EN)

**Android Project Structure** consists of organized directories and files that serve specific purposes in app development. Each part has a clear responsibility for code organization, resource management, and build configuration.

**Project Structure Theory:**
Android projects follow a standardized structure that separates concerns: source code, resources, configuration, and build files. This organization enables proper compilation, resource management, and deployment while maintaining clear separation between different types of content.

**Core Project Components:**
- **src/**: Source code (Kotlin/Java)
- **res/**: Compiled resources (layouts, strings, images)
- **AndroidManifest.xml**: App configuration and component declarations
- **build.gradle**: Build configuration and dependencies
- **assets/**: Raw files accessible at runtime

**Basic Project Structure:**
```
app/
├── src/main/
│   ├── java/com/example/app/     # Source code
│   ├── res/                      # Resources
│   │   ├── layout/              # XML layouts
│   │   ├── values/              # Strings, colors, dimensions
│   │   └── drawable/            # Images, icons
│   ├── assets/                  # Raw files
│   └── AndroidManifest.xml      # App configuration
├── build.gradle.kts             # Build configuration
└── proguard-rules.pro           # Code obfuscation rules
```

**Source Code Organization:**
```kotlin
// src/main/java/com/example/app/MainActivity.kt
package com.example.app

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**Resource Structure:**
```
res/
├── layout/                      # UI layouts
│   └── activity_main.xml
├── values/                      # App values
│   ├── strings.xml             # Text strings
│   ├── colors.xml              # Color definitions
│   └── dimens.xml              # Dimension values
├── drawable/                    # Images and icons
│   └── ic_launcher.xml
└── mipmap-*/                   # App icons (different densities)
    └── ic_launcher.png
```

**Resource Access in Code:**
```kotlin
// Access resources via R class
val appName = getString(R.string.app_name)
val color = getColor(R.color.primary_color)
val icon = getDrawable(R.drawable.ic_home)
val padding = resources.getDimensionPixelSize(R.dimen.default_padding)
```

**AndroidManifest.xml Configuration:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/AppTheme">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

**Build Configuration:**
```kotlin
// build.gradle.kts
android {
    namespace = "com.example.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
}
```

**Assets vs Resources:**
- **Resources (res/)**: Compiled, optimized, accessed via R class
- **Assets (assets/)**: Raw files, accessed via AssetManager

**Asset Access:**
```kotlin
// Read from assets
val inputStream = assets.open("config/settings.json")
val json = inputStream.bufferedReader().use { it.readText() }

// Load HTML in WebView
webView.loadUrl("file:///android_asset/html/about.html")
```

**Key Differences:**
- **res/**: UI resources, compiled at build time, type-safe access
- **assets/**: Data files, raw access at runtime, string-based paths
- **src/**: Source code, compiled to bytecode
- **AndroidManifest.xml**: App metadata, component declarations
- **build.gradle**: Build configuration, dependency management

## Ответ (RU)

**Структура Android проекта** состоит из организованных директорий и файлов, которые служат конкретным целям в разработке приложений. Каждая часть имеет чёткую ответственность за организацию кода, управление ресурсами и конфигурацию сборки.

**Теория структуры проекта:**
Android проекты следуют стандартизированной структуре, которая разделяет ответственности: исходный код, ресурсы, конфигурация и файлы сборки. Эта организация обеспечивает правильную компиляцию, управление ресурсами и развёртывание при сохранении чёткого разделения между различными типами контента.

**Основные компоненты проекта:**
- **src/**: Исходный код (Kotlin/Java)
- **res/**: Скомпилированные ресурсы (макеты, строки, изображения)
- **AndroidManifest.xml**: Конфигурация приложения и объявления компонентов
- **build.gradle**: Конфигурация сборки и зависимости
- **assets/**: Сырые файлы, доступные в рантайме

**Базовая структура проекта:**
```
app/
├── src/main/
│   ├── java/com/example/app/     # Исходный код
│   ├── res/                      # Ресурсы
│   │   ├── layout/              # XML макеты
│   │   ├── values/              # Строки, цвета, размеры
│   │   └── drawable/            # Изображения, иконки
│   ├── assets/                  # Сырые файлы
│   └── AndroidManifest.xml      # Конфигурация приложения
├── build.gradle.kts             # Конфигурация сборки
└── proguard-rules.pro           # Правила обфускации кода
```

**Организация исходного кода:**
```kotlin
// src/main/java/com/example/app/MainActivity.kt
package com.example.app

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**Структура ресурсов:**
```
res/
├── layout/                      # UI макеты
│   └── activity_main.xml
├── values/                      # Значения приложения
│   ├── strings.xml             # Текстовые строки
│   ├── colors.xml              # Определения цветов
│   └── dimens.xml              # Значения размеров
├── drawable/                    # Изображения и иконки
│   └── ic_launcher.xml
└── mipmap-*/                   # Иконки приложения (разные плотности)
    └── ic_launcher.png
```

**Доступ к ресурсам в коде:**
```kotlin
// Доступ к ресурсам через R класс
val appName = getString(R.string.app_name)
val color = getColor(R.color.primary_color)
val icon = getDrawable(R.drawable.ic_home)
val padding = resources.getDimensionPixelSize(R.dimen.default_padding)
```

**Конфигурация AndroidManifest.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/AppTheme">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

**Конфигурация сборки:**
```kotlin
// build.gradle.kts
android {
    namespace = "com.example.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
}
```

**Assets vs Resources:**
- **Resources (res/)**: Скомпилированные, оптимизированные, доступ через R класс
- **Assets (assets/)**: Сырые файлы, доступ через AssetManager

**Доступ к Assets:**
```kotlin
// Чтение из assets
val inputStream = assets.open("config/settings.json")
val json = inputStream.bufferedReader().use { it.readText() }

// Загрузка HTML в WebView
webView.loadUrl("file:///android_asset/html/about.html")
```

**Ключевые различия:**
- **res/**: UI ресурсы, компиляция во время сборки, типобезопасный доступ
- **assets/**: Файлы данных, сырой доступ в рантайме, строковые пути
- **src/**: Исходный код, компиляция в байт-код
- **AndroidManifest.xml**: Метаданные приложения, объявления компонентов
- **build.gradle**: Конфигурация сборки, управление зависимостями

---

## Follow-ups

- How to organize large Android projects with multiple modules?
- What are the best practices for resource organization?
- How to handle different build variants and flavors?

## References

- https://developer.android.com/studio/projects
- https://developer.android.com/guide/topics/resources

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]] - Manifest configuration
- [[q-android-app-components--android--easy]] - App components

### Related (Medium)
- [[q-gradle-build-system--android--medium]] - Build system
- [[q-android-modularization--android--medium]] - Project modularization
- [[q-android-jetpack-overview--android--easy]] - Jetpack libraries

### Advanced (Harder)
- [[q-android-architectural-patterns--android--medium]] - Architecture patterns
- [[q-android-build-optimization--android--medium]] - Build optimization
