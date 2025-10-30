---
id: 20251015-100154
title: Compose Multiplatform / Compose Multiplatform
aliases: [Compose Multiplatform, KMP Compose, Мультиплатформенный Compose]
topic: android
subtopics: [kmp, compose-multiplatform, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - c-jetpack-compose
  - q-compose-compiler-plugin--android--hard
  - q-kmm-architecture--android--hard
  - q-compose-custom-layout--android--hard
sources: []
created: 2025-10-15
updated: 2025-10-30
tags: [android/kmp, android/compose-multiplatform, android/ui-compose, compose, kmp, multiplatform, difficulty/hard]
---
# Вопрос (RU)
> Что такое Compose Multiplatform и как реализовать кроссплатформенную UI-архитектуру?

# Question (EN)
> What is Compose Multiplatform and how to implement cross-platform UI architecture?

---

## Ответ (RU)

**Compose Multiplatform (CMP)** — декларативный UI-фреймворк от JetBrains, расширяющий Jetpack Compose на Android, iOS, Desktop (JVM) и Web (Canvas/WASM). Использует Kotlin Multiplatform для шаринга UI-кода и бизнес-логики между платформами.

**Основное отличие от KMM**:
- KMM → шаринг domain/data слоя, нативный UI на каждой платформе
- CMP → единый UI-фреймворк + логика, один набор компонентов

**Целевой use case**: проекты с высоким уровнем UI-переиспользования (внутренние инструменты, enterprise-приложения, MVP), где приоритет — скорость разработки над платформенной кастомизацией.

### Project Structure

```kotlin
// shared/build.gradle.kts
kotlin {
  androidTarget()
  jvm("desktop")
  iosX64(); iosArm64(); iosSimulatorArm64()

  sourceSets {
    commonMain.dependencies {
      implementation(compose.runtime)
      implementation(compose.foundation)
      implementation(compose.material3)
    }
    androidMain.dependencies {
      implementation(compose.uiTooling)
    }
  }
}
```

### Expect/Actual для платформенных API

```kotlin
// ✅ commonMain
expect fun getPlatformName(): String

// ✅ androidMain
actual fun getPlatformName() = "Android"

// ✅ iosMain
actual fun getPlatformName() = "iOS"

// ❌ Избегать expect/actual для UI-компонентов
```

### Entry Points

```kotlin
// commonMain - общий UI
@Composable
fun App() {
  MaterialTheme {
    Screen()
  }
}

// androidMain
class MainActivity : ComponentActivity() {
  override fun onCreate(b: Bundle?) {
    super.onCreate(b)
    setContent { App() }
  }
}

// desktopMain
fun main() = application {
  Window(onCloseRequest = ::exitApplication, title = "App") {
    App()
  }
}
```

### Best Practices

**Shared**:
- State holders (ViewModel альтернативы)
- Navigation logic
- Screens, компоненты
- Theming

**Platform-specific**:
- Gesture handling (iOS swipe-back)
- Windowing (Desktop)
- Resources (через expect/actual)
- Performance profiling per target

### Trade-offs

**iOS Integration**:
- `UIViewController` wrapper → overhead
- Ограниченная SwiftUI interop
- Lifecycle mapping iOS ↔ Compose

**Web**:
- Canvas-based → проблемы с accessibility
- Bundle size (минимум ~2 MB)

**Desktop**:
- Windowing API различия (macOS/Windows/Linux)

## Answer (EN)

**Compose Multiplatform (CMP)** is a declarative UI framework by JetBrains extending Jetpack Compose to Android, iOS, Desktop (JVM), and Web (Canvas/WASM). Uses Kotlin Multiplatform to share UI code and business logic across platforms.

**Key difference from KMM**:
- KMM → shares domain/data layer, native UI per platform
- CMP → unified UI framework + logic, one component set

**Target use case**: projects with high UI reusability (internal tools, enterprise apps, MVPs) where development speed outweighs platform customization.

### Project Structure

```kotlin
// shared/build.gradle.kts
kotlin {
  androidTarget()
  jvm("desktop")
  iosX64(); iosArm64(); iosSimulatorArm64()

  sourceSets {
    commonMain.dependencies {
      implementation(compose.runtime)
      implementation(compose.foundation)
      implementation(compose.material3)
    }
    androidMain.dependencies {
      implementation(compose.uiTooling)
    }
  }
}
```

### Expect/Actual for Platform APIs

```kotlin
// ✅ commonMain
expect fun getPlatformName(): String

// ✅ androidMain
actual fun getPlatformName() = "Android"

// ✅ iosMain
actual fun getPlatformName() = "iOS"

// ❌ Avoid expect/actual for UI components
```

### Entry Points

```kotlin
// commonMain - shared UI
@Composable
fun App() {
  MaterialTheme {
    Screen()
  }
}

// androidMain
class MainActivity : ComponentActivity() {
  override fun onCreate(b: Bundle?) {
    super.onCreate(b)
    setContent { App() }
  }
}

// desktopMain
fun main() = application {
  Window(onCloseRequest = ::exitApplication, title = "App") {
    App()
  }
}
```

### Best Practices

**Shared**:
- State holders (ViewModel alternatives)
- Navigation logic
- Screens, components
- Theming

**Platform-specific**:
- Gesture handling (iOS swipe-back)
- Windowing (Desktop)
- Resources (via expect/actual)
- Performance profiling per target

### Trade-offs

**iOS Integration**:
- `UIViewController` wrapper → overhead
- Limited SwiftUI interop
- Lifecycle mapping iOS ↔ Compose

**Web**:
- Canvas-based → accessibility challenges
- Bundle size (minimum ~2 MB)

**Desktop**:
- Windowing API differences (macOS/Windows/Linux)

---

## Follow-ups
- How to handle platform-specific navigation patterns (iOS back swipe) without leaking into common code?
- What are performance implications of UIViewController wrapper on iOS vs native SwiftUI?
- How to structure expect/actual for filesystem, haptics, and secure storage APIs?
- When should you choose native UI over CMP for specific platform screens?
- How to minimize Web bundle size while sharing UI code across platforms?

## References
- [[c-jetpack-compose]]
- https://www.jetbrains.com/lp/compose-multiplatform/
- https://github.com/JetBrains/compose-multiplatform
- https://developer.android.com/develop/ui/compose

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]
- [[q-how-jetpack-compose-works--android--medium]]

### Related (Same Level)
- [[q-kmm-architecture--android--hard]]
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]]
