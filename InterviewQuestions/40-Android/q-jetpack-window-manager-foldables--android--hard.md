---
id: android-616
title: Jetpack Window Manager for Foldables / Jetpack Window Manager для складных устройств
aliases:
- Jetpack Window Manager Foldables
- Jetpack Window Manager для складных устройств
topic: android
subtopics:
- foldables-chromeos
- ui-compose
- ui-state
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- q-adaptive-layouts-compose--kotlin--hard
created: 2025-11-02
updated: 2025-11-10
tags:
- android/foldables-chromeos
- android/ui-compose
- android/ui-state
- difficulty/hard
sources:
- url: "https://developer.android.com/jetpack/androidx/releases/window"
  note: Jetpack Window Manager documentation
- url: "https://developer.android.com/guide/topics/large-screens/ideas"
  note: Adaptive layout patterns

---

# Вопрос (RU)
> Как адаптировать Android-приложение под планшеты и складные устройства с помощью Jetpack Window Manager: обрабатывать WindowSizeClass, posture, hinge и настраивать Compose/Views под разные состояния?

# Question (EN)
> How do you adapt an Android app for tablets and foldables using Jetpack Window Manager, handling WindowSizeClass, posture, and hinge data to customize Compose/`View` layouts across states?

---

## Ответ (RU)

### Краткая версия

- Используйте `calculateWindowSizeClass(activity)` для определения компактных/средних/расширенных раскладок.
- Применяйте Jetpack Window Manager (`androidx.window`) для чтения `WindowLayoutInfo` и `FoldingFeature` (posture, hinge, `isSeparating`, `bounds`).
- Для `View`-интерфейсов используйте `Activity` Embedding (`androidx.window.embedding`) и правила split-view.
- В Compose применяйте адаптивные скэффолды (`NavigationSuiteScaffold`, list-detail), учитывая шарнир и системные Insets.
- Тестируйте на эмуляторах складных устройств и оптимизируйте recomposition при изменении размера и posture.

### Подробная версия

#### Требования

- Функциональные:
  - Корректная адаптация UI под планшеты, большие экраны и складные устройства.
  - Поддержка разных состояний окна: compact/medium/expanded.
  - Реакция на posture и `FoldingFeature` (FLAT, HALF_OPENED), шарнир и разделение на панели.
  - Поддержка одно- и двухпанельных раскладок (master-detail, list-detail, multi-pane).
- Нефункциональные:
  - Отсутствие элементов под шарниром и в неинтерактивных зонах.
  - Производительность при частых изменениях размеров/положения окна.
  - Корректная работа в multi-window и на ChromeOS.

#### Архитектура

- Использовать слой адаптера window/layout-информации (обертка над Jetpack Window Manager), который поставляет UI состояние: `WindowSizeClass`, наличие/тип `FoldingFeature`, разделяющий ли шарнир, безопасные зоны.
- На уровне презентации (Compose/Views) подписываться на это состояние и выбирать соответствующую компоновку (одна панель, две панели, три панели).
- Инкапсулировать правила разметки и реагирование на posture в одном месте, чтобы избежать дублирования и обеспечить тестируемость.

#### 1. Получение WindowMetrics и SizeClass

```kotlin
@OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
@Composable
fun AdaptiveApp(windowSizeClass: WindowSizeClass) {
    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> CompactLayout()
        WindowWidthSizeClass.Medium -> ListDetailSplit()
        WindowWidthSizeClass.Expanded -> ThreePaneLayout()
    }
}
```

- Рассчитывайте `WindowSizeClass` через `calculateWindowSizeClass(activity)` (Material 3 / large-screen guidance).
- Используйте Jetpack Window Manager (`androidx.window`) для получения `WindowMetrics`, если нужен более низкоуровневый контроль.
- Сохраняйте класс размера в `ViewModel` или `remember` state.

#### 2. Posture и FoldingFeature

```kotlin
val windowInfoTracker = WindowInfoTracker.getOrCreate(context)
val layoutInfoFlow = windowInfoTracker.windowLayoutInfo(activity)

layoutInfoFlow.collect { info ->
    val foldingFeature = info.displayFeatures
        .filterIsInstance<FoldingFeature>()
        .firstOrNull()

    when (foldingFeature?.state) {
        FoldingFeature.State.FLAT -> renderFlat()
        FoldingFeature.State.HALF_OPENED -> renderFolded()
        null -> renderFlat()
    }
}
```

