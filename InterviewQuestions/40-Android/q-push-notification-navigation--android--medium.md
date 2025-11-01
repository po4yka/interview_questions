---
id: 20251012-12271174
title: "Push Notification Navigation / Навигация из push уведомлений"
aliases: [Push Notification Navigation, Навигация из push уведомлений, FCM Navigation, Navigation from Notifications]
topic: android
subtopics: [notifications, ui-navigation, intents-deeplinks]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-navigation-advanced--android--medium, q-activity-navigation-how-it-works--android--medium, q-what-navigation-methods-do-you-know--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-31
tags: [android/notifications, android/ui-navigation, android/intents-deeplinks, notifications, fcm, navigation, deeplink, difficulty/medium]
---

# Вопрос (RU)

Как открыть конкретную Activity или Fragment из push-уведомления?

# Question (EN)

How to open a specific Activity or Fragment from a push notification?

---

## Ответ (RU)

**Подход**: Настроить FCM service для создания PendingIntent с данными навигации, обработать intent в Activity через `onCreate()`/`onNewIntent()`

**Сложность**: Time O(1), Space O(1)

### 1. FCM Service с навигационными данными

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
            putExtra(EXTRA_ITEM_ID, itemId)
        }

        val pendingIntent = PendingIntent.getActivity(
            this,
            System.currentTimeMillis().toInt(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(0, notification)
    }
}
```

✅ **Правильно**: Использование data payload для передачи параметров навигации
✅ **Правильно**: FLAG_IMMUTABLE для PendingIntent (Android 12+)
❌ **Неправильно**: Использование notification payload без data - ограниченные возможности кастомизации

### 2. Обработка навигации в MainActivity

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navHost = supportFragmentManager
            .findFragmentById(R.id.nav_host) as NavHostFragment
        navController = navHost.navController

        handleNotificationIntent(intent)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        intent?.let { handleNotificationIntent(it) }
    }

    private fun handleNotificationIntent(intent: Intent) {
        val screen = intent.getStringExtra(EXTRA_SCREEN) ?: return
        val itemId = intent.getIntExtra(EXTRA_ITEM_ID, 0)

        when (screen) {
            "detail" -> navController.navigate(
                R.id.detailFragment,
                Bundle().apply { putInt("itemId", itemId) }
            )
            "profile" -> navController.navigate(R.id.profileFragment)
        }
    }
}
```

✅ **Правильно**: Обработка в `onNewIntent()` для launchMode="singleTop"
✅ **Правильно**: Проверка extras перед навигацией
❌ **Неправильно**: Навигация только в `onCreate()` - не работает если Activity уже открыта

### 3. Deep Links для навигации

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

✅ **Правильно**: Deep links упрощают навигацию и переиспользуются для web-to-app
✅ **Правильно**: setPackage() предотвращает открытие в других приложениях
❌ **Неправильно**: Отсутствие autoVerify для HTTPS deep links

### 4. Back Stack для правильной навигации

```kotlin
private fun createIntentWithBackStack(itemId: Int): PendingIntent {
    val stackBuilder = TaskStackBuilder.create(this).apply {
        addNextIntent(Intent(this@MyFCMService, MainActivity::class.java))
        addNextIntent(
            Intent(this@MyFCMService, DetailActivity::class.java).apply {
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

✅ **Правильно**: TaskStackBuilder создает корректный back stack
❌ **Неправильно**: Прямой переход на Detail без родительской Activity - кнопка Back закрывает приложение

**Объяснение**:
1. FCM Service получает сообщение и парсит data payload
2. Создается Intent с extras (screen, itemId) или deep link URI
3. PendingIntent передается в уведомление через setContentIntent()
4. При клике MainActivity обрабатывает intent в onCreate()/onNewIntent()
5. NavController выполняет переход на нужный экран с параметрами

## Answer (EN)

**Approach**: Configure FCM service to create PendingIntent with navigation data, handle intent in Activity via `onCreate()`/`onNewIntent()`

**Complexity**: Time O(1), Space O(1)

### 1. FCM Service with navigation data

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
            putExtra(EXTRA_ITEM_ID, itemId)
        }

        val pendingIntent = PendingIntent.getActivity(
            this,
            System.currentTimeMillis().toInt(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(0, notification)
    }
}
```

✅ **Correct**: Using data payload to pass navigation parameters
✅ **Correct**: FLAG_IMMUTABLE for PendingIntent (Android 12+)
❌ **Incorrect**: Using notification payload without data - limited customization

### 2. Handle navigation in MainActivity

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navHost = supportFragmentManager
            .findFragmentById(R.id.nav_host) as NavHostFragment
        navController = navHost.navController

        handleNotificationIntent(intent)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        intent?.let { handleNotificationIntent(it) }
    }

    private fun handleNotificationIntent(intent: Intent) {
        val screen = intent.getStringExtra(EXTRA_SCREEN) ?: return
        val itemId = intent.getIntExtra(EXTRA_ITEM_ID, 0)

        when (screen) {
            "detail" -> navController.navigate(
                R.id.detailFragment,
                Bundle().apply { putInt("itemId", itemId) }
            )
            "profile" -> navController.navigate(R.id.profileFragment)
        }
    }
}
```

✅ **Correct**: Handle in `onNewIntent()` for launchMode="singleTop"
✅ **Correct**: Check extras before navigation
❌ **Incorrect**: Navigation only in `onCreate()` - doesn't work if Activity already open

### 3. Deep Links for navigation

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

✅ **Correct**: Deep links simplify navigation and reusable for web-to-app
✅ **Correct**: setPackage() prevents opening in other apps
❌ **Incorrect**: Missing autoVerify for HTTPS deep links

### 4. Back Stack for proper navigation

```kotlin
private fun createIntentWithBackStack(itemId: Int): PendingIntent {
    val stackBuilder = TaskStackBuilder.create(this).apply {
        addNextIntent(Intent(this@MyFCMService, MainActivity::class.java))
        addNextIntent(
            Intent(this@MyFCMService, DetailActivity::class.java).apply {
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

✅ **Correct**: TaskStackBuilder creates proper back stack
❌ **Incorrect**: Direct jump to Detail without parent Activity - Back button closes app

**Explanation**:
1. FCM Service receives message and parses data payload
2. Create Intent with extras (screen, itemId) or deep link URI
3. PendingIntent passed to notification via setContentIntent()
4. On click MainActivity handles intent in onCreate()/onNewIntent()
5. NavController performs navigation to target screen with parameters

---

## Follow-ups

- How to handle notification when app is killed vs in background vs foreground?
- What's the difference between notification payload and data-only payload?
- How to pass complex objects (not just primitives) through notification intent?
- How to ensure only one notification opens even with multiple taps?
- How to test push notification navigation without backend?

## References

- [Android Notification Guide](https://developer.android.com/develop/ui/views/notifications)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [Navigation Component Deep Links](https://developer.android.com/guide/navigation/navigation-deep-link)
- [TaskStackBuilder Documentation](https://developer.android.com/reference/androidx/core/app/TaskStackBuilder)

## Related Questions

### Prerequisites (Easier)
- [[q-how-to-implement-a-photo-editor-as-a-separate-component--android--easy]]

### Related (Same Level)
- [[q-compose-navigation-advanced--android--medium]]
- [[q-activity-navigation-how-it-works--android--medium]]
- [[q-what-navigation-methods-do-you-know--android--medium]]

### Advanced (Harder)
- [[q-mvi-architecture--android--hard]]
