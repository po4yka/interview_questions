---
id: 20251015-100154
title: Compose Multiplatform / Compose Multiplatform (обзор)
aliases:
- Compose Multiplatform
- Compose Multiplatform overview
topic: android
subtopics:
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
- q-compose-compiler-plugin--android--hard
- q-compose-custom-layout--android--hard
- q-compose-lazy-layout-optimization--android--hard
created: 2025-10-15
updated: 2025-10-20
tags:
- android/ui-compose
- difficulty/hard
---

# Вопрос (RU)
> Compose Multiplatform (обзор)?

# Question (EN)
> Compose Multiplatform?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Definition and scope
- Compose Multiplatform (CMP) brings Compose UI to multiple targets with Kotlin Multiplatform (KMP): Android, iOS, Desktop, Web.
- You share UI, state, navigation, theming; platform entry points and interop remain platform‑specific.

### CMP vs KMM
- KMM: share domain/data; UI is native per platform (Android Compose, iOS SwiftUI).
- CMP: share UI + domain; one UI framework across targets, with platform shims when needed.

### Project structure (minimal)
- Modules: `shared` (commonMain + platform source sets), platform apps (androidApp, iosApp, desktopApp, jsApp).
- Targets: `androidTarget()`, `ios*()`, `jvm("desktop")`, `js(IR)`.

Minimal Gradle setup (no versions):
```kotlin
// shared/build.gradle.kts
plugins {
  kotlin("multiplatform")
  id("org.jetbrains.compose")
  id("com.android.library")
}

kotlin {
  androidTarget(); jvm("desktop"); js(IR) { browser() }
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

### Shared UI + platform adaptations
- Share composables/screens/navigation/theme in `commonMain`.
- Use `expect/actual` for platform APIs (logging, resources, window size, haptics).

Minimal expect/actual:
```kotlin
// commonMain
expect fun platformName(): String

// androidMain
actual fun platformName() = "Android"
```

Entry points (shared App + platform wrapper):
```kotlin
// commonMain
@Composable fun App() { /* Navigation + Screens */ }

// androidApp
class MainActivity: ComponentActivity() {
  override fun onCreate(b: Bundle?) { super.onCreate(b); setContent { App() } }
}
```

### Responsive layouts
- Derive window classes (compact/medium/expanded) and branch UI.
- Keep measurement simple; avoid deep trees in shared UI for desktop/web.

### Best practices
- Share: state holders, screens, theming, navigation; keep interop thin.
- Adapt: gestures, windowing, typography, spacing per platform.
- Performance: stable keys in lists, precompute with `remember`, profile on each target.
- Resources: use compose resources where possible; centralize strings.
- Testing: golden/screenshot across targets; exercise navigation and state.

### Limitations (today)
- iOS embedding via UIViewController wrapper; SwiftUI interop limited.
- Web is canvas‑based; bundle size and accessibility require care.
- Desktop windowing/inputs differ; shortcut/hover patterns diverge.

## Follow-ups
- How to structure expect/actual for filesystem, haptics, and secure storage?
- Strategies to keep bundle size small on Web while sharing UI?
- Approaches to platform navigation parity without leaking internals into common code?

## References
- https://www.jetbrains.com/lp/compose-multiplatform/
- https://developer.android.com/develop/ui/compose
- [[c-coroutines]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-lazy-layout-optimization--android--hard]]

### Advanced (Harder)
- [[q-compose-modifier-order-performance--android--medium]]
- [[q-compose-gesture-detection--android--medium]]
