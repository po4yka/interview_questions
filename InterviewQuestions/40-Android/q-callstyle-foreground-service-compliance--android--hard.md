---
id: android-645
title: CallStyle & Foreground Service Compliance / CallStyle и требования foreground-сервисов
aliases: [CallStyle & Foreground Service Compliance, CallStyle и требования foreground-сервисов]
topic: android
subtopics:
  - background-execution
  - notifications
  - service
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-communication-surfaces
  - q-android-service-types--android--easy
  - q-background-vs-foreground-service--android--medium
  - q-foreground-service-types--android--medium
  - q-when-can-the-system-restart-a-service--android--medium
created: 2025-11-02
updated: 2025-11-11
tags: [android/background-execution, android/notifications, android/service, difficulty/hard]
sources:
  - "https://developer.android.com/about/versions/13/behavior-changes-13#post-notification-runtime-permission"
  - "https://developer.android.com/about/versions/14/behavior-changes-14#foreground-services"
  - "https://developer.android.com/develop/ui/views/notifications/callstyle"

date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Как реализовать звонковые уведомления с использованием CallStyle и соблюсти требования foreground-сервисов: категории FGS, индикаторы приватности (микрофон/камера), разрешения и тестирование?

# Question (EN)
> How do you implement CallStyle notifications while complying with foreground-service requirements, including FGS types, privacy indicators, permissions, and testing?

---

## Ответ (RU)

### 1. Foreground `Service` Классификация

- На Android 13+ необходимо указывать один или несколько корректных `foregroundServiceType` (например: `phoneCall`, `camera`, `microphone`, и др. в соответствии с официальным списком для вашей функциональности).
- Для звонков → обязательно `FOREGROUND_SERVICE_TYPE_PHONE_CALL`; для видеозвонка дополнительно `FOREGROUND_SERVICE_TYPE_CAMERA` и/или `FOREGROUND_SERVICE_TYPE_MICROPHONE`, если реально используете камеру/микрофон.
- В манифесте для сервиса укажите соответствующие типы через `android:foregroundServiceType="phoneCall|camera|microphone"` и добавьте `android.permission.FOREGROUND_SERVICE_PHONE_CALL`, а при необходимости `android.permission.FOREGROUND_SERVICE_CAMERA` / `android.permission.FOREGROUND_SERVICE_MICROPHONE` согласно используемым типам.
- Для VoIP также учитывайте `RECORD_AUDIO` (runtime) и, при видеозвонках, `CAMERA` для доступа к микрофону/камере.
- На Android 14+ соблюдайте ограничения FGS: используйте только релевантные типы, не запускайте FGS без активного звонка или подготовительного сценария, который явно разрешён политиками.

### 2. CallStyle Notification

- Стартуйте FGS с корректным типом(типами):
  `startForeground(NOTIFICATION_ID, notification, FOREGROUND_SERVICE_TYPE_PHONE_CALL)`.
- Постройте уведомление:

```kotlin
val personCaller = Person.Builder().setName("Alex").setIcon(icon).build()
val callStyle = NotificationCompat.CallStyle.forIncomingCall(
    personCaller,
    answerIntent,
    declineIntent
)
val notification = NotificationCompat.Builder(context, CHANNEL_CALLS)
    .setStyle(callStyle)
    .setSmallIcon(R.drawable.ic_call)
    .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
    .setCategory(Notification.CATEGORY_CALL)
    .build()
```

- Используйте `forIncomingCall`, `forOngoingCall`, `forScreeningCall` в зависимости от сценария. Убедитесь, что pending intent'ы корректно обрабатываются сервисом/`ConnectionService` и приводят к обновлению состояния звонка и уведомления.

### 3. Privacy Indicators И mic/camera Access

- Android 12+: при использовании микрофона/камеры автоматически отображаются индикаторы приватности. Убедитесь, что поведение приложения прозрачно для пользователя (UI/описание объясняют использование).
- При необходимости предоставьте действия "Mute camera/mic" в уведомлении или UI звонка.
- Обрабатывайте runtime-разрешения (`RECORD_AUDIO`, `CAMERA`); при их отсутствии адаптируйте опыт (например, только входящий уведомительный экран до выдачи разрешения; не пытайтесь использовать ресурсы без разрешения).

