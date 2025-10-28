---
id: 20251015-100154
title: Compose Multiplatform / Compose Multiplatform (обзор)
aliases: [Compose Multiplatform, Compose Multiplatform overview, Мультиплатформенный Compose]
topic: android
subtopics: [ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-compose-compiler-plugin--android--hard
  - q-compose-custom-layout--android--hard
  - q-compose-lazy-layout-optimization--android--hard
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/ui-compose, difficulty/hard]
---
# Вопрос (RU)
> Что такое Compose Multiplatform и как его использовать для кроссплатформенной разработки?

# Question (EN)
> What is Compose Multiplatform and how to use it for cross-platform development?

---

## Ответ (RU)

### Определение
- Compose Multiplatform (CMP) - это расширение Jetpack Compose для создания UI на нескольких платформах: Android, iOS, Desktop, Web
- Использует Kotlin Multiplatform для шаринга кода между платформами
- Позволяет переиспользовать UI компоненты, состояние, навигацию и тему

### CMP vs KMM
- **KMM**: шаринг бизнес-логики и данных; UI остается нативным для каждой платформы
- **CMP**: шаринг UI + логики; единый UI фреймворк для всех платформ

### Структура проекта
```kotlin
// shared/build.gradle.kts
plugins {
  kotlin("multiplatform")
  id("org.jetbrains.compose")
  id("com.android.library")
}

kotlin {
  androidTarget()
  jvm("desktop")
  js(IR) { browser() }
  listOf(iosX64(), iosArm64(), iosSimulatorArm64())

  sourceSets {
    val commonMain by getting
    val androidMain by getting
    val iosMain by creating { dependsOn(commonMain) }
    val desktopMain by getting
    val jsMain by getting
  }
}
```

### Expect/Actual для платформенных API
```kotlin
// commonMain
expect fun platformName(): String

// androidMain
actual fun platformName() = "Android"

// iosMain
actual fun platformName() = "iOS"
```

### Точки входа
```kotlin
// commonMain - общий UI
@Composable
fun App() {
  MaterialTheme {
    Navigation()
  }
}

// ✅ Android
class MainActivity: ComponentActivity() {
  override fun onCreate(b: Bundle?) {
    super.onCreate(b)
    setContent { App() }
  }
}

// ✅ Desktop
fun main() = application {
  Window(onCloseRequest = ::exitApplication) {
    App()
  }
}
```

### Best Practices
- **Shared**: state holders, screens, theming, navigation
- **Platform-specific**: gestures, windowing, resources
- **Performance**: stable keys, `remember` для вычислений, профилирование на каждой платформе
- **Testing**: скриншотные тесты на всех таргетах

### Ограничения
- iOS: интеграция через UIViewController, ограниченная интеропа с SwiftUI
- Web: canvas-based рендеринг, вопросы bundle size и accessibility
- Desktop: различия в windowing и input обработке

## Answer (EN)

### Definition
- Compose Multiplatform (CMP) brings Compose UI to Android, iOS, Desktop, and Web targets
- Built on Kotlin Multiplatform for code sharing across platforms
- Allows sharing UI components, state management, navigation, and theming

### CMP vs KMM
- **KMM**: shares domain/data logic; UI remains platform-native (Compose on Android, SwiftUI on iOS)
- **CMP**: shares UI + logic; one UI framework across all targets

### Project Structure
```kotlin
// shared/build.gradle.kts
plugins {
  kotlin("multiplatform")
  id("org.jetbrains.compose")
  id("com.android.library")
}

kotlin {
  androidTarget()
  jvm("desktop")
  js(IR) { browser() }
  listOf(iosX64(), iosArm64(), iosSimulatorArm64())

  sourceSets {
    val commonMain by getting
    val androidMain by getting
    val iosMain by creating { dependsOn(commonMain) }
    val desktopMain by getting
    val jsMain by getting
  }
}
```

### Expect/Actual for Platform APIs
```kotlin
// commonMain
expect fun platformName(): String

// androidMain
actual fun platformName() = "Android"

// iosMain
actual fun platformName() = "iOS"
```

### Entry Points
```kotlin
// commonMain - shared UI
@Composable
fun App() {
  MaterialTheme {
    Navigation()
  }
}

// ✅ Android
class MainActivity: ComponentActivity() {
  override fun onCreate(b: Bundle?) {
    super.onCreate(b)
    setContent { App() }
  }
}

// ✅ Desktop
fun main() = application {
  Window(onCloseRequest = ::exitApplication) {
    App()
  }
}
```

### Best Practices
- **Share**: state holders, screens, theming, navigation
- **Platform-specific**: gestures, windowing, resources
- **Performance**: stable keys, `remember` for computations, profile each target
- **Testing**: screenshot tests across all targets

### Limitations
- iOS: integration via UIViewController wrapper, limited SwiftUI interop
- Web: canvas-based rendering, bundle size and accessibility concerns
- Desktop: windowing and input handling differences

---

## Follow-ups
- How to structure expect/actual for filesystem, haptics, and secure storage?
- Strategies to minimize bundle size on Web while sharing UI code?
- How to handle platform-specific navigation patterns without leaking into common code?
- What are the performance trade-offs between CMP and native UI on iOS?

## References
- https://www.jetbrains.com/lp/compose-multiplatform/
- https://github.com/JetBrains/compose-multiplatform
- https://developer.android.com/develop/ui/compose

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-lazy-layout-optimization--android--hard]]

### Advanced (Harder)
- None
