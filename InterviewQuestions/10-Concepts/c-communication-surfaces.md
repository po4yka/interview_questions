---
id: ivc-20251102-025
title: Communication Surfaces / Поверхности коммуникации
aliases:
  - Communication Surfaces
  - Поверхности коммуникации Android
kind: concept
summary: Android system surfaces for conversations, calls, and sharing including notifications, bubbles, CallStyle, and ShareSheet integrations
links: []
created: 2025-11-02
updated: 2025-11-02
tags:
  - android
  - concept
  - communication
  - notifications
  - sharing
date created: Sunday, November 2nd 2025, 02:45:00 pm
date modified: Sunday, November 2nd 2025, 02:45:00 pm
---

# Summary (EN)

Android communication surfaces let apps interact outside core UI through conversation notifications, bubbles, CallStyle, foreground-service indicators, ShareSheet, and dynamic shortcuts. They require strict compliance with privacy, background execution limits, and UX guidelines to deliver timely, secure experiences.

# Сводка (RU)

Поверхности коммуникации Android позволяют приложениям взаимодействовать с пользователем вне основного UI через уведомления переписки, bubbles, CallStyle, индикаторы foreground-служб, ShareSheet и динамические ярлыки. Они требуют строгого соблюдения правил приватности, ограничений фонового выполнения и UX-гайдлайнов.

## Core Topics

- Conversation notifications (MessagingStyle, Person, shortcuts) & bubbles lifecycle
- CallStyle notifications, foreground service requirements, mic/camera privacy indicators
- ShareSheet customization, direct share, ChooserTargets, predictive back integration
- Background limits, permissions (`POST_NOTIFICATIONS`, `FOREGROUND_SERVICE_*`)
- Telemetry & compliance (user actions, churn, policy changes)

## Considerations

- Test surfaces across Android 11–14 due to evolving APIs and restrictions.
- Provide graceful degradation on devices/features where surfaces aren’t supported.
- Monitor analytics (open rates, dismiss actions) to refine conversation experiences.
