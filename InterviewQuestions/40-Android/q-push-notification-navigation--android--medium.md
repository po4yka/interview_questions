---
id: android-305
title: Push Notification Navigation / Навигация из push уведомлений
aliases: [FCM Navigation, Navigation from Notifications, Push Notification Navigation, Навигация из push уведомлений]
topic: android
subtopics:
  - notifications
  - ui-navigation
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-compose-navigation
  - q-activity-navigation-how-it-works--android--medium
  - q-compose-navigation-advanced--android--medium
  - q-how-dialog-differs-from-other-navigation--android--medium
  - q-how-navigation-is-implemented-in-android--android--medium
  - q-what-navigation-methods-do-you-know--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-11
tags: [android/notifications, android/ui-navigation, deeplink, difficulty/medium, fcm, navigation, notifications]

date created: Saturday, November 1st 2025, 12:47:01 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---

# Вопрос (RU)

> Как открыть конкретную `Activity` или `Fragment` из push-уведомления?

# Question (EN)

> How to open a specific `Activity` or `Fragment` from a push notification?

---

## Ответ (RU)

**Подход**: Настроить FCM service для создания PendingIntent с данными навигации, обработать `Intent` в `Activity` через `onCreate()`/`onNewIntent()` (при `launchMode="singleTop"` или эквивалентном сценарии переиспользования `Activity`).

**Сложность**: Константные накладные расходы (Time O(1), Space O(1)) относительно стандартного клика по уведомлению.

### 1. FCM `Service` С Навигационными Данными

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onMessageReceived(message: RemoteMessage) {
        val screen = message.data["screen"] ?: "home"
        val itemId = message.data["item_id"]?.toIntOrNull()

        showNotification(
            title = message.notification?.title ?: "",
            screen = screen,
            itemId = itemId
        )
    }

    private fun showNotification(title: String, screen: String, itemId: Int?) {
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra(EXTRA_SCREEN, screen)
            itemId?.let { putExtra(EXTRA_ITEM_ID, it) }
        }

        val pendingIntent = PendingIntent.getActivity(
            this,
            /* requestCode = */ 0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        NotificationManagerCompat.from(this).notify(/* notificationId = */ 0, notification)
    }
}
```

✅ **Правильно**: Использование data payload для передачи параметров навигации.
✅ **Правильно**: `FLAG_IMMUTABLE` для `PendingIntent` (Android 12+).
❌ **Ограничение**: "Чистый" notification payload, обрабатываемый напрямую FCM без запуска вашего кода, ограничивает кастомизацию клика; для гибкой навигации используйте data-only сообщения или deep links/`click_action`.

### 2. Обработка Навигации В MainActivity

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navHost = supportFragmentManager
            .findFragmentById(R.id.nav_host) as NavHostFragment
        navController = navHost.navController

        // Обработка интента для запуска из уведомления.
        // При необходимости можно добавить проверку savedInstanceState,
        // чтобы избежать повторной навигации при пересоздании Activity.
        handleNotificationIntent(intent)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        // Работает, если MainActivity сконфигурирована как singleTop
        // или используется эквивалентное поведение.
        intent?.let { handleNotificationIntent(it) }
    }

    private fun handleNotificationIntent(intent: Intent) {
        val screen = intent.getStringExtra(EXTRA_SCREEN) ?: return
        val hasItemId = intent.hasExtra(EXTRA_ITEM_ID)
        val itemId = if (hasItemId) intent.getIntExtra(EXTRA_ITEM_ID, 0) else null

        when (screen) {
            "detail" -> {
                itemId?.let {
                    navController.navigate(
                        R.id.detailFragment,
                        Bundle().apply { putInt("itemId", it) }
                    )
                }
            }
            "profile" -> navController.navigate(R.id.profileFragment)
        }
    }
}
```

✅ **Правильно**: Обработка в `onNewIntent()` при `launchMode="singleTop"`, когда `Activity` переиспользуется.
✅ **Правильно**: Проверка extras перед навигацией.
❌ **Неправильно**: Полагаться только на `onCreate()` для обработки клика по уведомлению — если `Activity` уже открыта и переиспользуется, новый `Intent` придет в `onNewIntent()`.

### 3. Deep Links Для Навигации

```kotlin
// AndroidManifest.xml
<activity
    android:name=".MainActivity"
    android:launchMode="singleTop">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
            android:scheme="myapp"
            android:host="notification" />
        <!-- при необходимости добавьте path/pathPrefix для detail -->
    </intent-filter>
</activity>

// FCM Service
private fun createDeepLinkIntent(itemId: Int): Intent {
    val uri = Uri.parse("myapp://notification/detail?id=$itemId")
    return Intent(Intent.ACTION_VIEW, uri).apply {
        flags = Intent.FLAG_ACTIVITY_NEW_TASK
        setPackage(packageName)
    }
}
```

