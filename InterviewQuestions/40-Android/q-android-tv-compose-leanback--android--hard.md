---
id: android-623
title: Android TV Compose & Leanback / Android TV на Compose и Leanback
aliases:
- Android TV Compose & Leanback
- Android TV на Compose и Leanback
topic: android
subtopics:
- tv
- ui-compose
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
- q-android-auto-guidelines--android--hard
created: 2025-11-02
updated: 2025-11-11
tags:
- android/tv
- android/ui-compose
- difficulty/hard
sources:
- "https://developer.android.com/training/tv/start"
- "https://developer.android.com/jetpack/compose/tv"

---

# Вопрос (RU)
> Как построить интерфейс Android TV, совмещая Legacy Leanback и Compose for TV, обеспечивая навигацию фокусом, рекомендации и сертификацию Google TV?

# Question (EN)
> How do you build an Android TV UI by combining legacy Leanback and Compose for TV, ensuring focus navigation, recommendations, and Google TV certification requirements?

---

## Ответ (RU)

## Краткая Версия
- Используйте Leanback для проверенных экранов и контролов, Compose for TV — для новых и кастомных интерфейсов.
- Обеспечьте корректную DPAD-навигацию и фокус между Leanback и Compose.
- Настройте рекомендации/каналы и Watch Next согласно актуальным политикам Google TV.
- Используйте надёжный стек воспроизведения (Media3/ExoPlayer), тестируйте на реальных TV-устройствах.
- Ориентируйтесь на официальные чек-листы Google TV/Android TV для сертификации.

## Подробная Версия
### 1. Архитектура UI

- **Leanback** для существующих стабильных компонентов (`BrowseSupportFragment`, `PlaybackSupportFragment`).
- **Compose for TV** для новых экранов (поддержка DPAD-фокуса, `TvLazyRow`/`TvLazyColumn`, `ImmersiveList`).
- Для гибридных экранов: встраивайте `ComposeView` в Leanback-фрагменты или используйте навигацию между отдельными Leanback и Compose активити/фрагментами.

### 2. Requirements

- Функциональные:
  - Поддержка навигации DPAD/remote на всех экранах.
  - Единая навигация между Leanback и Compose-экранами.
  - Поддержка рекомендаций, каналов и Watch Next.
  - Стабильное воспроизведение видео (включая 4K/HDR, субтитры/CC).
- Нефункциональные:
  - Производительность и плавная анимация на TV-устройствах.
  - Соответствие политикам Google TV/Android TV и требованиям сертификации.
  - Предсказуемый фокус и отсутствие «ловушек» фокуса.

### 3. Architecture

- Разделяйте слой UI (Leanback/Compose) и доменную/данную логику (например, MVVM/Clean).
- Используйте навигацию, способную маршрутизировать к Leanback и Compose экранам.
- Инкапсулируйте работу с рекомендациями/каналами и плеером в отдельные компоненты/сервисы.

### 4. Фокус и навигация

```kotlin
@Composable
fun TvGrid(items: List<Video>) {
    TvLazyRow {
        items(items) { item ->
            Card(
                modifier = Modifier
                    .onFocusChanged { /* update state if needed */ }
                    .focusable()
            ) {
                Text(item.title)
            }
        }
    }
}
```

- Используйте Compose for TV фокус-API: `Modifier.focusable()`, `onFocusChanged`, `focusGroup`, `focusRestorer` для сохранения фокуса при обновлениях.
- Следите, чтобы DPAD-навигация (включая переходы между Leanback-вью и Compose-вью) была предсказуемой. Проверяйте переход фокуса через `nextFocus*` атрибуты и соответствующие контейнеры.
- Для Leanback используйте штатные механизмы: `FocusHighlightHandler`, `BrowseFrameLayout`, `BaseGridView` и их поведение по умолчанию вместо ручного управления там, где это не требуется.

### 5. Recommendations & Channels

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

- Для рекомендаций и каналов используйте Preview Channels / TV Provider API в зависимости от целевой платформы (Android TV vs Google TV), с учетом требуемых permission-ов и политики пользователя.
- Watch Next: используйте соответствующие API (`WatchNextPrograms` / Preview API) для добавления продолжения просмотра.
- Рекомендации должны регулярно обновляться и соответствовать актуальным политикам Google TV/Android TV (frequency, relevance, no spam).

### 6. Playback

- Для классического Leanback: `PlaybackTransportControlGlue` + `PlaybackGlueHost` (например, `VideoSupportFragmentGlueHost`).
- Для Compose-интеграции: оборачивайте `PlayerView`/видеоплеер через `AndroidView` или используйте рекомендованный ExoPlayer/Media3 стек, обеспечивая управление через DPAD.
- Проверяйте поддержку HDR/Dolby Vision и других форматов через доступные API (например, `MediaCodecList`/`MediaCodecInfo`, `Display`/`WindowManager`, Media3 capabilities) и учитывайте требования контент-провайдеров.

### 7. Testing & Certification

