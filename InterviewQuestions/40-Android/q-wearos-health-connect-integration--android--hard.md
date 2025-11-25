---
id: android-617
title: Wear OS Health Integration / Интеграция Health Services и Health Connect
aliases: [Wear OS Health Integration, Интеграция Health Services и Health Connect]
topic: android
subtopics:
  - sensors
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
  - c-android
  - q-android-auto-guidelines--android--hard
  - q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium
  - q-integration-testing-strategies--android--medium
  - q-nearby-nfc-uwb-integration--android--hard
created: 2025-11-02
updated: 2025-11-11
tags: [android/sensors, android/wear, difficulty/hard]
sources:
  - "https://developer.android.com/guide/health-and-fitness/health-connect"
  - "https://developer.android.com/training/wearables/health-services"

date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)
> Как построить систему сбора и синхронизации данных здоровья на Wear OS: комбинировать Health Services (онлайн измерения, batching) и Health Connect (шаринг на телефон), не нарушая энергобюджет и политику разрешений?

# Question (EN)
> How do you architect Wear OS health data collection that combines Health Services for measurements and Health Connect for data sharing, while respecting power budgets and permission policies?

---

## Ответ (RU)

## Краткая Версия
- Health Services на часах для получения метрик (passive/exercise), с использованием batching и точных временных меток.
- Health Connect как единая точка хранения и шаринга данных на устройстве.
- Companion-приложение для визуализации и синхронизации с сервером через Health Connect и/или Data Layer / BLE.
- Строгий контроль разрешений и уровней частоты измерений для соблюдения энергобюджета и политик.

## Подробная Версия
### Требования
- Функциональные:
  - Сбор ключевых метрик (например, пульс, шаги, калории, тренировки) на Wear OS.
  - Сохранение данных с точными временными метками и источником.
  - Синхронизация с телефоном и/или backend-сервером.
  - Интеграция с Health Connect для шаринга данных между приложениями.
- Нефункциональные:
  - Минимальное влияние на батарею часов.
  - Уважение приватности и явных разрешений пользователя.
  - Надежность при потере связи и отсутствии сети.
  - Масштабируемость по числу типов метрик и сценариев.

### Архитектура

1. **Health Services** — работа с сенсорами и метриками здоровья на часах (passive + exercise), минимизируя прямую работу с низкоуровневыми сенсорами.
2. **Health Connect** — централизованное хранилище/шина данных здоровья на устройстве, шаринг данных между приложениями и (при наличии) телефоном.
3. **Companion App** — отображение аналитики, агрегация и синхронизация с бекендом; взаимодействует через Health Connect и/или собственный канал связи (Wearable Data Layer / BLE).

См. также [[c-android]].

### Health Services Setup

(Упрощённый пример, точный API см. в документации Health Services.)

```kotlin
val measureClient = HealthServicesClient.getOrCreate(context).measureClient

val dataTypes = setOf(DataType.HEART_RATE_BPM, DataType.STEPS)

measureClient.registerMeasureCallback(
    dataTypes,
    Executors.newSingleThreadExecutor(),
    measureCallback,
)
```

- Используйте `PassiveMonitoringClient` для фонового/низкоэнергетичного сбора (сон, шаги, частота пульса при обычном использовании).
- Используйте `ExerciseClient` для активных тренировок, где допустим foreground service и более частые измерения.
- Используйте возможности batching (`MeasureCallback` / батчи точек данных) и всегда сохраняйте точный `timestamp` и `zoneOffset`, чтобы корректно формировать записи для Health Connect.

### Power Budget

- Запускайте `ForegroundService` только для активных тренировочных сессий через `ExerciseClient`; остальной сбор переводите в пассивный мониторинг.
- Избегайте постоянной работы `Activity`; используйте Tiles/Complications для отображения состояния и ключевых метрик на циферблате без пробуждения UI.
- Для фоновой агрегации/аплоада используйте системно-дружественные механизмы планирования задач (например, WorkManager с ограничениями по батарее/заряду), но не пытайтесь обходить лимиты длительными произвольными задачами.

### Health Connect Integration

```kotlin
val healthConnectClient = HealthConnectClient.getOrCreate(context)

val permissions = setOf(
    HealthPermission.getReadPermission(HeartRateRecord::class),
    HealthPermission.getWritePermission(HeartRateRecord::class),
)

suspend fun ensurePermissionsGranted() {
    val granted = healthConnectClient.permissionController.getGrantedPermissions()
    if (!granted.containsAll(permissions)) {
        // Используйте Activity Result API с
        // PermissionController.createRequestPermissionActivityContract()
        // или соответствующий Intent-запрос из актуального SDK.
    }
}
```

- Перед записью всегда проверяйте и запрашивайте разрешения через `PermissionController` Health Connect.
- Пакуйте данные в соответствующие `Record`-типы (`HeartRateRecord`, `StepsRecord` и т.д.) и записывайте через `insertRecords`, используя исходные временные метки из Health Services.
- Для обмена между часами и телефоном используйте:
  - Health Connect на каждом устройстве (если поддерживается) и согласованный слой синхронизации в companion app;
  - или Data Layer / собственный API companion app, если Health Connect недоступен или требуется near real-time.

