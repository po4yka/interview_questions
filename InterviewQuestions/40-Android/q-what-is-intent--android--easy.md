---
id: 20251012-122711160
title: "What Is Intent / Что такое Intent"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [android/intents-deeplinks, component-communication, explicit-intent, implicit-intent, intent, intents-deeplinks, difficulty/easy]
---

# Question (EN)

> What is Intent?

# Вопрос (RU)

> Что такое Intent?

## Answer (EN)

**Intent** is a messaging object used to **communicate between Android components** (Activity, Service, BroadcastReceiver) and between apps.

**Types:**

**1. Explicit Intent** - Specific component

```kotlin
// Start specific Activity
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("user_id", 123)
startActivity(intent)

// Start specific Service
startService(Intent(this, MusicService::class.java))
```

**2. Implicit Intent** - Action-based

```kotlin
// Open browser
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(intent)

// Share text
val intent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Hello!")
}
startActivity(Intent.createChooser(intent, "Share via"))
```

**Common Uses:**

**Start Activity:**

```kotlin
startActivity(Intent(this, MainActivity::class.java))
```

**Start Service:**

```kotlin
startService(Intent(this, DownloadService::class.java))
```

**Send Broadcast:**

```kotlin
sendBroadcast(Intent("com.example.CUSTOM_ACTION"))
```

**Pass Data:**

```kotlin
val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("name", "John")
intent.putExtra("age", 30)
startActivity(intent)

// Receive data
val name = intent.getStringExtra("name")
val age = intent.getIntExtra("age", 0)
```

**Summary:**

Intent is the **glue** that connects Android components, allowing them to communicate and pass data.

## Ответ (RU)

Intent — это механизм для связи между компонентами приложения или между приложениями. Позволяет запускать Activity, Service, отправлять broadcast и передавать данные.

---

## Follow-ups

-   What are security pitfalls with implicit intents and how to avoid them?
-   When to use PendingIntent instead of a direct Intent?
-   How do intent filters influence implicit intent resolution?

## References

-   `https://developer.android.com/guide/components/intents-filters` — Intents and intent filters
-   `https://developer.android.com/training/sharing/send` — Share data using intents

## Related Questions

### Related (Easy)

-   [[q-architecture-components-libraries--android--easy]] - Fundamentals
-   [[q-what-is-the-main-application-execution-thread--android--easy]] - Fundamentals
-   [[q-what-unifies-android-components--android--easy]] - Fundamentals
-   [[q-android-components-besides-activity--android--easy]] - Fundamentals

### Advanced (Harder)

-   [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
-   [[q-intent-filters-android--android--medium]] - Fundamentals
-   [[q-anr-application-not-responding--android--medium]] - Fundamentals
