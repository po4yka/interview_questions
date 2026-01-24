---
id: android-616
title: Jetpack Window Manager for Foldables / Jetpack Window Manager для складных
  устройств
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
- en
- ru
status: draft
moc: moc-android
related:
- c-android
- q-adaptive-layouts-compose--kotlin--hard
- q-how-does-jetpackcompose-work--android--medium
- q-how-jetpack-compose-works--android--medium
- q-jetpack-compose-basics--android--medium
created: 2025-11-02
updated: 2025-11-10
tags:
- android/foldables-chromeos
- android/ui-compose
- android/ui-state
- difficulty/hard
anki_cards:
- slug: android-616-0-en
  language: en
  anki_id: 1768396750103
  synced_at: '2026-01-23T16:45:05.923278'
- slug: android-616-0-ru
  language: ru
  anki_id: 1768396750127
  synced_at: '2026-01-23T16:45:05.924688'
sources:
- url: https://developer.android.com/jetpack/androidx/releases/window
  note: Jetpack Window Manager documentation
- url: https://developer.android.com/guide/topics/large-screens/ideas
  note: Adaptive layout patterns
---
# Вопрос (RU)
> Как адаптировать Android-приложение под планшеты и складные устройства с помощью Jetpack `Window` Manager: обрабатывать WindowSizeClass, posture, hinge и настраивать Compose/Views под разные состояния?

# Question (EN)
> How do you adapt an Android app for tablets and foldables using Jetpack `Window` Manager, handling WindowSizeClass, posture, and hinge data to customize Compose/`View` layouts across states?

---

## Ответ (RU)

## Краткая Версия
- Используйте `calculateWindowSizeClass(activity)` из `material3-window-size-class` в `Activity` для определения compact/medium/expanded и пробрасывайте в UI.
- Применяйте Jetpack `Window` Manager (`androidx.window`) для чтения `WindowLayoutInfo` и `FoldingFeature` (posture, hinge, `isSeparating`, `bounds`).
- Для `View`-интерфейсов используйте `ActivityEmbedding` (`androidx.window.embedding`) и правила split-view.
- В Compose применяйте адаптивные скэффолды (`NavigationSuiteScaffold`, list-detail), учитывая шарнир и системные insets.
- Тестируйте на эмуляторах складных устройств, эмулируйте posture/hinge через тестовые утилиты и оптимизируйте recomposition при изменении размера и posture.

## Подробная Версия
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

- Использовать слой адаптера window/layout-информации (обертка над Jetpack `Window` Manager), который поставляет UI состояние: `WindowSizeClass`, наличие/тип `FoldingFeature`, разделяющий ли шарнир, безопасные зоны.
- На уровне презентации (Compose/Views) подписываться на это состояние и выбирать соответствующую компоновку (одна панель, две панели, три панели).
- Инкапсулировать правила разметки и реагирование на posture в одном месте, чтобы избежать дублирования и обеспечить тестируемость.

#### 1. Получение WindowMetrics И SizeClass

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

- Рассчитывайте `WindowSizeClass` через `calculateWindowSizeClass(activity)` (из `androidx.compose.material3.windowsizeclass`) в `Activity` и передавайте его в корневой composable.
- Используйте Jetpack `Window` Manager (`androidx.window`) для получения `WindowMetrics`, если нужен более низкоуровневый контроль.
- Сохраняйте класс размера в `ViewModel` или локальном состоянии (`remember`) на уровне навигационного хоста для переиспользования.

#### 2. Posture И FoldingFeature

```kotlin
val windowInfoTracker = WindowInfoTracker.getOrCreate(context)
val layoutInfoFlow = windowInfoTracker.windowLayoutInfo(activity)

lifecycleScope.launch {
    lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
        layoutInfoFlow.collect { info ->
            val foldingFeature = info.displayFeatures
                .filterIsInstance<FoldingFeature>()
                .firstOrNull()

            when (foldingFeature?.state) {
                FoldingFeature.State.FLAT -> renderFlat()
                FoldingFeature.State.HALF_OPENED -> renderFolded()
                null -> renderFlat() // нет FoldingFeature — обычное "плоское" устройство или отсутствие шарнира
            }
        }
    }
}
```

