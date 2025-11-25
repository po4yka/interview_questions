---
id: android-630
title: Wear Compose UX Patterns / UX-паттерны Wear Compose
aliases: [UX-паттерны Wear Compose, Wear Compose UX Patterns]
topic: android
subtopics:
  - ui-compose
  - wear
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-jetpack-compose
  - q-android-tv-compose-leanback--android--hard
  - q-compose-core-components--android--medium
  - q-compose-custom-animations--android--medium
  - q-how-does-jetpackcompose-work--android--medium
created: 2025-11-02
updated: 2025-11-10
tags: [android/ui-compose, android/wear, difficulty/hard, ux]
sources:
- url: "https://developer.android.com/training/wearables/compose"
  note: Compose for Wear OS guide
- url: "https://github.com/google/horologist"
  note: Horologist libraries

date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)
> Как спроектировать сложное приложение на Wear OS с Compose: навигация со Swipe-to-dismiss, обработка rotary input, адаптация под круглые экраны, Tiles и Complications?

# Question (EN)
> How do you architect a complex Wear OS app with Compose, covering swipe-to-dismiss navigation, rotary input handling, round screen adaptation, and supporting Tiles and complications?

---

## Ответ (RU)

### 1. Навигация И Структура

- Используйте `SwipeDismissableNavHost` из Wear Compose для стековой навигации со встроенным swipe-to-dismiss.
- `rememberSwipeDismissableNavController()` хранит состояние навигации.
- Для отдельных экранов вне `SwipeDismissableNavHost` используйте `SwipeToDismissBox` для edge gestures (не дублируйте его поверх `SwipeDismissableNavHost`).

```kotlin
val navController = rememberSwipeDismissableNavController()

SwipeDismissableNavHost(
    navController = navController,
    startDestination = "home"
) {
    composable("home") { HomeScreen(navController) }
    composable("details/{id}") { backStackEntry ->
        val id = backStackEntry.arguments?.getString("id")
        requireNotNull(id)
        DetailsScreen(id)
    }
}
```

### 2. Scaling UI

- Для основных списков используйте `ScalingLazyColumn` (эффект масштабирования, улучшенная читаемость на круглых экранах).
- Используйте системные компоненты Wear Compose: `TimeText`, `Vignette`, `PositionIndicator`.
- Для изогнутого текста задействуйте `CurvedRow`, `CurvedText`.

### 3. Rotary Input & Жесты

```kotlin
val scalingState = rememberScalingLazyListState()

ScalingLazyColumn(
    state = scalingState,
    modifier = Modifier
        .focusable() // обеспечьте, что компонент получает фокус
        .onRotaryScrollEvent {
            scalingState.dispatchRawDelta(it.verticalScrollPixels)
            true
        }
) {
    // items(...)
}
```

- Обеспечьте получение фокуса (например, при появлении экрана) — без этого `onRotaryScrollEvent` может не вызываться.
- Horologist `RotaryScrollAdapter` упрощает привязку rotary input к состоянию списка.
- Используйте уместный haptic feedback (например, лёгкий клик при ключевых взаимодействиях), избегая несемантичных типов вроде `TextHandleMove` для скролла.

### 4. Tiles & Complications

- Tiles: реализуйте `TileService` на базе `androidx.wear.tiles` и используйте Compose-совместимый Tile DSL/Material-элементы для описания layout.

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
                                        text = "Steps"
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

- Логику получения состояния (шаги и т.п.) инкапсулируйте в репозитории/слое данных и считывайте её внутри сервиса; не используйте напрямую Compose state из UI.
- Complications реализуются через `ComplicationDataSourceService` (без Compose UI) и обновляются через `ComplicationDataSourceUpdateRequester`.

### 5. Performance & Power

