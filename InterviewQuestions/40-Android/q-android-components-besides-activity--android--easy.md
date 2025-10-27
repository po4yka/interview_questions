---
id: 20251015-132630
title: Android Components Besides Activity / Компоненты Android кроме Activity
aliases: [Android Components Besides Activity, Компоненты Android кроме Activity]
topic: android
subtopics: [activity, service, fragment]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-components--android--easy, q-fragment-vs-activity-lifecycle--android--medium, q-service-types-android--android--easy, c-service, c-lifecycle]
created: 2025-10-15
updated: 2025-10-27
tags: [android/activity, android/service, android/fragment, difficulty/easy]
sources:
  - https://developer.android.com/guide/components/fundamentals
  - https://developer.android.com/guide/components/services
  - https://developer.android.com/guide/components/broadcasts
---
# Вопрос (RU)

Какие компоненты Android существуют помимо Activity?

---

# Question (EN)

What Android components exist besides Activity?

## Answer (EN)

### 1. Service
Background operations without UI. Runs independently of Activity [[c-lifecycle|lifecycle]].

```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Background work execution
        downloadFile(intent?.getStringExtra("url"))
        return START_STICKY // ✅ Restart if killed
    }
}
```

**Key points**: Long-running tasks, music playback, downloads.

---

### 2. BroadcastReceiver
Responds to system-wide broadcast announcements.

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
        // ✅ Handle battery state change
    }
}
```

**Use cases**: Battery changes, connectivity, SMS received.

---

### 3. ContentProvider
Structured data sharing between applications.

```kotlin
class NotesProvider : ContentProvider() {
    override fun query(uri: Uri, projection: Array<String>?, ...): Cursor? {
        // ✅ Return data to requesting app
        return database.query(...)
    }
}
```

**Purpose**: Cross-app data access, unified data layer.

---

### 4. Fragment
Reusable UI module with own [[c-lifecycle|lifecycle]].

```kotlin
class ListFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.fragment_list, container, false) // ✅ Create UI
    }
}
```

**Benefits**: Modular UI, reusability, back stack support.

---

### Component Comparison

| Component | Purpose | Lifecycle | UI |
|-----------|---------|-----------|-----|
| **Service** | Background work | Independent | ❌ No |
| **BroadcastReceiver** | System events | Short-lived | ❌ No |
| **ContentProvider** | Data sharing | Singleton | ❌ No |
| **Fragment** | UI modules | Tied to Activity | ✅ Yes |

---

## Ответ (RU)

### 1. Service (Сервис)
Фоновые операции без UI. Работает независимо от жизненного цикла Activity.

```kotlin
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Выполнение фоновой работы
        downloadFile(intent?.getStringExtra("url"))
        return START_STICKY // ✅ Перезапуск при завершении системой
    }
}
```

**Применение**: Длительные задачи, воспроизведение музыки, загрузки.

---

### 2. BroadcastReceiver (Приёмник событий)
Реагирует на системные broadcast-сообщения.

```kotlin
class BatteryReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
        // ✅ Обработка изменения состояния батареи
    }
}
```

**Сценарии**: Изменение батареи, сети, получение SMS.

---

### 3. ContentProvider (Поставщик контента)
Структурированный обмен данными между приложениями.

```kotlin
class NotesProvider : ContentProvider() {
    override fun query(uri: Uri, projection: Array<String>?, ...): Cursor? {
        // ✅ Возврат данных запрашивающему приложению
        return database.query(...)
    }
}
```

**Назначение**: Межприложенский доступ к данным, единый слой данных.

---

### 4. Fragment (Фрагмент)
Переиспользуемый UI-модуль с собственным жизненным циклом.

```kotlin
class ListFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.fragment_list, container, false) // ✅ Создание UI
    }
}
```

**Преимущества**: Модульный UI, переиспользуемость, поддержка back stack.

---

### Сравнение компонентов

| Компонент | Назначение | Жизненный цикл | UI |
|-----------|------------|----------------|-----|
| **Service** | Фоновая работа | Независимый | ❌ Нет |
| **BroadcastReceiver** | Системные события | Краткосрочный | ❌ Нет |
| **ContentProvider** | Обмен данными | Singleton | ❌ Нет |
| **Fragment** | UI-модули | Привязан к Activity | ✅ Да |

---

## Follow-ups

- What's the difference between Started Service and Bound Service?
- When should you use Fragment vs Activity?
- How does ContentProvider ensure data security?
- What's the lifecycle of BroadcastReceiver?

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]] - App components overview

### Same Level
- [[q-service-types-android--android--easy]] - Service types
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Fragment lifecycle