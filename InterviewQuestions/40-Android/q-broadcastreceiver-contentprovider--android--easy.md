---
id: "20251015082237501"
title: "Broadcastreceiver Contentprovider / BroadcastReceiver и ContentProvider"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: - android
  - android/broadcast-receiver
  - android/content-provider
  - broadcast-receiver
  - content-provider
  - data-sharing
  - intent
  - system-events
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

Два важных компонента Android для **системных событий** и **обмена данными**.

**BroadcastReceiver** - Слушатель системных событий

Принимает **Intent сообщения** от системы или приложений.

**Основные случаи использования:**

```kotlin
// Изменение сетевого подключения
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val networkInfo = connectivityManager.activeNetworkInfo

        if (networkInfo?.isConnected == true) {
            // Сеть доступна
        } else {
            // Сеть недоступна
        }
    }
}

// Регистрация в AndroidManifest.xml
<receiver android:name=".NetworkReceiver">
    <intent-filter>
        <action android:name="android.net.conn.CONNECTIVITY_CHANGE" />
    </intent-filter>
</receiver>
```

**Примеры системных событий:**
- Изменение сети
- Получение SMS
- Низкий заряд батареи
- Изменение режима полета
- Изменение состояния WiFi

**ContentProvider** - Интерфейс обмена данными

Предоставляет **структурированный доступ к данным** для обмена данными между приложениями.

**Основные случаи использования:**

```kotlin
class ContactsProvider : ContentProvider() {
    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // Возвращаем данные контактов
        return database.query(...)
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        // Вставляем новый контакт
        return Uri.parse("content://contacts/${newId}")
    }
}

// Объявление в AndroidManifest.xml
<provider
    android:name=".ContactsProvider"
    android:authorities="com.example.contacts"
    android:exported="true" />
```

**Встроенные ContentProviders:**
- **Contacts**: Список контактов
- **MediaStore**: Изображения/видео из галереи
- **Calendar**: События календаря
- **CallLog**: История звонков
- **Settings**: Системные настройки

**Доступ к ContentProvider:**

```kotlin
// Чтение контактов
val cursor = contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null, null, null, null
)

cursor?.use {
    while (it.moveToNext()) {
        val name = it.getString(it.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME))
        // Используем данные контакта
    }
}
```

**Сравнение:**

| Компонент | Назначение | Вход | Выход | Пример |
|-----------|-----------|------|-------|--------|
| BroadcastReceiver | Слушатель событий | Intent | Действие | Изменение сети |
| ContentProvider | Доступ к данным | Запрос | Cursor | API контактов |

**Резюме:**

- **BroadcastReceiver**: Слушает широковещательные сообщения системы/приложений через Intent
- **ContentProvider**: Предоставляет структурированный доступ к данным для межприложенного взаимодействия


---

## Related Questions

### Related (Medium)
- [[q-what-is-broadcastreceiver--android--easy]] - Broadcast

### Advanced (Harder)
- [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]] - Broadcast
- [[q-how-to-connect-broadcastreceiver-so-it-can-receive-messages--android--medium]] - Broadcast
- [[q-kotlin-context-receivers--kotlin--hard]] - Broadcast
