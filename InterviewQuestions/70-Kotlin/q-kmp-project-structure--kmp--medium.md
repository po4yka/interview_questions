---
id: kotlin-kmp-002
title: "KMP Project Structure / Структура KMP проекта"
aliases: [KMP Source Sets, commonMain androidMain iosMain, Kotlin Multiplatform Structure]
topic: kotlin
subtopics: [kmp, multiplatform, project-structure]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin]
created: 2026-01-23
updated: 2026-01-23
tags: [kotlin, kmp, multiplatform, source-sets, project-structure, difficulty/medium]
---

# Question (EN)
> What is the source set structure in Kotlin Multiplatform projects (commonMain, androidMain, iosMain)?

# Vopros (RU)
> Какова структура source sets в проектах Kotlin Multiplatform (commonMain, androidMain, iosMain)?

## Answer (EN)

Kotlin Multiplatform projects organize code into **source sets** - hierarchical containers that group code by platform or capability.

### Standard Source Set Structure

```
shared/
  src/
    commonMain/          # Shared code for all platforms
      kotlin/
    commonTest/          # Tests for shared code
      kotlin/

    androidMain/         # Android-specific code
      kotlin/
    androidUnitTest/     # Android unit tests
      kotlin/

    iosMain/             # iOS-specific code (all iOS targets)
      kotlin/
    iosTest/             # iOS tests
      kotlin/

    iosArm64Main/        # iOS device-specific (optional)
      kotlin/
    iosSimulatorArm64Main/  # iOS simulator-specific (optional)
      kotlin/

    jvmMain/             # JVM/Desktop-specific (optional)
      kotlin/
    jsMain/              # JavaScript-specific (optional)
      kotlin/
```

### Source Set Hierarchy

```
                    commonMain
                        |
         +--------------+--------------+
         |              |              |
    androidMain     iosMain        jvmMain
                        |
              +---------+---------+
              |                   |
        iosArm64Main    iosSimulatorArm64Main
```

### Gradle Configuration (build.gradle.kts)

```kotlin
kotlin {
    // Target declarations
    androidTarget {
        compilations.all {
            kotlinOptions {
                jvmTarget = "17"
            }
        }
    }

    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach {
        it.binaries.framework {
            baseName = "shared"
            isStatic = true
        }
    }

    // Source set dependencies
    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
            implementation(libs.ktor.client.core)
        }

        commonTest.dependencies {
            implementation(libs.kotlin.test)
        }

        androidMain.dependencies {
            implementation(libs.ktor.client.android)
            implementation(libs.androidx.lifecycle.viewmodel)
        }

        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
        }
    }
}
```

### Code Visibility Rules

| Source Set | Can Access | Accessed By |
|------------|------------|-------------|
| **commonMain** | stdlib, multiplatform libs | All platform source sets |
| **androidMain** | commonMain + Android SDK | Android app |
| **iosMain** | commonMain + iOS/Darwin APIs | iOS app |
| **iosArm64Main** | iosMain + device-specific | iOS device builds |

### Intermediate Source Sets

Create shared code between specific platforms:

```kotlin
sourceSets {
    // Create intermediate source set for mobile platforms
    val mobileMain by creating {
        dependsOn(commonMain.get())
    }

    androidMain {
        dependsOn(mobileMain)
    }

    iosMain {
        dependsOn(mobileMain)
    }

    // Native-specific intermediate
    val nativeMain by creating {
        dependsOn(commonMain.get())
    }

    iosMain {
        dependsOn(nativeMain)
    }

    // linuxMain, macosMain, etc. would also depend on nativeMain
}
```

### Typical Project Layout

```
my-kmp-project/
  shared/                    # KMP module
    src/
      commonMain/
        kotlin/
          com/example/
            data/
              Repository.kt      # Shared interfaces
              models/
                User.kt          # Data classes
            domain/
              UseCases.kt        # Business logic
            Platform.kt          # expect declarations
      androidMain/
        kotlin/
          com/example/
            Platform.android.kt  # actual implementations
      iosMain/
        kotlin/
          com/example/
            Platform.ios.kt      # actual implementations
    build.gradle.kts

  androidApp/                # Android application
    src/main/
    build.gradle.kts

  iosApp/                    # iOS application (Xcode project)
    iosApp/
    iosApp.xcodeproj

  build.gradle.kts           # Root build file
  settings.gradle.kts
```

### Best Practices

1. **Maximize commonMain code** - push as much logic as possible to shared code
2. **Use intermediate source sets** for platform families (mobile, native, etc.)
3. **Keep platform source sets thin** - only truly platform-specific code
4. **Follow naming conventions** - `*.android.kt`, `*.ios.kt` for clarity

---

## Otvet (RU)

Проекты Kotlin Multiplatform организуют код в **source sets** - иерархические контейнеры, группирующие код по платформе или возможностям.

### Стандартная структура Source Sets

