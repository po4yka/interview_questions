---
id: 20251016-162753
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
  - q-android-app-components--android--easy
  - q-android-manifest-file--android--easy
  - q-android-service-types--android--easy
sources:
  - https://developer.android.com/guide/components/broadcasts
  - https://developer.android.com/guide/topics/providers/content-provider-basics
created: 2025-10-15
updated: 2025-10-28
tags: [android/broadcast-receiver, android/content-provider, difficulty/easy]
---
# Вопрос (RU)
> Что такое BroadcastReceiver и ContentProvider в Android?

# Question (EN)
> What are BroadcastReceiver and ContentProvider in Android?

---

## Ответ (RU)

### BroadcastReceiver

**Определение**: Компонент Android, который получает и обрабатывает широковещательные сообщения (broadcasts) от системы или других приложений.

**Основные виды**:
- System broadcasts (батарея, сеть, загрузка и т.д.)
- Custom broadcasts (между компонентами приложения)

**Регистрация**:
```kotlin
// ✅ Динамическая регистрация (рекомендуется)
class MainActivity : AppCompatActivity() {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            // Обработка события (макс. 10 сек)
        }
    }

    override fun onStart() {
        super.onStart()
        registerReceiver(receiver, IntentFilter(Intent.ACTION_POWER_CONNECTED))
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(receiver)
    }
}

// ❌ Статическая регистрация в Manifest (ограничена с Android 8+)
```

**Важные ограничения**:
- onReceive() должен завершиться за 10 сек (иначе ANR)
- Для долгих операций используйте WorkManager или JobScheduler

### ContentProvider

**Определение**: Компонент для структурированного доступа к данным приложения. Предоставляет единый интерфейс для чтения/записи данных между приложениями.

**Основные методы CRUD**:
```kotlin
class MyProvider : ContentProvider() {
    override fun onCreate(): Boolean = true

    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // Чтение данных
        return database.query(...)
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        // Добавление записи
        val id = database.insert(...)
        return ContentUris.withAppendedId(uri, id)
    }
}
```

**Когда использовать**:
- Обмен данными между приложениями
- Централизованное управление данными
- Интеграция с системными провайдерами (Contacts, Calendar)

## Answer (EN)

### BroadcastReceiver

**Definition**: An Android component that receives and handles broadcast messages from the system or other applications.

**Types**:
- System broadcasts (battery, network, boot, etc.)
- Custom broadcasts (between app components)

**Registration**:
```kotlin
// ✅ Dynamic registration (recommended)
class MainActivity : AppCompatActivity() {
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            // Handle event (max 10 sec)
        }
    }

    override fun onStart() {
        super.onStart()
        registerReceiver(receiver, IntentFilter(Intent.ACTION_POWER_CONNECTED))
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(receiver)
    }
}

// ❌ Static registration in Manifest (restricted since Android 8+)
```

**Key constraints**:
- onReceive() must complete within 10 sec (otherwise ANR)
- Use WorkManager or JobScheduler for long operations

### ContentProvider

**Definition**: A component for structured access to app data. Provides a unified interface for reading/writing data between applications.

**Core CRUD methods**:
```kotlin
class MyProvider : ContentProvider() {
    override fun onCreate(): Boolean = true

    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // Read data
        return database.query(...)
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        // Insert record
        val id = database.insert(...)
        return ContentUris.withAppendedId(uri, id)
    }
}
```

**When to use**:
- Sharing data between apps
- Centralized data management
- Integration with system providers (Contacts, Calendar)

---

## Follow-ups

- How to avoid ANR in onReceive() and delegate longer work safely?
- How to secure a ContentProvider (read/write permissions, Uri permissions)?
- When to use WorkManager vs BroadcastReceiver for background work?
- What's the difference between ordered and unordered broadcasts?
- How to implement URI matching in ContentProvider?

## References

- [[c-broadcast-receiver]]
- [[c-content-provider]]
- [[q-android-app-components--android--easy]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]]
- [[q-android-app-components--android--easy]]

### Related (Same Level)
- [[q-android-service-types--android--easy]]
- [[q-android-services-purpose--android--easy]]

### Advanced (Harder)
- [[q-what-is-workmanager--android--medium]]
- [[q-background-tasks-decision-guide--android--medium]]
