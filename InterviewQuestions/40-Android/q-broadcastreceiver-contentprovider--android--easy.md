---
id: 20251016-162753
title: BroadcastReceiver and ContentProvider / BroadcastReceiver и ContentProvider
aliases: [BroadcastReceiver and ContentProvider, BroadcastReceiver и ContentProvider]
topic: android
subtopics: [broadcast-receiver, content-provider]
question_kind: android
difficulty: easy
original_language: ru
language_tags: [ru, en]
status: draft
moc: moc-android
related: [q-android-manifest-file--android--easy, q-android-app-components--android--easy, q-android-service-types--android--easy]
created: 2025-10-15
updated: 2025-10-20
tags: [android/broadcast-receiver, android/content-provider, intent, data-sharing, difficulty/easy]
---

# Вопрос (RU)
> Что такое BroadcastReceiver и ContentProvider? В чем их назначение и ключевые отличия?

# Question (EN)
> What are BroadcastReceiver and ContentProvider? What are their purposes and key differences?

---

## Ответ (RU)

- **BroadcastReceiver**: компонент для реакции на широковещательные события (интенты) системы/приложений.
  - **Назначение**: подписка на события без UI; запуск логики по факту события.
  - **Регистрация**: манифест (статически) или в коде (динамически).
  - **Особенности**: очень короткая работа в onReceive; для долгих задач — Service/WorkManager.
  - **Применение**: сеть/питание/BOOT_COMPLETED/пользовательские broadcast’ы.
  - **Сниппет**:
```xml
<receiver android:name=".NetworkReceiver" android:exported="false">
    <intent-filter>
        <action android:name="android.net.conn.CONNECTIVITY_CHANGE" />
    </intent-filter>
</receiver>
```

- **ContentProvider**: стандартный интерфейс доступа к структурированным данным между приложениями.
  - **Назначение**: CRUD-операции через Uri/ContentResolver; граница процесса/приложения.
  - **Безопасность**: права/пермишены на уровне провайдера и Uri; контракт через authority.
  - **Применение**: контакты, медиа, настройки, собственные данные для шаринга.
  - **Сниппет**:
```xml
<provider
    android:name=".ContactsProvider"
    android:authorities="com.example.contacts"
    android:exported="true" />
```

- **Сравнение**:
  - BroadcastReceiver: реакция на события → триггер логики; вход: Intent; нет данных.
  - ContentProvider: доступ к данным → query/insert/update/delete; вход: Uri; выход: Cursor/число/Uri.

## Answer (EN)

- **BroadcastReceiver**: component for reacting to system/app broadcast events (intents).
  - **Purpose**: subscribe to events without UI; trigger logic on event.
  - **Registration**: manifest (static) or code (dynamic).
  - **Notes**: keep onReceive short; use Service/WorkManager for long work.
  - **Use cases**: connectivity/power/BOOT_COMPLETED/custom broadcasts.
  - **Snippet**:
```xml
<receiver android:name=".NetworkReceiver" android:exported="false">
    <intent-filter>
        <action android:name="android.net.conn.CONNECTIVITY_CHANGE" />
    </intent-filter>
</receiver>
```

- **ContentProvider**: standard interface for structured data access across apps.
  - **Purpose**: CRUD via Uri/ContentResolver; process/app boundary.
  - **Security**: permissions at provider and Uri levels; authority defines contract.
  - **Use cases**: contacts, media, settings, your own shared data.
  - **Snippet**:
```xml
<provider
    android:name=".ContactsProvider"
    android:authorities="com.example.contacts"
    android:exported="true" />
```

- **Comparison**:
  - BroadcastReceiver: event reaction → trigger logic; input: Intent; no data payload returned.
  - ContentProvider: data access → query/insert/update/delete; input: Uri; output: Cursor/count/Uri.

---

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
