---id: android-615
title: Media3 Migration Strategy / Стратегия миграции на Media3
aliases: [Media3 Migration Strategy, Стратегия миграции на Media3]
topic: android
subtopics: [media]
question_kind: android
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-surfaces, c-android-tv, c-media3, q-global-localization-strategy--android--hard, q-media3-transformer-workflows--android--hard, q-scoped-storage-migration-strategy--android--hard]
created: 2024-11-02
updated: 2025-11-10
tags: [android/media, difficulty/hard]
sources:
  - "https://developer.android.com/guide/topics/media/media3/getting-started"
  - "https://medium.com/androiddevelopers/media3-from-exoplayer-migration"

---
# Вопрос (RU)
> Как мигрировать с ExoPlayer на Media3: перестроить архитектуру плеера, перенести UI, сессии и офлайн-функциональность, не ломая авто/TV интеграцию?

# Question (EN)
> How do you migrate an ExoPlayer-based stack to Media3, covering player architecture, UI, session services, and offline features without breaking Auto/TV integrations?

---

## Ответ (RU)

### Краткий Вариант

- Последовательно перенесите зависимости на Media3.
- Постройте единый `MediaSession`/`MediaLibrarySession`-центричный слой.
- Обновите UI на `StyledPlayerView`/Compose-обёртки.
- Мигрируйте offline/DRM на `MediaItem` + Media3 `DownloadService`/`DownloadManager`.
- Проведите поэтапную валидацию Auto/TV/Assistant интеграций за feature flag.

### Подробный Вариант

#### Требования

- Функциональные:
  - Сохранить текущий UX и возможности воспроизведения (VOD/Live, seek, subtitles, audio tracks).
  - Обеспечить поддержку Android TV, Android Auto, cast, ассистентов и медиасессий.
  - Сохранить/перенести offline-загрузки и DRM.
- Нефункциональные:
  - Минимизировать даунтайм и регрессии (миграция поэтапно, через feature flags).
  - Поддерживать расширяемую архитектуру (инкапсулированный player layer, session layer).
  - Обеспечить наблюдаемость (логирование, метрики сессий и ошибок).

#### Архитектура

- Ввести абстрактный player facade поверх Media3 (`Player` + `MediaSession`/`MediaLibrarySession`), скрывающий детали.
- Использовать `MediaSessionService`/`MediaLibraryService` как единый backend для UI, Auto, TV, ассистентов.
- Для UI использовать общий компонент (`StyledPlayerView` или Compose-обёртку), подключённый к одному `MediaSession`.
- Вынести offline/DRM в отдельный модуль, использующий Media3 `DownloadService`, `DownloadManager` и `MediaItem.DrmConfiguration`.

#### 1. Переезд Зависимостей

- Замените `com.google.android.exoplayer:exoplayer` на `androidx.media3:media3-exoplayer`.
- Добавьте при необходимости: `media3-ui`, `media3-session`, `media3-cast`, `media3-datasource`, `media3-extractor` (в зависимости от используемых функций).
- Обновите namespace (`com.google.android.exoplayer2.*` → `androidx.media3.*`).

#### 2. Перестройка Player Слоя

```kotlin
val player = ExoPlayer.Builder(context)
    .setTrackSelector(DefaultTrackSelector(context))
    .setLoadControl(DefaultLoadControl())
    .build()
```

- `SimpleExoPlayer` больше нет; используйте `ExoPlayer.Builder`.
- Слушатели — `Player.Listener` (один интерфейс вместо нескольких `EventListener` в старом API).
- Используйте `MediaItem.Builder` (поддерживает DRM, clipping и доп. метаданные).

#### 3. Session & `Service`

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

- Для управления воспроизведением и интеграции с системным UI используйте `MediaSessionService` + `MediaSession`.
- Для сценариев с медиатекой/Android Auto, где нужен browsable каталог, используйте `MediaLibraryService`/`MediaLibrarySession` вместо или вместе с базовым `MediaSessionService`.
- Для Android Auto/Assistant опирайтесь на корректно настроенный `MediaSession`/`MediaLibrarySession` и совместимый браузерный контракт (`MediaBrowser` API); уведомления реализуйте через `MediaNotification.Provider`.
- Авто и TV клиенты используют единый contract поверх Media3 session API.

#### 4. UI Миграция

- `StyledPlayerView` живёт в `media3-ui`; замените XML namespace и класс, если раньше использовался `PlayerView` из ExoPlayer.
- Для Compose: оборачивайте `StyledPlayerView` через `AndroidView` или используйте проверенные сторонние Compose-обёртки.
- Для управления видимостью контроллеров используйте `StyledPlayerView.ControllerVisibilityListener`.

#### 5. Offline И DRM

- Offline — `DownloadService` + `DownloadManager` из `media3-exoplayer`/`media3-datasource`, перенесите существующую логику скачиваний на Media3 API.
- DRM — через `MediaItem.DrmConfiguration` (Widevine, PlayReady и др.): конфигурация DRM привязывается к `MediaItem`, но обработка key rotation и политики истечения лицензий остаётся на уровне DRM session/лицензионного сервера.

#### 6. Тестирование

- Unit/integration: используйте тестовые артефакты Media3 (`media3-test-utils`, `media3-test-utils-robolectric`) — `PlayerTestRunner`, фейки источников и т.п. (не для продакшена).
- Instrumented: `MediaControllerTestRule` и связанные утилиты для проверки session layer.
- Нагрузочные сценарии реализуйте поверх Media3 тест-утилит или собственного обёрнутого плеера; не используйте экспериментальные тестовые классы как runtime API.

#### 7. План Миграции

