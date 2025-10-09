---
topic: android
tags:
  - android
  - android/project-structure
  - assets
  - gradle
  - manifest
  - project-structure
  - resources
difficulty: easy
status: reviewed
---

# Из каких частей состоит проект и какая часть за что отвечает?

**English**: What parts make up an Android project and what is each part responsible for?

## Answer

An Android project consists of:

- **`src/`** — Source code (Kotlin/Java)
- **`res/`** — Resources (strings, images, layouts)
- **`AndroidManifest.xml`** — Component declarations, permissions, app entry point
- **`build.gradle`** — Build configuration, dependencies
- **`libs/`** — External libraries (JAR files)
- **`assets/`** — Files accessible at runtime (raw files)

---

## Android Project Structure

### Complete Directory Layout

```
my-android-app/
├── app/                              ← Main application module
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/                ← Java source code
│   │   │   │   └── com/example/app/
│   │   │   │       ├── MainActivity.kt
│   │   │   │       ├── LoginActivity.kt
│   │   │   │       └── viewmodel/
│   │   │   ├── kotlin/              ← Kotlin source code (alternative)
│   │   │   ├── res/                 ← Resources
│   │   │   │   ├── layout/          ← XML layouts
│   │   │   │   ├── values/          ← Strings, colors, dimensions
│   │   │   │   ├── drawable/        ← Images, icons
│   │   │   │   └── mipmap/          ← App icons
│   │   │   ├── assets/              ← Raw files
│   │   │   └── AndroidManifest.xml  ← App manifest
│   │   ├── test/                    ← Unit tests
│   │   └── androidTest/             ← Instrumentation tests
│   ├── build.gradle.kts             ← Module build script
│   └── proguard-rules.pro           ← ProGuard configuration
├── gradle/                           ← Gradle wrapper files
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── build.gradle.kts                  ← Project build script
├── settings.gradle.kts               ← Project settings
├── gradle.properties                 ← Gradle properties
└── local.properties                  ← Local SDK path
```

---

## 1. src/ — Source Code

**Purpose:** Contains all source code files (Kotlin, Java).

### Structure

```
src/
├── main/
│   ├── java/
│   │   └── com/example/app/
│   │       ├── MainActivity.kt
│   │       ├── LoginActivity.kt
│   │       ├── ui/
│   │       │   ├── home/
│   │       │   │   ├── HomeFragment.kt
│   │       │   │   └── HomeViewModel.kt
│   │       │   └── profile/
│   │       ├── data/
│   │       │   ├── repository/
│   │       │   └── network/
│   │       └── domain/
│   │           └── model/
│   └── kotlin/  ← Alternative location for Kotlin files
├── test/        ← Unit tests (JVM)
│   └── java/
│       └── com/example/app/
│           └── ViewModelTest.kt
└── androidTest/ ← Instrumentation tests (Android device/emulator)
    └── java/
        └── com/example/app/
            └── MainActivityTest.kt
```

---

### Example Files

**MainActivity.kt:**
```kotlin
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

**HomeViewModel.kt:**
```kotlin
package com.example.app.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class HomeViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<HomeUiState>(HomeUiState.Loading)
    val uiState: StateFlow<HomeUiState> = _uiState

    init {
        loadData()
    }

    private fun loadData() {
        viewModelScope.launch {
            // Load data
            _uiState.value = HomeUiState.Success(data)
        }
    }
}
```

---

## 2. res/ — Resources

**Purpose:** Contains all resources (layouts, strings, images, etc.).

### Resource Types

```
res/
├── layout/              ← XML layouts
│   ├── activity_main.xml
│   ├── fragment_home.xml
│   └── item_product.xml
├── values/              ← Values (strings, colors, dimensions)
│   ├── strings.xml
│   ├── colors.xml
│   ├── dimens.xml
│   └── styles.xml
├── values-ru/           ← Russian localization
│   └── strings.xml
├── drawable/            ← Vector drawables, XML shapes
│   ├── ic_home.xml
│   └── bg_button.xml
├── drawable-hdpi/       ← High-density bitmaps
│   └── image.png
├── drawable-xhdpi/      ← Extra-high-density bitmaps
│   └── image.png
├── mipmap-hdpi/         ← App icons (different densities)
│   └── ic_launcher.png
├── mipmap-xhdpi/
├── mipmap-xxhdpi/
├── mipmap-xxxhdpi/
├── font/                ← Custom fonts
│   └── roboto_bold.ttf
├── raw/                 ← Raw files (audio, video)
│   └── music.mp3
├── xml/                 ← XML configurations
│   └── network_security_config.xml
└── anim/                ← Animations
    └── fade_in.xml
