---
id: 20251015-094722
title: AndroidManifest.xml / Файл манифеста Android
aliases: ["AndroidManifest.xml", "Файл манифеста Android"]
topic: android
subtopics: [activity, app-startup, permissions]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, q-android-app-components--android--easy, q-intent-filters-android--android--medium]
created: 2025-10-15
updated: 2025-10-27
tags: [android/activity, android/app-startup, android/permissions, difficulty/easy]
sources: [https://github.com/Kirchhoff-/Android-Interview-Questions]
---
# Вопрос (RU)
> Что такое AndroidManifest.xml?

## Ответ (RU)

**AndroidManifest.xml** — центральный файл конфигурации, который объявляет компоненты приложения, разрешения и метаданные. Система Android читает этот файл перед запуском любого компонента для понимания структуры приложения.

**Ключевые обязанности:**
- **Объявление компонентов**: регистрация Activities, Services, BroadcastReceivers, ContentProviders
- **Управление разрешениями**: объявление требуемых и пользовательских разрешений
- **Метаданные приложения**: имя, иконка, тема, версия
- **Intent-фильтры**: определение способов запуска компонентов

**Базовая структура:**
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <!-- Разрешения -->
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

**Объявление компонентов:**
```xml
<!-- ✅ Экспортируемая Activity с фильтром -->
<activity android:name=".MainActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
    </intent-filter>
</activity>

<!-- ❌ Забыт exported для Activity с intent-filter -->
<activity android:name=".ViewActivity">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
    </intent-filter>
</activity>
```

**Управление разрешениями:**
```xml
<!-- Запрос разрешений -->
<uses-permission android:name="android.permission.CAMERA" />

<!-- Объявление пользовательского разрешения -->
<permission
    android:name="com.example.CUSTOM_PERMISSION"
    android:protectionLevel="signature" />
```

---

# Question (EN)
> What is AndroidManifest.xml?

## Answer (EN)

**AndroidManifest.xml** is the central configuration file that declares app components, permissions, and metadata. The Android system reads this file before launching any component to understand the app's structure.

**Core Responsibilities:**
- **Component Declaration**: Registers Activities, Services, BroadcastReceivers, ContentProviders
- **Permission Management**: Declares required and custom permissions
- **App Metadata**: Defines app name, icon, theme, version
- **Intent Filtering**: Specifies how components can be launched

**Basic Structure:**
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <!-- Permissions -->
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

**Component Declaration:**
```xml
<!-- ✅ Exported Activity with intent filter -->
<activity android:name=".MainActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
    </intent-filter>
</activity>

<!-- ❌ Missing exported for Activity with intent filter -->
<activity android:name=".ViewActivity">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
    </intent-filter>
</activity>
```

**Permission Management:**
```xml
<!-- Request permissions -->
<uses-permission android:name="android.permission.CAMERA" />

<!-- Declare custom permission -->
<permission
    android:name="com.example.CUSTOM_PERMISSION"
    android:protectionLevel="signature" />
```

## Follow-ups

- What happens if an Activity has an intent-filter but `exported` is false?
- How does the manifest interact with Gradle build configuration?
- What are the security implications of declaring custom permissions?
- How to configure different manifest attributes for build variants?

## References

- https://developer.android.com/guide/topics/manifest/manifest-intro
- [[c-permissions]]

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Understanding app components

### Related
- [[q-activity-lifecycle-methods--android--medium]] - Activity lifecycle details
- [[q-intent-filters-android--android--medium]] - Intent filter configuration

### Advanced
- [[q-android-security-practices-checklist--android--medium]] - Security best practices