✅ **Правильно**: Deep links упрощают навигацию и могут переиспользоваться для web-to-app.
✅ **Правильно**: `setPackage()` предотвращает открытие ссылки в других приложениях.
❌ **Важно**: Для HTTPS App Links отсутствие `autoVerify` / Digital Asset Links не ломает возможность открытия в приложении вообще, но ломает гарантированное "подтвержденное" поведение (verified app links).

### 4. Back `Stack` Для Правильной Навигации (`Activity`-based)

```kotlin
private fun createIntentWithBackStack(itemId: Int): PendingIntent {
    val stackBuilder = TaskStackBuilder.create(this).apply {
        addNextIntent(Intent(this@MyFirebaseMessagingService, MainActivity::class.java))
        addNextIntent(
            Intent(this@MyFirebaseMessagingService, DetailActivity::class.java).apply {
                putExtra("item_id", itemId)
            }
        )
    }

    return stackBuilder.getPendingIntent(
        0,
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
    )
}
```

✅ **Правильно**: `TaskStackBuilder` создает корректный back stack для цепочки `Activity`.
❌ **Замечание**: Переход напрямую на `DetailActivity` без родительского экрана технически возможен, но приведет к тому, что кнопка Back закроет приложение вместо возврата на список; `TaskStackBuilder` решает этот UX-вопрос.

(Если используется Navigation Component и фрагменты внутри одной `Activity`, back stack управляется `NavController`, и `TaskStackBuilder` применяется к `Activity`, а не к отдельным `Fragment`.)

**Объяснение**:
1. FCM `Service` получает сообщение и парсит data payload.
2. Создается `Intent` с extras (screen, itemId) или deep link URI.
3. `PendingIntent` передается в уведомление через `setContentIntent()`.
4. При клике `MainActivity` обрабатывает intent в `onCreate()`/`onNewIntent()` (в зависимости от launchMode/состояния).
5. `NavController` либо навигация между `Activity` выполняет переход на нужный экран с параметрами.

---

## Answer (EN)

**Approach**: Configure FCM service to create a PendingIntent with navigation data, handle the `Intent` in the `Activity` via `onCreate()`/`onNewIntent()` (when using `launchMode="singleTop"` or an equivalent single-activity reuse pattern).

**Complexity**: Constant overhead (Time O(1), Space O(1)) relative to a regular notification click.

### 1. FCM `Service` with Navigation Data

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onMessageReceived(message: RemoteMessage) {
        val screen = message.data["screen"] ?: "home"
        val itemId = message.data["item_id"]?.toIntOrNull()

        showNotification(
            title = message.notification?.title ?: "",
            screen = screen,
            itemId = itemId
        )
    }

    private fun showNotification(title: String, screen: String, itemId: Int?) {
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra(EXTRA_SCREEN, screen)
            itemId?.let { putExtra(EXTRA_ITEM_ID, it) }
        }

        val pendingIntent = PendingIntent.getActivity(
            this,
            /* requestCode = */ 0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        NotificationManagerCompat.from(this).notify(/* notificationId = */ 0, notification)
    }
}
```

✅ **Correct**: Using data payload to pass navigation parameters.
✅ **Correct**: `FLAG_IMMUTABLE` for PendingIntent (Android 12+).
❌ **Limitation**: A pure notification payload handled directly by FCM (without your service running) restricts custom click handling; for flexible navigation, use data-only messages and/or deep links/`click_action`.

### 2. Handle Navigation in MainActivity

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navHost = supportFragmentManager
            .findFragmentById(R.id.nav_host) as NavHostFragment
        navController = navHost.navController

        // Handle launch from notification.
        // Optionally guard with savedInstanceState to avoid duplicate navigation
        // when Activity is recreated.
        handleNotificationIntent(intent)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        // This is invoked when MainActivity is singleTop (or similar setup).
        intent?.let { handleNotificationIntent(it) }
    }

    private fun handleNotificationIntent(intent: Intent) {
        val screen = intent.getStringExtra(EXTRA_SCREEN) ?: return
        val hasItemId = intent.hasExtra(EXTRA_ITEM_ID)
        val itemId = if (hasItemId) intent.getIntExtra(EXTRA_ITEM_ID, 0) else null

        when (screen) {
            "detail" -> {
                itemId?.let {
                    navController.navigate(
                        R.id.detailFragment,
                        Bundle().apply { putInt("itemId", it) }
                    )
                }
            }
            "profile" -> navController.navigate(R.id.profileFragment)
        }
    }
}
```

✅ **Correct**: Handle in `onNewIntent()` when using `launchMode="singleTop"` so new intents from notifications are delivered correctly.
✅ **Correct**: Validate extras before navigation.
❌ **Incorrect**: Relying only on `onCreate()` for notification clicks — when the `Activity` is already running and reused, the new intent is delivered to `onNewIntent()` instead.

