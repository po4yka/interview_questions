---
id: 202510051234005
title: "Gradle Build System / Система сборки Gradle"
topic: android
status: reviewed
created: 2025-10-05
updated: 2025-10-05
difficulty: medium
topics:
  - android
subtopics:
  - gradle
  - build-variants
  - dependency-management
tags:
  - android
  - gradle
  - build-system
  - dependency-management
  - groovy
  - kotlin-dsl
  - difficulty/medium
language_tags:
  - en
  - ru
original_language: en
source: https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20is%20Gradle.md
author: null
related:
  - "[[moc-android]]"
  - "[[q-build-variants-android--android--medium]]"
  - "[[q-proguard-r8--android--medium]]"
moc:
  - "[[moc-android]]"
connections: []
---

# Gradle Build System / Система сборки Gradle

## English

### What is Gradle?

Gradle is an open-source build automation tool flexible enough to build almost any type of software. Gradle makes few assumptions about what you're trying to build or how to build it. This makes Gradle particularly flexible.

### Gradle in Android

Android Studio uses Gradle to automate and manage the build process while letting you define flexible, custom build configurations.

**Key components:**
- **Gradle**: The build toolkit
- **Android Gradle Plugin**: Works with the build toolkit to provide processes and configurable settings specific to building and testing Android apps

**Key features:**
- Each build configuration can define its own set of code and resources
- Reuse parts common to all versions of your app
- Run independent of Android Studio (command line, CI/CD servers)

### Language Support

Gradle runs on:
- **Groovy DSL** (Domain Specific Language) - traditional syntax
- **Kotlin DSL** - modern, type-safe alternative

### Android Build Glossary

Gradle and the Android Gradle plugin help you configure the following aspects of your build:

#### 1. Build Types

**Definition**: Build types define certain properties that Gradle uses when building and packaging your app.

**Characteristics:**
- Typically configured for different stages of your development lifecycle
- At least one build type must be defined
- Android Studio creates `debug` and `release` build types by default

**Examples:**
- **Debug build type**: Enables debug options, signs with debug key
- **Release build type**: May shrink, obfuscate, and sign with release key for distribution

**Code example:**
```kotlin
android {
    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            debuggable = true
        }
        release {
            minifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

#### 2. Product Flavors

**Definition**: Product flavors represent different versions of your app that you can release to users.

**Characteristics:**
- Optional - must be created manually
- Can use different code and resources
- Share and reuse parts common to all versions

**Examples:**
- Free and paid versions
- Different white-label versions
- API-level specific versions

**Code example:**
```kotlin
android {
    flavorDimensions += "version"
    productFlavors {
        create("free") {
            dimension = "version"
            applicationIdSuffix = ".free"
        }
        create("paid") {
            dimension = "version"
            applicationIdSuffix = ".paid"
        }
    }
}
```

#### 3. Build Variants

**Definition**: A build variant is a cross-product of build type and product flavor.

**Characteristics:**
- The configuration Gradle uses to build your app
- Not configured directly - formed from build types and product flavors
- Used to build different versions during development and for distribution

**Examples:**
- If you have `debug` and `release` build types
- And `free` and `paid` product flavors
- You get 4 build variants:
  - `freeDebug`
  - `freeRelease`
  - `paidDebug`
  - `paidRelease`

#### 4. Manifest Entries

**Definition**: Values you can specify for some properties of the manifest file in the build variant configuration.

**Characteristics:**
- Build values override existing values in the manifest file
- Useful for generating multiple variants with different properties
- Manifest merger tool merges settings when multiple manifests are present

**Code example:**
```kotlin
android {
    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
}
```

#### 5. Dependencies

**Definition**: The build system manages project dependencies from your local file system and from remote repositories.

**Benefits:**
- No need to manually search, download, and copy binary packages
- Automatic dependency resolution
- Transitive dependency support

#### 6. Signing

**Definition**: The build system lets you specify signing settings in the build configuration.

**Characteristics:**
- Can automatically sign your app during the build process
- Debug version: Signed with default key and certificate (no password prompt)
- Release version: Not signed unless you explicitly define a signing configuration

**Code example:**
```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("keystore.jks")
            storePassword = "password"
            keyAlias = "key"
            keyPassword = "password"
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

#### 7. Code and Resource Shrinking

