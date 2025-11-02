---
id: android-405
title: "Intent в Android / What Is Intent"
aliases: [Intent, Android Intent, Явный Intent, Неявный Intent]
topic: android
subtopics: [intents-deeplinks]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-intent-filters-android--android--medium, q-what-are-services-for--android--easy, q-android-components-besides-activity--android--easy]
created: 2025-10-15
updated: 2025-10-27
sources: [https://developer.android.com/guide/components/intents-filters]
tags: [android/intents-deeplinks, explicit-intent, implicit-intent, difficulty/easy]
---
# Вопрос (RU)

> Что такое Intent?

# Question (EN)

> What is Intent?

## Ответ (RU)

**Intent** — это объект-сообщение, используемый для **связи между компонентами Android** (Activity, Service, BroadcastReceiver) и между приложениями.

**Типы:**

**1. Explicit Intent** - Конкретный компонент

```kotlin
// Запуск конкретной Activity
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("user_id", 123)
startActivity(intent)

// Запуск конкретного Service
startService(Intent(this, MusicService::class.java))
```

**2. Implicit Intent** - На основе действия

```kotlin
// Открыть браузер
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(intent)

// Поделиться текстом
val intent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Hello!")
}
startActivity(Intent.createChooser(intent, "Поделиться через"))
```

**Передача данных:**

```kotlin
// ✅ Отправка
val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("name", "John")
startActivity(intent)

// ✅ Получение
val name = intent.getStringExtra("name")
```

**Итог:** Intent — связующее звено между компонентами Android.

## Answer (EN)

**Intent** is a messaging object used to **communicate between Android components** (Activity, Service, BroadcastReceiver) and between apps.

**Types:**

**1. Explicit Intent** — specific component

```kotlin
// ✅ Start specific Activity
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("user_id", 123)
startActivity(intent)
```

**2. Implicit Intent** — action-based

```kotlin
// ✅ Open browser
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(intent)

// ✅ Share text
val intent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Hello!")
}
startActivity(Intent.createChooser(intent, "Share via"))
```

**Pass data:**

```kotlin
// ✅ Send
val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("name", "John")
startActivity(intent)

// ✅ Receive
val name = intent.getStringExtra("name")
```

**Summary:** Intent is the glue connecting Android components.

---

## Follow-ups

- What are security pitfalls with implicit intents?
- When to use PendingIntent instead of direct Intent?
- How do intent filters work?

## References

- https://developer.android.com/guide/components/intents-filters
- https://developer.android.com/training/sharing/send

## Related Questions

### Related (Easy)
- [[q-what-are-services-for--android--easy]]
- [[q-android-components-besides-activity--android--easy]]

### Advanced (Harder)
- [[q-intent-filters-android--android--medium]]
