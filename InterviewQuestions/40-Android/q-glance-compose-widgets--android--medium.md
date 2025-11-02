---
id: android-621
title: Glance Compose Widgets / Виджеты Glance на Compose
aliases:
  - Glance Compose Widgets
  - Виджеты Glance на Compose
topic: android
subtopics:
  - widgets
  - compose
  - glance
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
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/widgets
  - android/glance
  - compose
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
- Состояние хранится через `GlanceStateDefinition` (Preferences/DataStore/Proto).

### 2. Состояние и обновления

```kotlin
object WeatherStateDefinition : GlanceStateDefinition<WeatherState> {
    override suspend fun getDataStore(context: Context, fileKey: String) =
        context.createDataStore(
            fileName = "$fileKey.preferences_pb",
            serializer = WeatherStateSerializer
        )
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

- Используйте WorkManager для периодических обновлений (`GlanceAppWidgetManager.getGlanceIds()`).
- Учитывайте ограничения по частоте обновлений (не чаще 30 мин без разрешений).

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

- Используйте `actionRunCallback`, `actionLaunchActivity`, `actionStartActivity`.
- Ограничения: нет кастомных composables, только Glance-виджеты.

### 4. Dynamic Color & Размеры

- Применяйте `GlanceTheme` + `dynamicColor = true`.
- Handle `LocalSize.current` для адаптации layout.

### 5. Тестирование

- Robolectric поддерживает Glance через `GlanceAppWidgetTestRule`.
- Снапшоты — `GlanceAppWidgetTestRule.snapshot`.
- Юнит-тесты сериализаторов состояния.

---

## Answer (EN)

- Extend `GlanceAppWidget`, store state via `GlanceStateDefinition`, and update using WorkManager or `updateAll`.
- Handle user interactions with `ActionCallback` and respect widget update frequency quotas.
- Use Glance theming for dynamic color and adapt layouts based on `LocalSize`.
- Test with Glance test rule, snapshot comparisons, and serialization unit tests.

---

## Follow-ups
- Как организовать списки (GlanceList) и диффы данных?
- Как обновлять виджет из push-уведомлений?
- Какие ограничения у Glance на Android < 12 (dynamic color fallback)?

## References
- [[c-glance]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/jetpack/compose/glance/appwidget