**Definition**: The build system lets you specify a different ProGuard rules file for each build variant.

**Features:**
- Built-in shrinking tools (R8)
- Shrinks code and resources
- Helps reduce APK or AAB size
- Different rules for different build variants

**Code example:**
```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

#### 8. Multiple APK Support

**Definition**: The build system can automatically build different APKs.

**Capabilities:**
- Each APK contains only the code and resources needed for specific configurations
- Can split by screen density
- Can split by Application Binary Interface (ABI)

**Code example:**
```kotlin
android {
    splits {
        abi {
            isEnable = true
            reset()
            include("x86", "x86_64", "armeabi-v7a", "arm64-v8a")
            isUniversalApk = true
        }
    }
}
```

### Build Configuration Files

When starting a new project, Android Studio automatically creates Gradle files based on sensible defaults.

#### Project File Structure

```
└── MyApp/                    # Project
    ├── build.gradle.kts      # Top-level build file
    ├── settings.gradle.kts   # Settings file
    └── app/                  # Module
        ├── build.gradle.kts  # Module-level build file
        ├── libs/
        └── src/
            └── main/         # Source set
                ├── java/
                │   └── com.example.myapp
                ├── res/
                │   ├── drawable/
                │   ├── values/
                │   └── ...
                └── AndroidManifest.xml
```

#### 1. The Gradle Settings File

**File**: `settings.gradle.kts` (Kotlin DSL) or `settings.gradle` (Groovy DSL)

**Location**: Root project directory

**Purpose**:
- Defines project-level repository settings
- Specifies which modules to include when building your app
- Multi-module projects need to specify each module for the final build

**Example:**
```kotlin
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "MyApp"
include(":app")
```

#### 2. The Top-Level Build File

**File**: `build.gradle.kts` (Kotlin DSL) or `build.gradle` (Groovy DSL)

**Location**: Root project directory

**Purpose**:
- Defines dependencies that apply to all modules in your project
- Contains code to clean your build directory

**Example:**
```kotlin
plugins {
    id("com.android.application") version "8.1.0" apply false
    id("com.android.library") version "8.1.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.0" apply false
}