### Политики И Тестирование

- Запрашивайте только те разрешения на здоровье и активность, которые реально нужны; обосновывайте их использование для Google Play review.
- Обрабатывайте потерю связи: данные, записанные в Health Connect на часах, должны быть локально консистентны и синхронизироваться при появлении телефона/сети согласно выбранной архитектуре.
- Используйте инструменты:
  - Health Services Emulator / virtual sensors для тестирования логики сбора,
  - `adb shell cmd health_connect` (или актуальные CLI-инструменты) для управления данными и разрешениями Health Connect.

### UX

- Дайте пользователю понятный выбор уровней сбора данных (например: только во время тренировок / периодически / почти непрерывно) с явным описанием влияния на батарею.
- Отображайте индикатор активности сбора (иконка/статус), уведомляйте о повышенном энергопотреблении при интенсивном мониторинге.
- Обеспечьте прозрачность: какие данные пишутся в Health Connect и кем могут быть прочитаны.

---

## Answer (EN)

## Short Version
- Use Health Services on the watch for health metrics (passive/exercise) with batching and precise timestamps.
- Use Health Connect as the unified on-device health data hub and sharing layer.
- Use a companion app for visualization and backend sync via Health Connect and/or Data Layer / BLE.
- Carefully manage permissions and sampling levels to respect power budgets and policies.

## Detailed Version
### Requirements
- Functional:
  - Collect key metrics (e.g., heart rate, steps, calories, workouts) on Wear OS.
  - Persist data with accurate timestamps and source attribution.
  - Sync data with the phone and/or backend services.
  - Integrate with Health Connect for cross-app health data sharing.
- Non-functional:
  - Minimal impact on watch battery.
  - Strong privacy and explicit user consent for health permissions.
  - Robust behavior under connectivity loss.
  - Scalability across multiple data types and use cases.

### Architecture

- Use Health Services on the watch as the primary interface to health metrics:
  - `PassiveMonitoringClient` for low-power background data.
  - `ExerciseClient` for workouts with higher sampling and allowed foreground service.
- Use Health Connect as the on-device health data hub for structured records and cross-app sharing.
- Use a companion app for rich analytics and backend sync; communicate via Health Connect where available and/or a dedicated channel (Wearable Data Layer / BLE).

See also [[c-android]].

### Health Services Setup

- Register measure callbacks for required types via the Health Services clients (see official docs for the exact API).
- Prefer batching and timestamps from Health Services instead of polling raw sensors.

### Power Management

- Restrict foreground services to active workout sessions; rely on passive monitoring otherwise.
- Prefer Tiles/Complications to show key metrics without keeping an `Activity` running.
- Use system-friendly background scheduling (e.g., WorkManager) for periodic aggregation and upload; do not bypass platform limits.

### Health Connect Integration

- Obtain a `HealthConnectClient` instance and request granular read/write permissions for specific record types (e.g., `HeartRateRecord`) using `PermissionController`.
- Before writing, check granted permissions; if missing, launch the Health Connect permission flow using the official `Activity` Result contract or intent from the SDK.
- Insert structured `Record` objects (e.g., `HeartRateRecord`, `StepsRecord`) via `insertRecords`, preserving source timestamps.
- For phone sync:
  - Use Health Connect on both devices plus companion logic where applicable, or
  - Use Data Layer / custom APIs for near real-time scenarios or when Health Connect is unavailable.

### Policy and Testing

- Request only necessary health-related permissions and clearly justify their use to comply with Google Play policies.
- Handle connectivity loss gracefully: buffer locally and sync when the phone/network becomes available.
- Use Health Services emulator/virtual sensors and Health Connect CLI tooling for automated and manual testing.

### UX

- Offer clear options for data collection intensity (workout-only / periodic / continuous) along with battery impact.
- Show sensor/monitoring status indicators and warnings for high power usage.
- Be transparent about what data is stored in Health Connect and which apps can access it.

---

## Дополнительные Вопросы (RU)
- Как передавать данные в real-time на телефон (BLE/Companion) при отсутствии Health Connect?
- Какие ограничения вводит Health Connect на историю данных и ревокацию разрешений?
- Как использовать Tiles/Complications для отображения данных без запуска `Activity`?

## Follow-ups
- How to stream data in real time to the phone (BLE/Companion) when Health Connect is unavailable?
- What constraints does Health Connect impose on data history and permission revocation?
- How to use Tiles/Complications to display data without starting an `Activity`?

## Ссылки (RU)
- https://developer.android.com/training/wearables/health-services
- https://developer.android.com/guide/health-and-fitness/health-connect

## References
- https://developer.android.com/training/wearables/health-services
- https://developer.android.com/guide/health-and-fitness/health-connect

## Related Questions

- [[q-android-auto-guidelines--android--hard]]
