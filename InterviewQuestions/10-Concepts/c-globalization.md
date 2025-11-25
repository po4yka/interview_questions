---
id: ivc-20251102-024
title: Globalization & Localization / Глобализация и локализация
aliases: [Globalization, Internationalization, Localization]
kind: concept
summary: Strategies for building Android apps that adapt to languages, regions, scripts, and cultural conventions
links: []
created: 2025-11-02
updated: 2025-11-02
tags: [accessibility, android, concept, globalization, localization]
date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Android globalization ensures apps behave correctly across locales, languages, and writing systems. It spans localization pipelines, resource management, bi-directional (RTL) layouts, pluralization, time/number formatting, font fallback for complex scripts, and cultural nuances (images, colors, legal content).

# Сводка (RU)

Глобализация Android-приложений гарантирует корректную работу во всех локалях, языках и системах письма. Включает процессы локализации, управление ресурсами, поддержку двунаправленных (RTL) интерфейсов, множественные формы, форматирование времени/чисел, резерв шрифтов для сложных скриптов и культурные нюансы (изображения, цвета, юридический контент).

## Core Topics

- Localization workflow: string resources, translatable flags, translation memory, pseudo-localization
- RTL & BiDi support: `android:supportsRtl`, layout mirroring, BiDi text handling, Compose APIs
- Formatting & pluralization: `Locale`, `NumberFormat`, `DateFormat`, `PluralRules`, `MeasureFormat`
- Fonts & typography: font fallback chains, downloadable fonts, complex scripts (CJK, Indic, Arabic)
- Regional compliance: store listings, currencies, legal statements, in-app purchase localization

## Considerations

- Automate pseudo-localization in CI to detect truncation and hard-coded strings.
- Keep translations external (TMS) with version control traceability.
- Validate UI with both LTR and RTL, multi-byte scripts, and large font accessibility settings.