```

---

### Example Resources

**res/layout/activity_main.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">

    <TextView
        android:id="@+id/textTitle"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/app_name"
        android:textSize="24sp" />

    <Button
        android:id="@+id/btnLogin"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="@string/login" />
</LinearLayout>
```

**res/values/strings.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">My App</string>
    <string name="login">Login</string>
    <string name="welcome">Welcome, %1$s!</string>
</resources>
```

**res/values-ru/strings.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Моё приложение</string>
    <string name="login">Войти</string>
    <string name="welcome">Добро пожаловать, %1$s!</string>
</resources>
```

**res/values/colors.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="purple_500">#FF6200EE</color>
    <color name="teal_200">#FF03DAC5</color>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>
```

---

### Accessing Resources in Code

```kotlin
// Access string
val appName = getString(R.string.app_name)

// Access color
val color = getColor(R.color.purple_500)

// Access drawable
val icon = getDrawable(R.drawable.ic_home)

// Access dimension
val padding = resources.getDimensionPixelSize(R.dimen.default_padding)

// Formatted string
val welcome = getString(R.string.welcome, "John")  // "Welcome, John!"
```

---

## 3. AndroidManifest.xml — App Configuration

**Purpose:** Declares app components, permissions, and entry point.

### Complete Manifest Example

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.CAMERA" />

    <!-- Required features -->
    <uses-feature
        android:name="android.hardware.camera"
        android:required="false" />

    <application
        android:name=".MyApplication"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:theme="@style/Theme.MyApp"
        android:networkSecurityConfig="@xml/network_security_config">

        <!-- Main launcher activity -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Other activities -->
        <activity
            android:name=".LoginActivity"
            android:exported="false"
            android:theme="@style/Theme.Login" />

        <!-- Services -->
        <service
            android:name=".MusicPlayerService"
            android:exported="false"
            android:foregroundServiceType="mediaPlayback" />

        <!-- Broadcast receivers -->
        <receiver
            android:name=".BootReceiver"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>

        <!-- Content providers -->
        <provider
            android:name=".FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>

        <!-- Meta-data -->
        <meta-data
            android:name="com.google.android.gms.version"
            android:value="@integer/google_play_services_version" />
    </application>
</manifest>
```

---

### Key Manifest Elements

| Element | Purpose |
|---------|---------|
| `<uses-permission>` | Request permissions (INTERNET, CAMERA, etc.) |
| `<uses-feature>` | Declare required hardware features |
| `<application>` | App-level configuration (icon, theme, name) |
| `<activity>` | Declare activities |
| `<service>` | Declare services |
| `<receiver>` | Declare broadcast receivers |
| `<provider>` | Declare content providers |
| `<intent-filter>` | Declare supported intents |
| `<meta-data>` | Key-value pairs for configuration |

---

## 4. build.gradle — Build Configuration

**Purpose:** Configure build settings, dependencies, plugins.

### Project-Level build.gradle.kts

```kotlin
// Top-level build file
plugins {
    id("com.android.application") version "8.7.0" apply false
    id("org.jetbrains.kotlin.android") version "2.1.0" apply false
}

tasks.register("clean", Delete::class) {
    delete(rootProject.buildDir)
}
```

---

### Module-Level build.gradle.kts

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.devtools.ksp") version "2.1.0-1.0.29" // KSP for Room
}

android {
    namespace = "com.example.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        viewBinding = true
        compose = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.0"
    }
}
```

---

### Key Build Configuration Elements

| Element | Purpose |
|---------|---------|
| `compileSdk` | SDK version to compile against |
| `minSdk` | Minimum Android version supported |
| `targetSdk` | Target Android version |
| `versionCode` | Internal version number |
| `versionName` | User-facing version string |
| `buildTypes` | Debug/Release configurations |
| `dependencies` | External libraries |

---

## 5. libs/ — External Libraries

**Purpose:** Store external JAR files (less common now, use Gradle dependencies instead).

### Usage

```
libs/
└── custom-library.jar
```

**Reference in build.gradle.kts:**
```kotlin
dependencies {
    implementation(files("libs/custom-library.jar"))
    // Or for all JARs in libs/
    implementation(fileTree(mapOf("dir" to "libs", "include" to listOf("*.jar"))))
}
```

**Modern approach (recommended):**
```kotlin
dependencies {
    // ✅ Use Maven repositories instead
    implementation("com.squareup.okhttp3:okhttp:4.11.0")
}
```

---

## 6. assets/ — Raw Files

**Purpose:** Store raw files accessible at runtime (not compiled).

### Structure

```
assets/
├── database/
│   └── initial_data.db
├── fonts/
│   └── custom_font.ttf
├── config/
│   └── settings.json
└── html/
    └── about.html