- Тестируйте на эмуляторе Android TV и физических устройствах (например, ADT-3, Chromecast with Google TV или устройствах партнёров).
- Проверяйте аудио задержки, HDR, дропы кадров и поведение плеера с помощью инструментов (`adb shell`, профайлинг, медиатесты), включая тестирование DPAD и фокуса.
- Для прохождения сертификации ориентируйтесь на официальные чек-листы Google TV/Android TV, CDD/CTS/VTS/TTF. Типичные требования включают: быстрое стартовое время приложения, корректную работу фокуса и safe area, поддержку субтитров/CC и стабильный playback, но точные числа и критерии зависят от программы сертификации.

---

## Answer (EN)

## Short Version
- Use Leanback for proven TV components, Compose for TV for new/custom UI.
- Ensure robust DPAD focus navigation across Leanback and Compose.
- Implement recommendations/channels and Watch Next per Google TV policies.
- Use a solid playback stack (Media3/ExoPlayer) and test on real TV devices.
- Follow official Google TV/Android TV checklists for certification readiness.

## Detailed Version
### 1. UI architecture

- Use **Leanback** for existing stable components (`BrowseSupportFragment`, `PlaybackSupportFragment`).
- Use **Compose for TV** for new screens (DPAD focus support, `TvLazyRow`/`TvLazyColumn`, `ImmersiveList`).
- For hybrid screens, embed `ComposeView` inside Leanback fragments or navigate between dedicated Leanback and Compose activities/fragments.

### 2. Requirements

- Functional:
  - Support DPAD/remote navigation on all screens.
  - Unified navigation between Leanback and Compose screens.
  - Support recommendations, channels, and Watch Next.
  - Stable video playback (including 4K/HDR, subtitles/CC).
- Non-functional:
  - Good performance and smooth animations on TV hardware.
  - Compliance with Google TV/Android TV policies and certification.
  - Predictable focus behavior without focus traps.

### 3. Architecture

- Separate UI layer (Leanback/Compose) from domain/data (e.g., MVVM/Clean).
- Use navigation capable of routing to both Leanback and Compose screens.
- Encapsulate recommendations/channels logic and player integration into dedicated components/services.

### 4. Focus and navigation

```kotlin
@Composable
fun TvGrid(items: List<Video>) {
    TvLazyRow {
        items(items) { item ->
            Card(
                modifier = Modifier
                    .onFocusChanged { /* update state if needed */ }
                    .focusable()
            ) {
                Text(item.title)
            }
        }
    }
}
```

- Use Compose for TV focus APIs: `Modifier.focusable()`, `onFocusChanged`, `focusGroup`, `focusRestorer` to keep focus stable across recompositions.
- Ensure DPAD navigation works predictably across hybrid UI: verify transitions between Leanback views and Compose views, use `nextFocus*` attributes when needed.
- In Leanback, rely on built-in helpers like `FocusHighlightHandler`, `BrowseFrameLayout`, and `BaseGridView` before resorting to manual focus management.

### 5. Recommendations & Channels

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

- Implement recommendations and channels using Preview Channels / TV Provider APIs appropriate for Android TV / Google TV, with required permissions and respecting user control over channels.
- For Watch Next, use the dedicated APIs (`WatchNextPrograms` / preview APIs) to surface continue-watching content.
- Keep recommendations refreshed and compliant with current Google TV content and spam policies.

### 6. Playback

- With Leanback, use `PlaybackTransportControlGlue` with a suitable `PlaybackGlueHost` (e.g., `VideoSupportFragmentGlueHost`).
- In Compose, embed your player (e.g., ExoPlayer with `PlayerView`) via `AndroidView` or use the recommended Media3/ExoPlayer integration, ensuring DPAD-based controls work on TV.
- Validate HDR/Dolby Vision and audio capabilities using appropriate platform APIs (`MediaCodec`/`MediaCodecList`, display capabilities, Media3) and meet studio/provider requirements where applicable.

### 7. Testing & Certification

- Test on the Android TV emulator and real devices (e.g., ADT-3, Chromecast with Google TV, partner devices).
- Measure audio latency, HDR behavior, frame drops, and playback stability using `adb` tools and profiling; thoroughly test DPAD navigation and focus.
- For certification, follow the official Google TV / Android TV checklists and CDD/CTS/VTS/TTF documentation. Typical expectations include fast startup, correct focus handling and safe areas, subtitles/CC support, and stable playback, but exact thresholds depend on the specific certification program.

---

## Дополнительные вопросы
- Как мигрировать существующее Leanback-приложение на Compose for TV постепенно?
- Какие требования к DRM/HDCP для контента 4K HDR?
- Как реализовать мультипрофильную поддержку (Kids) на Google TV?

## Follow-ups
- How to gradually migrate an existing Leanback app to Compose for TV?
- What are the DRM/HDCP requirements for 4K HDR content?
- How to implement multi-profile (Kids) support on Google TV?

## Ссылки
- [[c-android-tv]]
- https://developer.android.com/training/tv/start
- https://developer.android.com/jetpack/compose/tv

## References
- [[c-android-tv]]
- https://developer.android.com/training/tv/start
- https://developer.android.com/jetpack/compose/tv

## Related Questions

- [[c-android-tv]]
