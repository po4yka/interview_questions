---
id: android-644
title: Conversation Notifications & Bubbles / Уведомления и Bubbles для переписки
aliases:
- Conversation Notifications & Bubbles
- Уведомления и Bubbles для переписки
topic: android
subtopics:
- notifications
- ui-navigation
- ui-state
question_kind: theory
difficulty: hard
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-communication-surfaces
- q-advanced-share-sheet-shortcuts--android--hard
- q-dagger-build-time-optimization--android--medium
- q-data-sync-unstable-network--android--hard
- q-local-notification-exact-time--android--medium
created: 2025-11-02
updated: 2025-11-10
tags:
- android/notifications
- android/ui-navigation
- android/ui-state
- difficulty/hard
sources:
- https://developer.android.com/about/versions/11/features/bubbles
- https://developer.android.com/develop/ui/views/notifications/conversation
anki_cards:
- slug: android-644-0-en
  language: en
  anki_id: 1768366348550
  synced_at: '2026-01-23T16:45:06.355255'
- slug: android-644-0-ru
  language: ru
  anki_id: 1768366348576
  synced_at: '2026-01-23T16:45:06.356176'
---
# Вопрос (RU)
> Как реализовать и поддерживать conversation notifications и bubbles: shortcuts, MessagingStyle, человекоориентированные уведомления, ограничения Android 11–14 и аналитика?

# Question (EN)
> How do you implement and maintain conversation notifications and bubbles, covering shortcuts, MessagingStyle, person-centric metadata, Android 11–14 limitations, and analytics?

---

## Ответ (RU)

### 1. Модель Данных

- Определите для участников `Person` с именем и avatar/URI (для self-пользователя и собеседников).
- Создайте `ShortcutInfoCompat` с постоянным ID переписки и зарегистрируйте через `ShortcutManagerCompat.pushDynamicShortcut` (или pinned shortcuts).
- Связывайте уведомления с shortcut через `setShortcutId(conversationId)` и при необходимости `setLocusId` для улучшения интеграции с системным поиском/recents.

### 2. Conversation Notification

- Используйте `NotificationCompat.MessagingStyle` для системно распознаваемых conversation notifications:

```kotlin
val style = NotificationCompat.MessagingStyle(currentUser)
    .setConversationTitle("Chat with Alex")
    .setGroupConversation(false) // true для групповых чатов
    .addMessage("Hi!", timestamp, otherPerson)

val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setStyle(style)
    .setShortcutId(conversationId) // conversationId соответствует зарегистрированному shortcut
    .setCategory(Notification.CATEGORY_MESSAGE)
    .setSmallIcon(R.drawable.ic_message)
    .setShowWhen(true)
    .setAllowSystemGeneratedContextualActions(true) // smart replies/actions
    .addPerson(otherPerson) // добавляйте участников как Person
    .build()
```

- Для групповых чатов используйте `setGroupConversation(true)` и добавляйте всех участников через `addPerson`.
- Убедитесь, что `shortcutId` существует, и что уведомление помечено как категория MESSAGE для корректной обработки как беседы.

### 3. Bubbles

- Начиная с Android 11, платформенные bubbles предназначены для conversation notifications, связанных с корректным shortcut и person-метаданными; использование `MessagingStyle`, shortcut и `Person` делает поведение предсказуемым и соответствует рекомендациям.
- Требуется согласие пользователя (переключатель bubbles для приложения/диалога в системных настройках). Явного отдельного манифестного разрешения для bubbles не используется, но фактическая доступность зависит от версии и системных настроек.
- Используйте `NotificationCompat.BubbleMetadata`:

```kotlin
val bubbleMetadata = NotificationCompat.BubbleMetadata.Builder(pendingIntent, icon)
    .setDesiredHeight(600)
    .setAutoExpandBubble(false)
    .setSuppressNotification(false)
    .build()

val bubbleNotification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setStyle(style)
    .setShortcutId(conversationId)
    .setCategory(Notification.CATEGORY_MESSAGE)
    .setBubbleMetadata(bubbleMetadata)
    .setSmallIcon(R.drawable.ic_message)
    .build()
```