tasks.register("clean", Delete::class) {
    delete(rootProject.buildDir)
}
```

#### 3. The Module-Level Build File

**File**: `build.gradle.kts` (Kotlin DSL) or `build.gradle` (Groovy DSL)

**Location**: Each `project/module/` directory

**Purpose**:
- Configure build settings for the specific module
- Provide custom packaging options
- Define additional build types and product flavors
- Override settings in `main/` app manifest or top-level build script

**Example:**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.myapp"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

#### 4. Gradle Properties Files

Two properties files in the root project directory specify settings for the Gradle build toolkit:

**`gradle.properties`**:
- Configure project-wide Gradle settings
- Example: Gradle daemon's maximum heap size

```properties
org.gradle.jvmargs=-Xmx2048m
android.useAndroidX=true
kotlin.code.style=official
```

**`local.properties`**:
- Configure local environment properties
- Not checked into version control
- Properties:
  - `ndk.dir` - Path to the NDK (deprecated)
  - `sdk.dir` - Path to the SDK
  - `cmake.dir` - Path to CMake
  - `ndk.symlinkdir` - Symlink to NDK (Android Studio 3.5+)

```properties
sdk.dir=/Users/username/Library/Android/sdk
```

---

## Русский

### Что такое Gradle?

Gradle - это инструмент автоматизации сборки с открытым исходным кодом, достаточно гибкий для сборки почти любого типа программного обеспечения. Gradle делает мало предположений о том, что вы пытаетесь собрать или как это собрать. Это делает Gradle особенно гибким.

### Gradle в Android

Android Studio использует Gradle для автоматизации и управления процессом сборки, позволяя вам определять гибкие, настраиваемые конфигурации сборки.

**Ключевые компоненты:**
- **Gradle**: Инструментарий для сборки
- **Android Gradle Plugin**: Работает с инструментарием сборки для предоставления процессов и настраиваемых параметров, специфичных для сборки и тестирования приложений Android

**Ключевые возможности:**
- Каждая конфигурация сборки может определять свой собственный набор кода и ресурсов
- Повторное использование частей, общих для всех версий вашего приложения
- Работа независимо от Android Studio (командная строка, серверы CI/CD)

### Поддержка языков

Gradle работает на:
- **Groovy DSL** (Domain Specific Language) - традиционный синтаксис
- **Kotlin DSL** - современная, типобезопасная альтернатива

### Глоссарий сборки Android

Gradle и плагин Android Gradle помогают настроить следующие аспекты вашей сборки:

#### 1. Типы сборки (Build Types)

**Определение**: Типы сборки определяют определенные свойства, которые Gradle использует при сборке и упаковке вашего приложения.

**Характеристики:**
- Обычно настраиваются для разных этапов вашего жизненного цикла разработки
- Должен быть определен хотя бы один тип сборки
- Android Studio создает типы сборки `debug` и `release` по умолчанию

**Примеры:**
- **Тип сборки Debug**: Включает параметры отладки, подписывается отладочным ключом
- **Тип сборки Release**: Может сжимать, обфусцировать и подписывать релизным ключом для распространения

**Пример кода:**
```kotlin
android {
    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            debuggable = true
        }
        release {
            minifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

#### 2. Варианты продукта (Product Flavors)

**Определение**: Варианты продукта представляют различные версии вашего приложения, которые вы можете выпускать для пользователей.

**Характеристики:**
- Опциональны - должны создаваться вручную
- Могут использовать разный код и ресурсы
- Совместно используют и повторно используют части, общие для всех версий

**Примеры:**
- Бесплатная и платная версии
- Различные white-label версии
- Версии, специфичные для уровня API

**Пример кода:**
```kotlin
android {
    flavorDimensions += "version"
    productFlavors {
        create("free") {
            dimension = "version"
            applicationIdSuffix = ".free"
        }
        create("paid") {
            dimension = "version"
            applicationIdSuffix = ".paid"
        }
    }
}
```

#### 3. Варианты сборки (Build Variants)

**Определение**: Вариант сборки - это перекрестное произведение типа сборки и варианта продукта.

**Характеристики:**
- Конфигурация, которую Gradle использует для сборки вашего приложения
- Не настраивается напрямую - формируется из типов сборки и вариантов продукта
- Используется для сборки различных версий во время разработки и для распространения

**Примеры:**
- Если у вас есть типы сборки `debug` и `release`
- И варианты продукта `free` и `paid`
- Вы получите 4 варианта сборки:
  - `freeDebug`
  - `freeRelease`
  - `paidDebug`
  - `paidRelease`

#### 4. Записи манифеста (Manifest Entries)

**Определение**: Значения, которые вы можете указать для некоторых свойств файла манифеста в конфигурации варианта сборки.

**Характеристики:**
- Значения сборки переопределяют существующие значения в файле манифеста
- Полезно для генерации нескольких вариантов с различными свойствами
- Инструмент слияния манифестов объединяет настройки, когда присутствует несколько манифестов

**Пример кода:**
```kotlin
android {
    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
}
```

#### 5. Зависимости (Dependencies)

**Определение**: Система сборки управляет зависимостями проекта из вашей локальной файловой системы и из удаленных репозиториев.

**Преимущества:**
- Не нужно вручную искать, загружать и копировать бинарные пакеты
- Автоматическое разрешение зависимостей
- Поддержка транзитивных зависимостей

**Пример кода:**
```kotlin
dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
}
```

#### 6. Подписание (Signing)

**Определение**: Система сборки позволяет указать настройки подписания в конфигурации сборки.

**Характеристики:**
- Может автоматически подписывать ваше приложение во время процесса сборки
- Версия Debug: Подписана ключом и сертификатом по умолчанию (без запроса пароля)
- Версия Release: Не подписана, если вы явно не определили конфигурацию подписания

**Пример кода:**
```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("keystore.jks")
            storePassword = "password"
            keyAlias = "key"
            keyPassword = "password"
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

#### 7. Сжатие кода и ресурсов

**Определение**: Система сборки позволяет указать различный файл правил ProGuard для каждого варианта сборки.

**Возможности:**
- Встроенные инструменты сжатия (R8)
- Сжимает код и ресурсы
- Помогает уменьшить размер APK или AAB
- Различные правила для разных вариантов сборки

**Пример кода:**
```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

#### 8. Поддержка нескольких APK

**Определение**: Система сборки может автоматически создавать различные APK.

**Возможности:**
- Каждый APK содержит только код и ресурсы, необходимые для конкретных конфигураций
- Можно разделить по плотности экрана
- Можно разделить по Application Binary Interface (ABI)

**Пример кода:**
```kotlin
android {
    splits {
        abi {
            isEnable = true
            reset()
            include("x86", "x86_64", "armeabi-v7a", "arm64-v8a")
            isUniversalApk = true
        }
    }
}
```

### Файлы конфигурации сборки

При создании нового проекта Android Studio автоматически создает файлы Gradle на основе разумных значений по умолчанию.

#### Структура файлов проекта

```
└── MyApp/                    # Проект
    ├── build.gradle.kts      # Файл сборки верхнего уровня
    ├── settings.gradle.kts   # Файл настроек
    └── app/                  # Модуль
        ├── build.gradle.kts  # Файл сборки уровня модуля
        ├── libs/
        └── src/
            └── main/         # Набор источников
                ├── java/
                │   └── com.example.myapp
                ├── res/
                │   ├── drawable/
                │   ├── values/
                │   └── ...
                └── AndroidManifest.xml
```

#### 1. Файл настроек Gradle

**Файл**: `settings.gradle.kts` (Kotlin DSL) или `settings.gradle` (Groovy DSL)

**Расположение**: Корневая директория проекта

**Назначение**:
- Определяет настройки репозитория уровня проекта
- Указывает, какие модули включать при сборке вашего приложения
- Многомодульные проекты должны указывать каждый модуль для финальной сборки

**Пример:**
```kotlin
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "MyApp"
include(":app")
```

#### 2. Файл сборки верхнего уровня

**Файл**: `build.gradle.kts` (Kotlin DSL) или `build.gradle` (Groovy DSL)

**Расположение**: Корневая директория проекта

**Назначение**:
- Определяет зависимости, применимые ко всем модулям в вашем проекте
- Содержит код для очистки вашей директории сборки

**Пример:**
```kotlin
plugins {
    id("com.android.application") version "8.1.0" apply false
    id("com.android.library") version "8.1.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.0" apply false
}

tasks.register("clean", Delete::class) {
    delete(rootProject.buildDir)
}
```

#### 3. Файл сборки уровня модуля

**Файл**: `build.gradle.kts` (Kotlin DSL) или `build.gradle` (Groovy DSL)

**Расположение**: Каждая директория `project/module/`

**Назначение**:
- Настройка параметров сборки для конкретного модуля
- Предоставление пользовательских опций упаковки
- Определение дополнительных типов сборки и вариантов продукта
- Переопределение настроек в манифесте приложения `main/` или скрипте сборки верхнего уровня

**Пример:**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.myapp"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
}
```

#### 4. Файлы свойств Gradle

Два файла свойств в корневой директории проекта указывают настройки для инструментария сборки Gradle:

**`gradle.properties`**:
- Настройка параметров Gradle на уровне проекта
- Пример: Максимальный размер кучи демона Gradle

```properties
org.gradle.jvmargs=-Xmx2048m
android.useAndroidX=true
kotlin.code.style=official
```

**`local.properties`**:
- Настройка свойств локального окружения
- Не включается в систему контроля версий
- Свойства:
  - `ndk.dir` - Путь к NDK (устарело)
  - `sdk.dir` - Путь к SDK
  - `cmake.dir` - Путь к CMake
  - `ndk.symlinkdir` - Символическая ссылка на NDK (Android Studio 3.5+)

```properties
sdk.dir=/Users/username/Library/Android/sdk
```

---

## References

- [Android Developer Docs: Configure your build](https://developer.android.com/build)
- [Gradle Docs: What is Gradle?](https://docs.gradle.org/current/userguide/what_is_gradle.html)
- [Medium: Gradle Basics for Android Developers](https://medium.com/android-dev-corner/gradle-basics-for-android-developers-9d7a3bf062bb)
- [Kodeco: Gradle Tutorial for Android: Getting Started](https://www.kodeco.com/249-gradle-tutorial-for-android-getting-started)
- [Build Type, Product Flavor, Build Variant](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/Build%20Type%2C%20Product%20Flavor%2C%20Build%20Variant.md)
- [ProGuard](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What's%20Proguard.md)
- [App Bundles](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20App%20Bundles.md)
