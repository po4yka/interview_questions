---
id: 20251012-122769
title: Android Project Parts / Части Android проекта
aliases: ["Android Project Parts", "Части Android проекта"]
topic: android
subtopics: [gradle, architecture-modularization]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-manifest-file--android--easy, q-gradle-build-system--android--medium, q-android-modularization--android--medium]
created: 2025-10-15
updated: 2025-10-29
tags: [android/gradle, android/architecture-modularization, build-system, project-structure, difficulty/easy]
sources: []
---
# Вопрос (RU)
> Из каких основных частей состоит Android проект?

# Question (EN)
> What are the main parts of an Android project?

## Ответ (RU)

**Структура Android проекта** организована в виде каталогов и файлов с четко определенными обязанностями: исходный код, ресурсы, конфигурация и настройки сборки.

**Основные компоненты:**

```text
app/
├── src/main/
│   ├── java/                    # Исходный код (Kotlin/Java)
│   ├── res/                     # Компилируемые ресурсы
│   │   ├── layout/             # XML макеты UI
│   │   ├── values/             # strings, colors, dimens
│   │   └── drawable/           # Изображения и векторы
│   ├── assets/                  # Сырые файлы (JSON, шрифты)
│   └── AndroidManifest.xml      # Конфигурация приложения
└── build.gradle.kts              # Конфигурация сборки
```

**Организация кода и ресурсов:**

```kotlin
// ✅ Исходный код: src/main/java/com/example/app/
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}

// ✅ Type-safe доступ к ресурсам через R class
val appName = getString(R.string.app_name)
val color = getColor(R.color.primary_color)
val icon = ContextCompat.getDrawable(this, R.drawable.ic_launcher)
```

```kotlin
// ❌ Строковый доступ к assets (не type-safe)
val json = assets.open("config.json").bufferedReader().use { it.readText() }
```

**AndroidManifest.xml** - декларация компонентов:

```xml
<manifest package="com.example.app">
    <uses-permission android:name="android.permission.INTERNET" />

    <application android:label="@string/app_name">
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

**Build конфигурация** (build.gradle.kts):

```kotlin
android {
    namespace = "com.example.app"
    compileSdk = 35

    defaultConfig {
        minSdk = 24
        targetSdk = 35
    }

    buildFeatures {
        viewBinding = true
        compose = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
}
```

**Ключевые различия:**

| Компонент | Назначение | Доступ |
|-----------|-----------|--------|
| **res/** | Компилируемые ресурсы (layout, strings) | `R.layout.activity_main` (type-safe) |
| **assets/** | Сырые файлы (JSON, шрифты, медиа) | `assets.open("file.json")` (строковый путь) |
| **src/** | Исходный код Kotlin/Java | Компилируется в DEX bytecode |
| **AndroidManifest.xml** | Метаданные приложения, permissions | Читается во время установки |
| **build.gradle.kts** | Конфигурация сборки, зависимости | Обрабатывается Gradle |

## Answer (EN)

**Android Project Structure** organizes directories and files with clear responsibilities: source code, resources, configuration, and build settings.

**Core Components:**

```text
app/
├── src/main/
│   ├── java/                    # Source code (Kotlin/Java)
│   ├── res/                     # Compiled resources
│   │   ├── layout/             # XML UI layouts
│   │   ├── values/             # strings, colors, dimens
│   │   └── drawable/           # Images and vectors
│   ├── assets/                  # Raw files (JSON, fonts)
│   └── AndroidManifest.xml      # App configuration
└── build.gradle.kts              # Build configuration
```

**Code and Resource Organization:**

```kotlin
// ✅ Source code: src/main/java/com/example/app/
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}

// ✅ Type-safe resource access via R class
val appName = getString(R.string.app_name)
val color = getColor(R.color.primary_color)
val icon = ContextCompat.getDrawable(this, R.drawable.ic_launcher)
```

```kotlin
// ❌ String-based assets access (not type-safe)
val json = assets.open("config.json").bufferedReader().use { it.readText() }
```

**AndroidManifest.xml** - component declarations:

```xml
<manifest package="com.example.app">
    <uses-permission android:name="android.permission.INTERNET" />

    <application android:label="@string/app_name">
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

**Build Configuration** (build.gradle.kts):

```kotlin
android {
    namespace = "com.example.app"
    compileSdk = 35

    defaultConfig {
        minSdk = 24
        targetSdk = 35
    }

    buildFeatures {
        viewBinding = true
        compose = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
}
```

**Key Differences:**

| Component | Purpose | Access |
|-----------|---------|--------|
| **res/** | Compiled resources (layout, strings) | `R.layout.activity_main` (type-safe) |
| **assets/** | Raw files (JSON, fonts, media) | `assets.open("file.json")` (string path) |
| **src/** | Source code Kotlin/Java | Compiled to DEX bytecode |
| **AndroidManifest.xml** | App metadata, permissions | Read during installation |
| **build.gradle.kts** | Build configuration, dependencies | Processed by Gradle |

## Follow-ups

- What is the difference between res/ and assets/ directories for storing files?
- How does R class generation work and when is it triggered during the build process?
- What are the different source sets (main, debug, release) and how do they merge?
- When should you use version catalogs vs buildSrc for dependency management?
- How does multi-module project structure differ from single-module?

## References

- https://developer.android.com/studio/projects
- https://developer.android.com/guide/topics/resources/providing-resources
- https://developer.android.com/build

## Related Questions

### Prerequisites
- [[q-android-manifest-file--android--easy]]

### Related
- [[q-gradle-build-system--android--medium]]
- [[q-android-resources-qualifiers--android--medium]]

### Advanced
- [[q-android-modularization--android--medium]]
- [[q-android-build-optimization--android--medium]]