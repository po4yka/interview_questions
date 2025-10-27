---
id: 20251016-172637
title: "Foreground Service Types / Типы Foreground Service"
aliases: ["Foreground Service Types", "Типы Foreground Service"]
topic: android
subtopics: [service, background-execution]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-service-types--android--easy, q-workmanager-vs-alternatives--android--medium]
created: 2025-10-12
updated: 2025-01-27
tags: [android/service, android/background-execution, difficulty/medium, foreground-service, notifications]
sources: [https://developer.android.com/guide/components/foreground-services]
---
# Вопрос (RU)
> Что такое типы Foreground Service в Android? Как правильно реализовать foreground services?

# Question (EN)
> What are Foreground Service types in Android? How do you implement foreground services correctly?

---

## Ответ (RU)

**Foreground Services** выполняются с видимым уведомлением, позволяя длительным операциям продолжаться в фоне. С Android 10+ требуется объявление типа сервиса, а Android 14+ ввел строгие ограничения на запуск из фона.

**Ключевые требования:**
- Постоянное уведомление обязательно
- Тип сервиса в манифесте (Android 10+)
- Вызов `startForeground()` в течение 5 секунд
- Специфические разрешения для каждого типа

**Основные типы:**
```kotlin
// ✅ Распространённые типы
FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK  // Воспроизведение медиа
FOREGROUND_SERVICE_TYPE_LOCATION        // Отслеживание локации
FOREGROUND_SERVICE_TYPE_DATA_SYNC       // Синхронизация данных
FOREGROUND_SERVICE_TYPE_CAMERA          // Работа с камерой
FOREGROUND_SERVICE_TYPE_MICROPHONE      // Аудио-запись

// ⚠️ Специальные типы
FOREGROUND_SERVICE_TYPE_SHORT_SERVICE   // Быстрые операции < 3 мин (Android 12+)
FOREGROUND_SERVICE_TYPE_SPECIAL_USE     // Требует обоснование в Play Console (Android 14+)
```

**Объявление в манифесте:**
```xml
<manifest>
    <!-- ✅ Обязательные разрешения -->
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application>
        <service
            android:name=".MusicService"
            android:foregroundServiceType="mediaPlayback"
            android:exported="false" /> <!-- ✅ Не экспортируем -->
    </application>
</manifest>
```

**Реализация медиа-сервиса:**
```kotlin
class MusicService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()

        // ✅ Указываем тип при вызове startForeground
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        return START_STICKY // ✅ Для долгоживущих сервисов
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_music)
            .setContentTitle("Now Playing")
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true) // ✅ Постоянное уведомление
            .setStyle(
                androidx.media.app.NotificationCompat.MediaStyle()
                    .setShowActionsInCompactView(0, 1)
            )
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Android 14+ ограничения:**
```kotlin
// ❌ НЕЛЬЗЯ запускать foreground service из фона в большинстве случаев

// ✅ Исключения (можно запускать из фона):
// - MEDIA_PLAYBACK с активной медиа-сессией
// - PHONE_CALL во время звонка
// - CONNECTED_DEVICE при подключении Bluetooth/USB
// - Запуск через high-priority FCM
// - Запуск из действия уведомления
// - Запуск с точного будильника (AlarmManager)

// ⚠️ Рекомендация: используйте [[c-workmanager]] вместо foreground services где возможно
```

**Short Service для быстрых операций:**
```kotlin
class QuickUploadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            startForeground(
                NOTIFICATION_ID,
                createNotification(),
                // ✅ Комбинируем типы через bitwise OR
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SHORT_SERVICE or
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            )
        }

        uploadFile()
        return START_NOT_STICKY // ✅ Для одноразовых операций
    }

    // ✅ Обрабатываем таймаут (Android 12+)
    override fun onTimeout(startId: Int) {
        cleanup()
        stopSelf(startId)
    }
}
```

## Answer (EN)

**Foreground Services** run with a visible notification, allowing long-running operations to continue in the background. Android 10+ requires service type declaration, and Android 14+ introduced strict background launch restrictions.

**Key requirements:**
- Persistent notification mandatory
- Service type in manifest (Android 10+)
- Call `startForeground()` within 5 seconds
- Type-specific permissions required

**Main types:**
```kotlin
// ✅ Common types
FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK  // Media playback
FOREGROUND_SERVICE_TYPE_LOCATION        // Location tracking
FOREGROUND_SERVICE_TYPE_DATA_SYNC       // Data synchronization
FOREGROUND_SERVICE_TYPE_CAMERA          // Camera usage
FOREGROUND_SERVICE_TYPE_MICROPHONE      // Audio recording

// ⚠️ Special types
FOREGROUND_SERVICE_TYPE_SHORT_SERVICE   // Quick operations < 3 min (Android 12+)
FOREGROUND_SERVICE_TYPE_SPECIAL_USE     // Requires Play Console justification (Android 14+)
```

**Manifest declaration:**
```xml
<manifest>
    <!-- ✅ Required permissions -->
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application>
        <service
            android:name=".MusicService"
            android:foregroundServiceType="mediaPlayback"
            android:exported="false" /> <!-- ✅ Don't export -->
    </application>
</manifest>
```

**Media service implementation:**
```kotlin
class MusicService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()

        // ✅ Specify type when calling startForeground
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        return START_STICKY // ✅ For long-running services
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_music)
            .setContentTitle("Now Playing")
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true) // ✅ Persistent notification
            .setStyle(
                androidx.media.app.NotificationCompat.MediaStyle()
                    .setShowActionsInCompactView(0, 1)
            )
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Android 14+ restrictions:**
```kotlin
// ❌ CANNOT start foreground service from background in most cases

// ✅ Exemptions (can start from background):
// - MEDIA_PLAYBACK with active media session
// - PHONE_CALL during active call
// - CONNECTED_DEVICE when Bluetooth/USB connected
// - Started via high-priority FCM
// - Started from notification action
// - Started from exact alarm (AlarmManager)

// ⚠️ Recommendation: use [[c-workmanager]] instead of foreground services where possible
```

**Short Service for quick operations:**
```kotlin
class QuickUploadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            startForeground(
                NOTIFICATION_ID,
                createNotification(),
                // ✅ Combine types with bitwise OR
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SHORT_SERVICE or
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            )
        }

        uploadFile()
        return START_NOT_STICKY // ✅ For one-time operations
    }

    // ✅ Handle timeout (Android 12+)
    override fun onTimeout(startId: Int) {
        cleanup()
        stopSelf(startId)
    }
}
```

---

## Follow-ups

- What happens if you don't call `startForeground()` within 5 seconds?
- How do you handle service type changes at runtime?
- What are the testing strategies for foreground service lifecycle and Android 14 restrictions?
- How does `onTimeout()` behavior differ from manual timeout handling?

## References

- [[c-workmanager]] - Alternative to foreground services
- https://developer.android.com/guide/components/foreground-services
- https://developer.android.com/about/versions/14/changes/fgs-types-required

## Related Questions

### Prerequisites (Easier)
- [[q-android-service-types--android--easy]] - Service types and lifecycle
- Basic understanding of Android notifications and notification channels

### Related (Same Level)
- [[q-workmanager-vs-alternatives--android--medium]] - Background work comparison
- Service vs [[c-workmanager]] trade-offs and use cases

### Advanced (Harder)
- Implementing service binding with foreground services
- Advanced [[c-workmanager]] patterns for complex background work
