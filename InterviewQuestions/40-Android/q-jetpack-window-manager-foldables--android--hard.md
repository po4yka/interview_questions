---
id: android-616
title: Jetpack Window Manager for Foldables / Jetpack Window Manager для складных устройств
aliases:
  - Jetpack Window Manager Foldables
  - Jetpack Window Manager для складных устройств
topic: android
subtopics:
  - window-manager
  - foldable
  - adaptive-ui
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-window-size-class
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/foldable
  - android/window-manager
  - adaptive-ui
  - difficulty/hard
sources:
  - url: https://developer.android.com/jetpack/androidx/releases/window
    note: Jetpack Window Manager documentation
  - url: https://developer.android.com/guide/topics/large-screens/ideas
    note: Adaptive layout patterns
---

# Вопрос (RU)
> Как адаптировать Android-приложение под планшеты и складные устройства с помощью Jetpack Window Manager: обрабатывать WindowSizeClass, posture, hinge и настраивать Compose/Views под разные состояния?

# Question (EN)
> How do you adapt an Android app for tablets and foldables using Jetpack Window Manager, handling WindowSizeClass, posture, and hinge data to customize Compose/View layouts across states?

---

## Ответ (RU)

### 1. Получение WindowMetrics и SizeClass

```kotlin
@OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
@Composable
fun AdaptiveApp(windowSizeClass: WindowSizeClass) {
    val width = windowSizeClass.widthSizeClass
    when (width) {
        Compact -> CompactLayout()
        Medium -> ListDetailSplit()
        Expanded -> ThreePaneLayout()
    }
}
```

- Рассчитывайте `WindowSizeClass` через `calculateWindowSizeClass(activity)`.
- Сохраняйте класс размера в `ViewModel` или `remember` state.

### 2. Posture и FoldingFeature

```kotlin
val windowInfoTracker = WindowInfoTracker.getOrCreate(context)
val layoutInfoFlow = windowInfoTracker.windowLayoutInfo(activity)

layoutInfoFlow.collect { info ->
    val foldingFeature = info.displayFeatures.filterIsInstance<FoldingFeature>().firstOrNull()
    when (foldingFeature?.state) {
        FoldingFeature.State.FLAT -> renderFlat()
        FoldingFeature.State.HALF_OPENED -> renderTent()
    }
}
```

- `FoldingFeature.orientation` (HORIZONTAL/VERTICAL) используется, чтобы определить safe area.
- `isSeparating` указывает, делит ли шарнир экран.

### 3. ActivityEmbedding (Views)

```kotlin
RuleController.getInstance(context).setRules(
    setOf(
        SplitPairRule.Builder(...)
            .setMinWidthDp(600)
            .setFinishPrimaryWithSecondary(ALWAYS)
            .build()
    )
)
```

- Позволяет запускать master-detail в отдельном окне на планшетах.
- Работает поверх Window Manager.

### 4. Compose адаптация

- Используйте `NavigationSuiteScaffold` (Material 3) для адаптивной навигации.
- Паттерн `ListDetailPaneScaffold` (Accompanist Adaptive).
- Для hinge safe area: `WindowInsetsCompat.Type.displayCutout()` + `FoldingFeature.bounds`.

### 5. Тестирование

- Emulator Foldable (Pixel Fold, Surface Duo) + posture recording.
- UI тесты: `WindowLayoutInfoPublisherRule` (Jetpack test artifact).
- Snapshot тесты для разных size class.

### 6. Производительность

- Кэшируйте крупные UI состояния; избегайте heavy recomposition при posture change.
- Используйте `rememberSaveable` для хранения состояния панелей.
- На ChromeOS проверяйте multi-window (ResizableActivity flag).

---

## Answer (EN)

- Compute `WindowSizeClass` per activity and use it to branch UI into compact/medium/expanded experiences.
- Subscribe to `WindowLayoutInfo` to detect `FoldingFeature` posture, hinge orientation, and separation; adjust layout safe areas accordingly.
- Apply Activity Embedding rules for View-based UIs, enabling split pane experiences on tablets/foldables.
- In Compose, leverage `NavigationSuiteScaffold` or adaptive scaffolds, and account for hinge bounds via insets.
- Test with emulator foldable profiles and `WindowLayoutInfoPublisherRule`; profile recomposition under fold/unfold transitions.

---

## Follow-ups
- Как реализовать drag-and-drop между pane в режиме Expanded?
- Какие UX-анти-паттерны существуют для foldables (например, элементы под шарниром)?
- Как совместить ActivityEmbedding и Navigation Component в многопанельном приложении?

## References
- [[c-window-size-class]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/jetpack/androidx/releases/window
- https://developer.android.com/guide/topics/large-screens/ideas

## Related Questions

- [[c-window-size-class]]
- [[q-android-coverage-gaps--android--hard]]
