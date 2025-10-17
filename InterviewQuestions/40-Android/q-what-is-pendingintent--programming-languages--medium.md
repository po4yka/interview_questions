---
id: 20251012-122711164
title: "What Is Pendingintent / Что такое PendingIntent"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [languages, android, difficulty/medium]
---
# Что такое PendingIntent?

# Question (EN)
> What is PendingIntent?

# Вопрос (RU)
> Что такое PendingIntent?

---

## Answer (EN)

**PendingIntent** is a wrapper around an Intent that allows other components or applications to execute that Intent with your app's permissions, even when your app is not currently active. It's a token that you give to another application which allows the foreign application to use your application's permissions to execute a predefined piece of code.

### Key Characteristics

- **Deferred execution** - Intent executes later, not immediately
- **Permission delegation** - Runs with your app's permissions
- **Immutability** - Cannot be modified once created (with FLAG_IMMUTABLE)
- **Used by system** - Notifications, AlarmManager, AppWidgets

### Basic PendingIntent Creation

```kotlin
class PendingIntentExample : AppCompatActivity() {

    private fun createBasicPendingIntent() {
        // Intent to launch
        val intent = Intent(this, MainActivity::class.java)

        // Wrap in PendingIntent
        val pendingIntent = PendingIntent.getActivity(
            this,
            0, // Request code
            intent,
            PendingIntent.FLAG_IMMUTABLE // or FLAG_MUTABLE on Android 12+
        )
    }
}
```

### Types of PendingIntent

#### 1. PendingIntent for Activity

```kotlin
fun createActivityPendingIntent(context: Context): PendingIntent {
    val intent = Intent(context, DetailsActivity::class.java).apply {
        putExtra("ITEM_ID", 42)
        flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
    }

    return PendingIntent.getActivity(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE
    )
}
```

#### 2. PendingIntent for BroadcastReceiver

```kotlin
fun createBroadcastPendingIntent(context: Context): PendingIntent {
    val intent = Intent(context, MyBroadcastReceiver::class.java).apply {
        action = "com.example.ACTION_CUSTOM"
        putExtra("DATA", "value")
    }

    return PendingIntent.getBroadcast(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE
    )
}

class MyBroadcastReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val data = intent.getStringExtra("DATA")
        // Handle broadcast
    }
}
```

#### 3. PendingIntent for Service

```kotlin
fun createServicePendingIntent(context: Context): PendingIntent {
    val intent = Intent(context, MyService::class.java).apply {
        action = "ACTION_START_SERVICE"
    }

    return PendingIntent.getService(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE
    )
}
```

### PendingIntent Flags

```kotlin
class PendingIntentFlags {

    fun demonstrateFlags(context: Context) {
        val intent = Intent(context, MainActivity::class.java)

        // FLAG_IMMUTABLE - Cannot be modified (recommended for Android 12+)
        val immutablePI = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_IMMUTABLE
        )

        // FLAG_MUTABLE - Can be modified (use with caution)
        val mutablePI = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_MUTABLE
        )

        // FLAG_UPDATE_CURRENT - Update existing PendingIntent
        val updatePI = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        // FLAG_CANCEL_CURRENT - Cancel existing and create new
        val cancelPI = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_CANCEL_CURRENT
        )

        // FLAG_ONE_SHOT - Can only be used once
        val oneShotPI = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_ONE_SHOT
        )
    }
}
```

### Use Case 1: Notifications

```kotlin
class NotificationHelper(private val context: Context) {

    private val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

    fun showNotification() {
        // Create intent for notification tap
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("NOTIFICATION_ID", 1)
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_IMMUTABLE
        )

        // Action button intent
        val actionIntent = Intent(context, NotificationActionReceiver::class.java).apply {
            action = "ACTION_REPLY"
        }

        val actionPendingIntent = PendingIntent.getBroadcast(
            context,
            1,
            actionIntent,
            PendingIntent.FLAG_IMMUTABLE
        )

        // Build notification
        val notification = NotificationCompat.Builder(context, "channel_id")
            .setContentTitle("New Message")
            .setContentText("You have a new message")
            .setSmallIcon(R.drawable.ic_notification)
            .setContentIntent(pendingIntent) // Opens app when tapped
            .addAction(
                R.drawable.ic_reply,
                "Reply",
                actionPendingIntent // Action button
            )
            .setAutoCancel(true)
            .build()

        notificationManager.notify(1, notification)
    }
}

class NotificationActionReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            "ACTION_REPLY" -> {
                // Handle reply action
            }
        }
    }
}
```

### Use Case 2: AlarmManager

```kotlin
class AlarmScheduler(private val context: Context) {

    private val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager

    fun scheduleAlarm(timeInMillis: Long) {
        val intent = Intent(context, AlarmReceiver::class.java).apply {
            action = "com.example.ALARM_ACTION"
        }

        val pendingIntent = PendingIntent.getBroadcast(
            context,
            0,
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        // Set exact alarm
        alarmManager.setExact(
            AlarmManager.RTC_WAKEUP,
            timeInMillis,
            pendingIntent
        )
    }

    fun cancelAlarm() {
        val intent = Intent(context, AlarmReceiver::class.java)
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            0,
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_NO_CREATE
        )

        pendingIntent?.let {
            alarmManager.cancel(it)
            it.cancel()
        }
    }
}

class AlarmReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Handle alarm
        Toast.makeText(context, "Alarm triggered!", Toast.LENGTH_SHORT).show()
    }
}
```

