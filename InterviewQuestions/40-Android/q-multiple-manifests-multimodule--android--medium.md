---
topic: android
tags:
  - android
  - android-manifest
  - android/multi-module
  - android/project-structure
  - build-system
  - manifest-merging
  - modularization
  - multi-module
  - project-structure
difficulty: medium
status: reviewed
---

# Для проектов в которых есть несколько модулей, там может быть много Android Manifest'ов, для чего это делается?

**English**: In multi-module projects, there can be many AndroidManifest files. Why is this done?

## Answer

In multi-module projects, each module can have its own **AndroidManifest.xml** to:

1. **Declare module-specific dependencies** (`uses-permission`, `uses-feature`)
2. **Define module components** (Activity, Service, BroadcastReceiver)
3. **Automatically merge** all module manifests into the main app's AndroidManifest.xml

This allows **modular independence** - each module declares only what it needs, and the build system merges everything automatically.

---

## Why Multiple Manifests?

### Problem: Monolithic Manifest

In a single-module app, **one AndroidManifest.xml** contains everything:

```xml
<!-- app/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <!-- ❌ All permissions mixed together -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.LOCATION" />
    <uses-permission android:name="android.permission.READ_CONTACTS" />

    <application>
        <!-- ❌ All components mixed together -->
        <activity android:name=".LoginActivity" />
        <activity android:name=".ProfileActivity" />
        <activity android:name=".CameraActivity" />
        <activity android:name=".MapActivity" />
        <activity android:name=".ContactsActivity" />

        <service android:name=".NetworkService" />
        <service android:name=".LocationService" />
    </application>
</manifest>
```

**Problems:**
- **Unclear ownership** - which feature needs which permission?
- **Tight coupling** - can't remove a feature without manual manifest editing
- **No reusability** - can't reuse modules in other projects

---

### Solution: Module-Specific Manifests

Each module declares **only its own requirements**:

```
project/
├── app/
│   └── src/main/AndroidManifest.xml          ← Main app manifest
├── feature-login/
│   └── src/main/AndroidManifest.xml          ← Login module manifest
├── feature-camera/
│   └── src/main/AndroidManifest.xml          ← Camera module manifest
├── feature-map/
│   └── src/main/AndroidManifest.xml          ← Map module manifest
└── core-network/
    └── src/main/AndroidManifest.xml          ← Network module manifest
```

---

## Module Manifest Examples

### 1. Feature Module: Login

```xml
<!-- feature-login/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.feature.login">

    <!-- ✅ Only permissions needed by login feature -->
    <uses-permission android:name="android.permission.INTERNET" />

    <application>
        <!-- ✅ Only login-related components -->
        <activity
            android:name=".LoginActivity"
            android:exported="false" />

        <activity
            android:name=".SignUpActivity"
            android:exported="false" />
    </application>
</manifest>
```

**Benefits:**
- Clear: Login needs INTERNET
- Modular: Can be reused in other apps
- Maintainable: Easy to understand

---

### 2. Feature Module: Camera

```xml
<!-- feature-camera/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.feature.camera">

    <!-- ✅ Camera-specific permissions -->
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-feature
        android:name="android.hardware.camera"
        android:required="true" />

    <application>
        <!-- ✅ Camera-related components -->
        <activity
            android:name=".CameraActivity"
            android:exported="false"
            android:screenOrientation="portrait" />

        <provider
            android:name=".CameraFileProvider"
            android:authorities="${applicationId}.camera.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/camera_file_paths" />
        </provider>
    </application>
</manifest>
```

---

### 3. Feature Module: Map

```xml
<!-- feature-map/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.feature.map">

    <!-- ✅ Location permissions -->
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

    <application>
        <!-- ✅ Map-related components -->
        <activity
            android:name=".MapActivity"
            android:exported="false" />

        <service
            android:name=".LocationTrackingService"
            android:foregroundServiceType="location"
            android:exported="false" />

        <!-- Google Maps API Key -->
        <meta-data
            android:name="com.google.android.geo.API_KEY"
            android:value="${MAPS_API_KEY}" />
    </application>
</manifest>
```

---

### 4. Core Library Module: Network

```xml
<!-- core-network/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.core.network">

    <!-- ✅ Network permissions for all features using this module -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <!-- No <application> section needed for library modules -->
</manifest>
```

---

### 5. Main App Module

```xml
<!-- app/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <!-- ✅ Only app-level configuration -->
    <application
        android:name=".MyApplication"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/AppTheme">

        <!-- Main launcher activity -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- All module components are merged automatically! -->
    </application>
</manifest>
```

---

## Manifest Merging Process

### How Merging Works

The Android build system **automatically merges** all module manifests into the final app manifest.