- Активити для bubble должна поддерживать ресайзинг (`android:resizeableActivity="true"`) и корректное поведение в плавающем окне; `documentLaunchMode` настраивайте так, чтобы каждая беседа открывалась предсказуемо (например, отдельный таск для каждой беседы при необходимости).
- Обрабатывайте события сворачивания/закрытия через callbacks/интенты и фиксируйте это в аналитике.

### 4. Background Limits

- Соблюдайте `POST_NOTIFICATIONS` runtime permission (Android 13+). При отсутствии разрешения не показывайте обычные уведомления/бабблы для чата и уважайте выбор пользователя.
- Если используется Foreground `Service` (например, для ongoing calls, screen sharing, записи аудио/видео), применяйте соответствующие типы (`FOREGROUND_SERVICE_MICROPHONE`, `FOREGROUND_SERVICE_CAMERA` и т.д.) и связанную `CATEGORY_CALL`/`ongoing` нотификацию. Сами по себе bubbles для чата не требуют FGS.
- Android 13+: уведомления для новых установок по умолчанию отключены → нужен onboarding flow и явный запрос `POST_NOTIFICATIONS`.

### 5. Аналитика И UX

- Логируйте:
  - open rate уведомлений и bubble (открытие activity из уведомления/баббла),
  - частоту использования bubbles vs обычных уведомлений,
  - использование smart replies и contextual actions.
- `NotificationManager.getActiveNotifications()` используйте только для чтения текущих активных уведомлений (не как исторический лог) и для корректной чистки/обновления.
- Проводите A/B тестирование: контекстные действия, формат заголовка, аватарки, summary notifications, но без нарушения ожиданий системы.

### 6. Тестирование

- Тестируйте на эмуляторах/устройствах с API 30+ (Android 11–14), проверяя поведение conversation notifications и bubbles, в том числе системные настройки bubbles.
- Используйте тестовый `NotificationListenerService` для проверки содержимого и свойств уведомлений.
- Для end-to-end тестов применяйте UI Automation: `UiDevice.openNotification()` и `executeShellCommand("cmd notification expand-notifications")` / управление bubbles.

### 7. Политики И Приватность

- Чувствительные данные скрывайте на lock screen через `setVisibility(NotificationCompat.VISIBILITY_PRIVATE)` и соответствующие настройки пользователя.
- Предоставляйте в приложении настройки для бесед: отключение уведомлений для треда, отключение bubbles, уровни важности.
- Соблюдайте требования Play/Android policy: используйте bubbles и conversation surfaces для people-centric коммуникаций (личные и групповые чаты, звонки и т.п.), а не для агрессивного промо или нерелевантного контента, иначе возможен rejection.

---

## Answer (EN)

### 1. Data Model

- Define `Person` objects for all participants (including the self user) with names and avatar URIs.
- Create `ShortcutInfoCompat` with a stable conversation ID and register via `ShortcutManagerCompat.pushDynamicShortcut` (or pinned shortcuts).
- Link notifications to shortcuts via `setShortcutId(conversationId)` and optionally `setLocusId` for better integration with system search/recents.

### 2. Conversation Notification

- Use `NotificationCompat.MessagingStyle` so the system recognizes your notifications as conversations:

```kotlin
val style = NotificationCompat.MessagingStyle(currentUser)
    .setConversationTitle("Chat with Alex")
    .setGroupConversation(false) // true for group chats
    .addMessage("Hi!", timestamp, otherPerson)

val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setStyle(style)
    .setShortcutId(conversationId) // conversationId must match an existing shortcut
    .setCategory(Notification.CATEGORY_MESSAGE)
    .setSmallIcon(R.drawable.ic_message)
    .setShowWhen(true)
    .setAllowSystemGeneratedContextualActions(true) // smart replies/actions
    .addPerson(otherPerson) // add all participants as Person
    .build()
```

- For group chats, use `setGroupConversation(true)` and add all participants via `addPerson`.
- Ensure the `shortcutId` exists and the notification is marked with `CATEGORY_MESSAGE` so the system treats it as a conversation.