```
shared/
  src/
    commonMain/          # Общий код для всех платформ
      kotlin/
    commonTest/          # Тесты для общего кода
      kotlin/

    androidMain/         # Android-специфичный код
      kotlin/
    androidUnitTest/     # Android unit тесты
      kotlin/

    iosMain/             # iOS-специфичный код (все iOS таргеты)
      kotlin/
    iosTest/             # iOS тесты
      kotlin/

    iosArm64Main/        # iOS устройство-специфичный (опционально)
      kotlin/
    iosSimulatorArm64Main/  # iOS симулятор-специфичный (опционально)
      kotlin/

    jvmMain/             # JVM/Desktop-специфичный (опционально)
      kotlin/
    jsMain/              # JavaScript-специфичный (опционально)
      kotlin/
```

### Иерархия Source Sets

```
                    commonMain
                        |
         +--------------+--------------+
         |              |              |
    androidMain     iosMain        jvmMain
                        |
              +---------+---------+
              |                   |
        iosArm64Main    iosSimulatorArm64Main
```

### Конфигурация Gradle (build.gradle.kts)

```kotlin
kotlin {
    // Объявления таргетов
    androidTarget {
        compilations.all {
            kotlinOptions {
                jvmTarget = "17"
            }
        }
    }

    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach {
        it.binaries.framework {
            baseName = "shared"
            isStatic = true
        }
    }

    // Зависимости source sets
    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
            implementation(libs.ktor.client.core)
        }

        commonTest.dependencies {
            implementation(libs.kotlin.test)
        }

        androidMain.dependencies {
            implementation(libs.ktor.client.android)
            implementation(libs.androidx.lifecycle.viewmodel)
        }

        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
        }
    }
}
```

### Правила видимости кода

| Source Set | Имеет доступ к | Доступен для |
|------------|----------------|--------------|
| **commonMain** | stdlib, multiplatform библиотеки | Все платформенные source sets |
| **androidMain** | commonMain + Android SDK | Android приложение |
| **iosMain** | commonMain + iOS/Darwin API | iOS приложение |
| **iosArm64Main** | iosMain + устройство-специфичное | iOS билды для устройств |

### Промежуточные Source Sets

Создание общего кода между конкретными платформами:

```kotlin
sourceSets {
    // Промежуточный source set для мобильных платформ
    val mobileMain by creating {
        dependsOn(commonMain.get())
    }

    androidMain {
        dependsOn(mobileMain)
    }

    iosMain {
        dependsOn(mobileMain)
    }

    // Native-специфичный промежуточный
    val nativeMain by creating {
        dependsOn(commonMain.get())
    }

    iosMain {
        dependsOn(nativeMain)
    }

    // linuxMain, macosMain и т.д. также зависели бы от nativeMain
}
```

### Типичная структура проекта

```
my-kmp-project/
  shared/                    # KMP модуль
    src/
      commonMain/
        kotlin/
          com/example/
            data/
              Repository.kt      # Общие интерфейсы
              models/
                User.kt          # Data классы
            domain/
              UseCases.kt        # Бизнес-логика
            Platform.kt          # expect объявления
      androidMain/
        kotlin/
          com/example/
            Platform.android.kt  # actual реализации
      iosMain/
        kotlin/
          com/example/
            Platform.ios.kt      # actual реализации
    build.gradle.kts

  androidApp/                # Android приложение
    src/main/
    build.gradle.kts

  iosApp/                    # iOS приложение (Xcode проект)
    iosApp/
    iosApp.xcodeproj

  build.gradle.kts           # Корневой build файл
  settings.gradle.kts
```

### Лучшие практики

1. **Максимизируйте код в commonMain** - выносите как можно больше логики в общий код
2. **Используйте промежуточные source sets** для семейств платформ (mobile, native и т.д.)
3. **Держите платформенные source sets тонкими** - только действительно платформо-специфичный код
4. **Следуйте соглашениям по именованию** - `*.android.kt`, `*.ios.kt` для ясности

---

## Follow-ups

- How do you share code between Android and JVM targets?
- What is the default source set hierarchy in KMP?
- How do test source sets relate to main source sets?
- How do you configure custom intermediate source sets?

## Dopolnitelnye Voprosy (RU)

- Как разделить код между Android и JVM таргетами?
- Какова иерархия source sets по умолчанию в KMP?
- Как тестовые source sets связаны с main source sets?
- Как настроить кастомные промежуточные source sets?

## References

- [KMP Project Structure](https://kotlinlang.org/docs/multiplatform-discover-project.html)
- [Source Set Hierarchy](https://kotlinlang.org/docs/multiplatform-hierarchy.html)

## Ssylki (RU)

- [[c-kotlin]]
- [Структура проекта KMP](https://kotlinlang.org/docs/multiplatform-discover-project.html)

## Related Questions

- [[q-kmp-expect-actual--kmp--medium]]
- [[q-kmp-gradle-setup--kmp--medium]]
