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
status: reviewed
moc: moc-android
related:
- q-compose-compiler-plugin--jetpack-compose--hard
- q-compose-custom-layout--jetpack-compose--hard
- q-compose-lazy-layout-optimization--jetpack-compose--hard
created: 2025-10-15
updated: 2025-10-20
tags:
- android/ui-compose
- compose/multiplatform
- kmp
- difficulty/hard
---# Вопрос (RU)
> Что такое Compose Multiplatform, чем он отличается от KMM, как строить общий UI с платформенными адаптациями (Android, iOS, Desktop, Web)? Каковы ключевые ограничения и лучшие практики?

---

# Question (EN)
> What is Compose Multiplatform, how is it different from KMM, and how do you structure shared UI with platform adaptations (Android, iOS, Desktop, Web)? What are key limitations and best practices?

## Ответ (RU)

### Определение и охват
- Compose Multiplatform (CMP) переносит Compose UI на Android, iOS, Desktop, Web через KMP.
- Делим UI, состояние, навигацию, темы; точки входа и interop остаются платформенными.

### CMP vs KMM
- KMM: шарим домен/данные; UI нативный (Android Compose, iOS SwiftUI).
- CMP: шарим UI + домен; один UI‑фреймворк, платформенные адаптации тонким слоем.

### Структура проекта (минимум)
- Модули: `shared` (commonMain + платформенные), приложения: android/ios/desktop/js.
- Таргеты: `androidTarget()`, `ios*()`, `jvm("desktop")`, `js(IR)`.

Минимальная настройка Gradle (без версий):
```kotlin
plugins { kotlin("multiplatform"); id("org.jetbrains.compose"); id("com.android.library") }

kotlin {
  androidTarget(); jvm("desktop"); js(IR) { browser() }
  listOf(iosX64(), iosArm64(), iosSimulatorArm64())
  sourceSets { val commonMain by getting; val androidMain by getting; val iosMain by creating { dependsOn(commonMain) } }
}
```

### Общий UI + платформенные адаптации
- Шарим composable/экраны/навигацию/темы в `commonMain`.
- `expect/actual` для платформенных API (лог, ресурсы, размер окна, haptics).

Минимальный expect/actual:
```kotlin
// commonMain
expect fun platformName(): String
// androidMain
actual fun platformName() = "Android"
```

Точки входа (общий App + обёртка):
```kotlin
@Composable fun App() { /* Навигация + экраны */ }
// Android
class MainActivity: ComponentActivity() { override fun onCreate(b: Bundle?) { super.onCreate(b); setContent { App() } } }
```

### Адаптивные интерфейсы
- Классы окна (compact/medium/expanded) и разветвление UI.
- Избегайте глубоких деревьев; учитывайте desktop/web особенности.

### Лучшие практики
- Делите: state, экраны, темы, навигацию; interop держите тонким.
- Адаптируйте: жесты, окна, типографику, отступы под платформу.
- Производительность: стабильные ключи, `remember`, профилирование на каждой платформе.
- Ресурсы: compose resources, централизованные строки.
- Тесты: скриншоты/«golden» на всех таргетах; навигация и состояние.

### Ограничения
- iOS: обёртка UIViewController; ограниченная interop со SwiftUI.
- Web: Canvas, размер бандла, доступность.
- Desktop: окна/ввод, сочетания клавиш, hover‑паттерны.

---

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

