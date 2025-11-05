---
id: android-617
title: Wear OS Health Integration / Интеграция Health Services и Health Connect
aliases:
  - Wear OS Health Integration
  - Интеграция Health Services и Health Connect
topic: android
subtopics:
  - wear
  - health
  - sensors
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-wear-health
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/wear
  - android/health
  - sensors
  - difficulty/hard
sources:
  - url: https://developer.android.com/training/wearables/health-services
    note: Health Services documentation
  - url: https://developer.android.com/guide/health-and-fitness/health-connect
    note: Health Connect guide
---

# Вопрос (RU)
> Как построить систему сбора и синхронизации данных здоровья на Wear OS: комбинировать Health Services (онлайн измерения, batching) и Health Connect (шаринг на телефон), не нарушая энергобюджет и политику разрешений?

# Question (EN)
> How do you architect Wear OS health data collection that combines Health Services for measurements and Health Connect for data sharing, while respecting power budgets and permission policies?

---

## Ответ (RU)

### Архитектура

1. **Health Services** — работа с сенсорами в реальном времени.
2. **Health Connect** — централизованный storage/обмен данными, синхронизация с телефоном.
3. **Companion App** — отображение аналитики и бекенд-синхронизация.

### Health Services Setup

```kotlin
val measureClient = HealthServicesClient.getOrCreate(context).measureClient

val dataTypes = setOf(DataType.HEART_RATE_BPM, DataType.STEPS)

measureClient.registerMeasureCallback(
    dataTypes,
    Executors.newSingleThreadExecutor(),
    measureCallback
)
```

- Passive режим (`PassiveMonitoringClient`) для фонового сбора, `ExerciseClient` для активных тренировок.
- Используйте batching (`MeasureCallback` → `DataPointBatch`) и сохраняйте timestamp для Health Connect.

### Power Budget

- Запускайте `ForegroundService` только для Exercise сессий, остальное — passive monitoring.
- Используйте `Constraints` (battery not low) и `Quota` API для долгих тренировок.
- Выводите состояния в `Complication`/Tile, чтобы не держать Activity.

### Health Connect Integration

```kotlin
val permissions = setOf(
    Permission.HEART_RATE_READ,
    Permission.HEART_RATE_WRITE
)

val healthConnectClient = HealthConnectClient.getOrCreate(context)

if (healthConnectClient.permissionController.getGrantedPermissions()
    .containsAll(permissions).not()) {
    val intent = healthConnectClient.permissionController.createRequestPermissionActivityContract()
}
```

- Перед записью проверяйте `PermissionController`.
- Пакуйте данные в `Record` (`HeartRateRecord`, `StepsRecord`) и пишите через `insertRecords`.
- Для синхронизации с телефоном используйте `RemoteDataSync` или собственный API через companion app.

### Политики и тестирование

- Разрешения должны быть обоснованы (Google Play review).
- Тестируйте потерю связи: Health Connect пишет локально, синхронизирует при появлении телефона.
- Используйте `Health Services Emulator` для Mock-сенсоров и `adb shell cmd health connect` для тестов.

### UX

- Дайте пользователю выбор уровней сбора данных (continuous vs on-demand).
- Отображайте индикатор активности сенсора, уведомляйте о высоком энергопотреблении.

---

## Answer (EN)

- Use Health Services for on-device measurements (passive monitoring for low power, exercise sessions for workouts) and batch data via callbacks.
- Request Health Connect permissions explicitly; write aggregated `Record` objects for cross-app sharing.
- Synchronize with a companion app using Health Connect or custom APIs; handle offline scenarios gracefully.
- Manage power by limiting foreground services to workouts, leveraging passive monitoring elsewhere.
- Validate behavior with emulator tools and ensure Play Store compliance by justifying health data usage.

---

## Follow-ups
- Как передавать данные в real-time на телефон (BLE/Companion) при отсутствии Health Connect?
- Какие ограничения вводит Health Connect на историю данных и ревокацию разрешений?
- Как использовать Tiles/Complications для отображения данных без запуска Activity?

## References
- [[c-wear-health]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/training/wearables/health-services
- https://developer.android.com/guide/health-and-fitness/health-connect

## Related Questions

- [[c-wear-health]]
- [[q-android-coverage-gaps--android--hard]]
