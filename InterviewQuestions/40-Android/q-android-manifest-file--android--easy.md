---
id: 20251015-094722
title: AndroidManifest.xml / Файл манифеста Android
aliases:
- AndroidManifest.xml
- Файл манифеста Android
topic: android
subtopics:
- app-startup
- permissions
- activity
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-app-components--android--easy
- q-activity-lifecycle-methods--android--medium
- q-intent-filters-android--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/app-startup
- android/permissions
- android/activity
- difficulty/easy
source: https://github.com/Kirchhoff-/Android-Interview-Questions
---

## Answer (EN)
**AndroidManifest.xml** is the central configuration file that declares [[c-app-components|app components]], [[c-permissions|permissions]], and metadata. It serves as the entry point for the Android system to understand and launch your application through [[c-intent-filter|intent filters]].

**Manifest Theory:**
The manifest acts as a contract between your app and the Android system. It declares what components exist, what permissions are needed, and how the app should behave. The system reads this file before launching any component to understand the app's structure and requirements.

**Core Responsibilities:**
- **Component Declaration**: Registers Activities, Services, BroadcastReceivers, ContentProviders
- **Permission Management**: Declares required permissions and custom permissions
- **App Metadata**: Defines app name, icon, theme, and version information
- **Intent Filtering**: Specifies how components can be launched by intents

**Basic Manifest Structure:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.CAMERA" />

    <!-- App Configuration -->
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/AppTheme">

        <!-- Main Activity -->
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

**SDK Version Configuration:**
```xml
<uses-sdk
    android:minSdkVersion="21"
    android:targetSdkVersion="33" />
```

**Hardware Feature Requirements:**
```xml
<uses-feature
    android:name="android.hardware.camera"
    android:required="true" />

<uses-feature
    android:name="android.hardware.location"
    android:required="false" />
```

**Screen Support Configuration:**
```xml
<supports-screens
    android:smallScreens="true"
    android:normalScreens="true"
    android:largeScreens="true"
    android:xlargeScreens="true" />
```

**Custom Permissions:**
```xml
<permission
    android:name="com.example.app.CUSTOM_PERMISSION"
    android:protectionLevel="signature" />

<uses-permission android:name="com.example.app.CUSTOM_PERMISSION" />
```

**Service and Receiver Declaration:**
```xml
<service android:name=".MyService" />

<receiver android:name=".MyBroadcastReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>

<provider
    android:name=".MyContentProvider"
    android:authorities="com.example.app.provider"
    android:exported="false" />
```

**Intent Filter Theory:**
Intent filters declare how components can be launched. They specify actions, categories, and data types that the component can handle, allowing the system to route intents to the appropriate component.

**Common Intent Actions:**
- `MAIN`: Entry point of the app
- `VIEW`: Display data to user
- `EDIT`: Edit data
- `SEND`: Send data to other apps

## Follow-ups

- How to handle different screen densities in manifest?
- What are the differences between exported and non-exported components?
- How to configure app for different device configurations?

## References

- https://developer.android.com/guide/topics/manifest/manifest-intro
- https://www.geeksforgeeks.org/application-manifest-file-android/

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components basics

### Related (Medium)
- [[q-activity-lifecycle-methods--android--medium]] - Activity lifecycle
- [[q-intent-filters-android--android--medium]] - Intent filters
- [[q-android-app-bundles--android--easy]] - App distribution

### Advanced (Harder)
- [[q-android-security-practices-checklist--android--medium]] - Security practices
- [[q-android-build-optimization--android--medium]] - Build configuration