---
id: android-405
title: Intent в Android / What Is Intent
aliases: [Android Intent, Intent, Неявный Intent, Явный Intent]
topic: android
subtopics:
  - intents-deeplinks
question_kind: theory
difficulty: easy
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-intent
  - q-android-components-besides-activity--android--easy
  - q-android-lint-tool--android--medium
  - q-intent-filters-android--android--medium
  - q-main-thread-android--android--medium
  - q-parsing-optimization-android--android--medium
  - q-what-are-services-for--android--easy
created: 2025-10-15
updated: 2025-10-27
sources:
  - "https://developer.android.com/guide/components/intents-filters"
tags: [android/intents-deeplinks, difficulty/easy, explicit-intent, implicit-intent]

date created: Saturday, November 1st 2025, 12:47:08 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---
# Вопрос (RU)

> Что такое `Intent`?

# Question (EN)

> What is `Intent`?

## Ответ (RU)

**`Intent`** — это объект-сообщение, используемый для **связи между компонентами Android** (`Activity`, `Service`, `BroadcastReceiver`) и между приложениями.

**Типы:**

**1. Explicit `Intent`** - Конкретный компонент

```kotlin
// Запуск конкретной Activity
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("user_id", 123)
startActivity(intent)

// Запуск конкретного Service
startService(Intent(this, MusicService::class.java))
```

**2. Implicit `Intent`** - На основе действия

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

// ✅ Получение (например, в Activity через getIntent()/intent)
val name = intent.getStringExtra("name")
```

**Broadcast:** `Intent` также используется для отправки и приёма широковещательных сообщений через `BroadcastReceiver` (sendBroadcast и т.п.).

**Итог:** `Intent` — связующее звено между компонентами Android.

## Answer (EN)

**`Intent`** is a messaging object used to **communicate between Android components** (`Activity`, `Service`, `BroadcastReceiver`) and between apps.

**Types:**

**1. Explicit `Intent`** — specific component

```kotlin
// ✅ Start specific Activity
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("user_id", 123)
startActivity(intent)

// ✅ Start specific Service
startService(Intent(this, MusicService::class.java))
```

**2. Implicit `Intent`** — action-based

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

// ✅ Receive (e.g., in Activity via getIntent()/intent)
val name = intent.getStringExtra("name")
```

**Broadcast:** `Intent` is also used to send and receive broadcasts via `BroadcastReceiver` (e.g., sendBroadcast).

**Summary:** `Intent` is the glue connecting Android components.

---

## Дополнительные Вопросы (RU)

- Какие проблемы безопасности могут возникнуть при использовании неявных `Intent`?
- Когда следует использовать `PendingIntent` вместо прямого `Intent`?
- Как работают фильтры интентов (`intent-filter`)?

## Follow-ups

- What are security pitfalls with implicit intents?
- When to use PendingIntent instead of direct `Intent`?
- How do intent filters work?

## Ссылки (RU)

- [[c-intent]]
- "https://developer.android.com/guide/components/intents-filters"
- "https://developer.android.com/training/sharing/send"

## References

- [[c-intent]]
- https://developer.android.com/guide/components/intents-filters
- https://developer.android.com/training/sharing/send

## Связанные Вопросы (RU)

### Предпосылки / Концепты

- [[c-intent]]

### Связанные (Easy)
- [[q-what-are-services-for--android--easy]]
- [[q-android-components-besides-activity--android--easy]]

### Продвинутые (Сложнее)
- [[q-intent-filters-android--android--medium]]

## Related Questions

### Prerequisites / Concepts

- [[c-intent]]

### Related (Easy)
- [[q-what-are-services-for--android--easy]]
- [[q-android-components-besides-activity--android--easy]]

### Advanced (Harder)
- [[q-intent-filters-android--android--medium]]