- Держите recomposition лёгкой: используйте `remember`, immutable state, ключи для списков.
- Для долгих задач применяйте `WorkManager` и другие фоновые механизмы с осторожным выбором приоритетов (бережно к батарее).
- Минимизируйте тяжёлые ресурсы (большие битмапы, частые анимации), переиспользуйте объекты анимаций/haptics там, где это возможно.

### 6. Тестирование

- Ручные тесты на круглых и квадратных эмуляторах/устройствах, разных DPI.
- UI-тесты: `ComposeTestRule` + `createAndroidComposeRule` для экранов на Wear Compose.
- Accessibility: проверяйте touch target ≥ 48dp, поддержку TalkBack, контрастность и читаемость на небольшом экране.

## Краткая Версия
- Используйте `SwipeDismissableNavHost` и `SwipeToDismissBox` для нативной навигации со swipe-to-dismiss.
- Применяйте `ScalingLazyColumn`, `TimeText`, `Vignette`, `PositionIndicator`, `CurvedText` для адаптации под круглые экраны.
- Обрабатывайте rotary input через `onRotaryScrollEvent` или Horologist, обеспечивая фокус.
- Выносите данные и бизнес-логику в отдельные слои для экранов, Tiles и Complications.
- Оптимизируйте производительность и энергопотребление, минимизируя тяжёлый UI и фоновую работу.

### Детальная Версия

#### Требования

- Функциональные:
  - Навигация со swipe-to-dismiss для стековых экранов.
  - Поддержка rotary input для скролла и выбора.
  - Корректный UI на круглых и квадратных экранах.
  - Интеграция Tiles и Complications с общими данными приложения.
- Нефункциональные:
  - Низкое энергопотребление и быстрый отклик.
  - Стабильная работа при ограниченных ресурсах.
  - Хорошая доступность (крупные таргеты, контрастность, поддержка TalkBack).

#### Архитектура

- UI слой: Wear Compose (`SwipeDismissableNavHost`, `ScalingLazyColumn`, `TimeText`, `CurvedText`).
- Навигация: один `NavHost` для экранов часов, отдельные entry points для Tiles и Complications.
- Доменный слой: use-cases/интеракторы для бизнес-логики (агрегация данных шагов, уведомления, синхронизация с телефоном).
- Data слой: репозитории для Health Services, сенсоров, сети, DataLayer/companion app и локального кеша.
- Tiles и Complications: отдельные сервисы, которые обращаются к shared репозиториям, без прямой зависимости от Compose UI.

---

## Answer (EN)

### 1. Navigation and Structure

- Use `SwipeDismissableNavHost` from Wear Compose for stack-based navigation with built-in swipe-to-dismiss.
- Keep a shared navigation state via `rememberSwipeDismissableNavController()`.
- For screens outside `SwipeDismissableNavHost`, wrap content in `SwipeToDismissBox` for edge gestures (avoid layering it on top of `SwipeDismissableNavHost`).

```kotlin
val navController = rememberSwipeDismissableNavController()

SwipeDismissableNavHost(
    navController = navController,
    startDestination = "home"
) {
    composable("home") { HomeScreen(navController) }
    composable("details/{id}") { backStackEntry ->
        val id = backStackEntry.arguments?.getString("id")
        requireNotNull(id)
        DetailsScreen(id)
    }
}
```

### 2. Scaling UI

- Use `ScalingLazyColumn` for primary lists to get scaling and better readability on round screens.
- Leverage Wear Compose components: `TimeText`, `Vignette`, `PositionIndicator`.
- Use `CurvedRow` and `CurvedText` for curved text along the watch edge.

### 3. Rotary Input & Gestures

```kotlin
val scalingState = rememberScalingLazyListState()

ScalingLazyColumn(
    state = scalingState,
    modifier = Modifier
        .focusable() // ensure the component can receive focus
        .onRotaryScrollEvent {
            scalingState.dispatchRawDelta(it.verticalScrollPixels)
            true
        }
) {
    // items(...)
}
```