```
Build Process:
==============

1. Collect manifests:
   ├── app/AndroidManifest.xml
   ├── feature-login/AndroidManifest.xml
   ├── feature-camera/AndroidManifest.xml
   ├── feature-map/AndroidManifest.xml
   └── core-network/AndroidManifest.xml

2. Merge manifests (priority: app > features > libraries):
   └── Merged manifest with all components and permissions

3. Generate final AndroidManifest.xml:
   └── app/build/intermediates/merged_manifests/debug/AndroidManifest.xml
```

---

### Merge Priority

**Highest priority → Lowest priority:**

1. **app module** (main manifest)
2. **Feature modules** (dependencies)
3. **Library modules** (transitive dependencies)

**Example:**

```xml
<!-- feature-login/AndroidManifest.xml -->
<activity
    android:name=".LoginActivity"
    android:screenOrientation="portrait" />

<!-- app/AndroidManifest.xml -->
<activity
    android:name="com.example.feature.login.LoginActivity"
    android:screenOrientation="landscape" />  <!-- ✅ Overrides portrait -->
```

**Result:** `screenOrientation="landscape"` (app wins)

---

### Viewing Merged Manifest

**Android Studio:**

1. Open **app/src/main/AndroidManifest.xml**
2. Click **Merged Manifest** tab at the bottom
3. View the final merged result

**Command line:**

```bash

# Build the app
./gradlew assembleDebug

# View merged manifest
cat app/build/intermediates/merged_manifests/debug/AndroidManifest.xml
```

---

## Complete Multi-Module Example

### Project Structure

```
project/
├── app/
│   ├── build.gradle.kts
│   └── src/main/AndroidManifest.xml
│
├── core/
│   ├── network/
│   │   ├── build.gradle.kts
│   │   └── src/main/AndroidManifest.xml
│   └── database/
│       ├── build.gradle.kts
│       └── src/main/AndroidManifest.xml
│
└── feature/
    ├── login/
    │   ├── build.gradle.kts
    │   └── src/main/AndroidManifest.xml
    ├── camera/
    │   ├── build.gradle.kts
    │   └── src/main/AndroidManifest.xml
    └── map/
        ├── build.gradle.kts
        └── src/main/AndroidManifest.xml
```

---

### Module Dependencies

```kotlin
// app/build.gradle.kts
dependencies {
    implementation(project(":core:network"))
    implementation(project(":core:database"))
    implementation(project(":feature:login"))
    implementation(project(":feature:camera"))
    implementation(project(":feature:map"))
}
```

---

### Final Merged Manifest

```xml
<!-- app/build/intermediates/merged_manifests/debug/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <!-- ✅ Merged from all modules -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

    <uses-feature android:name="android.hardware.camera" android:required="true" />

    <application
        android:name="com.example.app.MyApplication"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/AppTheme">

        <!-- From app module -->
        <activity
            android:name="com.example.app.MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- From feature-login module -->
        <activity android:name="com.example.feature.login.LoginActivity" />
        <activity android:name="com.example.feature.login.SignUpActivity" />

        <!-- From feature-camera module -->
        <activity android:name="com.example.feature.camera.CameraActivity" />
        <provider
            android:name="com.example.feature.camera.CameraFileProvider"
            android:authorities="com.example.app.camera.fileprovider" />

        <!-- From feature-map module -->
        <activity android:name="com.example.feature.map.MapActivity" />
        <service android:name="com.example.feature.map.LocationTrackingService" />
        <meta-data
            android:name="com.google.android.geo.API_KEY"
            android:value="YOUR_API_KEY" />
    </application>
</manifest>
```

---

## Benefits of Module Manifests

### 1. Modular Independence

```kotlin
// feature-camera is self-contained
// Declares its own permissions and components
// Can be reused in other projects
```

**Remove camera feature?**
```kotlin
// app/build.gradle.kts
dependencies {
    // implementation(project(":feature:camera"))  // ✅ Just comment out
}

// ✅ Camera permissions and components automatically removed from merged manifest!
```

---

### 2. Clear Ownership

```
Which module needs CAMERA permission?
→ Look at feature-camera/AndroidManifest.xml

Which module needs LOCATION permission?
→ Look at feature-map/AndroidManifest.xml
```

**Before (monolithic):**
```xml
<!-- ❌ Unclear which feature needs what -->
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.LOCATION" />
```

**After (modular):**
```xml
<!-- feature-camera/AndroidManifest.xml -->
<uses-permission android:name="android.permission.CAMERA" />  <!-- ✅ Clear! -->

<!-- feature-map/AndroidManifest.xml -->
<uses-permission android:name="android.permission.LOCATION" />  <!-- ✅ Clear! -->
```

