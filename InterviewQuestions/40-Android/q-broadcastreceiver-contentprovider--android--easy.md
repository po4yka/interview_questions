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
status: draft
moc: moc-android
related:
- c-broadcast-receiver
- c-content-provider
- q-android-app-components--android--easy
- q-android-manifest-file--android--easy
- q-android-service-types--android--easy
sources:
- "https://developer.android.com/guide/components/broadcasts"
- "https://developer.android.com/guide/topics/providers/content-provider-basics"
created: 2025-10-15
updated: 2025-11-10
tags: [android/broadcast-receiver, android/content-provider, difficulty/easy]

---

# Вопрос (RU)
> Что такое `BroadcastReceiver` и `ContentProvider` в Android?

# Question (EN)
> What are `BroadcastReceiver` and `ContentProvider` in Android?

---

## Ответ (RU)

### `BroadcastReceiver`

**Компонент для получения системных и пользовательских событий**. Реагирует на широковещательные сообщения (broadcasts) от системы или других приложений.

**Виды broadcasts**:
- System: ACTION_BATTERY_LOW, ACTION_BOOT_COMPLETED, ACTION_POWER_CONNECTED
- Custom: события между компонентами приложения

**Регистрация**:
```kotlin
// ✅ Динамическая (lifecycle-aware)
class MainActivity : AppCompatActivity() {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            // Обработка должна быть быстрой (< ~10 сек, иначе риск ANR)
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

```xml
// ✅ Статическая в Manifest (для определённых системных и явных broadcast'ов доступна и после API 26)
<receiver android:name=".MyReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED"/>
    </intent-filter>
</receiver>
```

**Критичные ограничения**:
- `onReceive()` обычно вызывается в main thread; обработка должна быть быстрой (долгие операции → риск ANR)
- Для длительной фоновой работы использовать `WorkManager` / `JobScheduler` / `ForegroundService`
- Начиная с API 26 большинство неявных broadcast'ов для сторонних приложений ограничены; использовать явные или разрешённые системные события

### `ContentProvider`

**Стандартизированный интерфейс для доступа к структурированным данным**. Обеспечивает CRUD операции и обмен данными между приложениями через URI.

**Базовая реализация (упрощённый пример)**:
```kotlin
class ContactsProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // Инициализация БД / ресурсов
        return true
    }

    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? = db.query(...)

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        val id = db.insert(...)
        context?.contentResolver?.notifyChange(uri, null)
        return ContentUris.withAppendedId(uri, id)
    }

    override fun update(
        uri: Uri,
        values: ContentValues?,
        selection: String?,
        selectionArgs: Array<String>?
    ): Int = db.update(...)

    override fun delete(
        uri: Uri,
        selection: String?,
        selectionArgs: Array<String>?
    ): Int = db.delete(...)

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
    arrayOf(
        ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
        ContactsContract.CommonDataKinds.Phone.NUMBER
    ),
    null,
    null,
    null
)
```

**Сценарии применения**:
- Межпроцессное взаимодействие (IPC)
- Интеграция с системными данными (Contacts, Calendar, MediaStore)
- Централизованный контроль доступа к данным

## Answer (EN)

### `BroadcastReceiver`

**Component for receiving system and custom events**. Responds to broadcast messages from the system or other applications.

**Broadcast types**:
- System: ACTION_BATTERY_LOW, ACTION_BOOT_COMPLETED, ACTION_POWER_CONNECTED
- Custom: events between app components

**Registration**:
```kotlin
// ✅ Dynamic (lifecycle-aware)
class MainActivity : AppCompatActivity() {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            // Keep work fast (< ~10 sec; long work may cause ANR)
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

```xml
// ✅ Static in Manifest (still valid for certain system and explicit broadcasts on API 26+)
<receiver android:name=".MyReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED"/>
    </intent-filter>
</receiver>
```

**Critical constraints**:
- `onReceive()` is usually called on the main thread; work must be quick (long work → ANR risk)
- For long-running background work: use `WorkManager` / `JobScheduler` / a `ForegroundService`
- Since API 26, most implicit broadcasts for third-party apps are restricted; use explicit broadcasts or allowed system actions

### `ContentProvider`

**Standardized interface for accessing structured data**. Provides CRUD operations and data sharing between apps via URI.

**Basic implementation (simplified example)**:
```kotlin
class ContactsProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // Initialize DB / resources
        return true
    }

    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? = db.query(...)

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        val id = db.insert(...)
        context?.contentResolver?.notifyChange(uri, null)
        return ContentUris.withAppendedId(uri, id)
    }

    override fun update(
        uri: Uri,
        values: ContentValues?,
        selection: String?,
        selectionArgs: Array<String>?
    ): Int = db.update(...)

    override fun delete(
        uri: Uri,
        selection: String?,
        selectionArgs: Array<String>?
    ): Int = db.delete(...)

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
    arrayOf(
        ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
        ContactsContract.CommonDataKinds.Phone.NUMBER
    ),
    null,
    null,
    null
)
```

**Use cases**:
- Inter-process communication (IPC)
- Integration with system data (Contacts, Calendar, MediaStore)
- Centralized data access control

---

## Follow-ups

- How to avoid ANR in `BroadcastReceiver` when processing takes > 10 seconds?
- What's the difference between ordered and normal broadcasts, and when to use each?
- How to secure `ContentProvider` with read/write permissions and URI grants?
- When to choose `ContentProvider` vs direct database access for data sharing?
- How to implement `UriMatcher` for multi-table `ContentProvider` routing?

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
