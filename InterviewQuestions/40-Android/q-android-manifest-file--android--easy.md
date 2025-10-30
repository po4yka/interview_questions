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
updated: 2025-10-29
tags: [android/activity, android/app-startup, android/permissions, difficulty/easy]
sources: [https://github.com/Kirchhoff-/Android-Interview-Questions]
---
# Вопрос (RU)
> Что такое AndroidManifest.xml и зачем он нужен?

# Question (EN)
> What is AndroidManifest.xml and why is it needed?

## Ответ (RU)

**AndroidManifest.xml** — главный конфигурационный файл Android-приложения, который объявляет структуру и требования приложения системе.

**Основные функции:**
- **Регистрация компонентов** — Activities, Services, BroadcastReceivers, ContentProviders
- **Управление разрешениями** — запрос системных и объявление пользовательских разрешений
- **Метаданные приложения** — package name, минимальный SDK, иконка, тема
- **Intent-фильтры** — как система и другие приложения могут взаимодействовать с компонентами

**Минимальная структура:**
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name">

        <!-- ✅ Точка входа с правильным exported -->
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

**Критические требования:**
```xml
<!-- ✅ Для SDK 31+ обязателен exported -->
<activity android:name=".ShareActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
    </intent-filter>
</activity>

<!-- ❌ Приложение упадет при установке на API 31+ -->
<activity android:name=".ShareActivity">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
    </intent-filter>
</activity>

<!-- ✅ Защита компонента подписью -->
<permission
    android:name="com.example.INTERNAL_ACTION"
    android:protectionLevel="signature" />
```

**Слияние манифестов:**
```xml
<!-- build.gradle управляет версией, но базовая структура в manifest -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Gradle placeholder -->
    <uses-sdk android:minSdkVersion="${minSdkVersion}" />

    <!-- ✅ Переопределяется через Gradle flavors -->
    <application android:label="${appName}">
        <!-- Модули библиотек автоматически сливаются -->
    </application>
</manifest>
```

## Answer (EN)

**AndroidManifest.xml** is the main configuration file of an Android application that declares the app's structure and requirements to the system.

**Core Functions:**
- **Component Registration** — Activities, Services, BroadcastReceivers, ContentProviders
- **Permission Management** — requesting system permissions and declaring custom permissions
- **App Metadata** — package name, minimum SDK, icon, theme
- **Intent Filters** — how the system and other apps can interact with components

**Minimal Structure:**
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name">

        <!-- ✅ Entry point with proper exported -->
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

**Critical Requirements:**
```xml
<!-- ✅ For SDK 31+ exported is mandatory -->
<activity android:name=".ShareActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
    </intent-filter>
</activity>

<!-- ❌ App will crash on install for API 31+ -->
<activity android:name=".ShareActivity">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
    </intent-filter>
</activity>

<!-- ✅ Protect component with signature -->
<permission
    android:name="com.example.INTERNAL_ACTION"
    android:protectionLevel="signature" />
```

**Manifest Merging:**
```xml
<!-- build.gradle controls version, but base structure in manifest -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Gradle placeholder -->
    <uses-sdk android:minSdkVersion="${minSdkVersion}" />

    <!-- ✅ Overridden via Gradle flavors -->
    <application android:label="${appName}">
        <!-- Library module manifests auto-merge -->
    </application>
</manifest>
```

## Follow-ups

- What happens if multiple library modules declare the same component?
- How does manifest merging resolve conflicts between main and library manifests?
- What is the impact of `android:exported` on API levels below 31?
- How to declare features required by the app (camera, GPS, NFC)?
- What security risks exist with overly permissive intent-filters?

## References

- [[c-android-components]] - Deep dive into Android components
- [[c-permissions]] - Permission system architecture
- https://developer.android.com/guide/topics/manifest/manifest-intro

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - Understanding basic app components

### Related
- [[q-activity-lifecycle-methods--android--medium]] - Activity lifecycle and state
- [[q-intent-filters-android--android--medium]] - Intent filter patterns
- [[q-android-permissions-runtime--android--medium]] - Runtime permission model

### Advanced
- [[q-android-gradle-manifest-merge--android--hard]] - Manifest merging strategies
- [[q-android-security-practices-checklist--android--medium]] - Security best practices