- `FoldingFeature.orientation` (HORIZONTAL/VERTICAL) используется, чтобы определить безопасные зоны (safe areas) и расположение панелей.
- `isSeparating` указывает, делит ли шарнир (hinge) экран на логически независимые области.
- Для расчета области шарнира используйте `foldingFeature.bounds`; не путайте её с display cutout.

#### 3. ActivityEmbedding (Views)

```kotlin
RuleController.getInstance(context).setRules(
    setOf(
        SplitPairRule.Builder(/* primaryActivityClass */, /* secondaryActivityClass */)
            .setMinWidthDp(600)
            .setFinishPrimaryWithSecondary(SplitRule.FinishBehavior.ALWAYS)
            .build()
    )
)
```

- Позволяет запускать master-detail / list-detail в двух панелях для планшетов и складных устройств.
- Работает поверх Jetpack Window Manager (`androidx.window.embedding`).
- Пример носит схемный характер: в реальном коде необходимо настроить пары `Activity` и другие параметры (split ratio, layout direction и т.п.).

#### 4. Compose адаптация

- Используйте `NavigationSuiteScaffold` (Material 3) для адаптивной навигации (bottom bar / navigation rail / navigation drawer в зависимости от `WindowSizeClass`).
- Используйте паттерн `ListDetailPaneScaffold` (Accompanist Adaptive) или аналогичную двухпанельную компоновку.
- Для учета области шарнира используйте `FoldingFeature.bounds` и `isSeparating` из Jetpack Window Manager; системные insets (`WindowInsets` / `WindowInsetsCompat`, включая `displayCutout`) учитывайте отдельно для вырезов и системных жестов.

#### 5. Тестирование

- Используйте эмуляторы с профилями складных устройств (Pixel Fold, Surface Duo и др.) и меняйте posture/fold state.
- Для UI-тестов Jetpack Window Manager применяйте `WindowLayoutInfoPublisherRule` из тестового артефакта, чтобы эмулировать разные `FoldingFeature` конфигурации.
- Делайте snapshot/скриншот-тесты для разных `WindowSizeClass` и состояний posture.

#### 6. Производительность

- Избегайте тяжелых перерасчетов и крупных recomposition при изменении posture/size: выносите вычисления за пределы composable, кэшируйте с помощью `remember`/`derivedStateOf`.
- Используйте `rememberSaveable` для хранения состояния панелей (например, выбранный элемент списка), чтобы оно переживало изменение конфигурации и ориентации.
- На ChromeOS и больших экранах проверяйте поведение в режиме multi-window и при изменении размеров окна (activity должна быть resizable).

---

## Answer (EN)

### Short Version

- Use `calculateWindowSizeClass(activity)` to decide between compact/medium/expanded layouts.
- Use Jetpack Window Manager (`androidx.window`) to read `WindowLayoutInfo` and `FoldingFeature` (posture, hinge, `isSeparating`, `bounds`).
- For `View`-based UIs, configure `Activity` Embedding (`androidx.window.embedding`) split rules.
- In Compose, use adaptive scaffolds (`NavigationSuiteScaffold`, list-detail patterns) and honor hinge plus regular insets.
- Test on foldable/large-screen profiles and optimize recomposition when posture/size changes.

### Detailed Version

#### Requirements

- Functional:
  - Properly adapt UI for tablets, large screens, and foldable devices.
  - Support different window states: compact/medium/expanded.
  - React to posture and `FoldingFeature` (FLAT, HALF_OPENED), hinge, and separating panes.
  - Support single-, dual-, and multi-pane layouts (master-detail, list-detail, multi-pane).
- Non-functional:
  - Avoid placing critical UI under the hinge or in non-interactive areas.
  - Maintain performance under frequent resize/posture changes.
  - Behave correctly in multi-window and on ChromeOS.

#### Architecture

- Use a window/layout info adapter layer (wrapper around Jetpack Window Manager) that exposes UI state: `WindowSizeClass`, `FoldingFeature` presence/type, whether hinge is separating, safe areas.
- In the presentation layer (Compose/Views), observe this state and switch between appropriate layouts (single, two-pane, three-pane).
- Centralize layout rules and posture handling to avoid duplication and enable testing.

