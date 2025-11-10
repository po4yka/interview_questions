---
id: android-191
title: Compose Multiplatform / Compose Multiplatform
aliases: [Compose Multiplatform, KMP Compose]
topic: android
subtopics:
- compose-multiplatform
- kmp
- ui-compose
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-jetpack-compose
- q-compose-compiler-plugin--android--hard
- q-compose-custom-layout--android--hard
- q-kmm-architecture--android--hard
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/compose-multiplatform, android/kmp, android/ui-compose, compose, difficulty/hard, kmp, multiplatform]

---

# Вопрос (RU)
> Что такое Compose Multiplatform и как реализовать кроссплатформенную UI-архитектуру?

# Question (EN)
> What is Compose Multiplatform and how to implement cross-platform UI architecture?

---

## Ответ (RU)

**Compose Multiplatform (CMP)** — декларативный UI-фреймворк от JetBrains, расширяющий подход `Jetpack Compose` на Android, iOS, Desktop (`JVM`) и Web (рендеринг поверх Canvas/DOM, в том числе через WASM). Использует `Kotlin Multiplatform` для шаринга UI-кода и бизнес-логики между платформами.

**Основное отличие от KMM**:
- KMM → шаринг `domain`/`data` слоя, нативный UI на каждой платформе
- CMP → единый UI-фреймворк + логика, один набор компонентов (с возможностью платформенных адаптаций)

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
      // пример: tooling-просмотрщики для Android
      implementation(compose.uiToolingPreview)
    }
  }
}
```

### Expect/Actual Для Платформенных API

```kotlin
// ✅ commonMain
expect fun getPlatformName(): String

// ✅ androidMain
actual fun getPlatformName() = "Android"

// ✅ iosMain
actual fun getPlatformName() = "iOS"

// ❌ Избегать expect/actual для UI-компонентов,
//    вместо этого инкапсулировать платформенно-специфичный UI в отдельных обёртках.
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
- State holders (`ViewModel` альтернативы)
- Navigation logic
- Screens, компоненты
- Theming

**Platform-specific**:
- Gesture handling (iOS swipe-back)
- Windowing (`Desktop`)
- Resources (через `expect`/`actual` и/или предоставленные CMP API для ресурсов)
- Performance profiling per target

### Trade-offs

**iOS Integration**:
- `UIViewController` wrapper → overhead
- Ограниченная `SwiftUI` interop
- Lifecycle mapping iOS ↔ Compose

**Web**:
- Реализации на базе Canvas/DOM → сложности с accessibility
- `Bundle` size (минимум около нескольких MB)

**Desktop**:
- Windowing API различия (`macOS`/`Windows`/`Linux`)

### Краткая версия

- CMP расширяет декларативный подход `Jetpack Compose` на несколько платформ через `Kotlin Multiplatform`.
- Общий код: UI-дерево, состояние, навигация, тема.
- Платформенный код: интеграция с системными API, навигация, жесты, ресурсы.
- Использовать там, где важны переиспользование UI и скорость разработки.

### Подробная версия

- Описать требования к переиспользованию: какие части UI и логики должны быть общими.
- Спроектировать общий модуль с Composable-экранами и бизнес-логикой на KMP.
- Для каждой платформы реализовать точку входа и обёртки над системными API.
- Ясно разделить общий и платформенный слои, избегать утечек платформенных деталей в `commonMain`.

### Требования

- Функциональные:
  - Общий UI и бизнес-логика для Android, iOS, Desktop, Web.
  - Возможность платформенных адаптаций дизайна и поведения.
  - Интеграция с нативной навигацией и системными API.
- Нефункциональные:
  - Приемлемый размер бандла (особенно для Web).
  - Производительность близкая к нативной.
  - Поддерживаемость и тестируемость общего кода.

### Архитектура

- Общий модуль (`commonMain`): Composable-экраны, state management, навигация, общие use-case-ы.
- Платформенные модули (`androidMain`, `iosMain`, `desktopMain`, `webMain`): точки входа, адаптеры под платформенные API, ресурсы.
- Интеграция через абстракции и `expect`/`actual` только для инфраструктурных зависимостей.

## Answer (EN)

**Compose Multiplatform (CMP)** is a declarative UI framework by JetBrains that brings the `Jetpack Compose` approach to Android, iOS, Desktop (`JVM`), and Web (Canvas/DOM-based rendering, including via WASM). It uses `Kotlin Multiplatform` to share UI code and business logic across platforms.

