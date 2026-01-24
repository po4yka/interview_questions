---
id: android-621
title: Glance Compose Widgets / Виджеты Glance на Compose
aliases:
- Glance Compose Widgets
- Виджеты Glance на Compose
topic: android
subtopics:
- shortcuts-widgets
- ui-compose
- ui-widgets
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-glance
- c-jetpack-compose
- q-compose-core-components--android--medium
- q-compose-custom-animations--android--medium
- q-how-does-jetpackcompose-work--android--medium
created: 2025-11-02
updated: 2025-11-11
tags:
- android/glance
- android/shortcuts-widgets
- android/ui-compose
- android/ui-widgets
- difficulty/medium
anki_cards:
- slug: android-621-0-en
  language: en
  anki_id: 1768367361280
  synced_at: '2026-01-23T16:45:05.577716'
- slug: android-621-0-ru
  language: ru
  anki_id: 1768367361306
  synced_at: '2026-01-23T16:45:05.580185'
sources:
- url: https://developer.android.com/jetpack/compose/glance/appwidget
  note: Glance app widget guide
---
# Вопрос (RU)
> Как создать и поддерживать аппвиджет на Jetpack Glance: управлять состоянием, обновлениями, действиями и ограничениями RemoteViews?

# Question (EN)
> How do you build and maintain Jetpack Glance app widgets, handling state, updates, actions, and RemoteViews constraints?

---

## Ответ (RU)

### 1. Структура Glance

```kotlin
object WeatherStateDefinition : PreferencesGlanceStateDefinition // или ProtoGlanceStateDefinition / кастомная реализация

class WeatherWidget : GlanceAppWidget() {
    override val stateDefinition: GlanceStateDefinition<*> = WeatherStateDefinition

    @Composable
    override fun Content() {
        val uiState = currentState<WeatherState>()
        WeatherCard(uiState)
    }
}
```

- Наследуемся от `GlanceAppWidget`, реализуем `Content`.
- Привязываем `stateDefinition` к виджету, чтобы `currentState`/`updateAppWidgetState` работали корректно.
- Состояние обычно хранится через `GlanceStateDefinition` (Preferences/DataStore/Proto) или прокидывается через `update`/`updateAppWidgetState`.

### 2. Состояние И Обновления

```kotlin
// Пример использования готового PreferencesGlanceStateDefinition:
object WeatherStateDefinition : PreferencesGlanceStateDefinition

class WeatherWidgetReceiver : GlanceAppWidgetReceiver() {
    override val glanceAppWidget: GlanceAppWidget = WeatherWidget()

    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, appWidgetIds: IntArray) {
        super.onUpdate(context, appWidgetManager, appWidgetIds)
        // Триггерим фоновые обновления, если нужно
        WeatherUpdateWorker.enqueueForAll(context)
    }
}
```

- Можно использовать `GlanceStateDefinition` (или готовые `PreferencesGlanceStateDefinition`/`ProtoGlanceStateDefinition`) для персистентного состояния; при кастомной реализации обязательно реализуйте все требуемые методы (`getData`, `updateData`, `getLocation`/`getDataStore` в зависимости от версии API) с устойчивыми ключами.
- Для периодических обновлений обычно используют `WorkManager` + `GlanceAppWidgetManager(context).getGlanceIds(WeatherWidget::class.java)`.
- Учитывайте ограничения по обновлениям: для периодических обновлений действуют минимальные интервалы и квоты на частоту; ручные/событийные обновления возможны чаще, но также подчиняются системным лимитам по энергопотреблению.

### 3. Actions И Интерактивность

```kotlin
@Composable
fun WeatherCard(state: WeatherState) {
    Column(
        modifier = GlanceModifier
            .fillMaxSize()
            .background(ColorProvider(day = Color.White, night = Color.Black))
            .clickable(actionRunCallback<RefreshAction>())
    ) {
        Text("Temp: ${state.temp}")
    }
}

class RefreshAction : ActionCallback {
    override suspend fun onAction(
        context: Context,
        glanceId: GlanceId,
        parameters: ActionParameters
    ) {
        WeatherUpdateWorker.enqueue(context, glanceId, force = true)
    }
}
```

- Используйте `actionRunCallback` для фоновых действий и обновления виджета; `actionStartActivity` — для открытия экранов из виджета.
- Ограничения: нельзя использовать произвольные Compose-компоненты; доступны только Glance-компоненты и модификаторы, которые маппятся в `RemoteViews`.

### 4. Dynamic Color & Размеры

