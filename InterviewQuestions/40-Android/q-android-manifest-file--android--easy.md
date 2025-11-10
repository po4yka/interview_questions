---
id: android-360
title: AndroidManifest.xml / Файл манифеста Android
aliases: [AndroidManifest.xml, Файл манифеста Android]
topic: android
subtopics:
- app-startup
- intents-deeplinks
- permissions
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related: [c-android, q-android-app-components--android--easy, q-intent-filters-android--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/app-startup, android/intents-deeplinks, android/permissions, difficulty/easy]
sources:
- "https://github.com/Kirchhoff-/Android-Interview-Questions"
---

# Вопрос (RU)
> Что такое AndroidManifest.xml и зачем он нужен?

# Question (EN)
> What is AndroidManifest.xml and why is it needed?

## Ответ (RU)

**AndroidManifest.xml** — главный конфигурационный файл приложения, объявляющий его структуру системе Android.

См. также: [[c-android]].

**Основные функции:**
- **Регистрация компонентов** — Activities, Services, BroadcastReceivers, ContentProviders
- **Управление разрешениями** — системные и пользовательские permissions
- **Метаданные приложения** — package name, минимальный SDK, иконка, тема
- **`Intent`-фильтры** — точки взаимодействия с системой и другими приложениями

**Минимальная структура:**
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name">

        <!-- ✅ Точка входа с корректным exported -->
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
<!-- ✅ Для SDK 31+ обязателен exported при наличии intent-filter -->
<activity android:name=".ShareActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
    </intent-filter>
</activity>

<!-- ❌ Приложение не установится на API 31+ -->
<activity android:name=".ShareActivity">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
    </intent-filter>
</activity>
```

**Защита компонентов:**
```xml
<!-- Только приложения с той же подписью могут вызвать этот компонент -->
<permission
    android:name="com.example.INTERNAL_ACTION"
    android:protectionLevel="signature" />

<activity
    android:name=".InternalActivity"
    android:permission="com.example.INTERNAL_ACTION" />
```

**Слияние манифестов:**
```xml
<!-- Основной manifest сливается с библиотечными и Gradle-плейсхолдерами -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-sdk android:minSdkVersion="${minSdkVersion}" />

    <application android:label="${appName}">
        <!-- Компоненты из зависимостей добавляются автоматически -->
    </application>
</manifest>
```

## Answer (EN)

**AndroidManifest.xml** is the main configuration file that declares the app's structure to the Android system.

See also: [[c-android]].

**Core Functions:**
- **Component Registration** — Activities, Services, BroadcastReceivers, ContentProviders
- **Permission Management** — system and custom permissions
- **App Metadata** — package name, minimum SDK, icon, theme
- **`Intent` Filters** — interaction points with system and other apps

**Minimal Structure:**
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name">

        <!-- ✅ Entry point with correct exported -->
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
<!-- ✅ For SDK 31+ exported is mandatory with intent-filter -->
<activity android:name=".ShareActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
    </intent-filter>
</activity>

<!-- ❌ App won't install on API 31+ -->
<activity android:name=".ShareActivity">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
    </intent-filter>
</activity>
```

**Component Protection:**
```xml
<!-- Only apps with same signature can invoke this component -->
<permission
    android:name="com.example.INTERNAL_ACTION"
    android:protectionLevel="signature" />

<activity
    android:name=".InternalActivity"
    android:permission="com.example.INTERNAL_ACTION" />
```

**Manifest Merging:**
```xml
<!-- Main manifest merges with library and Gradle placeholders -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-sdk android:minSdkVersion="${minSdkVersion}" />

    <application android:label="${appName}">
        <!-- Components from dependencies added automatically -->
    </application>
</manifest>
```

## Дополнительные вопросы (RU)

- Как разрешаются конфликты при слиянии манифестов из нескольких библиотек?
- Какие атрибуты `<uses-feature>` влияют на видимость в Play Store?
- В чем разница между `protectionLevel="signature"` и `"signatureOrSystem"`?
- Можно ли полностью отказаться от AndroidManifest.xml в модульных приложениях?
- Как проверить итоговый merged manifest перед релизом?

## Follow-ups (EN)

- How are conflicts resolved when merging manifests from multiple libraries?
- Which `<uses-feature>` attributes affect visibility in the Play Store?
- What is the difference between `protectionLevel="signature"` and `"signatureOrSystem"`?
- Is it possible to completely avoid using AndroidManifest.xml in modular applications?
- How can you inspect the final merged manifest before release?

## Ссылки (RU)

- https://developer.android.com/guide/topics/manifest/manifest-intro — Официальное руководство по манифесту

## References (EN)

- https://developer.android.com/guide/topics/manifest/manifest-intro — Official manifest guide

## Связанные вопросы (RU)

### Базовые знания
- [[q-android-app-components--android--easy]] — Понимание компонентов приложения

### Связанные
- [[q-activity-lifecycle-methods--android--medium]] — Жизненный цикл `Activity`
- [[q-intent-filters-android--android--medium]] — Паттерны `Intent`-фильтров

### Продвинутые
- Стратегии слияния манифестов
- [[q-android-security-practices-checklist--android--medium]] — Рекомендации по безопасности

## Related Questions (EN)

### Prerequisites
- [[q-android-app-components--android--easy]] — Understanding app components

### Related
- [[q-activity-lifecycle-methods--android--medium]] — `Activity` lifecycle
- [[q-intent-filters-android--android--medium]] — `Intent` filter patterns

### Advanced
- Manifest merge strategies
- [[q-android-security-practices-checklist--android--medium]] — Security best practices