**Key difference from KMM**:
- KMM → shares `domain`/`data` layer, native UI per platform
- CMP → unified UI framework + logic, one component set (with room for platform-specific adaptations)

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
      // example: tooling previews for Android
      implementation(compose.uiToolingPreview)
    }
  }
}
```

### Expect/Actual For Platform APIs

```kotlin
// ✅ commonMain
expect fun getPlatformName(): String

// ✅ androidMain
actual fun getPlatformName() = "Android"

// ✅ iosMain
actual fun getPlatformName() = "iOS"

// ❌ Avoid expect/actual for UI components directly;
//    instead, wrap platform-specific UI behind composable/wrapper abstractions.
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
- State holders (alternatives to `ViewModel`)
- Navigation logic
- Screens, components
- Theming

**Platform-specific**:
- Gesture handling (iOS swipe-back)
- Windowing (`Desktop`)
- Resources (via `expect`/`actual` and/or CMP resource APIs)
- Performance profiling per target

### Trade-offs

**iOS Integration**:
- `UIViewController` wrapper → overhead
- Limited `SwiftUI` interop
- Lifecycle mapping iOS ↔ Compose

**Web**:
- Canvas/DOM-based implementations → accessibility challenges
- `Bundle` size (minimum around a few MB)

**Desktop**:
- Windowing API differences (`macOS`/`Windows`/`Linux`)

### Short Version

- CMP extends the declarative `Jetpack Compose` approach across platforms via `Kotlin Multiplatform`.
- Shared: UI tree, state, navigation, theming.
- Platform-specific: system APIs, navigation integration, gestures, resources.
- Use when UI reuse and development speed matter more than deep native tailoring.

### Detailed Version

- Define what UI and logic must be shared across platforms.
- Design a common module with composable screens and business logic using KMP.
- For each platform implement entry points and adapters to native APIs.
- Clearly separate shared and platform-specific layers; avoid leaking platform details into `commonMain`.

### Requirements

- Functional:
  - Shared UI and business logic for Android, iOS, Desktop, Web.
  - Ability to apply platform-specific adaptations in design and behavior.
  - Integration with native navigation and system APIs.
- Non-functional:
  - Acceptable bundle size (especially for Web).
  - Near-native performance.
  - Maintainability and testability of shared code.

### Architecture

- Shared module (`commonMain`): composable screens, state management, navigation, shared use cases.
- Platform modules (`androidMain`, `iosMain`, `desktopMain`, `webMain`): entry points, adapters to platform APIs, resources.
- Integration via abstractions and `expect`/`actual` only for infrastructure-level dependencies.

---

## Дополнительные вопросы (RU)

- Как обрабатывать платформенно-специфичные паттерны навигации (например, iOS back swipe), не проталкивая детали в общий код?
- Каковы перформанс-эффекты обёртки через `UIViewController` на iOS по сравнению с нативным `SwiftUI`?
- Как структурировать `expect`/`actual` для файловой системы, haptics и secure storage API?
- В каких случаях стоит предпочесть нативный UI вместо CMP для отдельных экранов?
- Как минимизировать размер Web-бандла при сохранении общего UI-кода между платформами?

## Follow-ups

- How to handle platform-specific navigation patterns (iOS back swipe) without leaking into common code?
- What are performance implications of `UIViewController` wrapper on iOS vs native `SwiftUI`?
- How to structure `expect`/`actual` for filesystem, haptics, and secure storage APIs?
- When should you choose native UI over CMP for specific platform screens?
- How to minimize Web bundle size while sharing UI code across platforms?

## Ссылки (RU)

- [[c-jetpack-compose]]
- [Compose Multiplatform](https://www.jetbrains.com/lp/compose-multiplatform/)
- https://github.com/JetBrains/compose-multiplatform
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)

## References

- [[c-jetpack-compose]]
- [Compose Multiplatform](https://www.jetbrains.com/lp/compose-multiplatform/)
- https://github.com/JetBrains/compose-multiplatform
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)

## Связанные вопросы (RU)

### Предпосылки (проще)
- [[q-android-jetpack-overview--android--easy]]
- [[q-how-jetpack-compose-works--android--medium]]

### Связанные (тот же уровень)
- [[q-kmm-architecture--android--hard]]
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]

### Продвинуто (сложнее)
- [[q-compose-performance-optimization--android--hard]]

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