- Используйте `GlanceTheme` и его `colors` (с поддержкой dynamic color, если доступно у хоста/на версии Android) для консистентного оформления.
- Обрабатывайте `LocalSize.current` для адаптации layout под разные размеры виджета.

### 5. Тестирование

- Используйте `GlanceAppWidgetTestRule` (Robolectric/инструментальные тесты) для рендеринга и проверки содержимого виджета.
- Делайте снапшоты с помощью `GlanceAppWidgetTestRule.snapshot` и сравнивайте получившиеся `RemoteViews`/layout с ожидаемыми.
- Пишите юнит-тесты для сериализаторов и логики обновления состояния.

---

## Answer (EN)

### 1. Glance Structure

```kotlin
object WeatherStateDefinition : PreferencesGlanceStateDefinition // or ProtoGlanceStateDefinition / custom implementation

class WeatherWidget : GlanceAppWidget() {
    override val stateDefinition: GlanceStateDefinition<*> = WeatherStateDefinition

    @Composable
    override fun Content() {
        val uiState = currentState<WeatherState>()
        WeatherCard(uiState)
    }
}
```

- Extend `GlanceAppWidget` and implement `Content`.
- Attach a `stateDefinition` to the widget so `currentState`/`updateAppWidgetState` can resolve state correctly.
- Store widget state via a `GlanceStateDefinition` (Preferences/DataStore/Proto) or pass/update data using `update`/`updateAppWidgetState`.

### 2. State and Updates

```kotlin
// Example using built-in PreferencesGlanceStateDefinition:
object WeatherStateDefinition : PreferencesGlanceStateDefinition

class WeatherWidgetReceiver : GlanceAppWidgetReceiver() {
    override val glanceAppWidget: GlanceAppWidget = WeatherWidget()

    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, appWidgetIds: IntArray) {
        super.onUpdate(context, appWidgetManager, appWidgetIds)
        // Trigger background updates if needed
        WeatherUpdateWorker.enqueueForAll(context)
    }
}
```

- Use a `GlanceStateDefinition` (or built-ins like `PreferencesGlanceStateDefinition`/`ProtoGlanceStateDefinition`) for persistent state; for custom definitions you must implement all required methods (`getData`, `updateData`, `getLocation`/`getDataStore` depending on API version) with stable keys.
- Use `WorkManager` plus `GlanceAppWidgetManager(context).getGlanceIds(WeatherWidget::class.java)` for periodic/background updates.
- Respect update quotas: periodic updates have minimum intervals and system-enforced limits; event-driven/manual updates can be more frequent but are still constrained by system power/abuse policies.

### 3. Actions and Interactivity

```kotlin
@Composable
fun WeatherCard(state: WeatherState) {
    Column(
        modifier = GlanceModifier
            .fillMaxSize()
            .background(ColorProvider(day = Color.White, night = Color.Black))
            .clickable(actionRunCallback<RefreshAction>())
    ) {
        Text("Temp: ${state.temp}")
    }
}

class RefreshAction : ActionCallback {
    override suspend fun onAction(
        context: Context,
        glanceId: GlanceId,
        parameters: ActionParameters
    ) {
        WeatherUpdateWorker.enqueue(context, glanceId, force = true)
    }
}
```

- Use `actionRunCallback` for background work and widget refresh; use `actionStartActivity` to launch activities from the widget.
- Glance does not allow arbitrary Compose UI; you must use the provided Glance composables and modifiers that map to `RemoteViews`.

### 4. Dynamic Color & Sizes

- Use `GlanceTheme` (with dynamic color when supported by the host/Android version) for consistent styling.
- Use `LocalSize.current` to adapt the layout to different widget sizes.

### 5. Testing

- Use `GlanceAppWidgetTestRule` with Robolectric/instrumentation tests to render and assert on widget content.
- Capture snapshots via `GlanceAppWidgetTestRule.snapshot` and compare the resulting `RemoteViews`/layout against expectations.
- Add unit tests for state serializers and update logic.

---

## Дополнительные Вопросы (RU)
- Как организовать списки (например, через поддерживаемые Glance-компоненты) и диффы данных?
- Как обновлять виджет из push-уведомлений?
- Какие ограничения у Glance на Android < 12 (dynamic color fallback)?

## Follow-ups (EN)
- How to implement lists (e.g., via supported Glance list components) and data diffing?
- How to update the widget from push notifications?
- What Glance limitations exist on Android < 12 (dynamic color fallback)?

## Ссылки (RU)
- [[c-glance]]
- https://developer.android.com/jetpack/compose/glance/appwidget

## References
- [[c-glance]]
- https://developer.android.com/jetpack/compose/glance/appwidget

## Related Questions

- [[c-glance]]
