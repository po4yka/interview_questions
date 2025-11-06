---
id: android-630
title: Wear Compose UX Patterns / UX-паттерны Wear Compose
aliases:
  - Wear Compose UX Patterns
  - UX-паттерны Wear Compose
topic: android
subtopics:
  - wear
  - compose
  - ui
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-wear-compose
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/wear
  - android/compose
  - ux
  - difficulty/hard
sources:
  - url: https://developer.android.com/training/wearables/compose
    note: Compose for Wear OS guide
  - url: https://github.com/google/horologist
    note: Horologist libraries
---

# Вопрос (RU)
> Как спроектировать сложное приложение на Wear OS с Compose: навигация со Swipe-to-dismiss, обработка rotary input, адаптация под круглые экраны, Tiles и Complications?

# Question (EN)
> How do you architect a complex Wear OS app with Compose, covering swipe-to-dismiss navigation, rotary input handling, round screen adaptation, and supporting Tiles and complications?

---

## Ответ (RU)

### 1. Навигация и структура

- Используйте `SwipeDismissableNavHost` (Horologist) для стековой навигации.
- `rememberSwipeDismissableNavController()` хранит состояние.
- Экраны оборачивайте в `SwipeToDismissBox` для edge gestures.

```kotlin
val navController = rememberSwipeDismissableNavController()

SwipeDismissableNavHost(
    navController = navController,
    startDestination = "home"
) {
    composable("home") { HomeScreen(navController) }
    composable("details/{id}") { backStackEntry ->
        DetailsScreen(backStackEntry.arguments?.getString("id")!!)
    }
}
```

### 2. Scaling UI

- Главные списки → `ScalingLazyColumn` (эффект масштабирования).
- Используйте `TimeText`, `Vignette`, `PositionIndicator`.
- Отрисовывайте curved текст через `CurvedRow`, `CurvedText`.

### 3. Rotary input & жесты

```kotlin
val scalingState = rememberScalingLazyListState()
ScalingLazyColumn(
    state = scalingState,
    modifier = Modifier
        .focusable()
        .onRotaryScrollEvent {
            scalingState.dispatchRawDelta(it.verticalScrollPixels)
            true
        }
) { /* items */ }
```

- Horologist `RotaryScrollAdapter` упрощает обработку.
- Используйте haptics (`HapticFeedbackType.TextHandleMove`) для подтверждения.

### 4. Tiles & Complications

- Tiles: создайте `TileService`, используйте Compose Tile DSL.

```kotlin
class StatsTileService : TileService() {
    override fun onTileRequest(requestParams: TileRequest): ListenableFuture<Tile> =
        Futures.immediateFuture(
            tile {
                timeline {
                    entry {
                        layout {
                            primaryLayout {
                                content {
                                    text {
                                        text = "Steps ${state.steps}"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        )
}
```

- Complications требуют `ComplicationDataSourceService` (не Compose) — обновляйте через `ComplicationDataSourceUpdateRequester`.

### 5. Performance & power

- Держите recomposition лёгкой; используйте `remember` и immutable state.
- Для long-running tasks – `WorkManager` + `Expedited` jobs осторожно (battery).
- Cache haptics/animations; избегайте heavy bitmaps (высокое DPI).

### 6. Тестирование

- Ручные тесты на круглых и квадратных эмуляторах, разных DPI.
- UI тесты: `ComposeTestRule` + `createAndroidComposeRule`.
- Accessibility: проверяйте touch target >= 48dp, support talkback.

---

## Answer (EN)

- Structure navigation with `SwipeDismissableNavHost`, wrap screens in `SwipeToDismissBox`, and keep state in a shared nav controller.
- Adopt `ScalingLazyColumn`, `TimeText`, `Vignette`, and curved composables to fit round screens.
- Handle rotary input via `onRotaryScrollEvent` or Horologist helpers, providing haptic feedback.
- Build Tiles with Compose Tile DSL and manage complications via data source services alongside the Compose UI.
- Optimize recomposition, manage background work conservatively, and validate across device shapes, accessibility, and battery constraints.

---

## Follow-ups
- Как интегрировать Health Services стримы в Compose UI с минимальной задержкой?
- Как реализовать offline caching и sync в Wear app (Companion + DataLayer)?
- Какие паттерны для multi-device navigation (Phone ↔ Watch) при Compose?

## References
- [[c-wear-compose]]
- https://developer.android.com/training/wearables/compose

## Related Questions

- [[c-wear-compose]]
