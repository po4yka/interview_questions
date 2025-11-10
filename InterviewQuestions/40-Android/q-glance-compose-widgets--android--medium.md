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
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-glance
  - c-jetpack-compose
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/shortcuts-widgets
  - android/ui-compose
  - android/ui-widgets
  - android/glance
  - difficulty/medium
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
class WeatherWidget : GlanceAppWidget() {
    @Composable
    override fun Content() {
        val uiState = currentState<WeatherState>()
        WeatherCard(uiState)
    }
}
```

- Наследуемся от `GlanceAppWidget`, реализуем `Content`.
- Состояние обычно хранится через `GlanceStateDefinition` (Preferences/DataStore/Proto) или прокидывается через `update`.

### 2. Состояние и обновления

```kotlin
object WeatherStateDefinition : GlanceStateDefinition<WeatherState> {
    override suspend fun getDataStore(context: Context, fileKey: String): DataStore<WeatherState> =
        DataStoreFactory.create(
            serializer = WeatherStateSerializer,
            produceFile = { context.dataStoreFile("$fileKey.preferences_pb") }
        )

    override suspend fun getDataStoreKey(context: Context, glanceId: GlanceId): String =
        glanceId.toString()
}

class WeatherWidgetReceiver : GlanceAppWidgetReceiver() {
    override val glanceAppWidget: GlanceAppWidget = WeatherWidget()

    override suspend fun onUpdate(
        context: Context,
        glanceId: GlanceId
    ) {
        WeatherUpdateWorker.enqueue(context, glanceId)
    }
}
```

- Можно использовать `GlanceStateDefinition` (или готовые `PreferencesGlanceStateDefinition`/`ProtoGlanceStateDefinition`) для персистентного состояния.
- Для периодических обновлений обычно используют WorkManager + `GlanceAppWidgetManager.getGlanceIds()`.
- Учитывайте ограничения по обновлениям: для периодических обновлений действуют минимальные интервалы (около 30 минут) и квоты на частоту; ручные/событийные обновления возможны чаще, но тоже подчиняются системным лимитам по энергопотреблению.

### 3. Actions и интерактивность

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

- Используйте `actionRunCallback` для фоновых действий, `actionStartActivity`/`actionStartActivityForResult` для открытия экранов.
- Ограничения: нельзя использовать произвольные Compose-компоненты; доступны только Glance-компоненты и модификаторы, которые маппятся в `RemoteViews`.

### 4. Dynamic Color & Размеры

- Используйте `GlanceTheme` и его `colors` (с поддержкой dynamic color, если доступно у хоста/на версии Android) для консистентного оформления.
- Обрабатывайте `LocalSize.current` для адаптации layout под разные размеры виджета.

### 5. Тестирование

- Используйте `GlanceAppWidgetTestRule` (Robolectric/инструментальные тесты) для рендеринга и проверки контента виджета.
- Делайте снапшоты с помощью `GlanceAppWidgetTestRule.snapshot` и сравнивайте выходной `RemoteViews`/layout.
- Пишите юнит-тесты для сериализаторов и логики обновления состояния.

---

## Answer (EN)

### 1. Glance structure

```kotlin
class WeatherWidget : GlanceAppWidget() {
    @Composable
    override fun Content() {
        val uiState = currentState<WeatherState>()
        WeatherCard(uiState)
    }
}
```

- Extend `GlanceAppWidget` and implement `Content`.
- Store widget state via a `GlanceStateDefinition` (Preferences/DataStore/Proto) or pass data via `update`.

### 2. State and updates

```kotlin
object WeatherStateDefinition : GlanceStateDefinition<WeatherState> {
    override suspend fun getDataStore(context: Context, fileKey: String): DataStore<WeatherState> =
        DataStoreFactory.create(
            serializer = WeatherStateSerializer,
            produceFile = { context.dataStoreFile("$fileKey.preferences_pb") }
        )

    override suspend fun getDataStoreKey(context: Context, glanceId: GlanceId): String =
        glanceId.toString()
}

class WeatherWidgetReceiver : GlanceAppWidgetReceiver() {
    override val glanceAppWidget: GlanceAppWidget = WeatherWidget()

    override suspend fun onUpdate(
        context: Context,
        glanceId: GlanceId
    ) {
        WeatherUpdateWorker.enqueue(context, glanceId)
    }
}
```

- Use a `GlanceStateDefinition` (or built-ins like `PreferencesGlanceStateDefinition`/`ProtoGlanceStateDefinition`) for persistent state.
- Use WorkManager plus `GlanceAppWidgetManager.getGlanceIds()` for periodic/background updates.
- Respect update quotas: periodic updates have a minimum interval (around 30 minutes) and system-enforced limits; event-driven/manual updates can be more frequent but are still constrained by system policies.

### 3. Actions and interactivity

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

- Use `actionRunCallback` for background logic and `actionStartActivity`/`actionStartActivityForResult` to launch activities from the widget.
- Glance does not allow arbitrary Compose UI; you must use the provided Glance composables and modifiers that map to `RemoteViews`.

### 4. Dynamic color & sizes

- Use `GlanceTheme` (with dynamic color when supported by the host/Android version) for consistent styling.
- Use `LocalSize.current` to adapt the layout to the widget size.

### 5. Testing

- Use `GlanceAppWidgetTestRule` with Robolectric/instrumentation to render and assert on widget content.
- Capture snapshots via `GlanceAppWidgetTestRule.snapshot` for layout/RemoteViews comparison.
- Add unit tests for state serializers and update logic.

---

## Дополнительные вопросы (RU)
- Как организовать списки (`GlanceList`) и диффы данных?
- Как обновлять виджет из push-уведомлений?
- Какие ограничения у Glance на Android < 12 (dynamic color fallback)?

## Follow-ups
- How to implement lists (`GlanceList`) and data diffing?
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