- `FoldingFeature.orientation` (HORIZONTAL/VERTICAL) используется, чтобы определить безопасные зоны (safe areas) и расположение панелей.
- `isSeparating` указывает, делит ли шарнир (hinge) экран на логически независимые области.
- Для расчета области шарнира используйте `foldingFeature.bounds`; не путайте её с display cutout.
- Отсутствие `FoldingFeature` трактуется как обычное устройство без шарнира (flat, цельный экран).

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
- Работает поверх Jetpack `Window` Manager (`androidx.window.embedding`).
- Пример носит схемный характер: в реальном коде необходимо настроить пары `Activity`, пороги размеров, split ratio, ориентацию/направление раскладки и учитывать актуальную версию `Window` API (XML-правила или программная конфигурация).

#### 4. Compose Адаптация

- Используйте `NavigationSuiteScaffold` (Material 3) для адаптивной навигации (bottom bar / navigation rail / navigation drawer в зависимости от `WindowSizeClass`).
- Используйте адаптивные двухпанельные компоненты: `ListDetailPaneScaffold` и аналогичные из актуальных adaptive-библиотек (`material3-adaptive`), либо их эквиваленты (Accompanist/legacy — с осознанием статуса библиотек).
- Для учета области шарнира используйте `FoldingFeature.bounds` и `isSeparating` из Jetpack `Window` Manager; системные insets (`WindowInsets` / `WindowInsetsCompat`, включая `displayCutout`) учитывайте отдельно для вырезов и системных жестов.

#### 5. Тестирование

- Используйте эмуляторы с профилями складных устройств (Pixel Fold, `Surface` Duo и др.) и меняйте posture/fold state.
- Для UI-тестов Jetpack `Window` Manager применяйте `WindowLayoutInfoPublisherRule` из тестового артефакта, чтобы эмулировать разные `FoldingFeature` конфигурации.
- Делайте snapshot/скриншот-тесты для разных `WindowSizeClass` и состояний posture.

#### 6. Производительность

- Избегайте тяжелых перерасчетов и крупных recomposition при изменении posture/size: выносите вычисления за пределы composable, кэшируйте с помощью `remember`/`derivedStateOf`.
- Используйте `rememberSaveable` для хранения состояния панелей (например, выбранный элемент списка), чтобы оно переживало изменение конфигурации и ориентации.
- На ChromeOS и больших экранах проверяйте поведение в режиме multi-window и при изменении размеров окна (activity должна быть resizable).

---

## Answer (EN)

## Short Version
- Use `calculateWindowSizeClass(activity)` from `material3-window-size-class` in the `Activity` to decide between compact/medium/expanded layouts and pass it down.
- Use Jetpack `Window` Manager (`androidx.window`) to read `WindowLayoutInfo` and `FoldingFeature` (posture, hinge, `isSeparating`, `bounds`).
- For `View`-based UIs, configure `ActivityEmbedding` (`androidx.window.embedding`) split rules.
- In Compose, use adaptive scaffolds (`NavigationSuiteScaffold`, list-detail patterns) and honor hinge plus regular insets.
- Test on foldable/large-screen profiles, simulate posture/hinge in tests, and optimize recomposition when posture/size changes.

## Detailed Version
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

- Use a window/layout info adapter layer (wrapper around Jetpack `Window` Manager) that exposes UI state: `WindowSizeClass`, `FoldingFeature` presence/type, whether hinge is separating, safe areas.
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