### 3. Bubbles

- On Android 11+, platform bubbles are intended for conversation notifications backed by proper shortcuts and person-centric metadata; using `MessagingStyle`, shortcuts, and `Person` makes behavior predictable and aligned with guidelines.
- Respect user control: bubbles are enabled/disabled per app/conversation in system settings; there is no separate manifest permission, but actual availability depends on OS version and user settings.
- Use `NotificationCompat.BubbleMetadata`:

```kotlin
val bubbleMetadata = NotificationCompat.BubbleMetadata.Builder(pendingIntent, icon)
    .setDesiredHeight(600)
    .setAutoExpandBubble(false)
    .setSuppressNotification(false)
    .build()

val bubbleNotification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setStyle(style)
    .setShortcutId(conversationId)
    .setCategory(Notification.CATEGORY_MESSAGE)
    .setBubbleMetadata(bubbleMetadata)
    .setSmallIcon(R.drawable.ic_message)
    .build()
```

- The bubble activity must support resizing (`android:resizeableActivity="true"`) and behave correctly in a floating window; configure `documentLaunchMode` so each conversation opens predictably (e.g., separate task per conversation if needed).
- Handle bubble collapse/close events via callbacks/intents and record them in analytics.

### 4. Background Limits

- Honor the `POST_NOTIFICATIONS` runtime permission (Android 13+). If it is not granted, do not show regular chat notifications/bubbles and respect the user's choice.
- When using a foreground `Service` (e.g., for ongoing calls, screen sharing, audio/video recording), use the correct foreground service types (such as `FOREGROUND_SERVICE_MICROPHONE`, `FOREGROUND_SERVICE_CAMERA`) and an associated `CATEGORY_CALL`/ongoing notification. Regular chat bubbles do not require a foreground service.
- For Android 13+, notifications are disabled by default for new installs → implement onboarding and explicitly request `POST_NOTIFICATIONS`.

### 5. Analytics and UX

- Track:
  - open rate from notifications and bubbles (opening the activity from notification/bubble),
  - frequency of bubble usage vs regular notifications,
  - usage of smart replies and contextual actions.
- Use `NotificationManager.getActiveNotifications()` only to inspect currently active notifications (not as historical storage) and to clean up/update them correctly.
- Run A/B tests on contextual actions, title format, avatars, summary notifications, etc., while keeping behavior consistent with system expectations.

### 6. Testing

- Test on emulators/devices with API 30+ (Android 11–14), verifying conversation flags, shortcut links, and bubble behavior, including system bubble settings.
- Use a test `NotificationListenerService` to inspect notification content and properties.
- For end-to-end tests, use UI automation: `UiDevice.openNotification()` and shell commands like `executeShellCommand("cmd notification expand-notifications")`, plus bubble interaction checks.

### 7. Policy and Privacy

- Hide sensitive information on the lock screen using `setVisibility(NotificationCompat.VISIBILITY_PRIVATE)` and respect user lockscreen preferences.
- Provide in-app controls per conversation: mute thread, disable bubbles, configure importance levels.
- Comply with Play/Android policies: use bubbles and conversation surfaces for people-centric communication (direct and group chats, calls, etc.), not for aggressive promotion or irrelevant content, to avoid rejection.

---

## Дополнительные Вопросы (RU)
- Как синхронизировать статус прочтения между устройствами и bubbles?
- Какие UX паттерны для групповых чатов и mentions?
- Как обрабатывать авторизацию/реактивацию после долгого отсутствия приложения (Doze, standby)?

## Follow-ups
- How to synchronize read status across devices and bubbles?
- What UX patterns to use for group chats and mentions?
- How to handle authentication/reactivation after long inactivity (Doze, standby)?

## Ссылки (RU)
- [[c-communication-surfaces]]
- https://developer.android.com/develop/ui/views/notifications/conversation

## References
- [[c-communication-surfaces]]
- https://developer.android.com/develop/ui/views/notifications/conversation

## Связанные Вопросы (RU)

- [[c-communication-surfaces]]

## Related Questions

- [[c-communication-surfaces]]
