---
id: android-645
title: CallStyle & Foreground Service Compliance / CallStyle и требования foreground-сервисов
aliases:
  - CallStyle & Foreground Service Compliance
  - CallStyle и требования foreground-сервисов
topic: android
subtopics:
  - communication
  - notifications
  - foreground-services
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-communication-surfaces
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/notifications
  - android/foreground-service
  - callstyle
  - difficulty/hard
sources:
  - url: https://developer.android.com/develop/ui/views/notifications/callstyle
    note: CallStyle documentation
  - url: https://developer.android.com/about/versions/13/behavior-changes-13#post-notification-runtime-permission
    note: Foreground service changes
  - url: https://developer.android.com/about/versions/14/behavior-changes-14#foreground-services
    note: Android 14 FGS policy
---

# Вопрос (RU)
> Как реализовать звонковые уведомления с использованием CallStyle и соблюсти требования foreground-сервисов: категории FGS, индикаторы приватности (микрофон/камера), разрешения и тестирование?

# Question (EN)
> How do you implement CallStyle notifications while complying with foreground-service requirements, including FGS types, privacy indicators, permissions, and testing?

---

## Ответ (RU)

### 1. Foreground `Service` классификация

- Android 13+ требует указать `foregroundServiceType` (`dataSync`, `mediaProjection`, `camera`, `microphone`, `phoneCall`).
- Для звонков → `FOREGROUND_SERVICE_TYPE_PHONE_CALL` (и `camera`/`microphone`, если видеозвонок).
- Добавьте в манифест `android.permission.FOREGROUND_SERVICE_PHONE_CALL`.

### 2. CallStyle Notification

- Стартуйте FGS → `startForeground(NOTIFICATION_ID, notification, FOREGROUND_SERVICE_TYPE_PHONE_CALL)`.
- Постройте уведомление:

```kotlin
val personCaller = Person.Builder().setName("Alex").setIcon(icon).build()
val callStyle = NotificationCompat.CallStyle.forIncomingCall(personCaller, answerIntent, declineIntent)
val notification = NotificationCompat.Builder(context, CHANNEL_CALLS)
    .setStyle(callStyle)
    .setSmallIcon(R.drawable.ic_call)
    .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
    .setCategory(Notification.CATEGORY_CALL)
    .build()
```

- Используйте `forIncomingCall`, `forOngoingCall`, `forScreeningCall` соответствующее сценарию.

### 3. Privacy Indicators и mic/camera access

- Android 12+: при использовании mic/camera отображаются индикаторы (green/orange). Убедитесь, что уведомление объясняет пользователю использование.
- Предоставьте \"Mute camera/mic\" actions в уведомлении.
- Обрабатывайте runtime permission (`RECORD_AUDIO`, `CAMERA`); без них уведомление должно адаптироваться.

### 4. Background ограничения

- Перед показом уведомления → `POST_NOTIFICATIONS` разрешение (Android 13).
- Incoming call: используйте `fullScreenIntent` только если соответствует policy (incoming, high priority). В других случаях → обычное уведомление.
- Ограничить длительность FGS: останавливайте, когда звонок завершён, чтобы избежать ANR/penalties.

### 5. Тестирование и политики

- CTS tests (Android 12-14) → проверяют использование FGS.
- Espresso/Automation: симулируйте входящий звонок, проверяйте доступность действий.
- Policy compliance: описать функционал в Play Console (вопросы о FGS), иметь user opt-in.

### 6. Интеграция с системными сервисами

- Используйте `ConnectionService`/`SelfManagedConnectionService` для deep integration (телефония).
- Для VoIP → `ROLE_DIALER` (если требуется). Учитывайте ограничения self-managed apps.
- Логируйте события (answer, decline, mute), чтобы анализировать UX.

### 7. Degradation & fallback

- На Android <11 → fallback к `CATEGORY_CALL` без CallStyle.
- Когда пользователь отключил разрешение bubble/call notifications → обеспечить in-app предупреждение.
- Учтите multi-device: синхронизируйте статус звонка с backend.

---

## Answer (EN)

- Declare appropriate foreground-service types (`phoneCall`, `camera`, `microphone`), request corresponding permissions, and start the service with a CallStyle notification.
- Configure CallStyle for incoming/ongoing/screening calls, providing answer/decline actions and immediate FGS behavior.
- Respect privacy indicators and runtime permissions, offering inline mute controls and adapting when mic/camera access is denied.
- Handle notification permissions, avoid overusing full-screen intents, and stop the FGS promptly after the call ends.
- Test across API levels, satisfy Play policies (FGS declarations), and integrate with connection services when deeper telephony integration is required.
- Plan fallbacks for older devices and disabled permissions, and synchronize call states across devices/backends.

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