### 4. Background Ограничения

- Перед показом уведомлений на Android 13+ запрашивайте `POST_NOTIFICATIONS` (если это не системный сценарий, освобождённый от разрешения). Корректно обрабатывайте случай отказа: звонковое уведомление не может быть показано без разрешения, продумайте in-app UX.
- Incoming call: используйте `fullScreenIntent` только для реальных входящих звонков и в соответствии с официальной policy; для остальных кейсов используйте обычные уведомления.
- Ограничивайте длительность работы FGS: останавливайте сервис, когда звонок завершён или становится неактуальным, чтобы избежать нарушений FGS-политик и возможных санкций. Не удерживайте FGS в неактивном состоянии (ожидание, idle) дольше, чем это оправдано политиками платформы/Play.

### 5. Тестирование И Политики

- Тестируйте поведение на разных API уровнях (особенно 12+), включая отсутствие/отзыв разрешений, запрет `POST_NOTIFICATIONS` и разные состояния активности.
- Инструментальные/автоматизированные тесты: симулируйте входящий звонок, проверяйте CallStyle, доступность действий (answer/decline/mute), работу full-screen intent, корректное завершение FGS и поведение при невозможности стартовать FGS.
- Policy compliance: корректно декларируйте FGS-типы и сценарии в Play Console, имейте понятное user-facing обоснование использования, избегайте неправомерного удержания foreground-сервисов и несоответствия заявленных и фактических типов.

### 6. Интеграция С Системными Сервисами

- Используйте `ConnectionService` для интеграции с телефонией и системным UI звонков, учитывая его требования и ограничения.
- `SelfManagedConnectionService` применяйте только если вы строите полностью управляемое своим UI решение; учтите строгие ограничения для self-managed приложений (ограничения по overlay, взаимодействию с системным dialer и т.п.) и то, что такие приложения не могут стать системным dialer'ом по умолчанию.
- Для VoIP-приложений `ROLE_DIALER` требуется только если вы хотите стать системным dialer'ом по умолчанию; для большинства VoIP-сценариев достаточно корректной интеграции через ConnectionService и CallStyle.
- Логируйте ключевые события (answer, decline, missed, mute), чтобы анализировать качество UX и корректность логики.

### 7. Degradation & Fallback

- На старых версиях Android `NotificationCompat.CallStyle` обеспечивает совместимость: визуальное оформление может быть менее богатым, но базовый сценарий звонкового уведомления сохраняется. При необходимости добавьте fallback на обычное уведомление с `CATEGORY_CALL`.
- Когда пользователь отключил относящиеся разрешения (уведомления, overlay/full-screen, bubbles) или специальные привилегии звонков, обеспечьте понятное in-app предупреждение и альтернативный UX.
- Для multi-device сценариев синхронизируйте статус звонка с backend так, чтобы уведомления и состояние звонка были консистентны.

### Краткая Версия (RU)

- Укажите корректные типы foreground-сервисов и соответствующие разрешения; на Android 14+ строго следите за соответствием типов и сценариев.
- Используйте `NotificationCompat.CallStyle` с подходящим вариантом (incoming/ongoing/screening) и `CATEGORY_CALL`.
- Соблюдайте индикаторы приватности и runtime-разрешения для микрофона/камеры.
- Запросите `POST_NOTIFICATIONS` на Android 13+, используйте full-screen только для реальных звонков и корректно обрабатывайте отказ.
- Останавливайте FGS сразу после завершения звонка и соблюдайте Play policy.

### Детальная Версия (RU)

#### Требования

- Функциональные:
  - Звонковое уведомление с действиями answer/decline/mute.
  - Поддержка входящих и текущих звонков, при необходимости видеозвонков.
  - Интеграция с `ConnectionService` при требовании системного UI.
- Нефункциональные:
  - Соблюдение FGS-политик и ограничений батареи.
  - Прозрачность приватности (индикаторы, понятные объяснения).
  - Надежность на разных API-уровнях.

#### Архитектура

- Компоненты:
  - Foreground `Service` с корректными `foregroundServiceType`.
  - Модуль уведомлений, построенный на `NotificationCompat.CallStyle`.
  - Интеграция с `ConnectionService` / `SelfManagedConnectionService` (по необходимости, с соблюдением их ограничений).
  - Модуль разрешений (`POST_NOTIFICATIONS`, `RECORD_AUDIO`, `CAMERA`).
