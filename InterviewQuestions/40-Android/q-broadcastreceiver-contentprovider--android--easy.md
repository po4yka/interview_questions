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
created: 2025-10-15
updated: 2025-10-20
tags: [android/broadcast-receiver, android/content-provider, difficulty/easy]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:53 pm
---

# Вопрос (RU)
> Что такое BroadcastReceiver и ContentProvider в Android?

# Question (EN)
> What are BroadcastReceiver and ContentProvider in Android?

---

## Ответ (RU)

### BroadcastReceiver

**Определение**: Компонент Android, который получает и обрабатывает широковещательные сообщения (broadcasts) от системы или других приложений. [[c-broadcast-receiver]] следует определённому жизненному циклу.

**Основные виды**:
- System broadcasts (батарея, сеть, загрузка и т.д.)
- Custom broadcasts (между компонентами приложения)

**Использование**:
```kotlin
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Обработка события (макс. 10 сек)
    }
}
```

**Регистрация**:
- В Manifest (статическая) - ограничена с Android 8+
- В коде (динамическая) - работает только пока компонент жив

### ContentProvider

**Определение**: Компонент для структурированного доступа к данным приложения. Предоставляет единый интерфейс для чтения/записи данных между приложениями.

**Основные методы**:
- `query()` - чтение данных
- `insert()` - добавление
- `update()` - обновление
- `delete()` - удаление

**Использование**:
```kotlin
class MyProvider : ContentProvider() {
    override fun query(uri: Uri, ...): Cursor? { ... }
    override fun insert(uri: Uri, values: ContentValues?): Uri? { ... }
    // и т.д.
}
```

**Когда использовать**:
- Sharing data between apps
- Централизованное управление данными
- Интеграция с Contacts, Calendar и т.д.

## Answer (EN)

### BroadcastReceiver

**Definition**: An Android component that receives and handles broadcast messages from the system or other applications.

**Types**:
- System broadcasts (battery, network, boot, etc.)
- Custom broadcasts (between app components)

**Usage**:
```kotlin
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Handle event (max 10 sec)
    }
}
```

**Registration**:
- In Manifest (static) - restricted since Android 8+
- In code (dynamic) - works only while component is alive

### ContentProvider

**Definition**: A component for structured access to app data. Provides a unified interface for reading/writing data between applications.

**Core methods**:
- `query()` - read data
- `insert()` - add
- `update()` - update
- `delete()` - delete

**Usage**:
```kotlin
class MyProvider : ContentProvider() {
    override fun query(uri: Uri, ...): Cursor? { ... }
    override fun insert(uri: Uri, values: ContentValues?): Uri? { ... }
    // etc.
}
```

**When to use**:
- Sharing data between apps
- Centralized data management
- Integration with Contacts, Calendar, etc.

## Follow-ups

- How to avoid ANR in onReceive and delegate longer work safely?
- How to secure a ContentProvider (read/write permissions, Uri permissions)?
- When to use WorkManager vs BroadcastReceiver for deferred work?

## References

- https://developer.android.com/guide/components/broadcasts
- https://developer.android.com/guide/topics/providers/content-provider-basics

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]]
- [[q-android-app-components--android--easy]]

### Related (Same Level)
- [[q-android-service-types--android--easy]]
- [[q-android-services-purpose--android--easy]]

### Advanced (Harder)
- [[q-android-modularization--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]