- Handle rotary input with `onRotaryScrollEvent` on a focusable component bound to list state (e.g., `ScalingLazyListState`), or use Horologist `RotaryScrollAdapter` to simplify mapping.
- Ensure the composable can gain focus; otherwise rotary events may not be delivered.
- Provide appropriate haptic feedback (e.g., subtle click or confirmation for key interactions), avoiding unrelated feedback types, including non-semantic ones such as `TextHandleMove` for scroll.

### 4. Tiles & Complications

- Implement Tiles via `TileService` using `androidx.wear.tiles` APIs and the Tile DSL/Material layout helpers.

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
                                        text = "Steps"
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

- Encapsulate data fetching logic (steps, etc.) in a repository/data layer and read it inside the service; avoid using Compose state from app UI directly in `TileService`.
- Implement complications with `ComplicationDataSourceService` (they do not use Compose UI directly) and trigger updates via `ComplicationDataSourceUpdateRequester`.

### 5. Performance & Power

- Keep recompositions cheap: use stable/immutable state, `remember`, and keys for list items; avoid heavy work in Composables.
- Use background work (e.g., `WorkManager`) conservatively, respecting battery constraints on Wear devices.
- Avoid heavy bitmaps and aggressive animations; reuse haptic and animation objects where applicable.

### 6. Testing

- Test on round and square emulators/devices and multiple DPI configurations.
- Use Compose UI testing (`ComposeTestRule`, `createAndroidComposeRule`) for Wear Compose screens.
- Verify accessibility: touch targets ≥ 48dp, proper TalkBack support, and sufficient contrast and legibility.

## Short Version
- Use `SwipeDismissableNavHost` and `SwipeToDismissBox` for native navigation with swipe-to-dismiss.
- Use `ScalingLazyColumn`, `TimeText`, `Vignette`, `PositionIndicator`, `CurvedText` to adapt to round screens.
- Handle rotary input via `onRotaryScrollEvent` or Horologist with correct focus.
- Share data and business logic across screens, Tiles, and complications via repositories.
- Optimize for performance and battery by minimizing heavy UI and background work.

## Detailed Version

#### Requirements

- Functional:
  - Swipe-to-dismiss navigation for stacked screens.
  - Rotary input support for scrolling and selection.
  - Proper UI behavior on round and square screens.
  - Tiles and complications integrated with shared app data.
- Non-functional:
  - Low power consumption and responsive interactions.
  - Robust behavior under constrained resources.
  - Good accessibility (large targets, contrast, TalkBack support).

#### Architecture

- UI layer: Wear Compose (`SwipeDismissableNavHost`, `ScalingLazyColumn`, `TimeText`, `CurvedText`).
- Navigation: single `NavHost` for watch screens; separate entry points for Tiles and complications.
- Domain layer: use cases/interactors implementing business logic (e.g., step aggregation, notifications, phone sync).
- Data layer: repositories for Health Services, sensors, network, DataLayer/companion app, and local cache.
- Tiles and complications: dedicated services consuming shared repositories without direct dependency on Compose UI.

---

## Дополнительные Вопросы (RU)
- Как интегрировать стримы Health Services в Compose UI с минимальной задержкой?
- Как реализовать offline caching и sync в Wear-приложении (Companion + DataLayer)?
- Какие паттерны использовать для multi-device навигации (телефон ↔ часы) при использовании Compose?

## Follow-ups
- How to integrate Health Services streams into Compose UI with minimal latency?
- How to implement offline caching and sync in a Wear app (Companion + DataLayer)?
- What patterns to use for multi-device navigation (Phone ↔ Watch) with Compose?

## Ссылки (RU)
- [[c-jetpack-compose]]
- https://developer.android.com/training/wearables/compose

## References
- [[c-jetpack-compose]]
- https://developer.android.com/training/wearables/compose

## Связанные Вопросы (RU)
- [[q-android-tv-compose-leanback--android--hard]]

## Related Questions
- [[q-android-tv-compose-leanback--android--hard]]
