---
id: android-623
title: Android TV Compose & Leanback / Android TV на Compose и Leanback
aliases:
  - Android TV Compose & Leanback
  - Android TV на Compose и Leanback
topic: android
subtopics:
  - tv
  - leanback
  - compose
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-android-tv
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/tv
  - android/leanback
  - android/compose-tv
  - difficulty/hard
sources:
  - url: https://developer.android.com/training/tv/start
    note: Android TV developer guide
  - url: https://developer.android.com/jetpack/compose/tv
    note: Compose for TV docs
---

# Вопрос (RU)
> Как построить интерфейс Android TV, совмещая Legacy Leanback и Compose for TV, обеспечивая навигацию фокусом, рекомендации и сертификацию Google TV?

# Question (EN)
> How do you build an Android TV UI by combining legacy Leanback and Compose for TV, ensuring focus navigation, recommendations, and Google TV certification requirements?

---

## Ответ (RU)

### 1. Архитектура UI

- **Leanback** для стабильных компонентов (BrowseSupportFragment, PlaybackSupportFragment).
- **Compose for TV** для новых экранов (поддержка фокуса, `TvLazyColumn`, `ImmersiveList`).
- Используйте `ComposeView` внутри Leanback для гибридных экранов.

### 2. Фокус и навигация

```kotlin
@Composable
fun TvGrid(items: List<Video>) {
    val focusRequester = remember { FocusRequester() }

    TvLazyRow {
        items(items) { item ->
            Card(
                modifier = Modifier
                    .focusRequester(focusRequester)
                    .onFocusChanged { /* update state */ }
                    .focusable()
            ) {
                Text(item.title)
            }
        }
    }
}
```

- Следите за DPAD-навигацией, используйте `focusRestorer`.
- Для Leanback — `FocusHighlightHandler`, `BrowseFrameLayout`.

### 3. Recommendations & Channels

```kotlin
val channelId = channelManager.createChannel(
    Channel.Builder()
        .setType(Channel.TYPE_PREVIEW)
        .setDisplayName("Top Picks")
        .build()
)

channelManager.addProgram(
    Program.Builder()
        .setChannelId(channelId)
        .setTitle(video.title)
        .setIntentUri(contentUri)
        .build()
)
```

- Watch Next: `WatchNextPrograms.insert`.
- Требуется регулярное обновление рекомендаций (policy).

### 4. Playback

- Leanback `PlaybackTransportControlGlue` + `GlueHost`.
- Compose integration: wrap `VideoView`/`PlayerView`.
- Поддержка HDR/Dolby Vision: проверка через `MediaCodecInfo`.

### 5. Testing & Certification

- Android TV emulator + physical device (ADT-3, Chromecast with Google TV).
- Audio latency, HDR, frame drops — тестирование `adb shell media playback`.
- Certification checklist: startup latency < 5s, focus safe areas, captions.

---

## Answer (EN)

- Combine Leanback fragments with Compose for TV components via embedded `ComposeView` or hybrid navigation.
- Manage focus using Compose TV focus APIs and Leanback focus helpers; ensure DPAD navigation works across hybrids.
- Implement recommendations (channels/watch next) and keep them refreshed to satisfy Google TV requirements.
- Integrate playback glue or ExoPlayer with HDR/audio compliance; validate with certification test suites.

---

## Follow-ups
- Как мигрировать существующее Leanback-приложение на Compose for TV постепенно?
- Какие требования к DRM/HDCP для контента 4K HDR?
- Как реализовать мультипрофильную поддержку (Kids) на Google TV?

## References
- [[c-android-tv]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/training/tv/start
- https://developer.android.com/jetpack/compose/tv
