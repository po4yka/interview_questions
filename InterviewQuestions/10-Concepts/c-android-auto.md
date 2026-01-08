---
id: "20260108-110549"
title: "Android Auto & Automotive OS / Android Auto и Automotive OS"
aliases: ["Android Auto", "Android Automotive OS", "Car App Library"]
summary: "Car-optimized Android platforms using car app templates and in-vehicle systems"
topic: "android"
subtopics: ["android-auto", "automotive", "in-car"]
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
tags: ["android", "android-auto", "automotive", "concept", "in-car", "difficulty/medium"]
---

# Summary (EN)

Android Auto (projected) and Android Automotive OS (native) deliver car-optimized experiences using the Car App Library. Apps must follow template constraints, driver distraction guidelines, and certification processes.

# Сводка (RU)

Android Auto (проекция) и Android Automotive OS (встроенная система) предоставляют оптимизированные для автомобиля интерфейсы через библиотеку шаблонов Car App Library. Приложения обязаны соблюдать ограничения по отвлечению водителя и проходить сертификацию.

## Core Concepts

- App categories: Navigation, Point of Interest, Messaging, Media.
- Template system (`ListTemplate`, `PaneTemplate`, `MapTemplate`) + `CarContext`.
- Approval flow через Google (QA, policy review).
- Automotive OS требует отдельного APK и HMI guidelines OEM.

## Considerations

- Ограниченный API доступ (нет произвольного UI).
- Требования к latency, voice commands, system integration (Assistant).
- Automotive OS поддерживает custom hardware integrations (HVAC, cluster).

