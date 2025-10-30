---
id: 20251029-170212
title: Design BLE Wearable Sync / Проектирование синхронизации BLE‑носимых устройств
aliases:
    [
        Design BLE Wearable Sync,
        Проектирование синхронизации BLE носимых,
        BLE Health Tracker Sync,
        Синхронизация BLE трекеров,
    ]
topic: android
subtopics: [bluetooth, service, lifecycle]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-lifecycle, c-workmanager, c-room]
sources: []
created: 2025-10-29
updated: 2025-10-29
tags:
    [
        android/bluetooth,
        android/service,
        android/lifecycle,
        difficulty/hard,
        platform/android,
        lang/kotlin,
        ble,
        wearable,
        health-tracker,
    ]
---

# Вопрос (RU)

> Как спроектировать синхронизацию BLE‑носимых устройств (трекер здоровья) для Android?

# Question (EN)

> How to design BLE wearable sync for a health tracker Android app?

---

### Upgraded Interview Prompt (RU)

Спроектируйте Android‑компаньон для BLE носимого. Требования: pairing & bonding, фоновая синхронизация каждые 10 мин, backfill пропущенных данных за 24ч, бюджет батареи <1%/ч во время активной синхронизации, защита приватности. Включите GATT profile, логику переподключения, модель данных, flow разрешений, наблюдаемость.

### Upgraded Interview Prompt (EN)

Build an Android companion app for a BLE wearable. Requirements: pairing & bonding, background sync every 10 min, missed‑data backfill for 24h, battery budget <1%/hr during active sync, and privacy safeguards. Include GATT profile, reconnect logic, data model, permissions flows, and observability.

## Ответ (RU)

BLE синхронизация носимых устройств требует stable pairing, GATT коммуникации, фоновой синхронизации и обработки reconnects.

### Архитектура

Модули: ble-core, device-manager, gatt-services, sync-engine, store (Room), analytics, flags.

### Pairing/Bonding

LE Secure Connections с passkey/Just Works в зависимости от устройства; персист bond; обработка revoke.

### GATT

Custom service с characteristics для summary + bulk history; включить notifications/indications; MTU negotiation; chunk больших передач.

### Sync

Foreground service во время активной синхронизации; иначе WorkManager с constraints и flex windows для выравнивания с Doze. Поддерживать device cursor для backfill последних 24ч; дедупликация по device timestamp + sequence.

### Reconnects

Экспоненциальный backoff; auto‑reconnect на 133/8 ошибки; кеш device address; request priority CONNECTION_PRIORITY_HIGH только во время передач.

### Батарея

Batch writes/reads; предпочитать notifications над polling; компрессия payload; throttle scans.

### Приватность/Безопасность

Шифрование на диске; минимизация PII; разрешить пользовательский opt‑out для cloud.

### Наблюдаемость

Connection success%, GATT error codes, sync duration, bytes/s, battery impact, crash/ANR.

### Тестирование

RF‑noisy окружения, телефон засыпает mid‑transfer, mismatch firmware устройства, потеря bond.

### Tradeoffs

Высокий connection priority ускоряет sync, но разряжает батарею; включать временно с явным timeout.

## Answer (EN)

BLE wearable sync requires stable pairing, GATT communication, background sync, and reconnect handling.

### Architecture

ble-core, device-manager, gatt-services, sync-engine, store (Room), analytics, flags.

### Pairing/Bonding

Use LE Secure Connections with passkey/Just Works depending on device; persist bond; handle revoke.

### GATT

Custom service with characteristics for summary + bulk history; enable notifications/indications; MTU negotiation; chunk large transfers.

### Sync

Foreground service during active sync; otherwise WorkManager with constraints and flex windows to align with Doze. Maintain device cursor to backfill last 24h; de‑dup by device timestamp + sequence.

### Reconnects

Exponential backoff; auto‑reconnect on 133/8 errors; cache device address; request priority CONNECTION_PRIORITY_HIGH only during transfers.

### Battery

Batch writes/reads; prefer notifications over polling; compress payload; throttle scans.

### Privacy/Security

Encrypt at rest; minimize PII; allow user opt‑out for cloud.

### Observability

Connection success%, GATT error codes, sync duration, bytes/s, battery impact, crash/ANR.

### Testing

RF‑noisy environments, phone sleeps mid‑transfer, device firmware mismatch, bond loss.

### Tradeoffs

Higher connection priority speeds sync but drains battery; enable temporarily with explicit timeout.

---

## Follow-ups

-   How to handle device firmware updates over BLE?
-   What strategy minimizes battery while ensuring data completeness?
-   How to handle multiple paired wearables simultaneously?
-   How to recover from corrupted GATT data?

## References

-   [[c-lifecycle]]
-   [[c-workmanager]]
-   [[c-room]]
-   https://developer.android.com/guide/topics/connectivity/bluetooth/ble-overview
-   [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]
-   [[ANDROID-INTERVIEWER-GUIDE]]

## Related Questions

### Prerequisites (Easier)

-   Understanding of BLE GATT profiles and Android background constraints

### Related (Same Level)

-   [[q-data-sync-unstable-network--android--hard]]

### Advanced (Harder)

-   Design a multi-device health data aggregation platform
