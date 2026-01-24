---
id: android-lc-014
title: onTrimMemory Levels / Уровни onTrimMemory
aliases: []
topic: android
subtopics:
- lifecycle
- memory
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Android interview preparation
status: draft
moc: moc-android
related:
- c-lifecycle
- c-memory
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/memory
- difficulty/medium
anki_cards:
- slug: android-lc-014-0-en
  language: en
  anki_id: 1769172284207
  synced_at: '2026-01-23T16:45:06.208909'
- slug: android-lc-014-0-ru
  language: ru
  anki_id: 1769172284233
  synced_at: '2026-01-23T16:45:06.210092'
---
# Question (EN)
> What are onTrimMemory levels and how to handle them?

# Vopros (RU)
> Какие уровни onTrimMemory и как их обрабатывать?

---

## Answer (EN)

**onTrimMemory()** is a callback that tells your app to release memory when system is under memory pressure.

**Levels when app is RUNNING (visible):**
```kotlin
TRIM_MEMORY_RUNNING_MODERATE  // System low on memory, app running
TRIM_MEMORY_RUNNING_LOW       // System very low, app might be affected
TRIM_MEMORY_RUNNING_CRITICAL  // System critical, app will be killed if no release
```

**Levels when app is CACHED (background):**
```kotlin
TRIM_MEMORY_UI_HIDDEN     // UI no longer visible, release UI resources
TRIM_MEMORY_BACKGROUND    // In LRU list, release what you can
TRIM_MEMORY_MODERATE      // Near middle of LRU list
TRIM_MEMORY_COMPLETE      // Near end of LRU, will be killed soon
```

**Implementation:**
```kotlin
class MyApplication : Application(), ComponentCallbacks2 {

    override fun onTrimMemory(level: Int) {
        super.onTrimMemory(level)

        when (level) {
            // App in foreground, system under pressure
            TRIM_MEMORY_RUNNING_MODERATE -> {
                // Release non-critical caches
                imageLoader.trimMemory(level)
            }

            TRIM_MEMORY_RUNNING_LOW,
            TRIM_MEMORY_RUNNING_CRITICAL -> {
                // Release everything possible
                clearAllCaches()
            }

            // App backgrounded
            TRIM_MEMORY_UI_HIDDEN -> {
                // Release UI resources (bitmaps, views)
                releaseUiResources()
            }

            // App in background, may be killed
            TRIM_MEMORY_BACKGROUND,
            TRIM_MEMORY_MODERATE -> {
                // Moderate cleanup
                trimCaches(50) // Keep 50%
            }

            TRIM_MEMORY_COMPLETE -> {
                // Release everything, will be killed soon
                clearAllCaches()
            }
        }
    }
}
```

**Activity level callback:**
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onTrimMemory(level: Int) {
        super.onTrimMemory(level)
        if (level >= TRIM_MEMORY_UI_HIDDEN) {
            // Activity not visible, release view-related caches
            glide.clearMemory()
        }
    }
}
```

**Common cacheable resources:**
- Image caches (Glide, Coil, Picasso)
- Database query caches
- Parsed JSON/XML data
- Downloaded assets not currently displayed

**Integration with image libraries:**
```kotlin
// Glide
Glide.get(context).trimMemory(level)

// Coil
imageLoader.memoryCache?.trimMemory(level)

// Picasso
Picasso.get().evictAll()
```

**Key insight:** `TRIM_MEMORY_UI_HIDDEN` is the best time to release UI resources - it's called immediately when app goes to background, before any memory pressure.

## Otvet (RU)

**onTrimMemory()** - callback, который сообщает приложению освободить память когда система испытывает нехватку памяти.

**Уровни когда приложение РАБОТАЕТ (видимо):**
```kotlin
TRIM_MEMORY_RUNNING_MODERATE  // Системе мало памяти, приложение работает
TRIM_MEMORY_RUNNING_LOW       // Системе очень мало, приложение может пострадать
TRIM_MEMORY_RUNNING_CRITICAL  // Система в критическом состоянии, приложение будет убито если не освободить
```

**Уровни когда приложение ЗАКЭШИРОВАНО (в фоне):**
```kotlin
TRIM_MEMORY_UI_HIDDEN     // UI больше не виден, освободить UI ресурсы
TRIM_MEMORY_BACKGROUND    // В LRU списке, освободить что можно
TRIM_MEMORY_MODERATE      // Около середины LRU списка
TRIM_MEMORY_COMPLETE      // Около конца LRU, скоро будет убито
```

**Реализация:**
```kotlin
class MyApplication : Application(), ComponentCallbacks2 {

    override fun onTrimMemory(level: Int) {
        super.onTrimMemory(level)

        when (level) {
            // Приложение на переднем плане, система под давлением
            TRIM_MEMORY_RUNNING_MODERATE -> {
                // Освободить некритичные кэши
                imageLoader.trimMemory(level)
            }

            TRIM_MEMORY_RUNNING_LOW,
            TRIM_MEMORY_RUNNING_CRITICAL -> {
                // Освободить всё возможное
                clearAllCaches()
            }

            // Приложение ушло в фон
            TRIM_MEMORY_UI_HIDDEN -> {
                // Освободить UI ресурсы (bitmaps, views)
                releaseUiResources()
            }

            // Приложение в фоне, может быть убито
            TRIM_MEMORY_BACKGROUND,
            TRIM_MEMORY_MODERATE -> {
                // Умеренная очистка
                trimCaches(50) // Оставить 50%
            }

            TRIM_MEMORY_COMPLETE -> {
                // Освободить всё, скоро будет убито
                clearAllCaches()
            }
        }
    }
}
```

**Callback на уровне Activity:**
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onTrimMemory(level: Int) {
        super.onTrimMemory(level)
        if (level >= TRIM_MEMORY_UI_HIDDEN) {
            // Activity не видна, освободить кэши связанные с view
            glide.clearMemory()
        }
    }
}
```

**Типичные кэшируемые ресурсы:**
- Кэши изображений (Glide, Coil, Picasso)
- Кэши запросов к базе данных
- Распарсенные JSON/XML данные
- Загруженные ассеты, не отображаемые сейчас

**Интеграция с библиотеками изображений:**
```kotlin
// Glide
Glide.get(context).trimMemory(level)

// Coil
imageLoader.memoryCache?.trimMemory(level)

// Picasso
Picasso.get().evictAll()
```

**Ключевое понимание:** `TRIM_MEMORY_UI_HIDDEN` - лучшее время для освобождения UI ресурсов - он вызывается сразу когда приложение уходит в фон, до любого давления на память.

---

## Follow-ups
- What is the difference between onTrimMemory and onLowMemory?
- How to profile memory usage in Android?
- When does system kill apps for memory?

## References
- [[c-lifecycle]]
- [[c-memory]]
- [[moc-android]]
