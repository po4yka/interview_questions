---
id: android-644
title: Conversation Notifications & Bubbles / Уведомления и Bubbles для переписки
aliases:
  - Conversation Notifications & Bubbles
  - Уведомления и Bubbles для переписки
topic: android
subtopics:
  - communication
  - notifications
  - bubbles
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
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/notifications
  - android/bubbles
  - communication
  - difficulty/hard
sources:
  - url: https://developer.android.com/develop/ui/views/notifications/conversation
    note: Conversation notifications guide
  - url: https://developer.android.com/about/versions/11/features/bubbles
    note: Bubbles feature overview
---

# Вопрос (RU)
> Как реализовать и поддерживать conversation notifications и bubbles: shortcuts, MessagingStyle, человекоориентированные уведомления, ограничения Android 11–14 и аналитика?

# Question (EN)
> How do you implement and maintain conversation notifications and bubbles, covering shortcuts, MessagingStyle, person-centric metadata, Android 11–14 limitations, and analytics?

---

## Ответ (RU)

### 1. Модель данных

- Определите `Person` с avatar/URI.
- Создайте `ShortcutInfoCompat` (ID переписки) и зарегистрируйте через `ShortcutManagerCompat.pushDynamicShortcut`.
- Связывайте уведомления с shortcut (`setShortcutId`) + `setLocusId`.

### 2. Conversation notification

- Используйте `NotificationCompat.MessagingStyle`:

```kotlin
val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setStyle(
        NotificationCompat.MessagingStyle(currentUser)
            .addMessage("Hi!", timestamp, otherPerson)
            .setConversationTitle("Chat with Alex")
    )
    .setShortcutId(conversationId)
    .setCategory(Notification.CATEGORY_MESSAGE)
    .setPerson(otherPerson)
    .setSmallIcon(R.drawable.ic_message)
    .setShowWhen(true)
    .setAllowSystemGeneratedContextualActions(true)
    .build()
```

- `setAllowSystemGeneratedContextualActions(true)` → smart replies/actions.
- Включайте `setGroupConversation(true)` для групп.

### 3. Bubbles

- Требует `BUBBLE_PERMISSION` (Android 14) и user opt-in.
- Notification builder: `setBubbleMetadata(
    NotificationCompat.BubbleMetadata.Builder(pendingIntent, icon).setDesiredHeight(600).build()
)`.
- Overlay activity (`documentLaunchMode="always"`, `android:resizeableActivity="true"`).
- Handle `BubbleCallback`: lifecycle events, collapse/dismiss analytics.

### 4. Background limits

- Уважайте `POST_NOTIFICATIONS` runtime permission.
- Foreground Service: для ongoing calls/chat heads: `FOREGROUND_SERVICE_MICROPHONE/CAMERA`.
- Android 13+: уведомления для new installs отключены по умолчанию → onboarding flow.

### 5. Аналитика и UX

- Логируйте open rate, bubble usage, smart reply adoption.
- Отправляйте `NotificationManager.getActiveNotifications()` → ревизия старых уведомлений.
- A/B тест: context actions, avatar placement, summary notifications.

### 6. Тестирование

- CTS emulator API 30-34: проверяйте bubbles behaviour.
- Espresso: `NotificationListenerService` для assert.
- UI Automation: `UiDevice.openNotification()` + `executeShellCommand("cmd notification expand-notifications")`.

### 7. Политики и приватность

- Чувствительные данные → скрывать из уведомления при lock screen (`setVisibility(NotificationCompat.VISIBILITY_PRIVATE)`).
- Предоставляйте настройки в app (mute thread, disable bubble).
- Соблюдайте Android policy: только реальные conversations → иначе риск rejection.

---

## Answer (EN)

- Model conversations with `Person` objects and dynamic shortcuts, linking notifications via shortcut IDs and locus IDs.
- Build `MessagingStyle` notifications with rich metadata, smart suggestions, and conversation categories.
- Configure bubble metadata, manage overlay activities, and handle bubble lifecycle callbacks (permission opt-in, dismissal).
- Respect notification runtime permissions, foreground service requirements, and evolving limits across Android 11–14.
- Track analytics on opens, bubble usage, and smart replies; offer in-app preferences and comply with privacy policies.
- Test across API levels using Notification listeners, UI automation, and ensure proper behavior on lock screens and summary notifications.

---

## Follow-ups
- Как синхронизировать статус прочтения между устройствами и bubbles?
- Какие UX паттерны для групповых чатов и mentions?
- Как обрабатывать авторизацию/реактивацию после долго отсутствия приложения (Doze, standby)?

## References
- [[c-communication-surfaces]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/develop/ui/views/notifications/conversation
