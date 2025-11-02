---
id: android-320
title: BroadcastReceiver and ContentProvider / BroadcastReceiver и ContentProvider
aliases: [BroadcastReceiver and ContentProvider, BroadcastReceiver и ContentProvider]
topic: android
subtopics:
  - broadcast-receiver
  - content-provider
question_kind: android
difficulty: easy
original_language: ru
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-android-app-components--android--easy
  - q-android-manifest-file--android--easy
  - q-android-service-types--android--easy
sources:
  - https://developer.android.com/guide/components/broadcasts
  - https://developer.android.com/guide/topics/providers/content-provider-basics
created: 2025-10-15
updated: 2025-10-29
tags: [android/broadcast-receiver, android/content-provider, difficulty/easy]
date created: Thursday, October 30th 2025, 11:11:16 am
date modified: Sunday, November 2nd 2025, 1:03:34 pm
---

# Вопрос (RU)
> Что такое BroadcastReceiver и ContentProvider в Android?

# Question (EN)
> What are BroadcastReceiver and ContentProvider in Android?

---

## Ответ (RU)

### BroadcastReceiver

**Компонент для получения системных и пользовательских событий**. Реагирует на широковещательные сообщения (broadcasts) от системы или других приложений.

**Виды broadcasts**:
- System: ACTION_BATTERY_LOW, ACTION_BOOT_COMPLETED, CONNECTIVITY_CHANGE
- Custom: события между компонентами приложения

**Регистрация**:
```kotlin
// ✅ Динамическая (lifecycle-aware)
class MainActivity : AppCompatActivity() {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            // Обработка < 10 сек (иначе ANR)
        }
    }

    override fun onStart() {
        super.onStart()
        registerReceiver(receiver, IntentFilter(Intent.ACTION_POWER_CONNECTED))
    }

    override fun onStop() {
        unregisterReceiver(receiver)
        super.onStop()
    }
}
```

```kotlin
// ❌ Статическая в Manifest (ограничена с API 26+)
<receiver android:name=".MyReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED"/>
    </intent-filter>
</receiver>
```

**Критичные ограничения**:
- onReceive() выполняется на main thread (max 10 сек → ANR)
- Для фоновой работы: WorkManager / JobScheduler

### ContentProvider

**Стандартизированный интерфейс для доступа к структурированным данным**. Обеспечивает CRUD операции и обмен данными между приложениями через URI.

**Базовая реализация**:
```kotlin
class ContactsProvider : ContentProvider() {
    override fun query(
        uri: Uri, projection: Array<String>?,
        selection: String?, selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? = db.query(...)

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        val id = db.insert(...)
        context?.contentResolver?.notifyChange(uri, null)
        return ContentUris.withAppendedId(uri, id)
    }

    override fun getType(uri: Uri): String? = when (uriMatcher.match(uri)) {
        CONTACTS -> "vnd.android.cursor.dir/vnd.app.contact"
        CONTACT_ID -> "vnd.android.cursor.item/vnd.app.contact"
        else -> null
    }
}
```

**Примеры использования**:
```kotlin
// Чтение контактов
val cursor = contentResolver.query(
    ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
    arrayOf(DISPLAY_NAME, NUMBER), null, null, null
)
```

**Сценарии применения**:
- Межпроцессное взаимодействие (IPC)
- Интеграция с системными данными (Contacts, Calendar, MediaStore)
- Централизованный контроль доступа к данным

## Answer (EN)

### BroadcastReceiver

**Component for receiving system and custom events**. Responds to broadcast messages from the system or other applications.

**Broadcast types**:
- System: ACTION_BATTERY_LOW, ACTION_BOOT_COMPLETED, CONNECTIVITY_CHANGE
- Custom: events between app components

**Registration**:
```kotlin
// ✅ Dynamic (lifecycle-aware)
class MainActivity : AppCompatActivity() {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            // Process < 10 sec (otherwise ANR)
        }
    }

    override fun onStart() {
        super.onStart()
        registerReceiver(receiver, IntentFilter(Intent.ACTION_POWER_CONNECTED))
    }

    override fun onStop() {
        unregisterReceiver(receiver)
        super.onStop()
    }
}
```

```kotlin
// ❌ Static in Manifest (restricted since API 26+)
<receiver android:name=".MyReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED"/>
    </intent-filter>
</receiver>
```

**Critical constraints**:
- onReceive() runs on main thread (max 10 sec → ANR)
- For background work: WorkManager / JobScheduler

### ContentProvider

**Standardized interface for accessing structured data**. Provides CRUD operations and data sharing between apps via URI.

**Basic implementation**:
```kotlin
class ContactsProvider : ContentProvider() {
    override fun query(
        uri: Uri, projection: Array<String>?,
        selection: String?, selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? = db.query(...)

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        val id = db.insert(...)
        context?.contentResolver?.notifyChange(uri, null)
        return ContentUris.withAppendedId(uri, id)
    }

    override fun getType(uri: Uri): String? = when (uriMatcher.match(uri)) {
        CONTACTS -> "vnd.android.cursor.dir/vnd.app.contact"
        CONTACT_ID -> "vnd.android.cursor.item/vnd.app.contact"
        else -> null
    }
}
```

**Usage example**:
```kotlin
// Reading contacts
val cursor = contentResolver.query(
    ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
    arrayOf(DISPLAY_NAME, NUMBER), null, null, null
)
```

**Use cases**:
- Inter-process communication (IPC)
- Integration with system data (Contacts, Calendar, MediaStore)
- Centralized data access control

---

## Follow-ups

- How to avoid ANR in BroadcastReceiver when processing takes > 10 seconds?
- What's the difference between ordered and normal broadcasts, and when to use each?
- How to secure ContentProvider with read/write permissions and URI grants?
- When to choose ContentProvider vs direct database access for data sharing?
- How to implement UriMatcher for multi-table ContentProvider routing?

## References

- Official: [Broadcasts Overview](https://developer.android.com/guide/components/broadcasts)
- Official: [Content Provider Basics](https://developer.android.com/guide/topics/providers/content-provider-basics)
- [[c-broadcast-receiver]]
- [[c-content-provider]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-manifest-file--android--easy]]

### Related (Same Level)
- [[q-android-service-types--android--easy]]
- [[q-android-services-purpose--android--easy]]

### Advanced (Harder)
- [[q-what-is-workmanager--android--medium]]
- [[q-background-tasks-decision-guide--android--medium]]
