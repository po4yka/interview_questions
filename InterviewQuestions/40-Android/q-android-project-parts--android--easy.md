---
id: 20251012-122769
title: Android Project Parts / Части Android проекта
aliases: ["Android Project Parts", "Части Android проекта"]
topic: android
subtopics: [architecture-modularization, gradle, ui-theming]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-manifest-file--android--easy, q-android-modularization--android--medium, q-gradle-build-system--android--medium]
created: 2025-10-15
updated: 2025-10-27
tags: [android/architecture-modularization, android/gradle, android/ui-theming, difficulty/easy]
sources: []
---
# Вопрос (RU)
> Из каких основных частей состоит Android проект?

# Question (EN)
> What are the main parts of an Android project?

## Ответ (RU)

**Структура Android проекта** организована в виде каталогов и файлов с четко определенными обязанностями: исходный код, ресурсы, конфигурация и настройки сборки.

**Основные компоненты:**

- **src/**: исходный код (Kotlin/Java)
- **res/**: компилируемые ресурсы (layouts, strings, изображения)
- **AndroidManifest.xml**: конфигурация приложения и объявление компонентов
- **build.gradle**: конфигурация сборки и зависимости
- **assets/**: сырые файлы для runtime доступа

**Структура проекта:**

```text
app/
├── src/main/
│   ├── java/              # Исходный код
│   ├── res/               # Ресурсы (layouts, strings, drawable)
│   ├── assets/            # Сырые файлы
│   └── AndroidManifest.xml
└── build.gradle.kts       # Конфигурация сборки
```

**Организация кода:**

```kotlin
// src/main/java/com/example/app/MainActivity.kt
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main) // ✅ Доступ через R class
    }
}
```

**Доступ к ресурсам:**

```kotlin
val appName = getString(R.string.app_name)        // ✅ Type-safe
val color = getColor(R.color.primary_color)
val padding = resources.getDimensionPixelSize(R.dimen.padding)
```

**AndroidManifest.xml:**

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
    compileSdk = 34

    defaultConfig {
        minSdk = 24
        targetSdk = 34
    }
}
```

**Ключевые различия:**

- **res/**: компилируемые ресурсы, type-safe доступ через R class
- **assets/**: сырые файлы, доступ через AssetManager по строковому пути
- **src/**: исходный код, компилируется в bytecode
- **AndroidManifest.xml**: метаданные приложения, декларация компонентов

## Answer (EN)

**Android Project Structure** organizes directories and files with clear responsibilities: source code, resources, configuration, and build settings.

**Core Components:**

- **src/**: source code (Kotlin/Java)
- **res/**: compiled resources (layouts, strings, images)
- **AndroidManifest.xml**: app configuration and component declarations
- **build.gradle**: build configuration and dependencies
- **assets/**: raw files for runtime access

**Project Structure:**

```text
app/
├── src/main/
│   ├── java/              # Source code
│   ├── res/               # Resources (layouts, strings, drawable)
│   ├── assets/            # Raw files
│   └── AndroidManifest.xml
└── build.gradle.kts       # Build configuration
```

**Code Organization:**

```kotlin
// src/main/java/com/example/app/MainActivity.kt
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main) // ✅ Access via R class
    }
}
```

**Resource Access:**

```kotlin
val appName = getString(R.string.app_name)        // ✅ Type-safe
val color = getColor(R.color.primary_color)
val padding = resources.getDimensionPixelSize(R.dimen.padding)
```

**AndroidManifest.xml:**

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
    compileSdk = 34

    defaultConfig {
        minSdk = 24
        targetSdk = 34
    }
}
```

**Key Differences:**

- **res/**: compiled resources, type-safe access via R class
- **assets/**: raw files, accessed via AssetManager by string path
- **src/**: source code, compiled to bytecode
- **AndroidManifest.xml**: app metadata, component declarations

## Follow-ups

- What is the difference between res/ and assets/ directories?
- How does R class generation work during build?
- When should you use buildSrc vs version catalogs for dependency management?

## References

- https://developer.android.com/studio/projects
- https://developer.android.com/guide/topics/resources

## Related Questions

### Prerequisites
- [[q-android-manifest-file--android--easy]]

### Related
- [[q-gradle-build-system--android--medium]]
- [[q-android-modularization--android--medium]]

### Advanced
- [[q-android-build-optimization--android--medium]]