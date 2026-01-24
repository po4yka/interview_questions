---
id: android-lc-013
title: Multi-Window Mode Lifecycle / Жизненный цикл Multi-Window
aliases: []
topic: android
subtopics:
- lifecycle
- multiwindow
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
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- difficulty/medium
anki_cards:
- slug: android-lc-013-0-en
  language: en
  anki_id: 1769172279182
  synced_at: '2026-01-23T16:45:06.151805'
- slug: android-lc-013-0-ru
  language: ru
  anki_id: 1769172279207
  synced_at: '2026-01-23T16:45:06.153626'
---
# Question (EN)
> How does Activity lifecycle differ in multi-window mode?

# Vopros (RU)
> Чем отличается lifecycle Activity в режиме multi-window?

---

## Answer (EN)

**Multi-window mode** (split-screen, picture-in-picture) has different lifecycle behavior than single-window mode.

**Key difference (API 24-29):**
- **Single window**: Only one Activity is RESUMED
- **Multi-window**: Only the focused Activity is RESUMED, others are PAUSED

**API 30+ change (multi-resume):**
- All visible Activities can be RESUMED simultaneously
- Requires opt-in: `android:resizeableActivity="true"` and proper handling

**Lifecycle in split-screen (pre-API 30):**
```
App A (focused):    RESUMED
App B (visible):    PAUSED  <- Still visible but paused!

[User taps App B]

App A (visible):    PAUSED
App B (focused):    RESUMED
```

**Multi-resume (API 30+):**
```kotlin
// In AndroidManifest.xml
<activity
    android:name=".MainActivity"
    android:resizeableActivity="true">
    <meta-data
        android:name="android.allow_multiple_resumed_activities"
        android:value="true" />
</activity>
```

**Handling properly:**
```kotlin
override fun onTopResumedActivityChanged(isTopResumed: Boolean) {
    super.onTopResumedActivityChanged(isTopResumed)
    if (isTopResumed) {
        // Activity has focus - acquire exclusive resources
        acquireCamera()
    } else {
        // Activity lost focus - release exclusive resources
        releaseCamera()
    }
}

override fun onPause() {
    super.onPause()
    // Don't stop video playback here in multi-window!
    if (!isInMultiWindowMode) {
        pauseVideo()
    }
}
```

**Picture-in-Picture (PiP):**
```kotlin
// Enter PiP mode
enterPictureInPictureMode(
    PictureInPictureParams.Builder()
        .setAspectRatio(Rational(16, 9))
        .build()
)

// Check if in PiP
override fun onPictureInPictureModeChanged(
    isInPiP: Boolean,
    newConfig: Configuration
) {
    if (isInPiP) {
        // Hide UI controls
        hideControls()
    } else {
        showControls()
    }
}
```

**Configuration change on multi-window:**
```kotlin
// Entering/exiting multi-window triggers config change
// Handle in manifest or code:
android:configChanges="screenSize|screenLayout|smallestScreenSize"

override fun onConfigurationChanged(newConfig: Configuration) {
    super.onConfigurationChanged(newConfig)
    // Adjust layout for new size
}
```

**Common mistakes:**
- Stopping media in `onPause()` (visible but paused in multi-window)
- Not handling exclusive resources (camera, microphone)
- Hardcoding window size assumptions

## Otvet (RU)

**Multi-window режим** (split-screen, picture-in-picture) имеет другое поведение lifecycle чем single-window режим.

**Ключевое отличие (API 24-29):**
- **Single window**: Только одна Activity в RESUMED
- **Multi-window**: Только Activity в фокусе RESUMED, остальные PAUSED

**Изменение в API 30+ (multi-resume):**
- Все видимые Activities могут быть RESUMED одновременно
- Требует opt-in: `android:resizeableActivity="true"` и правильную обработку

**Lifecycle в split-screen (до API 30):**
```
App A (в фокусе):   RESUMED
App B (видимо):     PAUSED  <- Всё ещё видимо, но paused!

[Пользователь тапает App B]

App A (видимо):     PAUSED
App B (в фокусе):   RESUMED
```

**Multi-resume (API 30+):**
```kotlin
// В AndroidManifest.xml
<activity
    android:name=".MainActivity"
    android:resizeableActivity="true">
    <meta-data
        android:name="android.allow_multiple_resumed_activities"
        android:value="true" />
</activity>
```

**Правильная обработка:**
```kotlin
override fun onTopResumedActivityChanged(isTopResumed: Boolean) {
    super.onTopResumedActivityChanged(isTopResumed)
    if (isTopResumed) {
        // Activity в фокусе - захватить эксклюзивные ресурсы
        acquireCamera()
    } else {
        // Activity потеряла фокус - освободить эксклюзивные ресурсы
        releaseCamera()
    }
}

override fun onPause() {
    super.onPause()
    // Не останавливайте воспроизведение видео здесь в multi-window!
    if (!isInMultiWindowMode) {
        pauseVideo()
    }
}
```

**Picture-in-Picture (PiP):**
```kotlin
// Войти в режим PiP
enterPictureInPictureMode(
    PictureInPictureParams.Builder()
        .setAspectRatio(Rational(16, 9))
        .build()
)

// Проверить в PiP ли
override fun onPictureInPictureModeChanged(
    isInPiP: Boolean,
    newConfig: Configuration
) {
    if (isInPiP) {
        // Скрыть элементы управления
        hideControls()
    } else {
        showControls()
    }
}
```

**Изменение конфигурации при multi-window:**
```kotlin
// Вход/выход из multi-window вызывает config change
// Обработать в манифесте или коде:
android:configChanges="screenSize|screenLayout|smallestScreenSize"

override fun onConfigurationChanged(newConfig: Configuration) {
    super.onConfigurationChanged(newConfig)
    // Адаптировать layout к новому размеру
}
```

**Частые ошибки:**
- Остановка медиа в `onPause()` (видимо но paused в multi-window)
- Не обрабатывать эксклюзивные ресурсы (камера, микрофон)
- Хардкод предположений о размере окна

---

## Follow-ups
- How to test multi-window behavior?
- What is onTopResumedActivityChanged?
- How to handle Picture-in-Picture actions?

## References
- [[c-lifecycle]]
- [[moc-android]]
