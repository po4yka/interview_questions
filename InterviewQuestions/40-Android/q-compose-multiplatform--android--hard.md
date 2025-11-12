---
id: android-191
title: Compose Multiplatform / Compose Multiplatform
aliases: [Compose Multiplatform, KMP Compose]
topic: android
subtopics:
- compose-multiplatform
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
tags: [android/compose-multiplatform, android/ui-compose, compose, difficulty/hard, multiplatform]

---

# Вопрос (RU)
> Что такое Compose Multiplatform и как реализовать кроссплатформенную UI-архитектуру?

# Question (EN)
> What is Compose Multiplatform and how to implement cross-platform UI architecture?

---

## Ответ (RU)

**Compose Multiplatform (CMP)** — декларативный UI-фреймворк от JetBrains, реализующий тот же подход декларативного UI, что и `Jetpack Compose`, и расширяющий его на Android, iOS, Desktop (`JVM`) и Web (рендеринг поверх Canvas/DOM, включая варианты на WASM/JS). Он использует `Kotlin Multiplatform` для шаринга UI-кода и бизнес-логики между платформами.

**Основное отличие от классического KMM-подхода**:
- KMM → шаринг `domain`/`data` слоя, нативный UI на каждой платформе
- CMP → единый декларативный UI-фреймворк + логика, общий набор компонентов (с возможностью платформенных адаптаций и использования нативного UI там, где нужно)

Поддержка отдельных таргетов и компонентов может находиться в разных стадиях зрелости (stable/RC/experimental) — это важно учитывать при выборе архитектуры продакшн-проекта.

**Целевой use case**: проекты с высоким уровнем UI-переиспользования (внутренние инструменты, enterprise-приложения, MVP), где приоритет — скорость разработки и консистентный UX над глубокой платформенной кастомизацией.

### Project Structure