#### 1. WindowMetrics and SizeClass

```kotlin
@OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
@Composable
fun AdaptiveApp(windowSizeClass: WindowSizeClass) {
    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> CompactLayout()
        WindowWidthSizeClass.Medium -> ListDetailSplit()
        WindowWidthSizeClass.Expanded -> ThreePaneLayout()
    }
}
```

- Compute `WindowSizeClass` per activity using `calculateWindowSizeClass(activity)` (Material 3 / large-screen guidance).
- Use Jetpack Window Manager (`androidx.window`) to obtain `WindowMetrics` when lower-level control is needed.
- Store the size class in a `ViewModel` or `remember` state.

#### 2. Posture and FoldingFeature

```kotlin
val windowInfoTracker = WindowInfoTracker.getOrCreate(context)
val layoutInfoFlow = windowInfoTracker.windowLayoutInfo(activity)

layoutInfoFlow.collect { info ->
    val foldingFeature = info.displayFeatures
        .filterIsInstance<FoldingFeature>()
        .firstOrNull()

    when (foldingFeature?.state) {
        FoldingFeature.State.FLAT -> renderFlat()
        FoldingFeature.State.HALF_OPENED -> renderFolded()
        null -> renderFlat()
    }
}
```

- Use `FoldingFeature.orientation` (HORIZONTAL/VERTICAL) to derive safe areas and pane placement.
- `isSeparating` indicates whether the hinge splits the screen into logically independent regions.
- Use `foldingFeature.bounds` for hinge area; do not confuse it with display cutouts.

#### 3. ActivityEmbedding (Views)

```kotlin
RuleController.getInstance(context).setRules(
    setOf(
        SplitPairRule.Builder(/* primaryActivityClass */, /* secondaryActivityClass */)
            .setMinWidthDp(600)
            .setFinishPrimaryWithSecondary(SplitRule.FinishBehavior.ALWAYS)
            .build()
    )
)
```

- Enables master-detail / list-detail two-pane layouts for tablets and foldables.
- Built on top of Jetpack Window Manager (`androidx.window.embedding`).
- Example is schematic: real code configures activity pairs and attributes (split ratio, layout direction, etc.).

#### 4. Compose Adaptation

- Use `NavigationSuiteScaffold` (Material 3) for adaptive navigation (bottom bar / navigation rail / navigation drawer based on `WindowSizeClass`).
- Use `ListDetailPaneScaffold` (Accompanist Adaptive) or similar dual-pane patterns.
- Respect hinge area via `FoldingFeature.bounds` and `isSeparating`; handle system insets (`WindowInsets` / `WindowInsetsCompat`, including `displayCutout`) separately.

#### 5. Testing

- Use emulator profiles for foldables (e.g., Pixel Fold, Surface Duo) and vary posture/fold state.
- For UI tests, use `WindowLayoutInfoPublisherRule` from the Jetpack Window Manager test artifact to emulate different `FoldingFeature` configurations.
- Perform screenshot/snapshot tests across `WindowSizeClass` values and postures.

#### 6. Performance

- Avoid heavy recomposition and expensive work on every posture/size change: move logic outside composables and cache with `remember`/`derivedStateOf`.
- Use `rememberSaveable` to preserve pane state (e.g., selected item) across configuration and orientation changes.
- On ChromeOS and large screens, verify behavior in multi-window and resizable modes.

---

## Дополнительные вопросы (RU)
- Как реализовать drag-and-drop между pane в режиме Expanded?
- Какие UX-анти-паттерны существуют для foldables (например, элементы под шарниром)?
- Как совместить ActivityEmbedding и Navigation Component в многопанельном приложении?

## Follow-ups (EN)
- How to implement drag-and-drop between panes in Expanded mode?
- What UX anti-patterns exist for foldables (e.g., placing elements under the hinge)?
- How to combine ActivityEmbedding and Navigation Component in a multi-pane app?

## Ссылки (RU)
- [[c-android-components]]
- [[c-android-view-system]]

## References
- https://developer.android.com/jetpack/androidx/releases/window
- https://developer.android.com/guide/topics/large-screens/ideas

## Связанные вопросы (RU)
- [[q-adaptive-layouts-compose--kotlin--hard]]

## Related Questions
- [[q-adaptive-layouts-compose--kotlin--hard]]
