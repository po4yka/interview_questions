---
id: "20260108-110550"
title: "Android Enterprise & MDM / Android Enterprise и MDM"
aliases: ["Android Enterprise", "Mobile Device Management Android", "Work Profile APIs"]
summary: "Android management APIs for work profiles, device owner, and zero-touch enrollment"
topic: "android"
subtopics: ["enterprise", "mdm", "security"]
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
tags: ["android", "concept", "enterprise", "mdm", "security", "difficulty/medium"]
---

# Summary (EN)

Android Enterprise provides management APIs for deploying work profiles, fully managed devices, and dedicated devices. Device Policy Controller (DPC) apps enforce policies, leverage zero-touch enrollment, and integrate with Google Play EMM APIs.

# Сводка (RU)

Android Enterprise предоставляет API для внедрения рабочих профилей, полностью управляемых устройств и специализированных терминалов. Приложения-контроллеры политик (DPC) применяют политики, используют zero-touch enrollment и интегрируются с Google Play EMM API.

## Key Concepts

- Management modes: Work Profile, Fully Managed, Dedicated, Corporate-Owned Work Profile (COPE).
- DevicePolicyManager: password policies, app restrictions, lockdowns.
- Enrollment workflows: QR provisioning, zero-touch, NFC bump.
- Play EMM API: private app distribution, managed configurations.

## Considerations

- Требует DPC-приложения с разрешением `BIND_DEVICE_ADMIN`.
- Политики безопасности должны соблюдать GDPR/региональные нормы.
- Требует backend для синхронизации политик и событий (Compliance).