### Use Case 3: App Widgets

```kotlin
class MyAppWidgetProvider : AppWidgetProvider() {

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        for (appWidgetId in appWidgetIds) {
            // Intent to launch app
            val intent = Intent(context, MainActivity::class.java)
            val pendingIntent = PendingIntent.getActivity(
                context,
                0,
                intent,
                PendingIntent.FLAG_IMMUTABLE
            )

            // Button click intent
            val buttonIntent = Intent(context, MyAppWidgetProvider::class.java).apply {
                action = "ACTION_WIDGET_BUTTON_CLICK"
            }
            val buttonPendingIntent = PendingIntent.getBroadcast(
                context,
                0,
                buttonIntent,
                PendingIntent.FLAG_IMMUTABLE
            )

            // Update widget
            val views = RemoteViews(context.packageName, R.layout.widget_layout)
            views.setOnClickPendingIntent(R.id.widget_root, pendingIntent)
            views.setOnClickPendingIntent(R.id.widget_button, buttonPendingIntent)

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }

    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)

        if (intent.action == "ACTION_WIDGET_BUTTON_CLICK") {
            // Handle button click
        }
    }
}
```

### Use Case 4: Geofencing

```kotlin
class GeofenceHelper(private val context: Context) {

    private val geofencingClient = LocationServices.getGeofencingClient(context)

    fun addGeofence(latitude: Double, longitude: Double, radius: Float) {
        val geofence = Geofence.Builder()
            .setRequestId("GEOFENCE_ID")
            .setCircularRegion(latitude, longitude, radius)
            .setExpirationDuration(Geofence.NEVER_EXPIRE)
            .setTransitionTypes(Geofence.GEOFENCE_TRANSITION_ENTER or Geofence.GEOFENCE_TRANSITION_EXIT)
            .build()

        val geofencingRequest = GeofencingRequest.Builder()
            .setInitialTrigger(GeofencingRequest.INITIAL_TRIGGER_ENTER)
            .addGeofence(geofence)
            .build()

        val intent = Intent(context, GeofenceBroadcastReceiver::class.java)
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            0,
            intent,
            PendingIntent.FLAG_MUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        if (ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
            geofencingClient.addGeofences(geofencingRequest, pendingIntent)
        }
    }
}
```

### Android 12+ Security Requirements

```kotlin
class Android12PendingIntent(private val context: Context) {

    fun createSecurePendingIntent() {
        val intent = Intent(context, MainActivity::class.java)

        // Android 12+ requires FLAG_IMMUTABLE or FLAG_MUTABLE
        val pendingIntent = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            PendingIntent.getActivity(
                context,
                0,
                intent,
                PendingIntent.FLAG_IMMUTABLE // Recommended
            )
        } else {
            PendingIntent.getActivity(
                context,
                0,
                intent,
                0
            )
        }
    }

    // Use FLAG_MUTABLE only when necessary
    fun createMutablePendingIntent() {
        val intent = Intent(context, MainActivity::class.java)

        val pendingIntent = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            PendingIntent.getActivity(
                context,
                0,
                intent,
                PendingIntent.FLAG_MUTABLE // Use with caution
            )
        } else {
            PendingIntent.getActivity(
                context,
                0,
                intent,
                0
            )
        }
    }
}
```

### Canceling PendingIntent

```kotlin
fun cancelPendingIntent(context: Context) {
    val intent = Intent(context, MainActivity::class.java)

    // Get existing PendingIntent (FLAG_NO_CREATE)
    val pendingIntent = PendingIntent.getActivity(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_NO_CREATE
    )

    // Cancel if exists
    pendingIntent?.cancel()
}
```

### Common Use Cases

| Use Case | Type | Purpose |
|----------|------|---------|
| Notifications | Activity | Open app when tapped |
| Notification Actions | Broadcast | Handle action buttons |
| Alarms | Broadcast | Trigger at specific time |
| App Widgets | Activity/Broadcast | Handle widget interactions |
| Geofencing | Broadcast | Location-based triggers |
| Media controls | Service | Control playback |

### Best Practices

1. **Use FLAG_IMMUTABLE** when possible (Android 12+ requirement)
2. **Use unique request codes** to distinguish different PendingIntents
3. **Include FLAG_UPDATE_CURRENT** to update existing PendingIntent
4. **Cancel PendingIntents** when no longer needed
5. **Avoid FLAG_MUTABLE** unless absolutely necessary
6. **Set explicit intents** for security

---

## Ответ (RU)

PendingIntent — это обёртка над Intent, позволяющая другим компонентам выполнить Intent от имени вашего приложения даже если оно сейчас не активно. Используется в уведомлениях, для запуска BroadcastReceiver или Service и в AlarmManager.

---

## Related Questions

### Prerequisites (Easier)
- [[q-architecture-components-libraries--android--easy]] - Fundamentals
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Fundamentals
- [[q-what-unifies-android-components--android--easy]] - Fundamentals

### Related (Medium)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
- [[q-what-is-pendingintent--android--medium]] - Fundamentals
- [[q-intent-filters-android--android--medium]] - Fundamentals
- [[q-anr-application-not-responding--android--medium]] - Fundamentals
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Fundamentals

### Advanced (Harder)
- [[q-how-application-priority-is-determined-by-the-system--android--hard]] - Fundamentals
- [[q-kotlin-context-receivers--kotlin--hard]] - Fundamentals