- Compute `WindowSizeClass` per activity using `calculateWindowSizeClass(activity)` (from `androidx.compose.material3.windowsizeclass`) in the `Activity` and pass it to the root composable.
- Use Jetpack `Window` Manager (`androidx.window`) to obtain `WindowMetrics` when lower-level control is needed.
- Keep the size class in a `ViewModel` or local state (`remember`) at the navigation host level for reuse.

#### 2. Posture and FoldingFeature

```kotlin
val windowInfoTracker = WindowInfoTracker.getOrCreate(context)
val layoutInfoFlow = windowInfoTracker.windowLayoutInfo(activity)

lifecycleScope.launch {
    lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
        layoutInfoFlow.collect { info ->
            val foldingFeature = info.displayFeatures
                .filterIsInstance<FoldingFeature>()
                .firstOrNull()

            when (foldingFeature?.state) {
                FoldingFeature.State.FLAT -> renderFlat()
                FoldingFeature.State.HALF_OPENED -> renderFolded()
                null -> renderFlat() // no FoldingFeature = regular flat device or no hinge
            }
        }
    }
}
```

- Use `FoldingFeature.orientation` (HORIZONTAL/VERTICAL) to derive safe areas and pane placement.
- `isSeparating` indicates whether the hinge splits the screen into logically independent regions.
- Use `foldingFeature.bounds` for the hinge area; do not confuse it with display cutouts.
- If there is no `FoldingFeature`, treat the device as a regular flat screen without a hinge.

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
- Built on top of Jetpack `Window` Manager (`androidx.window.embedding`).
- Example is schematic: in real code you configure activity pairs, size thresholds, split ratio, layout direction, and align with the current Window/Embedding API (XML rules or programmatic).

#### 4. Compose Adaptation

- Use `NavigationSuiteScaffold` (Material 3) for adaptive navigation (bottom bar / navigation rail / navigation drawer based on `WindowSizeClass`).
- Use adaptive dual-pane components such as `ListDetailPaneScaffold` and related layouts from current adaptive libraries (`material3-adaptive`), or their equivalents (including Accompanist where appropriate, noting library status).
- Respect hinge area via `FoldingFeature.bounds` and `isSeparating`; handle system insets (`WindowInsets` / `WindowInsetsCompat`, including `displayCutout`) separately for cutouts/gestures.

#### 5. Testing

- Use emulator profiles for foldables (e.g., Pixel Fold, `Surface` Duo) and vary posture/fold state.
- For UI tests with Jetpack `Window` Manager, use `WindowLayoutInfoPublisherRule` from the test artifact to emulate different `FoldingFeature` configurations.
- Perform screenshot/snapshot tests across `WindowSizeClass` values and postures.

#### 6. Performance

- Avoid heavy recomposition and expensive work on every posture/size change: move computations outside composables and cache with `remember`/`derivedStateOf`.
- Use `rememberSaveable` to preserve pane state (e.g., selected item) across configuration and orientation changes.
- On ChromeOS and large screens, verify behavior in multi-window and resizable modes.

---

## Дополнительные Вопросы (RU)
- Как реализовать drag-and-drop между pane в режиме Expanded?
- Какие UX-анти-паттерны существуют для foldables (например, элементы под шарниром)?
- Как совместить ActivityEmbedding и Navigation `Component` в многопанельном приложении?

## Follow-ups (EN)
- How to implement drag-and-drop between panes in Expanded mode?
- What UX anti-patterns exist for foldables (e.g., placing elements under the hinge)?
- How to combine ActivityEmbedding and Navigation `Component` in a multi-pane app?

## Ссылки (RU)
- [[c-android-components]]
- [[c-android-view-system]]

## References
- https://developer.android.com/jetpack/androidx/releases/window
- https://developer.android.com/guide/topics/large-screens/ideas

## Связанные Вопросы (RU)
- [[q-adaptive-layouts-compose--kotlin--hard]]

## Related Questions
- [[q-adaptive-layouts-compose--kotlin--hard]]
