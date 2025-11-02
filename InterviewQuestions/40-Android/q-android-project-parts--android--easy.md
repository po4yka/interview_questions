---
id: android-216
title: Android Project Parts / Части Android проекта
aliases: ["Android Project Parts", "Части Android проекта"]
topic: android
subtopics: [gradle, build-variants]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-manifest-file--android--easy, q-gradle-build-system--android--medium, q-android-modularization--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android/gradle, android/build-variants, build-system, project-structure, difficulty/easy]
sources: []
date created: Thursday, October 30th 2025, 11:26:32 am
date modified: Thursday, October 30th 2025, 12:42:56 pm
---

# Вопрос (RU)
> Из каких основных частей состоит Android проект?

# Question (EN)
> What are the main parts of an Android project?

## Ответ (RU)

**Структура Android проекта** организована в виде каталогов и файлов с четкими обязанностями: исходный код, ресурсы, конфигурация сборки.

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

**Организация кода:**

```kotlin
// ✅ Type-safe доступ к ресурсам через R class
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val appName = getString(R.string.app_name)
        val color = getColor(R.color.primary_color)
    }
}
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
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

**Build конфигурация:**

```kotlin
android {
    namespace = "com.example.app"
    compileSdk = 35

    defaultConfig {
        minSdk = 24
        targetSdk = 35
    }
}
```

**Ключевые различия:**

| Компонент | Назначение | Доступ |
|-----------|-----------|--------|
| **res/** | Компилируемые ресурсы | `R.layout.activity_main` (type-safe) |
| **assets/** | Сырые файлы | `assets.open("file.json")` (строковый путь) |
| **src/** | Исходный код | Компилируется в DEX bytecode |
| **AndroidManifest.xml** | Метаданные, permissions | Читается при установке |

## Answer (EN)

**Android Project Structure** organizes directories and files with clear responsibilities: source code, resources, build configuration.

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

**Code Organization:**

```kotlin
// ✅ Type-safe resource access via R class
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val appName = getString(R.string.app_name)
        val color = getColor(R.color.primary_color)
    }
}
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
        <activity android:name=".MainActivity" android:exported="true">
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
android {
    namespace = "com.example.app"
    compileSdk = 35

    defaultConfig {
        minSdk = 24
        targetSdk = 35
    }
}
```

**Key Differences:**

| Component | Purpose | Access |
|-----------|---------|--------|
| **res/** | Compiled resources | `R.layout.activity_main` (type-safe) |
| **assets/** | Raw files | `assets.open("file.json")` (string path) |
| **src/** | Source code | Compiled to DEX bytecode |
| **AndroidManifest.xml** | Metadata, permissions | Read during installation |

## Follow-ups

- What is the difference between res/ and assets/ directories for file access patterns?
- How does R class generation work and when is it triggered during builds?
- What are source sets (main, debug, release) and how do they merge?
- How do version catalogs improve multi-module dependency management?
- What happens when you exclude AndroidManifest.xml from a library module?

## References

- [[c-gradle-build-system]]
- [[c-android-resources]]
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