### 3. Deep Links for Navigation

```kotlin
// AndroidManifest.xml
<activity
    android:name=".MainActivity"
    android:launchMode="singleTop">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
            android:scheme="myapp"
            android:host="notification" />
        <!-- add path/pathPrefix for detail if needed -->
    </intent-filter>
</activity>

// FCM Service
private fun createDeepLinkIntent(itemId: Int): Intent {
    val uri = Uri.parse("myapp://notification/detail?id=$itemId")
    return Intent(Intent.ACTION_VIEW, uri).apply {
        flags = Intent.FLAG_ACTIVITY_NEW_TASK
        setPackage(packageName)
    }
}
```

✅ **Correct**: Deep links simplify navigation and can be reused for web-to-app.
✅ **Correct**: `setPackage()` prevents opening in other apps.
❌ **Important**: For HTTPS App Links, omitting `autoVerify` / Digital Asset Links does not completely prevent opening in your app, but it breaks verified app-link behavior (no guarantee the link will always resolve to your app).

### 4. Back `Stack` for Proper Navigation (`Activity`-based)

```kotlin
private fun createIntentWithBackStack(itemId: Int): PendingIntent {
    val stackBuilder = TaskStackBuilder.create(this).apply {
        addNextIntent(Intent(this@MyFirebaseMessagingService, MainActivity::class.java))
        addNextIntent(
            Intent(this@MyFirebaseMessagingService, DetailActivity::class.java).apply {
                putExtra("item_id", itemId)
            }
        )
    }

    return stackBuilder.getPendingIntent(
        0,
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
    )
}
```

✅ **Correct**: `TaskStackBuilder` creates a proper back stack for `Activities`.
❌ **Note**: Navigating directly to `DetailActivity` without its parent is technically valid but results in Back closing the app instead of returning to the list; `TaskStackBuilder` is recommended to provide a better UX.

(When using the Navigation Component with a single-`Activity`, multi-`Fragment` setup, `NavController` manages the fragment back stack; `TaskStackBuilder` is for `Activities`, not individual fragment destinations.)

**Explanation**:
1. FCM service receives the message and parses the data payload.
2. Create an `Intent` with extras (screen, itemId) or a deep link URI.
3. Attach a PendingIntent to the notification via `setContentIntent()`.
4. On click, `MainActivity` handles the intent in `onCreate()`/`onNewIntent()` depending on launchMode/state.
5. `NavController` or `Activity`-level navigation moves to the desired screen with the provided parameters.

---

## Дополнительные Вопросы (RU)

- Как обрабатывать уведомления в случаях: приложение убито, в фоне, на переднем плане?
- В чем разница между notification payload и data-only payload?
- Как передавать сложные объекты (не только примитивы) через `Intent` уведомления?
- Как гарантировать, что откроется только одно окно при множественных нажатиях по уведомлению?
- Как тестировать навигацию из push-уведомлений без реального backend?

## Follow-ups

- How to handle notification when app is killed vs in background vs foreground?
- What's the difference between notification payload and data-only payload?
- How to pass complex objects (not just primitives) through notification intent?
- How to ensure only one notification opens even with multiple taps?
- How to test push notification navigation without backend?

## Ссылки (RU)

- [Руководство по уведомлениям Android](https://developer.android.com/develop/ui/views/notifications)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [Deep Links в Navigation Component](https://developer.android.com/guide/navigation/navigation-deep-link)
- [Документация TaskStackBuilder](https://developer.android.com/reference/androidx/core/app/TaskStackBuilder)

## References

- [Android Notification Guide](https://developer.android.com/develop/ui/views/notifications)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [Navigation Component Deep Links](https://developer.android.com/guide/navigation/navigation-deep-link)
- [TaskStackBuilder Documentation](https://developer.android.com/reference/androidx/core/app/TaskStackBuilder)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-compose-navigation]]

### Предпосылки (Проще)

- [[q-how-to-implement-a-photo-editor-as-a-separate-component--android--easy]]

### Связанные (Тот Же уровень)

- [[q-compose-navigation-advanced--android--medium]]
- [[q-activity-navigation-how-it-works--android--medium]]
- [[q-what-navigation-methods-do-you-know--android--medium]]

### Продвинутые (Сложнее)

- [[q-mvi-architecture--android--hard]]

## Related Questions

### Prerequisites / Concepts

- [[c-compose-navigation]]

### Prerequisites (Easier)
- [[q-how-to-implement-a-photo-editor-as-a-separate-component--android--easy]]

### Related (Same Level)
- [[q-compose-navigation-advanced--android--medium]]
- [[q-activity-navigation-how-it-works--android--medium]]
- [[q-what-navigation-methods-do-you-know--android--medium]]

### Advanced (Harder)
- [[q-mvi-architecture--android--hard]]