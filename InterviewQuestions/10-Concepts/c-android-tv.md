---
id: "20260108-110549"
title: "Android TV & Google TV / Android TV и Google TV"
aliases: ["Android TV", "Google TV", "Leanback"]
summary: "TV-specific Android platform using Leanback and Compose for TV libraries"
topic: "android"
subtopics: ["compose-tv", "leanback", "tv"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-11-02"
updated: "2025-11-02"
tags: ["android", "compose-tv", "concept", "leanback", "tv", "difficulty/medium"]
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

