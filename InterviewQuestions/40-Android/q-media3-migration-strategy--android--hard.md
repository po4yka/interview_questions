---
id: android-615
title: Media3 Migration Strategy / Стратегия миграции на Media3
aliases:
  - Media3 Migration Strategy
  - Стратегия миграции на Media3
topic: android
subtopics:
  - media
  - media3
  - exoplayer
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-media3
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/media3
  - android/exoplayer
  - streaming
  - difficulty/hard
sources:
  - url: https://developer.android.com/guide/topics/media/media3/getting-started
    note: Official Media3 migration guide
  - url: https://medium.com/androiddevelopers/media3-from-exoplayer-migration
    note: ExoPlayer to Media3 migration best practices
---

# Вопрос (RU)
> Как мигрировать с ExoPlayer на Media3: перестроить архитектуру плеера, перенести UI, сессии и офлайн-функциональность, не ломая авто/TV интеграцию?

# Question (EN)
> How do you migrate an ExoPlayer-based stack to Media3, covering player architecture, UI, session services, and offline features without breaking Auto/TV integrations?

---

## Ответ (RU)

### 1. Переезд зависимостей

- Замените `com.google.android.exoplayer:exoplayer` на `androidx.media3:media3-exoplayer`.
- Добавьте `media3-ui`, `media3-session`, `media3-cast` в зависимости от функций.
- Обновите namespace (`com.google.android.exoplayer2.*` → `androidx.media3.*`).

### 2. Перестройка Player слоя

```kotlin
val player = ExoPlayer.Builder(context)
    .setTrackSelector(DefaultTrackSelector(context))
    .setLoadControl(DefaultLoadControl())
    .build()
```

- `SimpleExoPlayer` больше нет; используйте `ExoPlayer.Builder`.
- Слушатели — `Player.Listener` (один интерфейс вместо EventListener).
- Используйте `MediaItem.Builder` (поддерживает DRM, Clipping).

### 3. Session & Service

```kotlin
class PlaybackService : MediaSessionService() {
    private lateinit var mediaSession: MediaSession

    override fun onCreate() {
        super.onCreate()
        val player = providePlayer()
        mediaSession = MediaSession.Builder(this, player)
            .setId("app_session")
            .build()
    }
}
```

- `MediaSessionService` заменяет `MediaBrowserServiceCompat`.
- Для Android Auto/Assistant используйте `MediaNotification.Provider`.
- Авто и TV используют один и тот же session contract.

### 4. UI миграция

- `StyledPlayerView` живёт в `media3-ui`; замените XML namespace.
- Для Compose: `AndroidView` оборачивает `StyledPlayerView` или используйте сторонние Compose wrappers.
- Управление контроллерами — `PlayerView.ControllerVisibilityListener`.

### 5. Offline и DRM

- Offline — `DownloadService` + `DownloadManager` из `media3-exoplayer`.
- DRM — `MediaItem.DrmConfiguration` (Widevine, PlayReady).
- Key rotation и license expiry теперь внутри `MediaItem`.

### 6. Тестирование

- Unit: `PlayerTestRunner`, `FakeMediaSource`.
- Instrumented: `MediaControllerTestRule` для session layer.
- Нагрузочное: `StressTestPlayer.Builder`.

### 7. План миграции

1. Параллельно держите старый и новый player за Feature Flag.
2. Переведите session/service, затем UI.
3. Закройте кастомные listener-обёртки (многие API теперь упрощены).
4. Обновите интеграции Auto/TV, проверяя templates (версия car library > 1.3).

---

## Answer (EN)

### Migration Checklist
- Swap ExoPlayer dependencies for Media3 modules and update package imports.
- Replace `SimpleExoPlayer` with `ExoPlayer.Builder`, migrate listeners to `Player.Listener`.
- Rebuild session services using `MediaSessionService` and `MediaSession.Builder`.
- Update UI to `StyledPlayerView` from `media3-ui`, integrate with Compose via `AndroidView`.
- Port offline download stacks to `DownloadService`/`DownloadManager` and configure `MediaItem.DrmConfiguration`.
- Validate Android Auto/TV by exercising templates against the new session contract.

### Testing
- Use Media3 test artifacts (`PlayerTestRunner`, `MediaControllerTestRule`) to automate regression testing.
- Profile playback (startup time, rebuffer count) before/after migration using ExoPlayer analytics listener equivalents.

---

## Follow-ups
- Как мигрировать кастомный `RenderersFactory` или `DataSource.Factory`?
- Какие изменения требуются для интеграции с Chromecast (MediaRouter → media3-cast)?
- Как обеспечить совместимость с Android Auto 6+ и Media3 session API?

## References
- [[c-media3]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/guide/topics/media/media3/getting-started
- https://medium.com/androiddevelopers/media3-from-exoplayer-migration

## Related Questions

- [[c-media3]]
- [[q-android-coverage-gaps--android--hard]]