---

### 3. Reusability

```kotlin
// Project A uses login feature
dependencies {
    implementation(project(":feature:login"))
}

// Project B also uses login feature (same module!)
dependencies {
    implementation(project(":feature:login"))
}
```

**Login module is self-contained:**
- Has own manifest
- Declares own permissions
- Works independently

---

## Merge Conflicts and Resolution

### Problem: Conflicting Attributes

```xml
<!-- feature-login/AndroidManifest.xml -->
<activity
    android:name=".LoginActivity"
    android:screenOrientation="portrait" />

<!-- feature-profile/AndroidManifest.xml -->
<activity
    android:name="com.example.feature.login.LoginActivity"
    android:screenOrientation="landscape" />  <!-- ❌ Conflict! -->
```

**Error:**
```
Manifest merger failed : Attribute android:screenOrientation@value=landscape
from feature-profile conflicts with value=portrait from feature-login
```

---

### Solution 1: Remove Conflict

```xml
<!-- Remove conflicting attribute from one module -->
<activity android:name=".LoginActivity" />
```

---

### Solution 2: Override in App Module

```xml
<!-- app/AndroidManifest.xml has highest priority -->
<activity
    android:name="com.example.feature.login.LoginActivity"
    android:screenOrientation="portrait"
    tools:replace="android:screenOrientation" />
```

---

### Solution 3: Merge Tools

```xml
<!-- feature-login/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <activity
        android:name=".LoginActivity"
        android:screenOrientation="portrait"
        tools:node="replace" />  <!-- Replace entire node if conflict -->
</manifest>
```

**Merge tools:**
- `tools:node="merge"` - Merge attributes (default)
- `tools:node="replace"` - Replace entire node
- `tools:node="remove"` - Remove node
- `tools:replace="attributeName"` - Replace specific attribute

---

## Best Practices

### 1. Minimal Main Manifest

```xml
<!-- app/AndroidManifest.xml -->
<!-- ✅ Only app-level config, no feature-specific items -->
<manifest>
    <application
        android:name=".MyApplication"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name">

        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

---

### 2. Module Self-Sufficiency

```xml
<!-- ✅ Each module declares everything it needs -->
<!-- feature-camera/AndroidManifest.xml -->
<manifest>
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-feature android:name="android.hardware.camera" />

    <application>
        <activity android:name=".CameraActivity" />
        <provider android:name=".CameraFileProvider" />
    </application>
</manifest>
```

---

### 3. Library Modules: No Application Tag

```xml
<!-- core-network/AndroidManifest.xml -->
<!-- ✅ Library modules: only permissions, NO <application> -->
<manifest>
    <uses-permission android:name="android.permission.INTERNET" />
</manifest>
```

---

## Summary

**Why multiple AndroidManifest files in multi-module projects?**

1. **Module-specific dependencies:**
   - Each module declares its own permissions (`uses-permission`)
   - Each module declares its own features (`uses-feature`)

2. **Module components:**
   - Each module defines its own Activities, Services, etc.
   - Components are scoped to the module

3. **Automatic merging:**
   - Build system merges all manifests into app's manifest
   - Merge priority: app > features > libraries
   - Conflicts handled with merge tools

**Benefits:**
- ✅ **Modular independence** - modules are self-contained
- ✅ **Clear ownership** - easy to see what each module needs
- ✅ **Reusability** - modules can be reused across projects
- ✅ **Maintainability** - remove module = remove all its manifest entries

**Best practices:**
- Keep main app manifest minimal
- Make modules self-sufficient
- Library modules: no `<application>` tag
- Use merge tools to resolve conflicts

**View merged manifest:**
- Android Studio: **Merged Manifest** tab
- Command line: `app/build/intermediates/merged_manifests/debug/AndroidManifest.xml`

---

## Ответ

В многомодульных проектах каждый модуль может иметь свой **AndroidManifest.xml**, чтобы:

1. **Задавать зависимости** (`uses-permission`, `uses-feature`) для конкретного модуля
2. **Определять компоненты** (Activity, Service, BroadcastReceiver) для каждого модуля
3. **Автоматически объединять** манифесты всех модулей в AndroidManifest.xml главного (app) модуля

**Преимущества:**
- Модульная независимость - каждый модуль самодостаточен
- Чёткое владение - понятно какому модулю нужны какие разрешения
- Переиспользуемость - модули можно использовать в других проектах
- Поддерживаемость - удалили модуль = автоматически удалили все его записи из манифеста

**Процесс слияния:**
- Система сборки автоматически объединяет все манифесты
- Приоритет: app > feature модули > библиотеки
- Результат: `app/build/intermediates/merged_manifests/debug/AndroidManifest.xml`