```kotlin
// shared/build.gradle.kts (упрощённый пример)
kotlin {
  androidTarget()
  jvm("desktop")
  iosX64(); iosArm64(); iosSimulatorArm64()
  // при использовании Web:
  // wasmJs("wasm") // или js(...) в зависимости от выбранного стека

  sourceSets {
    commonMain.dependencies {
      implementation(compose.runtime)
      implementation(compose.foundation)
      // material/material3 доступны для основных таргетов CMP;
      // проверять совместимость с конкретной версией и таргетами.
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

// ❌ Избегать expect/actual для конкретных UI-компонентов;
//    вместо этого инкапсулировать платформенно-специфичный UI за абстракциями/
//    обёртками и вызывать их из общего кода.
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
- State holders (альтернативы `ViewModel` или обёртки над ним)
- Навигационная логика (абстрагированная от конкретных контроллеров)
- Экраны и UI-компоненты
- Темизация и дизайн-система

**Platform-specific**:
- Жесты и навигационные паттерны (например, iOS swipe-back)
- Окна и windowing (`Desktop`)
- Ресурсы (через `expect`/`actual` и/или предоставленные CMP API для ресурсов)
- Интеграция с системными API (камера, push, deeplink-и и др.)
- Performance-профилирование и тюнинг под каждый таргет

### Trade-offs

**iOS Integration**:
- Использование `UIViewController`/`UIResponder`-обёрток → накладные расходы и дополнительные уровни интеграции
- Ограниченная и эволюционирующая interop с `SwiftUI` и нативной навигацией
- Необходимость аккуратного маппинга жизненных циклов iOS ↔ Compose

**Web**:
- Canvas/DOM/WASM-реализации → потенциальные сложности с accessibility и SEO
- Размер бандла: типично несколько MB и выше (зависит от таргета, минификации и набора зависимостей)

**Desktop**:
- Отличия Windowing API (`macOS`/`Windows`/`Linux`)
- Особенности интеграции с нативными возможностями ОС (меню, системный трэй, shortcuts)

## Краткая Версия
- CMP реализует многоплатформенный вариант декларативного подхода `Compose` поверх `Kotlin Multiplatform`.
- Общий код: UI-дерево, состояние, навигация, тема, общая бизнес-логика.
- Платформенный код: интеграция с системными API, нативная навигация, жесты, ресурсы, точка входа.
- Использовать там, где важны переиспользование UI, единая дизайн-система и скорость разработки; при необходимости допускается смешанный подход с нативным UI для отдельных экранов.

## Подробная Версия
- Явно описать, какие части UI и логики должны быть общими.
- Спроектировать общий модуль с Composable-экранами и бизнес-логикой на KMP.
- Для каждой платформы реализовать точку входа и обёртки над системными API (навигация, insets, permissions и т.п.).
- Ясно разделить общий и платформенный слои, избегать утечек платформенных деталей в `commonMain`.
- Учитывать зрелость поддержки целевых таргетов (особенно iOS/Web) при принятии архитектурных решений.

### Требования

- Функциональные:
  - Общий UI и бизнес-логика для Android, iOS, Desktop, Web.
  - Возможность платформенных адаптаций дизайна и поведения.
  - Интеграция с нативной навигацией и системными API.
- Нефункциональные:
  - Приемлемый размер бандла (особенно для Web).
  - Производительность, приемлемая или близкая к нативной для ключевых сценариев.
  - Поддерживаемость и тестируемость общего кода.

### Архитектура

- Общий модуль (`commonMain`): Composable-экраны, state management, навигация, общие use-case-ы.
- Платформенные модули (`androidMain`, `iosMain`, `desktopMain`, `webMain`): точки входа, адаптеры под платформенные API, ресурсы.
- Интеграция через абстракции и `expect`/`actual` только для инфраструктурных зависимостей (filesystem, haptics, secure storage, network, prefs и т.п.).

## Answer (EN)

**Compose Multiplatform (CMP)** is a declarative UI framework by JetBrains that implements the same declarative Compose model and brings it to Android, iOS, Desktop (`JVM`), and Web (Canvas/DOM-based rendering, including WASM/JS options). It uses `Kotlin Multiplatform` to share UI code and business logic across platforms.

**Key difference from the classic KMM approach**:
- KMM → shares `domain`/`data` layer, native UI per platform
- CMP → unified declarative UI framework + logic, one component set (with room for platform-specific adaptations and using native UI where appropriate)

Support level for individual targets and components ranges from stable to experimental; this must be considered when designing production architecture.

**Target use case**: projects with high UI reusability (internal tools, enterprise apps, MVPs), where development speed and consistent UX are more important than deep native tailoring.

### Project Structure

```kotlin
// shared/build.gradle.kts (simplified example)
kotlin {
  androidTarget()
  jvm("desktop")
  iosX64(); iosArm64(); iosSimulatorArm64()
  // when using Web:
  // wasmJs("wasm") // or js(...) depending on chosen stack

  sourceSets {
    commonMain.dependencies {
      implementation(compose.runtime)
      implementation(compose.foundation)
      // material/material3 are available for major CMP targets;
      // verify compatibility with your specific version and targets.
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

// ❌ Avoid using expect/actual for concrete UI components directly;
//    instead, hide platform-specific UI behind composable/wrapper abstractions
//    and invoke them from shared code.
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
- State holders (alternatives to `ViewModel` or wrappers around it)
- Navigation logic (abstracted away from concrete controllers)
- Screens and UI components
- Theming and design system

**Platform-specific**:
- Gesture handling and navigation patterns (e.g., iOS back swipe)
- Windowing (`Desktop`)
- Resources (via `expect`/`actual` and/or CMP resource APIs)
- Integration with system APIs (camera, push, deeplinks, etc.)
- Performance profiling and tuning per target

### Trade-offs

**iOS Integration**:
- Using `UIViewController`/`UIResponder`-based wrappers → overhead and integration complexity
- Limited and evolving interop with `SwiftUI` and native navigation
- Careful lifecycle mapping required between iOS and Compose

**Web**:
- Canvas/DOM/WASM-based implementations → potential challenges with accessibility and SEO
- Bundle size: typically a few megabytes or more (depends on target, optimizations, and dependencies)

**Desktop**:
- Differences in windowing APIs across `macOS`/`Windows`/`Linux`
- Considerations for integrating with OS-native features (menus, system tray, shortcuts)

## Short Version
- CMP is the multiplatform implementation of the declarative `Compose` approach built on `Kotlin Multiplatform`.
- Shared: UI tree, state, navigation, theming, shared business logic.
- Platform-specific: system integrations, native navigation, gestures, resources, entry points.
- Use where UI reuse, unified design system, and development speed are priorities; combine with native UI for selected screens when needed.

## Detailed Version
- Explicitly define which parts of UI and logic must be shared.
- Design a common module with composable screens and business logic using KMP.
- For each platform, implement entry points and adapters to platform APIs (navigation, insets, permissions, etc.).
- Keep shared and platform-specific layers clearly separated; avoid leaking platform details into `commonMain`.
- Consider the maturity level of target support (especially iOS/Web) when making architectural decisions.

### Requirements

- Functional:
  - Shared UI and business logic for Android, iOS, Desktop, Web.
  - Ability to apply platform-specific adaptations in design and behavior.
  - Integration with native navigation and system APIs.
- Non-functional:
  - Acceptable bundle size (especially for Web).
  - Performance close enough to native for critical flows.
  - Maintainability and testability of shared code.

### Architecture

- Shared module (`commonMain`): composable screens, state management, navigation, shared use cases.
- Platform modules (`androidMain`, `iosMain`, `desktopMain`, `webMain`): entry points, adapters to platform APIs, resources.
- Integration via abstractions and `expect`/`actual` only for infrastructure-level dependencies (filesystem, haptics, secure storage, network, preferences, etc.).

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