```

---

### Accessing Assets

```kotlin
// Read file from assets
val inputStream = assets.open("config/settings.json")
val json = inputStream.bufferedReader().use { it.readText() }

// Read database
val dbFile = File(filesDir, "app.db")
assets.open("database/initial_data.db").use { input ->
    FileOutputStream(dbFile).use { output ->
        input.copyTo(output)
    }
}

// Load HTML in WebView
webView.loadUrl("file:///android_asset/html/about.html")
```

---

### res/ vs assets/

| Aspect | res/ | assets/ |
|--------|------|---------|
| **Structure** | Organized by type (layout/, drawable/) | Free-form directory structure |
| **Access** | Via R.id (compile-time) | Via AssetManager (runtime) |
| **Processing** | Compiled, optimized | Raw files, no processing |
| **Use case** | UI resources (layouts, strings, images) | Data files (JSON, databases, HTML) |

**Example:**
```kotlin
// res/ - compile-time, type-safe
val appName = getString(R.string.app_name)

// assets/ - runtime, string-based
val json = assets.open("data.json").bufferedReader().use { it.readText() }
```

---

## Additional Project Files

### gradle.properties

**Purpose:** Gradle configuration properties.

```properties

# Project-wide Gradle settings
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
org.gradle.parallel=true
org.gradle.caching=true

# AndroidX migration
android.useAndroidX=true
android.enableJetifier=true

# Kotlin code style
kotlin.code.style=official
```

---

### local.properties

**Purpose:** Local machine-specific settings (not committed to version control).

```properties

# Location of the Android SDK
sdk.dir=/Users/username/Library/Android/sdk
```

---

### proguard-rules.pro

**Purpose:** ProGuard/R8 code shrinking and obfuscation rules.

```proguard

# Keep model classes
-keep class com.example.app.data.model.** { *; }

# Keep Retrofit interfaces
-keepattributes Signature
-keep interface com.example.app.data.api.** { *; }

# Keep Gson annotations
-keepattributes *Annotation*
```

---

## Summary

**Android project parts:**

1. **`src/`** — Source code (Kotlin/Java)
   - `main/java/` - Production code
   - `test/` - Unit tests
   - `androidTest/` - Instrumentation tests

2. **`res/`** — Resources (compiled, optimized)
   - `layout/` - XML layouts
   - `values/` - Strings, colors, dimensions
   - `drawable/` - Images, icons
   - `mipmap/` - App icons

3. **`AndroidManifest.xml`** — App configuration
   - Components (Activity, Service, Receiver, Provider)
   - Permissions (`uses-permission`)
   - App metadata (icon, theme, name)

4. **`build.gradle`** — Build configuration
   - SDK versions (compileSdk, minSdk, targetSdk)
   - Dependencies (libraries)
   - Build types (debug, release)

5. **`libs/`** — External JAR libraries
   - Less common now (use Gradle dependencies)

6. **`assets/`** — Raw files (not compiled)
   - JSON, databases, HTML files
   - Accessed via AssetManager at runtime

**Key differences:**
- **res/** = compiled resources, accessed via R.id
- **assets/** = raw files, accessed via AssetManager

---

## Ответ

Проект Android состоит из:

- **`src/`** — исходный код (Kotlin/Java)
- **`res/`** — ресурсы (строки, изображения, макеты)
- **`AndroidManifest.xml`** — описание компонентов, разрешений, точки запуска
- **`build.gradle`** — настройки сборки, зависимости
- **`libs/`** — внешние библиотеки (JAR файлы)
- **`assets/`** — файлы, доступные в рантайме (сырые файлы)

**Основные отличия:**
- **res/** - компилируемые ресурсы, доступ через R.id
- **assets/** - сырые файлы, доступ через AssetManager

