---
id: ivc-20251102-010
title: Android TV & Google TV / Android TV и Google TV
aliases:
  - Android TV
  - Google TV
  - Leanback
kind: concept
summary: TV-specific Android platform using Leanback and Compose for TV libraries
links: []
created: 2025-11-02
updated: 2025-11-02
tags:
  - android
  - concept
  - tv
  - leanback
  - compose-tv
date created: Sunday, November 2nd 2025, 12:45:00 pm
date modified: Sunday, November 2nd 2025, 12:45:00 pm
---

# Summary (EN)

Android TV / Google TV provides a 10-foot experience via Leanback and Compose for TV. Applications must handle focus navigation, large screens, and content recommendations (Channels/Watch Next).

# Сводка (RU)

Android TV / Google TV обеспечивают интерфейс для больших экранов через Leanback и Compose for TV. Приложения обязаны поддерживать навигацию фокусом, адаптивные layout и систему рекомендаций (Channels/Watch Next).

## Core APIs

- Leanback (`BrowseSupportFragment`, `PlaybackSupportFragment`)
- Compose for TV (`androidx.tv.compose`)
- Recommendations: `Channel`, `Program`, `WatchNextPrograms`
- Input: DPAD/remote/voice

## Considerations

- UI должен быть оптимизирован под 720p/1080p/4K.
- Используйте `FocusRequester`, `onPreviewKeyEvent` в Compose for TV.
- Certification включает performance, HDR, audio passthrough tests.

