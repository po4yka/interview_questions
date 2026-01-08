---\
id: "20260108-110550"
title: "Media3 Transformer / Media3 Transformer"
aliases: ["Android Media Editing", "Media3 Transformer"]
summary: "Media3 Transformer API for video/audio editing, composition, and transcoding on Android"
topic: "android"
subtopics: ["editing", "media", "media3"]
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
tags: ["android", "concept", "editing", "media", "media3", "difficulty/medium"]
---\

# Summary (EN)

Media3 Transformer is the Jetpack API for editing and transcoding media. It provides composition, trimming, effect pipelines (video/effects/audio), asynchronous execution, and export progress callbacks, replacing legacy `MediaMuxer`/`MediaCodec` pipelines with a higher-level model.

# Сводка (RU)

Media3 Transformer — Jetpack API для редактирования и транскодирования медиа. Предлагает композицию, обрезку, пайплайны эффектов (видео/аудио), асинхронное выполнение и прогресс-колбеки, заменяя низкоуровневые `MediaMuxer`/`MediaCodec`.

## Key Concepts

- `Transformer`, `Composition`, `EditedMediaItem`
- `Effect` pipeline: `VideoEffects`, `AudioEffects`, LUTs, overlays
- Export targets: file path, `ParcelFileDescriptor`, `AssetFileDescriptor`
- Progress listeners, `Transformer.Listener`

## Considerations

- Ограничения по формату (исходный → выходной codec).
- Требования к ресурсам: фоновые `Service` + `WorkManager`.
- Профилирование: hardware codec availability, fallback на software.