- Поток данных:
  - Входящий звонок → запуск FGS → построение CallStyle уведомления → (опциональный) full-screen UI.
  - Действия пользователя → обработка в FGS/ConnectionService → обновление уведомления и завершение FGS при окончании звонка.

---

## Answer (EN)

- Declare appropriate foreground service types (e.g., `phoneCall`, and `camera`/`microphone` for video calls), set `android:foregroundServiceType` on the service accordingly, add the corresponding FGS permissions in the manifest, and request runtime permissions like `RECORD_AUDIO`/`CAMERA` when needed. On Android 14+ ensure that the declared types and actual usage match the allowed call scenarios.
- Start the foreground service with a CallStyle notification using the correct FGS type(s), and use the appropriate CallStyle variant for incoming/ongoing/screening calls, with answer/decline and mute actions as needed. Ensure that your pending intents are handled by the service/ConnectionService and correctly update call state and the notification.
- Respect privacy indicators on Android 12+, clearly communicate mic/camera usage, and adapt the experience when permissions are missing (e.g., show the incoming call UI but do not access audio/video until granted).
- Handle notification permissions (Android 13+ `POST_NOTIFICATIONS`), handle denial gracefully (no notification UI if permission is missing), use full-screen intents only for legitimate incoming-call scenarios, and stop the foreground service promptly when the call ends or is no longer relevant, avoiding long idle foreground usage.
- Test across API levels and permission states (including revoked `POST_NOTIFICATIONS`), verify CallStyle behavior, full-screen intent handling, FGS start/stop flows (including failure cases on newer OS versions), and ensure Play policy compliance by correctly declaring FGS types and providing clear justifications.
- Integrate with `ConnectionService` for deeper telephony integration when appropriate, and use `SelfManagedConnectionService` only for fully self-managed calling apps while respecting its stricter constraints (cannot become the default dialer, must follow overlay/interaction rules). Only request `ROLE_DIALER` if you truly need to become the default dialer; most VoIP apps can rely on ConnectionService + CallStyle.
- Provide fallbacks for older devices or restricted capabilities (e.g., simpler `CATEGORY_CALL` notifications) and keep call state synchronized across devices/backends for a consistent user experience.

### Short Version (EN)

- Set correct FGS types and permissions; on Android 14+ ensure strong alignment between declared types and actual usage.
- Use `NotificationCompat.CallStyle` with appropriate variants and `CATEGORY_CALL`.
- Honor privacy indicators and mic/camera runtime permissions.
- Request `POST_NOTIFICATIONS` on Android 13+, use full-screen only for real calls, and handle permission denial.
- Stop FGS as soon as the call ends and stay compliant with Play policies.

### Detailed Version (EN)

#### Requirements

- Functional:
  - Call-style notification with answer/decline/mute actions.
  - Support for incoming and ongoing calls, including video when needed.
  - Optional integration with `ConnectionService` for system UI.
- Non-functional:
  - Compliance with FGS policies and battery constraints.
  - Clear privacy behavior (indicators, explanations).
  - Reliability across API levels.

#### Architecture

- Components:
  - Foreground `Service` with correct `foregroundServiceType` values.
  - Notification module based on `NotificationCompat.CallStyle`.
  - Integration with `ConnectionService` / `SelfManagedConnectionService` where appropriate and compliant with their restrictions.
  - Permission handling module (`POST_NOTIFICATIONS`, `RECORD_AUDIO`, `CAMERA`).
- Data flow:
  - Incoming call → start FGS → build CallStyle notification → optional full-screen UI.
  - User actions → handled in FGS/ConnectionService → update notification and stop FGS when the call finishes.

---

## Follow-ups
- Как реализовать self-managed ConnectionService и синхронизацию с системным dialer?
- Какие метрики качества звонков важно собирать (answer rate, drop rate)?
- Как обрабатывать CallStyle вместе с bubbles для ongoing conversation?

## References
- [[c-communication-surfaces]]
- https://developer.android.com/develop/ui/views/notifications/callstyle

## Related Questions

- [[c-communication-surfaces]]