1. Параллельно держите старый и новый player за Feature Flag.
2. Сначала перенесите session/service слой (`MediaSession`/`MediaLibrarySession`), затем UI.
3. Адаптируйте кастомные listener-обёртки под `Player.Listener` и Media3 session callbacks.
4. Обновите интеграции Auto/TV, проверяя, что клиенты работают с новым Media3 session API и соответствующими template-библиотеками.

---

## Answer (EN)

### Short Version

- Gradually switch dependencies to Media3.
- Build a unified `MediaSession`/`MediaLibrarySession`-centric layer.
- Update UI to `StyledPlayerView`/Compose wrappers.
- Migrate offline/DRM to `MediaItem` plus Media3 `DownloadService`/`DownloadManager`.
- Validate Auto/TV/Assistant integrations stepwise behind a feature flag.

### Detailed Version

#### Requirements

- Functional:
  - Preserve existing playback UX and capabilities (VOD/Live, seeking, subtitles, audio tracks).
  - Support Android TV, Android Auto, Cast, assistants, and media sessions.
  - Preserve/migrate offline downloads and DRM.
- Non-functional:
  - Minimize downtime and regressions (phased rollout with feature flags).
  - Keep architecture extensible (encapsulated player and session layers).
  - Ensure observability (logging, session/error metrics).

#### Architecture

- Introduce a player facade over Media3 (`Player` + `MediaSession`/`MediaLibrarySession`) to hide implementation details.
- Use `MediaSessionService`/`MediaLibraryService` as a single backend for UI, Auto, TV, and assistant integrations.
- Use a shared UI component (`StyledPlayerView` or Compose wrapper) bound to the single `MediaSession`.
- Isolate offline/DRM into a separate module using Media3 `DownloadService`, `DownloadManager`, and `MediaItem.DrmConfiguration`.

### 1. Dependencies

- Replace `com.google.android.exoplayer:exoplayer` with `androidx.media3:media3-exoplayer`.
- Add required Media3 modules: `media3-ui`, `media3-session`, `media3-cast`, `media3-datasource`, `media3-extractor` depending on used features.
- Update imports/namespaces from `com.google.android.exoplayer2.*` to `androidx.media3.*`.

### 2. Player Layer

```kotlin
val player = ExoPlayer.Builder(context)
    .setTrackSelector(DefaultTrackSelector(context))
    .setLoadControl(DefaultLoadControl())
    .build()
```

- `SimpleExoPlayer` is removed; use `ExoPlayer.Builder`.
- Use the unified `Player.Listener` instead of multiple legacy listener interfaces.
- Use `MediaItem.Builder` for DRM, clipping, and extra metadata.

### 3. Session & `Service`

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

- Use `MediaSessionService` + `MediaSession` for playback control and system UI integration.
- For media library/Android Auto scenarios with a browsable catalog, use `MediaLibraryService`/`MediaLibrarySession` as the Media3 alternative to `MediaBrowserServiceCompat`.
- For Android Auto and Assistant, rely on a correctly configured `MediaSession`/`MediaLibrarySession` and compatible `MediaBrowser` contract; implement notifications via `MediaNotification.Provider`.
- Auto and TV clients consume a unified contract built on top of the Media3 session API.

### 4. UI Migration

- Use `StyledPlayerView` from `media3-ui`; update XML namespace and class if you previously used ExoPlayer's `PlayerView`.
- For Compose, wrap `StyledPlayerView` via `AndroidView` or use stable community wrappers.
- For controller visibility handling, use `StyledPlayerView.ControllerVisibilityListener`.

### 5. Offline and DRM

- Migrate offline downloads to `DownloadService` + `DownloadManager` from Media3 modules and adapt existing logic to the new APIs.
- Configure DRM via `MediaItem.DrmConfiguration` (e.g., Widevine, PlayReady); license expiration and key rotation logic remain in your DRM/license server layer.

### 6. Testing

- For unit/integration tests, use `media3-test-utils` and `media3-test-utils-robolectric` (`PlayerTestRunner`, fake sources, etc.) — tests only.
- For instrumented/session tests, use `MediaControllerTestRule` and related utilities.
- Build load tests around Media3 test utilities or your wrapped player; do not use experimental test classes as runtime APIs.

### 7. Migration Plan

1. Run old and new players in parallel behind a feature flag.
2. First migrate the session/service layer (`MediaSession`/`MediaLibrarySession`), then UI.
3. Adapt custom listener wrappers to `Player.Listener` and Media3 session callbacks.
4. Update and verify Android Auto/TV/Assistant integrations against the Media3 session and library session contract and current car/TV template libraries.

---

## Дополнительные Вопросы (RU)
- Как мигрировать кастомный `RenderersFactory` или `DataSource.Factory`?
- Какие изменения требуются для интеграции с Chromecast (MediaRouter → `media3-cast`)?
- Как обеспечить совместимость с Android Auto 6+ и Media3 session API (включая `MediaLibraryService`)?

## Follow-ups (EN)
- How to migrate a custom `RenderersFactory` or `DataSource.Factory`?
- What changes are required to migrate Chromecast integration (MediaRouter → `media3-cast`)?
- How to ensure compatibility with Android Auto 6+ and the Media3 session API (including `MediaLibraryService`)?

## Ссылки (RU)
- https://developer.android.com/guide/topics/media/media3/getting-started
- https://medium.com/androiddevelopers/media3-from-exoplayer-migration

## References (EN)
- https://developer.android.com/guide/topics/media/media3/getting-started
- https://medium.com/androiddevelopers/media3-from-exoplayer-migration

## Связанные Вопросы (RU)
- [[c-android-surfaces]]

## Related Questions (EN)
- [[c-android-surfaces]]
