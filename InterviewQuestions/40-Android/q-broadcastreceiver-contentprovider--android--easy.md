---
topic: android
tags:
  - android
  - android/broadcast-receiver
  - android/content-provider
  - broadcast-receiver
  - content-provider
  - data-sharing
  - intent
  - system-events
difficulty: easy
status: draft
---

# Что известно про ресиверы и контент-провайдеры?

# Question (EN)
> What are BroadcastReceiver and ContentProvider?

# Вопрос (RU)
> Что известно про ресиверы и контент-провайдеры?

---

## Answer (EN)

Two important Android components for **system events** and **data sharing**.

**BroadcastReceiver** - System Event Listener

Receives **Intent messages** from system or apps.

**Common Use Cases:**

```kotlin
// Network connectivity change
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val networkInfo = connectivityManager.activeNetworkInfo

        if (networkInfo?.isConnected == true) {
            // Network available
        } else {
            // Network unavailable
        }
    }
}

// Register in AndroidManifest.xml
<receiver android:name=".NetworkReceiver">
    <intent-filter>
        <action android:name="android.net.conn.CONNECTIVITY_CHANGE" />
    </intent-filter>
</receiver>
```

**System Events Examples:**
- Network change
- SMS received
- Battery low
- Airplane mode change
- WiFi state change

**ContentProvider** - Data Sharing Interface

Provides **structured data access** for sharing data between apps.

**Common Use Cases:**

```kotlin
class ContactsProvider : ContentProvider() {
    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // Return contacts data
        return database.query(...)
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        // Insert new contact
        return Uri.parse("content://contacts/${newId}")
    }
}

// Declare in AndroidManifest.xml
<provider
    android:name=".ContactsProvider"
    android:authorities="com.example.contacts"
    android:exported="true" />
```

**Built-in ContentProviders:**
- **Contacts**: Contact list
- **MediaStore**: Gallery images/videos
- **Calendar**: Calendar events
- **CallLog**: Call history
- **Settings**: System settings

**Accessing ContentProvider:**

```kotlin
// Read contacts
val cursor = contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null, null, null, null
)

cursor?.use {
    while (it.moveToNext()) {
        val name = it.getString(it.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME))
        // Use contact data
    }
}
```

**Comparison:**

| Component | Purpose | Input | Output | Example |
|-----------|---------|-------|--------|---------|
| BroadcastReceiver | Event listener | Intent | Action | Network change |
| ContentProvider | Data access | Query | Cursor | Contacts API |

**Summary:**

- **BroadcastReceiver**: Listens to system/app broadcasts via Intent
- **ContentProvider**: Provides structured data access for inter-app communication

---

## Ответ (RU)

**BroadcastReceiver** принимает сообщения (интенты) от системы или приложений, например при смене сети или получении SMS.

**ContentProvider** предоставляет структурированный способ доступа к данным, используется для обмена данными между приложениями (например, контакты, галерея).


---

## Related Questions

### Related (Easy)
- [[q-what-is-broadcastreceiver--android--easy]] - Broadcast

### Advanced (Harder)
- [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]] - Broadcast
- [[q-how-to-connect-broadcastreceiver-so-it-can-receive-messages--android--medium]] - Broadcast
- [[q-kotlin-context-receivers--kotlin--hard]] - Broadcast

---

## Related Questions

### Related (Easy)
- [[q-what-is-broadcastreceiver--android--easy]] - Broadcast

### Advanced (Harder)
- [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]] - Broadcast
- [[q-how-to-connect-broadcastreceiver-so-it-can-receive-messages--android--medium]] - Broadcast
- [[q-kotlin-context-receivers--kotlin--hard]] - Broadcast
