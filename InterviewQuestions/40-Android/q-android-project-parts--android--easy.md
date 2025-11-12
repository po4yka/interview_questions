---
id: android-216
title: Android Project Parts / Части Android проекта
aliases:
- Android Project Parts
- Части Android проекта
topic: android
subtopics:
- build-variants
- gradle
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-gradle
- q-android-manifest-file--android--easy
created: 2025-10-15
updated: 2025-11-10
tags:
- android/build-variants
- android/gradle
- build-system
- difficulty/easy
- project-structure
sources: []
---

# Вопрос (RU)
> Из каких основных частей состоит Android проект?

# Question (EN)
> What are the main parts of an Android project?

## Ответ (RU)

**Структура Android проекта** организована в виде каталогов и файлов с четкими обязанностями: исходный код, ресурсы, конфигурация сборки.

Ниже приведен упрощенный пример структуры одного app-модуля (без учёта всех вариантов source sets и дополнительных модулей):

**Основные компоненты:**

```text
app/
├── src/main/
│   ├── java/                    # Исходный код (Kotlin/Java; также возможна папка kotlin/)
│   ├── res/                     # Компилируемые ресурсы
│   │   ├── layout/              # XML макеты UI
│   │   ├── values/              # strings, colors, dimens
│   │   └── drawable/            # Изображения и векторы
│   ├── assets/                  # Сырые файлы (JSON, шрифты)
│   └── AndroidManifest.xml      # Конфигурация приложения
└── build.gradle.kts             # Конфигурация сборки модуля
```

(На уровне корня проекта также есть общий `settings.gradle(.kts)`, верхнеуровневый `build.gradle(.kts)` и Gradle wrapper (`gradlew`, `gradlew.bat`, папка `gradle/`); в реальных проектах часто используется несколько модулей.)

**Организация кода и ресурсов:**

```kotlin
// Доступ к ресурсам через класс R с проверкой идентификаторов и типов на этапе компиляции
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val appName = getString(R.string.app_name)
        val color = getColor(R.color.primaryColor)
    }
}
```

```kotlin
// Доступ к файлам в assets по строковому пути (без type-safe обёртки; стандартный способ)
val json = assets.open("config.json").bufferedReader().use { it.readText() }
```

**AndroidManifest.xml** - декларация компонентов и метаданных:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

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

**Build конфигурация (модуль):**

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
| **res/** | Компилируемые ресурсы | Через `R.*` (компилятор проверяет наличие и тип ресурса) |
| **assets/** | Сырые файлы | `assets.open("file.json")` (строковый путь, без type-safe) |
| **src/main/java**, **src/main/kotlin** | Исходный код | Компилируется в байткод JVM и затем в DEX |
| **AndroidManifest.xml** | Метаданные, permissions, компоненты | Используется системой при установке и запуске |

## Answer (EN)

**Android Project Structure** organizes directories and files with clear responsibilities: source code, resources, and build configuration.

Below is a simplified example of a single app module structure (not covering all source sets or additional modules):

**Core Components:**

```text
app/
├── src/main/
│   ├── java/                    # Source code (Kotlin/Java; kotlin/ directory may also be used)
│   ├── res/                     # Compiled resources
│   │   ├── layout/              # XML UI layouts
│   │   ├── values/              # strings, colors, dimens
│   │   └── drawable/            # Images and vectors
│   ├── assets/                  # Raw files (JSON, fonts)
│   └── AndroidManifest.xml      # App configuration
└── build.gradle.kts             # Module-level build configuration
```

(At the project root there are also `settings.gradle(.kts)`, a top-level `build.gradle(.kts)`, and the Gradle wrapper (`gradlew`, `gradlew.bat`, `gradle/` directory); real projects often contain multiple modules.)

**Code and resource organization:**

```kotlin
// Resource access via R class with compile-time checks for identifiers and resource types
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val appName = getString(R.string.app_name)
        val color = getColor(R.color.primaryColor)
    }
}
```

```kotlin
// String-based assets access (no type-safe wrapper, this is the standard way)
val json = assets.open("config.json").bufferedReader().use { it.readText() }
```

**AndroidManifest.xml** - component and metadata declarations:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

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

**Build configuration (module-level):**

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
| **res/** | Compiled resources | via `R.*` (compiler validates presence and type) |
| **assets/** | Raw files | `assets.open("file.json")` (string path, not type-safe) |
| **src/main/java**, **src/main/kotlin** | Source code | Compiled to JVM bytecode and then to DEX |
| **AndroidManifest.xml** | Metadata, permissions, components | Used by the system during install and runtime |

## Дополнительные вопросы (RU)

- Какова разница между каталогами res/ и assets/ с точки зрения доступа к файлам?
- Как происходит генерация класса R и на каком этапе сборки она выполняется?
- Что такое source sets (main, debug, release) и как они объединяются?
- Как version catalogs помогают управлять зависимостями в мульти-модульных проектах?
- Что произойдет, если исключить AndroidManifest.xml из library-модуля?

## Follow-ups

- What is the difference between res/ and assets/ directories for file access patterns?
- How does R class generation work and when is it triggered during builds?
- What are source sets (main, debug, release) and how do they merge?
- How do version catalogs improve multi-module dependency management?
- What happens when you exclude AndroidManifest.xml from a library module?

## Ссылки (RU)

- https://developer.android.com/studio/projects
- https://developer.android.com/guide/topics/resources/providing-resources
- https://developer.android.com/build

## References

- https://developer.android.com/studio/projects
- https://developer.android.com/guide/topics/resources/providing-resources
- https://developer.android.com/build

## Связанные вопросы (RU)

### Предпосылки / Концепции

- [[c-gradle]]
- [[q-android-manifest-file--android--easy]]

### Связанные вопросы
- [[q-android-modularization--android--medium]]

## Related Questions

### Prerequisites / Concepts

- [[c-gradle]]
- [[q-android-manifest-file--android--easy]]

### Related
- [[q-android-modularization--android--medium]]
